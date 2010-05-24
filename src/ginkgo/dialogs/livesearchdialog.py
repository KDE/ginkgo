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
from ginkgo.views.resourcestable import ResourcesTable
from ginkgo.dao import datamanager
from ginkgo.views.resourcesbytypetable import ResourcesByTypeTable

class LiveSearchDialog(QDialog):

    def __init__(self, parent=None, mainWindow=None, nepomukType=None, excludeList=None):
        super(LiveSearchDialog, self).__init__(parent)
        self.mainWindow = mainWindow
        self.nepomukType = nepomukType
        self.excludeList = excludeList
        self.setupUi(self)
        self.validate()


    def on_input_textEdited(self, text):
        input = str(self.input.text()).strip()
        if input and len(input) > 0:
            #recreate model, otherwise items keep being added to the previous one if the previous query has not finished
            #while the user updates the input text
            #count = self.matchingItems.table.model().rowCount(QModelIndex())
            self.matchingItems.installModels()
            #self.matchingItems.table.rowCountChanged(count, 0)
            datamanager.findResourcesByLabel(input, self.matchingItems.model.queryNextReadySlot, self.matchingItems.queryFinishedSlot, self.matchingItems)
        
        #self.validate()
        

    def validate(self):
        #TODO: check that text is not (\*])* (regexp)
        #self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(not self.input.text().isEmpty())
        #l = len(self.matchingItems.table.model().sourceModel().resources)
        #flag = len(self.matchingItems.selectedResources()) == 1
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        

    def selectedResource(self):
        if len(self.matchingItems.selectedResources()) > 0:
            return self.matchingItems.selectedResources()[0]
        return None
    
    def selectedResources(self):
        if len(self.matchingItems.selectedResources()) > 0:
            return self.matchingItems.selectedResources()
        return None
    

    def accept(self):
        
        QDialog.accept(self)


    def sizeHint(self):
        return QSize(450, 300)

    def setupUi(self, dialog):
        dialog.setObjectName("dialog")
        self.gridlayout = QGridLayout(dialog)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        
        label = QLabel(dialog)
        label.setText(i18n("&Name:"))
        self.gridlayout.addWidget(label, 0, 0, 1, 1)
        self.input = QLineEdit(dialog)
        self.input.setObjectName("input")
        self.gridlayout.addWidget(self.input, 1, 0, 1, 1)
        label.setBuddy(self.input)
        
        if self.nepomukType:
            self.matchingItems = ResourcesByTypeTable(mainWindow=dialog.mainWindow, nepomukType=self.nepomukType, dialog=self)
            
        else:
            self.matchingItems = ResourcesTable(mainWindow=dialog.mainWindow, dialog=self)
            self.matchingItems.table.setSelectionMode(QTableWidget.SingleSelection)
            
        label = QLabel(dialog)
        label.setText(i18n("Matching items:"))
        
        self.gridlayout.addWidget(label, 2, 0, 1, 1)
        self.gridlayout.addWidget(self.matchingItems, 3, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(dialog)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.NoButton | QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridlayout.addWidget(self.buttonBox, 4, 0, 1, 1)

        if self.nepomukType:
            dialog.setWindowTitle(i18n("Link to..."))
        else:
            dialog.setWindowTitle(i18n("Open resource"))

        self.buttonBox.accepted.connect(dialog.accept)
        self.buttonBox.rejected.connect(dialog.reject)
        
        QMetaObject.connectSlotsByName(dialog)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    form = LiveSearchDialog(None)
    form.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
    form.show()
    
    app.exec_()

