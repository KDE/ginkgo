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
from dao import datamanager
from ontologies import NFO, NIE, PIMO, NCO
from editors.resourceeditor import ResourceEditor, ResourceEditorUi
from PyKDE4.kdecore import i18n


class ClassEditor(ResourceEditor):
    def __init__(self, mainWindow=False, resource=None, superTypeResource=None, nepomukType=None):
        super(ClassEditor, self).__init__(mainWindow=mainWindow, resource=resource, nepomukType=Soprano.Vocabulary.RDFS.Class())
        self.defaultIcon = ""
        self.superTypeResource = superTypeResource
        self.ui = ClassEditorUi(self)
    
            
    def save(self):
        
        super(ClassEditor, self).save()
        
        if self.superTypeResource:
            self.resource.addProperty(Soprano.Vocabulary.RDFS.subClassOf(), Nepomuk.Variant(self.superTypeResource))
    

        pimoThingClass = Nepomuk.Resource(PIMO.Thing)
        self.resource.addProperty(Soprano.Vocabulary.RDFS.subClassOf(), Nepomuk.Variant(pimoThingClass))
        resourceClass = Nepomuk.Resource(Soprano.Vocabulary.RDFS.Class())
        self.resource.addProperty(Soprano.Vocabulary.RDFS.subClassOf(), Nepomuk.Variant(resourceClass))
        
            

class ClassEditorUi(ResourceEditorUi):
    
    def createMainPropertiesWidget(self, parent):

        propertiesWidget = QWidget(parent)

        self.gridlayout = QGridLayout(propertiesWidget)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        
        #self.gridlayout.setColumnStretch(0, 1)
        #self.gridlayout.setColumnStretch(1, 20)
 
#        self.firstname_label = QLabel(propertiesWidget)
#        self.firstname_label.setObjectName("firstname_label")
#        self.firstname_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
#        self.gridlayout.addWidget(self.firstname_label, 0, 0, 1, 1)
        self.name = QLineEdit(propertiesWidget)
        self.name.setObjectName("name")
        self.name.setMinimumWidth(180)
        
        self.name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
#        self.firstname_label.setBuddy(self.firstname)
        fnameBox = QGroupBox(i18n("Type Name"))
        #self.name_label = QLabel(propertiesWidget)
        #self.name_label.setObjectName("name_label")
        #self.gridlayout.addWidget(self.name_label, 1, 0, 1, 1)
        vbox = QVBoxLayout(fnameBox)
        vbox.addWidget(self.name)
        self.gridlayout.addWidget(fnameBox, 0, 0, 1, 1)
       
        spacerItem = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 4, 0, 1, 1)

        return propertiesWidget

    def updateFields(self):
        pass
    
    def retranslateUi(self):
        super(ClassEditorUi, self).retranslateUi()
