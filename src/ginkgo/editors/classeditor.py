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


class ClassEditor(ResourceEditor):
    def __init__(self, mainWindow=False, resource=None, superClassUri=None, nepomukType=None):
        super(ClassEditor, self).__init__(mainWindow=mainWindow, resource=resource, nepomukType=Soprano.Vocabulary.RDFS.Class())
        self.defaultIcon = ""
        self.superClassUri = superClassUri
        self.ui = ClassEditorUi(self)
    
            
    def save(self):
        
        #don't call the superclass save method this classes or not standard resource types
        self.setCursor(Qt.WaitCursor)
        if self.resource is None:
            print self.superClassUri
            self.resource = datamanager.createPimoClass(self.superClassUri, self.ui.label.text())
        self.unsetCursor()

    def focus(self):
        self.ui.label.setFocus(Qt.OtherFocusReason)    

class ClassEditorUi(ResourceEditorUi):
    
#    def createMainPropertiesWidget(self, parent):
#
#        propertiesWidget = QWidget(parent)
#
#        self.gridlayout = QGridLayout(propertiesWidget)
#        self.gridlayout.setObjectName("gridlayout")
#        
#        self.name = QLineEdit(propertiesWidget)
#        self.name.setObjectName("name")
#        
#        self.name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
#        fnameBox = QGroupBox(i18n("Type Name"))
#        vbox = QVBoxLayout(fnameBox)
#        vbox.addWidget(self.name)
#        self.gridlayout.addWidget(fnameBox, 0, 0, 1, 1)
#       
#        spacerItem = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding)
#        self.gridlayout.addItem(spacerItem, 4, 0, 1, 1)
#
#        return propertiesWidget

#    def updateFields(self):
#        if self.editor.resource:
#            self.label.setText(self.editor.resource.genericLabel())
    
    pass
