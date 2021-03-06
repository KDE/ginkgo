#!/usr/bin/env python
# -*- coding: utf-8 -*-
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


from PyKDE4.nepomuk import Nepomuk
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ginkgo.dao import datamanager
from ginkgo.ontologies import NFO, NIE, PIMO
from os import system
from os.path import join
from PyKDE4 import soprano
from PyKDE4.kdecore import i18n
from ginkgo.views.resourcestable import ResourcesTable, ResourcesTableModel,ResourcesSortFilterProxyModel

class ResourcesByTypeTable(ResourcesTable):

    def __init__(self, mainWindow=False, nepomukType=None, excludeList=None, dialog=None):
        self.nepomukType = nepomukType
        super(ResourcesByTypeTable, self).__init__(mainWindow=mainWindow, dialog=dialog, excludeList=excludeList)
        

    def statementAddedSlot(self, statement):
        predicate = statement.predicate().uri()
        if predicate == soprano.Soprano.Vocabulary.RDF.type():
            object = statement.object().uri()
            if object == self.nepomukType:
                subject = statement.subject().uri()
                newresource = Nepomuk.Resource(subject)
                self.addResource(newresource)

        
    def createModel(self):
        self.model = ResourcesTableModel(self)
        #self.model.setHeaders(["Full Name", "Creation Date", "Last Update"])
        self.model.setHeaders([i18n("Name"), i18n("Date")])
        datamanager.findResourcesByType(self.nepomukType, self.model.queryNextReadySlot, self.queryFinishedSlot, self)
        

