from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import pyqtSlot
from devicesinlan.ui.Ui_frmHelp import Ui_frmHelp
from devicesinlan.libdevicesinlan import package_filename
from devicesinlan.libdevicesinlan_gui import Languages_qcombobox

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
        Languages_qcombobox(self.cmbLanguage, self.mem, self.mem.settings.value("frmSettings/language", "en"))
        
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
        url=package_filename("devicesinlan", "data/{}.{}.html".format(program, self.languages.selected.id))
        f=open(url, encoding="UTF-8")
        html=f.read()
        f.close()
        self.viewer.setHtml(html)
        
