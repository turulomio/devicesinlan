from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Ui_frmAbout import *
import libdevicesinlan

class frmAbout(QDialog, Ui_frmAbout):
    def __init__(self, parent = None, name = None, modal = False):
        """
        Constructor
        
        @param parent The parent widget of this dialog. (QWidget)
        @param name The name of this dialog. (QString)
        @param modal Flag indicating a modal dialog. (boolean)
        """
        QDialog.__init__(self, parent)
        if name:
            self.setObjectName(name)
        self.setupUi(self)
        self.lblVersion.setText(self.tr("Versión {0}".format(libdevicesinlan.version)))
        self.textBrowser.setHtml(
            self.tr("La página del proyecto se encuentra en <a href=\"http://devicesinlan.sourceforge.net\">http://devicesinlan.sourceforge.net</a><p> <p>")+
            self.tr("Este programa ha sido desarrollado por Mariano Muñoz.<p>")+
            self.tr("Ha sido traducido por:")+
            "<ul><li>Mariano Muñoz</li><li>Nadejda Adam</li></ul><p>\n"+
            self.tr("a los siguientes idiomas<p>")+
            "<ul><li>English</li><li>Fran\xe7ais</li><li>Espa\xf1ol</li><li>Rom\xe2n</li><li>\u0420\u0443\u0441\u0441\u043a\u0438\u0439</li></ul><p>")


