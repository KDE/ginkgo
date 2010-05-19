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
from PyKDE4.kdecore import *
from PyKDE4.kio import *
from dao import datamanager
from ontologies import NFO, NIE, PIMO, NCO
from os import system
from os.path import join
from PyKDE4 import soprano
from PyKDE4.soprano import Soprano
from views.resourcecontextmenu import ResourceContextMenu
from datetime import *
import os
import subprocess
   

class ResourcesTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super(ResourcesTableModel, self).__init__(parent)
        self.resources = []
        self.headers = []
        self.editor = parent
        self.resourcestable = parent
    
    def rowCount(self, index):
        return len(self.resources)
    
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
        elif role == Qt.DecorationRole:
            if index.column() == 0:
                resource = self.resourceAt(index.row())
                return self.editor.mainWindow.resourceQIcon(resource)

        elif role == Qt.DisplayRole:
            #rowCurrency = currencyAt(index.row());
            #columnCurrency = currencyAt(index.column());
            #if (currencyMap.value(rowCurrency) == 0.0)
            #return "####";
            #amount = currencyMap.value(columnCurrency) / currencyMap.value(rowCurrency);
            #return QString("hello %s" % index.row())
            return self.itemAt(index)
            

        return QVariant()

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            return self.headers[section]
        else:
            return None


    def itemAt(self, index):
        resource = self.resources[index.row()]
        column = index.column()
        if column == 0:
            return resource.genericLabel()
        elif column == 1:
            return resource.property(Soprano.Vocabulary.NAO.lastModified()).toDateTime()
        elif column == 2:
            for type in resource.types():
                if type != Soprano.Vocabulary.RDFS.Resource():
                    label = type.toString()
                    label = str(label)
                    label = label[label.find("#") + 1:]
                    if label == "FileDataObject":
                        label = "File"
                    elif label == "TextDocument":
                        label = "File"
                    #return a QString instead of a str for the proxy model, which handles only QString
                    return QString(label)

    def resourceAt(self, row):
        return self.resources[row]

    def setResources(self, resources):
        self.resources = resources
        
    def setHeaders(self, headers):
        self.headers = headers
        
    
    #bool QAbstractItemModel::insertRows ( int row, int count, const QModelIndex & parent = QModelIndex() )
    def addResource(self, resource):
        self.beginInsertRows(QModelIndex(), len(self.resources), len(self.resources))
        self.resources.append(resource)
        self.endInsertRows()

    def clear(self):
        self.beginRemoveRows (QModelIndex(), 0, len(self.resources))
        self.resources = []
        self.endRemoveRows()
        
    #TODO: check why when a resource is deleted, it has no uri anymore
    #we just need to remove all resources from the model which have a void uri (e.g. the resource was deleted)
    #or whose uri equals the one to be removed from the model (e.g. the resource was unlinked)
    def removeResource(self, resourceUri):
        for row in range(len(self.resources)):
            resource = self.resourceAt(row)
            if resource and (resource.resourceUri() == resourceUri or len(resource.resourceUri().toString()) == 0):
                self.beginRemoveRows(QModelIndex(), row, row)
                self.resources.pop(row)
                self.endRemoveRows()
                break
                
    
    #this slot has to be in the model, not in the table, otherwise when we change the model table
    #(e.g in the labelinputdialog), the slot can possibly be called by other queries which are still running 
    def queryNextReadySlot(self, query):
        query.next()
        node = query.binding("r");
        resource = Nepomuk.Resource(node.uri())
        self.addResource(resource)
        if self.resourcestable.searchDialogMode:
            self.resourcestable.table.selectionModel().clearSelection()
            self.resourcestable.table.selectRow(0)

    

class ResourcesSortFilterProxyModel(QSortFilterProxyModel):
 
    def __init__(self, parent, excludeList=None):
        super(ResourcesSortFilterProxyModel, self).__init__(parent)
        self.excludeList = excludeList

    def filterAcceptsRow(self, sourceRowInt, sourceParentModelIndex):
