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

from PyQt4.QtCore import QUrl, QFile
from PyKDE4.nepomuk import Nepomuk
from PyKDE4.soprano import Soprano
from sys import exc_info
from traceback import format_exception
from dao import TMO, NFO, NIE, NCO
import os

def createResource(label, nepomukType):
    newResource = Nepomuk.Resource()
    newResource.setLabel(label)
    #res.setDescription("")

    types = newResource.types()
    types.append(nepomukType)
    newResource.setTypes(types)
    return newResource


def getFileResource(path):
    absolutePath = os.path.abspath(path)
    name = os.path.basename(path)
    url = "file://"+absolutePath
    file = Nepomuk.Resource(QUrl(url))
    
#    print file.isValid()
    if len(file.resourceUri().toString()) == 0:
        file.setProperty(NIE.url, Nepomuk.Variant(QUrl(url)))
        file.setProperty(NFO.fileName, Nepomuk.Variant(name))
        file.setLabel(name)

    return file

def removeResource(uri):            
    resource = Nepomuk.Resource(uri)
    resource.remove()


def findResourcesByType(nepomukType):
                
    nepomukType = Nepomuk.Types.Class(nepomukType)
    term = Nepomuk.Query.ResourceTypeTerm(nepomukType)
    
    query = Nepomuk.Query.Query(term);
    queryString = query.toSparqlQuery();
    
    #dirModel =  KDirModel()
    #searchUrl = query.toSearchUrl();
    #dirModel.dirLister().openUrl( searchUrl );
    
    #typeUri = "http://www.semanticdesktop.org/ontologies/2007/11/01/pimo#Person"
    #typeUri = "http://www.w3.org/1999/02/22-rdf-syntax-ns#Resource" 
    
    #queryString = "select distinct ?r  where { ?r a ?v1 . ?v1 <http://www.w3.org/2000/01/rdf-schema#subClassOf> <%s> .   }" % typeUri
    
    return executeQuery(queryString)


def executeAsyncQuery(sparql):
    model = Nepomuk.ResourceManager.instance().mainModel()
    #iter = model.executeQuery(sparql, Soprano.Query.QueryLanguageSparql)
    Soprano.Util.AsyncQuery.executeQuery(model, sparql, Soprano.Query.QueryLanguageSparql)

def executeQuery(sparql):
        
    model = Nepomuk.ResourceManager.instance().mainModel()
    iter = model.executeQuery(sparql, Soprano.Query.QueryLanguageSparql)
    
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

def findRelations(uri):
     
    resource = Nepomuk.Resource(uri)    
    related = set(resource.isRelateds())
    irelated = set(resource.isRelatedOf())
    relations = related.union(irelated)
    return relations

    #sparql = "select ?o  where  { <%s> <http://www.semanticdesktop.org/ontologies/2007/08/15/nao#isRelated> ?o . OPTIONAL {?o <http://www.semanticdesktop.org/ontologies/2007/08/15/nao#prefLabel> ?label } } order by ?label" % uri        
    #data = executeQuery(sparql)
    #return data


def findResourcesByLabel(label):
    
    queryString = "select distinct ?r, ?label  where { ?r <http://www.semanticdesktop.org/ontologies/2007/08/15/nao#prefLabel> ?label  . FILTER regex(?label,  \"%s\", \"i\")  }" % label 
    
    #queryString  ="select ?p ?o where {<nepomuk:/res/baf31883-a344-4b66-8031-b937447043e9> ?p ?o}"
    
    model = Nepomuk.ResourceManager.instance().mainModel()
    
    iter = model.executeQuery(queryString, Soprano.Query.QueryLanguageSparql)
    bindingNames = iter.bindingNames()

    data = []
    while iter.next() :
        bindingSet = iter.current()
        for i in range(len(bindingNames)) :
            v = bindingSet.value(bindingNames[i])
            if not v.isLiteral():
                resource = Nepomuk.Resource(v.uri())
                data.append(resource)
            else:
                value = v.literal().toString()
     
    return data

def findRootTasks():
    sparql = "select ?r  where { ?r a <%s> . OPTIONAL { { ?r <%s> ?st . } UNION { ?st <%s> ?r . } } . FILTER(!BOUND(?st)) . ?r nao:prefLabel ?label}  order by ?label" % (TMO.Task.toString(), TMO.superTask.toString(),TMO.subTask.toString())
    return executeQuery(sparql)

def findSubTasks(taskUri):
    sparql = "select ?r where { ?r a <%s> . ?r <%s> <%s> }" % (TMO.Task.toString(), TMO.superTask.toString(), taskUri)
    data = executeQuery(sparql)
        
    return data
        
def findResourcesByProperty(propertyUri, value):
    sparql = "select ?r where { ?r <%s> <%s> }" % (propertyUri, value)
    data = executeQuery(sparql)
#    manager = Nepomuk.ResourceManager.instance()    
#    resources = manager.allResourcesWithProperty(propertyUri, Nepomuk.Variant(value))
    return data

def findResourceProperties(resource):
    pass

def findResourceLiteralProperties(resource):
    data = []
    if resource is None:
        return data
    for key, value in resource.allProperties().iteritems():
        if not value.isResource():
            data.append([str(key), value])
    
    return data

    
if __name__ == "__main__":
    #data = findResourcesByProperty(QUrl('http://www.semanticdesktop.org/ontologies/2007/01/19/nie#url'),file)
#    data = findResourcesByProperty(NIE.url.toString(),"file:///home/arkub/F/CMakecccccc_Tutorial.pdf")
#    for elt in data:
#        print elt.resourceUri().toString() + " "+ elt.genericLabel()
#    
#    getFileResource("/home/arkub/F/CMakecccccc_Tutorial.pdf")
    nepomukType = NCO.Contact
    res = Nepomuk.Resource(nepomukType)
    print nepomukType
    for prop in res.properties():
        print prop.toString()
        print res.property(prop).toString()
    
    

