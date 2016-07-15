#!/usr/bin/python3
import argparse
import subprocess
import datetime
import platform
import os
import shutil
import sys
from PyQt5.QtWidgets import *   
if platform.system()=="Windows":
    sys.path.append("ui")
    sys.path.append("images")
elif platform.system()=="Linux":
    sys.path.append("/usr/lib/devicesinlan")
from libdevicesinlan import *

    

"""
    To see information of the ARP protocol, look into doc/devicesinlan.odt
"""
    
##############################################

args=None
app = QApplication(sys.argv)
app.setOrganizationName("DevicesInLAN")
app.setOrganizationDomain("devicesinlan.sourceforge.net")
app.setApplicationName("DevicesInLAN")

mem=Mem()
mem.change_language(mem.settings.value("frmSettings/language", "en"))

if platform.system()=="Windows":
    if os.path.exists(os.path.expanduser("~/.devicesinlan/"))==False:
        try:
            os.makedirs(os.path.expanduser("~/.devicesinlan/"))
        except:
            pass
        shutil.copy("known.txt.dist",os.path.expanduser("~/.devicesinlan/known.txt"))
        print(QApplication.translate("devicesinlan","I couldn't find .devicesinlan/known.txt.") + " " + QApplication.translate("devicesinlan","I copied distribution file to it.") + " "+ QApplication.translate("devicesinlan","Add your mac addresses to detect strage devices in your LAN."))

    app.setQuitOnLastWindowClosed(True)
    import frmMain
    frmMain = frmMain.frmMain(mem) 
    frmMain.show()
    sys.exit(app.exec_())

elif platform.system()=="Linux":
    parser=argparse.ArgumentParser(prog='devicesinlan', description=QApplication.translate("devicesinlan",'Show devices in a LAN making an ARP and a ICMP request to find them'),  
    epilog=QApplication.translate("devicesinlan","If you like this app, please vote for it in Sourceforge (https://sourceforge.net/projects/devicesinlan/reviews/).")+"\n"
          +QApplication.translate("devicesinlan","Developed by Mariano Muñoz 2015-{}".format(dateversion.year))
    , formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-v', '--version', action='version', version=version)
    parser.add_argument('-c',  '--console', help=QApplication.translate("devicesinlan",'Use console app'), action='store_true',  default=False)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-i',  '--interface', help=QApplication.translate("devicesinlan",'Net interface name'),  default='eth0')
    group.add_argument('-a',  '--add', help=QApplication.translate("devicesinlan",'Add a known device'), action='store_true')
    group.add_argument('-r',  '--remove', help=QApplication.translate("devicesinlan",'Remove a known device'), action='store_true')
    group.add_argument('-l',  '--list', help=QApplication.translate("devicesinlan",'List known device'), action='store_true')
    args=parser.parse_args()        
    
    if args.console==False:    
        if os.path.exists("/etc/devicesinlan/known.txt")==False:
            subprocess.check_output(["cp","/etc/devicesinlan/known.txt.dist","/etc/devicesinlan/known.txt"])
            print(QApplication.translate("devicesinlan","I couldn't find /etc/devicesinlan/known.txt.") + " " + QApplication.translate("devicesinlan","I copied distribution file to it.") + " "+ QApplication.translate("devicesinlan","Add your mac addresses to detect strage devices in your LAN."))

        app.setQuitOnLastWindowClosed(True)
        import frmMain 
        frmMain = frmMain.frmMain(mem) 
        frmMain.show()
        sys.exit(app.exec_())

    else:##Console
#        if args.add:
#            k=KnownDevice()
#            k.insert_mac()
#            k.insert_alias()
#            known.append(k)
#            known.save()    
#            print (Color.green(QApplication.translate("devicesinlan","Known device inserted")))
#            sys.exit(0)
#            
#        if args.remove:
#            k=KnownDevice()
#            k.insert_mac()
#            if known.remove_mac(k.mac):
#                known.save()
#                print (Color.green(QApplication.translate("devicesinlan","Mac removed")))
#            else:
#                print (Color.red(QApplication.translate("devicesinlan","I couldn't find the mac")))
#            sys.exit(0)
#            
#        if args.list:
#            known.print()
#            sys.exit(0)
                
        
        ## Load devices
        mem.interfaces.selected=mem.interfaces.find_by_id(args.interface)
        
        inicio=datetime.datetime.now()
        set=SetDevices(mem)
        set.setMethod(ArpScanMethod.PingArp)
        set.print()
        print (QApplication.translate("devicesinlan","It took {} with DevicesInLAN scanner.").format (datetime.datetime.now()-inicio))


