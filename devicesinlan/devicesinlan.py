import argparse
import datetime
import os
import sys
import signal
import logging
import platform
from colorama import init,  Style, Fore
from PyQt5.QtCore import QCoreApplication

def signal_handler(signal, frame):
        print(Style.BRIGHT+Fore.RED+tr("devicesinlan","You pressed 'Ctrl+C', exiting..."))
        sys.exit(0)

tr=QCoreApplication.translate
from devicesinlan.libdevicesinlan import ArpScanMethod, Device, Mem, SetDevices, input_int,  input_YN
from devicesinlan.version import __version__, __versiondate__
def main():
    init(autoreset=True)

    console=True
    app=QCoreApplication(sys.argv)

    app.setOrganizationName("DevicesInLAN")
    app.setOrganizationDomain("devicesinlan.sourceforge.net")
    app.setApplicationName("DevicesInLAN")

    signal.signal(signal.SIGINT, signal_handler)

    parser=argparse.ArgumentParser(prog='devicesinlan', description=tr("devicesinlan",'Show devices in a LAN making an ARP search to find them'),  
        epilog=app.translate("devicesinlan","If you like this app, please vote for it in Sourceforge (https://sourceforge.net/projects/devicesinlan/reviews/).")+"\n" +app.translate("devicesinlan","Developed by Mariano Muñoz 2015-{}".format(__versiondate__.year)), 
        formatter_class=argparse.RawTextHelpFormatter
        )
    parser.add_argument('--version', action='version', version="{} ({})".format(__version__, __versiondate__))
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--interface', help=app.translate("devicesinlan",'Net interface name'))
    group.add_argument('--add', help=app.translate("devicesinlan",'Add a known device'), action='store_true')
    group.add_argument('--remove', help=app.translate("devicesinlan",'Remove a known device'), action='store_true')
    group.add_argument('--list', help=app.translate("devicesinlan",'List known devices'), action='store_true')
    group.add_argument('--load', help=app.translate("devicesinlan",'Load known devices list'), action='store')
    group.add_argument('--save', help=app.translate("devicesinlan",'Save known devices list'), action='store')
    group.add_argument('--reset', help=app.translate("devicesinlan",'Reset known devices list'), action='store_true', default=False)
    parser.add_argument('--debug', help=app.translate("devicesinlan", "Debug program information"))

    if platform.system()=="Windows":
            parser.add_argument('--shortcuts-create', help="Create shortcuts for Windows", action='store_true', default=False)
            parser.add_argument('--shortcuts-remove', help="Remove shortcuts for Windows", action='store_true', default=False)

    args=parser.parse_args()        

    if platform.system()=="Windows":
            if args.shortcuts_create:
                    from devicesinlan.shortcuts import create
                    create()
                    sys.exit(0)
            if args.shortcuts_remove:
                    from devicesinlan.shortcuts import remove
                    remove()
                    sys.exit(0)

    #Por defecto se pone WARNING y mostrar´ia ERROR y CRITICAL
    logFormat = "%(asctime)s %(levelname)s %(module)s:%(lineno)d at %(funcName)s. %(message)s"
    dateFormat='%Y%m%d %I%M%S'

    if args.debug=="DEBUG":#Show detailed information that can help with program diagnosis and troubleshooting. CODE MARKS
        logging.basicConfig(level=logging.DEBUG, format=logFormat, datefmt=dateFormat)
    elif args.debug=="INFO":#Everything is running as expected without any problem. TIME BENCHMARCKS
        logging.basicConfig(level=logging.INFO, format=logFormat, datefmt=dateFormat)
    elif args.debug=="WARNING":#The program continues running, but something unexpected happened, which may lead to some problem down the road. THINGS TO DO
        logging.basicConfig(level=logging.WARNING, format=logFormat, datefmt=dateFormat)
    elif args.debug=="ERROR":#The program fails to perform a certain function due to a bug.  SOMETHING BAD LOGIC
        logging.basicConfig(level=logging.ERROR, format=logFormat, datefmt=dateFormat)
    elif args.debug=="CRITICAL":#The program encounters a serious error and may stop running. ERRORS
        logging.basicConfig(level=logging.CRITICAL, format=logFormat, datefmt=dateFormat)
    else:
        if args.debug:#Bad debug parameter
            logging.basicConfig(level=logging.CRITICAL, format=logFormat, datefmt=dateFormat)
            logging.critical("--debug parameter must be DEBUG, INFO, WARNING, ERROR or CRITICAL")
            sys.exit(1)
        else:     #No debug parameter
            logging.propagate=False

    mem=Mem()
    mem.setApp(app)
    mem.change_language(mem.settings.value("frmSettings/language", "en"))
    mem.setInstallationUUID()

    if args.load:
        if os.path.exists(args.load):
            current=SetDevices(mem).init__from_settings()
            new=SetDevices(mem).init__from_xml(args.load)
            for n in new.arr:
                c=current.find_by_mac(n.mac)
                if c==None:#Not found its mac so n is new
                    if input_YN(app.translate("devicesinlan", "Do you want to add this {} with MAC {} and set its name to {}?".format(n.type.name.lower(), n.mac, n.alias)), default=app.translate("devicesinlan", "Y"))==True:
                        n.link()
                else:
                    if n!=c:
                        if input_YN(app.translate("devicesinlan", "We already have a device with this MAC: {}. Do you want to change its alias ({}) and type ({}) to a {} named {}?".format(c.mac, c.alias, c.type.name.lower(), n.type.name.lower(), n.alias)), default=app.translate("devicesinlan", "Y"))==True:
                            n.link()
        else:
            print (Style.BRIGHT+Fore.RED+app.translate("devicesinlan", "File doesn't exist"))
        sys.exit(0)

    if args.reset:
        result=input_YN(app.translate("devicesinlan", "Are you sure you want to reset known devices database?"),  default=app.translate("devicesinlan","N"))
        if result==True:
            set=SetDevices(mem)
            set.init__from_settings()
            set.reset()
            print (Style.BRIGHT+Fore.RED+app.translate("devicesinlan", "Database was reset"))
        sys.exit(0)

    if args.save:
        set=SetDevices(mem)
        set.init__from_settings()
        set.saveXml(args.save)
        sys.exit(0)

    if args.add==True:
        d=Device(mem)
        d.insert_mac()
        d.insert_alias()
        d.insert_type()
        d.link()
        print (Style.BRIGHT+ Fore.GREEN + app.translate("devicesinlan","Device inserted"))
        mem.settings.sync()
        sys.exit(0)

    if args.remove==True:
        d=Device(mem)
        d.insert_mac()
        d.unlink()
        print (Style.BRIGHT+Fore.GREEN+app.translate("devicesinlan","Mac removed"))

        mem.settings.sync()
        sys.exit(0)

    if args.list==True:
        set=SetDevices(mem)
        set.init__from_settings()
        set.print_devices_from_settings()
        sys.exit(0)
    ## Load devices
    if args.interface:
        if mem.interfaces.find_by_id(args.interface)==None:
            print(Style.BRIGHT+Fore.RED+app.translate("devicesinlan", "This interface doesn't exist. Please remove the --interface parameter to use a wizard."))
            sys.exit(1)
        mem.interfaces.selected=mem.interfaces.find_by_id(args.interface)
    else:
        if mem.interfaces.length()==0:
            print(Style.BRIGHT+ Fore.RED+app.translate("devicesinlan", "There are not interfaces to scan."))
            sys.exit(1)
        mem.interfaces.print()
        while True:
            id=input_int(app.translate("devicesinlan", "Select an interface number"), 1)
            if id<=mem.interfaces.length():#Check id 
                break
        mem.interfaces.selected=mem.interfaces.find_by_id(mem.interfaces.arr[id-1].id())
        mem.settings.setValue("frmSettings/concurrence", input_int(app.translate("devicesinlan", "Input an integer with the request concurrence"), mem.settings.value("frmSettings/concurrence", 200)))
        mem.settings.sync()

    inicio=datetime.datetime.now()
    set=SetDevices(mem)
    set.setMethod(ArpScanMethod.PingArp)
    set.print()
    print (Style.BRIGHT+app.translate("devicesinlan","It took {} with DevicesInLAN scanner.").format (Fore.GREEN+str(datetime.datetime.now()-inicio)+ " "+ app.translate("devicesinlan", "seconds")+Fore.WHITE))
