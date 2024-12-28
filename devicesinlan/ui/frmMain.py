from PyQt6.QtCore import pyqtSlot, Qt, QPoint, QEvent, QUrl
from PyQt6.QtGui import QIcon, QPixmap, QDesktopServices, QAction
from PyQt6.QtWidgets import QMainWindow, QMenu, QTabWidget, QTableWidget,  QDialog, QWidget, QVBoxLayout, QLabel,  QAbstractItemView, QApplication, QMessageBox, QFileDialog
from datetime import datetime, date, timedelta
from devicesinlan.ui.Ui_frmMain import Ui_frmMain
from devicesinlan.libdevicesinlan import ArpScanMethod, DeviceManager
from devicesinlan import __version__, __versiondate__,  get_remote
from devicesinlan.libdevicesinlan_gui import  qmessagebox, qquestion,  DeviceManager_qtablewidget,  DeviceManager_qtablewidget_devices_from_settings
from devicesinlan.ui.frmSettings import frmSettings
from devicesinlan.ui.frmHelp import frmHelp
from devicesinlan.ui.frmAbout import frmAbout
from devicesinlan.ui.frmInterfaceSelector import frmInterfaceSelector
from devicesinlan.ui.frmDeviceCRUD import frmDeviceCRUD
from logging import warning
from sys import exit

