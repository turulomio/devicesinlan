import argparse
import codecs
from colorama import init as colorama_init,  Style, Fore
import datetime
import threading
import logging
import os
import re
import pkg_resources
import platform
import subprocess
import sys
import time
import socket
from PyQt5.QtCore import QCoreApplication, QSettings, QTranslator, QObject
from PyQt5.QtNetwork import QNetworkInterface, QAbstractSocket,  QTcpSocket
from concurrent.futures import ThreadPoolExecutor,  as_completed
from xml.dom import minidom
from uuid import  uuid4
from urllib.request import urlopen
from ipaddress import IPv4Network
from devicesinlan.version import __version__, __versiondate__

class TypesARP:
    Gratuitous = 1
    Standard = 2

## Mem object for setup
class MemSetup(QObject):
    def __init__(self):
        QObject.__init__(self)        
        self.name="DevicesInLAN"
        self.author=self.tr("Mariano Mu\\xf1oz")
        self.description=self.tr('Show devices in a LAN making an ARP search to find them with a user interface')
        self.epilog=self.tr("If you like this app, please give me a star in https://github.com/Turulomio/devicesinlan.")+"\n" +self.tr("Developed by {} 2015-{} \\xa9").format(self.author, __versiondate__.year)
        colorama_init()

    ## Sets QApplication Object to make a Qt application
    def setQApplication(self):
        if self.__class__.__name__ in ["MemSetup", "MemConsole"]:
            self.app=QCoreApplication(sys.argv)
        else:
            from PyQt5.QtWidgets import QApplication
            self.app=QApplication(sys.argv)
            self.app.setQuitOnLastWindowClosed(True)
        self.app.setOrganizationName(self.name)
        self.app.setOrganizationDomain(self.name)
        self.app.setApplicationName(self.name)
        self.translator=QTranslator()
        self.settings=QSettings()

    def mangenerator(self, language):
        from mangenerator import Man

        print("DESCRIPTION in {} is {}".format(language, self.tr("DESCRIPTION")))

        if language=="en":
            man=Man("man/man1/devicesinlan")
            mangui=Man("man/man1/devicesinlan_gui")
        else:
            man=Man("man/{}/man1/devicesinlan".format(language))
            mangui=Man("man/{}/man1/devicesinlan_gui".format(language))

        mangui.setMetadata("devicesinlan_gui",  1,   datetime.date.today(), "Mariano Muñoz", self.tr("Scans all devices in your LAN. Then you can set an alias to your known devices in order to detect future strange devices in your net."))
        mangui.setSynopsis("[--help] [--version] [--debug DEBUG]")
        mangui.header(self.tr("DESCRIPTION"), 1)
        mangui.paragraph(self.tr("In the app menu you have the followings features:"), 1)
        mangui.paragraph(self.tr("Devices > New Scan"), 2, True)
        mangui.paragraph(self.tr("Searches all devices in tha LAN and show them in a new tab. If some device is not in the known devices list it will be shown with a red background. Devices with a green background are trusted devices"), 3)
        mangui.paragraph(self.tr("Devices > Show devices database"), 2, True)
        mangui.paragraph(self.tr("Shows all known devices in a new tab."), 3)
        mangui.paragraph(self.tr("Right click allows you to edit known devices database."), 3)
        mangui.paragraph(self.tr("Devices > Load devices list"), 2, True)
        mangui.paragraph(self.tr("Loads a list of known devices in xml format."), 3)
        mangui.paragraph(self.tr("Devices > Save devices list"), 2, True)
        mangui.paragraph(self.tr("Saves the known devices list to a xml file."), 3)
        mangui.paragraph(self.tr("Devices > Reset database"), 2, True)
        mangui.paragraph(self.tr("Removes all known devices."), 3)
        mangui.paragraph(self.tr("This option erases all known devices in database."), 3)
        mangui.paragraph(self.tr("Configuration > Settings"), 2, True)
        mangui.paragraph(self.tr("In this dialog you can select your prefered language and you can configure the number of concurrence request."), 3)
        mangui.paragraph(self.tr("Help > Help"), 2, True)
        mangui.paragraph(self.tr("Shows this help information."), 3)
        mangui.paragraph(self.tr("Help > About"), 2, True)
        mangui.paragraph(self.tr("Shows information about DevicesInLAN license and authors."), 3)
        mangui.paragraph(self.tr("Help > Check for updates"), 2, True)
        mangui.paragraph(self.tr("Checks for updates in DevicesInLan repository."), 3)
        mangui.paragraph(self.tr("Help > Exit"), 2, True)
        mangui.paragraph(self.tr("Exits from program."), 3)
        mangui.save()
        mangui.saveHTML("devicesinlan/data/devicesinlan_gui.{}.html".format(language))

        man.setMetadata("devicesinlan",  1,   datetime.date.today(), "Mariano Muñoz", self.tr("Scans all devices in your LAN. Then you can set an alias to your known devices in order to detect future strange devices in your net."))
        man.setSynopsis("[--help] [--version] [--debug DEBUG] [ --interface | --add | --remove | --list | --load | --save | --reset ]")

        man.header(self.tr("DESCRIPTION"), 1)
        man.paragraph(self.tr("If you launch deviceslan without parameters a console wizard is launched."), 1)
        man.paragraph(self.tr("Morever you can use one of this parameters."), 1)
        man.paragraph("--interface", 2, True)
        man.paragraph(self.tr("Scans the net of the interface parameter and prints a list of the detected devices."), 3)
        man.paragraph(self.tr("If a device is not known, it will be showed in red. Devices in green are trusted devices."), 3)
        man.paragraph("--add", 2, True)
        man.paragraph(self.tr("Allows to add a known device from console."), 3)
        man.paragraph("--remove", 2, True)
        man.paragraph(self.tr("Allows to remove a known device from console."), 3)
        man.paragraph("--list", 2, True)
        man.paragraph(self.tr("Shows all known devices in database from console."), 3)
        man.paragraph("--load", 2, True)
        man.paragraph(self.tr("Loads a list of known devices in xml format."), 3)
        man.paragraph("--save", 2, True)
        man.paragraph(self.tr("Saves the known devices list to a xml file."), 3)
        man.paragraph("--debug", 2, True)
        man.paragraph(self.tr("Gives debugging information when running DevicesInLAN. It's deactivated by default"), 3)
        man.paragraph(self.tr("The parameter can take this options: CRITICAL, ERROR, WARNING, INFO, DEBUG."), 3)
        man.paragraph("--reset", 2, True)
        man.paragraph(self.tr("Removes all known devices."), 3)
        man.save()
        man.saveHTML("devicesinlan/data/devicesinlan.{}.html".format(language))



    ## Sets logging level for the app
    def setLoggingLevel(self, level):        
        #Por defecto se pone WARNING y mostrar´ia ERROR y CRITICAL
        logFormat = "%(asctime)s %(levelname)s %(module)s:%(lineno)d at %(funcName)s. %(message)s"
        dateFormat='%Y%m%d %I%M%S'

        if level=="DEBUG":#Show detailed information that can help with program diagnosis and troubleshooting. CODE MARKS
            logging.basicConfig(level=logging.DEBUG, format=logFormat, datefmt=dateFormat)
        elif level=="INFO":#Everything is running as expected without any problem. TIME BENCHMARCKS
            logging.basicConfig(level=logging.INFO, format=logFormat, datefmt=dateFormat)
        elif level=="WARNING":#The program continues running, but something unexpected happened, which may lead to some problem down the road. THINGS TO DO
            logging.basicConfig(level=logging.WARNING, format=logFormat, datefmt=dateFormat)
        elif level=="ERROR":#The program fails to perform a certain function due to a bug.  SOMETHING BAD LOGIC
            logging.basicConfig(level=logging.ERROR, format=logFormat, datefmt=dateFormat)
        elif level=="CRITICAL":#The program encounters a serious error and may stop running. ERRORS
            logging.basicConfig(level=logging.CRITICAL, format=logFormat, datefmt=dateFormat)
        else:
            if level:#Bad debug parameter
                logging.basicConfig(level=logging.CRITICAL, format=logFormat, datefmt=dateFormat)
                logging.critical("--debug parameter must be DEBUG, INFO, WARNING, ERROR or CRITICAL")
                sys.exit(1)
            else:     #No debug parameter
                logging.propagate=False

    def signal_handler(self, signal, frame):
            print(Style.BRIGHT+Fore.RED+self.tr("You pressed 'Ctrl+C', exiting..."))
            sys.exit(0)
            
    ## Changes Qt current Qtranslator
    ## @param language String with en, es .... None by defautt and search in settings
    ## @param url Stirng with the qm url. Useful in setup.py script. None by default
    def setLanguage(self, language=None, url=None):  
        if language==None:
            language=self.settings.value("frmSettings/language", "en")
        if url==None:
            url=pkg_resources.resource_filename("devicesinlan", "i18n/devicesinlan_{}.qm".format(language))

        if os.path.exists(url)==True:
            self.translator.load(url)
            self.app.installTranslator(self.translator)
            logging.info(self.tr("Language changed to {} using {}".format(language, url)))
        elif language!="en":
            logging.info("I couldn't found {}".format(url))

