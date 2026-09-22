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
from concurrent.futures import ProcessPoolExecutor

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
    * poe compile
    * Update ieee-oui with get-oui from arp-scan package
    * poe translate
    * mcedit devicesinlan/locale/es.po
    * poe translate
    * poe tests
    * poe dist_windows
    * poe dist_linux
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
    Updates and compiles Qt6 translations, and generates manual pages
    """
    mem=MemSetup()
    mem.setQApplication()

    pylupdate_cmd = which("pylupdate6") or "pylupdate6"
    for ts_file in [
        "devicesinlan/i18n/devicesinlan_es.ts",
        "devicesinlan/i18n/devicesinlan_fr.ts",
        "devicesinlan/i18n/devicesinlan_ro.ts",
        "devicesinlan/i18n/devicesinlan_ru.ts",
    ]:
        system(f"{pylupdate_cmd} --no-obsolete --ts {ts_file} devicesinlan")

    lrelease_cmd = which("lrelease") or which("lrelease-qt6") or which("lrelease6") or "/usr/lib64/qt6/bin/lrelease"
    system(f"{lrelease_cmd} devicesinlan.pro")
    for language in ["en", "fr", "ro", "ru", "es"]:
        mem.setLanguage(language)
        mem.mangenerator(language)


def dist_linux():
    """
    Builds standalone Linux executables for CLI and GUI using Nuitka.
    Output: dist/devicesinlan-<version>-linux-<bits> and dist/devicesinlan_gui-<version>-linux-<bits>
    """
    start = datetime.now()
    cwd = getcwd()
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
            
        gui_flags = (
            "--onefile "
            "--standalone "
            "--assume-yes-for-downloads "
            "--enable-plugin=pyqt6 "
            "--include-data-dir=devicesinlan/data=devicesinlan/data "
            "--include-data-dir=devicesinlan/i18n=devicesinlan/i18n "
        )
        
        cli_flags = (
            "--onefile "
            "--standalone "
            "--assume-yes-for-downloads "
            "--include-data-dir=devicesinlan/data=devicesinlan/data "
            "--nofollow-import-to=PyQt6 "
            "--nofollow-import-to=devicesinlan.libdevicesinlan_gui "
            "--nofollow-import-to=devicesinlan.ui "
        )
        
        cmd_gui = (
            f"python -m nuitka {gui_flags} "
            f"--output-filename=devicesinlan_gui-{__version__}-linux-{bits} "
            f"--output-dir={tmpdir}/dist_linux {gui_launcher}"
        )
        
        cmd_cli = (
            f"python -m nuitka {cli_flags} "
            f"--output-filename=devicesinlan-{__version__}-linux-{bits} "
            f"--output-dir={tmpdir}/dist_linux {cli_launcher}"
        )
        
        print(f"Building Linux GUI binary ({bits}) with Nuitka...")
        system(cmd_gui)
        print(f"Building Linux Console binary ({bits}) with Nuitka (Zero Qt/GUI dependencies)...")
        system(cmd_cli)
        
        system(f"cp -f {tmpdir}/dist_linux/* {cwd}/dist/")
        
    print(f"Linux binaries generated in ./dist/ in {datetime.now() - start}")


def dist_windows():
    """
    Builds standalone Windows executables (.exe with PE32+ format) for CLI and GUI using Nuitka in Wine.
    Output: dist/devicesinlan-<version>-windows-64bits.exe and dist/devicesinlan_gui-<version>-windows-64bits.exe
    """
    start = datetime.now()
    cwd = getcwd()
    makedirs("dist", exist_ok=True)

    if which("wine") is None:
        raise Exception("Wine is not installed in your system. Please install Wine.")

    url_download_exe = "https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe"
    url_download_exe_filename = path.join(cwd, path.basename(url_download_exe))
    if not path.exists(url_download_exe_filename):
        print(f"Downloading {url_download_exe}...")
        system(f"wget -q --show-progress {url_download_exe} -O {url_download_exe_filename}")

    with TemporaryDirectory() as tmpdir:
        wineprefix = f"WINEPREFIX={tmpdir}/wineprefix WINEDEBUG=-all"
        wine_python = f"{wineprefix} wine C:\\\\Python312\\\\python.exe"

        # Copies sources to tmpdir
        system(f"rsync -aq --exclude='.git' --exclude='dist' --exclude='.pytest_cache' . {tmpdir}/src")
        chdir(f"{tmpdir}/src")

        # Generate launcher files
        launcher_header = "import time\nif not hasattr(time, 'tzset'):\n    time.tzset = lambda: None\n"
        with open(f"{tmpdir}/src/run_gui.py", "w") as f:
            f.write(launcher_header + "from devicesinlan.devicesinlan import main_gui\nmain_gui()\n")
        with open(f"{tmpdir}/src/run_cli.py", "w") as f:
            f.write(launcher_header + "from devicesinlan.devicesinlan import main_console\nmain_console()\n")

        print("Setting up Wine Windows Python environment (Python 3.12)...")
        system(f"{wineprefix} wine {url_download_exe_filename} /passive AppendPath=1 TargetDir=C:\\\\Python312")
        system(f"{wine_python} -m pip install --upgrade pip")
        system(f"{wine_python} -m pip install . nuitka zstandard pefile")

        gui_flags = (
            "--onefile --standalone --assume-yes-for-downloads --enable-plugin=pyqt6 "
            "--mingw64 "
            "--experimental=force-dependencies-pefile "
            "--include-qt-plugins=platforms,styles,imageformats "
            "--windows-icon-from-ico=devicesinlan/images/devicesinlan.ico "
            "--windows-console-mode=disable "
            "--include-data-dir=devicesinlan/data=devicesinlan/data "
            "--include-data-dir=devicesinlan/i18n=devicesinlan/i18n "
        )
        cli_flags = (
            "--onefile --standalone --assume-yes-for-downloads "
            "--mingw64 "
            "--experimental=force-dependencies-pefile "
            "--windows-console-mode=force "
            "--include-data-dir=devicesinlan/data=devicesinlan/data "
            "--nofollow-import-to=PyQt6 "
            "--nofollow-import-to=devicesinlan.libdevicesinlan_gui "
            "--nofollow-import-to=devicesinlan.ui "
        )

        cmd_gui = f"{wine_python} -m nuitka {gui_flags} --output-filename=devicesinlan_gui-{__version__}-windows-64bits.exe --output-dir=dist_win run_gui.py"
        cmd_cli = f"{wine_python} -m nuitka {cli_flags} --output-filename=devicesinlan-{__version__}-windows-64bits.exe --output-dir=dist_win run_cli.py"

        print("Building Windows GUI PE binary with Nuitka in Wine...")
        system(cmd_gui)
        print("Building Windows Console PE binary with Nuitka in Wine (Zero Qt/GUI dependencies)...")
        system(cmd_cli)

        chdir(cwd)
        makedirs(f"{cwd}/dist", exist_ok=True)
        system(f"cp -f {tmpdir}/src/dist_win/*.exe {cwd}/dist/")

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
