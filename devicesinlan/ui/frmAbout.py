from PyQt6.QtCore import QUrl, PYQT_VERSION_STR
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QDialog
from colorama import __version__ as colorama__version__
from devicesinlan.ui.Ui_frmAbout import Ui_frmAbout
from devicesinlan.ui.myqtablewidget6 import qright, qleft
from devicesinlan import __version__, __versiondate__
from platform import python_version, system as  platform_system
from scapy import __version__ as scapy__version__,  VERSION

class frmAbout(QDialog, Ui_frmAbout):
    def __init__(self, mem, parent = None, name = None, modal = False):
        QDialog.__init__(self, parent)
        if name:
            self.setObjectName(name)
        self.mem=mem
        self.setupUi(self)
        self.lblVersion.setText(self.tr("Version {} ({})".format(__version__,  __versiondate__)))
        self.textBrowser.setHtml(
            self.tr("""Project web page is in <a href="http://github.com/turulomio/devicesinlan/">http://github.com/turulomio/devicesinlan/</a><p> <p>""")+
            self.tr("This program has been developed by Mariano Mu\xf1oz.<p>")+
            self.tr("It has been translated by:")+
            "<ul><li>Mariano Mu\xf1oz</li><li>Nadejda Adam</li></ul><p>\n"+
            self.tr("to the following languages<p>")+
            "<ul><li>English</li><li>Fran\xe7ais</li><li>Espa\xf1ol</li><li>Rom\xe2n</li><li>\u0420\u0443\u0441\u0441\u043a\u0438\u0439</li></ul><p>")
        #self.tblSoftware.settings(self.mem, "frmAbout")
        self.load_tblSoftware()
        self.tblSoftware.itemClicked.connect(self.OpenLink)

    def OpenLink(self, item):
        if item.column() == 1:
            QDesktopServices.openUrl(QUrl(item.text()));

    ##Function that fills tblSoftware with data 
    def load_tblSoftware(self):
        self.tblSoftware.setItem(0, 0, qright(colorama__version__))
        self.tblSoftware.setItem(0, 1, qleft("https://github.com/tartley/colorama"))
                        
        self.tblSoftware.setItem(1, 0, qright(PYQT_VERSION_STR))
        self.tblSoftware.setItem(1, 1, qleft("https://riverbankcomputing.com/software/pyqt/intro"))
                
        self.tblSoftware.setItem(2, 0, qright(python_version()))
        self.tblSoftware.setItem(2, 1, qleft("https://www.python.org"))
        
        if platform_system()=="Windows":
            self.tblSoftware.setItem(3, 0, qright(VERSION))
        else:
            self.tblSoftware.setItem(3, 0, qright(scapy__version__[:-1]))
        self.tblSoftware.setItem(3, 1, qleft("https://github.com/secdev/scapy"))
        
        #self.tblSoftware.applySettings()
