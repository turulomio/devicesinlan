from PyQt6.QtCore import Qt,  QCoreApplication, QTranslator, QSettings
from PyQt6.QtWidgets import QTableWidgetItem, QMessageBox, QApplication
from PyQt6.QtGui import QColor,  QPixmap, QIcon
from importlib import import_module
from devicesinlan.libdevicesinlan import MemConsole
from sys import argv

import_module("devicesinlan.ui.devicesinlan_rc") #Loads resources in memory and works

## devicesinlan_gui Mem object
class MemGUI(MemConsole):
    def __init__(self):
        MemConsole.__init__(self)

    def run(self, args):
        self.args=args
    ## Sets QApplication Object to make a Qt application
    def setQApplication(self):
        self.app=QApplication(argv)
        
#        QDir.addSearchPath("images",  f"{self.BASE_DIR}/images")
        self.app.setQuitOnLastWindowClosed(True)
        self.app.setOrganizationName(self.name)
        self.app.setOrganizationDomain(self.name)
        self.app.setApplicationName(self.name)
        self.translator=QTranslator()
        self.settings=QSettings()

def DeviceType_qpixmap(o):
    if o.id==0:
        return QPixmap(":/devicesinlan.png")
    elif o.id==1:
        return QPixmap(":/devices/video-television.png")
    elif o.id==2:
        return QPixmap(":/devices/camera-photo.png")
    elif o.id==3:
        return QPixmap(":/devices/camera-web.png")
    elif o.id==4:
        return QPixmap(":/devices/computer-laptop.png")
    elif o.id==5:
        return QPixmap(":/devices/computer.png")
    elif o.id==6:
        return QPixmap(":/devices/modem.png")
    elif o.id==7:
        return QPixmap(":/devices/smartphone.png")
    elif o.id==8:
        return QPixmap(":/devices/printer.png")
    elif o.id==9:
        return QPixmap(":/devices/tablet.png")
    elif o.id==10:
        return QPixmap(":/devices/usb-wireless.png")
    return None
    
def DeviceType_qicon(o):
    ico = QIcon()
    ico.addPixmap(DeviceType_qpixmap(o), QIcon.Mode.Normal, QIcon.State.Off) 
    return ico

def DeviceManager_qtablewidget(set, table):
    set.order_by_ip() 
    ##HEADERS
    table.setColumnCount(5)
    table.setHorizontalHeaderItem(0, QTableWidgetItem(QCoreApplication.translate("devicesinlan","Type" )))
    table.setHorizontalHeaderItem(1, QTableWidgetItem(QCoreApplication.translate("devicesinlan","MAC" )))
    table.setHorizontalHeaderItem(2,  QTableWidgetItem(QCoreApplication.translate("devicesinlan","Alias" )))
    table.setHorizontalHeaderItem(3, QTableWidgetItem(QCoreApplication.translate("devicesinlan","Hardware" )))
    table.setHorizontalHeaderItem(4, QTableWidgetItem(QCoreApplication.translate("devicesinlan","IP" )))
    ##DATA 
    table.clearContents()   
    table.setRowCount(set.length())
    for rownumber, h in enumerate(set.arr):
        alias=""
        if h.alias!=None:
            alias=h.alias
        if h.ip==set.mem.interfaces.selected.ip():
            alias=QCoreApplication.translate("devicesinlan","This device")
        if h.type!=None:#Error en Windows
            table.setItem(rownumber, 0, qleft(h.type.name))
            table.item(rownumber,0).setIcon(DeviceType_qicon(h.type))
        else:
            table.setItem(rownumber, 0, qleft("None"))
        table.setItem(rownumber, 1, qleft(h.mac))
        table.setItem(rownumber, 2, qleft(alias))
        table.setItem(rownumber, 3, qleft(h.oui))
        table.setItem(rownumber, 4, qleft(h.ip))
        if alias!="":
            for i in range(0, table.columnCount()):
                if h.ip==set.mem.interfaces.selected.ip():
                    table.item(rownumber, i).setBackground( QColor(182, 182, 255))
                else:
                    table.item(rownumber, i).setBackground( QColor(182, 255, 182))

        else:
            for i in range(0, table.columnCount()):
                table.item(rownumber, i).setBackground( QColor(255, 182, 182))       