## Mem object for console
class MemConsole(MemSetup):
    def __init__(self):
        MemSetup.__init__(self)
        self.interfaces=SetInterfaces(self)
        self.interfaces.load_all()
        self.types=SetDeviceTypes(self)
        self.types.load_all()
        
    ## Sets parser, logging and args confitions. This one is for console command. gui commond overrides this method.
    def parse_args(self):
        parser=argparse.ArgumentParser(prog='devicesinlan', description=self.description,  epilog=self.epilog, formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('--version', action='version', version="{} ({})".format(__version__, __versiondate__))
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--interface', help=self.tr('Net interface name'))
        group.add_argument('--add', help=self.tr('Add a known device'), action='store_true')
        group.add_argument('--remove', help=self.tr('Remove a known device'), action='store_true')
        group.add_argument('--list', help=self.tr('List known devices'), action='store_true')
        group.add_argument('--load', help=self.tr('Load known devices list'), action='store')
        group.add_argument('--save', help=self.tr('Save known devices list'), action='store')
        group.add_argument('--reset', help=self.tr('Reset known devices list'), action='store_true', default=False)
        parser.add_argument('--debug', help=self.tr( "Debug program information"))

        self.args=parser.parse_args()

        self.setLoggingLevel(self.args.debug)

        if self.args.load:
            if os.path.exists(self.args.load):
                current=SetDevices(self).init__from_settings()
                new=SetDevices(self).init__from_xml(self.args.load)
                for n in new.arr:
                    c=current.find_by_mac(n.mac)
                    if c==None:#Not found its mac so n is new
                        if input_YN(self.tr( "Do you want to add this {} with MAC {} and set its name to {}?".format(n.type.name.lower(), n.mac, n.alias)), default=self.tr( "Y"))==True:
                            n.link()
                    else:
                        if n!=c:
                            if input_YN(self.tr( "We already have a device with this MAC: {}. Do you want to change its alias ({}) and type ({}) to a {} named {}?".format(c.mac, c.alias, c.type.name.lower(), n.type.name.lower(), n.alias)), default=self.tr( "Y"))==True:
                                n.link()
            else:
                print (Style.BRIGHT+Fore.RED+self.tr( "File doesn't exist"))
            sys.exit(0)

        if self.args.reset:
            result=input_YN(self.tr( "Are you sure you want to reset known devices database?"),  default=self.tr("N"))
            if result==True:
                set=SetDevices(self)
                set.init__from_settings()
                set.reset()
                print (Style.BRIGHT+Fore.RED+self.tr( "Database was reset"))
            sys.exit(0)

        if self.args.save:
            set=SetDevices(self)
            set.init__from_settings()
            set.saveXml(self.args.save)
            sys.exit(0)

        if self.args.add==True:
            d=Device(self)
            d.insert_mac()
            d.insert_alias()
            d.insert_type()
            d.link()
            print (Style.BRIGHT+ Fore.GREEN + self.tr("Device inserted"))
            self.settings.sync()
            sys.exit(0)

        if self.args.remove==True:
            d=Device(self)
            d.insert_mac()
            d.unlink()
            print (Style.BRIGHT+Fore.GREEN+self.tr("Mac removed"))

            self.settings.sync()
            sys.exit(0)

        if self.args.list==True:
            set=SetDevices(self)
            set.init__from_settings()
            set.print_devices_from_settings()
            sys.exit(0)
        ## Load devices
        if self.args.interface:
            if self.interfaces.find_by_id(self.args.interface)==None:
                print(Style.BRIGHT+Fore.RED+self.tr( "This interface doesn't exist. Please remove the --interface parameter to use a wizard."))
                sys.exit(1)
            self.interfaces.selected=self.interfaces.find_by_id(self.args.interface)
        else:
            if self.interfaces.length()==0:
                print(Style.BRIGHT+ Fore.RED+self.tr( "There are not interfaces to scan."))
                sys.exit(1)
            self.interfaces.print()
            while True:
                id=input_int(self.tr( "Select an interface number"), 1)
                if id<=self.interfaces.length():#Check id 
                    break
            self.interfaces.selected=self.interfaces.find_by_id(self.interfaces.arr[id-1].id())
            self.settings.setValue("frmSettings/concurrence", input_int(self.tr( "Input an integer with the request concurrence"), self.settings.value("frmSettings/concurrence", 200)))
            self.settings.sync()

        inicio=datetime.datetime.now()
        set=SetDevices(self)
        set.setMethod(ArpScanMethod.PingArp)
        set.print()
        print (Style.BRIGHT+self.tr("It took {} with DevicesInLAN scanner.").format (Fore.GREEN+str(datetime.datetime.now()-inicio)+ " "+ self.tr( "seconds")+Fore.WHITE))

    def setInstallationUUID(self):
        if self.settings.value("frmMain/uuid", "None")=="None":
            self.settings.setValue("frmMain/uuid", str(uuid4()))
        url='http://devicesinlan.sourceforge.net/php/devicesinlan_installations.php?uuid={}&version={}&platform={}'.format(self.settings.value("frmMain/uuid"), __version__, platform.system())
        try:
            web=b2s(urlopen(url).read())
        except:
            web=self.tr("Error collecting statistics")
        logging.debug("{}, answering {}".format(web, url))

## devicesinlan_gui Mem object
class MemGUI(MemConsole):
    def __init__(self):
        MemConsole.__init__(self)

    ## Sets parser, logging and args confitions. This one is for devicesinlan_gui  command, that overrides supper method
    def parse_args(self):
        parser=argparse.ArgumentParser(prog='devicesinlan_gui', description=self.description,  epilog=self.epilog, formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('--version', action='version', version="{} ({})".format(__version__, __versiondate__))
        parser.add_argument('--debug', help=self.tr( "Debug program information"))
        self.args=parser.parse_args()        

        self.setLoggingLevel(self.args.debug)


class DeviceType:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.name=None
        
    def init__create(self, id, name):
        self.id=id
        self.name=name
        return self
        



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
        
    def print(self):
        """Printed number is self.id+1"""
        for type in self.arr:
            print (Style.BRIGHT + "{}. {}.".format(type.id+1, Style.BRIGHT+ Fore.GREEN+type.name))
    
    def order_by_name(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda c: c.name,  reverse=False)       
            return True
        except:
            return False       

class Interface(QObject):
    """Union of Interface and networkaddressentry. Remember than a interface can have networkaddressentry. ipaddress is qhostaddress"""
    def __init__(self, mem):
        QObject.__init__(self)
        self.mem=mem
        
#        self.id=None#Id numerico de Windows o id de Linux
#        self.name=None
#        self.ip=None
#        self.mac=None
#        self.mask=None
#        self.broadcast=None
    
    def addresses(self):
        """List of strings with all ip addresses in the net of the interface"""
        r=[]
        for addr in IPv4Network("{}/{}".format(self.ip(), self.netmask()), strict=False):
            r.append(addr)
        return r
        
    def id(self):
        return self.qnetworkinterface.name()
        
    def name(self):
        return self.qnetworkinterface.humanReadableName()
        
    def ip(self):
        return self.qnetworkaddressentry.ip().toString()
        
    def mac(self):
        return self.qnetworkinterface.hardwareAddress()
        
    def netmask(self):
        return self.qnetworkaddressentry.netmask().toString()
        
    def broadcast(self):
        return self.qnetworkaddressentry.broadcast().toString()
    
    def init__create(self, qnetworkinterface, qnetworkaddressentry):
        self.qnetworkinterface=qnetworkinterface
        self.qnetworkaddressentry=qnetworkaddressentry
        return self


    def __str__(self):
        return (self.tr("Interface {} ({}) with ip {}/{} and mac {}".format(self.name, self.id(), self.ip(), self.netmask(), self.mac())))
        
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
            if interface.id()==id:
                return interface
        return None

                
    def load_all(self):
        for i in QNetworkInterface.allInterfaces():
                for e in i.addressEntries():
                    if e.ip().isLoopback()==False and i.isValid() and e.ip().isMulticast()==False and e.ip().isNull()==False and e.ip().protocol()==QAbstractSocket.IPv4Protocol:
                        self.append(Interface(self.mem).init__create(i, e))
        
    def print(self):
        i=1
        for interface in self.arr:
            print (Style.BRIGHT + "{}. {} ({}/{} and MAC: {})".format(i, Style.BRIGHT+ Fore.GREEN+str(interface.id()), interface.ip(), interface.netmask(), interface.mac()))
            i=i+1

    def order_by_name(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda c: c.name(),  reverse=False)       
            return True
        except:
            return False       
              
                
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
        self.isDatabase=True#Used to show icons
        self.mem.settings.beginGroup("DeviceAlias")#Las key son sin DevicesAlias ahora
        for key in self.mem.settings.childKeys():
            d=Device(self.mem)
            d.mac=d.macwith2points(key).upper()
            d.alias=self.mem.settings.value("{}".format(d.macwithout2points(d.mac.upper())), None)
            self.arr.append(d)
        self.mem.settings.endGroup()
        
        logging.debug("Loaded {} devices from settings".format(self.length()))
        
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
        for addr in self.mem.interfaces.selected.addresses():
            if str(addr)==self.mem.interfaces.selected.ip():#Adds device if ip is interface ip and jumps it
                h=Device(self.mem)
                h.ip=str(addr)
                h.mac=self.mem.interfaces.selected.mac()
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
        def get_ip_mac_pinged(ip):
            """
                Returns a list  [ip,mac,pinged]
            """
            pinged=True
            mac=None
#            #PING
#            if platform.system()=="Windows":
#                output=subprocess.call(["ping", "-n", "1", ip], shell=False, stderr=subprocess.DEVNULL, creationflags=CREATE_NO_WINDOW)
#            else:
#                output=subprocess.call(["ping", "-c", "1", "-W", "1", ip], shell=False, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
#            if output==0:
#                pinged=True
            socket=QTcpSocket()
            socket.connectToHost(ip, 80)
            socket.close()



            #ARP
            if pinged==True:
                if platform.system()=="Windows":
                    CREATE_NO_WINDOW=0x08000000
                    arpexit=subprocess.check_output(["arp", "-a",  ip], creationflags=CREATE_NO_WINDOW)
                    for s in arpexit.split(b" "):
                        if len(s)==17 and s.find(b"-")!=-1:
                            mac=s.decode().replace("-", ":").upper()
                else:
                    arpexit=subprocess.check_output(["arp", ip])
                    for s in arpexit.decode('utf-8').split(" "):
                        if len(s)==17 and s.find(":")!=-1:
                            mac=s.upper()
            return(ip, mac, pinged)
            ###################################
        futures=[]
        concurrence=int(self.mem.settings.value("frmSettings/concurrence", 50))
        with ThreadPoolExecutor(max_workers=concurrence) as executor:
            for addr in self.mem.interfaces.selected.addresses():
                if str(addr)==self.mem.interfaces.selected.ip() :#Adds device if ip is interface ip and jumps it
                    h=Device(self.mem)
                    h.ip=str(addr)
                    h.mac=self.mem.interfaces.selected.mac().upper()
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
        
    def reset(self):
        todelete=[]#No puedo borrar de un for iterando
        for o in self.arr:
            todelete.append(o)
            
        for o in todelete:
            logging.info("Reseting {}".format(o.mac))
            self.unlink(o, remove_from_arr=True)
        
    def find_by_mac(self, mac):
        for d in self.arr:
            if d.mac.upper()==mac.upper():
                return d
        return None
        
    def link(self, o):
        if self.find_by_mac(o.mac)==None:#Insert in array, else is an update
            self.append(o)
        o.link()
        
    def unlink(self, o,  remove_from_arr=False):
        """
            Be carefoul removing in the seama for or iterations
            ., 
        """
        o.unlink()
        if remove_from_arr==True:
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
        print (Style.BRIGHT+ self.tr("{} DEVICES IN LAN FROM {} INTERFACE AT {}").format(self.length(), self.mem.interfaces.selected.id().upper(), str(datetime.datetime.now())[:-7]).center(maxlength))
        print (Style.BRIGHT+ "{}  {}  {}  {}  {}".format(" IP ".center(16,'='),"TYPE".center(maxtype,"=")," MAC ".center(17,'='), " ALIAS ".center(maxalias,'='), " HARDWARE ".center(maxoui,'=')))
        for h in self.arr:
            if h.ip==self.mem.interfaces.selected.ip():
                print ("{}  {}  {}  {}  {}".format(Style.BRIGHT+Fore.MAGENTA + h.ip.ljust(16), h.type.name.ljust(maxtype), h.mac.center(17),   self.tr("This device").ljust(maxalias), h.oui.ljust(maxoui)+ Style.RESET_ALL))
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


    def saveXml(self, filename):
        """
            Returns a string with a xml of the array. Used to export data
        """
        s='<devicesinlan version="{}">\n'.format(__version__)
        s=s+"\t<devices>\n"
        for d in self.arr:
            s=s+'\t\t<device alias="{}" mac="{}" type="{}"/>\n'.format(d.alias, d.mac, d.type.id)
        s=s+"\t</devices>\n"
        s=s+"</devicesinlan>\n"
        with codecs.open(filename, "w", "utf-8") as f:
            f.write(s)

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
        
    def __repr__(self):
        return ("Device {}".format(self.mac))
        
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

        url=pkg_resources.resource_filename("devicesinlan", "data/ieee-oui.txt")

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

    def insert_type(self):
        res=-1
        self.mem.types.print()
        while self.mem.types.find_by_id(res)==None:
            res=input_int(Style.BRIGHT+self.tr("Select a type for the known device"), 1)
            res=res-1#Due to number in prints were device.id+1
        self.type=self.mem.types.find_by_id(res)
            
        
    def link(self):
        self.mem.settings.setValue("DeviceAlias/{}".format(self.macwithout2points(self.mac.upper())), self.alias)
        self.mem.settings.setValue("DeviceType/{}".format(self.macwithout2points(self.mac.upper())), self.type.id)
        self.mem.settings.sync()
        
    def unlink(self):
        """If device is in a set You must use set.unlink(o)"""
        self.mem.settings.remove("DeviceAlias/{}".format(self.macwithout2points(self.mac.upper())))
        self.mem.settings.remove("DeviceType/{}".format(self.macwithout2points(self.mac.upper())))
        self.mem.settings.sync()
        logging.debug("Device {} unlinked".format(self.mac))
        self.type=self.mem.types.find_by_id(0)
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
            

def input_YN(pregunta, default="Y"):
    ansyes=QCoreApplication.translate("devicesinlan","Y")
    ansno=QCoreApplication.translate("devicesinlan","N")
    
    bracket="{}|{}".format(ansyes.upper(), ansno.lower()) if default.upper()==ansyes else "{}|{}".format(ansyes.lower(), ansno.upper())
    while True:
        print(Style.BRIGHT+ Fore.WHITE+"{} [{}]: ".format(pregunta,  Fore.GREEN+bracket+Fore.WHITE), end="")
        user_input = input().strip().upper()
        if not user_input or user_input=="":
            user_input=default
        if user_input == ansyes:
                return True
        elif user_input == ansno:
                return False
        else:
                print (QCoreApplication.translate("devicesinlan","Please enter '{}' or '{}'".format(ansyes, ansno)))

def input_string(text):
    return input(text)


def b2s(b, code='UTF-8'):
    return bytes(b).decode(code)
    
def s2b(s, code='UTF8'):
    if s==None:
        return "".encode(code)
    else:
        return s.encode(code)
        
