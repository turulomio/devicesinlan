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

            
class frmMain(QMainWindow, Ui_frmMain):#    
    def __init__(self, mem, parent = 0,  flags = False):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.showMaximized()
        self.setWindowTitle("DevicesInLan 2015-{}. GNU General Public License".format(dateversion.year))
        self.mem=mem
        self.tabWidget = QTabWidget(self.wdg)
        self.horizontalLayout.addWidget(self.tabWidget)
        self.on_actionScan_triggered()

        
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
        self.actionScan.setEnabled(False)
        self.tab = QWidget()
        self.tabWidget.addTab(self.tab, "Scanned at {}".format(datetime.datetime.now()))
        table=QTableWidget(self.tabWidget)
        horizontalLayout_2 = QVBoxLayout(self.tab)
        table.setColumnCount(0)
        table.setRowCount(0)
        horizontalLayout_2.addWidget(table)        
        table.setAlternatingRowColors(True)
        
        
        inicio=datetime.datetime.now()
        set=SetDevices(self.mem)
        set.qtablewidget(table)
        label=QLabel()
        label.setText(self.tr("It took {}".format(datetime.datetime.now()-inicio)))
        horizontalLayout_2.addWidget(label)
#        table.resizeRowsToContents()
        table.resizeColumnsToContents()
        self.actionScan.setEnabled(True)
        
        
        
        
