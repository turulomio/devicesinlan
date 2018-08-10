#!/usr/bin/python3
## @package ttyrecgenerator
## @brief Program that generate gifs and video from console output
## 
## This command belongs to too-many-files project and has it's own version number, so you only must edit it in that project. It needs libttyrecgenerator.py module

import argparse
import time
import colorama
import datetime
import gettext
import os
import subprocess
#from toomanyfiles import version, version_date


version="20180727"

def version_date():
    versio=version.replace("+","")
    return datetime.date(int(versio[:-4]),  int(versio[4:-2]),  int(versio[6:]))




# I had a lot of problems with UTF-8. LANG must be es_ES.UTF-8 to work. Nuevo sistema2
gettext.install('toomanyfiles')


if __name__ == "__main__":
    parser=argparse.ArgumentParser(prog='ttyrecgenerator', description=_('Create an animated gif/video from the output of the program passed as parameter'), epilog=_("Developed by Mariano Muñoz 2018-{}".format(version_date().year)), formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version=version)
    parser.add_argument('program',  help=_("Path to program"))
    parser.add_argument('--output', help=_("Ttyrec output path"), action="store", default="ttyrecord.rec")
    parser.add_argument('--video', help=_("Makes a simulation and doesn't remove files"), action="store_true", default=False)
    args=parser.parse_args()

    subprocess.run(["xterm", "-hold", "-bg", "black", "-geometry", "140x400", "-fa", "monaco", "-fs", "18", "-fg", "white", "-e", "ttyrec -e '{0}' {1}; ttygif {1}".format(args.program, args.output)])
    os.system("mv tty.gif {}.gif".format(args.output))
    if args.video==True:
        subprocess.run(["ffmpeg", "-i", "{}.gif".format(args.output), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "{}.mp4".format(args.output)])

