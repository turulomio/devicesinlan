import codecs
import datetime
import threading
import logging
import netifaces
import os
import re
import platform
import subprocess
import time
import socket
from PyQt5.QtCore import QCoreApplication, QSettings, QTranslator, Qt, QObject
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from PyQt5.QtGui import QColor,  QPixmap, QIcon
from colorama import Style, Fore
from concurrent.futures import ThreadPoolExecutor,  as_completed
from xml.dom import minidom
from uuid import  uuid4
from urllib.request import urlopen
import ipaddress
version = "1.0.1"
dateversion=datetime.date(2017, 2, 9)

class TypesARP:
    Gratuitous = 1
    Standard = 2

class Mem(QObject):
    def __init__(self):
        QObject.__init__(self)
        self.settings=QSettings()
        self.translator=QTranslator()
        self.interfaces=SetInterfaces(self)
        self.interfaces.load_all()
        self.types=SetDeviceTypes(self)
        self.types.load_all()

    def setApp(self, app):
        self.app=app#Link to app

    def setInstallationUUID(self):
        if self.settings.value("frmMain/uuid", "None")=="None":
            self.settings.setValue("frmMain/uuid", str(uuid4()))
        url='http://devicesinlan.sourceforge.net/php/devicesinlan_installations.php?uuid={}&version={}'.format(self.settings.value("frmMain/uuid"), version)
        try:
            web=b2s(urlopen(url).read())
        except:
            web=None
        logging.info(web)       

    def change_language(self, language):  
        """language es un string"""  
        urls= ["i18n/devicesinlan_" + language + ".qm","/usr/share/devicesinlan/devicesinlan_" + language + ".qm"]
        for url in urls:
            if os.path.exists(url)==True:
                self.translator.load(url)
                QCoreApplication.installTranslator(self.translator)
                logging.info(self.tr("Language changed to {} using {}".format(language, url)))
                return
        if language!="en":
            logging.info(self.tr("Using default (en)."))
        else:
            logging.warning(Style.BRIGHT+ Fore.CYAN+ self.tr("Language ({}) couldn't be loaded in {}. Using default (en).".format(language, urls)))

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


class SetDeviceTypes(QObject):
    def __init__(self, mem):
        QObject.__init__(self)
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
        self.append(DeviceType(self.mem).init__create(0, self.tr( "Unknown")))
        self.append(DeviceType(self.mem).init__create(1, self.tr( "Television")))
        self.append(DeviceType(self.mem).init__create(2, self.tr( "Digital camera")))
        self.append(DeviceType(self.mem).init__create(3, self.tr( "Web camera")))
        self.append(DeviceType(self.mem).init__create(4, self.tr( "Laptop")))
        self.append(DeviceType(self.mem).init__create(5, self.tr( "Computer")))
        self.append(DeviceType(self.mem).init__create(6, self.tr( "Modem")))
        self.append(DeviceType(self.mem).init__create(7, self.tr( "Smartphone")))
        self.append(DeviceType(self.mem).init__create(8, self.tr( "Printer")))
        self.append(DeviceType(self.mem).init__create(9, self.tr( "Tablet")))
        self.append(DeviceType(self.mem).init__create(10, self.tr( "Wireless USB dongle")))

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
class Interface(QObject):
    def __init__(self, mem):
        QObject.__init__(self)
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
        return (self.tr("Interface {} ({}) with ip {}/{} and mac {}".format(self.name, self.id, self.ip, self.mask, self.mac)))
        
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
        i=1
        for interface in self.arr:
            print (Style.BRIGHT + "{}. {} ({}/{} and MAC: {})".format(i, Style.BRIGHT+ Fore.GREEN+str(interface.id), interface.ip, interface.mask, interface.mac))
            i=i+1

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
                
