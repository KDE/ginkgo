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
from ginkgo.util import mime
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
            return label
        elif column == 1:
            return object.genericLabel()
        elif column == 2:
            return object.property(Soprano.Vocabulary.NAO.lastModified()).toDateTime()
        elif column == 3:
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
    
    def __init__(self, mainWindow=False, dialog=None, resource=None):
        self.resource = resource
        super(RelationsTable, self).__init__(mainWindow=mainWindow, dialog=dialog, sortColumn=1)
        self.table.horizontalHeader().setResizeMode(0, QHeaderView.Interactive)
        self.table.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)
        self.table.resizeColumnsToContents()


    def createModel(self):
        
        self.model = RelationsTableModel(self)
        self.model.setHeaders([i18n("Relation"), i18n("Title"), i18n("Date"), i18n("Type") ])
        
        if self.resource:
            relations = datamanager.findDirectRelations(self.resource.uri())

            data = []
            for predicate in relations.keys():
                for resource in relations[predicate]:
                    data.append((predicate, resource, True))

            inverseRelations = datamanager.findInverseRelations(self.resource.uri())
            for predicate in inverseRelations.keys():
                for resource in inverseRelations[predicate]:
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
        
    def createContextMenu(self, selection):
        return RelationContextMenu(self, selection)
    
    def setResource(self, resource):
        self.resource = resource


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
            
