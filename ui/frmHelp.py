from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QUrl, pyqtSlot
from Ui_frmHelp import Ui_frmHelp
import platform
from frmSettings import SetLanguages

class frmHelp(QDialog, Ui_frmHelp):
    def __init__(self, mem, parent = None, name = None, modal = False):
        """
        Constructor
        
        @param parent The parent widget of this dialog. (QWidget)
        @param name The name of this dialog. (QString)
        @param modal Flag indicating a modal dialog. (boolean)
        """
        QDialog.__init__(self, parent)
        self.mem=mem
        self.setupUi(self)
        self.languages=SetLanguages()
        self.languages.qcombobox(self.cmbLanguage, self.mem.settings.value("frmSettings/language", "en"))         
        
    @pyqtSlot(str)      
    def on_cmbLanguage_currentIndexChanged(self, stri):        
        self.languages.selected=self.languages.find_by_name(stri)
        if platform.system()=="Windows":
            self.viewer.setSource(QUrl("devicesinlan.{}.1.html".format(self.languages.selected.id)))    
        elif platform.system()=="Linux":
            self.viewer.setSource(QUrl("/usr/share/devicesinlan/devicesinlan.{}.1.html".format(self.languages.selected.id)))    
        self.retranslateUi(self)
