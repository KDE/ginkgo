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
from PyKDE4.kdecore import *
from PyKDE4.kio import *
from dao import PIMO, datamanager, NFO, NIE
from os import system
from os.path import join
from PyKDE4 import soprano
from editors.resourcecontextmenu import ResourceContextMenu
import os
import subprocess
   

class ResourcesTable(QWidget):

    '''
    - In dialog mode, we don't want that double clicking an item opens it up in a new editor. We want instead that this makes the dialog accept the selected item.
    '''
    def __init__(self, mainWindow=False, dialogMode=False, excludeList=None):
        super(ResourcesTable, self).__init__(mainWindow.editors)

        self.mainWindow = mainWindow
        self.dialogMode = dialogMode
        self.excludeList = excludeList
        
        
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
        #TODO: check
        if predicate and len(predicate.toString()) == 0:
            self.removeResource(subject.toString())


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
        #self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.MultiSelection)
        self.table.setDragDropMode(QAbstractItemView.NoDragDrop)
        
        self.table.setSortingEnabled(True)
        self.table.setShowGrid(True)
        self.table.verticalHeader().setVisible(False)
        
        self.table.setColumnCount(len(self.labelHeaders()))
        self.table.setHorizontalHeaderLabels(self.labelHeaders())
        
        if not self.dialogMode:
            QObject.connect(self.table, SIGNAL("activated (const QModelIndex&)"), self.activated)

        QObject.connect(self.table, SIGNAL("customContextMenuRequested (const QPoint&)"), self.showContextMenu)


    def showContextMenu(self, points):
        index = self.table.indexAt(points)
        if index:
            item = self.table.item(index.row(), 0)
            selection =  []
            if item:
                selindexes = self.table.selectionModel().selectedRows()
                for selindex in selindexes:
                    selitem = self.table.item(selindex.row(), 0)
                    selection.append(selitem.data(Qt.UserRole).toPyObject())
                #make sure the item below the mouse is added
                try:
                    selection.index(item.data(Qt.UserRole).toPyObject())
                except:
                    selection.append(item.data(Qt.UserRole).toPyObject())
                    
            menu = self.createContextMenu(selection)
            pos = self.table.mapToGlobal(points)
            menu.exec_(pos)

    def activated(self, index):
        if index.isValid():
            item = self.table.item(index.row(), 0)
            selection = item.data(Qt.UserRole).toPyObject()
            self.mainWindow.openResource(uri=selection)
      
    def createContextMenu(self, selection):
        return ResourceContextMenu(self, selection)

    def setData(self):
        self.fetchData()
        if self.data:
            if self.excludeList:
                for exclude in self.excludeList:
                    try:
                        self.data.remove(exclude)
                    except ValueError:
                        pass
                    
            self.table.setRowCount(len(self.data))
            self.table.setColumnCount(len(self.labelHeaders()))
            self.table.setHorizontalHeaderLabels(self.labelHeaders())
            selected = None
            for row, resource in enumerate(self.data):
                item = QTableWidgetItem(resource.genericLabel())
                icon = self.mainWindow.resourceIcon(resource, 16)
                item.setIcon(icon)
                
                item.setData(Qt.UserRole, resource.resourceUri().toString())
                self.table.setItem(row, 0, item)
            
            
            self.table.resizeColumnsToContents()
            if selected is not None:
                selected.setSelected(True)
                self.table.setCurrentItem(selected)
                self.table.scrollToItem(selected)
    
    #abstract            
    def labelHeaders(self):
        pass
  
        
    def addResource(self, resource):
        item = QTableWidgetItem(resource.genericLabel())
        icon = self.mainWindow.resourceIcon(resource, 16)
        item.setIcon(icon)
        item.setData(Qt.UserRole, resource.resourceUri().toString())
        self.table.setRowCount(self.table.rowCount() + 1)
        self.table.setItem(self.table.rowCount() - 1, 0, item)
        
    def removeResource(self, uri):
        #self.table.setRowCount(self.table.rowCount() -1 1)
        #self.table.setItem(self.table.rowCount() - 1, 0, item)
        
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                resource = item.data(Qt.UserRole).toPyObject()
                if resource == uri:
                    self.table.removeRow(row)

    #abstract
    def processAction(self, key, selectedUris):
#        if hasattr(self, "appDB") and self.appDB.has_key(key):
#            cmd1 = [self.appDB[key], self.appDB['URL']]
#            p1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
#            p1.poll()
#            #system('%s %s' % ())
#            return True
        if key == '&Open in new tab':
            for uri in selectedUris:
                self.mainWindow.openResource(uri, newTab=True)
        elif key == '&Delete':
            for uri in selectedUris:
                self.mainWindow.removeResource(uri)
        elif key == "Open &file":
            for uri in selectedUris:
                self.mainWindow.launchFile(uri)
        elif key == "Open &page":
            for uri in selectedUris:
                self.mainWindow.openWebPage(uri)


        
        #http://code.google.com/p/ file pydingo/handlers/directory/handler.py
        
        
#        self.appDB = {}
#        
#        if NFO.FileDataObject in resource.types():
#            url = str(resource.property(NIE.url).toString())
#            if url.find("file://") == 0:
#                url = url[len("file://"):]
#                if not os.path.exists(url):
#                    return
#            if url.find("filex://") == 0:
#                url = url[len("filex://"):]
#                if not os.path.exists(url):
#                    return
#                
#            meta = gnome_meta.get_meta_info(url)
#            
#            self.appDB = {'URL': url}
#            
#            openWithMenu = QMenu(menu)
#            openWithMenu.setTitle("Open with")
#        
#            if meta and len(meta) > 1 and meta['default_app']:
#                icon = mime.get_icon(meta['default_app'][0])
#                if icon:
#                    icon = QIcon(icon)
#                    openWithMenu.addAction(icon, meta['default_app'][1].decode('utf-8'))
#                else:
#                    openWithMenu.addAction(meta['default_app'][1].decode('utf-8'))
#                
#                self.appDB[meta['default_app'][1].decode('utf-8')] = meta['default_app'][2]
#                
#                if meta['other_apps'] and len(meta['other_apps']) > 1:
#                    for application in meta['other_apps']:
#                        icon = mime.get_icon(application[0])
#                        if icon:
#                            icon = QIcon(icon)
#                            openWithMenu.addAction(icon, application[1].decode('utf-8'))
#                        else:
#                            openWithMenu.addAction(application[1].decode('utf-8'))
#                        
#                        self.appDB[application[1].decode('utf-8')] = application[2]
#                    menu.addAction(openWithMenu.menuAction())
#            
#            else:
#                meta = gio_meta.get_meta_info(url)
#                if meta and len(meta) > 0:
#                    for application in meta:
#                        openWithMenu.addAction(application['name'].decode('utf-8'))
#                        self.appDB[application['name'].decode('utf-8')] = application['exec']
#                        menu.addAction(openWithMenu.menuAction())
#                else:
#                    pass
#
