# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'devicesinlan/ui/frmDeviceCRUD.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_frmDeviceCRUD(object):
    def setupUi(self, frmDeviceCRUD):
        frmDeviceCRUD.setObjectName("frmDeviceCRUD")
        frmDeviceCRUD.resize(539, 260)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/configure.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        frmDeviceCRUD.setWindowIcon(icon)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(frmDeviceCRUD)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.lblTitle = QtWidgets.QLabel(frmDeviceCRUD)
        self.lblTitle.setMinimumSize(QtCore.QSize(0, 30))
        self.lblTitle.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.lblTitle.setFont(font)
        self.lblTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.lblTitle.setObjectName("lblTitle")
        self.verticalLayout.addWidget(self.lblTitle)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.lblPixmap = QtWidgets.QLabel(frmDeviceCRUD)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblPixmap.sizePolicy().hasHeightForWidth())
        self.lblPixmap.setSizePolicy(sizePolicy)
        self.lblPixmap.setMinimumSize(QtCore.QSize(48, 48))
        self.lblPixmap.setMaximumSize(QtCore.QSize(48, 48))
        self.lblPixmap.setPixmap(QtGui.QPixmap(":/configure.png"))
        self.lblPixmap.setScaledContents(True)
        self.lblPixmap.setAlignment(QtCore.Qt.AlignCenter)
        self.lblPixmap.setObjectName("lblPixmap")
        self.horizontalLayout_2.addWidget(self.lblPixmap)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(frmDeviceCRUD)
        self.label_2.setMinimumSize(QtCore.QSize(150, 0))
        self.label_2.setMaximumSize(QtCore.QSize(150, 16777215))
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.cmbType = QtWidgets.QComboBox(frmDeviceCRUD)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbType.sizePolicy().hasHeightForWidth())
        self.cmbType.setSizePolicy(sizePolicy)
        self.cmbType.setObjectName("cmbType")
        self.horizontalLayout.addWidget(self.cmbType)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label = QtWidgets.QLabel(frmDeviceCRUD)
        self.label.setMinimumSize(QtCore.QSize(150, 0))
        self.label.setMaximumSize(QtCore.QSize(150, 16777215))
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.txtAlias = QtWidgets.QLineEdit(frmDeviceCRUD)
        self.txtAlias.setObjectName("txtAlias")
        self.horizontalLayout_3.addWidget(self.txtAlias)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_4 = QtWidgets.QLabel(frmDeviceCRUD)
        self.label_4.setMinimumSize(QtCore.QSize(150, 0))
        self.label_4.setMaximumSize(QtCore.QSize(150, 16777215))
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_5.addWidget(self.label_4)
        self.txtMAC = QtWidgets.QLineEdit(frmDeviceCRUD)
        self.txtMAC.setReadOnly(True)
        self.txtMAC.setObjectName("txtMAC")
        self.horizontalLayout_5.addWidget(self.txtMAC)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.buttonBox = QtWidgets.QDialogButtonBox(frmDeviceCRUD)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(frmDeviceCRUD)
        self.buttonBox.accepted.connect(frmDeviceCRUD.accept) # type: ignore
        self.buttonBox.rejected.connect(frmDeviceCRUD.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(frmDeviceCRUD)

    def retranslateUi(self, frmDeviceCRUD):
        _translate = QtCore.QCoreApplication.translate
        self.label_2.setText(_translate("frmDeviceCRUD", "Select a type"))
        self.label.setText(_translate("frmDeviceCRUD", "Device alias"))
        self.label_4.setText(_translate("frmDeviceCRUD", "Interface MAC"))
import devicesinlan.images.devicesinlan_rc
