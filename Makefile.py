#!/usr/bin/python3
import argparse
import datetime
import os
import sys
import platform
from subprocess import call, check_call
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
from libdevicesinlan import version

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


if __name__ == '__main__':
    start=datetime.datetime.now()
    parser=argparse.ArgumentParser(prog='Makefile.py', description='Makefile in python', epilog="Developed by Mariano Muñoz", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--doc', help="Generate docs and i18n",action="store_true",default=False)
    parser.add_argument('--compile', help="App compilation",action="store_true",default=False)
    parser.add_argument('--compile_images', help="App images compilation",action="store_true",default=False)
    parser.add_argument('--destdir', help="Directory to install",action="store",default="/")
    parser.add_argument('--uninstall', help="Uninstall",action="store_true",default=False)
    parser.add_argument('--dist_sources', help="Make a sources tar", action="store_true",default=False)
    parser.add_argument('--dist_linux', help="Make a Linux binary distribution", action="store_true",default=False)
    parser.add_argument('--dist_windows', help="Make a Windows binary distribution", action="store_true",default=False)
    parser.add_argument('--python', help="Python path", action="store",default='/usr/bin/python3')
    args=parser.parse_args()

    prefixbin=args.destdir+"/usr/bin"
    prefixlib=args.destdir+"/usr/lib/devicesinlan"
    prefixshare=args.destdir+"/usr/share/devicesinlan"
    prefixpixmaps=args.destdir+"/usr/share/pixmaps"
    prefixapplications=args.destdir+"/usr/share/applications"
    prefixman=args.destdir+"/usr/share/man"

    if "--dist_windows" in sys.argv and platform.system()!="Windows":
        print("You need to be in Windows to pass this parameters")
        sys.exit(1)
    elif "--dist_windows" not in sys.argv and platform.system=="Windows":#In windows only dist_windows
        print("You need to be in Linux to pass this parameters")
        sys.exit(1)


    if args.doc==True:
        shell("pylupdate5 -noobsolete -verbose devicesinlan.pro")
        shell("lrelease -qt5 devicesinlan.pro")
        futures=[]
        with ProcessPoolExecutor(max_workers=cpu_count()+1) as executor:
            futures.append(executor.submit(shell, "python3 mangenerator.py --language en"))
            futures.append(executor.submit(shell, "python3 mangenerator.py --language es"))
            futures.append(executor.submit(shell, "python3 mangenerator.py --language fr"))
            futures.append(executor.submit(shell, "python3 mangenerator.py --language ro"))
            futures.append(executor.submit(shell, "python3 mangenerator.py --language ru")) 
    elif args.uninstall==True:
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
    elif args.dist_sources==True:
        shell("{} setup.py sdist".format(args.python))
    elif args.dist_linux==True:
        shell("{} setup.py build_exe".format(args.python))    
        print (build_dir(), filename_output(), os.getcwd())
        pwd=os.getcwd()
        os.chdir(build_dir())
        print (build_dir(), filename_output(), os.getcwd())
        os.system("tar cvz -C '{0}/{2}/'  -f '{0}/dist/{1}.tar.gz' *".format(pwd, filename_output(),  build_dir()))
    elif args.dist_windows==True:
        check_call([sys.executable, "setup.py","bdist_msi"])
    elif args.compile==True:
        futures=[]
        with ProcessPoolExecutor(max_workers=cpu_count()+1) as executor:
            futures.append(executor.submit(shell, "pyuic5 ui/frmAbout.ui -o ui/Ui_frmAbout.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmHelp.ui -o ui/Ui_frmHelp.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmMain.ui -o ui/Ui_frmMain.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmSettings.ui -o ui/Ui_frmSettings.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmInterfaceSelector.ui -o ui/Ui_frmInterfaceSelector.py"))
            futures.append(executor.submit(shell, "pyuic5 ui/frmDeviceCRUD.ui -o ui/Ui_frmDeviceCRUD.py"))
    elif args.compile_images==True:
            shell("pyrcc5 images/devicesinlan.qrc -o images/devicesinlan_rc.py")
    else:
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
        shell("install -m 644 -o root ui/*.py libdevicesinlan.py libmangenerator.py images/*.py "+ prefixlib)
        shell("install -m 644 -o root i18n/*.qm " + prefixlib)
        shell("install -m 644 -o root devicesinlan.desktop "+ prefixapplications)
        shell("install -m 644 -o root images/devicesinlan.png "+ prefixpixmaps+"/devicesinlan.png")
        shell("install -m 644 -o root GPL-3.txt CHANGELOG.txt AUTHORS.txt INSTALL.txt ieee-oui.txt doc/devicesinlan*.html "+ prefixshare)
        shell("install -m 644 -o root doc/devicesinlan.en.1 "+ prefixman+"/man1/devicesinlan.1")
        shell("install -m 644 -o root doc/devicesinlan.es.1 "+ prefixman+"/es/man1/devicesinlan.1")
        shell("install -m 644 -o root doc/devicesinlan.fr.1 "+ prefixman+"/fr/man1/devicesinlan.1")
        shell("install -m 644 -o root doc/devicesinlan.ro.1 "+ prefixman+"/ro/man1/devicesinlan.1")
        shell("install -m 644 -o root doc/devicesinlan.ru.1 "+ prefixman+"/ru/man1/devicesinlan.1")
        
    print ("*** Process took {} using {} processors ***".format(datetime.datetime.now()-start , cpu_count()))

