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

from PyKDE4.nepomuk import Nepomuk
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.soprano import Soprano
from ginkgo.dao import datamanager
from ginkgo.ontologies import NFO, NIE, PIMO, NCO
from ginkgo.editors.resourceeditor import ResourceEditor, ResourceEditorUi
from PyKDE4.kdecore import i18n
from ginkgo.views.typepropertiestable import TypePropertiesTable
from ginkgo.dialogs.typechooserdialog import TypeChooserDialog

class PropertyEditor(ResourceEditor):
    #nepomukType is needed by Ginkgo call: newEditor = getClass(className)(mainWindow=self, resource=resource, nepomukType=type)
    #TODO: see how to make this argument optional in editors
    def __init__(self, mainWindow=False, resource=None, domainUri=None, nepomukType=None):
        super(PropertyEditor, self).__init__(mainWindow=mainWindow, resource=resource, nepomukType=Soprano.Vocabulary.RDF.Property())
        self.defaultIcon = ""
        self.domainUri = domainUri
        self.ui = PropertyEditorUi(self)
            
    def save(self):
        
        #don't call the superclass save method this classes or not standard resource types
        self.setCursor(Qt.WaitCursor)
        
        if self.resource is None:
            self.resource = datamanager.createPimoProperty(self.ui.label.text(), self.domainUri)
        
        super(PropertyEditor, self).save()
        self.unsetCursor()
        
    def updateDomain(self):
        #save the resource to create it if it doesn't exist yet
        if not self.resource:
            self.save()

        domainUrl = QUrl(self.resource.property(Soprano.Vocabulary.RDFS.domain()).toString())
        
        dialog = TypeChooserDialog(mainWindow=self.mainWindow, typesUris=[domainUrl])
        if dialog.exec_():
            selection = dialog.selectedResources()
            #add the general rdf:Resource type
            if len(selection) == 1:
                self.setCursor(Qt.WaitCursor)
                res = selection[0]
                self.resource.setProperty(Soprano.Vocabulary.RDFS.domain(), Nepomuk.Variant(res.resourceUri()))
                self.ui.updateFields()
                self.unsetCursor()

    


    def rangeLiteralChanged(self):
        if self.ui.isLiteral.isChecked():
            self.ui.stack.setCurrentWidget(self.ui.literalWidget)
        else:
            self.ui.stack.setCurrentWidget(self.ui.rangeClassWidget)

    def updateRangeType(self):
        pass    
            
    def updateRangeLiteral(self):
        idx = self.ui.literalBox.currentIndex()
        data = self.ui.literalBox.itemData(idx)
        literalTypeUri = QUrl(data.toString())
        self.mainWindow.setCursor(Qt.WaitCursor)
        self.resource.setProperty(Soprano.Vocabulary.RDFS.range(), Nepomuk.Variant(literalTypeUri))
        self.ui.updateFields()
        self.mainWindow.unsetCursor()
        #self.literalType = key
        

class PropertyEditorUi(ResourceEditorUi):
    
    def setupUi(self):
        super(PropertyEditorUi, self).setupUi()
        
    def createMainPropertiesWidget(self, parent):

        propertiesWidget = QWidget(parent)

        self.vboxl = QVBoxLayout(propertiesWidget)
        
        self.domain = QLineEdit(propertiesWidget)
        self.domain.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.domain.setEnabled(False)

        dbox = QGroupBox(i18n("Domain"))
        vbox = QVBoxLayout(dbox)
        vbox.addWidget(self.domain)
        button = QPushButton(propertiesWidget)
        button.setText(i18n("Change"))
        button.clicked.connect(self.editor.updateDomain)
        vbox.addWidget(button)
        
        self.vboxl.addWidget(dbox)
        
        
        rbox = QGroupBox(i18n("Range"))
        vbox = QVBoxLayout(rbox)
        self.isLiteral = QCheckBox(i18n("literal"))
        self.isLiteral.setChecked(True)
        self.isLiteral.clicked.connect(self.editor.rangeLiteralChanged)
        vbox.addWidget(self.isLiteral)
        
        rangeWidget = QWidget()
        self.stack = QStackedLayout(rangeWidget)
        
        self.literalWidget = QWidget()
        vbox1 = QVBoxLayout(self.literalWidget) 
        self.literalBox = QComboBox()
        for literal in ["", "boolean", "integer", "dateTime", "date", "duration", "float",  "int", "nonNegativeInteger", "string"]:
            self.literalBox.addItem(i18n(literal), QVariant("http://www.w3.org/2001/XMLSchema#"+literal))
        self.literalBox.addItem(i18n("Literal"), QVariant("http://www.w3.org/2000/01/rdf-schema#Literal"))
        vbox1.addWidget(self.literalBox)
        self.literalBox.activated.connect(self.editor.updateRangeLiteral)
        
        spacerItem = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding)
        vbox1.addItem(spacerItem)
        
        self.stack.addWidget(self.literalWidget)
        
        self.rangeClassWidget = QWidget()
        vbox1 = QVBoxLayout(self.rangeClassWidget)
        self.range = QLineEdit(propertiesWidget)
        self.range.setEnabled(False)
        vbox1.addWidget(self.range)

        self.rangeChangeButton = QPushButton(propertiesWidget)
        self.rangeChangeButton.setText(i18n("Change"))
        self.rangeChangeButton.clicked.connect(self.editor.updateRangeType)
        vbox1.addWidget(self.rangeChangeButton)
        
        self.stack.addWidget(self.rangeClassWidget)
        
        vbox.addWidget(rangeWidget)
        spacerItem = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding)
        vbox.addItem(spacerItem)

        self.vboxl.addWidget(rbox)
        
        spacerItem = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.vboxl.addItem(spacerItem)

        return propertiesWidget
    
    def updateFields(self):
        super(PropertyEditorUi, self).updateFields()
        if self.editor.resource:
            domainUri = QUrl(self.editor.resource.property(Soprano.Vocabulary.RDFS.domain()).toString())
            domainResource = Nepomuk.Resource(domainUri)
            self.domain.setText(domainResource.genericLabel())
            
            rangeUri = QUrl(self.editor.resource.property(Soprano.Vocabulary.RDFS.range()).toString())
            if str(rangeUri.toString()).find("http://www.w3.org/2001/XMLSchema") == 0:
                self.isLiteral.setChecked(True)
                idx = self.literalBox.findData(QVariant(rangeUri.toString()))
                if idx > 0:
                    self.literalBox.setCurrentIndex(idx)
                                         
            else:
                self.isLiteral.setChecked(False)
                rangeResource = Nepomuk.Resource(rangeUri)
                self.range.setText(rangeResource.genericLabel())
                self.stack.setCurrentWidget(self.rangeClassWidget)
                
                