from gettext import translation
from importlib.resources import files
from devicesinlan import __version__
from devicesinlan.reusing.github import download_from_github
from os import system, listdir, path, chdir, getcwd
from shutil import which
from sys import argv
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
from tempfile import TemporaryDirectory

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
    print("""New Release:
    * Change version and date in __init__.py"))
    * Change version and date in pyproject.toml"))
    * Edit Changelog in README"))
    * Update ieee-oui with get-oui from arp-scan package
    * poe translate")
    * mcedit devicesinlan/locale/es.po")
    * poe translate")
    * poetry install")
    * git commit -a -m 'devicesinlan-{}'".format(__version__))
    * git push")
    * Make a new tag in github"))
    * poetry pyinstaller
    * Upload wine created files
    * poetry build")
    * poetry publish --username turulomio --password")
    * Create a new gentoo ebuild with the new version"))
    * Upload to portage repository")) 
""")


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
    cwd=getcwd()
    # Check if wine is installed
    if which("wine") is None:
        raise Exception("Wine is not in your system")
    
    # Download python executable
    url_download_exe="https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
    filename=url_download_exe.split("/")[-1]
    print (filename)
    if not path.exists(filename):
        system("wget {filename}")
    
    # Create a new wine, install pythonon and the whole devicesinlan dependencies
    with TemporaryDirectory() as tmpdir:
        wineprefix=f"WINEPREFIX={tmpdir}"
        ## Copies sourcerces
        system(f"rsync -avzP . {tmpdir}")
        
        ## Install windows environment
        system (f"{wineprefix} wine python-3.11.8-amd64.exe /passive AppendPath=1")
        system (f"{wineprefix} wine pip install .")
        system (f"{wineprefix} wine pip install pyinstaller")
        
        chdir(tmpdir)
        #gui
        with open(f"{tmpdir}/run_gui.py","w") as f:
            f.write("import devicesinlan.devicesinlan\n")
            f.write("devicesinlan.devicesinlan.main_gui()\n")
        system(f"""{wineprefix} wine pyinstaller {tmpdir}/run_gui.py -n devicesinlan_gui-{__version__} --onefile --windowed  --icon {tmpdir}/devicesinlan/images/devicesinlan.ico --distpath ./dist/""")
        SystemError
        #console
        with open(f"{tmpdir}/run.py","w") as f:
            f.write("import devicesinlan.devicesinlan\n")
            f.write("devicesinlan.devicesinlan.main_console()\n")
        system(f"""{wineprefix} wine pyinstaller {tmpdir}/run.py -n devicesinlan-{__version__} --nowindowed --onefile  --icon {tmpdir}/devicesinlan/images/devicesinlan.ico --distpath ./dist/""")
        
        system(f"cp {tmpdir}/dist/* {cwd}/dist/")
            
