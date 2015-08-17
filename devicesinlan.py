#!/usr/bin/python3
import argparse
import codecs
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
import fcntl
import struct

"""
    To see information of the ARP protocol, look into doc/devicesinlan.odt
"""

# I had a lot of problems with UTF-8. LANG must be es_ES.UTF-8 to work
gettext.textdomain('devicesinlan')
_=gettext.gettext


class TypesARP:
    Gratuitous = 1
    Standard = 2


    

#class TimeoutError(Exception):
#    '''Exception levée après un timeout.'''
#    pass
#
#def timeout(function, timeout=10):
#    '''Exécute la fonction function (référence) et stoppe son exécution au bout d'un certain temps déterminé par timeout.
#       Retourne None si la fonction à été arretée par le timeout, et la valeur retournée par la fonction si son exécution se termine.'''
#
#    def raise_timeout(num, frame):
#        raise TimeoutError
#    
#    # On mappe la fonction à notre signal
#    signal.signal(signal.SIGALRM, raise_timeout)
#    # Et on définie le temps à attendre avant de lancer le signal
#    signal.alarm(timeout)
#    try:
#        retvalue = function()
#    except TimeoutError: # = Fonction quittée à cause du timeout
#        return None
#    else: # = Fonction quittée avant le timeout
#        # On annule le signal
#        signal.alarm(0)
#        return retvalue



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
        self.arp_scanner()#From arp_scan

    def length(self):
        """Number of devices in the set"""
        return len(self.arr)
        
    def arp_scanner(self):
        """Load Devices from arpscan output"""
        if args.my==False:
            ##With arp-scan
            try:
                output=subprocess.check_output(["arp-scan", "--interface", args.interface, "--localnet", "--ignoredups"]).decode('UTF-8')
            except:
                print (_("There was an error executing arp-scan.")+" "+_("Is the interface argument correct?."))
                sys.exit(2)
            for line in output.split("\n"):
                if line.find("\t")!=-1:
                    h=Device()
                    arr=line.split("\t")
                    h.ip=arr[0]
                    h.mac=arr[1]
                    h.hwname=arr[2]
                    for k in self.known.arr:
                        if k.mac.upper()==h.mac.upper():
                            h.alias=k.alias
                    self.arr.append(h)
        else:#args.my=True
            print (_("MY OWN ARP SCANNER IS IN DEVELOPING. RESULTS ARE NOT ENOUGH GOOD YET."))
            
            threads=[]
            for addr in ipaddress.IPv4Network('192.168.1.0/24'):
                t=TRequest(str(addr), args.interface,  TypesARP.Standard)
                t.start()
                threads.append(t)
                
            for t in threads:
                t.join()
                if t.mac!=None:
                    h=Device()
                    h.ip=t.ipaddr
                    h.mac=t.mac
                    h.hwname=t.hwname
                    for k in self.known.arr:
                        if k.mac.upper()==h.mac.upper():
                            h.alias=k.alias
                    self.arr.append(h)

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
        maxhwname=10#self.max_len_hwname()
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
    def __init__(self, ip, if_name, arp_type):
        threading.Thread.__init__(self)
        self.if_name=if_name
        self.arp_type = arp_type
        self.if_ipaddr = self.get_if_ipaddr() 
        self.socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.SOCK_RAW)
        self.socket.bind((if_name, socket.SOCK_RAW)) 
        self.ipaddr = ip
        self.mac=None#Mac address string
        self.hwname=None#String hardware name
        self.sent_frame=None
        self.received_frame=None


    def get_if_ipaddr(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            self.if_name.encode('utf-8')+b'\x00'*(256-len(self.if_name))#            struct.pack('256s', self.if_name[:15])
        )[20:24])
    

    def run(self):    
        self.arp_send()
        time.sleep(.3)
        self.arp_receive()
#        for i in range(4):
#            time.sleep(.3)
#            if self.arp_receive():
#                break
            
            
        if self.ipaddr in ("192.168.1.12", "192.168.1.102"):
            print ("""-------------------------------------------- {} from interface {}
Sent frame:
{}
Received frame:
{}
Macs: {}   {}   {}   {}
--------------------------------------------""".format(self.ipaddr,  self.if_ipaddr, self.sent_frame,  self.received_frame, self.bytes2mac(self.received_frame[0:6]),self.bytes2mac(self.received_frame[6:12]), self.bytes2mac(self.received_frame[22:28]),   self.bytes2mac(self.received_frame[32:38])))

        
        
    def arp_send(self):
        """
        00:06 HW address destination (broadcast)
        06:12 HW address of interface
        12:14 Protocolo type \x08\x06
        14:16 Protocolo Ethernet \x00\x01
        16:18 IPv4 que es \x08\x00
        18:19 HW MAC length bytes 6
        19:20 Protocol address length IPv4 es 4
        20:22 Arp operation request 00 01
        22:28 HW address of interface sender
        28:32 Ip del Interface
        32:38 Hardware address of target 00 00 00 00 00 00
        38:42 Ip del objetivo        
        """
