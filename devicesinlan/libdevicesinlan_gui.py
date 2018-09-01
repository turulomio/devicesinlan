from PyQt5.QtCore import Qt,  QCoreApplication
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox
from PyQt5.QtGui import QColor,  QPixmap, QIcon


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
    ico.addPixmap(DeviceType_qpixmap(o), QIcon.Normal, QIcon.Off) 
    return ico

def SetDevices_qtablewidget(set, table):
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

def SetDevices_qtablewidget_devices_from_settings(set, table):
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


def SetDeviceTypes_qcombobox(set, combo, selected=None):
    """Selected is id"""
    set.order_by_name()
    for l in set.arr:
        combo.addItem(DeviceType_qicon(l),  l.name, l.id)
    if selected==None:
        selected=0
    if selected!=None:
            combo.setCurrentIndex(combo.findData(selected))
    
def SetInterfaces_qcombobox(set, combo, selected=None):
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
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignCenter)
    return a
    
def qleft(string):
    a=QTableWidgetItem(str(string))
    a.setTextAlignment(Qt.AlignVCenter|Qt.AlignLeft)
    return a
    
def qmessagebox(message, type=QMessageBox.Information):
    m=QMessageBox()
    m.setWindowIcon(QIcon(":/devicesinlan.png"))
    m.setIcon(type)
    m.setText(str(message))
    m.exec_() 
    
def qquestion(message, qicon ):
    """
        return can be QMessageBox.Yes, QMessageBox.No
    """
    m=QMessageBox()
    m.setWindowIcon(qicon)
    return m.question(None, "DevicesInLan", message, QMessageBox.Yes, QMessageBox.No)
        
