## @namespace devicesinlan.devicesinlan
## @brief Package main functions

import signal
import sys

def main_console():
    from devicesinlan.libdevicesinlan import MemConsole
    mem=MemConsole()
    signal.signal(signal.SIGINT, mem.signal_handler)
    mem.setQApplication()
    mem.setLanguage()
    mem.setInstallationUUID()
    mem.parse_args()

## @namespace devicesinlan.libdevicesinlan
## @brief Package GUI main function
def main_gui():
    from devicesinlan.libdevicesinlan import MemGUI
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
