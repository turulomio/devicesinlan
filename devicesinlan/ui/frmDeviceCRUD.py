from PyQt6.QtWidgets import QDialog
from devicesinlan.ui.Ui_frmDeviceCRUD import Ui_frmDeviceCRUD
from devicesinlan.libdevicesinlan_gui import DeviceTypeManager_qcombobox


class frmDeviceCRUD(QDialog, Ui_frmDeviceCRUD):
    def __init__(self, mem, set, parent = None, name = None, modal = False):
        QDialog.__init__(self, parent)
        self.mem=mem
        self.set=set
        self.device=self.set.selected#Hay siempre ya que la lista es con ip desconocida almenos
        self.setupUi(self)
        self.txtMAC.setText(self.device.mac.upper())
        if self.device.alias:
            self.txtAlias.setText(self.device.alias)
        DeviceTypeManager_qcombobox(self.mem.types, self.cmbType, self.device.type.id)
        
    def on_buttonBox_accepted(self):
        self.device.alias=self.txtAlias.text()
        self.device.type=self.mem.types.find_by_id(self.cmbType.itemData(self.cmbType.currentIndex()))
        self.set.link(self.device)
