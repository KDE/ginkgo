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
from dao import NFO


class ResourceContextMenu(QMenu):
    def __init__(self, parent=None, selectedUris=False):
        super(ResourceContextMenu, self).__init__(parent)
        self.selectedUris = selectedUris
        self.parent = parent
        self.createActions()
                    
        
        self.triggered.connect(self.actionTriggered)
        QMetaObject.connectSlotsByName(self)
    
    def actionTriggered(self, action):
        key = unicode(action.text())
        self.parent.processAction(key, self.selectedUris)
        
    def createActions(self):
        self.addOpenAction()
        self.addExternalOpenAction()
        self.addDeleteAction()

    def addOpenAction(self):
        openInNewTabAction = QAction("Open in new tab", self)
        openInNewTabAction.setIcon(KIcon("tab-new-background-small"))
        self.addAction(openInNewTabAction)
    
    def addDeleteAction(self):
        action = QAction("Delete", self)
        action.setToolTip("Delete this resource from the Nepomuk database")
        action.setIcon(KIcon("edit-delete"))
        self.addAction(action)

    def addExternalOpenAction(self):
        if len(self.selectedUris) == 1:
            resource = Nepomuk.Resource(self.selectedUris[0])
            if resource and NFO.FileDataObject in resource.types(): 
                action = QAction("Open file", self)
                self.addAction(action)
    
            if resource and NFO.Website in resource.types():
                action = QAction("Open page", self)
                self.addAction(action)
        