class SetDevices(QObject):
    def __init__(self, mem):
        """This constructor load /etc/devicesinlan/known.txt and executes arp-scan and parses its result"""
        QObject.__init__(self)
        self.mem=mem
        self.arr=[]
        self.selected=None
        self.isDatabase=False#Returns True if is init__from_settings

    def init__from_xml(self, filename):
        """
            Constructor thal load devices from a xml file. Used to import data from file
        """
        xmldoc = minidom.parse(filename)
        itemlist = xmldoc.getElementsByTagName('device')
        for item in itemlist:
            d=Device(self.mem)
            d.alias=item.attributes['alias'].value
            d.mac=item.attributes['mac'].value
            d.type=self.mem.types.find_by_id(int(item.attributes['type'].value))
            self.append(d)
        return self

    def init__from_settings(self):
        """
            Load all devices in settings
        """
        self.isDatabase=True
        self.mem.settings.beginGroup("DeviceAlias")#Las key son sin DevicesAlias ahora
        for key in self.mem.settings.childKeys():
            d=Device(self.mem)
            d.mac=d.macwith2points(key).upper()
            d.alias=self.mem.settings.value("{}".format(d.macwithout2points(d.mac.upper())), None)
            self.arr.append(d)
        self.mem.settings.endGroup()
        
        #Carga los types antes no se pod´ia
        for d in self.arr:
            d.type=self.mem.types.find_by_id(int(self.mem.settings.value("DeviceType/{}".format(d.macwithout2points(d.mac.upper())), 0)))
        return self
            

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
        """Load Devices from ping and my arp output"""
        threads=[]
        for addr in ipaddress.IPv4Network("{}/{}".format(self.mem.interfaces.selected.ip, self.mem.interfaces.selected.mask), strict=False):
            if str(addr)==self.mem.interfaces.selected.ip :#Adds device if ip is interface ip and jumps it
                h=Device(self.mem)
                h.ip=str(addr)
                h.mac=self.mem.interfaces.selected.mac
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
                h.mac=t.mac.replace("-", ":")#This is for windows 
                h.oui=t.oui
                h.pinged=t.pinged
                if h.mac:
                    h.alias=self.mem.settings.value("DeviceAlias/{}".format(h.macwithout2points(h.mac.upper())), None)
                    h.type=self.mem.types.find_by_id(int(self.mem.settings.value("DeviceType/{}".format(h.macwithout2points(h.mac.upper())), 0)))
                self.arr.append(h)
                

        
    def pingarp(self):
        """Load Devices from scan with ping and arp commands output"""
        def get_ip_mac_pinged( ip):
            """
                Returns a list  [ip,mac,pinged]
            """
            pinged=False
            mac=None
            #PING
            if platform.system()=="Windows":
                CREATE_NO_WINDOW=0x08000000
                output=subprocess.call(["ping", "-n", "1", ip], shell=False, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
            else:
                output=subprocess.call(["ping", "-c", "1", "-W", "1", ip], shell=False, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            if output==0:
                pinged=True

            #ARP
            if pinged==True:
                if platform.system()=="Windows":
                    arpexit=subprocess.check_output(["arp", "-a",  ip], creationflags=CREATE_NO_WINDOW)
                    for s in arpexit.split(b" "):
                        if len(s)==17 and s.find(b"-")!=-1:
                            mac=s.decode().replace("-", ":").upper()
                else:
                    arpexit=subprocess.check_output(["/sbin/arp", ip])
                    for s in arpexit.decode('utf-8').split(" "):
                        if len(s)==17 and s.find(":")!=-1:
                            mac=s.upper()
            return(ip, mac, pinged)
            ###################################
        futures=[]
        concurrence=int(self.mem.settings.value("frmSettings/concurrence", 50))
        with ThreadPoolExecutor(max_workers=concurrence) as executor:
            for addr in ipaddress.IPv4Network("{}/{}".format(self.mem.interfaces.selected.ip, self.mem.interfaces.selected.mask), strict=False):
                if str(addr)==self.mem.interfaces.selected.ip :#Adds device if ip is interface ip and jumps it
                    h=Device(self.mem)
                    h.ip=str(addr)
                    h.mac=self.mem.interfaces.selected.mac.upper()
                    h.pinged=True     
                    h.alias=self.mem.settings.value("DeviceAlias/{}".format(h.macwithout2points(h.mac.upper())), None)
                    h.type=self.mem.types.find_by_id(int(self.mem.settings.value("DeviceType/{}".format(h.macwithout2points(h.mac.upper())), 0)))
                    self.arr.append(h)
                    continue
                else:
                    futures.append(executor.submit(get_ip_mac_pinged,  str(addr)))
                
            for i,  future in enumerate(as_completed(futures)):
                h=Device(self.mem)
                (h.ip, h.mac, h.pinged)=future.result()
                if h.mac!=None and h.pinged==True:
                    h.alias=self.mem.settings.value("DeviceAlias/{}".format(h.macwithout2points(h.mac.upper())), None)
                    h.type=self.mem.types.find_by_id(int(self.mem.settings.value("DeviceType/{}".format(h.macwithout2points(h.mac.upper())), 0)))
                    self.arr.append(h)#Solo si se da alias

    def max_len_oui(self):
        max=10
        for h in self.arr:
            if len(str(h.oui))>max:
                max=len(str(h.oui))
        return max

    def max_len_type(self):
        max=10
        for h in self.arr:
            if len(h.type.name)>max:
                max=len(h.type.name)
        return max
        
        
    def append(self, o):
        self.arr.append(o)
        
    def clear(self):
        for o in self.arr:
            self.arr.remove(o)
        
    def find_by_mac(self, mac):
        for d in self.arr:
            if d.mac.upper()==mac.upper():
                return d
        return None
        
    def link(self, o):
        if self.find_by_mac(o.mac)==None:#Insert in array, else is an update
            self.append(o)
        o.link()
        
    def unlink(self, o):
        o.unlink()
        if self.isDatabase==True:#Si es listado de database se debe borrar
            self.arr.remove(o)
        
    def max_len_alias(self):
        l=len(self.tr("This device"))
        for h in self.arr:
            if h.alias:
                le=len(h.alias)
                if l<le:
                    l=le
        return l
        
    def order_by_ip(self):
        self.arr=sorted(self.arr, key=lambda k: (int(k.ip.split(".")[0]), int(k.ip.split(".")[1]), int(k.ip.split(".")[2]), int(k.ip.split(".")[3])))
    def order_by_alias(self):
        try:
            self.arr=sorted(self.arr, key=lambda k: k.alias)
        except:
            pass
        
    def print(self):
        maxalias=self.max_len_alias()
        maxoui=self.max_len_oui()
        maxtype=self.max_len_type()
        maxlength=16+2+maxtype+2+17+2+maxalias+2+maxoui
        self.order_by_ip()
        print (Style.BRIGHT+ "="*(maxlength))
        print (Style.BRIGHT+ self.tr("{} DEVICES IN LAN FROM {} INTERFACE AT {}").format(self.length(), self.mem.interfaces.selected.id.upper(), str(datetime.datetime.now())[:-7]).center(maxlength))
        print (Style.BRIGHT+ "{}  {}  {}  {}  {}".format(" IP ".center(16,'='),"TYPE".center(maxtype,"=")," MAC ".center(17,'='), " ALIAS ".center(maxalias,'='), " HARDWARE ".center(maxoui,'=')))
        for h in self.arr:
            if h.ip==self.mem.interfaces.selected.ip:
                print ("{}  {}  {}  {}  {}".format(Style.BRIGHT+Fore.MAGENTA + h.ip.ljust(16), h.type.name.ljust(maxtype), h.mac.center(17),   self.tr("This device").ljust(maxalias), h.oui.ljust(maxoui)))
            else:
                if h.alias:
                    mac=Style.BRIGHT+Fore.GREEN + h.mac
                    alias=h.alias
                else:
                    mac=Style.BRIGHT+Fore.RED+ h.mac
                    alias=" "
                print ("{}  {}  {}  {}  {}".format(h.ip.ljust(16), h.type.name.ljust(maxtype),  mac.center(17),   Style.BRIGHT+Fore.YELLOW +  alias.ljust(maxalias), Style.NORMAL+Fore.WHITE+ h.oui.ljust(maxoui)))
        print (Style.BRIGHT + "="*(maxlength))
                

    def print_devices_from_settings(self):
        """
            Print list of all database devices
        """
        maxalias=self.max_len_alias()
        maxoui=self.max_len_oui()
        maxtype=self.max_len_type()
        maxlength=maxtype+2+17+2+maxalias+2+maxoui
        self.order_by_alias()
        print (Style.BRIGHT+"="*(maxlength))
        print (Style.BRIGHT+self.tr("{} DEVICES IN DATABASE AT {}").format(self.length(), str(datetime.datetime.now())[:-7]).center (maxlength))
        print (Style.BRIGHT+ "{}  {}  {}  {}".format(" TYPE ".center(maxtype,'=')," MAC ".center(17,'='), " ALIAS ".center(maxalias,'='), " HARDWARE ".center(maxoui,'=')))
        for h in self.arr:
            mac=Style.BRIGHT+ Fore.GREEN +h.mac
            print ("{}  {}  {}  {}".format(h.type.name.ljust(maxtype), mac.center(17),   Style.BRIGHT + Fore.YELLOW+ h.alias.ljust(maxalias), Style.NORMAL + Fore.WHITE+  str(h.oui).ljust(maxoui)))    
        print (Style.BRIGHT+"="*(maxlength))

    def qtablewidget(self, table):
        self.order_by_ip() 
        ##HEADERS
        table.setColumnCount(5)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(self.tr("Type" )))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(self.tr("MAC" )))
        table.setHorizontalHeaderItem(2,  QTableWidgetItem(self.tr("Alias" )))
        table.setHorizontalHeaderItem(3, QTableWidgetItem(self.tr("Hardware" )))
        table.setHorizontalHeaderItem(4, QTableWidgetItem(self.tr("IP" )))
        ##DATA 
        table.clearContents()   
        table.setRowCount(self.length())
        for rownumber, h in enumerate(self.arr):
            alias=""
            if h.alias!=None:
                alias=h.alias
            if h.type!=None:#Error en Windows
                table.setItem(rownumber, 0, qleft(h.type.name))
                table.item(rownumber,0).setIcon(h.type.qicon())
            else:
                table.setItem(rownumber, 0, qleft("None"))
            table.setItem(rownumber, 1, qleft(h.mac))
            table.setItem(rownumber, 2, qleft(alias))
            table.setItem(rownumber, 3, qleft(h.oui))
            table.setItem(rownumber, 4, qleft(h.ip))
            if h.alias!=None:
                for i in range(0, table.columnCount()):
                    table.item(rownumber, i).setBackground( QColor(182, 255, 182))       
            else:
                for i in range(0, table.columnCount()):
                    table.item(rownumber, i).setBackground( QColor(255, 182, 182))       

    def qtablewidget_devices_from_settings(self, table):
        self.order_by_alias() 
        ##HEADERS
        table.setColumnCount(4)
        table.setHorizontalHeaderItem(0, QTableWidgetItem(self.tr("Type" )))
        table.setHorizontalHeaderItem(1, QTableWidgetItem(self.tr("MAC" )))
        table.setHorizontalHeaderItem(2,  QTableWidgetItem(self.tr("Alias" )))
        table.setHorizontalHeaderItem(3, QTableWidgetItem(self.tr("Hardware" )))
        ##DATA 
        table.clearContents()   
        table.setRowCount(self.length())
        for rownumber, h in enumerate(self.arr):
            table.setItem(rownumber, 0, qleft(h.type.name))
            table.item(rownumber, 0).setIcon(h.type.qicon())
            table.setItem(rownumber, 1, qleft(h.mac))
            table.setItem(rownumber, 2, qleft(h.alias))
            table.setItem(rownumber, 3, qleft(h.oui))

    def xml(self):
        """
            Returns a string with a xml of the array. Used to export data
        """
        s='<devicesinlan version="{}">\n'.format(version)
        s=s+"\t<devices>\n"
        for d in self.arr:
            s=s+'\t\t<device alias="{}" mac="{}" type="{}"/>\n'.format(d.alias, d.mac, d.type.id)
        s=s+"\t</devices>\n"
        s=s+"</devicesinlan>\n"
        return s

