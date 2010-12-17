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


class RelationsTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super(RelationsTableModel, self).__init__(parent)
        self.relations = []
        self.editor = parent
    
    def rowCount(self, index):
        return len(self.relations)
    
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
            elif index.column() == 3:
                return Qt.AlignLeft | Qt.AlignVCenter

        elif role == Qt.DisplayRole:
            return self.itemAt(index)
        
        elif role == Qt.DecorationRole:
            if index.column() == 0:
                relation = self.relations[index.row()]
                direct = relation[2]
                if direct: 
                    return QIcon("/usr/share/icons/oxygen/16x16/actions/draw-triangle2.png")
                else:
                    return QIcon("/usr/share/icons/oxygen/16x16/actions/draw-triangle1.png")

            elif index.column() == 1:
                relation = self.relations[index.row()]
                object = relation[1] 
                return self.editor.mainWindow.resourceQIcon(object)

        return QVariant()

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            return self.headers[section]
        else:
            return None


    def itemAt(self, index):
        relation = self.relations[index.row()]
        predicate = relation[0]
        object = relation[1] 
        direction = relation[2]
        column = index.column()
        if column == 0:
            label = predicate.label("en")
            #return label
            return ""
        elif column == 1:
            label = unicode(object.genericLabel())
            if len(label) == 0:
                return object.resourceUri().toString()
            return label
            
        elif column == 3:
            dt = object.property(Soprano.Vocabulary.NAO.lastModified()).toDateTime()
            return dt.toString("dd/MM/yyyy")
        elif column == 2:
            for type in object.types():
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
        return self.relations[row]

    def resourceAt(self, row):
        return self.relations[row][1]
    
    def setRelations(self, relations):
        self.relations = relations
        
    def setHeaders(self, headers):
        self.headers = headers
        
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if index.column() == 0:
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index))
        
    #bool QAbstractItemModel::insertRows ( int row, int count, const QModelIndex & parent = QModelIndex() )
    def addRelation(self, predicate, target, direct):
        self.beginInsertRows(QModelIndex(), len(self.relations), len(self.relations))
        self.relations.append((predicate, target, direct))
        self.endInsertRows()
        
    def removeRelation(self, subject, predicate, target):
        for row in range(len(self.relations)):
            relation = self.objectAt(row)
            if relation and (relation[0] == predicate and relation[1] == target):
                self.beginRemoveRows(QModelIndex(), row, row)
                self.relations.pop(row)
                self.endRemoveRows()
                break
            elif relation and (relation[0] == predicate and relation[1] == subject):
                self.beginRemoveRows(QModelIndex(), row, row)
                self.relations.pop(row)
                self.endRemoveRows()
                break
                
            
class RelationsTable(ResourcesTable):
    
    def __init__(self, mainWindow=False, editor=None, dialog=None, resource=None):
        self.resource = resource
        self.editor = editor
        super(RelationsTable, self).__init__(mainWindow=mainWindow, dialog=dialog, sortColumn=2)
        
        #make it editable
        self.table.setEditTriggers(QTableWidget.SelectedClicked | QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        #self.table.setSelectionBehavior(QTableWidget.SelectItems)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        #self.table.setSelectionMode(QTableWidget.ExtendedSelection)

        
        self.table.horizontalHeader().setResizeMode(0, QHeaderView.Interactive)
        self.table.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)
        #self.table.setItemDelegate(RelationDelegate(self))
        self.table.resizeColumnsToContents()
        

    def createModel(self):
        
        self.model = RelationsTableModel(self)
        #self.model.setHeaders([i18n("Relation"), i18n("Title"), i18n("Date"), i18n("Type") ])
        self.model.setHeaders(["", i18n("Title"), i18n("Type"),i18n("Date") ])
        
        if self.resource:
            relations = datamanager.findDirectRelations(self.resource.uri())

            data = []
            for predicate in relations.keys():
                for resource in relations[predicate]:
                    data.append((predicate, resource, True))

            inverseRelations = datamanager.findInverseRelations(self.resource.uri())
            for tuple in inverseRelations:
                resource = tuple[0]
                predicate = tuple[1]
                #for resource in inverseRelations[predicate]:
                #TODO: see why we get some resources with a void predicate sometimes
                if predicate and predicate.uri() and len(str(predicate.uri().toString())) > 0:
                    data.append((predicate, resource, False))
            
            self.model.setRelations(data)
        

  
    def processAction(self, key, selectedResources, selectedRelations):
        if super(RelationsTable, self).processAction(key, selectedResources):
            return True
        elif self.resource and key == UNLINK:
            for relation in selectedRelations:
                direct = relation[2]
                predicate = relation[0]
                if direct:
                    subject = self.resource
                    object = relation[1]
                else:
                    subject = relation[1]
                    object = self.resource
                
                self.mainWindow.removeRelation(subject, predicate, object)
                
                #self.mainWindow.unlink(PIMO.isRelated, resourceUri, True) 

