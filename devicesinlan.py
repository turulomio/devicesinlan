#!/usr/bin/python3
import argparse
import datetime
import platform
import sys
import signal
def signal_handler(signal, frame):
        print(Style.BRIGHT+Fore.RED+app.translate("devicesinlan","You pressed 'Ctrl+C', exiting..."))
        sys.exit(0)
#############################3

if platform.system()=="Windows":
    sys.path.append("ui")
    sys.path.append("images")
elif platform.system()=="Linux":
    sys.path.append("/usr/lib/devicesinlan")
from libdevicesinlan import ArpScanMethod, Device, Mem, SetDevices, dateversion,  version,  input_int
from colorama import init,  Style, Fore
init(autoreset=True)

if len(sys.argv)>1:#To see if it's console or not
    from PyQt5.QtCore import QCoreApplication
    console=True
    app=QCoreApplication(sys.argv)
    tr=QCoreApplication.translate
else:
    from PyQt5.QtWidgets import QApplication
    console=False
    app=QApplication(sys.argv)
    tr=QApplication(sys.argv).translate

app.setOrganizationName("DevicesInLAN")
app.setOrganizationDomain("devicesinlan.sourceforge.net")
app.setApplicationName("DevicesInLAN")

mem=Mem()
mem.change_language(mem.settings.value("frmSettings/language", "en"))

signal.signal(signal.SIGINT, signal_handler)

parser=argparse.ArgumentParser(prog='devicesinlan', description=app.translate("devicesinlan",'Show devices in a LAN making an ARP and a ICMP request to find them'),  
epilog=app.translate("devicesinlan","If you like this app, please vote for it in Sourceforge (https://sourceforge.net/projects/devicesinlan/reviews/).")+"\n"
      +app.translate("devicesinlan","Developed by Mariano Muñoz 2015-{}".format(dateversion.year))
, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--version', action='version', version="{} ({})".format(version, dateversion))
group = parser.add_mutually_exclusive_group()
group.add_argument('--wizard', help=app.translate("devicesinlan",'Uses a wizard to select options'), action='store_true',  default=False)
group.add_argument('--interface', help=app.translate("devicesinlan",'Net interface name'))
group.add_argument('--add', help=app.translate("devicesinlan",'Add a known device'), action='store_true')
group.add_argument('--remove', help=app.translate("devicesinlan",'Remove a known device'), action='store_true')
group.add_argument('--list', help=app.translate("devicesinlan",'List known devices'), action='store_true')
args=parser.parse_args()        
    
if console==False:    
    app.setQuitOnLastWindowClosed(True)
    import frmMain 
    frmMain = frmMain.frmMain(mem) 
    frmMain.show()
    sys.exit(app.exec_())
else:##Console
    if args.add==True:
        d=Device(mem)
        d.insert_mac()
        d.insert_alias()
        d.type=mem.types.find_by_id(0)
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
            print(Style.BRIGHT+Fore.RED+app.translate("devicesinlan", "This interface doesn't exist. Please use --wizard parameter to help you."))
            sys.exit(1)
        mem.interfaces.selected=mem.interfaces.find_by_id(args.interface)
        
    if args.wizard==True:
        if mem.interfaces.length()==0:
            print(Style.BRIGHT+ Fore.RED+app.translate("devicesinlan", "There are not interfaces to scan."))
            sys.exit(1)
        mem.interfaces.print()
        while True:
            id=input_int(app.translate("devicesinlan", "Select an interface number"), 1)
            if id<=mem.interfaces.length():#Check id 
                break
        mem.interfaces.selected=mem.interfaces.find_by_id(mem.interfaces.arr[id-1].id)
        mem.settings.setValue("frmSettings/concurrence", input_int(app.translate("devicesinlan", "Input an integer with the request concurrence"), mem.settings.value("frmSettings/concurrence", 200)))
        
    
    inicio=datetime.datetime.now()
    set=SetDevices(mem)
    set.setMethod(ArpScanMethod.PingArp)
    set.print()
    print (Style.BRIGHT+app.translate("devicesinlan","It took {} with DevicesInLAN scanner.").format (Fore.GREEN+str(datetime.datetime.now()-inicio)+ " "+ app.translate("devicesinlan", "seconds")+Fore.WHITE))


