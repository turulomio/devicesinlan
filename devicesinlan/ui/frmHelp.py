from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSlot
from devicesinlan.ui.Ui_frmHelp import Ui_frmHelp
import pkg_resources
from devicesinlan.ui.frmSettings import SetLanguages

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
        self.setSource()
        
    @pyqtSlot(str)      
    def on_cmbProgram_currentIndexChanged(self, stri):
        self.setSource()

    ## Sets html source
    def setSource(self):
        self.languages.selected=self.languages.find_by_name(self.cmbLanguage.currentText())
        if self.cmbProgram.currentIndex()==1:
            program="devicesinlan"
        else:
            program="devicesinlan_gui"
        url=pkg_resources.resource_filename("devicesinlan", "data/{}.{}.html".format(program, self.languages.selected.id))
        f=open(url, encoding="UTF-8")
        html=f.read()
        f.close()
        self.viewer.setHtml(html)
        
