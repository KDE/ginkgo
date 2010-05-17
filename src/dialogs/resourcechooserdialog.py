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

from PyQt4.QtCore import Qt, SIGNAL, QObject, QMetaObject, QString
from PyQt4.QtGui import QGridLayout, QLabel, QLineEdit, QTextEdit, QDialogButtonBox, QApplication, QDialog, QTableWidget
from PyKDE4 import nepomuk
from views.resourcestable import ResourcesTable
from views.resourcesbytypetable import ResourcesByTypeTable
from PyKDE4.kdecore import i18n

class ResourceChooserDialogUi(object):

    def setupUi(self, dialog, nepomukType=None, excludeList=None):
        
        self.dialog = dialog
        dialog.setObjectName("dialog")
        dialog.resize(500, 300)
        self.gridlayout = QGridLayout(dialog)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.table = ResourcesByTypeTable(mainWindow=dialog.parent(), nepomukType=nepomukType, dialogMode=True, excludeList=excludeList)
        self.table.table.setColumnWidth(0,250)
        
        self.gridlayout.addWidget(self.table, 0, 0, 1, 1)
      
        self.buttonBox = QDialogButtonBox(dialog)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.NoButton | QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridlayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(dialog)
      
        self.table.table.activated.connect(self.activated)
        
        self.buttonBox.accepted.connect(dialog.accept)
        self.buttonBox.rejected.connect(dialog.reject)
        QMetaObject.connectSlotsByName(dialog)
        
        #dialog.setTabOrder(self.firstname, self.yearSpinBox)
        #dialog.setTabOrder(self.yearSpinBox, self.minutesSpinBox)
        
    def activated(self, index):
        if index.isValid():
            self.dialog.accept()

    def retranslateUi(self, dialog):
        dialog.setWindowTitle(i18n("Link to..."))

class ResourceChooserDialog(QDialog, ResourceChooserDialogUi):

    def __init__(self, parent=None, nepomukType=None, excludeList=None):
        super(ResourceChooserDialog, self).__init__(parent)
        self.setupUi(self, nepomukType, excludeList)

    def accept(self):
        self.selection =  self.table.selectedResources()
        QDialog.accept(self)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    form = ResourceChooserDialog()
    form.show()
    app.exec_()

