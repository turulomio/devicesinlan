# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/frmMain.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_frmMain(object):
    def setupUi(self, frmMain):
        frmMain.setObjectName("frmMain")
        frmMain.setWindowModality(QtCore.Qt.ApplicationModal)
        frmMain.resize(995, 568)
        frmMain.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        frmMain.setWindowTitle("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/devicesinlan.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        frmMain.setWindowIcon(icon)
        frmMain.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.wdg = QtWidgets.QWidget(frmMain)
        self.wdg.setObjectName("wdg")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.wdg)
        self.horizontalLayout.setObjectName("horizontalLayout")
        frmMain.setCentralWidget(self.wdg)
        self.menuBar = QtWidgets.QMenuBar(frmMain)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 995, 30))
        self.menuBar.setObjectName("menuBar")
        self.menuAyuda = QtWidgets.QMenu(self.menuBar)
        self.menuAyuda.setObjectName("menuAyuda")
        self.menuConfiguraci_n = QtWidgets.QMenu(self.menuBar)
        self.menuConfiguraci_n.setObjectName("menuConfiguraci_n")
        self.menuKnown_devices = QtWidgets.QMenu(self.menuBar)
        self.menuKnown_devices.setObjectName("menuKnown_devices")
        frmMain.setMenuBar(self.menuBar)
        self.toolBar = QtWidgets.QToolBar(frmMain)
        self.toolBar.setIconSize(QtCore.QSize(24, 24))
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.toolBar.setObjectName("toolBar")
        frmMain.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.status = QtWidgets.QStatusBar(frmMain)
        self.status.setObjectName("status")
        frmMain.setStatusBar(self.status)
        self.actionExit = QtWidgets.QAction(frmMain)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/exit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionExit.setIcon(icon1)
        self.actionExit.setObjectName("actionExit")
        self.actionAbout = QtWidgets.QAction(frmMain)
        self.actionAbout.setIcon(icon)
        self.actionAbout.setObjectName("actionAbout")
        self.actionSettings = QtWidgets.QAction(frmMain)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/configure.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSettings.setIcon(icon2)
        self.actionSettings.setObjectName("actionSettings")
        self.actionHelp = QtWidgets.QAction(frmMain)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/help.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionHelp.setIcon(icon3)
        self.actionHelp.setObjectName("actionHelp")
        self.actionScan = QtWidgets.QAction(frmMain)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/update.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionScan.setIcon(icon4)
        self.actionScan.setObjectName("actionScan")
        self.actionShowDatabase = QtWidgets.QAction(frmMain)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/database.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionShowDatabase.setIcon(icon5)
        self.actionShowDatabase.setObjectName("actionShowDatabase")
        self.actionResetDatabase = QtWidgets.QAction(frmMain)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(":/cancel.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionResetDatabase.setIcon(icon6)
        self.actionResetDatabase.setObjectName("actionResetDatabase")
        self.actionUpdates = QtWidgets.QAction(frmMain)
        self.actionUpdates.setIcon(icon4)
        self.actionUpdates.setObjectName("actionUpdates")
        self.actionListLoad = QtWidgets.QAction(frmMain)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(":/open.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionListLoad.setIcon(icon7)
        self.actionListLoad.setObjectName("actionListLoad")
        self.actionListSave = QtWidgets.QAction(frmMain)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(":/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionListSave.setIcon(icon8)
        self.actionListSave.setObjectName("actionListSave")
        self.menuAyuda.addAction(self.actionHelp)
        self.menuAyuda.addSeparator()
        self.menuAyuda.addAction(self.actionUpdates)
        self.menuAyuda.addAction(self.actionAbout)
        self.menuAyuda.addSeparator()
        self.menuAyuda.addAction(self.actionExit)
        self.menuConfiguraci_n.addAction(self.actionSettings)
        self.menuKnown_devices.addAction(self.actionScan)
        self.menuKnown_devices.addSeparator()
        self.menuKnown_devices.addAction(self.actionShowDatabase)
        self.menuKnown_devices.addSeparator()
        self.menuKnown_devices.addAction(self.actionListLoad)
        self.menuKnown_devices.addAction(self.actionListSave)
        self.menuKnown_devices.addSeparator()
        self.menuKnown_devices.addAction(self.actionResetDatabase)
        self.menuBar.addAction(self.menuKnown_devices.menuAction())
        self.menuBar.addAction(self.menuConfiguraci_n.menuAction())
        self.menuBar.addAction(self.menuAyuda.menuAction())
        self.toolBar.addAction(self.actionScan)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionShowDatabase)
        self.toolBar.addAction(self.actionSettings)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionAbout)
        self.toolBar.addAction(self.actionHelp)
        self.toolBar.addAction(self.actionExit)

        self.retranslateUi(frmMain)
        self.actionExit.triggered.connect(frmMain.close)
        QtCore.QMetaObject.connectSlotsByName(frmMain)

    def retranslateUi(self, frmMain):
        _translate = QtCore.QCoreApplication.translate
        self.menuAyuda.setTitle(_translate("frmMain", "&Help"))
        self.menuConfiguraci_n.setTitle(_translate("frmMain", "&Configuration"))
        self.menuKnown_devices.setTitle(_translate("frmMain", "&Devices"))
        self.toolBar.setWindowTitle(_translate("frmMain", "toolBar"))
        self.actionExit.setText(_translate("frmMain", "&Exit"))
        self.actionExit.setToolTip(_translate("frmMain", "Exit"))
        self.actionExit.setShortcut(_translate("frmMain", "Esc"))
        self.actionAbout.setText(_translate("frmMain", "&About"))
        self.actionSettings.setText(_translate("frmMain", "&Settings"))
        self.actionHelp.setText(_translate("frmMain", "&Help"))
        self.actionHelp.setToolTip(_translate("frmMain", "Muestra la ayuda del juego"))
        self.actionHelp.setShortcut(_translate("frmMain", "F1"))
        self.actionScan.setText(_translate("frmMain", "&New scan"))
        self.actionScan.setToolTip(_translate("frmMain", "New scan"))
        self.actionShowDatabase.setText(_translate("frmMain", "Show &devices database"))
        self.actionShowDatabase.setToolTip(_translate("frmMain", "Show devices database"))
        self.actionResetDatabase.setText(_translate("frmMain", "&Reset database"))
        self.actionResetDatabase.setToolTip(_translate("frmMain", "Reset database"))
        self.actionUpdates.setText(_translate("frmMain", "&Check for updates"))
        self.actionUpdates.setToolTip(_translate("frmMain", "Check for updates"))
        self.actionListLoad.setText(_translate("frmMain", "&Load devices list"))
        self.actionListLoad.setToolTip(_translate("frmMain", "Load devices list"))
        self.actionListSave.setText(_translate("frmMain", "&Save devices list"))
        self.actionListSave.setToolTip(_translate("frmMain", "Save devices list"))

import devicesinlan_rc