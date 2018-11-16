from setuptools import setup, Command

import datetime
import gettext
import logging
import os
import platform
import shutil
import site
import sys
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count



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
        os.system("rsync -avzP -e 'ssh -l turulomio' html/ frs.sourceforge.net:/home/users/t/tu/turulomio/userweb/htdocs/doxygen/too-many-files/ --delete-after")
        os.chdir("..")

class PyInstaller(Command):
    description = "pyinstaller file generator"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system("python setup.py uninstall")
        os.system("python setup.py install")
        f=open("build/run.py","w")
        f.write("import devicesinlan.devicesinlan_gui\n")
        f.write("devicesinlan.devicesinlan_gui.main()\n")
        f.close()
        os.chdir("build")
        os.system("""pyinstaller run.py -n devicesinlan-{} --onefile --nowindowed --icon ../devicesinlan/images/devicesinlan.ico --distpath ../dist""".format(__version__))

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
            for filename in os.listdir("devicesinlan/ui/"):
                if filename.endswith(".ui"):
                    without_extension=filename[:-3]
                    futures.append(executor.submit(os.system, "pyuic5 devicesinlan/ui/{0}.ui -o devicesinlan/ui/Ui_{0}.py".format(without_extension)))
            futures.append(executor.submit(os.system, "pyrcc5 devicesinlan/images/devicesinlan.qrc -o devicesinlan/images/devicesinlan_rc.py"))
        # Overwriting devicesinlan_rc
        for filename in os.listdir("devicesinlan/ui/"):
             if filename.startswith("Ui_"):
                 os.system("sed -i -e 's/devicesinlan_rc/devicesinlan.images.devicesinlan_rc/' devicesinlan/ui/{}".format(filename))

class Procedure(Command):
    description = "Uninstall installed files with install"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print("""
Nueva versión:
  * Cambiar la versión y la fecha en version.py
  * Modificar el Changelog en README
  * Update ieee-oui with get-oui
  * python setup.py doc
  * linguist
  * python setup.py doc
  * python setup.py install
  * python setup.py doxygen
  * git commit -a -m 'devicesinlan-version'
  * git push
  * Hacer un nuevo tag en GitHub
  * python setup.py sdist upload -r pypi
  * Crea un nuevo ebuild de Gentoo con la nueva versión
  * Subelo al repositorio del portage

  * Change to windows. Enter in an Administrator console.
  * Change to xulpymoney source directory and make git pull
  * python setup.py pyinstaller
  * Add file to github release

""")


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
            os.system("rm /usr/share/pixmaps/devicesinlan.png")
            os.system("rm /usr/share/applications/devicesinlan.desktop")
            os.system("rm /usr/share/man/man1/devicesinlan.1")
            os.system("rm /usr/share/man/es/man1/devicesinlan.1")
        else:
            print(site.getsitepackages())
            for file in os.listdir(site.getsitepackages()[1]):#site packages
                path=site.getsitepackages()[1]+"\\"+ file
                if file.find("devicesinlan")!=-1:
                    shutil.rmtree(path)
                    print(path,  "Erased")
            for file in os.listdir(site.getsitepackages()[0]+"\\Scripts\\"):#Scripts
                path=site.getsitepackages()[0]+"\\scripts\\"+ file
                if file.find("devicesinlan")!=-1:
                    os.remove(path)
                    print(path,  "Erased")



