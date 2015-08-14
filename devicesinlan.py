#!/usr/bin/python3
import argparse
import subprocess
import datetime
import gettext
import threading
import ipaddress
import os
import re
import sys
import socket
import time
from struct import pack, unpack
import signal

# I had a lot of problems with UTF-8. LANG must be es_ES.UTF-8 to work
gettext.textdomain('devicesinlan')
_=gettext.gettext

ARP_GRATUITOUS = 1
ARP_STANDARD = 2


def int2hex(int):
    pass

def val2int(val):
    '''Retourne une valeur sous forme d'octet en valeur sous forme d'entier.'''
    s=""
    for v in val:
        s=s+"{0:0=2d}".format(v)
    return int(s, 16)
    #return int(''.join(['%02d'%ord(c) for c in val]), 16)
    

class TimeoutError(Exception):
    '''Exception levée après un timeout.'''
    pass

def timeout(function, timeout=10):
    '''Exécute la fonction function (référence) et stoppe son exécution au bout d'un certain temps déterminé par timeout.
       Retourne None si la fonction à été arretée par le timeout, et la valeur retournée par la fonction si son exécution se termine.'''

    def raise_timeout(num, frame):
        raise TimeoutError
    
    # On mappe la fonction à notre signal
    signal.signal(signal.SIGALRM, raise_timeout)
    # Et on définie le temps à attendre avant de lancer le signal
    signal.alarm(timeout)
    try:
        retvalue = function()
    except TimeoutError: # = Fonction quittée à cause du timeout
        return None
    else: # = Fonction quittée avant le timeout
        # On annule le signal
        signal.alarm(0)
        return retvalue


class ArpRequest:
    '''Génère une requête ARP et attend la réponse'''
    
    def __init__(self, ipaddr, if_name, arp_type=ARP_GRATUITOUS):
        # Initialisation du socket (socket brut, donc besoin d'ê root)
        self.arp_type = arp_type
        self.if_ipaddr = socket.gethostbyname(socket.gethostname())
        self.socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.SOCK_RAW)
        self.socket.bind((if_name, socket.SOCK_RAW))
        self.ipaddr = ipaddr
        self.mac=None#Mac address string
        self.hwname=None#String hardware name
        self.init=None
        self.finished=False
        
    def request(self):
        '''Envois une requête arp et attend la réponse'''
        # Envois de 5 requêtes ARP
#        for _ in range(5):
        self.init=datetime.datetime.now()
        self.socket.setblocking(3)
        self._send_arp_request()
        
        for i in range(3):
            if self.finished==True:
                break
            time.sleep(1)
        # Puis attente de la réponse
        if timeout(self._wait_response, 3):
            return True
        else:
            return False

    def _send_arp_request(self):
        '''Envois une requête ARP pour la machine'''
        # Adresse logicielle de l'émetteur :
        if self.arp_type == ARP_STANDARD: 
            saddr = pack('!4B',*[int(x) for x in self.if_ipaddr.split('.')])
        else:
            saddr = pack('!4B',*[int(x) for x in self.ipaddr.split('.')])

        # Forge de la trame :
        frame = [
            ### Partie ETHERNET ###
            # Adresse mac destination (=broadcast) :
            pack('!6B', *(0xFF,) * 6),
            # Adresse mac source :
            self.socket.getsockname()[4],
            # Type de protocole (=ARP) :
            pack('!H', 0x0806),
            
            ### Partie ARP ###
            # Type de protocole matériel/logiciel (=Ethernet/IP) :
            pack('!HHBB', 0x0001, 0x0800, 0x0006, 0x0004),
            # Type d'opération (=ARP Request) :
            pack('!H', 0x0001),
            # Adresse matériel de l'émetteur :
            self.socket.getsockname()[4],
            # Adresse logicielle de l'émetteur :
            saddr,
            # Adresse matérielle de la cible (=00*6) :
            pack('!6B', *(0,) * 6),
            # Adresse logicielle de la cible (=adresse fournie au
            # constructeur) :
            pack('!4B', *[int(x) for x in self.ipaddr.split('.')])
        ]
        
        self.socket.send(b''.join(frame)) # Envois de la trame sur le réseau
        
    
    def _wait_response(self):
        '''Attend la réponse de la machine'''
        while 0xBeef:
            # Récupération de la trame :
            frame = self.socket.recv(1024)
            
            # Récupération du protocole sous forme d'entier :
            proto_type = val2int(unpack('!2s', frame[12:14])[0])
            if proto_type != 0x0806: # On passe le traitement si ce
                continue             # n'est pas de l'arp

            # Récupération du type d'opération sous forme d'entier :
            op = val2int(unpack('!2s', frame[20:22])[0])
            if op != 2:  # On passe le traitement pour tout ce qui n'est
                continue # pas une réponse ARP

            # Récupération des différentes addresses de la trame :
            arp_headers = frame[18:20]
            arp_headers_values = unpack('!1s1s', arp_headers)
            hw_size, pt_size = [val2int(v) for v in arp_headers_values]
            total_addresses_byte = hw_size * 2 + pt_size * 2
            arp_addrs = frame[22:22 + total_addresses_byte]
            
            src_hw, src_pt, dst_hw, dst_pt = unpack('!%ss%ss%ss%ss' % (hw_size, pt_size, hw_size, pt_size), arp_addrs)
            
            # Get MAC
            self.mac=""
            for b in src_hw:
                self.mac=self.mac+str(hex(b))[2:]+":"
            self.mac=self.mac[:-1]
            print (self.mac)
            
            # Comparaison de l'adresse recherchée avec l'adresse trouvée dans la trame :
            if src_pt == pack('!4B', *[int(x) for x in self.ipaddr.split('.')]):
                self.finished=True
                return True # Quand on a trouvé, on arrete de chercher ! Et oui, c'est mal de faire un retour dans une boucle, je sais :)


