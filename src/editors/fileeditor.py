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
from PyQt4 import Qsci, QtGui, QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from dao import datamanager
from ontologies import NFO, NIE, PIMO, NCO
from os import listdir
from os.path import isfile, isdir, expanduser, join
from editors.resourceeditor import ResourceEditor, ResourceEditorUi
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

        self.gridlayout = QGridLayout(propertiesWidget)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        
        nameBox = QGroupBox(i18n("Name"))
        #self.name_label = QLabel(propertiesWidget)
        #self.name_label.setObjectName("name_label")
        #self.gridlayout.addWidget(self.name_label, 1, 0, 1, 1)
        self.name = QLineEdit(propertiesWidget)
        self.name.setObjectName("name")
        vbox = QVBoxLayout(nameBox)
        vbox.addWidget(self.name)
        
        button = QPushButton(propertiesWidget)
        button.setText(i18n("Open"))
        button.clicked.connect(self.editor.openFile)
        vbox.addWidget(button)

        self.gridlayout.addWidget(nameBox, 1, 0, 1, 2)
        #self.name_label.setBuddy(self.name)
  
        
        spacerItem = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 2, 0, 1, 1)
        
        return propertiesWidget

    
    
    

