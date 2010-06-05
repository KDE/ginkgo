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

class TypesTableModel(ResourcesTableModel):
    def __init__(self, parent=None):
        super(TypesTableModel, self).__init__(parent)
        
    def itemAt(self, index):
        resource = self.resources[index.row()]
        column = index.column()
        if column == 0:
            return datamanager.uriToOntologyLabel(resource.resourceUri())
        elif column == 1:
            return resource.genericLabel()
            
class TypesTable(ResourcesTable):
    
    def __init__(self, mainWindow=False, typesUris=None, dialog=None):
        """ typesUris stands for the types to be selected"""
        
        self.typesUris = typesUris
        super(TypesTable, self).__init__(mainWindow=mainWindow, dialog=dialog)

        self.table.sortByColumn(1, Qt.AscendingOrder)
        self.updateSelection()
        
    def createModel(self):
        
        self.model = TypesTableModel(self)
        self.model.setHeaders([i18n("Ontology"), i18n("Name")])
        

        #TODO: find built-in conversion
        resourceSet = []
        array = []
#            for elt in resourceTypes:
#                typeResource = Nepomuk.Resource(elt)
#                ressourceArray.append(typeResource)
        
        rootClass = Nepomuk.Types.Class(Soprano.Vocabulary.RDFS.Resource())
        #rootClass = Nepomuk.Types.Class(PIMO.Thing)
        #rootItem = Nepomuk.Resource()
        self.addChildren(rootClass.uri(), array)
        
        for elt in array:
            resourceSet.append(Nepomuk.Resource(elt))
        self.model.setResources(resourceSet)

    def addChildren(self, resourceUri, set):
        
        typeClass = Nepomuk.Types.Class(resourceUri)
        subClasses = typeClass.subClasses()
        for subClass in subClasses:
            #TODO: why subClass are not instance of Resource?
            try:
                index = set.index(subClass.uri())
            except ValueError, e:
                set.append(subClass.uri())
                self.addChildren(subClass.uri(), set)

    def updateSelection(self):
        index = 0
        for item in self.model.resources:
            for resourceType  in self.typesUris:
                if item.resourceUri() == resourceType:
                    mindex = self.model.index(index, 0, QModelIndex())
                    pindex = self.table.model().mapFromSource(mindex)
                    self.table.selectionModel().select(pindex, QItemSelectionModel.Select)
                    mindex = self.model.index(index, 1, QModelIndex())
                    pindex = self.table.model().mapFromSource(mindex)
                    self.table.selectionModel().select(pindex, QItemSelectionModel.Select)
                    break
                    
            index = index +1    
        #selection = QItemSelection(selection1, selection2)
        
 
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    resource = Nepomuk.Resource("nepomuk:/res/ad17c07d-332f-4fc1-9363-476e0a951b43")
    table = TypesTable(typesUris=resource.types())
    table.show()
    
    app.exec_()

