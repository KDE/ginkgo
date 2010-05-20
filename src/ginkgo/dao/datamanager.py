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
from ginkgo.ontologies import NFO, NIE, PIMO, NCO, TMO
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
    url = "file://" + absolutePath
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


def test():
    labelTerm = Nepomuk.Query.ComparisonTerm(Nepomuk.Types.Property(Soprano.Vocabulary.NAO.prefLabel()), Nepomuk.Query.LiteralTerm(Soprano.LiteralValue("Alex")), Nepomuk.Query.ComparisonTerm.Contains)
    #labelTerm.setVariableName("label")
    #query = Nepomuk.Query.Query(labelTerm)
    
    nepomukType = Nepomuk.Types.Class(NCO.Contact)
    typeTerm = Nepomuk.Query.ResourceTypeTerm(nepomukType)
    query = Nepomuk.Query.Query(typeTerm)
    
    data =executeQuery(query.toSparqlQuery())
    for elt in data:
        elt.addProperty(Soprano.Vocabulary.RDF.type(), Nepomuk.Variant(NCO.PersonContact))
        
        
#    andTerm = Nepomuk.Query.AndTerm([typeTerm, labelTerm])
#    

#    print query.toSparqlQuery()
#    

#    print data

def findResourcesByType(nepomukType, queryNextReadySlot, queryFinishedSlot=None):
                
    nepomukType = Nepomuk.Types.Class(nepomukType)
    term = Nepomuk.Query.ResourceTypeTerm(nepomukType)
    
    
    
    query = Nepomuk.Query.Query(term);
    sparql = query.toSparqlQuery();
    
    #dirModel =  KDirModel()
    #searchUrl = query.toSearchUrl();
    #dirModel.dirLister().openUrl( searchUrl );
    
    #typeUri = "http://www.semanticdesktop.org/ontologies/2007/11/01/pimo#Person"
    #typeUri = "http://www.w3.org/1999/02/22-rdf-syntax-ns#Resource" 
    
    #queryString = "select distinct ?r  where { ?r a ?v1 . ?v1 <http://www.w3.org/2000/01/rdf-schema#subClassOf> <%s> .   }" % typeUri
    
    executeAsyncQuery(sparql, queryNextReadySlot, queryFinishedSlot)


def executeAsyncQuery(sparql, queryNextReadySlot, queryFinishedSlot):
    model = Nepomuk.ResourceManager.instance().mainModel()
    #iter = model.executeQuery(sparql, Soprano.Query.QueryLanguageSparql)
    query = Soprano.Util.AsyncQuery.executeQuery(model, sparql, Soprano.Query.QueryLanguageSparql)
    #self.query, SIGNAL("nextReady(Soprano.Util.AsyncQuery* ) "), self.queryNextReadySlot)
    query.nextReady.connect(queryNextReadySlot)
    if queryFinishedSlot:
        query.finished.connect(queryFinishedSlot)



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
    relatedInverse = set(resource.isRelatedOf())
    
    pimoRelated = resource.property(PIMO.isRelated)
    urls = pimoRelated.toUrlList()
    for elt in urls:
        related.add(Nepomuk.Resource(elt))
    
    pimoRelatedInverse = Nepomuk.ResourceManager.instance().allResourcesWithProperty(PIMO.isRelated, Nepomuk.Variant(resource))
    relations = related.union(relatedInverse).union(pimoRelatedInverse)
    
    return relations

    #sparql = "select ?o  where  { <%s> <http://www.semanticdesktop.org/ontologies/2007/08/15/nao#isRelated> ?o . OPTIONAL {?o <http://www.semanticdesktop.org/ontologies/2007/08/15/nao#prefLabel> ?label } } order by ?label" % uri        
    #data = executeQuery(sparql)
    #return data


#used by the matchitemdialog, see also the function labelSearch
def findResourcesByLabel(label, queryNextReadySlot, queryFinishedSlot=None):
    #handle regex
    label = label.replace("*", ".*")
    label = label.replace("?", ".")
       
    sparql = "select distinct ?r, ?label  where { ?r <http://www.semanticdesktop.org/ontologies/2007/08/15/nao#prefLabel> ?label  . FILTER regex(?label,  \"^%s\", \"i\")  }" % label
    executeAsyncQuery(sparql, queryNextReadySlot, queryFinishedSlot)
    

def findResourcesByLabelSync(label):
    queryString = "select distinct ?r, ?label  where { ?r <http://www.semanticdesktop.org/ontologies/2007/08/15/nao#prefLabel> ?label  . FILTER regex(?label,  \"%s\", \"i\")  }" % label 
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
    sparql = "select ?r  where { ?r a <%s> . OPTIONAL { { ?r <%s> ?st . } UNION { ?st <%s> ?r . } } . FILTER(!BOUND(?st)) . ?r nao:prefLabel ?label}  order by ?label" % (PIMO.Task.toString(), TMO.superTask.toString(), TMO.subTask.toString())
    return executeQuery(sparql)

def findSubTasks(taskUri):
    sparql = "select ?r where { ?r a <%s> . ?r <%s> <%s> }" % (PIMO.Task.toString(), TMO.superTask.toString(), taskUri)
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
        #if not value.isResource():
        data.append([str(key), value])
    
    return data


