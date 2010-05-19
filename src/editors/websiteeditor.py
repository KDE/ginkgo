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
from PyQt4 import Qsci, QtGui, QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from dao import datamanager
from ontologies import NFO, NIE, PIMO, NCO
from editors.resourceeditor import ResourceEditor, ResourceEditorUi
from util.krun import krun
from PyKDE4.kdecore import KUrl
from PyKDE4.kdecore import i18n

class WebsiteEditor(ResourceEditor):
    def __init__(self, mainWindow=False, resource=None, nepomukType=None):
        super(WebsiteEditor, self).__init__(mainWindow=mainWindow, resource=resource, nepomukType=nepomukType)
        self.defaultIcon = ""
        self.ui = WebsiteEditorUi(self)
    
    def save(self):
        
        super(WebsiteEditor, self).save()
        
        self.resource.setProperty(NIE.url, Nepomuk.Variant(self.ui.url.text()))
            

class WebsiteEditorUi(ResourceEditorUi):
    
    def createMainPropertiesWidget(self, parent):

        propertiesWidget = QWidget(parent)

        self.gridlayout = QGridLayout(propertiesWidget)

        self.name = QLineEdit(propertiesWidget)
        self.name.setObjectName("name")

        self.name.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        fnameBox = QGroupBox(i18n("Name"))
        vbox = QVBoxLayout(fnameBox)
        vbox.addWidget(self.name)
        self.gridlayout.addWidget(fnameBox, 0, 0, 1, 1)
       
        box = QGroupBox(i18n("URL"))
        vbox = QVBoxLayout(box)
        self.url = QLineEdit(propertiesWidget)
        self.url.setObjectName("url")
        vbox.addWidget(self.url)
        
        button = QPushButton(propertiesWidget)
        button.setText(i18n("Open"))
        button.clicked.connect(self.openWebPage)
        vbox.addWidget(button)
        
        self.gridlayout.addWidget(box, 2, 0, 1, 1)

        spacerItem = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 4, 0, 1, 1)
        

        return propertiesWidget
    
    def openWebPage(self):
        kurl = KUrl(self.url.text())
        krun(kurl, QWidget(), False)
        
    def updateFields(self):
        if self.editor.resource:
            self.name.setText(self.editor.resource.genericLabel())
            
            if len(self.editor.resource.property(NIE.url).toString()) > 0:
                self.url.setText(self.editor.resource.property(NIE.url).toString())
            else:
                self.url.setText(self.editor.resource.uri())
            
            self.description.setText(self.editor.resource.description())

    def retranslateUi(self):
        super(WebsiteEditorUi, self).retranslateUi()
#        self.firstname_label.setText(QApplication.translate("PersonEditDialog", "&First Name:", None, QApplication.UnicodeUTF8))
#        self.lastname_label.setText(QApplication.translate("PersonEditDialog", "&Last Name:", None, QApplication.UnicodeUTF8))
#        self.email_label.setText(QApplication.translate("PersonEditDialog", "&E-mail:", None, QApplication.UnicodeUTF8))        
#        self.phone_label.setText(QApplication.translate("PersonEditDialog", "&Phone:", None, QApplication.UnicodeUTF8))


    def resourceLabel(self):
        return self.name.text()
    