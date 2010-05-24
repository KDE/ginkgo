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
from ginkgo.views.resourcecontextmenu import ResourceContextMenu


            
class RelationsTable(ResourcesTable):
    
    def __init__(self, mainWindow=False, dialog=None, resource=None):
        self.resource = resource
        super(RelationsTable, self).__init__(mainWindow=mainWindow, dialog=dialog)
        #override the column policy
#        self.table.horizontalHeader().setResizeMode(0,QHeaderView.Interactive)
#        self.table.horizontalHeader().setStretchLastSection(True)
#        self.table.resizeColumnsToContents()


    def createModel(self):
        
        self.model = ResourcesTableModel(self)
        self.model.setHeaders([i18n("Name"), i18n("Date"), i18n("Type") ])
        
        if self.resource:
            resources = datamanager.findRelations(self.resource.uri())
            #TODO: find built-in conversion
            ressourceArray = []
            for elt in resources:
                ressourceArray.append(elt)
            self.model.setResources(ressourceArray)

  
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
            self.removeResource(subject)
            self.removeResource(object)

        #if a resource was completely removed, remove it from the relation table as well
        super(RelationsTable, self).statementRemovedSlot(statement)

    def processAction(self, key, resourceUri):
        if super(RelationsTable, self).processAction(key, resourceUri):
            return True
        elif self.resource and key == i18n("&Unlink from %1", self.resource.genericLabel()):
            self.mainWindow.unlink(Soprano.Vocabulary.NAO.isRelated(), resourceUri, True)
            self.mainWindow.unlink(PIMO.isRelated, resourceUri, True) 
        
    def createContextMenu(self, selection):
        return RelationsTableContextMenu(self, selection)
    
    def setResource(self, resource):
        self.resource = resource

class RelationsTableContextMenu(ResourceContextMenu):
    def __init__(self, parent=None, selectedUris=None):
        super(RelationsTableContextMenu, self).__init__(parent=parent, selectedUris=selectedUris)
    
        
    def createActions(self):

        if self.selectedUris:
            self.addOpenAction()
            self.addExternalOpenAction()
            
            action = QAction(i18n("&Unlink from %1", self.parent.resource.genericLabel()), self)
            action.setIcon(KIcon("nepomuk"))
            self.addAction(action)
            self.addSendMailAction()
                
            self.addDeleteAction()
        else:
            #the user right clicked in the empty zone
            
            self.addMenu(self.parent.mainWindow.linkToMenu)
            
