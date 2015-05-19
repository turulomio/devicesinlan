#!/usr/bin/python3
import argparse
import subprocess
import datetime
import gettext
import os
import sys

# I had a lot of problems with UTF-8. LANG must be es_ES.UTF-8 to work
gettext.textdomain('devicesinlan')
_=gettext.gettext

class Color:
    def green(s):
       return "\033[92m{}\033[0m".format(s)
    
    def red(s):
       return "\033[91m{}\033[0m".format(s)
    
    def bold(s):
       return "\033[1m{}\033[0m".format(s)

class SetHosts:
    def __init__(self):
        """This constructor load /etc/devicesinlan/known.txt and executes arp-scan and parses its result"""
        self.arr=[]
        self.known={} #Dictionary with knows macs and its alias
        self.load_known()#From etc
        self.load_arpscan()#From arp_scan
    
    def load_known(self):
        f=open("/etc/devicesinlan/known.txt","r")
        for l in f.readlines():
            ar=l.split("=")
            if len(ar)==2:
                try:
                    ar=l.split("=")
                    mac=ar[0].strip()
                    alias=ar[1].strip()
                    self.known[mac]=alias
                except:
                    print(_("Error parsing {}").format(l))
        f.close()
        
    def load_arpscan(self):
        """Load Hosts from arpscan output"""
        try:
            output=subprocess.check_output(["arp-scan", "--interface", args.interface, "-l", "--ignoredups"]).decode('UTF-8')
        except:
            print (_("There was an error executing arp-scan.")+" "+_("Is the interface argument correct?."))
            sys.exit(2)
        for line in output.split("\n"):
            if line.find("\t")!=-1:
                h=Host()
                arr=line.split("\t")
                h.ip=arr[0]
                h.mac=arr[1]
                h.hwname=arr[2]
                for k,v in self.known.items():
                    if k.upper()==h.mac.upper():
                        h.alias=v
                self.arr.append(h)
                

    def max_len_hwname(self):
        return  max(len(h.hwname) for h in self.arr)

    def max_len_alias(self):
        l=0
        for h in self.arr:
            if h.alias:
                le=len(h.alias)
                if l<le:
                    l=le
        return l
        
    def print(self):
        maxalias=self.max_len_alias()
        maxhwname=self.max_len_hwname()
        print (Color.bold(_("DEVICES IN LAN FROM {} INTERFACE AT {}").format(args.interface.upper(), str(datetime.datetime.now())[:-7]).center (6+15+17+maxalias+maxhwname)))
        print ()
        print (Color.bold("{}  {}  {}  {}".format(" IP ".center(15,'=')," MAC ".center(17,'='), " ALIAS ".center(maxalias,'='), " HARDWARE ".center(maxhwname,'='))))
        for h in self.arr:
            if h.alias:
                mac=Color.green(h.mac)
                alias=h.alias
            else:
                mac=Color.red(h.mac)
                alias=""
            print ("{}  {}  {}  {}".format(h.ip.ljust(15), mac, Color.bold(alias.ljust(maxalias)), h.hwname.ljust(maxhwname)))        



class Host:
    def __init__(self):
        self.ip=None
        self.mac=None
        self.hwname=None
        self.alias=None


##############################################
##Parse arguments
parser=argparse.ArgumentParser(prog='devicesinlan', description=_('Show devices in a LAN'),  epilog=_("Developed by Mariano Muñoz 2015 ©"))
parser.add_argument('-v', '--version', action='version', version="0.3.0")
parser.add_argument('-i',  '--interface', help='Net interface name',  default='eth0')
args=parser.parse_args()


##Make system checks
if os.path.exists("/usr/bin/arp-scan")==False:
    print(_("I couldn't find /usr/bin/arp-scan.") + " " + _("Please install it."))
    sys.exit(1)

if os.path.exists("/etc/devicesinlan/known.txt")==False:
    subprocess.check_output(["cp","/etc/devicesinlan/known.txt.dist","/etc/devicesinlan/known.txt"])
    print(_("I couldn't find /etc/devicesinlan/known.txt.") + " " + _("I copied distribution file to it.") + " "+ _("Add your mac addresses to detect strage devices in your LAN."))

## Load hosts
set=SetHosts()
set.print()

