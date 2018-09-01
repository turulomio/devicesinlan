#!/usr/bin/python3
import argparse
import datetime
import os
import sys
import platform
from subprocess import call, check_call
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
from libdevicesinlan import version,  MemApp
from libmangenerator import Man
from PyQt5.QtCore import QCoreApplication

def shell(*args):
    print(" ".join(args))
    call(args,shell=True)

def build_dir():
    pyversion="{}.{}".format(sys.version_info[0], sys.version_info[1])
    if sys.platform=="win32":
        so="win"
        if platform.architecture()[0]=="64bit":
            pl="amd64"
        else:
            pl="win32"
            return "build/exe.{}-{}".format(sys.platform, pyversion)
    else:#linux
        so="linux"
        if platform.architecture()[0]=="64bit":
            pl="x86_64"
        else:
            pl="i686"
    return "build/exe.{}-{}-{}".format(so, pl, pyversion)

def filename_output():
    if sys.platform=="win32":
        so="windows"
        if platform.architecture()[0]=="64bit":
            pl="amd64"
        else:
            pl="win32"
    else:#linux
        so="linux"
        if platform.architecture()[0]=="64bit":
            pl="x86_64"
        else:
            pl="x86"
    return "xulpymoney-{}-{}.{}".format(so,  version, pl)
    
def makefile_compile():
    futures=[]
    with ProcessPoolExecutor(max_workers=cpu_count()+1) as executor:
        futures.append(executor.submit(shell, "pyuic5 ui/frmAbout.ui -o ui/Ui_frmAbout.py"))
        futures.append(executor.submit(shell, "pyuic5 ui/frmHelp.ui -o ui/Ui_frmHelp.py"))
        futures.append(executor.submit(shell, "pyuic5 ui/frmMain.ui -o ui/Ui_frmMain.py"))
        futures.append(executor.submit(shell, "pyuic5 ui/frmSettings.ui -o ui/Ui_frmSettings.py"))
        futures.append(executor.submit(shell, "pyuic5 ui/frmInterfaceSelector.ui -o ui/Ui_frmInterfaceSelector.py"))
        futures.append(executor.submit(shell, "pyuic5 ui/frmDeviceCRUD.ui -o ui/Ui_frmDeviceCRUD.py"))
def makefile_compile_images():
    shell("pyrcc5 images/devicesinlan.qrc -o images/devicesinlan_rc.py")
def makefile_dist_linux():
    shell("{} setup.py build_exe".format(args.python))    
    print (build_dir(), filename_output(), os.getcwd())
    pwd=os.getcwd()
    os.chdir(build_dir())
    print (build_dir(), filename_output(), os.getcwd())
    os.system("tar cvz -C '{0}/{2}/'  -f '{0}/dist/{1}.tar.gz' *".format(pwd, filename_output(),  build_dir()))
def makefile_dist_sources():
    shell("{} setup.py sdist".format(args.python))
def makefile_dist_windows():
    check_call([sys.executable, "setup.py","bdist_msi"])
def makefile_doc():
    shell("pylupdate5 -noobsolete -verbose devicesinlan.pro")
    shell("lrelease -qt5 devicesinlan.pro")
    for language in ["en", "fr", "ro", "ru", "es"]:
        mangenerator(language)

