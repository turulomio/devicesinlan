import codecs
import datetime
import threading
import gettext
import netifaces
import os
import re
import platform
import subprocess
import time
import socket
from PyQt5.QtCore import QCoreApplication, QSettings, QTranslator, Qt
from PyQt5.QtWidgets import QTableWidgetItem, QApplication
from PyQt5.QtGui import QColor,  QPixmap, QIcon
import ipaddress
version="0.8.0"
dateversion=datetime.date(2017, 1, 18)


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
        self.settings=QSettings()
        self.translator=QTranslator()
        self.interfaces=SetInterfaces(self)
        self.interfaces.load_all()
        self.types=SetDeviceTypes(self)
        self.types.load_all()
        
    def change_language(self, language):  
        """language es un string"""  
        urls= ["i18n/devicesinlan_" + language + ".qm","/usr/share/devicesinlan/devicesinlan_" + language + ".qm"]
        for url in urls:
            if os.path.exists(url)==True:
                break
        self.translator.load(url)
        QCoreApplication.installTranslator(self.translator);

class DeviceType:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.name=None
        
    def init__create(self, id, name):
        self.id=id
        self.name=name
        return self
        
    def qpixmap(self):
        if self.id==0:
            return QPixmap(":/devicesinlan.png")
        elif self.id==1:
            return QPixmap(":/devices/video-television.png")
        elif self.id==2:
            return QPixmap(":/devices/camera-photo.png")
        elif self.id==3:
            return QPixmap(":/devices/camera-web.png")
        elif self.id==4:
            return QPixmap(":/devices/computer-laptop.png")
        elif self.id==5:
            return QPixmap(":/devices/computer.png")
        elif self.id==6:
            return QPixmap(":/devices/modem.png")
        elif self.id==7:
            return QPixmap(":/devices/smartphone.png")
        elif self.id==8:
            return QPixmap(":/devices/printer.png")
        elif self.id==9:
            return QPixmap(":/devices/tablet.png")
        elif self.id==10:
            return QPixmap(":/devices/usb-wireless.png")
        return None
        
    def qicon(self):
        ico = QIcon()
        ico.addPixmap(self.qpixmap(), QIcon.Normal, QIcon.Off) 
        return ico


class SetDeviceTypes:
    def __init__(self, mem):
        self.mem=mem
        self.arr=[]
        
    def length(self):
        return len (self.arr)
        
    def find_by_id(self, id):
        if id==None:
            id=0
        for type in self.arr:
            if type.id==id:
                return type
        return None
        
    def append(self, o):
        self.arr.append(o)
        
    def load_all(self):
        self.append(DeviceType(self.mem).init__create(0, QApplication.translate("devicesinlan", "Unknown")))
        self.append(DeviceType(self.mem).init__create(1, QApplication.translate("devicesinlan", "Television")))
        self.append(DeviceType(self.mem).init__create(2, QApplication.translate("devicesinlan", "Digital camera")))
        self.append(DeviceType(self.mem).init__create(3, QApplication.translate("devicesinlan", "Web camera")))
        self.append(DeviceType(self.mem).init__create(4, QApplication.translate("devicesinlan", "Laptop")))
        self.append(DeviceType(self.mem).init__create(5, QApplication.translate("devicesinlan", "Computer")))
        self.append(DeviceType(self.mem).init__create(6, QApplication.translate("devicesinlan", "Modem")))
        self.append(DeviceType(self.mem).init__create(7, QApplication.translate("devicesinlan", "Smartphone")))
        self.append(DeviceType(self.mem).init__create(8, QApplication.translate("devicesinlan", "Printer")))
        self.append(DeviceType(self.mem).init__create(9, QApplication.translate("devicesinlan", "Tablet")))
        self.append(DeviceType(self.mem).init__create(10, QApplication.translate("devicesinlan", "Wireless USB dongle")))

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
            combo.addItem(l.qicon(), l.name, l.id)
        if selected==None:
            selected=0
        if selected!=None:
                combo.setCurrentIndex(combo.findData(selected))        
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
            except:
                pass
        
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
                
class ArpScanMethod:
    PingArp=0 #Ping + ARP
    Arping=1 #Arping utility
    Own=2#My own scan
    ArpScanner=3#Arpescanner
                
