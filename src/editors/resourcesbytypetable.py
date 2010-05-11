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
from dao import PIMO, datamanager
from os import system
from os.path import join
from PyKDE4 import soprano
from editors.resourcestable import ResourcesTable
from editors.resourcecontextmenu import ResourceContextMenu

class ResourcesByTypeTable(ResourcesTable):

    def __init__(self, mainWindow=False, dialogMode=False, nepomukType=None, excludeList=None):
        self.nepomukType = nepomukType
        super(ResourcesByTypeTable, self).__init__(mainWindow=mainWindow, dialogMode=dialogMode, excludeList=excludeList)

    def statementAddedSlot(self, statement):
        predicate = statement.predicate().uri()
        if predicate == soprano.Soprano.Vocabulary.RDF.type():
            object = statement.object().uri()
            if object == self.nepomukType:
                subject = statement.subject().uri()
                newresource = Nepomuk.Resource(subject)
                self.addResource(newresource)

    def labelHeaders(self):
        return ["Name"]
  
    def fetchData(self):
        self.data = datamanager.findResourcesByType(self.nepomukType)

    def createContextMenu(self, selection):
        return ResourcesByTypeContextMenu(self, selection)

    def processAction(self, key, resourceUri):
        if super(ResourcesByTypeTable, self).processAction(key, resourceUri):
            return True
        
class ResourcesByTypeContextMenu(ResourceContextMenu):
    def __init__(self, parent=None, selectedUris=None):
        super(ResourcesByTypeContextMenu, self).__init__(parent=parent, selectedUris=selectedUris)
    
    def createActions(self):
        if self.selectedUris:
            self.addOpenAction()
            if len(self.selectedUris) == 1:
                resource = Nepomuk.Resource(self.selectedUris[0])
                self.parent.addFileLaunchActions(self, resource)
            self.addDeleteAction()
        