def makefile_install_all():
        shell("install -o root -d "+ prefixbin)
        shell("install -o root -d "+ prefixlib)
        shell("install -o root -d "+ prefixshare)
        shell("install -o root -d "+ prefixpixmaps)
        shell("install -o root -d "+ prefixapplications)
        shell("install -o root -d "+ prefixman+"/man1")
        shell("install -o root -d "+ prefixman+"/es/man1")
        shell("install -o root -d "+ prefixman+"/fr/man1")
        shell("install -o root -d "+ prefixman+"/ro/man1")
        shell("install -o root -d "+ prefixman+"/ru/man1")

        shell("install -m 755 -o root devicesinlan.py "+ prefixbin+"/devicesinlan")
        shell("install -m 755 -o root devicesinlan_gui.py "+ prefixbin+"/devicesinlan_gui")
        shell("install -m 644 -o root ui/*.py libdevicesinlan.py libdevicesinlan_gui.py images/*.py "+ prefixlib)
        shell("install -m 644 -o root i18n/*.qm " + prefixlib)
        shell("install -m 644 -o root devicesinlan.desktop "+ prefixapplications)
        shell("install -m 644 -o root images/devicesinlan.png "+ prefixpixmaps+"/devicesinlan.png")
        shell("install -m 644 -o root GPL-3.txt CHANGELOG.txt AUTHORS.txt INSTALL.txt ieee-oui.txt doc/devicesinlan*.html "+ prefixshare)
        shell("install -m 644 -o root doc/devicesinlan.en.1 "+ prefixman+"/man1/devicesinlan.1")
        shell("install -m 644 -o root doc/devicesinlan.es.1 "+ prefixman+"/es/man1/devicesinlan.1")
        shell("install -m 644 -o root doc/devicesinlan.fr.1 "+ prefixman+"/fr/man1/devicesinlan.1")
        shell("install -m 644 -o root doc/devicesinlan.ro.1 "+ prefixman+"/ro/man1/devicesinlan.1")
        shell("install -m 644 -o root doc/devicesinlan.ru.1 "+ prefixman+"/ru/man1/devicesinlan.1")
        shell("install -m 644 -o root doc/devicesinlan_gui.en.1 "+ prefixman+"/man1/devicesinlan_gui.1")
        shell("install -m 644 -o root doc/devicesinlan_gui.es.1 "+ prefixman+"/es/man1/devicesinlan_gui.1")
        shell("install -m 644 -o root doc/devicesinlan_gui.fr.1 "+ prefixman+"/fr/man1/devicesinlan_gui.1")
        shell("install -m 644 -o root doc/devicesinlan_gui.ro.1 "+ prefixman+"/ro/man1/devicesinlan_gui.1")
        shell("install -m 644 -o root doc/devicesinlan_gui.ru.1 "+ prefixman+"/ru/man1/devicesinlan_gui.1")

def makefile_install_console():
        shell("install -o root -d "+ prefixbin)
        shell("install -o root -d "+ prefixlib)
        shell("install -o root -d "+ prefixshare)
        shell("install -o root -d "+ prefixman+"/man1")
        shell("install -o root -d "+ prefixman+"/es/man1")
        shell("install -o root -d "+ prefixman+"/fr/man1")
        shell("install -o root -d "+ prefixman+"/ro/man1")
        shell("install -o root -d "+ prefixman+"/ru/man1")

        shell("install -m 755 -o root devicesinlan.py "+ prefixbin+"/devicesinlan")
        shell("install -m 644 -o root libdevicesinlan.py "+ prefixlib)
        shell("install -m 644 -o root i18n/*.qm " + prefixlib)
        shell("install -m 644 -o root GPL-3.txt CHANGELOG.txt AUTHORS.txt INSTALL.txt ieee-oui.txt "+ prefixshare)
        shell("install -m 644 -o root doc/devicesinlan.en.1 "+ prefixman+"/man1/devicesinlan.1")
        shell("install -m 644 -o root doc/devicesinlan.es.1 "+ prefixman+"/es/man1/devicesinlan.1")
        shell("install -m 644 -o root doc/devicesinlan.fr.1 "+ prefixman+"/fr/man1/devicesinlan.1")
        shell("install -m 644 -o root doc/devicesinlan.ro.1 "+ prefixman+"/ro/man1/devicesinlan.1")
        shell("install -m 644 -o root doc/devicesinlan.ru.1 "+ prefixman+"/ru/man1/devicesinlan.1")
        shell("install -m 644 -o root doc/devicesinlan_gui.en.1 "+ prefixman+"/man1/devicesinlan_gui.1")
        shell("install -m 644 -o root doc/devicesinlan_gui.es.1 "+ prefixman+"/es/man1/devicesinlan_gui.1")
        shell("install -m 644 -o root doc/devicesinlan_gui.fr.1 "+ prefixman+"/fr/man1/devicesinlan_gui.1")
        shell("install -m 644 -o root doc/devicesinlan_gui.ro.1 "+ prefixman+"/ro/man1/devicesinlan_gui.1")
        shell("install -m 644 -o root doc/devicesinlan_gui.ru.1 "+ prefixman+"/ru/man1/devicesinlan_gui.1")