class SetDevices:
    def __init__(self, mem):
        """This constructor load /etc/devicesinlan/known.txt and executes arp-scan and parses its result"""
        self.mem=mem
        self.arr=[]
        self.selected=None


    def init__from_settings(self):
        """
            Load all devices in settings
        """
        
        self.mem.settings.beginGroup("DeviceAlias")#Las key son sin DevicesAlias ahora
        for key in self.mem.settings.childKeys():
            d=Device(self.mem)
            d.mac=d.macwith2points(key)
            d.alias=self.mem.settings.value("{}".format(d.macwithout2points(d.mac.upper())), None)
            d.oui=get_oui(d.mac)
            self.arr.append(d)
        self.mem.settings.endGroup()
        
        #Carga los types antes no se pod´ia
        for d in self.arr:
            d.type=self.mem.types.find_by_id(int(self.mem.settings.value("DeviceType/{}".format(d.macwithout2points(d.mac.upper())), 0)))
            

    def setMethod(self, arpscanmethod):
        if arpscanmethod==ArpScanMethod.PingArp:
            self.pingarp()
        elif arpscanmethod==ArpScanMethod.Arping:
            pass
        elif arpscanmethod==ArpScanMethod.Own:
            self.own()
        elif arpscanmethod==ArpScanMethod.ArpScanner:
            pass
            


    def length(self):
        """Number of devices in the set"""
        return len(self.arr)
        
    def own(self):
        """Load Devices from arpscan output"""
#            output=subprocess.check_output(["arp-scan", "--interface", self.mem.args.interface, "--localnet", "--ignoredups"]).decode('UTF-8')
        threads=[]
        for addr in ipaddress.IPv4Network("{}/{}".format(self.mem.interfaces.selected.ip, self.mem.interfaces.selected.mask), strict=False):
            if str(addr)==self.mem.interfaces.selected.ip :#Adds device if ip is interface ip and jumps it
                h=Device(self.mem)
                h.ip=str(addr)
                h.mac=self.mem.interfaces.selected.mac
                h.oui=get_oui(h.mac)
                h.pinged=True     
                h.alias=self.mem.settings.value("DeviceAlias/{}".format(h.macwithout2points(h.mac.upper())), None)
                h.type=self.mem.types.find_by_id(int(self.mem.settings.value("DeviceType/{}".format(h.macwithout2points(h.mac.upper())), 0)))
                self.arr.append(h)
                continue
            t=TRequest(str(addr), self.mem.interfaces.selected,  TypesARP.Standard)
            t.start()
            threads.append(t)
            time.sleep(0.01)
            
        for t in threads:
            t.join()
            if t.mac!=None or t.pinged==True:
                h=Device(self.mem)
                h.ip=t.ip
                h.mac=t.mac
                h.oui=t.oui
                h.pinged=t.pinged
                if h.mac:
                    h.alias=self.mem.settings.value("DeviceAlias/{}".format(h.macwithout2points(h.mac.upper())), None)
                    h.type=self.mem.types.find_by_id(int(self.mem.settings.value("DeviceType/{}".format(h.macwithout2points(h.mac.upper())), 0)))
                self.arr.append(h)

        
    def pingarp(self):
        """Load Devices from arpscan output"""
        threads=[]
