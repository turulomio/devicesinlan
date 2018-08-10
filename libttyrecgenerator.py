#!/usr/bin/python3
## @package libttyrecgenerator
## @brief Library to generate gifs and video from console output
## 
## This library belongs to too-many-files project and has it's own version number, so you only must edit it in that project

import argparse
import time
import colorama
import datetime
import gettext
import os
import subprocess




#from toomanyfiles import version, version_date



#If you are localizing your module, you must take care not to make global changes, e.g. to the built-in namespace. You should not use the GNU gettext API but instead the class-based API.
#Let’s say your module is called “spam” and the module’s various natural language translation .mo files reside in /usr/share/locale in GNU gettext format. Here’s what you would put at the top of your module:

t = gettext.translation('toomanyfiles', '/usr/share/locale')
_ = t.gettext


version="20180810"

def version_date():
    versio=version.replace("+","")
    return datetime.date(int(versio[:-4]),  int(versio[4:-2]),  int(versio[6:]))

class RecSession:
    def __init__(self):
        self.__hostname="MyLinux"
        self.__cwd="/home/ttyrec/"
        
    def path(self):
        return "{} {}".format(colorama.Fore.RED + "sg" + colorama.Style.RESET_ALL, colorama.Fore.BLUE + "/ttyrec/ # " + colorama.Style.RESET_ALL)

    ## # must be added to s
    def comment(self, s, sleep=4):
        print(self.path()+ colorama.Fore.YELLOW + s + colorama.Style.RESET_ALL)
        time.sleep(sleep)

    def command(self, s, sleep=6):
        print()
        print(self.path() + colorama.Fore.GREEN + s + colorama.Style.RESET_ALL)
        print(subprocess.check_output(s,shell=True).decode('utf-8'))
        time.sleep(sleep)

    def chdir(self, dir, sleep=6):
        print()
        print(self.path() + colorama.Fore.GREEN + "cd " + dir + colorama.Style.RESET_ALL)
        os.chdir(dir)
        print()
        time.sleep(sleep)


    def command_pipe(self, c1,c2, sleep=6):
        cmd = "{}|{}".format(c1,c2)
        print()
        print(self.path() + colorama.Fore.GREEN + cmd + colorama.Style.RESET_ALL)
        ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = ps.communicate()[0]
        print (output.decode('utf-8'))
        time.sleep(6)


    def change_language(self, language):
        if language=="en":
            gettext.install('toomanyfiles', 'badlocale')
        else:
            lang1=gettext.translation('toomanyfiles', '/usr/share/locale', languages=[language])
            lang1.install()