#        index0 = sourceModel()->index(sourceRowInt, 0, sourceParentModelIndex);
#        index1 = sourceModel()->index(sourceRow, 1, sourceParent);
#        index2 = sourceModel()->index(sourceRow, 2, sourceParent);
#
#        return (sourceModel()->data(index0).toString().contains(filterRegExp())
#             || sourceModel()->data(index1).toString().contains(filterRegExp()))
#            && dateInRange(sourceModel()->data(index2).toDate());
        #TODO: optimize
        if self.excludeList is None:
            return True
        else:
            resource = self.sourceModel().resourceAt(sourceRowInt)
            for elt in self.excludeList:
                if elt.resourceUri() == resource.resourceUri():
                    return False
        return True
    
    def lessThan(self, index1, index2):
        data1 = self.sourceModel().itemAt(index1)
        data2 = self.sourceModel().itemAt(index2)
        if (type(data1) == QDateTime):
            return data1 < data2
        elif (type(data1) == QString): 
            return QString.localeAwareCompare(data1, data2) < 0
        else:
            return True
     


class ResourcesTable(QWidget):

    '''
    - In dialog mode, we don't want that double clicking an item opens it up in a new editor. We want instead that this makes the dialog accept the selected item.
    - We still need to keep the possibility to pass resources, since some tables don't use the asyncquery mode (relations table for instance)
    - searchDialogMode is used by labelinputdialog.py for live results of matching items below the input line edit
    '''
    def __init__(self, mainWindow=False, resources=None, dialogMode=False, excludeList=None, searchDialogMode=False):
        super(ResourcesTable, self).__init__(mainWindow.workarea)

        self.mainWindow = mainWindow
        self.dialogMode = dialogMode
        
        self.searchDialogMode = searchDialogMode
        if self.searchDialogMode:
            self.dialogMode = True
            
        self.excludeList = excludeList
        self.resources = resources
        
        
        model = Nepomuk.ResourceManager.instance().mainModel()
        model.statementAdded.connect(self.statementAddedSlot)
        model.statementRemoved.connect(self.statementRemovedSlot)

        self.createTable()
        self.installModels(excludeList)
        
        self.table.sortByColumn(0, Qt.AscendingOrder)
        self.table.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        self.table.resizeColumnsToContents()

        verticalLayout = QVBoxLayout(self)
        verticalLayout.setObjectName("editor")
        verticalLayout.addWidget(self.table)
        self.setLayout(verticalLayout)


    #abstract
    def statementAddedSlot(self, statement):
        predicate = statement.predicate().uri()

    def statementRemovedSlot(self, statement):
        subject = statement.subject().uri()
        predicate = statement.predicate().uri()
        #TODO: check
        if predicate and len(predicate.toString()) == 0:
            self.table.model().sourceModel().removeResource(subject)

        
    def queryFinishedSlot(self, query):
        #set the size of the columns again once all resources have been added, otherwise some columns don't have the
        #right size for the contents they contain
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        


    def createTable(self):
        self.table = QTableView()
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setWordWrap(True)
        self.table.setDragEnabled(False)
        self.table.setAcceptDrops(False)
        self.table.setDropIndicatorShown(False)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        #if not self.searchDialogMode:
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        #else:
        #    self.table.setSelectionMode(QTableWidget.SingleSelection)
            
        
        self.table.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.table.setSortingEnabled(True)
        self.table.setShowGrid(True)
        self.table.verticalHeader().setVisible(False)
       
        
        if not self.dialogMode:
            QObject.connect(self.table, SIGNAL("activated (const QModelIndex&)"), self.activated)

        QObject.connect(self.table, SIGNAL("customContextMenuRequested (const QPoint&)"), self.showContextMenu)


    def createModel(self):
        self.model = ResourcesTableModel(self)
        self.model.setHeaders([i18n("Name"), i18n("Date"), i18n("Type")])
        
        if self.resources:
            self.model.setResources(self.resources)
            #self.model.setHeaders(["Full Name", "Creation Date", "Last Update"])
            

    def installModels(self, excludeList=None):
        self.createModel()
        self.proxyModel = ResourcesSortFilterProxyModel(None, excludeList)
        self.proxyModel.setSourceModel(self.model)
        self.proxyModel.setDynamicSortFilter(True)
        self.table.setModel(self.proxyModel)
        
        
    
    def selectedResources(self):
        selection = []
        selindexes = self.table.selectionModel().selectedRows()
        for selindex in selindexes:
            sourceIndex = self.table.model().mapToSource(selindex)
            selitem = self.table.model().sourceModel().resourceAt(sourceIndex.row())
            selection.append(selitem)
        return selection
        

    def showContextMenu(self, points):
        index = self.table.indexAt(points)
        selection = []
        if index.isValid():
            #convert the proxy index to the source index
            #see http://doc.trolltech.com/4.6/qsortfilterproxymodel.html
            sourceIndex = self.table.model().mapToSource(index)
            item = self.table.model().sourceModel().resourceAt(sourceIndex.row())
            if item:
                selection = self.selectedResources() 
                #make sure the item below the mouse is added to the selection even though
                #the row is not selected
                try:
                    selection.index(item)
                except:
                    selection.append(item)
                    
        menu = self.createContextMenu(selection)
        pos = self.table.mapToGlobal(points)
        menu.exec_(pos)

    def activated(self, index):
        if index.isValid():
            sindex = self.table.model().mapToSource(index)
            resource = self.table.model().sourceModel().resourceAt(sindex.row())
            self.mainWindow.openResource(uri=resource.resourceUri())
      
    def createContextMenu(self, selection):
        return ResourceContextMenu(self, selection)
    
        
    def addResource(self, resource):
        index = self.table.model().sourceModel().addResource(resource)
        
    def removeResource(self, uri):
        #self.table.setRowCount(self.table.rowCount() -1 1)
        #self.table.setItem(self.table.rowCount() - 1, 0, item)
        self.table.model().sourceModel().removeResource(uri)

    #abstract
    def processAction(self, key, selectedUris):
