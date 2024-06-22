from colorama import init as colorama_init,  Style, Fore
from PyQt6.QtCore import QCoreApplication, QSettings, QTranslator, QObject
from PyQt6.QtNetwork import QNetworkInterface, QAbstractSocket,  QTcpSocket
from codecs import open
from concurrent.futures import ThreadPoolExecutor,  as_completed                            
from datetime import datetime, date    
from importlib.resources import files 
from pydicts.casts import bytes2str
from devicesinlan.reusing.libmanagers import ObjectManager_With_IdName, ObjectManager_Selectable
from devicesinlan import __version__, author
from devicesinlan.reusing.text_inputs import input_YN, input_int
from ipaddress import IPv4Network
from logging import debug,  info
from os import path
from platform import system as platform_system
from pydicts import lod
from re import match
from subprocess import check_output
from sys import exit, argv
from uuid import  uuid4
from urllib.request import urlopen
from xml.dom import minidom


## Converts a string to set inside an XML to a valid XML string
def string2xml(s):
    s=s.replace('"','&apos;' )
    s=s.replace('<','&lt;' )
    s=s.replace('>','&gt;' )
    s=s.replace('&','&amp;' )
    s=s.replace("'",'&apos;' )
    return s

## Converts a string to set inside an XML to a valid XML string
def xml2string(s):
    s=s.replace('&apos;','"')
    s=s.replace('&lt;','<')
    s=s.replace('&gt;','>')
    s=s.replace('&amp;','&')
    s=s.replace('&apos;',"'")
    return s


