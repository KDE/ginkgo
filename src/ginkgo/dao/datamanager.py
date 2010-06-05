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

from PyQt4.QtCore import QUrl, QFile, QDateTime, QString
from PyKDE4.nepomuk import Nepomuk
from PyKDE4.soprano import Soprano
from ginkgo.ontologies import NFO, NIE, PIMO, NCO, TMO
from sys import exc_info
from traceback import format_exception

import os

DC_TERMS = "http://purl.org/dc/terms/"
DC_TYPES = "http://purl.org/dc/dcmitype/"

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


def scrap1():
    url = QUrl("nepomuk:/res/a8b8ed53-3f5e-4199-b824-f7f0360408c5")
    res = Nepomuk.Resource(url)
    print res
    
    print res.genericIcon()
    print "finishing"
    
    

def scrap():
    
    
    
    labelTerm = Nepomuk.Query.ComparisonTerm(Nepomuk.Types.Property(Soprano.Vocabulary.NAO.prefLabel()), Nepomuk.Query.LiteralTerm(Soprano.LiteralValue("Alex")), Nepomuk.Query.ComparisonTerm.Contains)
    labelTerm.setVariableName("label")
    #query = Nepomuk.Query.Query(labelTerm)

    
    nepomukType = Nepomuk.Types.Class(NCO.Contact)
    typeTerm = Nepomuk.Query.ResourceTypeTerm(nepomukType)
    query = Nepomuk.Query.Query(typeTerm)
    
    data = findResources(query.toSparqlQuery())
    for elt in data:
        elt.addProperty(Soprano.Vocabulary.RDF.type(), Nepomuk.Variant(NCO.PersonContact))
        
        
#    andTerm = Nepomuk.Query.AndTerm([typeTerm, labelTerm])
#    

#    print query.toSparqlQuery()
#    

#    print data

def findResourcesByType(nepomukType, queryNextReadySlot, queryFinishedSlot=None, controller=None):
                
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
    
    executeAsyncQuery(sparql, queryNextReadySlot, queryFinishedSlot, controller)


def executeAsyncQuery(sparql, queryNextReadySlot, queryFinishedSlot, controller=None):
    """The controller variable is used for the controller to close and disconnect the query when necessary"""
    
    model = Nepomuk.ResourceManager.instance().mainModel()
    #iter = model.executeQuery(sparql, Soprano.Query.QueryLanguageSparql)
    query = Soprano.Util.AsyncQuery.executeQuery(model, sparql, Soprano.Query.QueryLanguageSparql)
    #self.query, SIGNAL("nextReady(Soprano.Util.AsyncQuery* ) "), self.queryNextReadySlot)
    
    if controller:
        controller.setQuery(query)
    query.nextReady.connect(queryNextReadySlot)
    if queryFinishedSlot:
        query.finished.connect(queryFinishedSlot)


def executeSparqlQuery(sparql):
        
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

def findResources(sparql):
        
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

def findDirectRelations(uri):
    resource = Nepomuk.Resource(uri)    
    relations = dict()
    props = resource.properties()
    
    for prop in props:
        if props[prop].isResourceList():
            relations[prop.toString()] = set(props[prop].toResourceList())
        elif props[prop].isResource():
            #TODO: it seems there's a Nepomuk bug with property rdfs:range when its value is not a Resource type
            #see range.py
            checkuri = str(props[prop].toResource().resourceUri().toString())
            if len(checkuri.strip()) > 0:
                relations[prop.toString()] = set([props[prop].toResource()])
            
    newrelations = dict()
    for key in relations.keys():
        prop = Nepomuk.Types.Property(QUrl(key))
        newrelations[prop] = relations[key]

    return newrelations

def findInverseRelations(uri):
    
    sparql = "select * where {?s ?p <%s>}" % uri
    #TODO: use the query API
    model = Nepomuk.ResourceManager.instance().mainModel()
    iter = model.executeQuery(sparql, Soprano.Query.QueryLanguageSparql)
    
    
    data = []
    while iter.next() :
        bindingSet = iter.current()
        subject = Nepomuk.Resource(bindingSet.value("s").uri())
        predicate = Nepomuk.Types.Property(bindingSet.value("p").uri())
            
        data.append((subject, predicate))
        
    return data