#        t=TRequestPingArp("192.168.1.100")
#        t.start()
#        threads.append(t)
#        t.join()
#        t=TRequestPingArp("192.168.1.167")
#        t.start()
#        threads.append(t)
        
        for addr in ipaddress.IPv4Network("{}/{}".format(self.mem.interfaces.selected.ip, self.mem.interfaces.selected.mask), strict=False):
            if str(addr)==self.mem.interfaces.selected.ip :#Adds device if ip is interface ip and jumps it
                h=Device(self.mem)
                h.ip=str(addr)
                h.mac=self.mem.interfaces.selected.mac
                h.oui=get_oui(h.mac)
                h.pinged=True     
                h.alias=self.mem.settings.value("DeviceAlias/{}".format(h.macwithout2points(h.mac.upper())), None)
                h.type=self.mem.types.find_by_id(int(self.mem.settings.value("DeviceType/{}".format(h.macwithout2points(h.mac.upper())), 0)))
                self.arr.append(h)
                continue
            t=TRequestPingArp(str(addr))
            t.start()
            threads.append(t)
            
        for t in threads:
            t.join()
            if t.mac!=None or t.pinged==True:
                h=Device(self.mem)
                h.ip=t.ip
                h.mac=t.mac
                h.oui=t.oui
                h.pinged=t.pinged
                if h.mac:
                    h.alias=self.mem.settings.value("DeviceAlias/{}".format(h.macwithout2points(h.mac.upper())), None)
                    h.type=self.mem.types.find_by_id(int(self.mem.settings.value("DeviceType/{}".format(h.macwithout2points(h.mac.upper())), 0)))
                self.arr.append(h)


    def max_len_oui(self):
        max=15
        for h in self.arr:
            if len(str(h.oui))>max:
                max=len(str(h.oui))
        return max

    def max_len_type(self):
        max=0
        for h in self.arr:
            if len(h.type.name)>max:
                max=len(h.type.name)
        return max

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
    def order_by_alias(self):
        self.arr=sorted(self.arr, key=lambda k: k.alias)
        
    def print(self):
        maxalias=self.max_len_alias()
        maxoui=self.max_len_oui()
        maxtype=self.max_len_type()
        self.order_by_ip()
        print (Color.bold("="*(16+2+maxtype+2+17+2+maxalias+2+maxoui)))
        print (Color.bold(QApplication.translate("devicesinlan","{} DEVICES IN LAN FROM {} INTERFACE AT {}").format(self.length(), self.mem.interfaces.selected.id.upper(), str(datetime.datetime.now())[:-7]).center (6+15+17+maxalias+maxoui)))
        print (Color.bold("{}  {}  {}  {}  {}".format(" IP ".center(16,'='),"TYPE".center(maxtype,"=")," MAC ".center(17,'='), " ALIAS ".center(maxalias,'='), " HARDWARE ".center(maxoui,'='))))
        for h in self.arr:
            if h.ip==self.mem.interfaces.selected.ip:
                print ("{}  {}  {}  {}  {}".format(Color.pink(h.ip.ljust(16)), Color.pink(h.type.name.ljust(maxtype)), Color.pink(h.mac.center(17)),   Color.pink(QApplication.translate("devicesinlan","This device").ljust(maxalias)), Color.pink(h.oui.ljust(maxoui))))
            else:
                if h.alias:
                    mac=Color.green(h.mac)
                    alias=h.alias
                else:
                    mac=Color.red(h.mac)
                    alias=" "     
                print ("{}  {}  {}  {}".format(h.ip.ljust(16), h.type.name.ljust(maxtype),  mac.center(17),   Color.yellow(alias.ljust(maxalias)), str(h.oui).ljust(maxoui)))    
        print (Color.bold("="*(16+2+maxtype+2+17+2+maxalias+2+maxoui)))
                

    def print_devices_from_settings(self):
        """
            Print list of all database devices
        """
        maxalias=self.max_len_alias()
        maxoui=self.max_len_oui()
        maxtype=self.max_len_type()
        self.order_by_alias()
        print (Color.bold("="*(maxtype+2+17+2+maxalias+2+maxoui)))
        print (Color.bold(QApplication.translate("devicesinlan","{} DEVICES IN DATABASE AT {}").format(self.length(), str(datetime.datetime.now())[:-7]).center (6+15+17+maxalias+maxoui)))        
        print (Color.bold("{}  {}  {}  {}".format(" TYPE ".center(maxtype,'=')," MAC ".center(17,'='), " ALIAS ".center(maxalias,'='), " HARDWARE ".center(maxoui,'='))))
        for h in self.arr:
            mac=Color.green(h.mac)
            print ("{}  {}  {}  {}".format(h.type.name.ljust(maxtype), mac.center(17),   Color.yellow(h.alias.ljust(maxalias)), str(h.oui).ljust(maxoui)))    
        print (Color.bold("="*(maxtype+2+17+2+maxalias+2+maxoui)))

    def qtablewidget(self, table):
        self.order_by_ip() 
        ##HEADERS
        table.setColumnCount(4)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(QApplication.translate("devicesinlan","IP" )))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(QApplication.translate("devicesinlan","MAC" )))
        table.setHorizontalHeaderItem(2,  QTableWidgetItem(QApplication.translate("devicesinlan","Alias" )))
        table.setHorizontalHeaderItem(3, QTableWidgetItem(QApplication.translate("devicesinlan","Hardware" )))
        ##DATA 
        table.clearContents()   
        table.setRowCount(self.length())
        for rownumber, h in enumerate(self.arr):
            alias=""
            if h.alias!=None:
                alias=h.alias
            table.setItem(rownumber, 0, qleft(h.ip))
            table.setItem(rownumber, 1, qleft(h.mac))
            table.setItem(rownumber, 2, qleft(alias))
            table.setItem(rownumber, 3, qleft(h.oui))
            if h.alias!=None:
                for i in range(0, table.columnCount()):
                    table.item(rownumber, i).setBackground( QColor(182, 255, 182))       
            else:
                for i in range(0, table.columnCount()):
                    table.item(rownumber, i).setBackground( QColor(255, 182, 182))       
            if h.type!=None:
                table.item(rownumber, 1).setIcon(h.type.qicon())

