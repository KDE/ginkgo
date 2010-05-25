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
from PyKDE4.kdeui import KIcon
from PyKDE4.kdecore import i18n
from ginkgo.ontologies import NFO, NCO
from ginkgo.actions import *

class ResourceContextMenu(QMenu):
    def __init__(self, parent=None, selectedUris=False):
        super(ResourceContextMenu, self).__init__(parent)
        self.selectedUris = selectedUris
        self.parent = parent
        self.createActions()

        self.triggered.connect(self.actionTriggered)
        QMetaObject.connectSlotsByName(self)
    
    def actionTriggered(self, action):
        
        key = action.property("key").toString()
        self.parent.processAction(key, self.selectedUris)
        
    def createActions(self):
        self.addOpenAction()
        self.addExternalOpenAction()
        self.addSendMailAction()
        self.addSetAsContextAction()
        self.addDeleteAction()
        

    def addOpenAction(self):
        openInNewTabAction = QAction(i18n("&Open in new tab"), self)
        openInNewTabAction.setProperty("key", QVariant(OPEN_IN_NEW_TAB))
        openInNewTabAction.setIcon(KIcon("tab-new-background-small"))
        self.addAction(openInNewTabAction)
    
    def addDeleteAction(self):
        action = QAction(i18n("&Delete"), self)
        action.setProperty("key", QVariant(DELETE))
        action.setToolTip(i18n("Delete this resource from the Nepomuk database"))
        action.setIcon(KIcon("edit-delete"))
        self.addAction(action)

    def addExternalOpenAction(self):
        if len(self.selectedUris) == 1:
            resource = Nepomuk.Resource(self.selectedUris[0])
            if resource and NFO.FileDataObject in resource.types(): 
                action = QAction(i18n("Open &file"), self)
                action.setProperty("key", QVariant(OPEN_FILE))
                self.addAction(action)
    
            if resource and NFO.Website in resource.types():
                action = QAction(i18n("Open &page"), self)
                action.setProperty("key", QVariant(OPEN_PAGE))
                self.addAction(action)
        


    def addSendMailAction(self):
        for item in self.selectedUris:
            res = Nepomuk.Resource(item)
            #TODO: check that the NCO.emailAddress property is not void
            if not NCO.PersonContact in res.types():
                return
        action = QAction(i18n("&Write e-mail to"), self)
        action.setProperty("key", QVariant(WRITE_EMAIL))
        self.addAction(action)
        
    def addSetAsContextAction(self):
        if len(self.selectedUris) == 1:
            action = QAction(i18n("Set as &context"), self)
            action.setProperty("key", QVariant(SET_AS_CONTEXT))
            self.addAction(action)
            
