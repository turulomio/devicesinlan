import datetime
import sys
from PyQt5.QtWidgets import *

from Ui_frmMain import *
from frmAbout import *
from frmHelp import *
from libdevicesinlan import *
from frmSettings import *
from frmHelp import *
from frmAbout import *
from frmInterfaceSelector import *

            
class frmMain(QMainWindow, Ui_frmMain):#    
    def __init__(self, mem, parent = 0,  flags = False):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.showMaximized()
        self.setWindowTitle("DevicesInLan 2015-{}. GNU General Public License".format(dateversion.year))
        self.mem=mem
        self.sets=[]#Array of sets
        self.tables=[]#Array of tables
        self.tabWidget = QTabWidget(self.wdg)
        self.horizontalLayout.addWidget(self.tabWidget)
        self.showMaximized()
        self.repaint()

        
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
    def on_actionScan_triggered(self):
        f=frmInterfaceSelector(self.mem, self)
        f.exec_()
        if f.result()!=QDialog.Accepted:
            return
        
        
        self.tab = QWidget()
        self.tabWidget.addTab(self.tab, QIcon(":/open.png"),self.tr("Scanned at {}").format(str(datetime.datetime.now()).split(".")[0]))
        table=QTableWidget(self.tabWidget)
        horizontalLayout_2 = QVBoxLayout(self.tab)
        table.setColumnCount(0)
        table.setRowCount(0)
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        horizontalLayout_2.addWidget(table)        
        table.setAlternatingRowColors(True)
        
        
        inicio=datetime.datetime.now()
        set=SetDevices(self.mem)
        set.qtablewidget(table)
        self.sets.append(set)
        self.tables.append(table)
        label=QLabel()
        label.setText(self.tr("It took {} to detect {} devices".format(datetime.datetime.now()-inicio, set.length())))
        horizontalLayout_2.addWidget(label)
        table.resizeColumnsToContents()
        table.customContextMenuRequested[QPoint].connect(self.on_customContextMenuRequested)
        table.itemSelectionChanged.connect(self.on_itemSelectionChanged)
        self.tabWidget.setCurrentWidget(self.tab)

    def on_customContextMenuRequested(self, pos):
        table=self.tables[self.tabWidget.currentIndex()]
        menu=QMenu()
        menu.addAction(self.actionDeviceLink)
        menu.addAction(self.actionDeviceUnlink)
        menu.exec_(table.mapToGlobal(pos))


    def on_itemSelectionChanged(self):
        set=self.sets[self.tabWidget.currentIndex()]
        table=self.tables[self.tabWidget.currentIndex()]
        try:
            for i in table.selectedItems():#itera por cada item no rowse.
                set.selected=set.arr[i.row()]
        except:
            set.selected=None
        print ("selected: " +  str(set.selected))        
