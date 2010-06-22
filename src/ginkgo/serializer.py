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
from mako.runtime import Context
from StringIO import StringIO
from ginkgo.dao import datamanager
from ginkgo.util import fileutil, util
from mako.template import Template
from ginkgo.model.resource import Resource
from ginkgo.model.nepomukresource import NepomukResource

BIBTEX = "bibtex"
RDF_XML = "rdfxml"
RDF_N3 = "rdfn3"
CUSTOM_EXPORT = "custom-export"

class Serializer(object):
    def __init__(self, outputPath, templateName):
        super(Serializer, self).__init__()
        self.outputPath = outputPath
        self.templateName = templateName
        fileutil.writeStringToFile("", self.outputPath)
        tmplResource = datamanager.findResourceByLabel(self.templateName)
        tmplContent = unicode(tmplResource.description())
        self.tmpl = Template(tmplContent)
        self.mapper = util.createDictFromResourceDescription("BibtexOntologyMapper")
        
    def serialize(self, resource):
        buf = StringIO()
        gresource = NepomukResource(resource)
        ctx = Context(buf, resource=gresource, mapper=self.mapper)
        self.tmpl.render_context(ctx)
        fileutil.appendStringToFile(buf.getvalue(), self.outputPath)
    
        
    def queryNextReadySlot(self, query):
        node = query.binding("r");
        resource = Nepomuk.Resource(node.uri())
        self.serialize(resource)
        query.next()
    
    def queryFinishedSlot(self):
        pass
    
    def setQuery(self, query):
        self.query = query
        
        
