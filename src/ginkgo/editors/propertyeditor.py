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
        self.unsetCursor()

    def focus(self):
        self.ui.label.setFocus(Qt.OtherFocusReason)    

class PropertyEditorUi(ResourceEditorUi):
    
    def setupUi(self):
        super(PropertyEditorUi, self).setupUi()
