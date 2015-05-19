#!/usr/bin/python3
import subprocess
import datetime
import gettext

# I had a lot of problems with UTF-8. LANG must be es_ES.UTF-8 to work
gettext.textdomain('devicesinlan')
_=gettext.gettext



def green(s):
   return "\033[92m{}\033[0m".format(s)

def red(s):
   return "\033[91m{}\033[0m".format(s)


def bold(s):
   return "\033[1m{}\033[0m".format(s)

class SetHosts:
    def __init__(self):
        self.arr=[]

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



class Host:
    def __init__(self):
        self.ip=None
        self.mac=None
        self.hwname=None
        self.alias=None

    def load(self,line,arps):
        arr=line.split("\t")
        self.ip=arr[0]
        self.mac=arr[1]
        self.hwname=arr[2]
        for k,v in arps.items():
            if k==self.mac:
                self.alias=v
        return self

output=subprocess.check_output(["arp-scan", "--interface", "eth0", "-l", "--ignoredups"]).decode('UTF-8')



#Loading arps
arps={}
f=open("/etc/devicesinlan/known.txt","r")
for l in f.readlines():
    arr=l.split("=")
    if len(arr)==2:
        try:
            arr=l.split("=")
            mac=arr[0].strip()
            alias=arr[1].strip()
            arps[mac]=alias
        except:
            print(_("Error parsing {}").format(l))
f.close()

set=SetHosts()


for line in output.split("\n"):
    if line.find("\t")!=-1:
        set.arr.append(Host().load(line,arps))
#    for k,v in arps.items():
#        line=line.replace(k,"{}\t[{}]".format(green(k),bold(v)))

maxalias=set.max_len_alias()
maxhwname=set.max_len_hwname()
print (bold(_("DEVICES IN MY LAN AT {}").format(str(datetime.datetime.now())[:-7]).center (6+15+17+maxalias+maxhwname)))
print ()
print (bold("{}  {}  {}  {}".format(" IP ".center(15,'=')," MAC ".center(17,'='), " ALIAS ".center(maxalias,'='), " HARDWARE ".center(maxhwname,'='))))
for h in set.arr:
    if h.alias:
        mac=green(h.mac)
        alias=h.alias
    else:
        mac=red(h.mac)
        alias=""
    print ("{}  {}  {}  {}".format(h.ip.ljust(15), mac, bold(alias.ljust(maxalias)), h.hwname.ljust(maxhwname)))
