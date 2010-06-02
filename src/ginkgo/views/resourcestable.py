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
from ginkgo.dao import datamanager
from ginkgo.ontologies import NFO, NIE, PIMO, NCO
from os import system
from os.path import join
from PyKDE4 import soprano
from PyKDE4.soprano import Soprano
from ginkgo.views.objectcontextmenu import ObjectContextMenu
from ginkgo import *
from datetime import *
from ginkgo.actions import *
import os
import subprocess
   
def getClass(clazz):
    parts = clazz.split('.')
    module = ".".join(parts[:-1])
    module = __import__(module)
    for comp in parts[1:]:
        module = getattr(module, comp)            
    return module

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
                resource = self.objectAt(index.row())
                return self.editor.mainWindow.resourceQIcon(resource)

        elif role == Qt.DisplayRole:
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
                    label = unicode(label)
                    if label.find("#") > 0:
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
                    return QString(label)

    def objectAt(self, row):
        return self.resources[row]
    
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
            resource = self.objectAt(row)
            if resource and (resource.resourceUri() == resourceUri or len(resource.resourceUri().toString()) == 0):
                self.beginRemoveRows(QModelIndex(), row, row)
                self.resources.pop(row)
                self.endRemoveRows()
                break
                
    
    #this slot has to be in the model, not in the table, otherwise when we change the model table
    #(e.g in the labelinputdialog), the slot can possibly be called by other queries which are still running 
    def queryNextReadySlot(self, query):
        
        node = query.binding("r");
        resource = Nepomuk.Resource(node.uri())
        self.addResource(resource)
        #TODO: find the proper way
        if self.resourcestable.dialog and self.resourcestable.dialog.__class__ == getClass("ginkgo.dialogs.livesearchdialog.LiveSearchDialog"):
            self.resourcestable.table.selectionModel().clearSelection()
            self.resourcestable.table.selectRow(0)

        query.next()
          

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
            resource = self.sourceModel().objectAt(sourceRowInt)
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
    - searchDialogMode is used by livesearchdialog.py for live results of matching items below the input line edit
    '''
    def __init__(self, mainWindow=False, resources=None, excludeList=None, dialog=None, sortColumn=None):
        if mainWindow:
            super(ResourcesTable, self).__init__(mainWindow.workarea)
        else:
            super(ResourcesTable, self).__init__()

        self.mainWindow = mainWindow
        self.dialog = dialog
        
        self.excludeList = excludeList
        self.resources = resources
        
        
        model = Nepomuk.ResourceManager.instance().mainModel()
        model.statementAdded.connect(self.statementAddedSlot)
        model.statementRemoved.connect(self.statementRemovedSlot)

        self.createTable()
        self.installModels(excludeList)
        
        if sortColumn == None:
            sortColumn = 0
        
        if sortColumn >= 0:
            self.table.sortByColumn(sortColumn, Qt.AscendingOrder)
        
        self.table.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        self.table.resizeColumnsToContents()

        verticalLayout = QVBoxLayout(self)
        verticalLayout.setObjectName("editor")
        verticalLayout.addWidget(self.table)
        self.setLayout(verticalLayout)


    #abstract
    def statementAddedSlot(self, statement):
        #predicate = statement.predicate().uri()
        pass

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
        if self.mainWindow.currentWorkWidget() is self:
            self.mainWindow.stopQueryAction.setEnabled(False)
        
        
        self._query = None


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
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        
        self.table.setDragDropMode(QAbstractItemView.NoDragDrop)
        self.table.setSortingEnabled(True)
        self.table.setShowGrid(True)
        self.table.verticalHeader().setVisible(False)
        
        self.table.activated.connect(self.activated)
        
        self.table.customContextMenuRequested.connect(self.showContextMenu)


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
        
        
    
    def selectedObjects(self):
        selection = []
        selindexes = self.table.selectionModel().selectedRows()
        for selindex in selindexes:
            sourceIndex = self.table.model().mapToSource(selindex)
            selitem = self.table.model().sourceModel().objectAt(sourceIndex.row())
            selection.append(selitem)
        return selection
        

    def showContextMenu(self, points):
        index = self.table.indexAt(points)
        selection = []
        if index.isValid():
            #convert the proxy index to the source index
            #see http://doc.trolltech.com/4.6/qsortfilterproxymodel.html
            sourceIndex = self.table.model().mapToSource(index)
            item = self.table.model().sourceModel().objectAt(sourceIndex.row())
            if item:
                selection = self.selectedObjects() 
                #make sure the item below the mouse is added to the selection even though
                #the row is not selected
                try:
                    selection.index(item)
                except:
                    selection.append(item)
                    
        menu = self.createContextMenu(index, selection)
        if menu:
            pos = self.table.mapToGlobal(points)
            menu.exec_(pos)

    def activated(self, index):
        if index.isValid() and self.isActivableColumn(index.column()):
            sindex = self.table.model().mapToSource(index)
            resource = self.table.model().sourceModel().resourceAt(sindex.row())
            if not self.dialog:
                self.mainWindow.openResource(uri=resource.resourceUri())
            else:
                self.dialog.accept()
                
    def isActivableColumn(self, column):
        return True
      
    def createContextMenu(self, index, selection):
        return ObjectContextMenu(self, selection)
    
        
    def addResource(self, resource):
        index = self.table.model().sourceModel().addResource(resource)
        
    def removeResource(self, uri):
        #self.table.setRowCount(self.table.rowCount() -1 1)
        #self.table.setItem(self.table.rowCount() - 1, 0, item)
        self.table.model().sourceModel().removeResource(uri)

    def processAction(self, key, selectedResources):
        if key == OPEN_IN_NEW_TAB:
            for uri in selectedResources:
                self.mainWindow.openResource(uri, newTab=True)
        elif key == DELETE:
            for uri in selectedResources:
                self.mainWindow.removeResource(uri)
        elif key == OPEN_FILE:
            for uri in selectedResources:
                self.mainWindow.openResourceExternally(uri, True)
        elif key == OPEN_PAGE:
            for uri in selectedResources:
                self.mainWindow.openResourceExternally(uri, False)
        elif key == WRITE_EMAIL:
            self.mainWindow.writeEmail(selectedResources)
        elif key == SET_AS_CONTEXT:
            resource = Nepomuk.Resource(selectedResources[0])
            self.mainWindow.setResourceAsContext(resource)


    def closeEvent(self, event):
        print "closing..."
        try:
            print event
        except Exception, e:
            print "An error occurred: '%s.'" % str(e)


    def setQuery(self, query):
        self._query = query

    def query(self):
        return self._query

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