class myTab(QWidget):
    """Widget to add tabs and vinculate set and,table"""
    def __init__(self, set, tabWidget):
        QWidget.__init__(self)
        self.set=set
        self.tabWidget=tabWidget
        self.table=QTableWidget(self.tabWidget)
        self.verticalLayout = QVBoxLayout(self)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.verticalLayout.addWidget(self.table)        
        self.table.setAlternatingRowColors(True)
        if self.set.isDatabase==True:
            self.tabWidget.addTab(self, QIcon(":/database.png"),self.tr("Database devices at {}").format(str(datetime.now()).split(".")[0]))
        else:
            self.tabWidget.addTab(self, QIcon(":/open.png"),self.tr("Scanned at {}").format(str(datetime.now()).split(".")[0]))
        self.tabWidget.setCurrentWidget(self)
        self.table_update()
        self.label=QLabel(self)
        self.verticalLayout.addWidget(self.label)
        self.table.customContextMenuRequested[QPoint].connect(self.on_customContextMenuRequested)
        self.table.itemSelectionChanged.connect(self.on_itemSelectionChanged)
        
        self.actionDeviceLink = QAction(self)
        icon5 = QIcon()
        icon5.addPixmap(QPixmap(":/save.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionDeviceLink.setIcon(icon5)
        self.actionDeviceLink.triggered.connect(self.on_actionDeviceLink_triggered)
        
        self.actionDeviceUnlink = QAction(self)
        self.actionDeviceUnlink.setText(self.tr("Remove known device"))
        icon6 = QIcon()
        icon6.addPixmap(QPixmap(":/cancel.png"), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionDeviceUnlink.setIcon(icon6)
        self.actionDeviceUnlink.triggered.connect(self.on_actionDeviceUnlink_triggered)

    def setLabelText(self, t):
        self.label.setText(t)
    
    def table_update(self):
        if self.set.isDatabase==True:
            DeviceManager_qtablewidget_devices_from_settings(self.set, self.table)
        else:
            DeviceManager_qtablewidget(self.set, self.table)
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
        f.exec() 
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
        menu.exec(self.table.mapToGlobal(pos))

class frmMain(QMainWindow, Ui_frmMain):#    
    def __init__(self, mem, parent = 0,  flags = False):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.showMaximized()
        self.setWindowTitle("DevicesInLan 2015-{}. GNU General Public License".format(__versiondate__.year))
        self.mem=mem
        self.tabWidget = QTabWidget(self.wdg)
        self.tabWidget.setTabsClosable(True)
        self.horizontalLayout.addWidget(self.tabWidget)
        self.showMaximized()
        self.tabWidget.tabCloseRequested.connect(self.on_tabWidget_tabCloseRequested)
        if date.today()-date.fromordinal(int(self.mem.settings.value("frmMain/lastupdate", 1)))>=timedelta(days=7):
            self.checkUpdates(False)
                
    @pyqtSlot()      
    def on_actionUpdates_triggered(self):
        self.checkUpdates(True)            
        
    @pyqtSlot()      
    def on_actionListLoad_triggered(self):
        filename=QFileDialog.getOpenFileName(self, "", "", "eXtensible Markup Language (*.xml)")[0]
        if filename!="":
            current=DeviceManager(self.mem).init__from_settings()
            new=DeviceManager(self.mem).init__from_xml(filename)
            for n in new.arr:
                c=current.find_by_mac(n.mac)
                if c==None:#Not found its mac so n is new
                    if qquestion(self.tr("Do you want to add this {} with MAC {} and set its name to {}?".format(n.type.name.lower(), n.mac, n.alias)),  QIcon(":/save.png"))==QMessageBox.Yes:
                        n.link()
                else:
                    if n!=c:
                        if qquestion(self.tr("We already have a device with this MAC: {}. Do you want to change its alias ({}) and type ({}) to a {} named {}?".format(c.mac, c.alias, c.type.name.lower(), n.type.name.lower(), n.alias)),  QIcon(":/save.png"))==QMessageBox.Yes:
                            n.link()
    
    @pyqtSlot()      
    def on_actionListSave_triggered(self):
        devices=DeviceManager(self.mem).init__from_settings()
        c=str(datetime.now()).replace("-","").replace(":","").replace(" ","_")[:-7]
        filename= QFileDialog.getSaveFileName(self, self.tr("Save File"), "devicesinlan_{}.xml".format(c), self.tr("eXtensible Markup Language (*.xml)"))[0]
        if filename!="":
            devices.saveXml(filename)

    def checkUpdates(self, showdialogwhennoupdates=False):
        remoteversion=get_remote("https://raw.githubusercontent.com/turulomio/devicesinlan/refs/heads/main/devicesinlan/__init__.py")
        if remoteversion==None:
            qmessagebox(self.tr("I couldn't look for updates. Try it later.."))
            return
                
        if remoteversion.replace("+", "")==__version__.replace("+", ""):#Quita el más de desarrollo 
            if showdialogwhennoupdates==True:
                qmessagebox(self.tr("You have the last version"))
        else:
            m=QMessageBox()
            m.setIcon(QMessageBox.Icon.Information)
            m.setWindowIcon(QIcon(":/devicesinlan.png"))
            m.setTextFormat(Qt.TextFormat.RichText)#this is what makes the links clickable
            m.setText(self.tr("There is a new DevicesInLAN version. You can download it from <a href='https://github.com/Turulomio/devicesinlan/releases'>GitHub</a>."))
            m.exec() 
        self.mem.settings.setValue("frmMain/lastupdate", date.today().toordinal())

    @pyqtSlot(QEvent)   
    def closeEvent(self,event):   
        warning ("Exiting")
        QApplication.closeAllWindows()
        QApplication.exit()
        exit(0)

    @pyqtSlot()      
    def on_actionAbout_triggered(self):
        fr=frmAbout(self.mem, self, "frmAbout")
        fr.open()

    @pyqtSlot()  
    def on_actionReportIssue_triggered(self):        
            QDesktopServices.openUrl(QUrl("https://github.com/turulomio/devicesinlan/issues/new"))

    @pyqtSlot()      
    def on_actionResetDatabase_triggered(self):
        m=QMessageBox()
        icon6 = QIcon()
        icon6.addPixmap(QPixmap(":/cancel.png"), QIcon.Mode.Normal, QIcon.State.Off)
        m.setWindowIcon(icon6)
        confirm=m.question(self, self.tr("Erase database confirmation"), self.tr("This action will erase known devices database. Do you want to continue?."), QMessageBox.Yes, QMessageBox.No)
        if confirm==QMessageBox.Yes:
            devices=DeviceManager(self.mem).init__from_settings()
            devices.reset()
            self.on_actionShowDatabase_triggered()
        
    @pyqtSlot()      
    def on_actionHelp_triggered(self):
        fr=frmHelp(self.mem, self,"frmHelp")
        fr.open()

    @pyqtSlot()      
    def on_actionSettings_triggered(self):
        f=frmSettings(self.mem, self)
        f.exec()
        self.retranslateUi(self)
        self.repaint()

    @pyqtSlot()      
    def on_actionScan_triggered(self):
        f=frmInterfaceSelector(self.mem, self)
        f.exec()
        if f.result()!=QDialog.DialogCode.Accepted:
            return
        
        inicio=datetime.now()
        set=DeviceManager(self.mem)
        set.setMethod(ArpScanMethod.PingArp)
        
        self.tab = myTab(set, self.tabWidget)
        self.tab.setLabelText(self.tr("It took {} to detect {} devices".format(datetime.now()-inicio, set.length())))
        set.print()

    @pyqtSlot()
    def on_actionShowDatabase_triggered(self):
        inicio=datetime.now()
        set=DeviceManager(self.mem)
        set.init__from_settings()
        
        self.tab = myTab(set, self.tabWidget)
        self.tab.setLabelText(self.tr("It took {} to show {} devices".format(datetime.now()-inicio, set.length())))
        set.print_devices_from_settings()

    def on_tabWidget_tabCloseRequested(self, index):
        self.tabWidget.removeTab(index)
