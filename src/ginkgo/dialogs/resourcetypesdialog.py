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

from PyQt4.QtCore import Qt, SIGNAL, QObject, QMetaObject, QString, QSize, QModelIndex
from PyQt4.QtGui import QGridLayout, QLabel, QLineEdit, QTextEdit, QDialogButtonBox, QApplication, QDialog, QWidget, QSizePolicy, QTableWidget
from PyKDE4.kdecore import i18n
from PyKDE4.nepomuk import Nepomuk
from ginkgo.views.resourcestable import ResourcesTable
from ginkgo.dao import datamanager
from ginkgo.views.resourcetypestable import ResourceTypesTable


class ResourceTypesDialog(QDialog):

    def __init__(self, parent=None, mainWindow=None, resource=None):
        
        super(ResourceTypesDialog, self).__init__(parent)
        self.mainWindow = mainWindow
        self.mainWindow.setCursor(Qt.WaitCursor)
        self.resource = resource
        self.setupUi(self)
        self.validate()
        self.mainWindow.unsetCursor()

    def validate(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        

    def selectedResources(self):
        if len(self.table.selectedObjects()) > 0:
            return self.table.selectedObjects()
        return None
    

    def accept(self):
        
        QDialog.accept(self)


    def sizeHint(self):
        return QSize(600, 300)

    def setupUi(self, dialog):
        dialog.setObjectName("dialog")
        self.gridlayout = QGridLayout(dialog)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        
        self.table = ResourceTypesTable(mainWindow=dialog.mainWindow, resource=self.resource, dialog=self)
            
        self.gridlayout.addWidget(self.table, 0, 0, 1, 1)
            
        self.buttonBox = QDialogButtonBox(dialog)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.NoButton | QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridlayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.buttonBox.accepted.connect(dialog.accept)
        self.buttonBox.rejected.connect(dialog.reject)
        
        
        self.setWindowTitle(i18n("Select type(s)"))
        QMetaObject.connectSlotsByName(dialog)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    resource = Nepomuk.Resource("nepomuk:/res/ad17c07d-332f-4fc1-9363-476e0a951b43")

    form = ResourceTypesDialog(resource=resource)
    form.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
    form.show()
    
    app.exec_()