def findInverseRelationsTemp(uri):
    resource = Nepomuk.Resource(uri)    
    relations = dict()
    
    props = resourceTypesProperties(resource)
    for property in props:
        #skip the RDF.type() property, otherwise for classes we get all their instances
        if property.uri() == Soprano.Vocabulary.RDF.type():
            continue
        
        irel = Nepomuk.ResourceManager.instance().allResourcesWithProperty(property.uri(), Nepomuk.Variant(resource))
        if len(irel) > 0 and relations.has_key(property.uri().toString()):
            relations[property.uri().toString()] = relations[property.uri().toString()].union(irel)
        elif len(irel) > 0:
            relations[property.uri().toString()] = set(irel)

    #TODO: the dict should directly contain property objects, and compare them properly
    #see how to give the dict a good hash function for properties (based on the comparison of their uri)

    newrelations = dict()
    for key in relations.keys():
        prop = Nepomuk.Types.Property(QUrl(key))
        newrelations[prop] = relations[key]
    
    return newrelations


def findRelations(uri):
     
    resource = Nepomuk.Resource(uri)    
    relations = dict()
    props = resource.properties()
    
    for prop in props:
        if props[prop].isResourceList():
            relations[prop.toString()] = set(props[prop].toResourceList())
        elif props[prop].isResource():
            relations[prop.toString()] = set([props[prop].toResource()])
            

    props = resourceTypesProperties(resource)
    for property in props:
        irel = Nepomuk.ResourceManager.instance().allResourcesWithProperty(property.uri(), Nepomuk.Variant(resource))
        if len(irel) > 0 and relations.has_key(property.uri().toString()):
            relations[property.uri().toString()] = relations[property.uri().toString()].union(irel)
        elif len(irel) > 0:
            relations[property.uri().toString()] = set(irel)

    #TODO: the dict should directly contain property objects, and compare them properly
    #see how to give the dict a good hash function for properties (based on the comparison of their uri)

    newrelations = dict()
    for key in relations.keys():
        prop = Nepomuk.Types.Property(QUrl(key))
        newrelations[prop] = relations[key]
    
    return newrelations

def resourceTypesProperties(resource, includePropertiesWithNonLiteralRange=True, includePropertiesWithLiteralRange=False):
    """ Returns properties whose domain is one of the types of the resource passed as argument.
    """
    
    props = []
    for type in resource.types():
        typeClass = Nepomuk.Types.Class(type)
        tprops = typeProperties(typeClass, includePropertiesWithNonLiteralRange, includePropertiesWithLiteralRange)
        for aprop in tprops:
            #TODO: do it the proper way
            try:
                props.index(aprop)
            except:
                props.append(aprop)

        for parentClass in typeClass.allParentClasses():
            tprops = typeProperties(parentClass, includePropertiesWithNonLiteralRange, includePropertiesWithLiteralRange)
            for aprop in tprops:
                try:
                    props.index(aprop)
                except:
                    props.append(aprop)

    return props

def typeProperties(nepomukTypeClass, includePropertiesWithNonLiteralRange=True, includePropertiesWithLiteralRange=False):
    props = []
    for property in nepomukTypeClass.domainOf():
        #TODO: it seems class.isValid() always return True even for Literals
        #TODO: see range.py -> we need to use the Nepomuk.Resource object 
        #instead of dealing with Nepomuk.Types.Property, whose range method
        #returns something that does not match the actual range property 
        #rangeuri = str(property.range().uri().toString())
        #print str(property.uri().toString())
        #print "rangeuri: %s " % rangeuri
        #if property.range().isValid():
        resourceProp = Nepomuk.Resource(property.uri())
        rangeValue = str(resourceProp.property(Soprano.Vocabulary.RDFS.range()).toString())
        #TODO: we should check that the range is not either any Literal subclass
        if rangeValue.find("http://www.w3.org/2001/XMLSchema#") < 0 and rangeValue.find("http://www.w3.org/2000/01/rdf-schema#Literal") < 0:
            if includePropertiesWithNonLiteralRange: 
                props.append(property)
        elif includePropertiesWithLiteralRange:
            props.append(property)
            
    return props

def findRelateds(uri):
     
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

def findResourcesByLabel(label, queryNextReadySlot, queryFinishedSlot=None, controller=None):

    label = label.replace("*", ".*")
    label = label.replace("?", ".")

    literalTerm = Nepomuk.Query.LiteralTerm(Soprano.LiteralValue(label))
    prop = Nepomuk.Types.Property(Soprano.Vocabulary.NAO.prefLabel())
    term = Nepomuk.Query.ComparisonTerm(prop, literalTerm, Nepomuk.Query.ComparisonTerm.Regexp)
    query = Nepomuk.Query.Query(term)
    sparql = query.toSparqlQuery()

    executeAsyncQuery(sparql, queryNextReadySlot, queryFinishedSlot, controller)

