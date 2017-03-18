from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSlot
from Ui_frmInterfaceSelector import Ui_frmInterfaceSelector


class frmInterfaceSelector(QDialog, Ui_frmInterfaceSelector):
    def __init__(self, mem, parent = None, name = None, modal = False):
        QDialog.__init__(self, parent)
        self.mem=mem
        self.setupUi(self)
        self.mem.interfaces.qcombobox(self.cmbName, self.mem.settings.value("frmInterfaceSelector/interface_id", None))

    @pyqtSlot(int)      
    def on_cmbName_currentIndexChanged(self, id): 
        self.mem.interfaces.selected=self.mem.interfaces.find_by_id(self.cmbName.itemData(id))
        if self.mem.interfaces.selected!=None:
            self.txtIP.setText(self.mem.interfaces.selected.ip())
            self.txtMAC.setText(self.mem.interfaces.selected.mac())
            self.txtBroadcast.setText(self.mem.interfaces.selected.broadcast())
            self.txtMask.setText(self.mem.interfaces.selected.netmask())
            self.txtId.setText(self.mem.interfaces.selected.id())

    def on_buttonBox_accepted(self):
        self.mem.settings.setValue("frmInterfaceSelector/interface_id", self.mem.interfaces.selected.id())
