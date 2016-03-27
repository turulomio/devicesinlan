#!/usr/bin/python3
import argparse
import subprocess
import datetime
import gettext
import platform
import os
import shutil
import sys

"""
    To see information of the ARP protocol, look into doc/devicesinlan.odt
"""
    
##############################################

args=None
known=None

_=gettext.gettext



if platform.system()=="Windows":
    sys.path.append("ui")
    sys.path.append("images")
    from libdevicesinlan import *
    if os.path.exists(os.path.expanduser("~/.devicesinlan/"))==False:
        try:
            os.makedirs(os.path.expanduser("~/.devicesinlan/"))
        except:
            pass
        shutil.copy("known.txt.dist",os.path.expanduser("~/.devicesinlan/known.txt"))
        print(_("I couldn't find .devicesinlan/known.txt.") + " " + _("I copied distribution file to it.") + " "+ _("Add your mac addresses to detect strage devices in your LAN."))
    import PyQt5.QtCore
    import PyQt5.QtGui
    import PyQt5.QtWidgets
    import frmMain 

    
    app = PyQt5.QtWidgets.QApplication(sys.argv)
    app.setApplicationName("devicesinlan {0}".format(str(datetime.datetime.now())))
    app.setQuitOnLastWindowClosed(True)

    frmMain = frmMain.frmMain() 
    frmMain.show()
    sys.exit(app.exec_())

elif platform.system()=="Linux":
    sys.path.append("/usr/lib/devicesinlan")
    from libdevicesinlan import *
    parser=argparse.ArgumentParser(prog='devicesinlan', description=_('Show devices in a LAN making an ARP and a ICMP request to find them'),  
    epilog=_("If you like this app, please vote for it in Sourceforge (https://sourceforge.net/projects/devicesinlan/reviews/).")+"\n"
          +_("Developed by Mariano Muñoz 2015 ©")
    , formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-v', '--version', action='version', version=version)
    parser.add_argument('-m', '--my', help=_('Use my own arp scanner'), action='store_true')
    parser.add_argument('-c',  '--console', help=_('Use console app'), action='store_true',  default=False)
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

    if args.console==False:
        
        import PyQt5.QtCore
        import PyQt5.QtGui
        import PyQt5.QtWidgets
        import frmMain 

        
        app = PyQt5.QtWidgets.QApplication(sys.argv)
        app.setApplicationName("devicesinlan {0}".format(str(datetime.datetime.now())))
        app.setQuitOnLastWindowClosed(True)

        frmMain = frmMain.frmMain() 
        frmMain.show()
        sys.exit(app.exec_())

    else:##Console
        
        
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


