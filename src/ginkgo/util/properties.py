#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
from PyKDE4.nepomuk import Nepomuk
from PyKDE4.soprano import Soprano
from PyQt4.QtCore import QUrl



def findRelations(uri):
     
    resource = Nepomuk.Resource(uri)    
    relations = dict()
    props = resource.properties()
    
    for prop in props:
        if props[prop].isResourceList():
            relations[prop.toString()] = set(props[prop].toResourceList())
        elif props[prop].isResource():
            relations[prop.toString()] = set([props[prop].toResource()])
            

    props = domainProperties(resource)
    for property in props:
        irel = Nepomuk.ResourceManager.instance().allResourcesWithProperty(property.uri(), Nepomuk.Variant(resource))
        if len(irel) > 0 and relations.has_key(property.uri().toString()):
            relations[property.uri().toString()] = relations[property.uri().toString()].union(irel)
        elif len(irel) > 0:
            relations[property.uri().toString()] = set(irel)
    
    for rel in relations:
        print rel
        for elt in relations[rel]:
            print elt.genericLabel()

    return relations

def domainProperties(resource, includePropertiesWithLiteralRange=False):
    """ Returns properties whose domain is one of the types of the resource passed as argument.
    """
    
    props = []
    for type in resource.types():
        typeClass = Nepomuk.Types.Class(type)
        for property in typeClass.domainOf():
            if property.range().isValid():
                props.append(Nepomuk.Types.Property(property))

    return props

findRelations(QUrl("nepomuk:/res/9ec996a2-31b6-42af-9b3c-42eb90e88f4a"))