## Mem object for setup
class MemSetup(QObject):
    def __init__(self):
        QObject.__init__(self)        
        
        self.BASE_DIR=path.dirname(__file__)
        colorama_init()
        self.name="DevicesInLAN"


        self.lod_languages=[
            {"code":"en",  "flag": ":/flags/uk.png", "name":"English"}, 
            {"code":"es",  "flag": ":/flags/spain.png", "name":"Espa\xf1ol"}, 
            {"code":"fr",  "flag": ":/flags/france.png", "name":"Fran\xe7ais"}, 
            {"code":"ro",  "flag": ":/flags/rumania.png", "name":"Rom\xe2n"}, 
            {"code":"ru",  "flag": ":/flags/rusia.png", "name":"\u0420\u0443\u0441\u0441\u043a\u0438\u0439"}, 

        ]

        self.dod_languages=lod.lod2dod(self.lod_languages,  "code")

    ## Sets QApplication Object to make a Qt application
    def setQApplication(self):        
        self.app=QCoreApplication(argv)
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

        mangui.setMetadata("devicesinlan_gui",  1,   date.today(), author, self.tr("Scans all devices in your LAN. Then you can set an alias to your known devices in order to detect future strange devices in your net."))
        mangui.setSynopsis("[--help] [--version] [--debug DEBUG]")
        mangui.header(self.tr("DESCRIPTION"), 1)
        mangui.paragraph(self.tr("In the app menu you have the followings features:"), 1)
        mangui.paragraph(self.tr("Devices > New Scan"), 2, True)
        mangui.paragraph(self.tr("Searches all devices in the LAN and show them in a new tab. If some device is not in the known devices list it will be shown with a red background. Devices with a green background are trusted devices"), 3)
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

        man.setMetadata("devicesinlan",  1,   date.today(), author, self.tr("Scans all devices in your LAN. Then you can set an alias to your known devices in order to detect future strange devices in your net."))
        man.setSynopsis("[-h] [--version] [--method {PingArp,ScapyArping,Scapy}] [--interface INTERFACE | --add | --remove | --list | --load LOAD | --save SAVE | --reset] [--debug DEBUG]")

        man.header(self.tr("DESCRIPTION"), 1)
        man.paragraph(self.tr("If you launch DevicesInLan without parameters a console wizard is launched."), 1)
        man.paragraph(self.tr("Morever you can use one of this parameters."), 1)
        man.paragraph("--interface", 1, True)
        man.paragraph(self.tr("Scans the net of the interface parameter and prints a list of the detected devices."), 2)
        man.paragraph(self.tr("If a device is not known, it will be showed in red. Devices in green are trusted devices."), 2)
        man.paragraph("--add", 1, True)
        man.paragraph(self.tr("Allows to add a known device from console."), 2)
        man.paragraph("--remove", 1, True)
        man.paragraph(self.tr("Allows to remove a known device from console."), 2)
        man.paragraph("--list", 1, True)
        man.paragraph(self.tr("Shows all known devices in database from console."), 2)
        man.paragraph("--load", 1, True)
        man.paragraph(self.tr("Loads a list of known devices in xml format."), 2)
        man.paragraph("--save", 1, True)
        man.paragraph(self.tr("Saves the known devices list to a xml file."), 2)
        man.paragraph("--debug", 1, True)
        man.paragraph(self.tr("Gives debugging information when running DevicesInLAN. It's deactivated by default"), 2)
        man.paragraph(self.tr("The parameter can take this options: CRITICAL, ERROR, WARNING, INFO, DEBUG."), 2)
        man.paragraph("--reset", 1, True)
        man.paragraph(self.tr("Removes all known devices."), 2)

        man.header(self.tr("SCAN METHODS"), 1)
        man.paragraph(self.tr("DevicesInLan can use several methods to scan for devices. You just need to add the --method in console mode."), 1)
        man.paragraph("PingArp", 1, True)
        man.paragraph(self.tr("It tries to make a socket connection with any device in the lan. Then it searches with 'arp' command the mac information"), 2)
        man.paragraph(self.tr("PingArp method is used in windows and linux versions by default."), 2)

        man.paragraph("Scapy", 1, True)
        man.paragraph(self.tr("Uses Scapy to create an ARP request and capture its answer for each ip in the subnet to get macs information."), 2)
        man.paragraph(self.tr("This method can be used in windows and linux versions, but it needs to be executed with administrator role."), 2)
        man.paragraph(self.tr("Morever, you need to install 'npcap' in order to execute it in Windows."),  2)

        man.paragraph("ScapyArping", 1, True)
        man.paragraph(self.tr("Uses Scapy arping function to create ARP request and capture its answer for each ip in the subnet to get macs information."), 2)
        man.paragraph(self.tr("This method can be used in windows and linux versions, but it needs to be executed with administrator role."), 2)
        man.paragraph(self.tr("Morever, you need to install 'npcap' in order to execute it in Windows."),  2)

        man.header(self.tr("EXAMPLES"), 1)
        man.paragraph("devicesinlan", 1, True)
        man.paragraph(self.tr("Default command. It uses PingArp method."), 2)
        man.paragraph("devicesinlan --method ScapyArping", 1, True)
        man.paragraph(self.tr("It uses ScapyArping method."), 2)
        man.save()
        man.saveHTML("devicesinlan/data/devicesinlan.{}.html".format(language))


    def signal_handler(self, signal, frame):
            print(Style.BRIGHT+Fore.RED+self.tr("You pressed 'Ctrl+C', exiting..."))
            exit(0)
            
    ## Changes Qt current Qtranslator
    ## @param language String with en, es .... None by defautt and search in settings
    def setLanguage(self, language=None):
        if language==None:
            language=self.settings.value("frmSettings/language", "en")
            
        url=files("devicesinlan") / "i18n/devicesinlan_{}.qm".format(language)
        
        if language=="en":
            info("Changing to default language: en")
            self.app.removeTranslator(self.translator)
            self.translator=QTranslator()
        else:
            self.translator.load(str(url))
            self.app.installTranslator(self.translator)
            info(self.tr("Language changed to {} using {}".format(language, url)))

