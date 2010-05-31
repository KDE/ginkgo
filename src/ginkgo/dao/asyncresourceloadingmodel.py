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
from PyKDE4.soprano import Soprano 
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import time



class AsyncResourceLoadingModel:

    def __init__(self, sparql):
        self.sparql = sparql


    def query(self):
        model = Nepomuk.ResourceManager.instance().mainModel()

        self.query = Soprano.Util.AsyncQuery.executeQuery(model, self.sparql, Soprano.Query.QueryLanguageSparql)
        #self.query, SIGNAL("nextReady(Soprano.Util.AsyncQuery* ) "), self.queryNextReadySlot)
        self.query.nextReady.connect(self.queryNextReadySlot)
        self.query.finished.connect(self.queryFinished)

    def queryNextReadySlot(self, query):
        query.next()
        node = query.binding( "r" );
        
    def queryFinished(self, query):
        #self.emit(query.finishedLoading())
        pass


if __name__ == "__main__":
    nepomukType = Nepomuk.Types.Class(Soprano.Vocabulary.RDFS.Resource())
    term = Nepomuk.Query.ResourceTypeTerm(nepomukType)
    query = Nepomuk.Query.Query(term)
    sparql = query.toSparqlQuery()
    asyncmodel = AsyncResourceLoadingModel(sparql)
    asyncmodel.query()
    
    app = QApplication(sys.argv)
    #app.setOrganizationName("KDE")
    #app.setOrganizationDomain("kde.org")
    app.setApplicationName("Gingko")
    sys.exit(app.exec_())
