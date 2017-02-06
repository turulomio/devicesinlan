from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QUrl
from Ui_frmHelp import Ui_frmHelp
import platform

class frmHelp(QDialog, Ui_frmHelp):
    def __init__(self, parent = None, name = None, modal = False):
        """
        Constructor
        
        @param parent The parent widget of this dialog. (QWidget)
        @param name The name of this dialog. (QString)
        @param modal Flag indicating a modal dialog. (boolean)
        """
        QDialog.__init__(self, parent)
        if name:
            self.setObjectName(name)
        self.setupUi(self)
        if platform.system()=="Windows":
            self.viewer.setSource(QUrl("devicesinlan.html"))    
        elif platform.system()=="Linux":
            self.viewer.setSource(QUrl("/usr/share/devicesinlan/devicesinlan.html"))    