class Device(QObject):
    def __init__(self, mem):
        QObject.__init__(self)
        self.mem=mem
        self.ip=None
        self.mac=None
        self.__oui=None# You must use self.oui()
        self.alias=None
        self.pinged=False
        self.type=None
        
    def __eq__(self, other):
        if other==None:
            return False
        if self.mac.upper()==other.mac.upper() and self.alias==other.alias and self.type.id==other.type.id:
            return True
        return False
        
    def validate_mac(self, s):
        if len(s)!=17:
            return False

        if re.match(r'([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})', s):
            return True
        return False
        
    @property
    def oui(self):
        """
            Se invoca como self.oui
        """
        if self.__oui!=None:#It already has been searched
            return self.__oui

        if self.mac==None:
            print("I can't get oui of a None MAC")
            return self.__oui

        if platform.system()=="Windows":
            url="ieee-oui.txt"
        elif platform.system()=="Linux":
            url="/usr/share/devicesinlan/ieee-oui.txt"

        self.__oui=""
        mac=self.mac.replace(":", "")[:-6]
        f=open(url, "rb")
        for line in f.readlines():
            if line.find(mac.encode())!=-1:
                self.__oui=line.decode('utf-8').split("\t")[1][:-2].upper()
        return self.__oui

    def validate_alias(self, s):
        if len(s)>40:
            return False
        if len(s)==0:
            return False
        return True
        
    def insert_mac(self):
        validated=False
        while  validated==False:
            print(Style.BRIGHT+ self.tr("Input the MAC of the known device (XX:XX:XX:XX:XX:XX): "), end="")
            self.mac=input().upper()
            if self.validate_mac(self.mac):
                validated=True
            else:
                print (Style.BRIGHT+ Fore.RED+ self.tr("You need to insert a mac with the next format: 2A:3B:4C:5D:6E:7A"))

    def insert_alias(self):
        validated=False
        while validated==False:
            print(Style.BRIGHT+self.tr("Input an alias of the known device: "), end="")
            self.alias=input()
            if self.validate_alias(self.alias):
                validated=True
            else:
                print (Style.BRIGHT+Fore.RED+ self.tr("You need to add an alias"))

        
    def link(self):
        self.mem.settings.setValue("DeviceAlias/{}".format(self.macwithout2points(self.mac.upper())), self.alias)
        self.mem.settings.setValue("DeviceType/{}".format(self.macwithout2points(self.mac.upper())), self.type.id)
        self.mem.settings.sync()
        
    def unlink(self):
        """If device is in a set You must use set.unlink(o)"""
        self.mem.settings.remove("DeviceAlias/{}".format(self.macwithout2points(self.mac.upper())))
        self.mem.settings.remove("DeviceType/{}".format(self.macwithout2points(self.mac.upper())))
        self.type=self.mem.types.find_by_id(0)
        self.alias=None
        self.mem.settings.sync()
        
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