#        if hasattr(self, "appDB") and self.appDB.has_key(key):
#            cmd1 = [self.appDB[key], self.appDB['URL']]
#            p1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE)
#            p1.poll()
#            #system('%s %s' % ())
#            return True
        if key == i18n('&Open in new tab'):
            for uri in selectedUris:
                self.mainWindow.openResource(uri, newTab=True)
        elif key == i18n('&Delete'):
            for uri in selectedUris:
                self.mainWindow.removeResource(uri)
        elif key == i18n("Open &file"):
            for uri in selectedUris:
                self.mainWindow.openResourceExternally(uri, True)
        elif key == i18n("Open &page"):
            for uri in selectedUris:
                self.mainWindow.openResourceExternally(uri, False)
        elif key == i18n("&Write e-mail to"):
            self.mainWindow.writeEmail(selectedUris)

        
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


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    contacts = datamanager.findResourcesByType(NCO.Contact)
    
    
    
    model = ResourcesTableModel()
    model.setHeaders(["Full Name", "Creation Date", "Last Update"])

    proxyModel = ResourcesSortFilterProxyModel(app)
    proxyModel.setSourceModel(model)
    proxyModel.setDynamicSortFilter(True)
    
    
    model.setResources(contacts)
    view = QTableView()
    view.setSortingEnabled(True)
    view.sortByColumn(0, Qt.AscendingOrder)
    
    view.setModel(proxyModel)
    view.resizeColumnsToContents()
    view.setWordWrap(True)
    view.setDragEnabled(False)
    view.setAcceptDrops(False)
    view.setDropIndicatorShown(False)
    view.setContextMenuPolicy(Qt.CustomContextMenu)
    view.setAlternatingRowColors(True)
    view.setEditTriggers(QTableWidget.NoEditTriggers)
    #self.table.setSelectionBehavior(QTableWidget.SelectRows)
    view.setDragDropMode(QAbstractItemView.NoDragDrop)
    
    view.setSortingEnabled(True)
    view.setShowGrid(True)
    
    view.show()
    view.verticalHeader().setVisible(False)    
    app.exec_()

