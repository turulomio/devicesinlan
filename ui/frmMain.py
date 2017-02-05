import datetime
import sys
from PyQt5.QtCore import pyqtSlot, Qt, QPoint, QEvent
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QMenu, QTabWidget, QTableWidget,  QDialog, QWidget, QVBoxLayout, QLabel,  QAbstractItemView, qApp

from Ui_frmMain import Ui_frmMain
from libdevicesinlan import dateversion,  SetDevices,  ArpScanMethod
from frmSettings import frmSettings
from frmHelp import frmHelp
from frmAbout import frmAbout
from frmInterfaceSelector import frmInterfaceSelector
from frmDeviceCRUD import frmDeviceCRUD

            
class frmMain(QMainWindow, Ui_frmMain):#    
    def __init__(self, mem, parent = 0,  flags = False):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.showMaximized()
        self.setWindowTitle("DevicesInLan 2015-{}. GNU General Public License".format(dateversion.year))
        self.mem=mem
        self.sets=[]#Array of sets
        self.tables=[]#Array of tables
        self.currentTable=None
        self.currentSet=None
        self.tabWidget = QTabWidget(self.wdg)
        self.horizontalLayout.addWidget(self.tabWidget)
        self.showMaximized()
        self.tabWidget.currentChanged.connect(self.on_tabWidget_currentChanged)

        
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
    def on_actionShowDatabase_triggered(self):
        self.tab = QWidget()
        table=QTableWidget(self.tabWidget)
        horizontalLayout_2 = QVBoxLayout(self.tab)
        table.setColumnCount(0)
        table.setRowCount(0)
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        horizontalLayout_2.addWidget(table)        
        table.setAlternatingRowColors(True)
        
        
        inicio=datetime.datetime.now()
        set=SetDevices(self.mem)
        set.init__from_settings()
        self.sets.append(set)
        self.tables.append(table)
        self.tabWidget.addTab(self.tab, QIcon(":/database.png"),self.tr("Database devices at {}").format(str(datetime.datetime.now()).split(".")[0]))
        self.tabWidget.setCurrentWidget(self.tab)
        self.table_update(set, table)
        label=QLabel()
        label.setText(self.tr("It took {} to show {} devices".format(datetime.datetime.now()-inicio, set.length())))
        horizontalLayout_2.addWidget(label)
        table.customContextMenuRequested[QPoint].connect(self.on_customContextMenuRequested)
        table.itemSelectionChanged.connect(self.on_itemSelectionChanged)

        
    @pyqtSlot()      
    def on_actionHelp_triggered(self):
        fr=frmHelp(self,"frmHelp")
        fr.open()
        
                
    @pyqtSlot()      
    def on_actionSettings_triggered(self):
        f=frmSettings(self.mem, self)
        f.exec_()
        self.retranslateUi(self)
        self.repaint()
        
            
    @pyqtSlot()      
    def on_actionDeviceLink_triggered(self):
        f=frmDeviceCRUD(self.mem, self.currentSet)
        f.exec_() 
        self.table_update(self.currentSet, self.currentTable)
        
    @pyqtSlot()      
    def on_actionDeviceUnlink_triggered(self):
        self.currentSet.unlink(self.currentSet.selected)
        self.table_update(self.currentSet, self.currentTable)
        
    def table_update(self, set, table):
        if set.isDatabase==True:
            set.qtablewidget_devices_from_settings(table)
        else:
            set.qtablewidget(table)
        table.resizeColumnsToContents()
        
        
        
    @pyqtSlot()      
    def on_actionScan_triggered(self):
        f=frmInterfaceSelector(self.mem, self)
        f.exec_()
        if f.result()!=QDialog.Accepted:
            return
        
        
        self.tab = QWidget()
        table=QTableWidget(self.tabWidget)
        horizontalLayout_2 = QVBoxLayout(self.tab)
        table.setColumnCount(0)
        table.setRowCount(0)
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        horizontalLayout_2.addWidget(table)        
        table.setAlternatingRowColors(True)
        
        
        inicio=datetime.datetime.now()
        set=SetDevices(self.mem)
        set.setMethod(ArpScanMethod.PingArp)
        self.sets.append(set)
        self.tables.append(table)
        self.tabWidget.addTab(self.tab, QIcon(":/open.png"),self.tr("Scanned at {}").format(str(datetime.datetime.now()).split(".")[0]))
        self.tabWidget.setCurrentWidget(self.tab)
        self.table_update(set, table)
        label=QLabel()
        label.setText(self.tr("It took {} to detect {} devices".format(datetime.datetime.now()-inicio, set.length())))
        horizontalLayout_2.addWidget(label)
        table.customContextMenuRequested[QPoint].connect(self.on_customContextMenuRequested)
        table.itemSelectionChanged.connect(self.on_itemSelectionChanged)

    def on_customContextMenuRequested(self, pos):
        if self.currentSet.selected==None:
            self.actionDeviceLink.setEnabled(False)
            self.actionDeviceUnlink.setEnabled(False)
        else:
            self.actionDeviceLink.setEnabled(True)
            if self.currentSet.isDatabase==True:
                self.actionDeviceLink.setEnabled(False)
            else:
                self.actionDeviceUnlink.setEnabled(True)
        menu=QMenu()
        menu.addAction(self.actionDeviceLink)
        menu.addAction(self.actionDeviceUnlink)
        menu.exec_(self.currentTable.mapToGlobal(pos))

    def on_tabWidget_currentChanged(self, index):
        self.currentSet=self.sets[index]
        self.currentTable=self.tables[index]

    def on_itemSelectionChanged(self):
        try:
            for i in self.currentTable.selectedItems():#itera por cada item no rowse.
                self.currentSet.selected=self.currentSet.arr[i.row()]
            if self.currentSet.selected.mac==None:
                self.currentSet.selected=None
        except:
            self.currentSet.selected=None   
