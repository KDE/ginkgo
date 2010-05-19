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
from PyKDE4.kdeui import *
from PyKDE4.kdecore import i18n
from PyKDE4.soprano import Soprano 
from views.resourcestree import ResourcesTree, ResourcesTreeModel
from ontologies import PIMO


class TypesView(QWidget):

    def __init__(self, mainWindow=False):
        super(TypesView, self).__init__()
        self.mainWindow = mainWindow

        layout = QGridLayout(self)
        
        configWidget = QWidget(self)
        hbox = QHBoxLayout(configWidget)
        
        name = QLabel(i18n("Ontologies:"))
        hbox.addWidget(name)
        self.ontologies = QComboBox()
        self.ontologies.addItem("All")
        self.ontologies.addItem("PIMO")
        self.ontologies.setCurrentIndex(1)
        self.ontology = "PIMO"
        self.ontologies.activated.connect(self.update)
        
        hbox.addWidget(self.ontologies)
        
        
        actionData = [Soprano.Vocabulary.RDFS.Class(), i18n("&Type"), i18n("&Types"), "document-new", i18n("Create new type")]
        #self.createAction(type[1], getattr(self, "newResource"), None, type[3], type[4], type[0]))
        #action = self.mainWindow.createAction(actionData[1], self.mainWindow.newResource, None, actionData[3], actionData[4], actionData[0])
#        button = KPushButton()
#        button.setText(i18n("New type"))
        #button.setStyleSheet("border:none")
        #button.setIcon(KIcon("document-new"))
#        button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
#        button.clicked.connect(self.mainWindow.newType)
#        hbox.addWidget(button)
                         
        
        spacerItem = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hbox.addItem(spacerItem)
                
        layout.addWidget(configWidget, 0, 0, 1, 1)
        self.setCursor(Qt.WaitCursor)
        self.typesTree = ResourcesTree(mainWindow=self.mainWindow, makeActions=True)
        self.unsetCursor()
        
        layout.addWidget(self.typesTree, 1, 0, 30, 1)
        
        self.retranslateUi()
        self.updateFields()
        

    def updateFields(self):
        pass
            
    def retranslateUi(self):
        pass


    def update(self):
        key = self.ontologies.currentText()
        if key != self.ontology:
            self.mainWindow.setCursor(Qt.WaitCursor)
            model = ResourcesTreeModel(mainWindow=self.mainWindow)
            if key == "All":
                model.loadData(Soprano.Vocabulary.RDFS.Resource())
            else:
                model.loadData(PIMO.Thing)
            
            self.typesTree.tree.setModel(model)
            self.ontology = key
            self.mainWindow.unsetCursor()
        self.ontology = key
        
        
