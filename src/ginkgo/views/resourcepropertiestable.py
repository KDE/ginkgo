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
from ginkgo.dao import datamanager
from ginkgo.ontologies import NFO, NIE, PIMO
from os import system
from os.path import join
from PyKDE4 import soprano
from PyKDE4.kdecore import i18n
from ginkgo.views.resourcestable import ResourcesTable, ResourcesTableModel
import os
import subprocess
from ginkgo.actions import *

class PropertyContextMenu(QMenu):
    def __init__(self, parent=None, propvalue=False):
        super(PropertyContextMenu, self).__init__(parent)
        self.propvalue = propvalue
        self.parent = parent
        self.createActions()
        self.triggered.connect(self.actionTriggered)
        QMetaObject.connectSlotsByName(self)
    
    def actionTriggered(self, action):
        key = action.property("key").toString()
        self.parent.processAction(key, self.propvalue)
        
    def createActions(self):
        copyAction = QAction(i18n("&Copy value to clipboard"), self)
        copyAction.setProperty("key", QVariant(COPY_TO_CLIPBOARD))
        #openInNewTabAction.setIcon(KIcon("tab-new-background-small"))
        self.addAction(copyAction)
    

class ResourcePropertiesTableModel(ResourcesTableModel):
    def __init__(self, parent=None, data=None):
        super(ResourcePropertiesTableModel, self).__init__(parent)
        self.data = data
        
    def itemAt(self, index):
        column = index.column()
        if column == 0:
            propname = self.data[index.row()][0]
            if propname.find("#") > 0:
                propname = propname[propname.find("#")+1:]
            return propname
        elif column == 1:
            value = self.data[index.row()][1]
            if value:
                return value.toString()
            return ""

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
                propuri = self.data[index.row()][0]
                propResource = Nepomuk.Resource(propuri)
                return self.editor.mainWindow.resourceQIcon(propResource)

        return QVariant()

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            return self.headers[section]
        else:
            return None
   

class ResourcePropertiesTable(ResourcesTable):
    
    def __init__(self, mainWindow=False, resource=None, dialog=None):
        self.resource = resource
        super(ResourcePropertiesTable, self).__init__(mainWindow=mainWindow, dialog=dialog)
        self.resource = resource
        self.table.horizontalHeader().setResizeMode(0, QHeaderView.Interactive)
        self.table.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)

    def createModel(self):
        data = datamanager.findResourceLiteralProperties(self.resource)
        if self.resource:
            uriprop = ["uri", self.resource.resourceUri()]
            data.append(uriprop)
        self.model = ResourcePropertiesTableModel(self, data=data)
        
        self.model.setHeaders([i18n("Property"), i18n("Value")])


    def showContextMenu(self, points):
        index = self.table.indexAt(points)
        if index.isValid():
            #convert the proxy index to the source index
            #see http://doc.trolltech.com/4.6/qsortfilterproxymodel.html
            sourceIndex = self.table.model().mapToSource(index)
            propvalue = self.table.model().sourceModel().data[sourceIndex.row()]
            if propvalue:
                menu = self.createContextMenu(propvalue)
                pos = self.table.mapToGlobal(points)
                menu.exec_(pos)
                
                
    def createContextMenu(self, propvalue):
        return PropertyContextMenu(self, propvalue)

    def setResource(self, resource):
        self.resource = resource
        self.installModels()        
    
    def processAction(self, key, propvalue):
        if key == COPY_TO_CLIPBOARD:
            print propvalue