class Color:
    def green(s):
       return "\033[92m{}\033[0m".format(s)
    
    def red(s):
       return "\033[91m{}\033[0m".format(s)
    
    def bold(s):
       return "\033[1m{}\033[0m".format(s)

class SetDevices:
    def __init__(self):
        """This constructor load /etc/devicesinlan/known.txt and executes arp-scan and parses its result"""
        self.arr=[]
        self.known=SetKnownDevices()
        self.load_arpscan()#From arp_scan

    def length(self):
        """Number of devices in the set"""
        return len(self.arr)
        
    def load_arpscan(self):
        """Load Devices from arpscan output"""
        
        ##With arp-scan
#        try:
#            output=subprocess.check_output(["arp-scan", "--interface", args.interface, "-l", "--ignoredups"]).decode('UTF-8')
#        except:
#            print (_("There was an error executing arp-scan.")+" "+_("Is the interface argument correct?."))
#            sys.exit(2)
#        for line in output.split("\n"):
#            if line.find("\t")!=-1:
#                h=Device()
#                arr=line.split("\t")
#                h.ip=arr[0]
#                h.mac=arr[1]
#                h.hwname=arr[2]
#                for k in self.known.arr:
#                    if k.mac.upper()==h.mac.upper():
#                        h.alias=k.alias
#                self.arr.append(h)
                
        ##With arprequest code
        threads=[]
        for addr in ipaddress.IPv4Network('192.168.1.0/24'):
            t=TRequest(str(addr), args.interface)
            t.start()
            
        for t in threads:
            t.join()
            if t.request.mac!=None:
                h=Device()
                h.ip=t.request.ipaddr
                h.mac=t.request.mac
                h.hwname=""
                for k in self.known.arr:
                    if k.mac.upper()==h.mac.upper():
                        h.alias=k.alias
                self.arr.append(h)
#                
        ##With arprequest code f8:8e:85:c3:6d:7f
#        ar=ArpRequest("192.168.1.1", args.interface)
#        res=ar.request()
#        if res==True:
#            h=Device()
#            h.ip="192.168.1.1"
#            h.mac=ar.mac
#            h.hwname=""
#            for k in self.known.arr:
#                if k.mac.upper()==h.mac.upper():
#                    h.alias=k.alias
#            self.arr.append(h)
            
    def max_len_hwname(self):
        return  max(len(h.hwname) for h in self.arr)

    def max_len_alias(self):
        l=0
        for h in self.arr:
            if h.alias:
                le=len(h.alias)
                if l<le:
                    l=le
        return l
        
    def order_by_ip(self):
        self.arr=sorted(self.arr, key=lambda k: (int(k.ip.split(".")[0]), int(k.ip.split(".")[1]), int(k.ip.split(".")[2]), int(k.ip.split(".")[3])))
        
    def print(self):
        maxalias=self.max_len_alias()
        maxhwname=self.max_len_hwname()
        self.order_by_ip()
        print (Color.bold(_("{} DEVICES IN LAN FROM {} INTERFACE AT {}").format(self.length(), args.interface.upper(), str(datetime.datetime.now())[:-7]).center (6+15+17+maxalias+maxhwname)))
        print ()
        print (Color.bold("{}  {}  {}  {}".format(" IP ".center(15,'=')," MAC ".center(17,'='), " ALIAS ".center(maxalias,'='), " HARDWARE ".center(maxhwname,'='))))
        for h in self.arr:
            if h.alias:
                mac=Color.green(h.mac)
                alias=h.alias
            else:
                mac=Color.red(h.mac)
                alias=""
            print ("{}  {}  {}  {}".format(h.ip.ljust(15), mac, Color.bold(alias.ljust(maxalias)), h.hwname.ljust(maxhwname)))        



class Device:
    def __init__(self):
        self.ip=None
        self.mac=None
        self.hwname=None
        self.alias=None

class TRequest(threading.Thread):
    def __init__(self, ip, interface):
        threading.Thread.__init__(self)
        self.init=datetime.datetime.now()
        self.request=ArpRequest(ip, interface)

    
    def run(self):    
        self.request.request()
        

    
