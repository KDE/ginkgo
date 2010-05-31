#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
from PyKDE4.nepomuk import Nepomuk
from PyKDE4.soprano import Soprano
from PyQt4.QtCore import QUrl

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

def printArray(data):
    for elt in data:
        print str(elt.resourceUri()) +" " +elt.genericLabel()


def tagMatch():
    tagTerm = Nepomuk.Query.ResourceTerm(Nepomuk.Resource("cloud"))
    prop = Nepomuk.Types.Property(Soprano.Vocabulary.NAO.hasTag())
    term = Nepomuk.Query.ComparisonTerm(prop, tagTerm, Nepomuk.Query.ComparisonTerm.Equal)
    query = Nepomuk.Query.Query(term)
    sparql = query.toSparqlQuery()
    data = executeQuery(sparql)
    printArray(data)

#label in unicode
def labelMatch(label):
    
    label = label.replace("*", ".*")
    label = label.replace("?", ".")

    literalTerm = Nepomuk.Query.LiteralTerm(Soprano.LiteralValue(label))
    prop = Nepomuk.Types.Property(Soprano.Vocabulary.NAO.prefLabel())
    term = Nepomuk.Query.ComparisonTerm(prop, literalTerm, Nepomuk.Query.ComparisonTerm.Regexp)
    query = Nepomuk.Query.Query(term)
    sparql = query.toSparqlQuery()
    data = executeQuery(sparql)
    printArray(data)

def typeAndLabelMatch(typeUri, label):
    nepomukType = Nepomuk.Types.Class(typeUri)
    typeTerm = Nepomuk.Query.ResourceTypeTerm(nepomukType)

    literalTerm = Nepomuk.Query.LiteralTerm(Soprano.LiteralValue(label))
    prop = Nepomuk.Types.Property(Soprano.Vocabulary.NAO.prefLabel())
    labelTerm = Nepomuk.Query.ComparisonTerm(prop, literalTerm, Nepomuk.Query.ComparisonTerm.Regexp)
    
    
    andTerm = Nepomuk.Query.AndTerm(typeTerm, labelTerm)
    
    query = Nepomuk.Query.Query(andTerm)
    sparql = query.toSparqlQuery()
    data = executeQuery(sparql)
    printArray(data)

    
    
#labelMatch(unicode(unicode("^Franç*")))
PersonContact = QUrl('http://www.semanticdesktop.org/ontologies/2007/03/22/nco#PersonContact')
Organization = QUrl('http://www.semanticdesktop.org/ontologies/2007/11/01/pimo#Organization')

typeAndLabelMatch(Soprano.Vocabulary.RDFS.Resource(),unicode("^N"))

typeAndLabelMatch(Organization,unicode("^N"))

typeAndLabelMatch(PersonContact,unicode("^N"))


