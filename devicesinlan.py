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

"""
    To see information of the ARP protocol, look into doc/devicesinlan.odt
"""

# I had a lot of problems with UTF-8. LANG must be es_ES.UTF-8 to work
gettext.textdomain('devicesinlan')
_=gettext.gettext


class TypesARP:
    Gratuitous = 1
    Standard = 2

class Color:
    def green(s):
       return "\033[92m{}\033[0m".format(s)
    
    def red(s):
       return "\033[91m{}\033[0m".format(s)
    
    def bold(s):
       return "\033[1m{}\033[0m".format(s)

    def pink(s):
        return "\033[95m{}\033[0m".format(s)
        
    def yellow(s):
        return "\033[93m{}\033[0m".format(s)
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
                print (Color.red(_("There was an error executing arp-scan.")))
                print ("  * "+_("Is the interface argument correct?."))    
                if os.path.exists("/usr/bin/arp-scan")==False:
                    print("  * "+_("I couldn't find /usr/bin/arp-scan.") + " " + _("Please install it or use the -m option."))
                sys.exit(2)
            for line in output.split("\n"):
                if line.find("\t")!=-1:
                    h=Device()
                    arr=line.split("\t")
                    h.ip=arr[0]
                    h.mac=arr[1]
                    h.oui=arr[2]
                    h.pinged=False
                    for k in self.known.arr:
                        if k.mac.upper()==h.mac.upper():
                            h.alias=k.alias
                    self.arr.append(h)
            h=Device()
            h.ip=get_if_ip(args.interface)
            h.alias=_("This device")
            h.mac=get_if_mac(args.interface)
            h.oui=get_oui(h.mac)
            self.arr.append(h)
        else:#args.my=True            
            threads=[]
            if_ip=get_if_ip(args.interface)
            for addr in ipaddress.IPv4Network('192.168.1.0/24'):
                if str(addr)==if_ip :#Adds device if ip is interface ip and jumps it
                    h=Device()
                    h.ip=str(addr)
                    h.mac=get_if_mac(args.interface)
                    h.oui=get_oui(h.mac)
                    h.pinged=True     
                    self.arr.append(h)
                    continue
                t=TRequest(str(addr), args.interface,  TypesARP.Standard)
                t.start()
                threads.append(t)
                time.sleep(0.01)
                
            for t in threads:
                t.join()
                if t.mac!=None or t.pinged==True:
                    h=Device()
                    h.ip=t.ip
                    h.mac=t.mac
                    h.oui=t.oui
                    h.pinged=t.pinged
                    for k in self.known.arr:
                        if h.mac:
                            if k.mac.upper()==h.mac.upper():
                                h.alias=k.alias
                    self.arr.append(h)

    def max_len_oui(self):
        ma=max(len(h.oui) for h in self.arr)
        if ma==0:
            return 14
        return ma

    def max_len_alias(self):
        l=14
        for h in self.arr:
            if h.alias:
                le=len(h.alias)
                if l<le:
                    l=le
        return l
        
    def order_by_ip(self):
        self.arr=sorted(self.arr, key=lambda k: (int(k.ip.split(".")[0]), int(k.ip.split(".")[1]), int(k.ip.split(".")[2]), int(k.ip.split(".")[3])))
        
    def print(self):
        numpings=0
        if_ip=get_if_ip(args.interface)
        maxalias=self.max_len_alias()
        maxoui=self.max_len_oui()
        self.order_by_ip()
        print (Color.bold("="*(16+2+17+2+maxalias+2+maxoui)))
        print (Color.bold(_("{} DEVICES IN LAN FROM {} INTERFACE AT {}").format(self.length(), args.interface.upper(), str(datetime.datetime.now())[:-7]).center (6+15+17+maxalias+maxoui)))
        print (Color.bold("{}  {}  {}  {}".format(" IP ".center(16,'=')," MAC ".center(17,'='), " ALIAS ".center(maxalias,'='), " HARDWARE ".center(maxoui,'='))))
        for h in self.arr:
            if h.mac==None:
                mac="                 "
            else:
                mac=h.mac
            if h.pinged==True:
                numpings=numpings+1
                pinged="*"
            else:
                pinged=" "
            if h.ip==if_ip:
                print ("{}  {}  {}  {}".format(Color.pink((pinged+h.ip).ljust(16)), Color.pink(mac.center(17)),   Color.pink(_("This device").ljust(maxalias)), Color.pink(h.oui.ljust(maxoui))))
            else:
                if h.alias:
                    mac=Color.green(mac)
                    alias=h.alias
                else:
                    mac=Color.red(mac)
                    alias=" "     
                print ("{}  {}  {}  {}".format((pinged+h.ip).ljust(16), mac.center(17),   Color.yellow(alias.ljust(maxalias)), h.oui.ljust(maxoui)))    
        print (Color.bold("="*(16+2+17+2+maxalias+2+maxoui)))        
        if args.my:
            print (_("There was reply to a ping from IP address with '*' ({} pings).").format(numpings))

