from datetime import datetime
from gettext import translation
from importlib.resources import files
from devicesinlan import __version__
from devicesinlan.reusing.github import download_from_github
from devicesinlan.libdevicesinlan import MemSetup
from os import system, listdir, path, chdir, getcwd, makedirs
from shutil import which
from sys import argv
from multiprocessing import cpu_count
from tempfile import TemporaryDirectory
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

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
    print(f"""New Release:
    * Change version and date in __init__.py
    * Change version and date in pyproject.toml
    * poe release
    * git checkout -b devicesinlan-{__version__}
    * Edit Changelog in README
    * Update ieee-oui with get-oui from arp-scan package
    * poe translate
    * mcedit devicesinlan/locale/es.po
    * poe translate
    * poetry install
    * git commit -a -m 'devicesinlan-{__version__}'
    * git push
    * Make a pull request into main branch
    * Make a new tag in github
    * git checkout main
    * git pull
    * poetry pyinstaller
    * Upload wine created files
    * poetry build
    * poetry publish 
    * Create a new gentoo ebuild with the new version
    * Upload to portage repository
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
        common_parameters='--onefile --add-data="devicesinlan/i18n/*.qm:devicesinlan/i18n"  --add-data="devicesinlan/data:devicesinlan/data" --distpath ./dist/'
        commands = [
#            f"""pyinstaller {tmpdir}/run_gui.py -n devicesinlan_gui-{__version__} --windowed --icon {tmpdir}/devicesinlan/images/devicesinlan.ico  {common_parameters} --workpath="linux_ui""", 
#            f"""pyinstaller {tmpdir}/run.py -n devicesinlan-{__version__} --console  {common_parameters}""", 
            f"""{wineprefix} wine pyinstaller {tmpdir}/run_gui.py -n devicesinlan_gui-{__version__} --windowed  --icon {tmpdir}/devicesinlan/images/devicesinlan.ico  {common_parameters}""", 
            f"""{wineprefix} wine pyinstaller {tmpdir}/run.py -n devicesinlan-{__version__} --console  {common_parameters}""", 
        ]

        #Launching concurrent process
        futures=[]
        executor = ProcessPoolExecutor(max_workers=cpu_count())

        # Start each command as a separate process
        for cmd in commands:
            futures.append(executor.submit(system, cmd))

        for f in tqdm(as_completed(futures), total=len(futures)):
            pass

        makedirs(f"{cwd}/dist/", exist_ok=True)
        system(f"cp {tmpdir}/dist/* {cwd}/dist/")
        print(f"All processes have finished in {datetime.now()-start}")
        print("Windows executables doesn't work in wine due to they use Windows commands. Test in a windows system, because they should work")


def statistics_server():
    """
       Publish a statistic server in Sourceforge DevicesInlan Web Project
    """
    system(r"find statistics -type d -exec chmod -c 755 {} \;")
    system(r"find statistics -type f -exec chmod -c 644 {} \;")
    system("rsync -avzP -e 'ssh -l turulomio,devicesinlan' statistics/ web.sourceforge.net:/home/groups/d/de/devicesinlan/htdocs/ --delete-after")

def tests():
    system("pytest devicesinlan/tests.py")
