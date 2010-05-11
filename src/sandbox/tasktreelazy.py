#http://stackoverflow.com/questions/1185021/is-there-a-bug-in-my-code-for-populating-a-qtreeview

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from dao import datamanager, TMO, PIMO
import sys
 
class Node(object):
    hasFinishedLoading = False
 
    def __init__(self, value, parent=None, depth=0):
        self.parent = parent
        self.children = []
        self.depth = depth
        self.value = value
 
    def canFetchMore(self):
        return not self.hasFinishedLoading
 
    def fetchMore(self):
        
#        if len(source) == 5:
            
        #source = source[:5]
        if self.parent is None:
            data = datamanager.findResourcesByType(TMO.Task)
            self.children.extend(Node(i.genericLabel(), self, self.depth + 1) for i in data)
            self.hasFinishedLoading = True
        else:
            data = datamanager.findResourcesByType(PIMO.Person)
            self.children.extend(Node(i.genericLabel(), self, self.depth + 1) for i in data)
            self.hasFinishedLoading = True
 
    def data(self, column, role):
        if role == Qt.DisplayRole:
            return QVariant(self.value)
        return QVariant()
 
    def __len__(self):
        return len(self.children)
 
class Model(QAbstractItemModel):
    def __init__(self):
        super(Model, self).__init__()
        self.rootNode = Node(None, None, -1)
 
    def canFetchMore(self, parent):
        if parent.isValid():
            node = parent.internalPointer()
        else:
            node = self.rootNode
        return node.canFetchMore()
 
    def hasChildren(self, index):
        if not index.isValid():
            return True
        return index.internalPointer().depth < 3
 
    def fetchMore(self, parent):
        # fetchMore() should theoretically be enclosed by the other calls
        if not parent.isValid():
            node = self.rootNode
        else:
            node = parent.internalPointer()
 
        self.beginInsertRows(parent, len(node), len(node) + 4)
        node.fetchMore()
        self.endInsertRows()
 
    def rowCount(self, modelIndex=QModelIndex()):
        if not modelIndex.isValid():
            node = self.rootNode
        else:
            node = modelIndex.internalPointer()
        return len(node)
 
    def columnCount(self, modelIndex=QModelIndex()):
        return 1
 
    def data(self, modelIndex, role=Qt.DisplayRole):
        return modelIndex.internalPointer().data(modelIndex.column(), role)
 
    def index(self, row, column, parent=QModelIndex()):
        if not parent.isValid():
            parent = self.rootNode
        else:
            parent = parent.internalPointer()
        
        return self.createIndex(row, column, parent.children[row]) 
 
    def parent(self, index):
        node = index.internalPointer()
        if node.parent is self.rootNode:
            return QModelIndex()
        row = node.parent.children.index(node)
        return self.createIndex(row, 0, node.parent)
 
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return QVariant(u"Name")
        
        return QVariant()
 
app = QApplication(sys.argv)
 
treeView = QTreeView()
 
model = Model()
treeView.setModel(model)
 
treeView.show()
app.exec_()