class Device:
    def __init__(self):
        self.ip=None
        self.mac=None
        self.oui=None
        self.alias=None
        self.pinged=False

class TRequest(threading.Thread):
    def __init__(self, ip, if_name, arp_type):
        threading.Thread.__init__(self)
        self.arp_type = arp_type
        self.if_name=if_name
        self.if_ip = get_if_ip(self.if_name) 
        self.ip = ip
        self.mac=None#Mac address string
        self.oui=""#String hardware name
        self.arp_sent_frame=None
        self.arp_received_frame=None
        self.icmp_sent_frame=None
        self.icmp_received_frame=None
        self.pinged=False

    def ping_process(self):
        for i in range(1):
            if self.pinged==False:
                try: 
                    output=subprocess.call(["ping", "-c", "1", "-W", "1", self.ip], shell=False, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                    if output==0:
                        self.pinged=True
                except: #if exit is not 0
                    pass
                time.sleep(.1*i)
            else:
                break    

    def run(self):    
        self.arp_process()
        self.ping_process()

#        if self.ip in ("192.168.1.12", "192.168.1.102"):
#            print ("""-------------------------------------------- {} from interface {}
#Sent frame:
#{}
#Received frame:
#{}
#Macs: {}   {}   {}   {}
#--------------------------------------------""".format(self.ip,  self.if_ip, self.arp_sent_frame,  self.arp_received_frame, self.bytes2mac(self.arp_received_frame[0:6]),self.bytes2mac(self.arp_received_frame[6:12]), self.bytes2mac(self.arp_received_frame[22:28]),   self.bytes2mac(self.arp_received_frame[32:38])))


    def arp_process(self):        
        def arp_send():
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
    
            frame2=b"\xff\xff\xff\xff\xff\xff"+ \
                socket_arp.getsockname()[4] + \
                b"\x08\x06" + \
                b"\x00\x01" + \
                b"\x08\x00" + \
                b"\x06" + \
                b"\x04" + \
                b"\x00\x01" + \
                socket_arp.getsockname()[4] + \
                self.ip2bytes(self.if_ip) + \
                b"\x00\x00\x00\x00\x00\x00" + \
                self.ip2bytes(self.ip)
            self.arp_sent_frame=frame2
            socket_arp.send(frame2)
        def arp_receive():
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
            frame = socket_arp.recv(1024)    
            self.arp_received_frame=frame
            
            if frame[12:14] != b'\x08\x06': # Checks ARP protocol
                return False
    
            if frame[20:22] != b'\x00\x02': #Checks ARP Answer
                return False
    
            #Compare ip whith ip of the trame
            if self.ip==self.bytes2ip(frame[28:32]):    
                self.mac=self.bytes2mac(frame[22:28])
                self.oui=get_oui(self.mac)
                return True
                
            return False
        ##############################################
        for i in range(3):
            if self.mac==None:
                socket_arp = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.SOCK_RAW)
                socket_arp.bind((self.if_name, socket.SOCK_RAW)) 
                arp_send()
                time.sleep(.1*i)
                arp_receive()
                socket_arp.close()

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


def main():
    parser=argparse.ArgumentParser(prog='devicesinlan', description=_('Show devices in a LAN making an ARP and a ICMP request to find them'),  epilog=_("Developed by Mariano Muñoz 2015 ©"))
    parser.add_argument('-v', '--version', action='version', version="0.5.0")
    parser.add_argument('-m', '--my', help=_('Use my own arp scanner'), action='store_true')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-i',  '--interface', help=_('Net interface name'),  default='eth0')
    group.add_argument('-a',  '--add', help=_('Add a known device'), action='store_true')
    group.add_argument('-r',  '--remove', help=_('Remove a known device'), action='store_true')
    group.add_argument('-l',  '--list', help=_('List known device'), action='store_true')
    global args
    args=parser.parse_args()
      
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
    if args.my==True:
        scanner="DevicesInLAN"
    else:
        scanner="arp-scan"
    print (_("It took {} with {} scanner.").format (datetime.datetime.now()-inicio, Color.yellow(scanner)))

def ping_command():
    """If detects OS ping, it uses it
    None: Not found
    String Comand to use"""
    if os.path.exists("/bin/ping"):
        return "ping"
    return None
    
def get_oui(mac):
    mac=mac.replace(":", "").upper()[:-6]
    if len(mac)!=6:#No tiene los 3 primeros n´umeros de la mac
        return ""
    f=open("/usr/share/devicesinlan/ieee-oui.txt", "rb")
    for line in f.readlines():
        if line.find(mac.encode())!=-1:
            return line.decode('utf-8').split("\t")[1][:-1].upper()
            
def get_if_ip(name):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    r=socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        name.encode('utf-8')+b'\x00'*(256-len(name))#            struct.pack('256s', self.if_name[:15])
    )[20:24])
    return r
    
def get_if_mac(name):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(), 0x8927,  name.encode('utf-8')+b'\x00'*(256-len(name)))
    return ''.join(['%02x:' % b for b in info[18:24]])[:-1]
    
##############################################

args=None
known=None
if __name__ == "__main__":
    main()
