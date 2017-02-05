from PyQt5.QtWidgets import QDialog
from Ui_frmHelp import Ui_frmHelp

class frmHelp(QDialog, Ui_frmHelp):
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
        self.browser.setHtml(
            self.tr("<h2>Documentation</h2>")
        )
