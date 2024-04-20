from PyQt6.QtWidgets import QDialog
from devicesinlan.libdevicesinlan_gui import Languages_qcombobox
from devicesinlan.ui.Ui_frmSettings import Ui_frmSettings

class frmSettings(QDialog, Ui_frmSettings):
    def __init__(self, mem, parent = None, name = None, modal = False):
        QDialog.__init__(self, parent)
        self.mem=mem
        self.setupUi(self) 
        Languages_qcombobox(self.cmbLanguage, self.mem, self.mem.settings.value("frmSettings/language", "en"))
        self.selected_language=self.mem.dod_languages[self.mem.settings.value("frmSettings/language", "en")]
        self.spnConcurrent.setValue(int(self.mem.settings.value("frmSettings/concurrence", 200)))

    def on_cmbLanguage_currentIndexChanged(self, index):
        self.selected_language=self.mem.lod_languages[index]
        self.mem.setLanguage( self.selected_language["code"])
        self.retranslateUi(self)
        
    def on_buttonBox_accepted(self):
        self.mem.settings.setValue("frmSettings/language", self.selected_language["code"])
        self.mem.settings.setValue("frmSettings/concurrence", self.spnConcurrent.value())
        self.mem.settings.sync()
