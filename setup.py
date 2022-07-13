from setuptools import setup, Command
import gettext
import os
import platform
import shutil
import site
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
        os.system("rsync -avzP -e 'ssh -l turulomio' html/ frs.sourceforge.net:/home/users/t/tu/turulomio/userweb/htdocs/doxygen/devicesinlan/ --delete-after")
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
        #gui
        f=open("build/run.py","w")
        f.write("import devicesinlan.devicesinlan\n")
        f.write("devicesinlan.devicesinlan.main_gui()\n")
        f.close()
        os.chdir("build")
        os.system("""pyinstaller run.py -n devicesinlan_gui-{} --onefile --windowed  --icon ../devicesinlan/images/devicesinlan.ico --distpath ../dist""".format(__version__))
        os.chdir("..")


        #Console
        f=open("build/run.py","w")
        f.write("import devicesinlan.devicesinlan\n")
        f.write("devicesinlan.devicesinlan.main_console()\n")
        f.close()
        os.chdir("build")
        os.system("""pyinstaller run.py -n devicesinlan-{} --onefile --nowindowed --icon ../devicesinlan/images/devicesinlan.ico --distpath ../dist""".format(__version__))
        os.chdir("..")


class Reusing(Command):
    description = "Update code from https://github.com/turulomio/reusingcode"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from sys import path
        path.append("devicesinlan/reusing")
        from github import download_from_github
        from file_functions import replace_in_file

        download_from_github('turulomio','reusingcode','PyQt5/myqtablewidget.py', 'devicesinlan/reusing')
        download_from_github('turulomio','reusingcode','python/call_by_name.py', 'devicesinlan/reusing')
        download_from_github('turulomio','reusingcode','python/casts.py', 'devicesinlan/reusing')
        download_from_github('turulomio','reusingcode','python/decorators.py', 'devicesinlan/reusing')
        download_from_github('turulomio','reusingcode','python/file_functions.py', 'devicesinlan/reusing')
        download_from_github('turulomio','reusingcode','python/github.py', 'devicesinlan/reusing')
        download_from_github('turulomio','reusingcode','python/libmanagers.py', 'devicesinlan/reusing')
        download_from_github('turulomio','reusingcode','python/datetime_functions.py', 'devicesinlan/reusing')
        download_from_github('turulomio','reusingcode','python/text_inputs.py', 'devicesinlan/reusing')
        download_from_github('turulomio','reusingcode','python/package_resources.py', 'devicesinlan/reusing')
        
        replace_in_file("devicesinlan/reusing/libmanagers.py",  "from datetime_functions",  "from .datetime_functions")
        replace_in_file("devicesinlan/reusing/libmanagers.py",  "from call_by_name",  "from .call_by_name")
        replace_in_file("devicesinlan/reusing/myqtablewidget.py",  "from .. ",  "from .")

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
                 os.system("sed -i -e 's/from myqtablewidget/from devicesinlan.reusing.myqtablewidget/' devicesinlan/ui/{}".format(filename))


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
  * Update ieee-oui with get-oui from arp-scan package
  * python setup.py doc
  * linguist
  * python setup.py doc
  * python setup.py install
  * python setup.py doxygen
  * git commit -a -m 'devicesinlan-{}'
  * git push
  * Hacer un nuevo tag en GitHub
  * python setup.py sdist upload -r pypi
  * python setup.py uninstall
  * Crea un nuevo ebuild de Gentoo con la nueva versión
  * Subelo al repositorio del portage

  * Change to windows. Enter in an Administrator console.
  * Change to xulpymoney source directory and make git pull
  * python setup.py pyinstaller
  * Add file to github release
""".format(__version__))


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
            os.system("rm /usr/bin/devicesinlan*")
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

    def run(self):
        from devicesinlan.libdevicesinlan import MemSetup
        mem=MemSetup()
        mem.setQApplication()

        os.system("pylupdate5 -noobsolete -verbose devicesinlan.pro")
        os.system("lrelease -qt5 devicesinlan.pro")
        for language in ["en", "fr", "ro", "ru", "es"]:
            mem.setLanguage(language)
            mem.mangenerator(language)

    ########################################################################
#__version__
__version__= None
with open('devicesinlan/version.py', encoding='utf-8') as f:
    for line in f.readlines():
        if line.find("__version__ =")!=-1:
            __version__=line.split("'")[1]

#data_files
if platform.system()=="Linux":
    data_files=[
                 ('/usr/share/man/man1/', ['man/man1/devicesinlan.1']),
                 ('/usr/share/man/es/man1/', ['man/es/man1/devicesinlan.1']),
                 ('/usr/share/pixmaps/', ['devicesinlan/images/devicesinlan.png']),
                 ('/usr/share/applications/', ['devicesinlan.desktop']),
               ]
else:
    data_files=[]
#entry_points
entry_points={
    'gui_scripts': [   
        'devicesinlan_gui=devicesinlan.devicesinlan:main_gui',
    ],
    'console_scripts': [    
        'devicesinlan=devicesinlan.devicesinlan:main_console',
    ],
}
if platform.system()=="Windows":
    entry_points["console_scripts"].append('devicesinlan_shortcuts=devicesinlan.shortcuts:create')

setup(name='devicesinlan',
    version=__version__,
    description='Find devices in a lan',
    long_description='Project web page is at https://github.com/turulomio/devicesinlan/',
    long_description_content_type='text/markdown',
    classifiers=['Development Status :: 5 - Production/Stable',
              'Intended Audience :: End Users/Desktop',
              'Topic :: System :: Networking :: Monitoring',
              'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
              'Programming Language :: Python :: 3',
             ], 
    keywords='network monitoring',
    url='https://github.com/turulomio/devicesinlan',
    author='turulomio',
    author_email='turulomio@yahoo.es',
    license='GPL-3',
    packages=['devicesinlan'],
    entry_points = entry_points,
    install_requires= [ 'setuptools',
                        'colorama', 
                        'scapy', 
                        'PyQt5',
                        'pywin32;platform_system=="Windows"',
                        'pytz', 
                        ], #PyQt5 and PyQtChart doesn't have egg-info in Gentoo, so I remove it to install it with ebuild without making 2 installations. Should be added manually when using pip to install
    data_files=data_files,
    cmdclass={
                        'doxygen': Doxygen,
                        'doc': Doc,
                        'uninstall':Uninstall, 
                        'compile': Compile, 
                        'pyinstaller': PyInstaller,
                        'procedure': Procedure,
                        'reusing': Reusing,
                     },
    zip_safe=False,
    include_package_data=True, 
    )

_=gettext.gettext#To avoid warnings
