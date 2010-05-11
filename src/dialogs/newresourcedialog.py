# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newresourcedialog.ui'
#
# Created: Sat May  8 19:31:30 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_NewResourceDialog(object):
    def setupUi(self, NewResourceDialog):
        NewResourceDialog.setObjectName("NewResourceDialog")
        NewResourceDialog.resize(308, 156)
        self.vboxlayout = QtGui.QVBoxLayout(NewResourceDialog)
        self.vboxlayout.setObjectName("vboxlayout")
        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setObjectName("vboxlayout1")
        self.gridlayout = QtGui.QGridLayout()
        self.gridlayout.setObjectName("gridlayout")
        self.label_2 = QtGui.QLabel(NewResourceDialog)
        self.label_2.setObjectName("label_2")
        self.gridlayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.lineEdit = QtGui.QLineEdit(NewResourceDialog)
        self.lineEdit.setObjectName("lineEdit")
        self.gridlayout.addWidget(self.lineEdit, 0, 1, 1, 1)
        self.vboxlayout1.addLayout(self.gridlayout)
        self.buttonBox = QtGui.QDialogButtonBox(NewResourceDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.vboxlayout1.addWidget(self.buttonBox)
        self.vboxlayout.addLayout(self.vboxlayout1)

        self.retranslateUi(NewResourceDialog)
        QtCore.QMetaObject.connectSlotsByName(NewResourceDialog)

    def retranslateUi(self, NewResourceDialog):
        NewResourceDialog.setWindowTitle(QtGui.QApplication.translate("NewResourceDialog", "New Resource", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("NewResourceDialog", "Name", None, QtGui.QApplication.UnicodeUTF8))

