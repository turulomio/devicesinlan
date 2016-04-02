from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from Ui_frmSettings import *

class Language:
    def __init__(self, id, name):
        self.id=id
        self.name=name
        
    def qpixmap(self):
        if self.id=="fr":
            return QPixmap(":/flags/france.png")
        elif self.id=="es":
            return QPixmap(":/flags/spain.png")
        elif self.id=="en":
            return QPixmap(":/flags/uk.png")
        elif self.id=="ro":
            return QPixmap(":/flags/rumania.png")
        elif self.id=="ru":
            return QPixmap(":/flags/rusia.png")
            
    def qicon(self):
        ico = QIcon()
        ico.addPixmap(self.qpixmap(), QIcon.Normal, QIcon.Off) 
        return ico

class SetLanguages:
    def __init__(self):
        self.arr=[]
        self.selected=None
        self.load_all()
        
    def append(self, o):
        self.arr.append(o)
        
    def load_all(self):
        self.append(Language("en","English" ))
        self.append(Language("es",QApplication.translate("devicesinlan","Espanol" )))
        self.append(Language("fr",QApplication.translate("devicesinlan","Francais" )))
        self.append(Language("ro","Rom\xe2n" ))
        self.append(Language("ru",'\u0420\u0443\u0441\u0441\u043a\u0438\u0439' ))

    def find_by_id(self, id):
        for l in self.arr:
            if l.id==id:
                return l
        return None
    def find_by_name(self, name):
        for l in self.arr:
            if l.name==name:
                return l
        return None    
        
    def order_by_name(self):
        """Orders the Set using self.arr"""
        try:
            self.arr=sorted(self.arr, key=lambda c: c.name,  reverse=False)       
            return True
        except:
            return False        

    def qcombobox(self, combo, selected=None):
        """Selected is id"""
        self.order_by_name()
        for l in self.arr:
            combo.addItem(l.qicon(), l.name, l.id)
        if selected!=None:
                combo.setCurrentIndex(combo.findData(selected))        
        
class frmSettings(QDialog, Ui_frmSettings):
    def __init__(self, mem, parent = None, name = None, modal = False):
        QDialog.__init__(self, parent)
        self.mem=mem
        self.setupUi(self)
        self.languages=SetLanguages()
        self.languages.qcombobox(self.cmbLanguage, self.mem.settings.value("frmSettings/language", "en"))            

    @pyqtSlot(str)      
    def on_cmbLanguage_currentIndexChanged(self, stri):        
        self.languages.selected=self.languages.find_by_name(stri)
        self.mem.change_language( self.languages.selected.id)
        self.retranslateUi(self)
        
    def on_buttonBox_accepted(self):
        self.mem.settings.setValue("frmSettings/language", self.languages.selected.id)