def input_int(text, default=None):
    while True:
        if default==None:
            res=input(Style.BRIGHT+text+": ")
        else:
            print(Style.BRIGHT+ Fore.WHITE+"{} [{}]: ".format(text, Fore.GREEN+str(default)+Fore.WHITE), end="")
            res=input()
        try:
            if res==None or res=="":
                res=default
            res=int(res)
            return res
        except:
            pass
            

def input_string(text):
    return input(text)

    
def qbool(bool):
    """Prints bool and check. Is read only and enabled"""
    a=QTableWidgetItem()
    a.setFlags( Qt.ItemIsSelectable |  Qt.ItemIsEnabled )#Set no editable
    if bool:
        a.setCheckState(Qt.Checked);
        a.setText(QCoreApplication.translate("devicesinlan","True"))
    else:
        a.setCheckState(Qt.Unchecked);
        a.setText(QCoreApplication.translate("devicesinlan","False"))
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignCenter)
    return a
    
def qleft(string):
    a=QTableWidgetItem(str(string))
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignLeft)
    return a

def b2s(b, code='UTF-8'):
    return bytes(b).decode(code)
    
def s2b(s, code='UTF8'):
    if s==None:
        return "".encode(code)
    else:
        return s.encode(code)
        
def qmessagebox(message, type=QMessageBox.Information):
    m=QMessageBox()
    m.setWindowIcon(QIcon(":/devicesinlan.png"))
    m.setIcon(type)
    m.setText(str(message))
    m.exec_() 
    
def qquestion(message, qicon ):
    """
        return can be QMessageBox.Yes, QMessageBox.No
    """
    m=QMessageBox()
    m.setWindowIcon(qicon)
    return m.question(None, "DevicesInLan", message, QMessageBox.Yes, QMessageBox.No)
        