def makefile_uninstall():
    shell("rm " + prefixbin + "/devicesinlan*")
    shell("rm -Rf " + prefixlib)
    shell("rm -Rf " + prefixshare)
    shell("rm -fr " + prefixpixmaps + "/devicesinlan.png")
    shell("rm -fr " + prefixapplications +"/devicesinlan.desktop")
    shell("rm -Rf {}/man1/devicesinlan.1".format(prefixman))
    shell("rm -Rf {}/es/man1/devicesinlan.1".format(prefixman))
    shell("rm -Rf {}/fr/man1/devicesinlan.1".format(prefixman))
    shell("rm -Rf {}/ro/man1/devicesinlan.1".format(prefixman))
    shell("rm -Rf {}/ru/man1/devicesinlan.1".format(prefixman))
    shell("rm -Rf {}/man1/devicesinlan_gui.1".format(prefixman))
    shell("rm -Rf {}/es/man1/devicesinlan_gui.1".format(prefixman))
    shell("rm -Rf {}/fr/man1/devicesinlan_gui.1".format(prefixman))
    shell("rm -Rf {}/ro/man1/devicesinlan_gui.1".format(prefixman))
    shell("rm -Rf {}/ru/man1/devicesinlan_gui.1".format(prefixman))

def video():
    os.chdir("doc/ttyrec")
    shell("ttyrecgenerator --output devicesinlan_howto_es 'python3 howto.py --language es' --video")
    shell("ttyrecgenerator --output devicesinlan_howto_en 'python3 howto.py --language en' --video")
    os.chdir("../..")

def doxygen():
    os.chdir("doc")
    shell("doxygen Doxyfile")
    shell("rsync -avzP -e 'ssh -l turulomio' html/ frs.sourceforge.net:/home/users/t/tu/turulomio/userweb/htdocs/doxygen/devicesinlan/ --delete-after")
    os.chdir("..")