#    def showContextMenu(self, index, points):
#        index = self.table.indexAt(points)
#        if index.isValid() and index.column() == 1:
#            super(RelationsTable, self).showContextMenu(points)

    def createContextMenu(self, index, selection):
        if not index.isValid() or index.column() == 1:
            return RelationContextMenu(self, selection)
    
    def setResource(self, resource):
        self.resource = resource
        self.installModels()
        #we don't want the resize method to be moved to installModels, 'cause it causes display problem
        #in the livesearchdialog when results appear progressively
        self.table.resizeColumnsToContents()
        #without the line below, the table does not use the space available
        self.table.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)
        
        self.table.selectionModel().currentChanged.connect(self.selectionChanged)

    def isActivableColumn(self, column):
        if column ==1 or column == 3:
            return True
        return False
        

    def statementAddedSlot(self, statement):
        predicateUri = statement.predicate().uri()
        predicate = Nepomuk.Types.Property(predicateUri)
        
        #if the range of the predicate is a literal, return 
        if not predicate.range().isValid():
            return
        
        #the table doesn't display type relations
        if predicateUri == Soprano.Vocabulary.RDF.type():
            return
        
        subjectUri = statement.subject().uri()
        objectUri = statement.object().uri()
        if self.resource and subjectUri == self.resource.resourceUri():
            #check that the object is a resource, not a literal
            #TODO: improve this check
            if str(objectUri.toString()).find("http://www.w3.org/2001/XMLSchema#") < 0:
                object = Nepomuk.Resource(objectUri)
                self.table.model().sourceModel().addRelation(predicate, object, True)
        elif self.resource and objectUri == self.resource.resourceUri():
            subject = Nepomuk.Resource(subjectUri)
            self.table.model().sourceModel().addRelation(predicate, subject, False)
                
        
    def statementRemovedSlot(self, statement):
        predicateUri = statement.predicate().uri()
        predicate = Nepomuk.Types.Property(predicateUri)
        if not predicate.range().isValid():
            return
        subjectUri = statement.subject().uri()
        objectUri = statement.object().uri()
        subject = Nepomuk.Resource(subjectUri)
        object = Nepomuk.Resource(objectUri)
        
        if self.resource == subject or self.resource == object:
            self.table.model().sourceModel().removeRelation(subject, predicate, object)
        

        #if a resource was completely removed, remove it from the relation table as well
        #super(RelatedsTable, self).statementRemovedSlot(statement)
        
    def selectionChanged(self, selectedIndex, deselectedIndex):
        selectedIndex = self.table.model().mapToSource(selectedIndex)
        #print "selection: %s" % selectedIndex.row()
        selectedResource = self.model.resourceAt(selectedIndex.row())
        label = unicode(selectedResource.genericLabel()).lower()
        #print label
        selections = []
        text = u"%s" % self.editor.toPlainText()
        text = text.lower()
        import re
        starts = [match.start() for match in re.finditer(re.escape(label), text)]
        #print starts
        for start in starts:
            selection = QTextEdit.ExtraSelection() 
            selection.cursor = QTextCursor(self.editor.document())
            selection.cursor.setPosition(start)
            selection.cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor,len(label))
            selection.format.setBackground(Qt.yellow)    
            selections.append(selection)
        
        self.editor.setExtraSelections(selections)                

