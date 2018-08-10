#!/usr/bin/python3
import argparse
import time
import colorama
import os
import subprocess
import gettext
import sys
sys.path.append("/usr/lib/toomanyfiles")

from libttyrecgenerator import RecSession
# I had a lot of problems with UTF-8. LANG must be es_ES.UTF-8 to work
gettext.install('devicesinlan', '/usr/share/locale')

parser=argparse.ArgumentParser(description='HOWTO to save with ttyrec', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('--language', help=_("Sets output language"), action="store",default='en')
args=parser.parse_args()

r=RecSession()
r.change_language(args.language)
r.comment("# " + _("This is a video to show how to use the 'devicesinlan' command"))
r.command("devicesinlan")
time.sleep(20)
sys.exit(0)