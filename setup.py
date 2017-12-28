from cx_Freeze import setup, Executable
import sys
sys.path.append('ui')
sys.path.append('images')
from libdevicesinlan import version

print ("Building for", sys.platform, version)
name="devicesinlan"

#Add files
include_files=[ 'images/devicesinlan.ico', 'GPL-3.txt', 'ieee-oui.txt']
include_files.append(("i18n/devicesinlan_es.qm", "i18n/devicesinlan_es.qm"))
include_files.append(("i18n/devicesinlan_fr.qm", "i18n/devicesinlan_fr.qm"))
include_files.append(("i18n/devicesinlan_ro.qm", "i18n/devicesinlan_ro.qm"))
include_files.append(("i18n/devicesinlan_ru.qm", "i18n/devicesinlan_ru.qm"))
include_files.append(("doc/devicesinlan.en.1.html", "devicesinlan.en.1.html"))
include_files.append(("doc/devicesinlan.es.1.html", "devicesinlan.es.1.html"))
include_files.append(("doc/devicesinlan.fr.1.html", "devicesinlan.fr.1.html"))
include_files.append(("doc/devicesinlan.ro.1.html", "devicesinlan.ro.1.html"))
include_files.append(("doc/devicesinlan.ru.1.html", "devicesinlan.ru.1.html"))

#Build options
if sys.platform=='win32':
      base = 'Win32GUI'
      #base="Console"
      shortcut_table = [
          ("DesktopShortcut",        # Shortcut
           "DesktopFolder",          # Directory_
           "DevicesInLan",     # Name
           "TARGETDIR",              # Component_
           "[TARGETDIR]devicesinlan.exe",   # Target
           None,                     # Arguments
           None,                     # Description
           None,                     # Hotkey
           None,                     # Icon
           None,                     # IconIndex
           None,                     # ShowCmd
           'TARGETDIR'               # WkDir
           ),
      ]

      msi_data = {"Shortcut": shortcut_table}  # This will be part of the 'data' option of bdist_msi
      build_msi_options = {
           'upgrade_code': '{3849730B-2375-4F76-B4A5-343277A23BDE}',
           'add_to_path': False,
           'initial_target_dir': r'[ProgramFilesFolder]\%s' % (name),
           'data': msi_data
            }
 
      build_exe_options = dict(includes = [],excludes=[], include_files=include_files)
      options={'bdist_msi': build_msi_options, 'build_exe': build_exe_options}

else:#linux
      base="Console"
      include_files.append("doc/devicesinlan.en.1")
      include_files.append("doc/devicesinlan.es.1")
      include_files.append("doc/devicesinlan.fr.1")
      include_files.append("doc/devicesinlan.ro.1")
      include_files.append("doc/devicesinlan.ru.1")
      build_options = dict(includes = [], excludes = [], include_files=include_files)
      options=dict(build_exe = build_options)

executables = [
      Executable('devicesinlan.py', base=base, icon='images/devicesinlan.ico', shortcutName= name, shortcutDir='ProgramMenuFolder')
]

setup(name=name,
      version = version,
      author = 'Mariano Muñoz',
      author_email="turulomio@yahoo.es", 
      description = 'Search devices in my LAN',
      options = options,
      url="https://sourceforge.net/projects/devicesinlan/", 
      executables = executables)
