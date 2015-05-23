#!/usr/bin/python3
import argparse
import subprocess
import datetime
import gettext
import os
import re
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
        self.known=SetKnownHosts()
        self.load_arpscan()#From arp_scan

        
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



    
class KnownHost:
    def __init__(self):
        self.mac=None
        self.alias=None

    def validate_mac(self, s):
        if len(s)!=17:
            return False

        if re.match(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', s):
            return True
        return False

    def validate_alias(self, s):
        if len(s)>40:
            return False
        if len(s)==0:
            return False
        return True
        
    def insert_mac(self):
        validated=False
        while  validated==False:
            self.mac=input(Color.bold(_("Input the MAC of the known device (xx:xx:xx:xx:xx:xx): ")))
            if self.validate_mac(self.mac):
                validated=True
            else:
                print (Color.red(_("You need to insert a mac with the next format: 2a:3b:4c:5d:6e:7a")))

    def insert_alias(self):
        validated=False
        while validated==False:
            self.alias=input(Color.bold(_("Input an alias of the known device: ")))
            if self.validate_alias(self.alias):
                validated=True
            else:
                print (Color.red(_("You need to add an alias")))

class SetKnownHosts:
    def __init__(self):
        self.arr=[]
        self.load()
        
    
    def remove_mac(self, mac):
        """Returns a boolean if is deleted"""
        todelete=[]
        for k in self.arr:
            if k.mac==mac:
                todelete.append(k)
        
        for k in todelete:
            self.arr.remove(k)
            return True
        
        return False
    
    def load(self):
        f=open("/etc/devicesinlan/known.txt","r")
        for l in f.readlines():
            ar=l.split("=")
            if len(ar)==2:
                try:
                    k=KnownHost()
                    ar=l.split("=")
                    k.mac=ar[0].strip()
                    k.alias=ar[1].strip()
                    self.arr.append(k)
                except:
                    print(_("Error parsing {}").format(l))
        f.close()        
        
    def save(self):
        """Save etc file"""
        f=open("/etc/devicesinlan/known.txt","w")
        for k in self.arr:
            f.write("{} = {}\n".format(k.mac.lower(), k.alias))
        f.close()        
    

##############################################
##Parse arguments
parser=argparse.ArgumentParser(prog='devicesinlan', description=_('Show devices in a LAN'),  epilog=_("Developed by Mariano Muñoz 2015 ©"))
parser.add_argument('-v', '--version', action='version', version="0.3.0")
parser.add_argument('-i',  '--interface', help=_('Net interface name'),  default='eth0')
parser.add_argument('-a',  '--add', help=_('Add a known device'), action='store_true')
parser.add_argument('-r',  '--remove', help=_('Remove a known device'), action='store_true')
args=parser.parse_args()


##Make system checks
if os.path.exists("/usr/bin/arp-scan")==False:
    print(_("I couldn't find /usr/bin/arp-scan.") + " " + _("Please install it."))
    sys.exit(1)

if os.path.exists("/etc/devicesinlan/known.txt")==False:
    subprocess.check_output(["cp","/etc/devicesinlan/known.txt.dist","/etc/devicesinlan/known.txt"])
    print(_("I couldn't find /etc/devicesinlan/known.txt.") + " " + _("I copied distribution file to it.") + " "+ _("Add your mac addresses to detect strage devices in your LAN."))

known=SetKnownHosts()

if args.add:
    k=KnownHost()
    k.insert_mac()
    k.insert_alias()
    known.arr.append(k)
    known.save()    
    print (Color.green(_("Known host inserted")))
    sys.exit(0)
    
if args.remove:
    k=KnownHost()
    k.insert_mac()
    if known.remove_mac(k.mac):
        known.save()
        print (Color.green(_("Mac removed")))
    else:
        print (Color.red(_("I couldn't find the mac")))
    sys.exit(0)

## Load hosts
set=SetHosts()
set.print()

