#!/usr/bin/env python
#
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

from ginkgo.dao import datamanager
from ginkgo.ontologies import PIMO
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdeui import *
from PyKDE4.nepomuk import Nepomuk
from PyKDE4 import soprano
from PyKDE4.soprano import Soprano
from PyKDE4.kdecore import i18n
from ginkgo.views.objectcontextmenu import ObjectContextMenu
from ginkgo.actions import *

class ResourceNode(object):
    def __init__(self, data, parent=None):
        self.parentNode = parent
        self.nodeData = data
        self.children = []

    def addChild(self, child):
        self.children.append(child)

    def child(self, row):
        return self.children[row]

    def childrenCount(self):
        return len(self.children)

    def parent(self):
        return self.parentNode

    def row(self):
        if self.parentNode:
            return self.parentNode.children.index(self)

        return 0

    def insertChildren(self, position, count, columns):
        if position < 0 or position > len(self.children):
            return False

        for row in range(count):
            data = [None for v in range(columns)]
            item = ResourceNode(data, self)
            self.children.insert(position, item)

        return True

    def removeChildren(self, position, count):
        if position < 0 or position + count > len(self.children):
            return False

        for row in range(count):
            self.children.pop(position)

        return True
    
    

class ResourcesTreeModel(QAbstractItemModel):
    def __init__(self, parent=None, mainWindow=None):
        super(ResourcesTreeModel, self).__init__(parent)
        self.headerData = ["Name","Ontology", "Description"]
        self.mainWindow = mainWindow
        

    def columnCount(self, parent):
        if parent.isValid():
            #return parent.internalPointer().columnCount()
            return len(self.headerData)
            
        else:
            return len(self.headerData)

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Qt.DecorationRole:
            item = index.internalPointer()
            type = item.nodeData
            if self.mainWindow and index.column() == 0:
                return self.mainWindow.typeQIcon(type.uri())
            else:
                return None
        
        elif role == Qt.DisplayRole:
            item = index.internalPointer()
            #print item.nodeData.label("")
            if index.column() == 0:
                #return item.nodeData.name()
