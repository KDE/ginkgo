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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ginkgo.dao import datamanager
from ginkgo.ontologies import NFO, NIE, PIMO
from os import system
from os.path import join
from PyKDE4.soprano import Soprano
from PyKDE4.kdeui import KIcon
from PyKDE4.kdecore import i18n
from ginkgo.views.resourcestable import ResourcesTable, ResourcesTableModel
from ginkgo.views.objectcontextmenu import ObjectContextMenu
from ginkgo.actions import * 
import gobject

class SuggestionsTableModel(ResourcesTableModel):
    def __init__(self, parent=None):
        super(SuggestionsTableModel, self).__init__(parent)
        self.data = []
        self.table = parent
    
        

   
class SuggestionsTable(ResourcesTable):
    
    def __init__(self, mainWindow=False, editor=None, resource=None, title=None, text=None):
        self.resource = resource
        
        self.doImageAnalysis = False
        
        path = self.resource.property(NIE.url)
        if path:
            path = str(path.toString())
            if path.find(".png") > 0:
                self.doImageAnalysis = True
                self.path = path
                
        
        self.editor = editor
        super(SuggestionsTable, self).__init__(mainWindow=mainWindow, dialog=None)
        self.setText(text)
        self.setTitle(title)

    def createModel(self):
        self.model = SuggestionsTableModel(self)
        #self.model.setHeaders([i18n("Relation"), i18n("Title"), i18n("Date"), i18n("Type") ])
        self.model.setHeaders(["Title", "Date", "Type"])


    def selectionChanged(self, selectedIndex, deselectedIndex):
        selectedIndex = self.table.model().mapToSource(selectedIndex)
        #print "selection: %s" % selectedIndex.row()
        selectedResource = self.model.objectAt(selectedIndex.row())
        label = unicode(selectedResource.genericLabel()).lower()
        #print label
        selections = []
        import re
        starts = [match.start() for match in re.finditer(re.escape(label), self.textLower)]
        #print starts
        for start in starts:
            selection = QTextEdit.ExtraSelection() 
            selection.cursor = QTextCursor(self.editor.document())
            selection.cursor.setPosition(start)
            selection.cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor,len(label))
            selection.format.setBackground(Qt.yellow)    
            selections.append(selection)
        
        self.editor.setExtraSelections(selections)
        
        

    def newEntityHandler(self, entityUri, occurrences):
        resource = Nepomuk.Resource(entityUri)
        label = u"%s" % resource.genericLabel()
        relevance =  occurrences[0][2]
        print "%s [%s] [%s]" % (label, entityUri, relevance)
        
        #if self.text.find(label) >=0:
        if relevance >= 0.9:
            if resource != self.resource and resource not in self.relations and resource not in self.model.resources:
                self.addResource(resource)
                
    def textExtractedHandler(self, text):
        print "Extracted text from image: '%s'" % text
    


    def finishedAnalyzisHandler(self):
        print "finished"
        self.loop.quit()
    
    def finishedImageAnalyzisHandler(self):
        print "finished image analyzis"
#        if self.path.find("olena-test-gartner-social-software-quadrant.png") > 0:
#            self.addResource(Nepomuk.Resource(QUrl("nepomuk:/res/64c8c9a9-1ba2-46c7-96e0-3e52763bd959")))
    

    def setText(self, text):
        self.text = text
        self.textLower = text.lower()
        

    def setTitle(self, title):
        self.title = title

    def runAnalyzis(self):
        self.relations = []
        #the selection model needs to be here, since the table model is reinstalled when the user asks for new suggestions
        self.table.selectionModel().currentChanged.connect(self.selectionChanged)
        
        #populate existing relations for not suggesting entities that are already linked to the current resource
        directRelations = datamanager.findDirectRelations(self.resource.uri())
        for predicate in directRelations.keys():
            for resource in directRelations[predicate]:
                self.relations.append(resource)
        
        inverseRelations = datamanager.findInverseRelations(self.resource.uri())
        for tuple in inverseRelations:
            resource = tuple[0]
            self.relations.append(resource)

        self.loop = gobject.MainLoop()
        datamanager.analyzeText(self.text, self.newEntityHandler, self.finishedAnalyzisHandler)
        
        datamanager.analyzeText(self.title, self.newEntityHandler, self.finishedAnalyzisHandler)
        
        if self.doImageAnalysis:
            print "analysing image %s" % self.path
            datamanager.analyzeResource(self.path, self.newEntityHandler, self.textExtractedHandler, self.finishedImageAnalyzisHandler)
        
        
        self.loop.run()
        #TODO: handle stop


    def createContextMenu(self, index, selection):
        return SuggestionContextMenu(self, selection)
    
    def processAction(self, key, selectedResources):
        super(SuggestionsTable, self).processAction(key, selectedResources)
        if key == CREATE_RELATION:
            for resource in selectedResources:
                self.resource.addProperty(Soprano.Vocabulary.NAO.isRelated(), Nepomuk.Variant(resource))
                self.removeResource(resource.resourceUri())


class SuggestionContextMenu(ObjectContextMenu):
    def __init__(self, parent, selectedResources):
        super(SuggestionContextMenu, self).__init__(parent, selectedResources)

    def createActions(self):
        self.addRelationAction()
        self.addOpenAction()
        self.addExternalOpenAction()
        self.addSendMailAction()
        self.addSetAsContextAction()
        self.addDeleteAction()

    def addRelationAction(self):
        action = QAction(i18n("&Create relation(s)"), self)
        action.setProperty("key", QVariant(CREATE_RELATION))
        action.setIcon(KIcon("nepomuk"))
        self.addAction(action)
