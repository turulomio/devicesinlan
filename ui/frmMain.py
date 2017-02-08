import datetime
import sys
from PyQt5.QtCore import pyqtSlot, Qt, QPoint, QEvent
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMainWindow, QMenu, QTabWidget, QTableWidget,  QDialog, QWidget, QVBoxLayout, QLabel,  QAbstractItemView, qApp, QMessageBox, QAction

from Ui_frmMain import Ui_frmMain
from libdevicesinlan import dateversion,  SetDevices,  ArpScanMethod
from frmSettings import frmSettings
from frmHelp import frmHelp
from frmAbout import frmAbout
from frmInterfaceSelector import frmInterfaceSelector
from frmDeviceCRUD import frmDeviceCRUD



class myTab(QWidget):
    """Widget to add tabs and vinculate set and,table"""
    def __init__(self, set, tabWidget):
        QWidget.__init__(self)
        self.set=set
        self.tabWidget=tabWidget
        self.table=QTableWidget(self.tabWidget)
        self.verticalLayout = QVBoxLayout(self)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.verticalLayout.addWidget(self.table)        
        self.table.setAlternatingRowColors(True)
        if self.set.isDatabase==True:
            self.tabWidget.addTab(self, QIcon(":/database.png"),self.tr("Database devices at {}").format(str(datetime.datetime.now()).split(".")[0]))
        else:
            self.tabWidget.addTab(self, QIcon(":/open.png"),self.tr("Scanned at {}").format(str(datetime.datetime.now()).split(".")[0]))
        self.tabWidget.setCurrentWidget(self)
        self.table_update()
        self.label=QLabel(self)
        self.verticalLayout.addWidget(self.label)
        self.table.customContextMenuRequested[QPoint].connect(self.on_customContextMenuRequested)
        self.table.itemSelectionChanged.connect(self.on_itemSelectionChanged)
        
        self.actionDeviceLink = QAction(self)
        icon5 = QIcon()
        icon5.addPixmap(QPixmap(":/save.png"), QIcon.Normal, QIcon.Off)
        self.actionDeviceLink.setIcon(icon5)
        self.actionDeviceLink.triggered.connect(self.on_actionDeviceLink_triggered)
        
        self.actionDeviceUnlink = QAction(self)
        self.actionDeviceUnlink.setText(self.tr("Remove known device"))
        icon6 = QIcon()
        icon6.addPixmap(QPixmap(":/cancel.png"), QIcon.Normal, QIcon.Off)
        self.actionDeviceUnlink.setIcon(icon6)
        self.actionDeviceUnlink.triggered.connect(self.on_actionDeviceUnlink_triggered)
        
        
    def setLabelText(self, t):
        self.label.setText(t)
    
    def table_update(self):
        if self.set.isDatabase==True:
            self.set.qtablewidget_devices_from_settings(self.table)
        else:
            self.set.qtablewidget(self.table)
        self.table.resizeColumnsToContents()
        
        

    def on_itemSelectionChanged(self):
        try:
            for i in self.table.selectedItems():#itera por cada item no rowse.
                self.set.selected=self.set.arr[i.row()]
            if self.set.selected.mac==None:
                self.set.selected=None
        except:
            self.set.selected=None   

    @pyqtSlot()      
    def on_actionDeviceLink_triggered(self):
        f=frmDeviceCRUD(self.set.mem, self.set)
        f.lblTitle.setText(self.actionDeviceLink.text())
        f.exec_() 
        self.table_update()
        
    @pyqtSlot()      
    def on_actionDeviceUnlink_triggered(self):
        self.set.unlink(self.set.selected)
        self.table_update()
        
    def on_customContextMenuRequested(self, pos):
        if self.set.selected==None:
            self.actionDeviceLink.setEnabled(False)
            self.actionDeviceUnlink.setEnabled(False)
        else:
            self.actionDeviceLink.setEnabled(True)
            self.actionDeviceUnlink.setEnabled(True)
            if self.set.isDatabase==True:
                self.actionDeviceLink.setText(self.tr("Edit known device"))
            else:
                self.actionDeviceLink.setText(self.tr("Set as a known device"))
        menu=QMenu()
        menu.addAction(self.actionDeviceLink)
        menu.addAction(self.actionDeviceUnlink)
        menu.exec_(self.table.mapToGlobal(pos))

class frmMain(QMainWindow, Ui_frmMain):#    
    def __init__(self, mem, parent = 0,  flags = False):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.showMaximized()
        self.setWindowTitle("DevicesInLan 2015-{}. GNU General Public License".format(dateversion.year))
        self.mem=mem
        self.tabWidget = QTabWidget(self.wdg)
        self.tabWidget.setTabsClosable(True)
        self.horizontalLayout.addWidget(self.tabWidget)
        self.showMaximized()
        self.tabWidget.tabCloseRequested.connect(self.on_tabWidget_tabCloseRequested)

        
    @pyqtSlot(QEvent)   
    def closeEvent(self,event):   
        print ("Exiting")
        qApp.closeAllWindows()
        qApp.exit()
        sys.exit(0)

    @pyqtSlot()      
    def on_actionAbout_triggered(self):
        fr=frmAbout(self,"frmAbout")
        fr.open()

    @pyqtSlot()      
    def on_actionResetDatabase_triggered(self):
        m=QMessageBox()
        icon6 = QIcon()
        icon6.addPixmap(QPixmap(":/cancel.png"), QIcon.Normal, QIcon.Off)
        m.setWindowIcon(icon6)
        confirm=m.question(self, self.tr("Erase database confirmation"), self.tr("This action will erase known devices database. Do you want to continue?."), QMessageBox.Yes, QMessageBox.No)
        if confirm==QMessageBox.Yes:
            self.mem.settings.clear()
            self.mem.settings.sync()
            self.on_actionShowDatabase_triggered()
        
    @pyqtSlot()      
    def on_actionHelp_triggered(self):
        fr=frmHelp(self.mem, self,"frmHelp")
        fr.open()

    @pyqtSlot()      
    def on_actionSettings_triggered(self):
        f=frmSettings(self.mem, self)
        f.exec_()
        self.retranslateUi(self)
        self.repaint()


    @pyqtSlot()      
    def on_actionScan_triggered(self):
        f=frmInterfaceSelector(self.mem, self)
        f.exec_()
        if f.result()!=QDialog.Accepted:
            return
        
        inicio=datetime.datetime.now()
        set=SetDevices(self.mem)
        set.setMethod(ArpScanMethod.PingArp)
        
        self.tab = myTab(set, self.tabWidget)
        self.tab.setLabelText(self.tr("It took {} to detect {} devices".format(datetime.datetime.now()-inicio, set.length())))
        
        set.print()

    @pyqtSlot()      
    def on_actionShowDatabase_triggered(self):
        inicio=datetime.datetime.now()
        set=SetDevices(self.mem)
        set.init__from_settings()
        
        self.tab = myTab(set, self.tabWidget)
        self.tab.setLabelText(self.tr("It took {} to show {} devices".format(datetime.datetime.now()-inicio, set.length())))
        
        set.print_devices_from_settings()

    def on_tabWidget_tabCloseRequested(self, index):
#        self.tabWidget.currentWidget().close()
        self.tabWidget.removeTab(index)