## Mem object for console
class MemConsole(MemSetup):
    def __init__(self):
        MemSetup.__init__(self)
        self.interfaces=InterfaceManager(self)
        self.interfaces.load_all()
        self.types=DeviceTypeManager(self)
        self.types.load_all()
        
    ## Sets parser, logging and args confitions. This one is for console command. gui commond overrides this method.
    def run(self, args):
        self.args=args
        

        self.method=ArpScanMethod.string2attribute(self.args.method)

        if self.args.load:
            if path.exists(self.args.load):
                current=DeviceManager(self).init__from_settings()
                new=DeviceManager(self).init__from_xml(self.args.load)
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
            exit(0)

        if self.args.reset:
            result=input_YN(self.tr( "Are you sure you want to reset known devices database?"),  default=self.tr("N"))
            if result==True:
                set=DeviceManager(self)
                set.init__from_settings()
                set.reset()
                print (Style.BRIGHT+Fore.RED+self.tr( "Database was reset"))
            exit(0)

        if self.args.save:
            set=DeviceManager(self)
            set.init__from_settings()
            set.saveXml(self.args.save)
            exit(0)

        if self.args.add==True:
            d=Device(self)
            d.insert_mac()
            d.insert_alias()
            d.insert_type()
            d.link()
            print (Style.BRIGHT+ Fore.GREEN + self.tr("Device inserted"))
            self.settings.sync()
            exit(0)

        if self.args.remove==True:
            d=Device(self)
            d.insert_mac()
            d.unlink()
            print (Style.BRIGHT+Fore.GREEN+self.tr("Mac removed"))

            self.settings.sync()
            exit(0)

        if self.args.list==True:
            set=DeviceManager(self)
            set.init__from_settings()
            set.print_devices_from_settings()
            exit(0)
        ## Load devices
        if self.args.interface:
            if self.interfaces.find_by_id(self.args.interface)==None:
                print(Style.BRIGHT+Fore.RED+self.tr( "This interface doesn't exist. Please remove the --interface parameter to use a wizard."))
                exit(1)
            self.interfaces.selected=self.interfaces.find_by_id(self.args.interface)
        else:
            if self.interfaces.length()==0:
                print(Style.BRIGHT+ Fore.RED+self.tr( "There are not interfaces to scan."))
                exit(1)
            self.interfaces.print()
            while True:
                id=input_int(self.tr( "Select an interface number"), 1)
                if id<=self.interfaces.length():#Check id 
                    break
            self.interfaces.selected=self.interfaces.find_by_id(self.interfaces.arr[id-1].id())
            self.settings.setValue("frmSettings/concurrence", input_int(self.tr( "Input an integer with the request concurrence"), self.settings.value("frmSettings/concurrence", 200)))
            self.settings.sync()

        inicio=datetime.now()
        set=DeviceManager(self)
        set.setMethod(self.method)
        set.print()
        print (Style.BRIGHT+self.tr("DevicesInLan took {} with method {}.").format (Fore.GREEN+str(datetime.now()-inicio)+ " "+ self.tr( "seconds")+Fore.WHITE, self.args.method))

    def setInstallationUUID(self):
        if self.settings.value("frmMain/uuid", "None")=="None":
            self.settings.setValue("frmMain/uuid", str(uuid4()))
        url='https://devicesinlan.sourceforge.net/php/devicesinlan_installations.php?uuid={}&version={}&platform={}'.format(self.settings.value("frmMain/uuid"), __version__, platform_system())
        try:
            web=bytes2str(urlopen(url).read())
        except:
            web=self.tr("Error collecting statistics")
        debug("{}, answering {}".format(web, url))


## This function checks if currrent user is root or administrator in Windows or Linux
def need_administrator(method):
    def new_func(*args, **kwargs):
        if platform_system=='Windows':
            from ctypes.windll.shell32 import IsUserAnAdmin
            if IsUserAnAdmin()!=True:
                print("You need to be an Administrator to execute this code.")
        else:
            from os import geteuid
            if geteuid() !=0:
                print("You need to be root to execute this code.")
                exit(-1)
        return method(*args, **kwargs)
    return new_func

class DeviceType:
    def __init__(self, mem):
        self.mem=mem
        self.id=None
        self.name=None
        
    def init__create(self, id, name):
        self.id=id
        self.name=name
        return self