def findResourcesByTypeAndLabel(typeUri, label, queryNextReadySlot, queryFinishedSlot=None, controller=None):
    
    label = label.replace("*", ".*")
    label = label.replace("?", ".")
    label = label.replace("'", "\\'")

    nepomukType = Nepomuk.Types.Class(typeUri)
    typeTerm = Nepomuk.Query.ResourceTypeTerm(nepomukType)

    literalTerm = Nepomuk.Query.LiteralTerm(Soprano.LiteralValue(label))
    prop = Nepomuk.Types.Property(Soprano.Vocabulary.NAO.prefLabel())
    labelTerm = Nepomuk.Query.ComparisonTerm(prop, literalTerm, Nepomuk.Query.ComparisonTerm.Regexp)
    
    andTerm = Nepomuk.Query.AndTerm(typeTerm, labelTerm)
    
    query = Nepomuk.Query.Query(andTerm)
    sparql = query.toSparqlQuery()
    executeAsyncQuery(sparql, queryNextReadySlot, queryFinishedSlot, controller)

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
    return findResources(sparql)

def findSubTasks(taskUri):
    sparql = "select ?r where { ?r a <%s> . ?r <%s> <%s> }" % (PIMO.Task.toString(), TMO.superTask.toString(), taskUri)
    data = findResources(sparql)
        
    return data
        
def findResourcesByProperty(propertyUri, value):
    sparql = "select ?r where { ?r <%s> <%s> }" % (propertyUri, value)
    data = findResources(sparql)
#    manager = Nepomuk.ResourceManager.instance()    
#    resources = manager.allResourcesWithProperty(propertyUri, Nepomuk.Variant(value))
    return data

def findResourceProperties(resource):
    pass

def findResourceLiteralProperties(resource):
    data = []
    if resource is None:
        return data
    for key, value in resource.properties().iteritems():
        #if not value.isResource():
        data.append((str(key.toString()), value))
    
    return data


def listResourcesOrderedByDate(queryNextReadySlot, queryFinishedSlot, controller):
    sparql = "select distinct ?r, ?label  where { ?r nao:prefLabel ?label  .  ?r nao:lastModified ?lastModified } order by desc(?lastModified) limit 100" 
    executeAsyncQuery(sparql, queryNextReadySlot, queryFinishedSlot, controller)
    

#see also findResourcesByLabel
#def labelSearch(label, queryNextReadySlot, queryFinishedSlot, controller):
#    label = label.replace("*", ".*")
#    label = label.replace("?", ".")
#       
#    sparql = "select distinct ?r, ?label  where { ?r <http://www.semanticdesktop.org/ontologies/2007/08/15/nao#prefLabel> ?label  . FILTER regex(?label,  \"%s\", \"i\")  }" % label
#    executeAsyncQuery(sparql, queryNextReadySlot, queryFinishedSlot, controller)


def fullTextSearch(term, queryNextReadySlot, queryFinishedSlot=None, controller=None):
    if term is None:
        return
    
    if len(term.strip()) == 0:
        return
    
    term = Nepomuk.Query.LiteralTerm(Soprano.LiteralValue(term))
    query = Nepomuk.Query.Query(term)
    sparql = query.toSparqlQuery()
    #data = executeQuery(sparql)
    executeAsyncQuery(sparql, queryNextReadySlot, queryFinishedSlot, controller)


