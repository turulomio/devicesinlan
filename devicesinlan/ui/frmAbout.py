from PyQt5.QtWidgets import QDialog
from devicesinlan.ui.Ui_frmAbout import Ui_frmAbout
from devicesinlan.version import __version__, __versiondate__

class frmAbout(QDialog, Ui_frmAbout):
    ##Constructor        
    # @param parent The parent widget of this dialog. (QWidget)
    # @param name The name of this dialog. (QString)
    # @param modal Flag indicating a modal dialog. (boolean)
    def __init__(self, parent = None, name = None, modal = False):
        QDialog.__init__(self, parent)
        if name:
            self.setObjectName(name)
        self.setupUi(self)
        self.lblVersion.setText(self.tr("Version {} ({})".format(__version__,  __versiondate__)))
        self.textBrowser.setHtml(
            self.tr("Project web page is in <a href=\"http://devicesinlan.sourceforge.net\">http://devicesinlan.sourceforge.net</a><p> <p>")+
            self.tr("This program has been developed by Mariano Mu\xf1oz.<p>")+
            self.tr("It has been translated by:")+
            "<ul><li>Mariano Mu\xf1oz</li><li>Nadejda Adam</li></ul><p>\n"+
            self.tr("to the following languages<p>")+
            "<ul><li>English</li><li>Fran\xe7ais</li><li>Espa\xf1ol</li><li>Rom\xe2n</li><li>\u0420\u0443\u0441\u0441\u043a\u0438\u0439</li></ul><p>")


