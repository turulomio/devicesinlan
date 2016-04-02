import codecs
import datetime
import threading
import gettext
import netifaces
import os
import platform
import subprocess
import time
import re
import socket
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import ipaddress
version="0.6.0.1"
dateversion=datetime.date(2016, 3, 27)


# I had a lot of problems with UTF-8. LANG must be es_ES.UTF-8 to work
gettext.textdomain('devicesinlan')
gettext.bindtextdomain('devicesinlan', "./")
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

class Mem:
    def __init__(self):
        self.known=SetKnownDevices(self)
        self.settings=QSettings()
        self.translator=QTranslator()
        self.interfaces=SetInterfaces(self)
        self.interfaces.load_all()
        self.interfaces.print()
        
    def change_language(self, language):  
        """language es un string"""  
        urls= ["i18n/devicesinlan_" + language + ".qm","/usr/share/devicesinlan/devicesinlan_" + language + ".qm"]
        for url in urls:
            if os.path.exists(url)==True:
                print ("Found {} from {}".format(url,  os.getcwd()))
                break
            else:
                print ("Not found {} from {}".format(url,  os.getcwd()))        
            
        self.translator.load(url)
        QCoreApplication.installTranslator(self.translator);

class Interface:
    def __init__(self, mem):
        self.mem=mem
        self.id=None#Id numerico de Windows o id de Linux
        self.name=None
        self.ip=None
        self.mac=None
        self.mask=None
        self.broadcast=None
        
    def init__create(self, id, name, ip, mac, mask, broadcast):
        self.id=id
        self.name=name
        self.ip=ip
        self.mac=mac
        self.mask=mask
        self.broadcast=broadcast
        return self
        
    def __str__(self):
        return (QApplication.translate("devicesinlan","Interface {} ({}) with ip {}/{} and mac {}".format(self.name, self.id, self.ip, self.mask, self.mac)))
        
class SetInterfaces:
    def __init__(self, mem):
        self.arr=[]
        self.mem=mem
        self.selected=None
        
    def length(self):
        return len(self.arr)
        
    def append(self, o):
        self.arr.append(o)
        
    def find_by_id(self, id):
        for interface in self.arr:
            if interface.id==id:
                return interface
        return None
        
    def load_all(self):   
        if platform.system()=="Windows":
            idformac=-1000
        elif platform.system()=="Linux":
            idformac=netifaces.AF_PACKET
        for iface in netifaces.interfaces():
            try:
                for i, ifa in enumerate(netifaces.ifaddresses(iface)[netifaces.AF_INET]):#Puede haber varias IP en interfaz: Af_inet ES PARA IPV4
                    if netifaces.ifaddresses(iface)[netifaces.AF_INET][i]["addr"]!="127.0.0.1":
                        self.append(Interface(self.mem).init__create(
                            iface, 
                            None, 
                            netifaces.ifaddresses(iface)[netifaces.AF_INET][i]["addr"],
                            netifaces.ifaddresses(iface)[idformac][i]["addr"], 
                            netifaces.ifaddresses(iface)[netifaces.AF_INET][i]["netmask"],
                            netifaces.ifaddresses(iface)[netifaces.AF_INET][i]["broadcast"]  
                        ))
#                        print("Done")
#                    else:
#                        print ("Eliminating loopbak")
            except:
                pass
#                print (QApplication.translate("devicesinlan", "Interface not well parsed and not selected"))
        
    def print(self):
        for interface in self.arr:
            print ( interface)

    def order_by_name(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda c: c.name,  reverse=False)       
            return True
        except:
            return False       
            
    def qcombobox(self, combo, selected=None):
        """Selected is id"""
        self.order_by_name()
        for l in self.arr:
            if l.name==None:
                name="Interfaz sin nombre"
            else:
                name=l.name
            combo.addItem(name, l.id)
        if selected!=None:
                combo.setCurrentIndex(combo.findData(selected))        
class SetDevices:
    def __init__(self, mem):
        """This constructor load /etc/devicesinlan/known.txt and executes arp-scan and parses its result"""
        self.mem=mem
        self.arr=[]
        self.known=SetKnownDevices(self.mem)
        self.arp_scanner()#From arp_scan
        self.selected=None

    def length(self):
        """Number of devices in the set"""
        return len(self.arr)
        
    def arp_scanner(self):
        """Load Devices from arpscan output"""
#            output=subprocess.check_output(["arp-scan", "--interface", self.mem.args.interface, "--localnet", "--ignoredups"]).decode('UTF-8')
        threads=[]
        for addr in ipaddress.IPv4Network("{}/{}".format(self.mem.interfaces.selected.ip, self.mem.interfaces.selected.mask), strict=False):
            if str(addr)==self.mem.interfaces.selected.ip :#Adds device if ip is interface ip and jumps it
                h=Device()
                h.ip=str(addr)
                h.mac=self.mem.interfaces.selected.mac
                h.oui=get_oui(h.mac)
                h.pinged=True     
                self.arr.append(h)
                continue
            t=TRequest(str(addr), self.mem.interfaces.selected,  TypesARP.Standard)
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
        maxalias=self.max_len_alias()
        maxoui=self.max_len_oui()
        self.order_by_ip()
        print (Color.bold("="*(16+2+17+2+maxalias+2+maxoui)))
        print (Color.bold(QApplication.translate("devicesinlan","{} DEVICES IN LAN FROM {} INTERFACE AT {}").format(self.length(), self.mem.interfaces.selected.id.upper(), str(datetime.datetime.now())[:-7]).center (6+15+17+maxalias+maxoui)))
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
            if h.ip==self.mem.interfaces.selected.ip:
                print ("{}  {}  {}  {}".format(Color.pink((pinged+h.ip).ljust(16)), Color.pink(mac.center(17)),   Color.pink(QApplication.translate("devicesinlan","This device").ljust(maxalias)), Color.pink(h.oui.ljust(maxoui))))
            else:
                if h.alias:
                    mac=Color.green(mac)
                    alias=h.alias
                else:
                    mac=Color.red(mac)
                    alias=" "     
                print ("{}  {}  {}  {}".format((pinged+h.ip).ljust(16), mac.center(17),   Color.yellow(alias.ljust(maxalias)), h.oui.ljust(maxoui)))    
        print (Color.bold("="*(16+2+17+2+maxalias+2+maxoui)))        
        print (QApplication.translate("devicesinlan","There was reply to a ping from IP address with '*' ({} pings).").format(numpings))
            
    def qtablewidget(self, table):
        numpings=0
