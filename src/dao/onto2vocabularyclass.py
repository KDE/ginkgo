
#!/bin/env python

# This file is part of Soprano Project
# 
# Copyright (C) 2007-2010 Sebastian Trueg <trueg@kde.org>
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
# 
# You should have received a copy of the GNU Library General Public License
# along with this library; see the file COPYING.LIB.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.

"""
This is a port of onto2vocabularyclass to Python.
It, however, does not contain any of the error handling
present in the original onto2vocabularyclass.
"""

import sys
from PyKDE4.soprano import Soprano
from PyQt4 import QtCore


reservedKeywords = [ 'class' ]

def normalizeName(name):
    return name.replace('-','')


def disambiguateKeyword(name, className):
    if name in reservedKeywords:
        return className.lower() + name[0].upper() + name.lower()
    return name


def extractRelevantResources(graph):
    resources = []
    it = graph.listStatements( Soprano.Node(), Soprano.Node(Soprano.Vocabulary.RDF.type()), Soprano.Node() )
    while it.next():
        s = it.current()
        if not s.context().isValid() or not graph.containsStatement( s.context(), Soprano.Node(Soprano.Vocabulary.RDF.type()), Soprano.Node(Soprano.Vocabulary.NRL.GraphMetadata()) ):
            resources.append(s.subject())
    return resources


def main():
    QtCore.QCoreApplication( sys.argv )

    fileName = ''
    className = ''
    encoding = ''
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--name':
            i+=1
            className = sys.argv[i]

        elif sys.argv[i] == '--encoding':
            i+=1
            encoding = sys.argv[i]
            
        elif i == len(sys.argv)-1:
            fileName = sys.argv[i]

        i+=1

    parser = Soprano.PluginManager.instance().discoverParserForSerialization( Soprano.mimeTypeToSerialization( encoding ), encoding )
    it = parser.parseFile( fileName, QtCore.QUrl("http://dummybaseuri.org"), Soprano.mimeTypeToSerialization( encoding ), encoding )
    graph = Soprano.Graph()
    while it.next():
        graph.addStatement( it.current() )

    sourceFile = open(className+'.py', 'w')

    allResources = extractRelevantResources(graph)
    normalizedResources = {}
    done = []
    for resource in allResources:
        uri = resource.uri().toString()
        if not uri in normalizedResources:
            name = resource.uri().fragment()
        if not len(name) == 0 and not name in done:
            normalizedResources[uri] = name

    namespaceUri = QtCore.QUrl(normalizedResources.keys()[0])
    namespaceUri.setFragment('')
    ontoNamespace = namespaceUri
    print 'Namespace: %s' % namespaceUri
    print dir(sourceFile)

    print >> sourceFile, 'from PyQt4 import QtCore'
    for uri, name in normalizedResources.iteritems():
        print >> sourceFile, "%s = QtCore.QUrl('%s')" % (normalizeName(name), uri)
        
if __name__ == '__main__':
    main()
    
