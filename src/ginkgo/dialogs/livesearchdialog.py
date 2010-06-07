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
from ginkgo.views.resourcestable import ResourcesTable
from ginkgo.dao import datamanager
from ginkgo.views.resourcesbytypetable import ResourcesByTypeTable
from ginkgo.ontologies import NFO

class LiveSearchDialog(QDialog):

    def __init__(self, parent=None, mainWindow=None, resource=None, excludeList=None, title=None):
        super(LiveSearchDialog, self).__init__(parent)
        self.mainWindow = mainWindow
        self.resource = resource

        self.excludeList = excludeList
        if title is None:
            self.title = i18n("Open Resource")
            self.objectNameLabel = i18n("Name")
        else:
            self.title = title
            self.objectNameLabel = i18n("&Object")
            
        self.typeUri = Soprano.Vocabulary.RDFS.Resource()
        #default predicate
        self.predicate = Soprano.Vocabulary.NAO.isRelated()
        self.setupUi(self)
        self.input.setFocus(Qt.OtherFocusReason)
        self.validate()


    def on_input_textEdited(self, text):
        self.searchMatchingItems()
        #self.validate()
        
    def onTypeFilterChanged(self):
        action = self.sender()
        nepomukType = action.property("nepomukType")
        
        self.typeUri = QUrl(nepomukType.toString())
       
        label = nepomukType.toString()
        label = unicode(label)
        
        if self.typeUri == Soprano.Vocabulary.RDFS.Resource():
            label = i18n("All")
        elif label.find("#") > 0:
            label = label[label.find("#") + 1:]
            if label == "FileDataObject":
                label = "File"
            elif label == "TextDocument":
                label = "File"
            #return a QString instead of a str for the proxy model, which handles only QString
            
        elif label.find("nepomuk:/") == 0:
            #this is a custom type, we need to get the label of the ressource
            typeResource = Nepomuk.Resource(label)
            label = typeResource.genericLabel()
        else:
            label = label[label.rfind("/") + 1:]
        
        self.typeFilterButton.setText(i18n(label))
       
        self.searchMatchingItems()
    
    def onPropertyChanged(self):
        index = self.properties.currentIndex()
        data = self.properties.itemData(index).toString()
        self.predicate = QUrl(data) 
        
    def searchMatchingItems(self):
        
        input = unicode(self.input.text()).strip()
        if  input and len(input) > 0:
            #find resources starting with the input entered
            input = "^" + input
        
        #recreate model, otherwise items keep being added to the previous one if the previous query has not finished
        #while the user updates the input text
        #count = self.matchingItems.table.model().rowCount(QModelIndex())
        self.matchingItems.installModels()
        #self.matchingItems.table.rowCountChanged(count, 0)
        
        
        #search only we don't have both an empty input and all types
        if input and len(input) > 0 or self.typeUri != Soprano.Vocabulary.RDFS.Resource():
            datamanager.findResourcesByTypeAndLabel(self.typeUri, input, self.matchingItems.model.queryNextReadySlot, self.matchingItems.queryFinishedSlot, self.matchingItems)
            

    def validate(self):
        #TODO: check that text is not (\*])* (regexp)
        #self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(not self.input.text().isEmpty())
        #l = len(self.matchingItems.table.model().sourceModel().resources)
        #flag = len(self.matchingItems.selectedResources()) == 1
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)

    def selectedResource(self):
        if len(self.matchingItems.selectedObjects()) > 0:
            return self.matchingItems.selectedObjects()[0]
        return None
    
    def selectedResources(self):
        if len(self.matchingItems.selectedObjects()) > 0:
            return self.matchingItems.selectedObjects()
        return None

    def selectedPredicate(self):
        return self.predicate

    def accept(self):
        QDialog.accept(self)

    def sizeHint(self):
        return QSize(450, 300)

    def setupUi(self, dialog):
        dialog.setObjectName("dialog")
        vbox = QVBoxLayout(dialog)
#        self.gridlayout.setMargin(9)
#        self.gridlayout.setSpacing(6)
#        self.gridlayout.setObjectName("gridlayout")
        
        #if this is a new relation dialog
        if self.resource is not None:
            propertyWidget = QWidget(dialog)
            hbox = QHBoxLayout(propertyWidget)
            hbox.setContentsMargins(0, 0, 0, 0)
            label = QLabel(propertyWidget)
            label.setText(i18n("&Relation type:"))
            hbox.addWidget(label)
            self.properties = QComboBox()
            label.setBuddy(self.properties)
            props = []
            
            for property in datamanager.resourceTypesProperties(self.resource, True, False):
                ontology = datamanager.ontologyAbbreviationForUri(property.uri())
                item = property.label("en") + " [" + ontology + "]"
                props.append((property, item))
                     
            sortedProps = sorted(props, key=lambda tuple: tuple[1])
            index = 0
            isRelatedIndex = 0
            for tuple in sortedProps: 
                self.properties.addItem(tuple[1], QVariant(str(tuple[0].uri().toString())))
                if tuple[0].uri() == Soprano.Vocabulary.NAO.isRelated():
                    isRelatedIndex = index 
                index = index + 1
            hbox.addWidget(self.properties)
            self.properties.setCurrentIndex(isRelatedIndex)
            self.properties.activated.connect(self.onPropertyChanged)
            vbox.addWidget(propertyWidget)
        
        filter = QWidget(dialog)
        hbox = QHBoxLayout(filter)
        label = QLabel(filter)
        label.setText(self.objectNameLabel)
        hbox.addWidget(label)
        self.input = QLineEdit(filter)
        self.input.setObjectName("input")
        label.setBuddy(self.input)
        hbox.addWidget(self.input)
        
        label = QLabel(filter)
        label.setText(i18n("&Type:"))
        hbox.addWidget(label)
        
        
        self.typeFilterButton = QToolButton()
        self.typeFilterButton.setText(i18n("All"))
        self.typeFilterButton.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.typeFilterButton.setToolTip(i18n("Filter by type"))
        self.typeFilterButton.setIcon(KIcon("nepomuk"))
        self.typeFilterButton.setPopupMode(QToolButton.InstantPopup)
        self.typeFilterMenu = QMenu(self)
        self.typeFilterMenu.setTitle(i18n("Filter by type"))
        self.typeFilterMenu.setIcon(KIcon("nepomuk"))
        label.setBuddy(self.typeFilterButton)
        
        self.typeFilterMenu.addAction(self.mainWindow.createAction(i18n("&All"), self.onTypeFilterChanged, None, "nepomuk", None, Soprano.Vocabulary.RDFS.Resource()))
            
        for type in self.mainWindow.placesData:
            self.typeFilterMenu.addAction(self.mainWindow.createAction(type[1], self.onTypeFilterChanged, None, type[3], None, type[0]))
            
            
                
        self.typeFilterButton.setMenu(self.typeFilterMenu)
        hbox.addWidget(self.typeFilterButton)
        hbox.setContentsMargins(0, 0, 0, 0)
        
        vbox.addWidget(filter)
        
        self.matchingItems = ResourcesTable(mainWindow=dialog.mainWindow, dialog=self)
            
        label = QLabel(dialog)
        label.setText(i18n("Matching items:"))
        
        vbox.addWidget(label)
        vbox.addWidget(self.matchingItems)

        self.buttonBox = QDialogButtonBox(dialog)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.NoButton | QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        vbox.addWidget(self.buttonBox)

        dialog.setWindowTitle(i18n(self.title))

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

