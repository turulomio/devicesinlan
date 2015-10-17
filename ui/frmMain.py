import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Ui_frmMain import *
from frmAbout import *
from frmHelp import *

            
class frmMain(QMainWindow, Ui_frmMain):#    
    def __init__(self, parent = 0,  flags = False):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.showMaximized()

        
    @pyqtSlot(QEvent)   
    def closeEvent(self,event):   
        print ("saliendo")
        qApp.closeAllWindows()
        qApp.exit()
        sys.exit(0)
