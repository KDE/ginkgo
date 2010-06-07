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
from PyKDE4.soprano import Soprano
from PyKDE4.kdeui import KIcon
from PyKDE4.kdecore import i18n
from ginkgo.views.resourcestable import ResourcesTable, ResourcesTableModel
from ginkgo.views.objectcontextmenu import ObjectContextMenu
from ginkgo.actions import * 


class SparqlResultsTableModel(ResourcesTableModel):
    def __init__(self, parent=None):
        super(SparqlResultsTableModel, self).__init__(parent)
        self.data = []
        self.table = parent
    
    def rowCount(self, index):
        return len(self.data)
    
    def columnCount(self, index):
        #return len(self.headers)
        return 2
        
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
            elif index.column() == 3:
                return Qt.AlignLeft | Qt.AlignVCenter

        elif role == Qt.DisplayRole:
            return self.itemAt(index)
        
        return QVariant()


    def itemAt(self, index):
        item = self.data[index.row()]
        return item[index.column()]

    def queryNextReadySlot(self, query):

#        bindingNames = query.bindingNames()
#        for bindingName in bindingNames:
#            print bindingName
        
        
        if len(self.headers) == 0:
            self.headers = ["?b", "?c"]
            #self.table.table.horizontalHeader().headerDataChanged(Qt.Horizontal, 0, 1)
            #self.table.table.horizontalHeader().showSection(1)
            
        bNode = query.binding("b")
        cNode = query.binding("c")
        bvalue = self.nodeToString(bNode)
        cvalue = self.nodeToString(cNode)
        
        self.beginInsertRows(QModelIndex(), len(self.data), len(self.data))
        self.data.append((bvalue, cvalue))
        self.endInsertRows()
        query.next()

    def nodeToString(self, node):
        if node.isResource():
            value = node.uri()
            valueQstr = value.toString()
            label = unicode(valueQstr)
            if label.find("#") > 0:
                label = label[label.find("#") + 1:]
            ontologyLabel = datamanager.ontologyAbbreviationForUri(QUrl(valueQstr), False)
            if ontologyLabel != label:
                return label+" ["+ontologyLabel+"]"
            return label
        elif node.isLiteral():
            value = unicode(node.literal().toString())
            if len(value) > 100:
                value = value[0:100] +"..."
            return value
        

   
class SparqlResultsTable(ResourcesTable):
    
    def __init__(self, mainWindow=False, dialog=None, sparql=None):
        self.sparql = sparql
        super(SparqlResultsTable, self).__init__(mainWindow=mainWindow, dialog=dialog)

    def createModel(self):
        self.model = SparqlResultsTableModel(self)
        #self.model.setHeaders([i18n("Relation"), i18n("Title"), i18n("Date"), i18n("Type") ])
        self.model.setHeaders(["", ""])
        datamanager.executeAsyncQuery(self.sparql, self.model.queryNextReadySlot, self.queryFinishedSlot, self)
        
        #TODO: handle stop
    def setSparql(self, sparql):
        self.sparql = sparql

    