def DeviceManager_qtablewidget_devices_from_settings(set, table):
    set.order_by_alias() 
    ##HEADERS
    table.setColumnCount(4)
    table.setHorizontalHeaderItem(0, QTableWidgetItem(QCoreApplication.translate("devicesinlan","Type" )))
    table.setHorizontalHeaderItem(1, QTableWidgetItem(QCoreApplication.translate("devicesinlan","MAC" )))
    table.setHorizontalHeaderItem(2,  QTableWidgetItem(QCoreApplication.translate("devicesinlan","Alias" )))
    table.setHorizontalHeaderItem(3, QTableWidgetItem(QCoreApplication.translate("devicesinlan","Hardware" )))
    ##DATA 
    table.clearContents()   
    table.setRowCount(set.length())
    for rownumber, h in enumerate(set.arr):
        table.setItem(rownumber, 0, qleft(h.type.name))
        table.item(rownumber, 0).setIcon(DeviceType_qicon(h.type))
        table.setItem(rownumber, 1, qleft(h.mac))
        table.setItem(rownumber, 2, qleft(h.alias))
        table.setItem(rownumber, 3, qleft(h.oui))


def DeviceTypeManager_qcombobox(set, combo, selected=None):
    """Selected is id"""
    set.order_by_name()
    for l in set.arr:
        combo.addItem(DeviceType_qicon(l),  l.name, l.id)
    if selected==None:
        selected=0
    if selected!=None:
            combo.setCurrentIndex(combo.findData(selected))
    
def InterfaceManager_qcombobox(set, combo, selected=None):
    """Selected is id"""
    set.order_by_name()
    for l in set.arr:
        if l.name()==None:
            name="Interfaz sin nombre"
        else:
            name=l.name()
        combo.addItem(name, l.id())
    if selected!=None:
            combo.setCurrentIndex(combo.findData(selected))      
            
            
def Languages_qcombobox(combo,  mem, selected=None):
    """Selected is id"""
    for d in mem.lod_languages:
        ico=QIcon()
        ico.addPixmap(QPixmap(d["flag"]), QIcon.Mode.Normal, QIcon.State.Off) 
        combo.addItem(ico, d["name"], d["code"])
    if selected!=None:
            combo.setCurrentIndex(combo.findData(selected))        
            
def qbool(bool):
    """Prints bool and check. Is read only and enabled"""
    a=QTableWidgetItem()
    a.setFlags( Qt.ItemIsSelectable |  Qt.ItemIsEnabled )#Set no editable
    if bool:
        a.setCheckState(Qt.Checked);
        a.setText(QCoreApplication.translate("devicesinlan","True"))
    else:
        a.setCheckState(Qt.Unchecked);
        a.setText(QCoreApplication.translate("devicesinlan","False"))
    a.setTextAlignment(Qt.AlignmentFlag.AlignVCenter|Qt.AlignmentFlag.AlignCenter)
    return a
    
def qleft(string):
    a=QTableWidgetItem(str(string))
    a.setTextAlignment(Qt.AlignmentFlag.AlignVCenter|Qt.AlignmentFlag.AlignLeft)
    return a
    
def qmessagebox(message, type=QMessageBox.Icon.Information):
    m=QMessageBox()
    m.setWindowIcon(QIcon(":/devicesinlan.png"))
    m.setIcon(type)
    m.setText(str(message))
    m.exec() 
    
def qquestion(message, qicon ):
    """
        return can be QMessageBox.Yes, QMessageBox.No
    """
    m=QMessageBox()
    m.setWindowIcon(qicon)
    return m.question(None, "DevicesInLan", message, QMessageBox.Yes, QMessageBox.No)
        
