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
from dao import PIMO, datamanager, NFO, NIE
from os import system
from os.path import join
from PyKDE4.soprano import Soprano
from editors.resourcestable import ResourcesTable
from util import gnome_meta, gio_meta, mime
from editors.resourcecontextmenu import ResourceContextMenu


class RelationsTable(ResourcesTable):
    
    def __init__(self, mainWindow=False, dialogMode=False, resource=None):
        self.resource=resource
        super(RelationsTable, self).__init__(mainWindow=mainWindow, dialogMode=dialogMode)
        
        
    def labelHeaders(self):
        return ["Name"]

    def fetchData(self):
        
        if self.resource:
            self.data = datamanager.findRelations(self.resource.uri())
        else:
            self.data = []
  
    def statementAddedSlot(self, statement):
        predicate = statement.predicate().uri()
        if predicate == Soprano.Vocabulary.NAO.isRelated() or predicate == PIMO.isRelated:
            subject = statement.subject().uri()
            object = statement.object().uri()
            if self.resource and subject == self.resource.resourceUri():
                newrelation = Nepomuk.Resource(object)
                self.addResource(newrelation)
            elif object and self.resource and object == self.resource.resourceUri():
                newrelation = Nepomuk.Resource(subject)
                self.addResource(newrelation)
                
        
    def statementRemovedSlot(self, statement):
        subject = statement.subject().uri()
        predicate = statement.predicate().uri()
        object = statement.object().uri()
        
        if predicate == Soprano.Vocabulary.NAO.isRelated() or predicate == PIMO.isRelated:
            self.removeResource(subject.toString())
            self.removeResource(object.toString())

        #if a resource was completely removed, remove it from the relation table as well
        super(RelationsTable, self).statementRemovedSlot(statement)

    def processAction(self, key, resourceUri):
        if super(RelationsTable, self).processAction(key, resourceUri):
            return True
        elif key == 'Unlink from '+self.resource.genericLabel():
            self.mainWindow.unlink(Soprano.Vocabulary.NAO.isRelated(), resourceUri, True)
            self.mainWindow.unlink(PIMO.isRelated, resourceUri, True) 
        
    def createContextMenu(self, selection):
        return RelationsTableContextMenu(self, selection)

class RelationsTableContextMenu(ResourceContextMenu):
    def __init__(self, parent=None, selectedUris=None):
        super(RelationsTableContextMenu, self).__init__(parent=parent, selectedUris=selectedUris)
    
        
    def createActions(self):

        if self.selectedUris:
            self.addOpenAction()
            action = QAction("Unlink from "+self.parent.resource.genericLabel(), self)
            action.setIcon(QIcon(":/nepomuk-small"))
            self.addAction(action)
            if len(self.selectedUris) == 1:
                resource = Nepomuk.Resource(self.selectedUris[0])
                self.parent.addFileLaunchActions(self, resource)
            self.addDeleteAction()
        else:
            #the user right clicked in the empty zone
            
            self.addMenu(self.parent.mainWindow.linkToMenu)
            
