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
from PyKDE4.soprano import Soprano
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ginkgo.dao import datamanager
from ginkgo.ontologies import NFO, NIE, PIMO
from os import system
from os.path import join
from PyKDE4.soprano import Soprano
from PyKDE4.kdeui import KIcon
from PyKDE4.kdecore import i18n
from ginkgo.views.resourcestable import ResourcesTable, ResourcesTableModel
from ginkgo.views.objectcontextmenu import ObjectContextMenu
from ginkgo.actions import *

class TypesTableModel(ResourcesTableModel):
    def __init__(self, parent=None):
        super(TypesTableModel, self).__init__(parent)
        
    def itemAt(self, index):
        resource = self.resources[index.row()]
        column = index.column()
        if column == 0:
            return datamanager.ontologyAbbreviationForUri(resource.resourceUri())
        elif column == 1:
            return resource.genericLabel()
        
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if index.column() == 0 or index.column() == 1: 
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)
            
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index))
            
class TypesTable(ResourcesTable):
    
    def __init__(self, mainWindow=False, typesUris=None, dialog=None):
        """ typesUris stands for the types to be selected"""
        
        self.typesUris = typesUris
        super(TypesTable, self).__init__(mainWindow=mainWindow, dialog=dialog)

        self.table.sortByColumn(1, Qt.AscendingOrder)
        self.table.horizontalHeader().setResizeMode(0, QHeaderView.Interactive)
        self.table.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)
        self.table.resizeColumnsToContents()
        #self.updateSelection()
        self.table.setEditTriggers(QTableWidget.SelectedClicked | QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        self.table.setSelectionBehavior(QTableWidget.SelectItems)
        self.table.setItemDelegate(TypeDelegate(self))
        
        
        
    def createModel(self):
        
        self.model = TypesTableModel(self)
        self.model.setHeaders([i18n("Ontology"), i18n("Name")])
        

        #TODO: find built-in conversion
        resourceSet = []
        array = []
#            for elt in resourceTypes:
#                typeResource = Nepomuk.Resource(elt)
#                ressourceArray.append(typeResource)
        
#        rootClass = Nepomuk.Types.Class(Soprano.Vocabulary.RDFS.Resource())
#        self.addChildren(rootClass.uri(), array)
        
        #add the root element, Resource, to the set of types
        #resourceSet.append(Nepomuk.Resource(Soprano.Vocabulary.RDFS.Resource()))
        for typeUri in self.typesUris:
            resourceSet.append(Nepomuk.Resource(typeUri))
        self.model.setResources(resourceSet)

#    def addChildren(self, resourceUri, set):
#        
#        typeClass = Nepomuk.Types.Class(resourceUri)
#        subClasses = typeClass.subClasses()
#        for subClass in subClasses:
#            #TODO: why subClass are not instance of Resource?
#            try:
#                index = set.index(subClass.uri())
#            except ValueError, e:
#                set.append(subClass.uri())
#                self.addChildren(subClass.uri(), set)

    def updateSelection(self):
        index = 0
        for item in self.model.resources:
            for resourceType  in self.typesUris:
                if item.resourceUri() == resourceType:
                    mindex = self.model.index(index, 0, QModelIndex())
                    pindex = self.table.model().mapFromSource(mindex)
                    self.table.selectionModel().select(pindex, QItemSelectionModel.Select)
                    mindex = self.model.index(index, 1, QModelIndex())
                    pindex = self.table.model().mapFromSource(mindex)
                    self.table.selectionModel().select(pindex, QItemSelectionModel.Select)
                    break
                    
            index = index + 1    
        #selection = QItemSelection(selection1, selection2)


    def createContextMenu(self, index, selection):
        return TypeChooserContextMenu(self, selection)
    
    def processAction(self, key, selectedResources):
        if key == TYPE_LIST_ADD_TYPE:
            self.addType()
            
        elif key == TYPE_LIST_REMOVE_TYPE:
            for resource in selectedResources:
                #do not remove the Resource type
                if resource.resourceUri() != Soprano.Vocabulary.RDFS.Resource():
                    self.table.model().sourceModel().removeResource(resource.resourceUri())

    
    def activated(self, index):
        """Overrides ResourceTable:activated so that no action is fired (dialog:accept) when 
        a resource gets activated."""
      
        return None
            
    def addType(self):
        newTypeResource = Nepomuk.Resource(Soprano.Vocabulary.RDFS.Resource())
        self.table.model().sourceModel().addResource(newTypeResource)
                

class TypeChooserContextMenu(ObjectContextMenu):
    def __init__(self, parent=None, selectedResources=None):
        super(TypeChooserContextMenu, self).__init__(parent, selectedResources)

    def createActions(self):

        if self.selectedResources:
            action = QAction(i18n("&Remove type"), self)
            action.setProperty("key", QVariant(TYPE_LIST_REMOVE_TYPE))
            self.addAction(action)
            
        else:
            #the user right clicked in the empty zone
            action = QAction(i18n("&Add type"), self)
            action.setProperty("key", QVariant(TYPE_LIST_ADD_TYPE))
            self.addAction(action)
            
            

class TypeDelegate(QItemDelegate):

    def __init__(self, parent=None):
        super(TypeDelegate, self).__init__(parent)
        self.table = parent
        self.ontologies = datamanager.findOntologies()

    def paint(self, painter, option, index):
        QItemDelegate.paint(self, painter, option, index)


    def sizeHint(self, option, index):
        fm = option.fontMetrics
        if index.column() == 0:
            return QSize(fm.width("DCMI Terms"), fm.height())
        return QItemDelegate.sizeHint(self, option, index)


    def createEditor(self, parent, option, index):
        if index.column() == 0:
            combobox = QComboBox(parent)
            combobox.setEditable(False)
            
            for ontology in self.ontologies:
                abbrev = unicode(ontology.property(Soprano.Vocabulary.NAO.hasDefaultNamespaceAbbreviation()).toString())
                if len(abbrev) == 0:
                    abbrev = ontology.resourceUri().toString()
                combobox.addItem(abbrev, QVariant(str(ontology.resourceUri().toString())))
            
            return combobox
        
        elif index.column() == 1:
            #edition of a property value
            #identify the range of the property
            sindex = self.table.table.model().mapToSource(index)
            currentType = index.model().sourceModel().resourceAt(sindex.row())
            currentOntology = datamanager.ontologyForUri(currentType.resourceUri())

            self.classes = datamanager.findOntologyClasses(currentOntology.resourceUri())
            
            combobox = QComboBox(parent)
            combobox.setEditable(False)
            
            for clazz in self.classes:
                combobox.addItem(clazz.genericLabel(), QVariant(unicode(clazz.resourceUri().toString())))
            
            return combobox
            
        else:
            return None


    def commitAndCloseEditor(self):
        editor = self.sender()
#        if isinstance(editor, (QTextEdit, QLineEdit)):
#            self.emit(SIGNAL("commitData(QWidget*)"), editor)
#            self.emit(SIGNAL("closeEditor(QWidget*)"), editor)


    def setEditorData(self, editor, index):
        sindex = self.table.table.model().mapToSource(index)
        currentType = index.model().sourceModel().resourceAt(sindex.row())
        currentOntology = datamanager.ontologyForUri(currentType.resourceUri())
        
        if index.column() == 0:
            i = 0
            for ontology in self.ontologies:
                if currentOntology.resourceUri() == ontology.resourceUri():
                    editor.setCurrentIndex(i)
                    break
                i = i + 1
           
        elif index.column() == 1:
            i = 0
            for clazz in self.classes:
                if currentType.resourceUri() == clazz.resourceUri():
                    editor.setCurrentIndex(i)
                    break
                i = i + 1

    def setModelData(self, editor, model, index):
        
        sindex = self.table.table.model().mapToSource(index)
        cindex = editor.currentIndex()
        
        if index.column() == 0:
            newOntology = self.ontologies[cindex]
            #get first class of that ontology
            classes = datamanager.findOntologyClasses(newOntology.resourceUri())
            if classes:
                index.model().sourceModel().resources[sindex.row()] = classes[0] 
            
        elif index.column() == 1:
            index.model().sourceModel().resources[sindex.row()] = self.classes[cindex]

                        
 
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    resource = Nepomuk.Resource("nepomuk:/res/ad17c07d-332f-4fc1-9363-476e0a951b43")
    table = TypesTable(typesUris=resource.types())
    table.show()
    
    app.exec_()