class RelationContextMenu(ObjectContextMenu):
    def __init__(self, parent=None, selectedRelations=None):
        #The selection contains tuples: predicate, object, direct/inverse
        selectedResources = []
        self.selectedRelations = selectedRelations
        
        for relation in selectedRelations:
            selectedResources.append(relation[1])

        
        super(RelationContextMenu, self).__init__(parent, selectedResources)

    def actionTriggered(self, action):        
        key = action.property("key").toString()
        self.parent.processAction(key, self.selectedResources, self.selectedRelations)
                
    def createActions(self):

        if self.selectedResources:
            self.addOpenAction()
            self.addExternalOpenAction()
            
            self.addSendMailAction()

            #action = QAction(i18n("&Unlink from %1", self.parent.resource.genericLabel()), self)
            action = QAction(i18n("&Remove relation(s)"), self)
            action.setProperty("key", QVariant(UNLINK))
            action.setIcon(KIcon("nepomuk"))
            self.addAction(action)
                
            self.addDeleteAction()
        else:
            #the user right clicked in the empty zone
            
            self.addMenu(self.parent.mainWindow.linkToMenu)
            
class RelationDelegate(QItemDelegate):

    def __init__(self, parent=None):
        super(RelationDelegate, self).__init__(parent)
        self.table = parent
        

    def paint(self, painter, option, index):
        QItemDelegate.paint(self, painter, option, index)


    def sizeHint(self, option, index):
        fm = option.fontMetrics
        if index.column() == 0:
            return QSize(fm.width("is organization member"), fm.height())
        return QItemDelegate.sizeHint(self, option, index)


    def createEditor(self, parent, option, index):
        if index.column() == 0:
            combobox = QComboBox(parent)
            combobox.setEditable(False)
            props = []
            sindex = self.table.table.model().mapToSource(index)
            
            #we list the properties that are compatible with the subject type
            #the subject type depends on the direction of the relation: current resource 
            #is subject or is object of the relation?
            
            currentRelation = index.model().sourceModel().relations[sindex.row()]
            direct = currentRelation[2]
            if direct:
                subject =  self.table.resource
            else:
                subject =  currentRelation[1]

            for property in datamanager.resourceTypesProperties(subject, True, False):
                item = property.label("en") +" ["+datamanager.ontologyAbbreviationForUri(property.uri(), False)+"]"
                props.append((property, item))
                 
            self.sortedProps = sorted(props, key=lambda tuple: tuple[1])            
            
            
            for tuple in self.sortedProps: 
                combobox.addItem(tuple[1], QVariant(str(tuple[0].uri().toString())))
            
            
            return combobox
        else:
            return QItemDelegate.createEditor(self, parent, option,index)


    def commitAndCloseEditor(self):
        editor = self.sender()
#        if isinstance(editor, (QTextEdit, QLineEdit)):
#            self.emit(SIGNAL("commitData(QWidget*)"), editor)
#            self.emit(SIGNAL("closeEditor(QWidget*)"), editor)


    def setEditorData(self, editor, index):

        if index.column() == 0:
            sindex = self.table.table.model().mapToSource(index)
            currentRelation = index.model().sourceModel().relations[sindex.row()]
            predicate = currentRelation[0]
            i = 0
            for relation in self.sortedProps:
                if relation[0].uri().toString() == predicate.uri().toString():
                    editor.setCurrentIndex(i)
                    break
                i = i +1
           
        else:
            QItemDelegate.setEditorData(self, editor, index)


    def setModelData(self, editor, model, index):
        if index.column() == 0:
            sindex = self.table.table.model().mapToSource(index)
            cindex = editor.currentIndex()
            relation = index.model().sourceModel().relations[sindex.row()]
            predicate = relation[0]
            direct = relation[2]
            if direct:
                subject = self.table.resource
                object = relation[1]
            else:
                subject = relation[1]
                object = self.table.resource
            
            newPredicate = self.sortedProps[cindex][0]
            if newPredicate.uri().toString() != predicate.uri().toString():
                self.table.setCursor(Qt.WaitCursor)
                subject.addProperty(newPredicate.uri(), Nepomuk.Variant(object.resourceUri()))
                subject.removeProperty(predicate.uri(), Nepomuk.Variant(object.resourceUri()))
                self.table.unsetCursor()
            #don't do that since the model gets already updated through signal emission
            #index.model().sourceModel().relations[index.row()] = (newPredicate, object, direct)
        else:
            QItemDelegate.setModelData(self, editor, model, index)
            

