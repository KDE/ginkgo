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



class AsyncResourceLoadingModel:

    def __init__(self, sparql):
        self.sparql = sparql


    def query(self):
    	model = Nepomuk.ResourceManager.instance().mainModel()
    	#self.sparql = "select distinct ?r  where { ?r a <http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#FileDataObject> .    }"
        data = self.executeSyncQuery()
        print data

    	query = Soprano.Util.AsyncQuery.executeQuery(model, self.sparql, Soprano.Query.QueryLanguageSparql)
    	QObject.connect( query, SIGNAL("nextReady(Soprano.Util.AsyncQuery* ) "), self.queryNextReadySlot)
    	

    def queryNextReadySlot(self, query):
    	print "getting next"
    	query.next()
    	
    def executeSyncQuery(self):
    	model = Nepomuk.ResourceManager.instance().mainModel()
    	print self.sparql
    	iter = model.executeQuery(self.sparql, Soprano.Query.QueryLanguageSparql)
        bindingNames = iter.bindingNames()
        data = []
        while iter.next() :
            bindingSet = iter.current()
            for i in range(len(bindingNames)) :
                v = bindingSet.value(bindingNames[i])
                uri = v.uri()
                #.genericLabel()
                resource = Nepomuk.Resource(uri)
                data.append(resource)
        return data

if __name__ == "__main__":
	
	nepomukType = Nepomuk.Types.Class(Soprano.Vocabulary.RDFS.Resource())
	term = Nepomuk.Query.ResourceTypeTerm(nepomukType)
	query = Nepomuk.Query.Query(term)
	sparql = query.toSparqlQuery()
	asyncmodel = AsyncResourceLoadingModel(sparql)
	asyncmodel.query()
	
	