class KnownDevice:
    def __init__(self):
        self.mac=None
        self.alias=None

    def validate_mac(self, s):
        if len(s)!=17:
            return False

        if re.match(r'([0-9a-f]{2}[:-]){5}([0-9a-f]{2})', s):
            return True
        return False

    def validate_alias(self, s):
        if len(s)>40:
            return False
        if len(s)==0:
            return False
        return True
        
    def insert_mac(self):
        validated=False
        while  validated==False:
            self.mac=input(Color.bold(_("Input the MAC of the known device (xx:xx:xx:xx:xx:xx): "))).lower()
            if self.validate_mac(self.mac):
                validated=True
            else:
                print (Color.red(_("You need to insert a mac with the next format: 2a:3b:4c:5d:6e:7a")))

    def insert_alias(self):
        validated=False
        while validated==False:
            self.alias=input(Color.bold(_("Input an alias of the known device: ")))
            if self.validate_alias(self.alias):
                validated=True
            else:
                print (Color.red(_("You need to add an alias")))

class SetKnownDevices:
    def __init__(self):
        self.arr=[]
        self.load()
        
    def append(self, k):
        if self.exists(k):
            self.remove_mac(k.mac)#Sustitute it
            print ("Mac already exists, overwriting it")
        self.arr.append(k)
    def print(self):
        maxalias=self.max_len_alias()     
        print (Color.bold(_("KNOWN DEVICES BY USER AT {}").format( str(datetime.datetime.now())[:-7]).center (17+2+maxalias)))
        print ()
        print (Color.bold("{}  {}".format(" MAC ".center(17,'='), " ALIAS ".center(maxalias,'='))))
        known.order_by_alias()
        for k in known.arr:
            print ("{} {}".format(Color.green(k.mac), Color.bold(k.alias)))

    def remove_mac(self, mac):
        """Returns a boolean if is deleted"""
        todelete=[]
        for k in self.arr:
            if k.mac==mac:
                todelete.append(k)
        
        for k in todelete:
            self.arr.remove(k)
        if len(todelete)>0:    
            return True
        
        return False
        
    def exists(self, kh):
        """Only checks mac, so only need mac to be checked"""
        for k in self.arr:
            if k.mac==kh.mac:
                return True
        return False
    
    def load(self):
        f=open("/etc/devicesinlan/known.txt","r")
        for l in f.readlines():
            ar=l.split("=")
            if len(ar)==2:
                try:
                    k=KnownDevice()
                    ar=l.split("=")
                    k.mac=ar[0].strip()
                    k.alias=ar[1].strip()
                    self.arr.append(k)
                except:
                    print(_("Error parsing {}").format(l))
        f.close()        
    
    def max_len_alias(self):
        l=0
        for h in self.arr:
            if h.alias:
                le=len(h.alias)
                if l<le:
                    l=le
        return l
        
    def save(self):
        """Save etc file"""
        f=open("/etc/devicesinlan/known.txt","w")
        for k in self.arr:
            f.write("{} = {}\n".format(k.mac.lower(), k.alias))
        f.close()        
        
    def order_by_alias(self):
        self.arr=sorted(self.arr, key=lambda k: k.alias)

##############################################
##Parse arguments
parser=argparse.ArgumentParser(prog='devicesinlan', description=_('Show devices in a LAN'),  epilog=_("Developed by Mariano Muñoz 2015 ©"))
parser.add_argument('-v', '--version', action='version', version="0.5.0")
group = parser.add_mutually_exclusive_group()
group.add_argument('-i',  '--interface', help=_('Net interface name'),  default='eth0')
group.add_argument('-a',  '--add', help=_('Add a known device'), action='store_true')
group.add_argument('-r',  '--remove', help=_('Remove a known device'), action='store_true')
group.add_argument('-l',  '--list', help=_('List known device'), action='store_true')
args=parser.parse_args()


##Make system checks
if os.path.exists("/usr/bin/arp-scan")==False:
    print(_("I couldn't find /usr/bin/arp-scan.") + " " + _("Please install it."))
    sys.exit(1)

if os.path.exists("/etc/devicesinlan/known.txt")==False:
    subprocess.check_output(["cp","/etc/devicesinlan/known.txt.dist","/etc/devicesinlan/known.txt"])
    print(_("I couldn't find /etc/devicesinlan/known.txt.") + " " + _("I copied distribution file to it.") + " "+ _("Add your mac addresses to detect strage devices in your LAN."))

known=SetKnownDevices()

if args.add:
    k=KnownDevice()
    k.insert_mac()
    k.insert_alias()
    known.append(k)
    known.save()    
    print (Color.green(_("Known device inserted")))
    sys.exit(0)
    
if args.remove:
    k=KnownDevice()
    k.insert_mac()
    if known.remove_mac(k.mac):
        known.save()
        print (Color.green(_("Mac removed")))
    else:
        print (Color.red(_("I couldn't find the mac")))
    sys.exit(0)
    
if args.list:
    known.print()
    sys.exit(0)
        

## Load devices
inicio=datetime.datetime.now()
set=SetDevices()
set.print()
print ("Took {}".format (datetime.datetime.now()-inicio))

