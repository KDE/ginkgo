# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newpersondialog.ui'
#
# Created: Sat May  8 19:31:29 2010
#      by: PyQt4 UI code generator 4.7.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_NewPersonDialog(object):
    def setupUi(self, NewPersonDialog):
        NewPersonDialog.setObjectName("NewPersonDialog")
        NewPersonDialog.resize(308, 156)
        self.vboxlayout = QtGui.QVBoxLayout(NewPersonDialog)
        self.vboxlayout.setObjectName("vboxlayout")
        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setObjectName("vboxlayout1")
        self.gridlayout = QtGui.QGridLayout()
        self.gridlayout.setObjectName("gridlayout")
        self.label_2 = QtGui.QLabel(NewPersonDialog)
        self.label_2.setObjectName("label_2")
        self.gridlayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.label_4 = QtGui.QLabel(NewPersonDialog)
        self.label_4.setObjectName("label_4")
        self.gridlayout.addWidget(self.label_4, 1, 0, 1, 1)
        self.lineEdit = QtGui.QLineEdit(NewPersonDialog)
        self.lineEdit.setObjectName("lineEdit")
        self.gridlayout.addWidget(self.lineEdit, 0, 1, 1, 1)
        self.lineEdit_2 = QtGui.QLineEdit(NewPersonDialog)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridlayout.addWidget(self.lineEdit_2, 1, 1, 1, 1)
        self.vboxlayout1.addLayout(self.gridlayout)
        self.buttonBox = QtGui.QDialogButtonBox(NewPersonDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.vboxlayout1.addWidget(self.buttonBox)
        self.vboxlayout.addLayout(self.vboxlayout1)

        self.retranslateUi(NewPersonDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), NewPersonDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), NewPersonDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(NewPersonDialog)

    def retranslateUi(self, NewPersonDialog):
        NewPersonDialog.setWindowTitle(QtGui.QApplication.translate("NewPersonDialog", "New Person", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("NewPersonDialog", "Name", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("NewPersonDialog", "E-mail", None, QtGui.QApplication.UnicodeUTF8))

