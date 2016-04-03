from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from Ui_frmDeviceCRUD import *


class frmDeviceCRUD(QDialog, Ui_frmDeviceCRUD):
    def __init__(self, mem, device, parent = None, name = None, modal = False):
        QDialog.__init__(self, parent)
        self.mem=mem
        self.device=device
        self.setupUi(self)
        self.txtMAC.setText(self.device.mac.upper())
        if self.device.alias:
            self.txtAlias.setText(self.device.alias)
        self.mem.types.qcombobox(self.cmbType, self.device.type.id)
        
    def on_buttonBox_accepted(self):
        self.device.alias=self.txtAlias.text()
        self.device.type=self.mem.types.find_by_id(self.cmbType.itemData(self.cmbType.currentIndex()))
        self.device.link()
