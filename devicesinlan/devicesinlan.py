## @namespace devicesinlan.devicesinlan
## @brief Package main functions

from signal import signal,  SIGINT
from sys import exit
from devicesinlan import __version__, __versiondate__, epilog
from devicesinlan.reusing.text_inputs import press_key_to_continue
from platform import system as platform_system
from logging import basicConfig, DEBUG, INFO, WARNING, ERROR,  CRITICAL, critical
from argparse import ArgumentParser, RawTextHelpFormatter
_=str

## Sets logging level for the app
def setLoggingLevel(level):        
    #Por defecto se pone WARNING y mostrar´ia ERROR y CRITICAL
    logFormat = "%(asctime)s %(levelname)s %(module)s:%(lineno)d at %(funcName)s. %(message)s"
    dateFormat='%Y%m%d %I%M%S'

    if level=="DEBUG":#Show detailed information that can help with program diagnosis and troubleshooting. CODE MARKS
        basicConfig(level=DEBUG, format=logFormat, datefmt=dateFormat)
    elif level=="INFO":#Everything is running as expected without any problem. TIME BENCHMARCKS
        basicConfig(level=INFO, format=logFormat, datefmt=dateFormat)
    elif level=="WARNING":#The program continues running, but something unexpected happened, which may lead to some problem down the road. THINGS TO DO
        basicConfig(level=WARNING, format=logFormat, datefmt=dateFormat)
    elif level=="ERROR":#The program fails to perform a certain function due to a bug.  SOMETHING BAD LOGIC
        basicConfig(level=ERROR, format=logFormat, datefmt=dateFormat)
    elif level=="CRITICAL":#The program encounters a serious error and may stop running. ERRORS
        basicConfig(level=CRITICAL, format=logFormat, datefmt=dateFormat)
    else:
        if level:#Bad debug parameter
            basicConfig(level=CRITICAL, format=logFormat, datefmt=dateFormat)
            critical("--debug parameter must be DEBUG, INFO, WARNING, ERROR or CRITICAL")
            exit(1)
#            else:     #No debug parameter


def main_console():
    #Separate to launch logging before QT    
    parser=ArgumentParser(prog='devicesinlan',  epilog=epilog, formatter_class=RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version="{} ({})".format(__version__, __versiondate__))
    parser.add_argument('--method', action='store', choices=['PingArp', 'ScapyArping', 'Scapy'], default='PingArp')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--interface', help=_('Net interface name'))
    group.add_argument('--add', help=_('Add a known device'), action='store_true')
    group.add_argument('--remove', help=_('Remove a known device'), action='store_true')
    group.add_argument('--list', help=_('List known devices'), action='store_true')
    group.add_argument('--load', help=_('Load known devices list'), action='store')
    group.add_argument('--save', help=_('Save known devices list'), action='store')
    group.add_argument('--reset', help=_('Reset known devices list'), action='store_true', default=False)
    parser.add_argument('--debug', help=_( "Debug program information"), default=None)

    args=parser.parse_args()

    if args.debug is not None:
        setLoggingLevel(args.debug)
    
    from devicesinlan.libdevicesinlan import MemConsole
    mem=MemConsole()
    signal(SIGINT, mem.signal_handler)
    mem.setQApplication()
    mem.setLanguage()
    mem.setInstallationUUID()
    mem.run(args)
    if platform_system()=="Windows":
        press_key_to_continue()

## @namespace devicesinlan.libdevicesinlan
## @brief Package GUI main function
def main_gui():        

    #Separate to launch logging before QT    
    parser=ArgumentParser(prog='devicesinlan_gui',  epilog=epilog, formatter_class=RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version="{} ({})".format(__version__, __versiondate__))
    parser.add_argument('--debug', help=_( "Debug program information"), default=None)
    args=parser.parse_args()      
    if args.debug is not None:
        setLoggingLevel(args.debug)  
    from devicesinlan.libdevicesinlan_gui import MemGUI
    from devicesinlan.ui.frmMain  import frmMain
    mem=MemGUI()
    signal(SIGINT, mem.signal_handler)
    mem.setQApplication()
    mem.setLanguage()
    mem.setInstallationUUID()
    mem.run(args)

    f = frmMain(mem) 
    f.show()

    exit(mem.app.exec())