#        if self.arp_type == TypesARP.Standard: 
#            saddr = self.ip2bytes(self.if_ipaddr)
#        else:
#            saddr = self.ip2bytes(self.ipaddr)
            
        frame2=b"\xff\xff\xff\xff\xff\xff"+ \
            self.socket.getsockname()[4] + \
            b"\x08\x06" + \
            b"\x00\x01" + \
            b"\x08\x00" + \
            b"\x06" + \
            b"\x04" + \
            b"\x00\x01" + \
            self.socket.getsockname()[4] + \
            self.ip2bytes(self.if_ipaddr) + \
            b"\x00\x00\x00\x00\x00\x00" + \
            self.ip2bytes(self.ipaddr)
#        print( self.bytes2mac(self.socket.getsockname()[4]), self.if_ipaddr, self.ip2bytes(self.if_ipaddr), self.ipaddr, self.ip2bytes(self.ipaddr))
        self.sent_frame=frame2
        self.socket.send(frame2)

    def bytes2mac(self, bytes):     
        """Bytes to mac address"""   
        b=codecs.encode(bytes, 'hex_codec') #Obtenemos b'008cfa7019b7'
        s=b.decode('utf-8')
        arr=[s[i:i+2] for i in range(0, len(s), 2)]
        return "{0[0]}:{0[1]}:{0[2]}:{0[3]}:{0[4]}:{0[5]}".format(arr)
        
    def bytes2ip(self, bytes):
        """Bytes to ip address"""
        s=""
        for b in bytes:#b is an int
            s=s+"{}.".format(b)
        return s[:-1]
    
    def ip2bytes(self, ipstr):
        arr=[int(x) for x in ipstr.split('.')]
        s=b""
        for a in arr:
            s=s+bytes([a]) #To be treated as an byte of integer
        return s

    def bytes2text(self, bytes):
        """Bytes to string"""
        s=""
        for b in bytes:
            try:
                if b>32:
                    s=s+chr(b)
            except:
                pass
        return s

    def arp_receive(self):
        '''
        00:06 Mac Destination FF:FF:FF:FF:FF:FF
        06:12 MAC Origin 
        12:14 Protocolo type \x08\x06
        18:19 Hardware size 6 b'\x06'
        19:20 IP size 4 b'\x04'
        20:22 ARP operation \x00\x02, request es 1, reverse 3y 4
        22:28 Returned MAC
        28:32 Returned IP
        32:38 Original MAC
        38:42 Original IP
        '''
        frame = self.socket.recv(1024)    
        self.received_frame=frame
        
        if frame[12:14] != b'\x08\x06': # Checks ARP protocol
            return False

        if frame[20:22] != b'\x00\x02': #Checks ARP Answer
            return False

        #Compare ip whith ip of the trame
        if self.ipaddr==self.bytes2ip(frame[28:32]):    
            self.mac=self.bytes2mac(frame[22:28])
            self.hwname=""
            return True
        return False

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

def main():
    parser=argparse.ArgumentParser(prog='devicesinlan', description=_('Show devices in a LAN'),  epilog=_("Developed by Mariano Muñoz 2015 ©"))
    parser.add_argument('-v', '--version', action='version', version="0.5.0")
    parser.add_argument('-m', '--my', help=_('Use my own arp scanner'), action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-i',  '--interface', help=_('Net interface name'),  default='eth0')
    group.add_argument('-a',  '--add', help=_('Add a known device'), action='store_true')
    group.add_argument('-r',  '--remove', help=_('Remove a known device'), action='store_true')
    group.add_argument('-l',  '--list', help=_('List known device'), action='store_true')
    global args
    args=parser.parse_args()
    
    
    ##Make system checks
    if os.path.exists("/usr/bin/arp-scan")==False:
        print(_("I couldn't find /usr/bin/arp-scan.") + " " + _("Please install it."))
        sys.exit(1)
    
    if os.path.exists("/etc/devicesinlan/known.txt")==False:
        subprocess.check_output(["cp","/etc/devicesinlan/known.txt.dist","/etc/devicesinlan/known.txt"])
        print(_("I couldn't find /etc/devicesinlan/known.txt.") + " " + _("I copied distribution file to it.") + " "+ _("Add your mac addresses to detect strage devices in your LAN."))
    
    global known
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

args=None
known=None
if __name__ == "__main__":
    main()