#see also findResourcesByLabel
def labelSearch(label, queryNextReadySlot, queryFinishedSlot):
    label = label.replace("*", ".*")
    label = label.replace("?", ".")
       
    sparql = "select distinct ?r, ?label  where { ?r <http://www.semanticdesktop.org/ontologies/2007/08/15/nao#prefLabel> ?label  . FILTER regex(?label,  \"%s\", \"i\")  }" % label
    executeAsyncQuery(sparql, queryNextReadySlot, queryFinishedSlot)


def fullTextSearch(term, queryNextReadySlot, queryFinishedSlot=None):
    if term is None:
        return
    
    if len(term.strip()) == 0:
        return
    
    term = Nepomuk.Query.LiteralTerm(Soprano.LiteralValue(term))
    query = Nepomuk.Query.Query(term)
    sparql = query.toSparqlQuery()
    #data = executeQuery(sparql)
    executeAsyncQuery(sparql, queryNextReadySlot, queryFinishedSlot)


#Ported from C++ from svn://anonsvn.kde.org/home/kde/trunk/playground/base/nepomuk-kde/nepomukutils/pimomodel.cpp
def createPimoClass(parentClassUri, label, comment=None, icon=None):
    if label is None or len(str(label).strip()) == 0:
        print "Class label cannot be empty."
        return None
    
    parentClass = Nepomuk.Types.Class(parentClassUri)
    pimoThingClass = Nepomuk.Types.Class(PIMO.Thing)
    if parentClassUri != PIMO.Thing and not parentClass.isSubClassOf(pimoThingClass):
        print "New PIMO class needs to be subclass of pimo:Thing."
        return None
    
    #TODO: see pimomodel.cpp
#        if ( !name.isEmpty() ) {
#        QString normalizedName = name.replace( QRegExp( "[^\\w\\.\\-_:]" ), "" );
#        QUrl s = "nepomuk:/" + normalizedName;
#        while( 1 ) {
#            if ( !q->executeQuery( QString("ask where { { <%1> ?p1 ?o1 . } UNION { ?r2 <%1> ?o2 . } UNION { ?r3 ?p3 <%1> . } }")
#                                   .arg( QString::fromAscii( s.toEncoded() ) ), Soprano::Query::QueryLanguageSparql ).boolValue() ) {
#                return s;
#            }
#            s = "nepomuk:/" + normalizedName + '_' +  KRandom::randomString( 20 );
#        }
#    }

    classUri = Nepomuk.ResourceManager.instance().generateUniqueUri()

    ctx = Soprano.Node(pimoContext())
    model = Nepomuk.ResourceManager.instance().mainModel()
    stmt = Soprano.Statement(Soprano.Node(QUrl(classUri)), Soprano.Node(Soprano.Vocabulary.RDF.type()), Soprano.Node(Soprano.Vocabulary.RDFS.Class()), ctx)
    model.addStatement(stmt)
    stmt = Soprano.Statement(Soprano.Node(QUrl(classUri)), Soprano.Node(Soprano.Vocabulary.RDFS.subClassOf()), Soprano.Node(parentClassUri), ctx)
    model.addStatement(stmt)
    stmt = Soprano.Statement(Soprano.Node(QUrl(classUri)), Soprano.Node(Soprano.Vocabulary.RDFS.label()), Soprano.Node(Soprano.LiteralValue(label)), ctx)
    model.addStatement(stmt)
    return Nepomuk.Resource(classUri)
    
#Ported from C++ from svn://anonsvn.kde.org/home/kde/trunk/playground/base/nepomuk-kde/nepomukutils/pimomodel.cpp
def pimoContext():
    sparql = "select ?c ?onto where {?c a <%s> . OPTIONAL {?c a ?onto . FILTER(?onto=<%s>). } } " % (str(PIMO.PersonalInformationModel.toString()), str(Soprano.Vocabulary.NRL.Ontology().toString()))
    model = Nepomuk.ResourceManager.instance().mainModel()
    it = model.executeQuery(sparql, Soprano.Query.QueryLanguageSparql)
    if it.next():
        pimoContext = it.binding(0).uri()
        if not it.binding(1).isValid():
            it.close()
            model.addStatement(pimoContext, Soprano.Vocabulary.RDF.type(), Soprano.Vocabulary.NRL.Ontology(), pimoContext)

    else:
        it.close()
        pimoContext = Nepomuk.ResourceManager.instance().generateUniqueUri()
        model.addStatement(pimoContext, Soprano.Vocabulary.RDF.type(), PIMO.PersonalInformationModel, pimoContext)
        model.addStatement(pimoContext, Soprano.Vocabulary.RDF.type(), Soprano.Vocabulary.NRL.Ontology(), pimoContext)
    return pimoContext

    
if __name__ == "__main__":
    #data = findResourcesByProperty(QUrl('http://www.semanticdesktop.org/ontologies/2007/01/19/nie#url'),file)
#    data = findResourcesByProperty(NIE.url.toString(),"file:///home/arkub/F/CMakecccccc_Tutorial.pdf")
#    for elt in data:
#        print elt.resourceUri().toString() + " "+ elt.genericLabel()
#    
#    getFileResource("/home/arkub/F/CMakecccccc_Tutorial.pdf")
#    nepomukType = NCO.Contact
#    res = Nepomuk.Resource(nepomukType)
#    print nepomukType
#    for prop in res.properties():
#        print prop.toString()
#        print res.property(prop).toString()
    
#    createPimoClass(PIMO.Thing, "Song")
    test()
    

