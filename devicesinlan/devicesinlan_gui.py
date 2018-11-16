#!/usr/bin/python3
import argparse
import sys
import logging
from colorama import init
from PyQt5.QtWidgets import QApplication

#############################

from devicesinlan.libdevicesinlan import Mem
from devicesinlan.version import __version__, __versiondate__
from devicesinlan.ui.frmMain  import frmMain
def main():
    init(autoreset=True)

    app=QApplication(sys.argv)
                
    app.setOrganizationName("DevicesInLAN")
    app.setOrganizationDomain("devicesinlan.sourceforge.net")
    app.setApplicationName("DevicesInLAN")

    parser=argparse.ArgumentParser(prog='devicesinlan_gui', description=app.translate("devicesinlan",'Show devices in a LAN making an ARP search to find them with a user interface'),  
        epilog=app.translate("devicesinlan","If you like this app, please vote for it in Sourceforge (https://sourceforge.net/projects/devicesinlan/reviews/).")+"\n" +app.translate("devicesinlan","Developed by Mariano Muñoz 2015-{}".format(__versiondate__.year)), 
        formatter_class=argparse.RawTextHelpFormatter
        )
    parser.add_argument('--version', action='version', version="{} ({})".format(__version__, __versiondate__))
    parser.add_argument('--debug', help=app.translate("devicesinlan", "Debug program information"))
    args=parser.parse_args()        

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

    app.setQuitOnLastWindowClosed(True)
    f = frmMain(mem) 
    f.show()
    sys.exit(app.exec_())