def mangenerator(language):
    """
        Create man pages for parameter language
    """
    mem.change_language(language)
    print("DESCRIPTION in {} is {}".format(language, QCoreApplication.translate("devicesinlan", "DESCRIPTION")))

    man=Man("doc/devicesinlan_gui.{}".format(language))
    man.setMetadata("devicesinlan_gui",  1,   datetime.date.today(), "Mariano Muñoz", QCoreApplication.translate("devicesinlan","Scans all devices in your LAN. Then you can set an alias to your known devices in order to detect future strange devices in your net."))
    man.setSynopsis("[--help] [--version] [--debug DEBUG]")
    man.header(QCoreApplication.translate("devicesinlan","DESCRIPTION"), 1)
    man.paragraph(QCoreApplication.translate("devicesinlan","In the app menu you have the followings features:"), 1)
    man.paragraph(QCoreApplication.translate("devicesinlan","Devices > New Scan"), 2, True)
    man.paragraph(QCoreApplication.translate("devicesinlan","Searches all devices in tha LAN and show them in a new tab. If some device is not in the known devices list it will be shown with a red background. Devices with a green background are trusted devices"), 3)
    man.paragraph(QCoreApplication.translate("devicesinlan","Devices > Show devices database"), 2, True)
    man.paragraph(QCoreApplication.translate("devicesinlan","Shows all known devices in a new tab."), 3)
    man.paragraph(QCoreApplication.translate("devicesinlan","Right click allows you to edit known devices database."), 3)
    man.paragraph(QCoreApplication.translate("devicesinlan","Devices > Load devices list"), 2, True)
    man.paragraph(QCoreApplication.translate("devicesinlan","Loads a list of known devices in xml format."), 3)
    man.paragraph(QCoreApplication.translate("devicesinlan","Devices > Save devices list"), 2, True)
    man.paragraph(QCoreApplication.translate("devicesinlan","Saves the known devices list to a xml file."), 3)
    man.paragraph(QCoreApplication.translate("devicesinlan","Devices > Reset database"), 2, True)
    man.paragraph(QCoreApplication.translate("devicesinlan","Removes all known devices."), 3)
    man.paragraph(QCoreApplication.translate("devicesinlan","This option erases all known devices in database."), 3)
    man.paragraph(QCoreApplication.translate("devicesinlan","Configuration > Settings"), 2, True)
    man.paragraph(QCoreApplication.translate("devicesinlan","In this dialog you can select your prefered language and you can configure the number of concurrence request."), 3)
    man.paragraph(QCoreApplication.translate("devicesinlan","Help > Help"), 2, True)
    man.paragraph(QCoreApplication.translate("devicesinlan","Shows this help information."), 3)
    man.paragraph(QCoreApplication.translate("devicesinlan","Help > About"), 2, True)
    man.paragraph(QCoreApplication.translate("devicesinlan","Shows information about DevicesInLAN license and authors."), 3)
    man.paragraph(QCoreApplication.translate("devicesinlan","Help > Check for updates"), 2, True)
    man.paragraph(QCoreApplication.translate("devicesinlan","Checks for updates in DevicesInLan repository."), 3)
    man.paragraph(QCoreApplication.translate("devicesinlan","Help > Exit"), 2, True)
    man.paragraph(QCoreApplication.translate("devicesinlan","Exits from program."), 3)
    man.save()
    man.saveHTML()

    man=Man("doc/devicesinlan.{}".format(language))
    man.setMetadata("devicesinlan",  1,   datetime.date.today(), "Mariano Muñoz", QCoreApplication.translate("devicesinlan","Scans all devices in your LAN. Then you can set an alias to your known devices in order to detect future strange devices in your net."))
    man.setSynopsis("[--help] [--version] [--debug DEBUG] [ --interface | --add | --remove | --list | --load | --save | --reset ]")

    man.header(QCoreApplication.translate("devicesinlan","DESCRIPTION"), 1)
    man.paragraph(QCoreApplication.translate("devicesinlan","If you launch deviceslan without parameters a console wizard is launched."), 1)
    man.paragraph(QCoreApplication.translate("devicesinlan","Morever you can use one of this parameters."), 1)
    man.paragraph("--interface", 2, True)
    man.paragraph(QCoreApplication.translate("devicesinlan","Scans the net of the interface parameter and prints a list of the detected devices."), 3)
    man.paragraph(QCoreApplication.translate("devicesinlan","If a device is not known, it will be showed in red. Devices in green are trusted devices."), 3)
    man.paragraph("--add", 2, True)
    man.paragraph(QCoreApplication.translate("devicesinlan","Allows to add a known device from console."), 3)
    man.paragraph("--remove", 2, True)
    man.paragraph(QCoreApplication.translate("devicesinlan","Allows to remove a known device from console."), 3)
    man.paragraph("--list", 2, True)
    man.paragraph(QCoreApplication.translate("devicesinlan","Shows all known devices in database from console."), 3)
    man.paragraph("--load", 2, True)
    man.paragraph(QCoreApplication.translate("devicesinlan","Loads a list of known devices in xml format."), 3)
    man.paragraph("--save", 2, True)
    man.paragraph(QCoreApplication.translate("devicesinlan","Saves the known devices list to a xml file."), 3)
    man.paragraph("--debug", 2, True)
    man.paragraph(QCoreApplication.translate("devicesinlan","Gives debugging information when running DevicesInLAN. It's deactivated by default"), 3)
    man.paragraph(QCoreApplication.translate("devicesinlan","The parameter can take this options: CRITICAL, ERROR, WARNING, INFO, DEBUG."), 3)
    man.paragraph("--reset", 2, True)
    man.paragraph(QCoreApplication.translate("devicesinlan","Removes all known devices."), 3)
    man.save()
    man.saveHTML()
    ########################################################################