class DeviceTypeManager(QObject, ObjectManager_With_IdName):
    def __init__(self, mem):
        QObject.__init__(self)
        ObjectManager_With_IdName.__init__(self)
        self.mem=mem
        
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
            print (Style.BRIGHT + "{}. {}.".format(type.id+1, Fore.GREEN+type.name + Style.RESET_ALL))
    
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
        
    ##Conversts 255.255.255.0 to 24
    def netmask_to_int(self):
        sintegers=self.netmask().split(".")
        sbits=""
        for s in sintegers:
            sbits=sbits+bin(int(s))[2:]#Converts to binary, prefix 0b that I remove
        r=0
        for s in sbits:
            r=r+int(s)
        return r
    
    ##If interface ip 192.168.1.12 and netmask 255.255.255.0 return 192.168.1.0/24
    ##If interface ip 192.168.1.12 and netmask 255.255.254.0 return 192.168.0.0/23
    ## If there is a 0 in the netmask result is 0
    def network(self):
        sip=self.ip().split(".")
        smask=self.netmask().split(".")
        r=[]
        for i in range(len(sip)):
            if bin(int(smask[i]))[2:].find("0")>=0:#Converts to binary, prefix 0b that I remove
                r.append("0")
            else:
                r.append(sip[i])
        net=".".join(r)
        return "{}/{}".format(net, self.netmask_to_int())
        
        
    def broadcast(self):
        return self.qnetworkaddressentry.broadcast().toString()
    
    def init__create(self, qnetworkinterface, qnetworkaddressentry):
        self.qnetworkinterface=qnetworkinterface
        self.qnetworkaddressentry=qnetworkaddressentry
        return self


    def __str__(self):
        return (self.tr("Interface {} ({}) with ip {}/{} and mac {}".format(self.name, self.id(), self.ip(), self.netmask(), self.mac())))
        
class InterfaceManager(ObjectManager_Selectable):
    def __init__(self, mem):
        ObjectManager_Selectable.__init__(self)
        self.mem=mem
        
    def find_by_id(self, id):
        for interface in self.arr:
            if interface.id()==id:
                return interface
        return None

                
    def load_all(self):
        for i in QNetworkInterface.allInterfaces():
                for e in i.addressEntries():
                    if e.ip().isLoopback()==False and i.isValid() and e.ip().isMulticast()==False and e.ip().isNull()==False and e.ip().protocol()==QAbstractSocket.NetworkLayerProtocol.IPv4Protocol and e.ip().isLinkLocal()==False:
                        self.append(Interface(self.mem).init__create(i, e))
        
    def print(self):
        for i, interface in enumerate(self.arr):
            print ("{}. {} ( {} / {} and MAC: {} )".format(
                        Style.BRIGHT+ str(i+1), 
                        Fore.GREEN+str(interface.id()), 
                        Fore.WHITE+ interface.ip() + Fore.GREEN, 
                        Fore.WHITE + interface.netmask() + Fore.GREEN, 
                        Fore.WHITE + interface.mac() + Fore.GREEN ) + Style.RESET_ALL)

    def order_by_name(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda c: c.name(),  reverse=False)       
            return True
        except:
            return False       

class ArpScanMethod:
    PingArp=0 #Ping + ARP
    ScapyArping=4#Scapy python module arping function needs ROOT  and winpcap in windows
    Scapy=5#A pelo with scapy
    @classmethod
    def string2attribute(self, s):
        for attr, value in self.__dict__.items():
            if attr==s:
                return value
        return None