#Ported from C++ from svn://anonsvn.kde.org/home/kde/trunk/playground/base/nepomuk-kde/nepomukutils/pimomodel.cpp
def createPimoClass(parentClassUri, label, comment=None, icon=None):
    
    if label is None or len(unicode(label).strip()) == 0:
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

    classUri = Nepomuk.ResourceManager.instance().generateUniqueUri(label)
    stmts = []
    stmts.append(Soprano.Statement(Soprano.Node(classUri), Soprano.Node(Soprano.Vocabulary.RDF.type()), Soprano.Node(Soprano.Vocabulary.RDFS.Class())))
    stmts.append(Soprano.Statement(Soprano.Node(classUri), Soprano.Node(Soprano.Vocabulary.RDFS.subClassOf()), Soprano.Node(QUrl(parentClassUri))))
    #this is needed for the class to show up as a child of the PIMO class chosen
    if parentClassUri != PIMO.Thing:
        stmts.append(Soprano.Statement(Soprano.Node(classUri), Soprano.Node(Soprano.Vocabulary.RDFS.subClassOf()), Soprano.Node(PIMO.Thing)))
    #this is needed until we use an inferencer, otherwise searching for instances of resource won't include the instances of this class
    stmts.append(Soprano.Statement(Soprano.Node(classUri), Soprano.Node(Soprano.Vocabulary.RDFS.subClassOf()), Soprano.Node(Soprano.Vocabulary.RDFS.Resource())))
    #TODO: check why pimomodel.cpp does not use Soprano.Node wrapping
    #TODO: check why all classes in the db are subclass of themselves
    stmts.append(Soprano.Statement(Soprano.Node(classUri), Soprano.Node(Soprano.Vocabulary.RDFS.subClassOf()), Soprano.Node(QUrl(classUri))))
    stmts.append(Soprano.Statement(Soprano.Node(classUri), Soprano.Node(Soprano.Vocabulary.RDFS.label()), Soprano.Node(Soprano.LiteralValue(label))))
    stmts.append(Soprano.Statement(Soprano.Node(classUri), Soprano.Node(Soprano.Vocabulary.NAO.created()), Soprano.Node(Soprano.LiteralValue(QDateTime.currentDateTime()))))

    if addPimoStatements(stmts) == Soprano.Error.ErrorNone: 
        #the parent's class needs a rerset for reloading its children classes
        parentClass.reset()
        return Nepomuk.Resource(classUri)
    
    return None

#Ported from C++ from svn://anonsvn.kde.org/home/kde/trunk/playground/base/nepomuk-kde/nepomukutils/pimomodel.cpp
def createPimoProperty(label, domainUri, rangeUri=Soprano.Vocabulary.RDFS.Resource(), comment=None, icon=None):
    if not rangeUri.isValid():
        print "[Ginkgo] Invalid range"
        return QUrl()
    
    if not label or len(label) == 0:
        print "[Ginkgo] Empty label"
        return QUrl()
    
    domainClass = Nepomuk.Types.Class(domainUri)
    pimoThingClass = Nepomuk.Types.Class(PIMO.Thing)

    if domainUri != PIMO.Thing and not domainClass.isSubClassOf(pimoThingClass):
        print "[Ginkgo] New PIMO properties need to have a pimo:Thing related domain."

    propertyUri = Nepomuk.ResourceManager.instance().generateUniqueUri(label)
    stmts = []
    stmts.append(Soprano.Statement(Soprano.Node(propertyUri), Soprano.Node(Soprano.Vocabulary.RDF.type()), Soprano.Node(Soprano.Vocabulary.RDF.Property())))
    #stmts.append(Soprano.Statement(Soprano.Node(propertyUri), Soprano.Node(Soprano.Vocabulary.RDFS.subPropertyOf()), Soprano.Node(PIMO.isRelated)))
    stmts.append(Soprano.Statement(Soprano.Node(propertyUri), Soprano.Node(Soprano.Vocabulary.RDFS.domain()), Soprano.Node(domainUri)))
    stmts.append(Soprano.Statement(Soprano.Node(propertyUri), Soprano.Node(Soprano.Vocabulary.RDFS.range()), Soprano.Node(rangeUri)))
    #TODO set the prefLabel of the resource corresponding to this property?
    #TODO why a property needs to be a subproperty of itself
    stmts.append(Soprano.Statement(Soprano.Node(propertyUri), Soprano.Node(Soprano.Vocabulary.RDFS.subPropertyOf()), Soprano.Node(propertyUri)))
    stmts.append(Soprano.Statement(Soprano.Node(propertyUri), Soprano.Node(Soprano.Vocabulary.RDFS.label()), Soprano.Node(Soprano.LiteralValue(label))))
    stmts.append(Soprano.Statement(Soprano.Node(propertyUri), Soprano.Node(Soprano.Vocabulary.NAO.created()), Soprano.Node(Soprano.LiteralValue(QDateTime.currentDateTime()))))
    
    if addPimoStatements(stmts) == Soprano.Error.ErrorNone: 
        #we reset the entity so that its properties will get refreshed
        domainClass.reset()
        return Nepomuk.Resource(propertyUri)
    
    
    
    return None
    