if __name__ == '__main__':
    start=datetime.datetime.now()
    parser=argparse.ArgumentParser(prog='Makefile.py', description='Makefile in python', epilog="Developed by Mariano Muñoz", formatter_class=argparse.RawTextHelpFormatter)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--doc', help="Generate docs and i18n",action="store_true",default=False)
    group.add_argument('--compile', help="App compilation",action="store_true",default=False)
    group.add_argument('--compile_images', help="App images compilation",action="store_true",default=False)
    group.add_argument('--install_all', help="Directory to install console and gui app. / recomended",action="store", metavar="PATH", default=None)
    group.add_argument('--install_console', help="Directory to install only console app. / recomended",action="store", metavar="PATH", default=None)
    group.add_argument('--uninstall', help="Uninstall. / recomended",action="store", metavar="PATH", default=None)
    group.add_argument('--dist_sources', help="Make a sources tar", action="store_true",default=False)
    group.add_argument('--dist_linux', help="Make a Linux binary distribution", action="store_true",default=False)
    group.add_argument('--dist_windows', help="Make a Windows binary distribution", action="store_true",default=False)
    group.add_argument('--doxygen', help="Generate api documentation with doxygen",action="store_true",default=False)
    group.add_argument('--video', help="Make a HOWTO video and gif", action="store_true",default=False)
    parser.add_argument('--python', help="Python path", action="store",default='/usr/bin/python3')



    args=parser.parse_args()

    if "--dist_windows" in sys.argv and platform.system()!="Windows":
        print("You need to be in Windows to pass this parameters")
        sys.exit(1)
    elif "--dist_windows" not in sys.argv and platform.system=="Windows":#In windows only dist_windows
        print("You need to be in Linux to pass this parameters")
        sys.exit(1)

    app=QCoreApplication(sys.argv)#Needed for man generator
    app.setOrganizationName("DevicesInLAN")
    app.setOrganizationDomain("devicesinlan.sourceforge.net")
    app.setApplicationName("devicesinlan_makefile")

    mem=MemApp()
    mem.setApp(app)

    if args.install_all or args.install_console or args.uninstall:
        if args.install_all:
            destdir=args.install_all
        elif args.install_console:
            destdir=args.install_console
        elif args.uninstall:
            destdir=args.uninstall

        prefixbin=destdir+"/usr/bin"
        prefixlib=destdir+"/usr/lib/devicesinlan"
        prefixshare=destdir+"/usr/share/devicesinlan"
        prefixpixmaps=destdir+"/usr/share/pixmaps"
        prefixapplications=destdir+"/usr/share/applications"
        prefixman=destdir+"/usr/share/man"

        if args.install_all:
            makefile_install_all()
        if args.install_console:
            makefile_install_console()
        if args.uninstall:
            makefile_uninstall()

    elif args.doc==True:
        makefile_doc()
    elif args.dist_sources==True:
        makefile_dist_sources()
    elif args.dist_linux==True:
        makefile_dist_linux()
    elif args.dist_windows==True:
        makefile_dist_windows()
    elif args.compile==True:
        makefile_compile()
    elif args.compile_images==True:
        makefile_compile_images()
    elif args.doxygen==True:
        doxygen()
    elif args.video==True:
        video()

    print ("*** Process took {} using {} processors ***".format(datetime.datetime.now()-start , cpu_count()))

