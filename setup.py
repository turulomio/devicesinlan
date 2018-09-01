from devicesinlan import __version__
from setuptools import setup, Command
from mangenerator import Man

import datetime
import gettext
import logging
import os
import platform
import site
import sys
from PyQt5.QtCore import QCoreApplication,  QTranslator
from colorama import Style, Fore
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
def change_language(language):  
    """language es un string"""
    url= "devicesinlan/data/devicesinlan_{}.qm".format(language)
    if os.path.exists(url)==True:
        translator.load(url)
        QCoreApplication.installTranslator(translator)
        logging.info(("Language changed to {} using {}".format(language, url)))
        return
    if language!="en":
        logging.warning(Style.BRIGHT+ Fore.CYAN+ app.tr("Language ({}) couldn't be loaded in {}. Using default (en).".format(language, url)))

class Doxygen(Command):
    description = "Create/update doxygen documentation in doc/html"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print("Creating Doxygen Documentation")
        os.system("""sed -i -e "41d" doc/Doxyfile""")#Delete line 41
        os.system("""sed -i -e "41iPROJECT_NUMBER         = {}" doc/Doxyfile""".format(__version__))#Insert line 41
        os.chdir("doc")
        os.system("doxygen Doxyfile")
        os.system("cp ttyrec/devicesinlan_howto_en.gif html")#Copies images
        os.system("rsync -avzP -e 'ssh -l turulomio' html/ frs.sourceforge.net:/home/users/t/tu/turulomio/userweb/htdocs/doxygen/too-many-files/ --delete-after")
        os.chdir("..")

class Video(Command):
    description = "Create video/GIF from console ouput"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.chdir("doc/ttyrec")
        os.system("ttyrecgenerator --output devicesinlan_howto_es 'python3 howto.py' --lc_all es_ES.UTF-8")
        os.system("ttyrecgenerator --output devicesinlan_howto_en 'python3 howto.py' --lc_all C")
        os.chdir("../..")

class Compile(Command):
    description = "Compile ui and images"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        futures=[]
        with ProcessPoolExecutor(max_workers=cpu_count()+1) as executor:
            futures.append(executor.submit(os.system, "pyuic5 devicesinlan/ui/frmAbout.ui -o devicesinlan/ui/Ui_frmAbout.py"))
            futures.append(executor.submit(os.system, "pyuic5 devicesinlan/ui/frmHelp.ui -o devicesinlan/ui/Ui_frmHelp.py"))
            futures.append(executor.submit(os.system, "pyuic5 devicesinlan/ui/frmMain.ui -o devicesinlan/ui/Ui_frmMain.py"))
            futures.append(executor.submit(os.system, "pyuic5 devicesinlan/ui/frmSettings.ui -o devicesinlan/ui/Ui_frmSettings.py"))
            futures.append(executor.submit(os.system, "pyuic5 devicesinlan/ui/frmInterfaceSelector.ui -o devicesinlan/ui/Ui_frmInterfaceSelector.py"))
            futures.append(executor.submit(os.system, "pyuic5 devicesinlan/ui/frmDeviceCRUD.ui -o devicesinlan/ui/Ui_frmDeviceCRUD.py"))
            futures.append(executor.submit(os.system, "pyrcc5 images/devicesinlan.qrc -o devicesinlan/ui/devicesinlan_rc.py"))
        for file in ['devicesinlan/ui/Ui_frmAbout.py', 'devicesinlan/ui/Ui_frmHelp.py', 'devicesinlan/ui/Ui_frmMain.py', 'devicesinlan/ui/Ui_frmSettings.py', 'devicesinlan/ui/Ui_frmInterfaceSelector.py', 'devicesinlan/ui/Ui_frmDeviceCRUD.py']:
            os.system("sed -i -e 's/devicesinlan_rc/devicesinlan.ui.devicesinlan_rc/' {}".format(file))

class Uninstall(Command):
    description = "Uninstall installed files with install"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if platform.system()=="Linux":
            os.system("rm -Rf {}/devicesinlan*".format(site.getsitepackages()[0]))
            os.system("rm /usr/bin/devicesinlan")
            os.system("rm /usr/share/man/man1/devicesinlan.1")
            os.system("rm /usr/share/man/es/man1/devicesinlan.1")
        else:
            print(_("Uninstall command only works in Linux"))

class Doc(Command):
    description = "Update man pages and translations"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system("pylupdate5 -noobsolete -verbose devicesinlan.pro")
        os.system("lrelease -qt5 devicesinlan.pro")
        for language in ["en", "fr", "ro", "ru", "es"]:
            self.mangenerator(language)

    def mangenerator(self, language):
        change_language(language)
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

app=QCoreApplication(sys.argv)

app.setOrganizationName("DevicesInLAN")
app.setOrganizationDomain("devicesinlan.sourceforge.net")
app.setApplicationName("DevicesInLAN")
translator=QTranslator()
with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

if platform.system()=="Linux":
    data_files=[]
    #('/usr/share/man/man1/', ['man/man1/devicesinlan.1']), 
    #            ('/usr/share/man/es/man1/', ['man/es/man1/devicesinlan.1'])
    #           ]
else:
    data_files=[]

setup(name='devicesinlan',
    version=__version__,
    description='Find devices in a lan',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=['Development Status :: 4 - Beta',
              'Intended Audience :: Developers',
              'Topic :: Software Development :: Build Tools',
              'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
              'Programming Language :: Python :: 3',
             ], 
    keywords='remove files datetime patterns',
    url='https://devicesinlan.sourceforge.io/',
    author='Turulomio',
    author_email='turulomio@yahoo.es',
    license='GPL-3',
    packages=['devicesinlan'],
    entry_points = {'console_scripts': [    'devicesinlan=devicesinlan.devicesinlan:main',
                                                                        'devicesinlan_gui=devicesinlan.devicesinlan_gui:main',
                                    ],
                },
    install_requires=['colorama','setuptools'],
    data_files=data_files,
    cmdclass={
                        'doxygen': Doxygen,
                        'doc': Doc,
                        'uninstall':Uninstall, 
                        'video': Video, 
                        'compile': Compile, 
                     },
    zip_safe=False,
    include_package_data=True
    )

_=gettext.gettext#To avoid warnings
