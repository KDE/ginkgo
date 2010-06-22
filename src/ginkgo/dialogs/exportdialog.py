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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.soprano import Soprano
from PyKDE4.nepomuk import Nepomuk
from PyKDE4.kdecore import i18n
from PyKDE4.kdeui import KIcon
from ginkgo.dao import datamanager
from ginkgo.serializer import BIBTEX, RDF_N3, RDF_XML, CUSTOM_EXPORT


class ExportDialog(QDialog):

    def __init__(self, parent=None, mainWindow=None):
        super(ExportDialog, self).__init__(parent)
        self.mainWindow = mainWindow
        self.title = "Export"
            
        self.setupUi(self)
        self.destinationFileInput.setFocus(Qt.OtherFocusReason)
        self.validate()

    def validate(self):
        #TODO: check that text is not (\*])* (regexp)
        #self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(not self.input.text().isEmpty())
        #l = len(self.matchingItems.table.model().sourceModel().resources)
        #flag = len(self.matchingItems.selectedResources()) == 1
        if len(self.destinationFileInput.text()) > 0:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        
    def onDestinationFileInputEdited(self, text):
        self.validate()

        
    def onFormatChanged(self):
        action = self.sender()
        idx = self.formats.currentIndex()
        format = self.formats.itemData(idx).toString()
        if format == CUSTOM_EXPORT:
            self.templateField.setText("")
            self.templateField.setEnabled(True)
        else:
            self.templateField.setEnabled(False)
            
        if format == RDF_N3 or format == RDF_XML:
            self.templateField.setText("DefaultExportTemplate")
        elif format == BIBTEX:
            self.templateField.setText("BibtexTemplate")
    
    def getDestinationFilePath(self):
        return unicode(self.destinationFileInput.text()).strip()
    
    def getExportTemplateName(self):
        templateName = unicode(self.templateField.text()).strip()
        return templateName 
        
    
    def selectExportFile(self):
        path = QFileInfo(".").path()
        #TODO: create a QFileDialog instance and set appropriate button labels ("Ok" instead of "Open")
        fpath = QFileDialog.getOpenFileName(self, i18n("Export to File"))
        self.destinationFileInput.setText(fpath)
        return fpath
        
    
    def accept(self):
        QDialog.accept(self)

#    def sizeHint(self):
#        return QSize(450, 300)

    def setupUi(self, dialog):
        gbox = QGridLayout(dialog)

        
        label = QLabel(dialog)
        label.setText(i18n("&Destination file:"))
        self.destinationFileInput = QLineEdit(dialog)
        self.destinationFileInput.setText("/home/arkub/tmp/out.rdf")
        self.destinationFileInput.textChanged.connect(self.onDestinationFileInputEdited)
        
        label.setBuddy(self.destinationFileInput)
        browseButton = QPushButton(dialog)
        browseButton.setText(i18n("Browse..."))
        browseButton.clicked.connect(self.selectExportFile)
        
        gbox.addWidget(label, 0, 0, 1, 1)
        gbox.addWidget(self.destinationFileInput, 0, 1, 1, 1)
        gbox.addWidget(browseButton, 0, 2, 1, 1)
        
        label = QLabel(dialog)
        label.setText(i18n("&Format:"))
        self.formats = QComboBox(dialog)
        self.formats.addItem("RDF/XML", RDF_XML)
        self.formats.addItem("RDF/N3", RDF_N3)
        self.formats.addItem("BibTeX", BIBTEX)
        self.formats.addItem(i18n("Custom"), CUSTOM_EXPORT)
        self.formats.activated.connect(self.onFormatChanged)
        label.setBuddy(self.formats)
        gbox.addWidget(label, 1, 0, 1, 1)
        gbox.addWidget(self.formats, 1, 1, 1, 2)
        
        label = QLabel(dialog)
        label.setText(i18n("&Template:"))
        self.templateField = QLineEdit(dialog)
        self.templateField.setEnabled(False)
        label.setBuddy(self.templateField)
        self.templateField.setText("DefaultExportTemplate")
        self.templateField.setText("BibtexTemplate")
        
        gbox.addWidget(label, 2, 0, 1, 1)
        gbox.addWidget(self.templateField, 2, 1, 1, 2)
        
        
        self.buttonBox = QDialogButtonBox(dialog)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.NoButton | QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        gbox.addWidget(self.buttonBox, 3, 0, 2, 3)

        dialog.setWindowTitle(i18n(self.title))

        self.buttonBox.accepted.connect(dialog.accept)
        self.buttonBox.rejected.connect(dialog.reject)
        
        self.formats.setCurrentIndex(2)
        
        QMetaObject.connectSlotsByName(dialog)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    form = ExportDialog(None)
    form.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))
    form.show()
    
    app.exec_()

