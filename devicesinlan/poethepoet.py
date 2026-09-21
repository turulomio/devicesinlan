from datetime import datetime
from gettext import translation
from importlib.resources import files
from devicesinlan import __version__
from devicesinlan.reusing.github import download_from_github
from devicesinlan.libdevicesinlan import MemSetup
from os import system, listdir, path, chdir, getcwd, makedirs
from shutil import which
from sys import argv
from struct import calcsize
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
    * Create an issue with next version 
    * Create a branch for that issue and paste recommended code to console
    * Change version and date in __init__.py
    * Change version and date in pyproject.toml
    * poe release
    * Update ieee-oui with get-oui from arp-scan package
    * poe translate
    * mcedit devicesinlan/locale/es.po
    * poe translate
    * git commit -a -m 'devicesinlan-{__version__}'
    * git push
    * Make a pull request into main branch
    * Make a new tag in github
    * git checkout main
    * git pull
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


def dist_linux():
    """
    Builds standalone Linux executables for CLI and GUI using Nuitka.
    Output: dist/devicesinlan-<version>-linux-<bits> and dist/devicesinlan_gui-<version>-linux-<bits>
    """
    start = datetime.now()
    makedirs("dist", exist_ok=True)
    bits = f"{calcsize('P') * 8}bits"
    
    with TemporaryDirectory() as tmpdir:
        # Generate launcher files
        gui_launcher = path.join(tmpdir, "run_gui.py")
        cli_launcher = path.join(tmpdir, "run_cli.py")
        
        with open(gui_launcher, "w") as f:
            f.write("from devicesinlan.devicesinlan import main_gui\n")
            f.write("main_gui()\n")
            
        with open(cli_launcher, "w") as f:
            f.write("from devicesinlan.devicesinlan import main_console\n")
            f.write("main_console()\n")
            
        common_flags = (
            "--onefile "
            "--standalone "
            "--assume-yes-for-downloads "
            "--include-data-dir=devicesinlan/data=devicesinlan/data "
            "--include-data-dir=devicesinlan/i18n=devicesinlan/i18n "
        )
        
        cli_exclusions = (
            "--nofollow-import-to=devicesinlan.libdevicesinlan_gui "
            "--nofollow-import-to=devicesinlan.ui "
            "--nofollow-import-to=PyQt6.QtWidgets "
            "--nofollow-import-to=PyQt6.QtGui "
            "--nofollow-import-to=PyQt6.QtSvg "
            "--nofollow-import-to=PyQt6.QtOpenGL "
            "--nofollow-import-to=PyQt6.QtPrintSupport "
            "--nofollow-import-to=PyQt6.QtSql "
            "--nofollow-import-to=PyQt6.QtTest "
            "--nofollow-import-to=PyQt6.QtXml "
            "--nofollow-import-to=PyQt6.QtDBus "
        )
        
        cmd_gui = (
            f"python -m nuitka {common_flags} --enable-plugin=pyqt6 "
            f"--linux-icon=devicesinlan/images/devicesinlan.png "
            f"--output-filename=devicesinlan_gui-{__version__}-linux-{bits} "
            f"--output-dir=dist {gui_launcher}"
        )
        
        cmd_cli = (
            f"python -m nuitka {common_flags} --enable-plugin=pyqt6 {cli_exclusions} "
            f"--output-filename=devicesinlan-{__version__}-linux-{bits} "
            f"--output-dir=dist {cli_launcher}"
        )
        
        print(f"Building Linux GUI binary ({bits}) with Nuitka...")
        system(cmd_gui)
        print(f"Building Linux Console binary ({bits}) with Nuitka (GUI excluded)...")
        system(cmd_cli)
        
    print(f"Linux binaries generated in ./dist/ in {datetime.now() - start}")


def dist_windows():
    """
    Builds standalone Windows executables (.exe) for CLI and GUI using Nuitka.
    Run on a Windows host/runner or CI.
    Output: dist/devicesinlan-<version>-windows-<bits>.exe and dist/devicesinlan_gui-<version>-windows-<bits>.exe
    """
    start = datetime.now()
    makedirs("dist", exist_ok=True)
    bits = f"{calcsize('P') * 8}bits"
    
    with TemporaryDirectory() as tmpdir:
        # Generate launcher files
        gui_launcher = path.join(tmpdir, "run_gui.py")
        cli_launcher = path.join(tmpdir, "run_cli.py")
        
        with open(gui_launcher, "w") as f:
            f.write("from devicesinlan.devicesinlan import main_gui\n")
            f.write("main_gui()\n")
            
        with open(cli_launcher, "w") as f:
            f.write("from devicesinlan.devicesinlan import main_console\n")
            f.write("main_console()\n")
            
        common_flags = (
            "--onefile "
            "--standalone "
            "--assume-yes-for-downloads "
            "--include-data-dir=devicesinlan/data=devicesinlan/data "
            "--include-data-dir=devicesinlan/i18n=devicesinlan/i18n "
        )
        
        cli_exclusions = (
            "--nofollow-import-to=devicesinlan.libdevicesinlan_gui "
            "--nofollow-import-to=devicesinlan.ui "
            "--nofollow-import-to=PyQt6.QtWidgets "
            "--nofollow-import-to=PyQt6.QtGui "
            "--nofollow-import-to=PyQt6.QtSvg "
            "--nofollow-import-to=PyQt6.QtOpenGL "
            "--nofollow-import-to=PyQt6.QtPrintSupport "
            "--nofollow-import-to=PyQt6.QtSql "
            "--nofollow-import-to=PyQt6.QtTest "
            "--nofollow-import-to=PyQt6.QtXml "
            "--nofollow-import-to=PyQt6.QtDBus "
        )
        
        cmd_gui = (
            f"python -m nuitka {common_flags} --enable-plugin=pyqt6 "
            f"--windows-icon-from-ico=devicesinlan/images/devicesinlan.ico "
            f"--windows-console-mode=disable "
            f"--output-filename=devicesinlan_gui-{__version__}-windows-{bits}.exe "
            f"--output-dir=dist {gui_launcher}"
        )
        
        cmd_cli = (
            f"python -m nuitka {common_flags} --enable-plugin=pyqt6 {cli_exclusions} "
            f"--windows-console-mode=force "
            f"--output-filename=devicesinlan-{__version__}-windows-{bits}.exe "
            f"--output-dir=dist {cli_launcher}"
        )
        
        print(f"Building Windows GUI binary ({bits}) with Nuitka...")
        system(cmd_gui)
        print(f"Building Windows Console binary ({bits}) with Nuitka (GUI excluded)...")
        system(cmd_cli)
        
    print(f"Windows binaries generated in ./dist/ in {datetime.now() - start}")


def statistics_server():
    """
       Publish a statistic server in Sourceforge DevicesInlan Web Project
    """
    system(r"find statistics -type d -exec chmod -c 755 {} \;")
    system(r"find statistics -type f -exec chmod -c 644 {} \;")
    system("rsync -avzP -e 'ssh -l turulomio,devicesinlan' statistics/ web.sourceforge.net:/home/groups/d/de/devicesinlan/htdocs/ --delete-after")

def tests():
    system("pytest devicesinlan/tests.py")
