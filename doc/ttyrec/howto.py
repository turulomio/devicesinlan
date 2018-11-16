#!/usr/bin/python3
import time
import gettext

from ttyrecgenerator import RecSession
# I had a lot of problems with UTF-8. LANG must be es_ES.UTF-8 to work
gettext.install('devicesinlan', '/usr/share/locale')

r=RecSession()
r.comment("# " + _("This is a video to show how to use the 'devicesinlan' command"))
r.command("devicesinlan")
time.sleep(20)
r.comment(" ")