#        if_ip=get_if_ip(self.mem.args.interface)
        self.order_by_ip() 
        ##HEADERS
        table.setColumnCount(5)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("devicesinlan","IP" )))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("devicesinlan","MAC" )))
        table.setHorizontalHeaderItem(2,  QTableWidgetItem(QApplication.translate("devicesinlan","Alias" )))
        table.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("devicesinlan","Hardware" )))
        table.setHorizontalHeaderItem(4, QTableWidgetItem(QApplication.translate("devicesinlan","Ping" )))
        ##DATA 
#        table.applySettings()
        table.clearContents()   
        table.setRowCount(self.length())
#        self.sort()
        for rownumber, h in enumerate(self.arr):
            alias=""
            if h.alias!=None:
                alias=h.alias
            table.setItem(rownumber, 0, qleft(h.ip))
            table.setItem(rownumber, 1, qleft(h.mac))
            table.setItem(rownumber, 2, qleft(alias))
            table.setItem(rownumber, 3, qleft(h.oui))
            table.setItem(rownumber, 4,  qbool(h.pinged))
            if h.pinged==True:
                numpings=numpings+1
            if h.alias!=None:
                for i in range(0, table.columnCount()):
                    table.item(rownumber, i).setBackground( QColor(182, 255, 182))       
            else:
                for i in range(0, table.columnCount()):
                    table.item(rownumber, i).setBackground( QColor(255, 182, 182))       


class Device:
    def __init__(self):
        self.ip=None
        self.mac=None
        self.oui=None
        self.alias=None
        self.pinged=False

class TRequest(threading.Thread):
    def __init__(self, ip, interface, arp_type):
        threading.Thread.__init__(self)
        self.arp_type = arp_type
        self.interface=interface
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
                self.ip2bytes(self.interface.ip) + \
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
                socket_arp.bind((self.interface.id, socket.SOCK_RAW)) 
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
            self.mac=input(Color.bold(QApplication.translate("devicesinlan","Input the MAC of the known device (xx:xx:xx:xx:xx:xx): "))).lower()
            if self.validate_mac(self.mac):
                validated=True
            else:
                print (Color.red(QApplication.translate("devicesinlan","You need to insert a mac with the next format: 2a:3b:4c:5d:6e:7a")))

    def insert_alias(self):
        validated=False
        while validated==False:
            self.alias=input(Color.bold(QApplication.translate("devicesinlan","Input an alias of the known device: ")))
            if self.validate_alias(self.alias):
                validated=True
            else:
                print (Color.red(QApplication.translate("devicesinlan","You need to add an alias")))

class SetKnownDevices:
    def __init__(self, mem):
        self.mem=mem
        self.arr=[]
        self.load()
        
    def append(self, k):
        if self.exists(k):
            self.remove_mac(k.mac)#Sustitute it
            print ("Mac already exists, overwriting it")
        self.arr.append(k)
    def print(self):
        maxalias=self.max_len_alias()     
        print (Color.bold(QApplication.translate("devicesinlan","KNOWN DEVICES BY USER AT {}").format( str(datetime.datetime.now())[:-7]).center (17+2+maxalias)))
        print ()
        print (Color.bold("{}  {}".format(" MAC ".center(17,'='), " ALIAS ".center(maxalias,'='))))
        self.mem.known.order_by_alias()
        for k in self.mem.known.arr:
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
        if platform.system()=="Windows":
            f=open(os.path.expanduser("~/.devicesinlan/known.txt"),"r")
        elif platform.system()=="Linux":
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
                    print(QApplication.translate("devicesinlan","Error parsing {}").format(l))
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
        if platform.system()=="Windows":
            f=open(os.path.expanduser("~/.devicesinlan/known.txt"),"w")
        elif platform.system()=="Linux":
            f=open("/etc/devicesinlan/known.txt","w")
        for k in self.arr:
            f.write("{} = {}\n".format(k.mac.lower(), k.alias))
        f.close()        
        
    def order_by_alias(self):
        self.arr=sorted(self.arr, key=lambda k: k.alias)

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

    
def qbool(bool):
    """Prints bool and check. Is read only and enabled"""
    a=QTableWidgetItem()
    a.setFlags( Qt.ItemIsSelectable |  Qt.ItemIsEnabled )#Set no editable
    if bool:
        a.setCheckState(Qt.Checked);
        a.setText(QApplication.translate("devicesinlan","True"))
    else:
        a.setCheckState(Qt.Unchecked);
        a.setText(QApplication.translate("devicesinlan","False"))
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignCenter)
    return a
    
def qleft(string):
    a=QTableWidgetItem(str(string))
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignLeft)
    return a