class DeviceManager(QObject, ObjectManager_Selectable):
    def __init__(self, mem):
        """This constructor load /etc/devicesinlan/known.txt and executes arp-scan and parses its result"""
        QObject.__init__(self)
        ObjectManager_Selectable.__init__(self)
        self.mem=mem
        self.isDatabase=False#Returns True if is init__from_settings

    def init__from_xml(self, filename):
        """
            Constructor thal load devices from a xml file. Used to import data from file
        """
        xmldoc = minidom.parse(filename)
        itemlist = xmldoc.getElementsByTagName('device')
        for item in itemlist:
            d=Device(self.mem)
            d.alias=xml2string(item.attributes['alias'].value)
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
        
        debug("Loaded {} devices from settings".format(self.length()))
        
        #Carga los types antes no se pod´ia
        for d in self.arr:
            d.type=self.mem.types.find_by_id(int(self.mem.settings.value("DeviceType/{}".format(d.macwithout2points(d.mac.upper())), 0)))
        return self

    def setMethod(self, arpscanmethod):
        if arpscanmethod==ArpScanMethod.PingArp:
            self.method_pingarp()
        elif arpscanmethod==ArpScanMethod.ScapyArping:
            self.method_scapy_arping()
        elif arpscanmethod==ArpScanMethod.Scapy:
            self.method_scapy()
        
    def method_pingarp(self):
        """Load Devices from scan with ping and arp commands output"""
        def get_ip_mac_pinged(ip):
            """
                Returns a list  [ip,mac,pinged]
            """
            pinged=True
            mac=None
            sock=QTcpSocket()
            sock.connectToHost(ip, 80)
            sock.close()

            #ARP
            if pinged==True:
                if platform_system()=="Windows":
                    CREATE_NO_WINDOW=0x08000000
                    arpexit=check_output(["arp", "-a",  ip], creationflags=CREATE_NO_WINDOW)
                    for s in arpexit.split(b" "):
                        if len(s)==17 and s.find(b"-")!=-1:
                            mac=s.decode().replace("-", ":").upper()
                else:
                    arpexit=check_output(["arp", ip])
                    for s in arpexit.decode('utf-8').split(" "):
                        if len(s)==17 and s.find(":")!=-1:
                            mac=s.upper()
            return(ip, mac, pinged)
            ###################################
        futures=[]
        concurrence=int(self.mem.settings.value("frmSettings/concurrence", 200))
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

    @need_administrator
    def method_scapy(self):
        ## Returns a list  [ip,mac,pinged]
        def get_ip_mac_pinged(ip):
            pinged=True
            mac=None
            packet = srp(Ether(dst='ff:ff:ff:ff:ff:ff')/ARP(pdst=ip)/Padding(load='\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'),timeout=2, verbose=False)
            try:
                mac=packet[0][0][1].hwsrc.upper()
            except IndexError:
                mac=None
            return(ip, mac, pinged)
            ###################################
        from scapy.layers.l2 import srp, Ether, ARP
        from scapy.all import  Padding
        futures=[]
        concurrence=int(self.mem.settings.value("frmSettings/concurrence", 200))
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
                    
    ## NEED ROOT PRIVILEGES AND PYTHON COMPILED WITH IPV6
    @need_administrator
    def method_scapy_arping(self):
        from scapy.layers.l2 import arping
        for o in arping(self.mem.interfaces.selected.network(), verbose=False)[0]:
            h=Device(self.mem)
            h.ip=o[1].psrc
            h.mac=o[1].src.upper()
            h.pinged=True
            if h.mac!=None and h.pinged==True:
                h.alias=self.mem.settings.value("DeviceAlias/{}".format(h.macwithout2points(h.mac.upper())), None)
                h.type=self.mem.types.find_by_id(int(self.mem.settings.value("DeviceType/{}".format(h.macwithout2points(h.mac.upper())), 0)))
                self.arr.append(h)#Solo si se da alias
        #Adds current interface ip
        h=Device(self.mem)
        h.ip=self.mem.interfaces.selected.ip()
        h.mac=self.mem.interfaces.selected.mac().upper()
        h.pinged=True     
        h.alias=self.mem.settings.value("DeviceAlias/{}".format(h.macwithout2points(h.mac.upper())), None)
        h.type=self.mem.types.find_by_id(int(self.mem.settings.value("DeviceType/{}".format(h.macwithout2points(h.mac.upper())), 0)))
        self.arr.append(h)

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
        
    def reset(self):
        todelete=[]#No puedo borrar de un for iterando
        for o in self.arr:
            todelete.append(o)
            
        for o in todelete:
            info("Reseting {}".format(o.mac))
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
        print (Style.BRIGHT+ "="*(maxlength) + Style.RESET_ALL)
        print (Style.BRIGHT+ self.tr("{} DEVICES IN LAN FROM {} INTERFACE AT {}").format(self.length(), self.mem.interfaces.selected.id().upper(), str(datetime.now())[:-7]).center(maxlength) + Style.RESET_ALL)
        print (Style.BRIGHT+ "{}  {}  {}  {}  {}".format(" IP ".center(16,'='),"TYPE".center(maxtype,"=")," MAC ".center(17,'='), " ALIAS ".center(maxalias,'='), " HARDWARE ".center(maxoui,'=')) + Style.RESET_ALL)
        for h in self.arr:
            if h.ip==self.mem.interfaces.selected.ip():
                print (Style.BRIGHT + Fore.MAGENTA + "{}  {}  {}  {}  {}".format(h.ip.ljust(16), h.type.name.ljust(maxtype), h.mac.center(17),   self.tr("This device").ljust(maxalias), h.oui.ljust(maxoui))+ Style.RESET_ALL)
            else:
                if h.alias:
                    mac=Style.BRIGHT+Fore.GREEN + h.mac
                    alias=h.alias
                else:
                    mac=Style.BRIGHT+Fore.RED+ h.mac
                    alias=" "
                print ("{}  {}  {}  {}  {}".format(h.ip.ljust(16), h.type.name.ljust(maxtype),  mac.center(17),   Style.BRIGHT+Fore.YELLOW +  alias.ljust(maxalias), Style.NORMAL+Fore.WHITE+ h.oui.ljust(maxoui)) + Style.RESET_ALL)
        print (Style.BRIGHT + "="*(maxlength) + Style.RESET_ALL)

    def print_devices_from_settings(self):
        """
            Print list of all database devices
        """
        maxalias=self.max_len_alias()
        maxoui=self.max_len_oui()
        maxtype=self.max_len_type()
        maxlength=maxtype+2+17+2+maxalias+2+maxoui
        self.order_by_alias()
        print (Style.BRIGHT+"="*(maxlength) + Style.RESET_ALL)
        print (Style.BRIGHT+self.tr("{} DEVICES IN DATABASE AT {}").format(self.length(), str(datetime.now())[:-7]).center (maxlength) + Style.RESET_ALL)
        print (Style.BRIGHT+ "{}  {}  {}  {}".format(" TYPE ".center(maxtype,'=')," MAC ".center(17,'='), " ALIAS ".center(maxalias,'='), " HARDWARE ".center(maxoui,'=')) + Style.RESET_ALL)
        for h in self.arr:
            mac=Style.BRIGHT+ Fore.GREEN +h.mac
            print ("{}  {}  {}  {}".format(h.type.name.ljust(maxtype), mac.center(17),   Style.BRIGHT + Fore.YELLOW+ h.alias.ljust(maxalias), Style.NORMAL + Fore.WHITE+  str(h.oui).ljust(maxoui)) + Style.RESET_ALL)
        print (Style.BRIGHT+"="*(maxlength) + Style.RESET_ALL)


    def saveXml(self, filename):
        """
            Returns a string with a xml of the array. Used to export data
        """
        s='<devicesinlan version="{}">\n'.format(__version__)
        s=s+"\t<devices>\n"
        for d in self.arr:
            s=s+'\t\t<device alias="{}" mac="{}" type="{}"/>\n'.format(string2xml(d.alias), d.mac, d.type.id)
        s=s+"\t</devices>\n"
        s=s+"</devicesinlan>\n"
        with open(filename, "w", "utf-8") as f:
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

        if match(r'([0-9a-fA-F]{2}[:-]){5}([0-9a-fA-F]{2})', s):
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

        url=files("devicesinlan") / "data/ieee-oui.txt"

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
        debug("Device {} unlinked".format(self.mac))
        self.type=self.mem.types.find_by_id(0)
        self.alias=None
        
    def macwith2points(self, macwithout):
        macwith=""
        for i in range(6):
            macwith=macwith+macwithout[i*2]+macwithout[i*2+1]+":"
        return macwith[:-1]
        
    def macwithout2points(self, macwith):
        return macwith.replace(":", "")

    def signal_handler(self, signal, frame):
            print(Style.BRIGHT+Fore.RED+self.tr("You pressed 'Ctrl+C', exiting..."))
            exit(0)
            
    ## Changes Qt current Qtranslator
    ## @param language String with en, es .... None by defautt and search in settings
    def setLanguage(self, language=None):
        if language==None:
            language=self.settings.value("frmSettings/language", "en")

        url=files("devicesinlan") / "i18n/devicesinlan_{}.qm".format(language)
        
        if language=="en":
            info("Changing to default language: en")
            self.app.removeTranslator(self.translator)
            self.translator=QTranslator()
        else:
            self.translator.load(url)
            self.app.installTranslator(self.translator)
            info(self.tr("Language changed to {} using {}".format(language, url)))
            
