
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

from PyQt4.QtCore import QUrl, QVariant
from resource import Resource
from PyKDE4.nepomuk import Nepomuk
from PyKDE4.soprano import Soprano
from ginkgo.dao import datamanager



class NepomukResource(Resource):
    """Convenient wrapper class adding methods to the Nepomuk.Resource type."""
    
    def __init__(self, resource):
        self.resource = resource
    
    
    def getTypeName(self, ontologyAbbrev):
        """Finds the first type of this resource that belongs to the ontology having the given abbreviation,
            and returns its name."""
        
        typesUris = self.resource.types()
        for typeUri in typesUris:
            abbrev = datamanager.ontologyAbbreviationForUri(typeUri)
            if abbrev == ontologyAbbrev:
                type = Nepomuk.Types.Class(typeUri)
                typeName = unicode(type.name())
                return typeName
        
        return None
    
    def getProperties(self, ontologyAbbrev):
        properties = self.resource.properties()
        foundProperties = []
        for propertyUri in properties:
            abbrev = datamanager.ontologyAbbreviationForUri(propertyUri)
            if abbrev == ontologyAbbrev:
                property = Nepomuk.Types.Property(propertyUri)
                foundProperties.append(property)
        
        return foundProperties
    
    def getPropertyValue(self, propertyUriOrShortName, ontologyAbbrev=None):
        values = self.getPropertyValues(propertyUriOrShortName, ontologyAbbrev)
        if len(values) > 0:
            return values[0]
        return ""

    def getPropertyValues(self, propertyUriOrShortName, ontologyAbbrev=None):
        propertyUri = None
        if ontologyAbbrev:
            ontology = datamanager.abbrevToOntology(ontologyAbbrev)
            
            if ontology:
                namespace = ontology.property(Soprano.Vocabulary.NAO.hasDefaultNamespace()).toString()
                print "Namespace:" % namespace
                #TODO: fix ontology import
                if namespace == "http://purl.org/net/nknouf/ns/bibtex#":
                    namespace = "file:///tmp/bibtex.owl#"
                fullname = namespace + propertyUriOrShortName
                propertyUri = QUrl(fullname)
        else:
            propertyUri = propertyUriOrShortName
            
        values = []
        if propertyUri:
            for pptyUrl, pptyValue in self.resource.properties().iteritems():
                if pptyUrl == propertyUri:
                    values.append(pptyValue.toString())
            return values
        return []        


if __name__ == "__main__":
    #TODO: see why with bibtex, we don't get the properties nor the types of the resource
    resource = Nepomuk.Resource("nepomuk:/res/6d864e70-a710-4fdc-bc9c-e65167c7226f")
    print resource

    nresource = NepomukResource(resource)
    
    nresource.getPropertyValue("prefLabel","nao")
#    for prop in nresource.getProperties("nao"):
#        print prop.name()
#    resource = NepomukResource(nresource)
#    label = resource.getTypeLabel("bibtex")
#    print label
    
