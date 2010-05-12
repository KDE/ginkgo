#!/usr/bin/env python

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

from dao import TMO, datamanager, PIMO
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdeui import *
from PyKDE4.nepomuk import Nepomuk
from PyKDE4 import soprano
from editors.resourcecontextmenu import ResourceContextMenu


class TreeItem(object):
    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        #return len(self.itemData)
        return 1

    def data(self, column):
        try:
            return self.itemData
        except IndexError:
            return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0

    def insertChildren(self, position, count, columns):
        if position < 0 or position > len(self.childItems):
            return False

        for row in range(count):
            data = [None for v in range(columns)]
            item = TreeItem(data, self)
            self.childItems.insert(position, item)

        return True

    def removeChildren(self, position, count):
        if position < 0 or position + count > len(self.childItems):
            return False

        for row in range(count):
            self.childItems.pop(position)

        return True



class TreeModel(QAbstractItemModel):
    def __init__(self, ginkgo, parent=None, hiddenTask=None):
        super(TreeModel, self).__init__(parent)
        self.ginkgo = ginkgo
        self.setupModelData(hiddenTask)

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
            resource = item.data(index.column())
            #return self.ginkgo.resourceIcon(resource)
            return QIcon(":/task-small")
        
        elif role == Qt.DisplayRole:
            item = index.internalPointer()
            return item.data(index.column()).genericLabel()
        else:
            return None
            
    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.rootItem.data(section)

        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

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

    def setupModelData(self, hiddenTask):

        self.rootItem = TreeItem("Name")
        tasks = datamanager.findRootTasks()
        self.addChildren(self.rootItem, tasks, hiddenTask)
            

    def addChildren(self, node, tasks, hiddenTask):
        for task in tasks:
            if hiddenTask is None or not task.uri() == hiddenTask.uri(): 
                child = TreeItem(task, node)
                node.appendChild(child)
                subtasks = datamanager.findSubTasks(task.uri())
                self.addChildren(child, subtasks, hiddenTask)
            
            
            #for subtask in subtasks:
            #    node.appendChild(TreeItem(subtask, node))



class TaskTreeView(QTreeView):
    def __init__(self, ginkgo, hiddenTask=None):
        super(TaskTreeView, self).__init__()
        model = TreeModel(ginkgo, hiddenTask=hiddenTask)
        self.setModel(model)
        self.setWindowTitle("Task Tree")
        self.setDragEnabled(False)
        self.setAcceptDrops(False)
        #self.setContextMenuPolicy(Qt.CustomContextMenu)
        #self.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.setSortingEnabled(True)
        delegate = ItemDelegate()
        self.setItemDelegate(delegate)


class ItemDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(QItemDelegate, self).__init__(parent)
    

    def sizeHint(self, option, index): 
        return QSize(0, 25);
    
    def icon(self, column):
        return QIcon(":/task-16")
        
class TaskTree(QWidget):
    '''
    - makeActions was added for handling the case of the tree embedded in a dialog, from which we don't want a context menu
    '''
    
    def __init__(self, mainWindow=False, makeActions=False, hiddenTask=None):
        super(TaskTree, self).__init__()
        
        self.mainWindow = mainWindow
        self.nepomukType = PIMO.Task
        
        verticalLayout = QVBoxLayout(self)
        verticalLayout.setObjectName("editor")
        self.tasktree = TaskTreeView(mainWindow, hiddenTask)
        verticalLayout.addWidget(self.tasktree)
        self.setLayout(verticalLayout)
        
        if makeActions:
            self.tasktree.setContextMenuPolicy(Qt.CustomContextMenu)
            self.tasktree.customContextMenuRequested.connect(self.showContextMenu)
            self.tasktree.activated.connect(self.activateResource)
            self.connect(mainWindow, SIGNAL('taskHierarchyUpdated'), self.refresh)

            model = Nepomuk.ResourceManager.instance().mainModel()
            model.statementAdded.connect(self.statementAddedSlot)
            model.statementRemoved.connect(self.statementRemovedSlot)            
            QMetaObject.connectSlotsByName(self)


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
        
        index = self.tasktree.indexAt(points)
        if index:
            #selection=  item.data(Qt.UserRole).toPyObject()
            item = self.tasktree.model().getItem(index)
            task = item.data(0)
            
            if type(task) is Nepomuk.Resource:
                menu = TaskContextMenu(self, resourceUri=task.uri(), deleteAction=item.childCount() == 0)
                pos = self.tasktree.mapToGlobal(points)
                menu.exec_(pos)

    def activateResource(self, index):
        if index.isValid():
            item = self.tasktree.model().getItem(index)
            #selection=  item.data(Qt.UserRole).toPyObject()
            self.mainWindow.openResource(uri=item.data(0).uri())


    def refresh(self):
        
        model = TreeModel(self.mainWindow)
        self.tasktree.setModel(model)


    def processAction(self, key, selectedUris):
        if key == '&New sub-task':
            self.mainWindow.newTask(superTaskUri=selectedUris[0])
        elif key == '&Open in new tab':
            self.mainWindow.openResource(uri=selectedUris[0], newTab=True)
        elif key == '&Delete':
            self.mainWindow.removeResource(selectedUris[0])

#    def resourceCreatedSlot(self, resource):
#        
#        model = TreeModel(self.mainWindow)
#        self.tasktree.setModel(model)
#
#    def resourceRemovedSlot(self, uri):
#        
##        for row in range(self.table.rowCount()):
##            item = self.table.item(row, 0)
##            if item:
##                resource =  item.data(Qt.UserRole).toPyObject()
##                if resource == uri:
##                    self.table.removeRow(row)
#        index = self.tasktree.selectionModel().currentIndex()
#        model = self.tasktree.model()
#        model.removeRow(index.row(), index.parent())
#        #self.updateActions()


class TaskContextMenu(ResourceContextMenu):
    def __init__(self, parent=None, resourceUri=False, deleteAction=False):
        self.deleteAction = deleteAction
        super(TaskContextMenu, self).__init__(parent=parent, selectedUris=[resourceUri])
        

    def createActions(self):
        self.addOpenAction()
        action = QAction("New sub-task", self)
        action.setIcon(KIcon("view-task-add"))
        action.setProperty("nepomukType", PIMO.Task)
        self.addAction(action)
        if self.deleteAction:
            self.addDeleteAction()

        

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    view = TaskTree()
    view.show()
    
    sys.exit(app.exec_())

