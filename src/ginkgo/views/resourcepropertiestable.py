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
import os
import subprocess
   

class ResourcePropertiesTable(QWidget):


    def __init__(self, mainWindow=False, resource=None, dialogMode=False):
        super(ResourcePropertiesTable, self).__init__(mainWindow.workarea)

        self.resource = resource
        self.mainWindow = mainWindow
        self.dialogMode = dialogMode

        model = Nepomuk.ResourceManager.instance().mainModel()
        model.statementAdded.connect(self.statementAddedSlot)
        model.statementRemoved.connect(self.statementRemovedSlot)

        self.createTable()
        self.setData()
        
        verticalLayout = QVBoxLayout(self)
        verticalLayout.setObjectName("editor")
        verticalLayout.addWidget(self.table)
        self.setLayout(verticalLayout)
        
        QMetaObject.connectSlotsByName(self)

    #abstract
    def statementAddedSlot(self, statement):
        predicate = statement.predicate().uri()

    def statementRemovedSlot(self, statement):
        subject = statement.subject().uri()
        predicate = statement.predicate().uri()


    def createTable(self):
        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.resizeColumnsToContents()
        
        self.table.setWordWrap(True)
        self.table.setDragEnabled(False)
        self.table.setAcceptDrops(False)
        self.table.setDropIndicatorShown(False)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)

        #self.table.setDragDropMode(QAbstractItemView.DragDrop)
        self.table.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.table.setSortingEnabled(True)
        self.table.setShowGrid(True)
        self.table.verticalHeader().setVisible(False)

        self.table.setColumnCount(len(self.labelHeaders()))
        self.table.setHorizontalHeaderLabels(self.labelHeaders())
        
        

        #QObject.connect(self.table, SIGNAL("customContextMenuRequested (const QPoint&)"), self.showContextMenu)


    def showContextMenu(self, points):
        index = self.table.indexAt(points)
        if index:
            item = self.table.item(index.row(), 0)
            selection = None
            if item:
                selection = item.data(Qt.UserRole).toPyObject()
            menu = self.createContextMenu(selection)
            pos = self.table.mapToGlobal(points)
            menu.exec_(pos)


    def setData(self):
        self.fetchData()
        if self.data:
            self.table.setRowCount(len(self.data))
            self.table.setColumnCount(len(self.labelHeaders()))
            self.table.setHorizontalHeaderLabels(self.labelHeaders())
            selected = None
            for row, propvalue in enumerate(self.data):
                
                propname = propvalue[0]
                propname = propname[propname.find("#")+1:]
                item = QTableWidgetItem(propname)
                #icon = self.mainWindow.getResourceIcon(resource, 16)
                #item.setIcon(icon)
                
                #item.setData(Qt.UserRole, resource.resourceUri().toString())
                self.table.setItem(row, 0, item)
                self.table.setItem(row, 1, QTableWidgetItem(propvalue[1].toString()))
                
            
            self.table.resizeColumnsToContents()
            if selected is not None:
                selected.setSelected(True)
                self.table.setCurrentItem(selected)
                self.table.scrollToItem(selected)
    
    #abstract            
    def labelHeaders(self):
        return [i18n("Property"), i18n("Value")]
  

    def fetchData(self):
        self.data = datamanager.findResourceLiteralProperties(self.resource)

    def setResource(self, resource):
        self.resource = resource
        self.setData()        