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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdeui import KIcon
from ginkgo.dao import datamanager
from ginkgo.ontologies import NFO, NIE, PIMO
from os import system
from os.path import join
from PyKDE4 import soprano
from PyKDE4.kdecore import i18n
from ginkgo.views.resourcestable import ResourcesTable, ResourcesTableModel
from ginkgo.views.objectcontextmenu import ObjectContextMenu
import os
import subprocess
from ginkgo.actions import NEW_PROPERTY, DELETE, OPEN_IN_NEW_TAB

class PropertyContextMenu(ObjectContextMenu):
    def __init__(self, parent=None, selectedProperties=False):
        self.selectedProperties = selectedProperties
        
        selectedResources = []
        for property in selectedProperties:
            selectedResources.append(Nepomuk.Resource(property.uri()))
    
        super(PropertyContextMenu, self).__init__(parent, selectedResources)
        
        
    def createActions(self):
        if self.selectedResources:
            self.addOpenAction()
        
        newPropertyAction = QAction(i18n("&New property"), self)
        newPropertyAction.setProperty("key", QVariant(NEW_PROPERTY))
        self.addAction(newPropertyAction)

        if self.selectedResources:
            self.addDeleteAction()

        
        


class TypePropertiesTableModel(ResourcesTableModel):
    def __init__(self, parent=None, data=None):
        super(TypePropertiesTableModel, self).__init__(parent)
        self.data = data
        
    def itemAt(self, index):
        column = index.column()
        if column == 0:
            parentClass = self.data[index.row()][0]
            return parentClass.label("en")
        elif column == 1:
            property = self.data[index.row()][1]
            uri = property.uri()
            ontologyLabel = datamanager.uriToOntologyLabel(uri)
            return property.label("en") + " [" + ontologyLabel + "]"
        elif column == 2:
            property = self.data[index.row()][1]
            range = property.range()
            if range.isValid():
                return range.label("en")
            else:
                dataType = str(property.literalRangeType().dataTypeUri().toString())
                index = dataType.find("#")
                if index > 0 and len(dataType) > index:
                    dataType = dataType[index + 1:]
                return dataType

    def rowCount(self, index):
        return len(self.data)
    
    def columnCount(self, index):
        return len(self.headers)

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        if role == Qt.TextAlignmentRole:
            if index.column() == 0:
                return Qt.AlignLeft | Qt.AlignVCenter
            elif index.column() == 1:
                return Qt.AlignLeft | Qt.AlignVCenter
            elif index.column() == 2:
                return Qt.AlignLeft | Qt.AlignVCenter
        elif role == Qt.DisplayRole:

            return self.itemAt(index)
        elif role == Qt.DecorationRole:
            if index.column() == 0:
                parentClass = self.data[index.row()][0]
                parentClassResource = Nepomuk.Resource(parentClass.uri())
                return self.editor.mainWindow.resourceQIcon(parentClassResource)
            
            elif index.column() == 1:
                property = self.objectAt(index.row())
                propResource = Nepomuk.Resource(property.uri())
                return self.editor.mainWindow.resourceQIcon(propResource)


        return QVariant()

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            return self.headers[section]
        else:
            return None
        
    def resourceAt(self, row):
        return Nepomuk.Resource(self.data[row][1].uri())

    def objectAt(self, row):
        return self.data[row][1]
   
class TypePropertiesTable(ResourcesTable):
    
    def __init__(self, mainWindow=False, resource=None, dialog=None):
        self.resource = resource
        super(TypePropertiesTable, self).__init__(mainWindow=mainWindow, dialog=dialog)
        self.resource = resource
        self.table.horizontalHeader().setResizeMode(0, QHeaderView.Interactive)
        self.table.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)

    def createModel(self):
        data = []
        
        if self.resource:
            clazz = Nepomuk.Types.Class(self.resource.resourceUri())
            props = datamanager.typeProperties(clazz, True)
            for prop in props:
                data.append((clazz, prop))
            
            for parentClass in clazz.allParentClasses():
                props = datamanager.typeProperties(parentClass, True)
                for prop in props:
                    data.append((parentClass, prop))
                    
        self.model = TypePropertiesTableModel(self, data=data)
        self.model.setHeaders([i18n("Inherited from"), i18n("Name"), i18n("Range")])


                
    def createContextMenu(self, index, selection):
        return PropertyContextMenu(self, selection)

    def setResource(self, resource):
        self.resource = resource
        self.installModels()        
    
    def processAction(self, key, selectedResources):
        if super(TypePropertiesTable, self).processAction(key, selectedResources):
            return True
        elif key == NEW_PROPERTY:
            self.mainWindow.newProperty()

