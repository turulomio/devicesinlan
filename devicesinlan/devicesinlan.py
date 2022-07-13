## @namespace devicesinlan.devicesinlan
## @brief Package main functions

import signal
import sys
from devicesinlan.reusing.text_inputs import press_key_to_continue
from platform import system as platform_system

def main_console():
    from devicesinlan.libdevicesinlan import MemConsole
    mem=MemConsole()
    signal.signal(signal.SIGINT, mem.signal_handler)
    mem.setQApplication()
    mem.setLanguage()
    mem.setInstallationUUID()
    mem.parse_args()
    if platform_system()=="Windows":
        press_key_to_continue()

## @namespace devicesinlan.libdevicesinlan
## @brief Package GUI main function
def main_gui():
    from devicesinlan.libdevicesinlan_gui import MemGUI
    from devicesinlan.ui.frmMain  import frmMain

    mem=MemGUI()
    signal.signal(signal.SIGINT, mem.signal_handler)
    mem.setQApplication()
    mem.setLanguage()
    mem.setInstallationUUID()
    mem.parse_args()

    f = frmMain(mem) 
    f.show()

    sys.exit(mem.app.exec_())
