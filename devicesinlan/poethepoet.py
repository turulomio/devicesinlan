from gettext import translation
from importlib.resources import files
from devicesinlan import __version__
from devicesinlan.reusing.github import download_from_github
from os import system, listdir, chdir
from sys import argv
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count

try:
    t=translation('devicesinlan', files("devicesinlan") / "locale")
    _=t.gettext
except:
    _=str

def compile():
    futures=[]
    with ProcessPoolExecutor(max_workers=cpu_count()+1) as executor:
        for filename in listdir("devicesinlan/ui/"):
            if filename.endswith(".ui"):
                without_extension=filename[:-3]
                futures.append(executor.submit(system, "pyuic6 devicesinlan/ui/{0}.ui -o devicesinlan/ui/Ui_{0}.py".format(without_extension)))
        #futures.append(executor.submit(system, "pyrcc5 devicesinlan/images/devicesinlan.qrc -o devicesinlan/images/devicesinlan_rc.py"))
    # Overwriting devicesinlan_rc
    for filename in listdir("devicesinlan/ui/"):
         if filename.startswith("Ui_"):
             system("sed -i -e 's/devicesinlan_rc/devicesinlan.images.devicesinlan_rc/' devicesinlan/ui/{}".format(filename))
             system("sed -i -e 's/from myqtablewidget/from devicesinlan.reusing.myqtablewidget/' devicesinlan/ui/{}".format(filename))

    
def reusing():
    """
        Actualiza directorio reusing
        poe reusing
        poe reusing --local
    """
    local=False
    if len(argv)==2 and argv[1]=="--local":
        local=True
        print("Update code in local without downloading was selected with --local")
    if local==False:
        download_from_github("turulomio", "reusingcode", "python/github.py", "devicesinlan/reusing")
        download_from_github("turulomio", "reusingcode", "python/libmanagers.py", "devicesinlan/reusing")
        download_from_github("turulomio", "reusingcode", "python/text_inputs.py", "devicesinlan/reusing")

def release():
        print(_("New Release:"))
        print(_("  * Change version and date in __init__.py"))
        print(_("  * Change version and date in pyproject.toml"))
        print(_("  * Edit Changelog in README"))
        print("  * poe translate")
        print("  * mcedit devicesinlan/locale/es.po")
        print("  * poe translate")
        print("  * poetry install")
#        print("  * python setup.py doxygen")
        print("  * git commit -a -m 'devicesinlan-{}'".format(__version__))
        print("  * git push")
        print(_("  * Make a new tag in github"))
        print("  * poetry build")
        print("  * poetry publish --username turulomio --password")
        print(_("  * Create a new gentoo ebuild with the new version"))
        print(_("  * Upload to portage repository")) 
#Nueva versión:
#  * Cambiar la versión y la fecha en version.py
#  * Modificar el Changelog en README
#  * Update ieee-oui with get-oui from arp-scan package
#  * python setup.py doc
#  * linguist
#  * python setup.py doc
#  * python setup.py install
#  * python setup.py doxygen
#  * git commit -a -m 'devicesinlan-{}'
#  * git push
#  * Hacer un nuevo tag en GitHub
#  * python setup.py sdist upload -r pypi
#  * python setup.py uninstall
#  * Crea un nuevo ebuild de Gentoo con la nueva versión
#  * Subelo al repositorio del portage
#
#  * Change to windows. Enter in an Administrator console.
#  * Change to xulpymoney source directory and make git pull
#  * python setup.py pyinstaller
#  * Add file to github release

def translate():
        #es
        system("xgettext -L Python --no-wrap --no-location --from-code='UTF-8' -o devicesinlan/locale/devicesinlan.pot devicesinlan/*.py")
        system("msgmerge -N --no-wrap -U devicesinlan/locale/es.po devicesinlan/locale/devicesinlan.pot")
        system("msgfmt -cv -o devicesinlan/locale/es/LC_MESSAGES/devicesinlan.mo devicesinlan/locale/es.po")
        system("msgfmt -cv -o devicesinlan/locale/fr/LC_MESSAGES/devicesinlan.mo devicesinlan/locale/fr.po")
#        from devicesinlan.libdevicesinlan import MemSetup
#        mem=MemSetup()
#        mem.setQApplication()
#
#        os.system("pylupdate5 -noobsolete -verbose devicesinlan.pro")
#        os.system("lrelease -qt5 devicesinlan.pro")
#        for language in ["en", "fr", "ro", "ru", "es"]:
#            mem.setLanguage(language)
#            mem.mangenerator(language)


def pyinstaller():
        system("python setup.py uninstall")
        system("python setup.py install")
        #gui
        f=open("build/run.py","w")
        f.write("import devicesinlan.devicesinlan\n")
        f.write("devicesinlan.devicesinlan.main_gui()\n")
        f.close()
        chdir("build")
        system("""pyinstaller run.py -n devicesinlan_gui-{} --onefile --windowed  --icon ../devicesinlan/images/devicesinlan.ico --distpath ../dist""".format(__version__))
        chdir("..")


        #Console
        f=open("build/run.py","w")
        f.write("import devicesinlan.devicesinlan\n")
        f.write("devicesinlan.devicesinlan.main_console()\n")
        f.close()
        chdir("build")
        system("""pyinstaller run.py -n devicesinlan-{} --onefile --nowindowed --icon ../devicesinlan/images/devicesinlan.ico --distpath ../dist""".format(__version__))
        chdir("..")