class Doc(Command):
    description = "Update man pages and translations"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


    def change_language(self,language):  
        """language es un string"""
        from PyQt5.QtCore import  QTranslator
        translator=QTranslator(app)
        url= os.getcwd()+"/devicesinlan/i18n/devicesinlan_{}.qm".format(language)
        if os.path.exists(url)==True:
            translator.load(url)
            app.installTranslator(translator)
            print(("Language changed to {} using {}".format(language, url)))
            return
        else:
            print("I couldn't found {}".format(url))
        if language!="en":
            print(QCoreApplication.translate("Core", "Language ({}) couldn't be loaded in {}. Using default (en).".format(language, url)))


    def run(self):
        from PyQt5.QtCore import QCoreApplication
        global app
        app=QCoreApplication(sys.argv)
        app.setOrganizationName("DevicesInLAN")
        app.setOrganizationDomain("devicesinlan.sourceforge.net")
        app.setApplicationName("DevicesInLAN")

        os.system("pylupdate5 -noobsolete -verbose devicesinlan.pro")
        os.system("lrelease -qt5 devicesinlan.pro")
        for language in ["en", "fr", "ro", "ru", "es"]:
            self.mangenerator(language)

    def mangenerator(self, language):
        from mangenerator import Man

        self.change_language(language)
        print("DESCRIPTION in {} is {}".format(language, app.translate("devicesinlan", "DESCRIPTION")))

        if language=="en":
            man=Man("man/man1/devicesinlan")
            mangui=Man("man/man1/devicesinlan_gui")
        else:
            man=Man("man/{}/man1/devicesinlan".format(language))
            mangui=Man("man/{}/man1/devicesinlan_gui".format(language))

        mangui.setMetadata("devicesinlan_gui",  1,   datetime.date.today(), "Mariano Muñoz", app.translate("devicesinlan","Scans all devices in your LAN. Then you can set an alias to your known devices in order to detect future strange devices in your net."))
        mangui.setSynopsis("[--help] [--version] [--debug DEBUG]")
        mangui.header(app.translate("devicesinlan","DESCRIPTION"), 1)
        mangui.paragraph(app.translate("devicesinlan","In the app menu you have the followings features:"), 1)
        mangui.paragraph(app.translate("devicesinlan","Devices > New Scan"), 2, True)
        mangui.paragraph(app.translate("devicesinlan","Searches all devices in tha LAN and show them in a new tab. If some device is not in the known devices list it will be shown with a red background. Devices with a green background are trusted devices"), 3)
        mangui.paragraph(app.translate("devicesinlan","Devices > Show devices database"), 2, True)
        mangui.paragraph(app.translate("devicesinlan","Shows all known devices in a new tab."), 3)
        mangui.paragraph(app.translate("devicesinlan","Right click allows you to edit known devices database."), 3)
        mangui.paragraph(app.translate("devicesinlan","Devices > Load devices list"), 2, True)
        mangui.paragraph(app.translate("devicesinlan","Loads a list of known devices in xml format."), 3)
        mangui.paragraph(app.translate("devicesinlan","Devices > Save devices list"), 2, True)
        mangui.paragraph(app.translate("devicesinlan","Saves the known devices list to a xml file."), 3)
        mangui.paragraph(app.translate("devicesinlan","Devices > Reset database"), 2, True)
        mangui.paragraph(app.translate("devicesinlan","Removes all known devices."), 3)
        mangui.paragraph(app.translate("devicesinlan","This option erases all known devices in database."), 3)
        mangui.paragraph(app.translate("devicesinlan","Configuration > Settings"), 2, True)
        mangui.paragraph(app.translate("devicesinlan","In this dialog you can select your prefered language and you can configure the number of concurrence request."), 3)
        mangui.paragraph(app.translate("devicesinlan","Help > Help"), 2, True)
        mangui.paragraph(app.translate("devicesinlan","Shows this help information."), 3)
        mangui.paragraph(app.translate("devicesinlan","Help > About"), 2, True)
        mangui.paragraph(app.translate("devicesinlan","Shows information about DevicesInLAN license and authors."), 3)
        mangui.paragraph(app.translate("devicesinlan","Help > Check for updates"), 2, True)
        mangui.paragraph(app.translate("devicesinlan","Checks for updates in DevicesInLan repository."), 3)
        mangui.paragraph(app.translate("devicesinlan","Help > Exit"), 2, True)
        mangui.paragraph(app.translate("devicesinlan","Exits from program."), 3)
        mangui.save()
        mangui.saveHTML("devicesinlan/data/devicesinlan_gui.{}.html".format(language))

        man.setMetadata("devicesinlan",  1,   datetime.date.today(), "Mariano Muñoz", app.translate("devicesinlan","Scans all devices in your LAN. Then you can set an alias to your known devices in order to detect future strange devices in your net."))
        man.setSynopsis("[--help] [--version] [--debug DEBUG] [ --interface | --add | --remove | --list | --load | --save | --reset ]")

        man.header(app.translate("devicesinlan","DESCRIPTION"), 1)
        man.paragraph(app.translate("devicesinlan","If you launch deviceslan without parameters a console wizard is launched."), 1)
        man.paragraph(app.translate("devicesinlan","Morever you can use one of this parameters."), 1)
        man.paragraph("--interface", 2, True)
        man.paragraph(app.translate("devicesinlan","Scans the net of the interface parameter and prints a list of the detected devices."), 3)
        man.paragraph(app.translate("devicesinlan","If a device is not known, it will be showed in red. Devices in green are trusted devices."), 3)
        man.paragraph("--add", 2, True)
        man.paragraph(app.translate("devicesinlan","Allows to add a known device from console."), 3)
        man.paragraph("--remove", 2, True)
        man.paragraph(app.translate("devicesinlan","Allows to remove a known device from console."), 3)
        man.paragraph("--list", 2, True)
        man.paragraph(app.translate("devicesinlan","Shows all known devices in database from console."), 3)
        man.paragraph("--load", 2, True)
        man.paragraph(app.translate("devicesinlan","Loads a list of known devices in xml format."), 3)
        man.paragraph("--save", 2, True)
        man.paragraph(app.translate("devicesinlan","Saves the known devices list to a xml file."), 3)
        man.paragraph("--debug", 2, True)
        man.paragraph(app.translate("devicesinlan","Gives debugging information when running DevicesInLAN. It's deactivated by default"), 3)
        man.paragraph(app.translate("devicesinlan","The parameter can take this options: CRITICAL, ERROR, WARNING, INFO, DEBUG."), 3)
        man.paragraph("--reset", 2, True)
        man.paragraph(app.translate("devicesinlan","Removes all known devices."), 3)
        man.save()
        man.saveHTML("devicesinlan/data/devicesinlan.{}.html".format(language))

    ########################################################################

with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

## Version captured from commons to avoid problems with package dependencies
__version__= None
with open('devicesinlan/version.py', encoding='utf-8') as f:
    for line in f.readlines():
        if line.find("__version__ =")!=-1:
            __version__=line.split("'")[1]


if platform.system()=="Linux":
    data_files=[
                 ('/usr/share/man/man1/', ['man/man1/devicesinlan.1']), 
                 ('/usr/share/man/es/man1/', ['man/es/man1/devicesinlan.1'])
               ]
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
    install_requires= [ 'setuptools',
                        'colorama', 
                        'PyQt5;platform_system=="Windows"',
                        'pywin32;platform_system=="Windows"',
                        ], #PyQt5 and PyQtChart doesn't have egg-info in Gentoo, so I remove it to install it with ebuild without making 2 installations. Should be added manually when using pip to install
    data_files=data_files,
    cmdclass={
                        'doxygen': Doxygen,
                        'doc': Doc,
                        'uninstall':Uninstall, 
                        'compile': Compile, 
                        'pyinstaller': PyInstaller,
                        'procedure': Procedure,
                     },
    zip_safe=False,
    include_package_data=True
    )

_=gettext.gettext#To avoid warnings
