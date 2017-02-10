import datetime
import argparse
import os
import sys
from libdevicesinlan import version, dateversion
from libmangenerator import Man
from PyQt5.QtCore import QCoreApplication, QTranslator
import logging

if __name__ == "__main__":
    parser=argparse.ArgumentParser( prog='mangenerator', 
                                                            description='devicesinlan doc system',  
                                                            epilog="Developed by Mariano Muñoz 2015-{}".format(dateversion.year), 
                                                            formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version="{} ({})".format(version, dateversion))
    parser.add_argument('--language', help='Language (en|fr|ro|es|ru)', default='en')
    parser.add_argument('--debug', help="Debug program information", default="WARNING")
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
        logging.basicConfig(level=logging.CRITICAL, format=logFormat, datefmt=dateFormat)
        logging.critical("--debug parameter must be DEBUG, INFO, WARNING, ERROR or CRITICAL")
        sys.exit(1)

    if args.language not in ["en", "fr", "ro", "ru", "es"]:
        logging.critical("Bad language")
        sys.exit(1)
    
    app=QCoreApplication(sys.argv)
    app.setOrganizationName("DevicesInLAN")
    app.setOrganizationDomain("devicesinlan.sourceforge.net")
    app.setApplicationName("mangenerator")
    translator=QTranslator()
    urls= ["i18n/devicesinlan_" + args.language + ".qm","/usr/share/devicesinlan/devicesinlan_" + args.language+ ".qm"]
    if args.language!="en":
        for url in urls:
            if os.path.exists(url)==True:
                translator.load(url)
                QCoreApplication.installTranslator(translator)
            else:
                print("Language {} not detected".format(args.language))
    
    man=Man("doc/devicesinlan.{}".format(args.language))
    man.setMetadata("devicesinlan",  1,   datetime.date.today(), "Mariano Muñoz", QCoreApplication.translate("mangenerator","Scans all devices in your LAN. Then you can set an alias to your known devices in order to detect future strange devices in your net."))
    man.setSynopsis("[-h] [--version] [--debug DEBUG] [ --wizard | --interface | --add | --remove | --list ]")
    man.header(QCoreApplication.translate("mangenerator","GUI MODE DESCRIPTION"), 1)
    man.paragraph(QCoreApplication.translate("mangenerator","If you launch devicesinlan without parameters and you are in a graphic system (Linux or Windows) it launches the program with a Qt Interface."), 1)
    man.paragraph(QCoreApplication.translate("mangenerator","In the app menu you have the followings features:"), 1)
    man.paragraph(QCoreApplication.translate("mangenerator","Devices > New Scan"), 2, True)
    man.paragraph(QCoreApplication.translate("mangenerator","Devices > Show devices database"), 2, True)
    man.paragraph(QCoreApplication.translate("mangenerator","Devices > Load devices list"), 2, True)
    man.paragraph(QCoreApplication.translate("mangenerator","Devices > Save devices list"), 2, True)
    man.paragraph(QCoreApplication.translate("mangenerator","Devices > Reset database"), 2, True)
    man.paragraph(QCoreApplication.translate("mangenerator","This option erases all known devices in database."), 3)
    man.paragraph(QCoreApplication.translate("mangenerator","Configuration > Settings"), 2, True)
    man.paragraph(QCoreApplication.translate("mangenerator","In this dialog you can select your prefered language and you can configure the number of concurrence request."), 3)
    man.paragraph(QCoreApplication.translate("mangenerator","Help > Help"), 2, True)
    man.paragraph(QCoreApplication.translate("mangenerator","Shows this help information."), 3)
    man.paragraph(QCoreApplication.translate("mangenerator","Help > About"), 2, True)
    man.paragraph(QCoreApplication.translate("mangenerator","Shows information about DevicesInLAN license and authors."), 3)
    man.paragraph(QCoreApplication.translate("mangenerator","Help > Check for updates"), 2, True)
    man.paragraph(QCoreApplication.translate("mangenerator","Help > Exit"), 2, True)
    man.paragraph(QCoreApplication.translate("mangenerator","Exits from program."), 3)
    
    
    man.header(QCoreApplication.translate("mangenerator","CONSOLE MODE DESCRIPTION"), 1)
    man.paragraph(QCoreApplication.translate("mangenerator","If you launch deviceslan with [ --wizard | --interface | --add | --remove | --list ], it will be executed in console mode."), 1)
    man.paragraph("--wizard", 2, True)
    man.paragraph(QCoreApplication.translate("mangenerator","It list all interfaces in the system and lets you to select the one you wish and the number of concurrent request. After that, it scans the net and prints a list of the detected devices."), 3)
    man.paragraph("--interface", 2, True)
    man.paragraph(QCoreApplication.translate("mangenerator","Scans the net of the interface parameter and prints a list of the detected devices."), 3)
    man.paragraph(QCoreApplication.translate("mangenerator","If a device is not known, it will be showed in red. Devices in green are trusted devices."), 3)
    man.paragraph("--add", 2, True)
    man.paragraph(QCoreApplication.translate("mangenerator","Allows to add a known device from console."), 3)
    man.paragraph("--remove", 2, True)
    man.paragraph(QCoreApplication.translate("mangenerator","Allows to remove a known device from console."), 3)
    man.paragraph("--list", 2, True)
    man.paragraph(QCoreApplication.translate("mangenerator","Shows all knows devices in database from console."), 3)
    man.save()
    man.saveHTML()
