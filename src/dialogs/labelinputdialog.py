#!/usr/bin/env python
# -*- coding: utf-8 -*-

## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE included in the packaging of
## this file. 
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
## See the NOTICE file distributed with this work for additional
## information regarding copyright ownership.

from PyQt4.QtCore import Qt, SIGNAL, QObject, QMetaObject, QString, QSize
from PyQt4.QtGui import QGridLayout, QLabel, QLineEdit, QTextEdit, QDialogButtonBox, QApplication, QDialog, QWidget, QSizePolicy

class LabelInputDialogUi(object):
    def setupUi(self, dialog):
        dialog.setObjectName("dialog")
        self.gridlayout = QGridLayout(dialog)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        
        self.label = QLabel(dialog)
        self.label.setObjectName("label")
        self.gridlayout.addWidget(self.label, 0, 0, 1, 1)
        self.input = QLineEdit(dialog)
        self.input.setObjectName("input")
        self.gridlayout.addWidget(self.input, 1, 0, 1, 1)
        self.label.setBuddy(self.input)

        self.buttonBox = QDialogButtonBox(dialog)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.NoButton | QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridlayout.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.retranslateUi(dialog)
        self.buttonBox.accepted.connect(dialog.accept)
        self.buttonBox.rejected.connect(dialog.reject)
        
        QMetaObject.connectSlotsByName(dialog)
        #dialog.setTabOrder(self.firstname, self.yearSpinBox)
        #dialog.setTabOrder(self.yearSpinBox, self.minutesSpinBox)
        
    def retranslateUi(self, dialog):
        dialog.setWindowTitle(QApplication.translate("LabelInputDialog", "Open Resource", None, QApplication.UnicodeUTF8))
        #self.acquiredDateEdit.setDisplayFormat(QApplication.translate("PersonEditDialog", "ddd MMM d, yyyy", None, QApplication.UnicodeUTF8))
        self.label.setText(QApplication.translate("LabelInputDialog", "&Name:", None, QApplication.UnicodeUTF8))

    

class LabelInputDialog(QDialog, LabelInputDialogUi):

    def __init__(self, parent=None):
        super(LabelInputDialog, self).__init__(parent)
        self.setupUi(self)
        self.validate()


    def on_input_textEdited(self, text):
        self.validate()
        

    def validate(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(not self.input.text().isEmpty())


    def accept(self):
        
        QDialog.accept(self)


    def sizeHint(self):
        return QSize(300, 30)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    form = LabelInputDialog(None)
    form.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum))
    form.show()
    
    app.exec_()

