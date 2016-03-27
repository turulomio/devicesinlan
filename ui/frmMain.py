import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Ui_frmMain import *
from frmAbout import *
from frmHelp import *
from libdevicesinlan import *

            
class frmMain(QMainWindow, Ui_frmMain):#    
    def __init__(self, parent = 0,  flags = False):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.showMaximized()
        self.setWindowTitle("DevicesInLan 2015-{}. GNU General Public License".format(dateversion.year))

        
    @pyqtSlot(QEvent)   
    def closeEvent(self,event):   
        print ("saliendo")
        qApp.closeAllWindows()
        qApp.exit()
        sys.exit(0)

    @pyqtSlot()      
    def on_actionAcercaDe_triggered(self):
        fr=frmAbout(self,"frmabout")
        fr.open()
        
                
    @pyqtSlot()      
    def on_actionSettings_triggered(self):
        f=frmSettings(self.settings, self.translator,    self)
        f.exec_()
        if self.game!=None:
            self.game.retranslateUi(self)
            for p in self.game.panels:
                p.retranslateUi(self)
                p.repaint()
                p.setJugador(p.jugador)#Se repinta
        self.retranslateUi(self)
        self.repaint()
        
        
        