#    QUrl propertyUri = newPropertyUri( label );
#
#    QList<Soprano::Statement> sl;
#    sl << Soprano::Statement( propertyUri, Soprano::Vocabulary::RDF::type(), Soprano::Vocabulary::RDF::Property() )
#       << Soprano::Statement( propertyUri, Soprano::Vocabulary::RDFS::subPropertyOf(), Vocabulary::PIMO::isRelated() )
#       << Soprano::Statement( propertyUri, Soprano::Vocabulary::RDFS::domain(), domainUri )
#       << Soprano::Statement( propertyUri, Soprano::Vocabulary::RDFS::range(), range )
#       << Soprano::Statement( propertyUri, Soprano::Vocabulary::RDFS::label(), Soprano::LiteralValue( label ) )
#       << Soprano::Statement( propertyUri, Soprano::Vocabulary::NAO::created(), Soprano::LiteralValue( QDateTime::currentDateTime() ) );
#    if ( !comment.isEmpty() ) {
#        sl << Soprano::Statement( propertyUri, Soprano::Vocabulary::RDFS::comment(), Soprano::LiteralValue( comment ) );
#    }
#    if ( !icon.isEmpty() ) {
#        // FIXME: create a proper Symbol object, if possible maybe a subclass DesktopIcon if its a standard icon
#        sl << Soprano::Statement( propertyUri, Soprano::Vocabulary::NAO::hasSymbol(), Soprano::LiteralValue( icon ) );
#    }
#
#    if( addPimoStatements( sl ) == Soprano::Error::ErrorNone ) {
#        return propertyUri;
#    }
#    else {
#        return QUrl();
#    }
#}
   



#Ported from C++ from svn://anonsvn.kde.org/home/kde/trunk/playground/base/nepomuk-kde/nepomukutils/pimomodel.cpp
def pimoContext():
    sparql = "select ?c ?onto where {?c a <%s> . OPTIONAL {?c a ?onto . FILTER(?onto=<%s>). } } " % (str(PIMO.PersonalInformationModel.toString()), str(Soprano.Vocabulary.NRL.Ontology().toString()))
    model = Nepomuk.ResourceManager.instance().mainModel()
    it = model.executeQuery(sparql, Soprano.Query.QueryLanguageSparql)
    if it.next():
        pimoContext = it.binding(0).uri()
        if not it.binding(1).isValid():
            stmt = Soprano.Statement(Soprano.Node(pimoContext), Soprano.Node(Soprano.Vocabulary.RDF.type()), Soprano.Node(Soprano.Vocabulary.NRL.Ontology()), Soprano.Node(pimoContext))
            model.addStatement(stmt)

    else:
        pimoContext = QUrl(Nepomuk.ResourceManager.instance().generateUniqueUri())
        stmt = Soprano.Statement(Soprano.Node(pimoContext), Soprano.Node(Soprano.Vocabulary.RDF.type()), Soprano.Node(PIMO.PersonalInformationModel), Soprano.Node(pimoContext))
        model.addStatement(stmt)
        stmt = Soprano.Statement(Soprano.Node(pimoContext), Soprano.Node(Soprano.Vocabulary.RDF.type()), Soprano.Node(Soprano.Vocabulary.NRL.Ontology()), Soprano.Node(pimoContext))
        model.addStatement(stmt)
    it.close()
    return pimoContext

def addPimoStatements(statements):
    ctx = pimoContext()
    model = Nepomuk.ResourceManager.instance().mainModel()

    for statement in statements:
        statement.setContext(Soprano.Node(ctx))
        model.addStatement(statement)
    
    return Soprano.Error.ErrorNone


#uri can be QUrl or QString
def uriToOntologyLabel(uri, forTypes=True):
    """
    Converts an uri to a label.
    Example: http://www.semanticdesktop.org/ontologies/2007/11/01/pimo#Task -> pimo
    """
    
    #convert QUrl to str only if uri is not a String already
    tmp = QString("")
    if uri.__class__ != tmp.__class__:
        uri = unicode(uri.toString())
    else:
        uri = unicode(uri)
    
    if uri.find(DC_TERMS) == 0:
        return "DCMI terms"
    
    elif uri.find(DC_TYPES) == 0:
        return "DCMI type"

    index1 = uri.rfind("/")
    index2 = uri.find("#")
    if index1 > 0 and index2 > index1:
        return uri[index1 + 1:index2]
    #user created type
    if forTypes and uri.find("nepomuk:/") == 0:
        return "pimo extended"

    return uri
    
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
    scrap1()
    