#                if item.label:
#                    return item.label
#                else:
#                    return item.nodeData.name()
                return item.nodeData.genericLabel()
            elif index.column() ==1:
                return datamanager.uriToOntologyLabel(item.nodeData.resourceUri())
                
            elif index.column() == 2:
                desc=  item.nodeData.genericDescription()
                desc = desc.replace("\n","")
                return desc

        else:
            return None
            
    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headerData[section]

        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentNode = self.rootItem
        else:
            parentNode = parent.internalPointer()

        childNode = parentNode.child(row)
        if childNode:
            return self.createIndex(row, column, childNode)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childNode = index.internalPointer()
        parentNode = childNode.parent()

        if parentNode == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentNode.row(), 0, parentNode)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childrenCount()

    def getItem(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self.rootItem
    

    def removeRows(self, position, rows, parent=QModelIndex()):
        parentItem = self.getItem(parent)

        self.beginRemoveRows(parent, position, position + rows - 1)
        success = parentItem.removeChildren(position, rows)
        self.endRemoveRows()

        return success

    def loadData(self, rootType = PIMO.Thing):

        #type = Soprano.Vocabulary.RDFS.Resource()
        #rootClass = Nepomuk.Types.Class(rootType)
        
        Nepomuk.ResourceManager.instance().clearCache()
        
        rootTypeResource = Nepomuk.Resource(rootType)
        
        self.rootItem = ResourceNode(rootTypeResource)
        self.addChildren(self.rootItem, rootTypeResource)
            
        
    def addChildren(self, node, typeResource):

        typeClass = Nepomuk.Types.Class(typeResource.resourceUri())
        
        subClasses = typeClass.subClasses()
        tuples = []
        for subClass in subClasses:
            #TODO: why subClass are not instance of Resource?
            #TODO: why pimo:Thing is not listed in the subClasses of itself while it is in the database
            #don't add to the children list a class that subclasses itself
            if typeResource.resourceUri() == subClass.uri():
                continue
            subClassResource = Nepomuk.Resource(subClass.uri())
            
            tuples.append((subClassResource, subClassResource.genericLabel()))
        
        sortedResources = sorted(tuples, key=lambda tuple: tuple[1])

        
        for tuple in sortedResources:
            
            child = ResourceNode(tuple[0], node)
            node.addChild(child)
            self.addChildren(child, tuple[0])



class ResourcesTree(QWidget):
    '''
    - makeActions was added for handling the case of the tree embedded in a dialog, from which we don't want a context menu
    '''
    
    def __init__(self, mainWindow=False, makeActions=False):
        super(ResourcesTree, self).__init__()
        
        self.mainWindow = mainWindow
        
        verticalLayout = QVBoxLayout(self)
        verticalLayout.setObjectName("editor")
        
        self.tree = QTreeView(mainWindow)
        
        verticalLayout.addWidget(self.tree)
        self.setLayout(verticalLayout)
        self.tree.setItemDelegate(ResourceNodeDelegate())

        model = ResourcesTreeModel(mainWindow=self.mainWindow)
        model.loadData()
        self.tree.setModel(model)
        self.tree.setColumnWidth(0, 300)

        #won't work properly except if 1) used from the __main__ method, 2) this class (not from ginkgo.py: segfault)
        #proxyModel = TypesSortFilterProxyModel(None)
        #proxyModel.setDynamicSortFilter(True)
        #proxyModel.setSourceModel(model)
        #self.tree.setSortingEnabled(True) 
        #self.tree.sortByColumn(0, Qt.AscendingOrder) 

        smodel = Nepomuk.ResourceManager.instance().mainModel()
        smodel.statementAdded.connect(self.statementAddedSlot)
        smodel.statementRemoved.connect(self.statementRemovedSlot)            
        
        
        if makeActions:
            self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
            self.tree.customContextMenuRequested.connect(self.showContextMenu)
            #self.tree.activated.connect(self.activateResource)
            #self.connect(mainWindow, SIGNAL('taskHierarchyUpdated'), self.refresh)

#            model = ResourcesTreeModel()
#            QMetaObject.connectSlotsByName(self)




    def statementAddedSlot(self, statement):
        predicate = statement.predicate().uri()
        #TODO: the tree get actually refreshed twice due to each newly class being a subclass of itself 
        if predicate == soprano.Soprano.Vocabulary.RDFS.subClassOf():
            self.refresh()

    def statementRemovedSlot(self, statement):
        subject = statement.subject().uri()
        predicate = statement.predicate().uri()
        #TODO: check
        if predicate == soprano.Soprano.Vocabulary.RDFS.subClassOf():
            print "removed a subclass relation..."

    def refresh(self):
        typeClass = Nepomuk.Types.Class(PIMO.Thing)
        
        for sc in typeClass.subClasses():
            res = Nepomuk.Resource(sc.uri())
             
        model = ResourcesTreeModel(mainWindow=self.mainWindow)
        model.loadData()
        self.tree.setModel(model)

        
    def showContextMenu(self, points):
        
        index = self.tree.indexAt(points)
        if index:
            item = self.tree.model().getItem(index)
            if item:
                menu = TypesContextMenu(self, resourceUri=item.nodeData.resourceUri())
                pos = self.tree.mapToGlobal(points)
                menu.exec_(pos)
            
    def processAction(self, key, selectedUris):
        if key == NEW_INSTANCE:
            self.mainWindow.newResource(selectedUris[0])
            
        elif key == NEW_SUBTYPE:
            self.mainWindow.newType(superClassUri=selectedUris[0])
        
        elif key == OPEN_IN_NEW_TAB:
            self.mainWindow.openResource(uri=selectedUris[0], newTab=True)
        
        elif key == DELETE:
            for uri in selectedUris:
                self.mainWindow.removeResource(uri)
        
        elif key == ADD_TO_PLACES:
            for uri in selectedUris:
                self.mainWindow.addToPlaces(uri)
                
        elif key == NEW_TYPE:
            self.mainWindow.newType(superClassUri=selectedUris[0])

class TypesSortFilterProxyModel(QSortFilterProxyModel):
 
    def __init__(self, parent):
        super(TypesSortFilterProxyModel, self).__init__(parent)

    def filterAcceptsRow(self, sourceRowInt, sourceParentModelIndex):

        return True
    
    def lessThan(self, index1, index2):
        data1 = self.sourceModel().data(index1, Qt.DisplayRole)
        data2 = self.sourceModel().data(index2, Qt.DisplayRole)
        return QString.localeAwareCompare(data1, data2)
    
#    def parent(self, index):
#        return self.sourceModel().parent(index) 


class ResourceNodeDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(QItemDelegate, self).__init__(parent)
    

    def sizeHint(self, option, index): 
        return QSize(0, 25);


class TypesContextMenu(ObjectContextMenu):
    def __init__(self, parent=None, resourceUri=False, deleteAction=False):
        self.deleteAction = deleteAction
        super(TypesContextMenu, self).__init__(parent, [resourceUri])
        
    def createActions(self):
        if self.selectedResources[0] == PIMO.Thing:
            action = QAction(i18n("&New type"), self)
            action.setProperty("key", QVariant(NEW_TYPE))
            self.addAction(action)
        else:
            action = QAction(i18n("New &instance"), self)
            action.setProperty("key",QVariant(NEW_INSTANCE))
            self.addAction(action)
            self.addSeparator()
            self.addOpenAction()
            action = QAction(i18n("&Add to places"), self)
            action.setProperty("key",QVariant(ADD_TO_PLACES))
            self.addAction(action)
            nodeClass = Nepomuk.Types.Class(self.selectedResources[0])
            pimoThingClass = Nepomuk.Types.Class(PIMO.Thing)
            if nodeClass.isSubClassOf(pimoThingClass):
                self.addSeparator()
                action = QAction(i18n("&New sub-type"), self)
                action.setProperty("key", QVariant(NEW_SUBTYPE))
                self.addAction(action)
#        self.addDeleteAction()
        

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    widget = QWidget()
    treeview = ResourcesTree(mainWindow=widget)
    treeview.setWindowTitle("Resources Tree")

   
    
    treeview.show()


    
    app.exec_()