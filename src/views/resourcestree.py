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

from dao import datamanager
from ontologies import PIMO
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdeui import *
from PyKDE4.nepomuk import Nepomuk
from PyKDE4 import soprano
from PyKDE4.soprano import Soprano
from PyKDE4.kdecore import i18n
from views.resourcecontextmenu import ResourceContextMenu


class ResourceNode(object):
    def __init__(self, data, label=None, parent=None):
        self.parentNode = parent
        self.nodeData = data
        self.label = label
        self.children = []

    def addChild(self, child):
        self.children.append(child)

    def child(self, row):
        return self.children[row]

    def childrenCount(self):
        return len(self.children)

    def columnCount(self):
        return 1

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
        self.headerData = ["Name","Description"]
        self.mainWindow = mainWindow
        

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Qt.DecorationRole:
            item = index.internalPointer()
            type = item.nodeData
            if self.mainWindow:
                return self.mainWindow.typeQIcon(type.uri())
            else:
                return None
        
        elif role == Qt.DisplayRole:
            item = index.internalPointer()
            #print item.nodeData.label("")
            if index.column() == 0:
                #return item.nodeData.name()
                if item.label:
                    return item.label
                else:
                    return item.nodeData.name()
#            elif index.column() ==1:
#                return item.nodeData.comment(QString())
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
        rootClass = Nepomuk.Types.Class(rootType)
        
        self.rootItem = ResourceNode(rootClass)
        self.addChildren(self.rootItem, rootClass)
            

    def addChildren(self, node, typeClass):
        
        subClasses = typeClass.subClasses()
        tuples = []
        for subClass in subClasses:
            #TODO: why subClass are not instance of Resource?
            subClassResource = Nepomuk.Resource(subClass.uri())
            tuples.append((subClass, subClassResource.genericLabel()))
        
        sortedSubClasses = sorted(tuples, key=lambda tuple: tuple[1])
        
        for tuple in sortedSubClasses:
            child = ResourceNode(tuple[0], tuple[1], node)
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

        #won't work properly except if 1) used from the __main__ method, 2) this class (not from ginkgo.py: segfault)
        #proxyModel = TypesSortFilterProxyModel(None)
        #proxyModel.setDynamicSortFilter(True)
        #proxyModel.setSourceModel(model)
        #self.tree.setSortingEnabled(True) 
        #self.tree.sortByColumn(0, Qt.AscendingOrder) 

        
        
        if makeActions:
            self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
            self.tree.customContextMenuRequested.connect(self.showContextMenu)
            #self.tree.activated.connect(self.activateResource)
            #self.connect(mainWindow, SIGNAL('taskHierarchyUpdated'), self.refresh)

#            model = ResourcesTreeModel()
#            model = Nepomuk.ResourceManager.instance().mainModel()
#            model.statementAdded.connect(self.statementAddedSlot)
#            model.statementRemoved.connect(self.statementRemovedSlot)            
#            QMetaObject.connectSlotsByName(self)




    def statementAddedSlot(self, statement):
        predicate = statement.predicate().uri()
        if predicate == soprano.Soprano.Vocabulary.RDF.type():
            object = statement.object().uri()
            if object == self.nepomukType:
                self.refresh()

    def statementRemovedSlot(self, statement):
        predicate = statement.predicate().uri()
        #TODO: check
        if predicate and len(predicate.toString()) == 0:
            self.refresh()

    def showContextMenu(self, points):
        
        index = self.tree.indexAt(points)
        if index:
            item = self.tree.model().getItem(index)
            menu = TypesContextMenu(self, resourceUri=item.nodeData.uri())
            pos = self.tree.mapToGlobal(points)
            menu.exec_(pos)
            
    def processAction(self, key, selectedUris):
        if key == i18n('&New sub-type'):
            self.mainWindow.newSubType(superTypeUri=selectedUris[0])
        
        elif key == i18n('&Open in new tab'):
            self.mainWindow.openResource(uri=selectedUris[0], newTab=True)
        
        elif key == i18n("&Delete"):
            for uri in selectedUris:
                self.mainWindow.removeResource(uri)
        elif key == i18n("&Add to places"):
            for uri in selectedUris:
                self.mainWindow.addToPlaces(uri)

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


class TypesContextMenu(ResourceContextMenu):
    def __init__(self, parent=None, resourceUri=False, deleteAction=False):
        self.deleteAction = deleteAction
        super(TypesContextMenu, self).__init__(parent=parent, selectedUris=[resourceUri])
        
    def createActions(self):
        self.addOpenAction()
        action = QAction(i18n("&Add to places"), self)
        self.addAction(action)
        nodeClass = Nepomuk.Types.Class(self.selectedUris[0])
        pimoThingClass = Nepomuk.Types.Class(PIMO.Thing)
        if nodeClass.isSubClassOf(pimoThingClass):
            action = QAction(i18n("&New sub-type"), self)
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