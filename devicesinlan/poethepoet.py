from datetime import datetime
from gettext import translation
from importlib.resources import files
from devicesinlan import __version__
from devicesinlan.reusing.github import download_from_github
from devicesinlan.libdevicesinlan import MemSetup
from os import system, listdir, path, chdir, getcwd, makedirs
from shutil import which
from sys import argv
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
from subprocess import Popen
from tempfile import TemporaryDirectory
from tqdm import tqdm

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
        futures.append(executor.submit(system, "/usr/lib64/qt6/libexec/rcc -g python devicesinlan/images/devicesinlan.qrc | sed '0,/PySide6/s//PyQt6/' > devicesinlan/images/devicesinlan_rc.py"))
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
    """
        I couldn't do it with qt6
    """
    mem=MemSetup()
    mem.setQApplication()

    system("pylupdate5 -noobsolete -verbose devicesinlan.pro")
    system("/usr/lib64/qt5/bin/lrelease devicesinlan.pro")
    for language in ["en", "fr", "ro", "ru", "es"]:
        mem.setLanguage(language)
        mem.mangenerator(language)


def pyinstaller():
    start=datetime.now()
    cwd=getcwd()
    
    # Download python windows executable
    url_download_exe="https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    url_download_exe_filename=path.basename(url_download_exe)
    if not path.exists(url_download_exe_filename):
        system(f"wget {url_download_exe}")

    # Create a new wine, install pythonon and the whole devicesinlan dependencies
    with TemporaryDirectory() as tmpdir:
        ## Generate launchers
        with open(f"{tmpdir}/run_gui.py","w") as f:
            f.write("import devicesinlan.devicesinlan\n")
            f.write("devicesinlan.devicesinlan.main_gui()\n")
        with open(f"{tmpdir}/run.py","w") as f:
            f.write("import devicesinlan.devicesinlan\n")
            f.write("devicesinlan.devicesinlan.main_console()\n")
        
        ## Copies sources to tmpdir
        system(f"rsync -avzP . {tmpdir}")
        chdir(tmpdir)
        
        
        ## Check if wine is installed
        if which("wine") is None:
            raise Exception("Wine is not in your system")
    

            
        ## Install windows environment
        wineprefix=f"WINEPREFIX={tmpdir}"
        system (f"{wineprefix} wine {url_download_exe_filename} /passive AppendPath=1")
        system (f"{wineprefix} wine pip install .")
        system (f"{wineprefix} wine pip install pyinstaller")



        # List of commands you want to run in the background. IF SOMETHING GOES WRONG USE SYSTEM WITH THAT PROCESS
        commands = [
            f"""pyinstaller {tmpdir}/run_gui.py -n devicesinlan_gui-{__version__} --onefile --add-data="devicesinlan/i18n/*.qm:devicesinlan/i18n"  --add-data="devicesinlan/data:devicesinlan/data"  --windowed --distpath ./dist/""", 
            f"""pyinstaller {tmpdir}/run.py -n devicesinlan-{__version__} --onefile --nowindowed --add-data="devicesinlan/i18n/*.qm:devicesinlan/i18n"  --add-data="devicesinlan/data:devicesinlan/data" --distpath ./dist/""", 
            f"""{wineprefix} wine pyinstaller {tmpdir}/run_gui.py -n devicesinlan_gui-{__version__} --onefile --add-data="devicesinlan/i18n/*.qm:devicesinlan/i18n"  --add-data="devicesinlan/data:devicesinlan/data"   --windowed  --icon {tmpdir}/devicesinlan/images/devicesinlan.ico --distpath ./dist/""", 
            f"""{wineprefix} wine pyinstaller {tmpdir}/run.py -n devicesinlan-{__version__} --nowindowed --add-data="devicesinlan/i18n/*.qm:devicesinlan/i18n"  --add-data="devicesinlan/data:devicesinlan/data"   --onefile  --icon {tmpdir}/devicesinlan/images/devicesinlan.ico --distpath ./dist/""", 
        ]

        # List to keep track of process objects
        processes = []

        # Start each command as a separate process
        for cmd in commands:
            process = Popen(cmd, shell=True)
            processes.append(process)

        # Wait for all processes to complete
        for process in tqdm(processes):
            process.wait()

        makedirs(f"{cwd}/dist/", exist_ok=True)
        system(f"cp {tmpdir}/dist/* {cwd}/dist/")
        print(f"All processes have finished in {datetime.now()-start}")
