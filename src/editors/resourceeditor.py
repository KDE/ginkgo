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

from editors.relationstable import RelationsTable
from editors.resourcepropertiestable import ResourcePropertiesTable
from PyKDE4.soprano import Soprano 
import os

def getClass( clazz ):
    parts = clazz.split('.')
    module = ".".join(parts[:-1])
    module = __import__( module )
    for comp in parts[1:]:
        module = getattr(module, comp)            
    return module


class ResourceEditor(QWidget):
    def __init__(self, mainWindow=False, resource=None, nepomukType=None):
        super(ResourceEditor, self).__init__()
        self.mainWindow = mainWindow
        self.defaultIcon = ":/nepomuk-large"
        self.resource = resource
        self.nepomukType = nepomukType
        
        if self.__class__ == getClass("editors.resourceeditor.ResourceEditor"):
            self.ui = ResourceEditorUi(self)
            

        

    def resourceIcon(self):
        if self.resource:
            return self.mainWindow.resourceIcon(self.resource, 64)
        elif self.nepomukType:
            return self.mainWindow.typeIcon(self.nepomukType, 64)   
        else:
            return KIcon(self.defaultIcon)

    def selectIcon(self):
        path = QFileInfo("~/").path()
        fname = QFileDialog.getOpenFileName(self, "Select Icon - Ginkgo", path, "Images (*.png *.jpg *.jpeg *.bmp)")
        
        #first save the resource to make sure it exists
        self.save()
        
        if fname and len(fname) > 0 and os.path.exists(fname):
            self.resource.setSymbols([fname])
            self.ui.iconButton.setIcon(KIcon(fname))

    def save(self):
        if self.resource is None:
            self.resource = self.mainWindow.createResource(self.ui.resourceLabel(), self.nepomukType)
        
        else:
            #TODO: remove an editor when the edited resource was deleted externally
            if len(self.resource.types()) == 0:
                self.resource = self.mainWindow.createResource(self.ui.resourceLabel(), self.nepomukType)      
        
        self.ui.relationsTable.setResource(self.resource)
        self.ui.propsTable.setResource(self.resource)
        
        #save generic properties
        self.resource.setLabel(self.ui.resourceLabel())
        self.resource.setDescription(self.ui.description.toPlainText())
                            
    def focus(self):
        self.ui.name.setFocus(Qt.OtherFocusReason)

class ResourceEditorUi(object):
    
    def __init__(self, editor):
        self.editor = editor
        self.setupUi()

    
    def setupUi(self):
        #create the card sheet on the left
        card = QWidget(self.editor)
        vlayout = QVBoxLayout(card)
        vlayout.addWidget(self.createIconWidget(card))
        vlayout.addWidget(self.createMainPropertiesWidget(card))
        
        #create the right pane: description + relations
        rightpane = QSplitter(self.editor)
        rightpane.setOrientation(Qt.Vertical)
        
        descriptionWidget = QWidget(rightpane)
        vboxlayout = QVBoxLayout(descriptionWidget)
        self.descriptionLabel = QLabel(descriptionWidget) 
        self.description = QTextEdit(self.editor)
        self.description.setTabChangesFocus(True)
        #self.description.setLineWrapMode(QTextEdit.NoWrap)
        self.description.setAcceptRichText(False)
        self.description.setObjectName("Notes")
        self.description.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.descriptionLabel.setBuddy(self.description)
        vboxlayout.addWidget(self.descriptionLabel)
        vboxlayout.addWidget(self.description)
        
        relpropWidget = KTabWidget(rightpane)
        #vboxlayout = QVBoxLayout(relationsWidget)
        #self.relationsLabel = QLabel(relationsWidget)
        
        self.relationsTable = RelationsTable(mainWindow=self.editor.mainWindow, resource=self.editor.resource)
        self.propsTable = ResourcePropertiesTable(mainWindow=self.editor.mainWindow, resource=self.editor.resource)
        
        relpropWidget.addTab(self.relationsTable , "Relations")
        relpropWidget.addTab(self.propsTable, "Properties")
        
#        self.relationsLabel.setBuddy(relationsTable)
#        vboxlayout.addWidget(self.relationsLabel)
#        vboxlayout.addWidget(relationsTable)
        
        rightpane.addWidget(descriptionWidget)
        rightpane.addWidget(relpropWidget)
        rightpane.setSizes([20,400])
        
        #self.tabs.addTab(self.description, "Description")
        #self.tabs.setTabPosition(QTabWidget.North)
        
        splitter = QSplitter(self.editor)
        hlayout = QHBoxLayout(self.editor)
        hlayout.addWidget(splitter)
        splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        splitter.addWidget(card)
        splitter.addWidget(rightpane)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        
        self.retranslateUi()
        self.updateFields()
        

    def updateFields(self):
        if self.editor.resource:
            self.name.setText(self.editor.resource.property(Soprano.Vocabulary.NAO.prefLabel()).toString())
            self.description.setText(self.editor.resource.description())

            
    def retranslateUi(self):
        self.descriptionLabel.setText(QApplication.translate("ResourceEditor", "&Description:", None, QApplication.UnicodeUTF8))
        #self.relationsLabel.setText(QApplication.translate("ResourceEditor", "&Relations:", None, QApplication.UnicodeUTF8))
        

    def createIconWidget(self, parent):
        iconWidget = QWidget(parent)
        iconWidgetLayout = QHBoxLayout(iconWidget)
        self.iconButton = QPushButton();
        self.iconButton.setIcon(self.editor.resourceIcon())
        size = QSize(80, 80)
        self.iconButton.setIconSize(size)
        self.iconButton.setContentsMargins(40, 40, 40, 40)
        #button.setStyleSheet("border: 20px solid #fff;")
        self.iconButton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.editor.connect(self.iconButton, SIGNAL("clicked()"), self.editor.selectIcon)
        iconWidgetLayout.addStretch(1)
        iconWidgetLayout.addWidget(self.iconButton)
        iconWidgetLayout.addStretch(1)
        return iconWidget

    def createMainPropertiesWidget(self, parent):
        propertiesWidget = QWidget(parent)

        self.gridlayout = QGridLayout(propertiesWidget)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        
        nameBox = QGroupBox("Name")
        #self.name_label = QLabel(propertiesWidget)
        #self.name_label.setObjectName("name_label")
        #self.gridlayout.addWidget(self.name_label, 1, 0, 1, 1)
        self.name = QLineEdit(propertiesWidget)
        self.name.setObjectName("name")
        vbox = QVBoxLayout(nameBox)
        vbox.addWidget(self.name)
        self.gridlayout.addWidget(nameBox, 1, 0, 1, 2)
        #self.name_label.setBuddy(self.name)
        
        spacerItem = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 2, 0, 1, 1)
        
        return propertiesWidget
    
    def resourceLabel(self):
        return self.name.text()