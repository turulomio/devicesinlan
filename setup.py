from cx_Freeze import setup, Executable
import sys,os, shutil
sys.path.append('ui')
sys.path.append('images')

def winversion():
    return "0.1"
#    versio=version.replace("+","")
#    return versio[:-4]+"."+versio[4:-2]+"."+versio[6:]

print ("Building for", sys.platform,  winversion())
name="devicesinlan"


#Add files
include_files=[ 'devicesinlan.ico', 'GPL-3.txt']
#for f in os.listdir('i18n/'):#adding qm
#      if f[len(f)-3:]==".qm":
#            include_files.append('i18n/'+f)
#            print (f)


#Build options
if sys.platform=='win32':
      base = 'Win32GUI'
      version=winversion()
      build_msi_options = {
           'upgrade_code': '{3849730B-2375-4F76-B4A5-343277A23B9B}',
           'add_to_path': False,
           'initial_target_dir': r'[ProgramFilesFolder]\%s' % (name),
            }
 
      build_exe_options = dict(includes = [],excludes=[], include_files=include_files)

      options={'bdist_msi': build_msi_options,
               'build_exe': build_exe_options}
else:#linux
      base="Console"
      build_options = dict(includes = [], excludes = [], include_files=include_files)
      options=dict(build_exe = build_options)

executables = [
      Executable('devicesinlan.py', base=base, icon='devicesinlan.ico', shortcutName= name, shortcutDir='ProgramMenuFolder')
]

setup(name=name,
      version = winversion(),
      author = 'Mariano Muñoz',
      description = 'Search devices in my LAN',
      options = options,
      executables = executables)

#After build
if sys.platform=='linux':
      builddir='build/exe.linux-x86-3.4'
