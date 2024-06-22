from PyQt6.QtWidgets import QDialog
from devicesinlan.ui.Ui_frmHelp import Ui_frmHelp
from devicesinlan.libdevicesinlan_gui import Languages_qcombobox
from importlib.resources import files 

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
        self.selected_language=self.mem.dod_languages[self.mem.settings.value("frmSettings/language", "en")]
        
    def on_cmbLanguage_currentIndexChanged(self, index):
        self.selected_language=self.mem.lod_languages[index]
        self.setSource()
        
    def on_cmbProgram_currentIndexChanged(self, index):
        self.setSource()

    ## Sets html source
    def setSource(self):        
        if self.cmbProgram.currentIndex()==1:
            program="devicesinlan"
        else:
            program="devicesinlan_gui"
            
            
        url=files("devicesinlan") / "data/{}.{}.html".format(program, self.selected_language["code"])
        with open(url, encoding="UTF-8") as f:
            self.viewer.setHtml(f.read())