class Device:
    def __init__(self, mem):
        self.mem=mem
        self.ip=None
        self.mac=None
        self.oui=None
        self.alias=None
        self.pinged=False
        self.type=None
        
        
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

        
    def link(self):
        self.mem.settings.setValue("DeviceAlias/{}".format(self.macwithout2points(self.mac.upper())), self.alias)
        self.mem.settings.setValue("DeviceType/{}".format(self.macwithout2points(self.mac.upper())), self.type.id)
        
    def unlink(self):
        self.mem.settings.remove("DeviceAlias/{}".format(self.macwithout2points(self.mac.upper())))
        self.mem.settings.remove("DeviceType/{}".format(self.macwithout2points(self.mac.upper())))
        self.type=None
        self.alias=None
        
    def macwith2points(self, macwithout):
        macwith=""
        for i in range(6):
            macwith=macwith+macwithout[i*2]+macwithout[i*2+1]+":"
        return macwith[:-1]
        
    def macwithout2points(self, macwith):
        return macwith.replace(":", "")

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
        
        


class TRequestPingArp(threading.Thread):
    def __init__(self, ip):
        threading.Thread.__init__(self)
        self.ip = ip
        self.mac=None#Mac address string
        self.oui=""#String hardware name
        self.pinged=False
        
    def run(self):
        #PING
        if platform.system()=="Windows":
            CREATE_NO_WINDOW=0x08000000
            output=subprocess.check_output(["ping", "-n", "1", self.ip], shell=False, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
            #if there are two "bytes" words, the ping was made correctly
            entrecomas=output.split(b"bytes")
            if len(entrecomas)==3:
                self.pinged=True
        else:
            output=subprocess.call(["ping", "-c", "1", "-W", "1", self.ip], shell=False, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            if output==0:
                self.pinged=True
        #ARP
        if self.pinged==True:
            if platform.system()=="Windows":
                arpexit=subprocess.check_output(["arp", "-a",  self.ip], creationflags=CREATE_NO_WINDOW)
                for s in arpexit.split(b" "):
                    if len(s)==17 and s.find(b"-")!=-1:
                        self.mac=s.decode()
                        self.oui=get_oui(self.mac)
            else:
                arpexit=subprocess.check_output(["arp", self.ip])
                for s in arpexit.decode('utf-8').split(" "):
                    if len(s)==17 and s.find(":")!=-1:
                        self.mac=s
                        self.oui=get_oui(self.mac)

def ping_command():
    """If detects OS ping, it uses it
    None: Not found
    String Comand to use"""
    if os.path.exists("/bin/ping"):
        return "ping"
    return None
    
def get_oui(mac):
    if platform.system()=="Windows":
        url="ieee-oui.txt"
        mac=mac.replace("-", "").upper()[:-6]
    elif platform.system()=="Linux":
        mac=mac.replace(":", "").upper()[:-6]
        url="/usr/share/devicesinlan/ieee-oui.txt"
    if len(mac)!=6:#No tiene los 3 primeros n´umeros de la mac
        return ""
    f=open(url, "rb")
    for line in f.readlines():
        if line.find(mac.encode())!=-1:
            return line.decode('utf-8').split("\t")[1][:-2].upper()

    
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
