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
from ginkgo.dao import datamanager
from PyKDE4.soprano import Soprano
from ginkgo.ontologies import NFO, NIE, PIMO, NCO
from os import listdir
from os.path import isfile, isdir, expanduser, join
from ginkgo.editors.resourceeditor import ResourceEditor, ResourceEditorUi
from PyKDE4.kdecore import i18n

class FileEditor(ResourceEditor):
    def __init__(self, mainWindow=False, resource=None, nepomukType=None):
        super(FileEditor, self).__init__(mainWindow=mainWindow, resource=resource, nepomukType=nepomukType)
        self.defaultIcon = ":/document-large"
        
        self.ui = FileEditorUi(self)
    

    def openFile(self):
        if self.resource and self.resource.uri():
            self.mainWindow.openResourceExternally(self.resource.uri(), True)
            

class FileEditorUi(ResourceEditorUi):
    
    def createMainPropertiesWidget(self, parent):
        propertiesWidget = QWidget(parent)

        self.vboxl = QVBoxLayout(propertiesWidget)
#        self.gridlayout.setMargin(9)
#        self.gridlayout.setSpacing(6)

        button = QPushButton(propertiesWidget)
        button.setText(i18n("Open"))
        button.clicked.connect(self.editor.openFile)

        self.vboxl.addWidget(button)
        
        spacerItem = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.vboxl.addItem(spacerItem)
        
        return propertiesWidget
    
    def updateFields(self):
        super(FileEditorUi, self).updateFields()
        if self.editor.resource:
            label = self.editor.resource.property(Soprano.Vocabulary.NAO.prefLabel()).toString()
            if not label or len(label) == 0:
                self.label.setText(self.editor.resource.property(NFO.fileName).toString())
    

