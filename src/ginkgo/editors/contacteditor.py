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
from PyKDE4.soprano import Soprano
from PyQt4 import Qsci, QtGui, QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ginkgo.dao import datamanager
from ginkgo.ontologies import NFO, NIE, PIMO, NCO
from os import listdir
from os.path import isfile, isdir, expanduser, join
from ginkgo.editors.resourceeditor import ResourceEditor, ResourceEditorUi
import codecs
from PyKDE4.kdecore import i18n


class ContactEditor(ResourceEditor):
    def __init__(self, mainWindow=False, resource=None, nepomukType=None):
        super(ContactEditor, self).__init__(mainWindow=mainWindow, resource=resource, nepomukType=nepomukType)
        self.defaultIcon = ""
        
        self.ui = ContactEditorUi(self)
    
            
    def save(self):
        
        super(ContactEditor, self).save()
        
        self.resource.setProperty(NCO.nameGiven, Nepomuk.Variant(self.ui.firstname.text()))
        self.resource.setProperty(NCO.nameFamily, Nepomuk.Variant(self.ui.lastname.text()))
        self.resource.setProperty(NCO.emailAddress, Nepomuk.Variant(self.ui.email.text()))
        self.resource.setProperty(NCO.phoneNumber, Nepomuk.Variant(self.ui.phone.text()))
    
    def focus(self):
        self.ui.firstname.setFocus(Qt.OtherFocusReason)    
    

class ContactEditorUi(ResourceEditorUi):
    
    
    def nameTextEditedSlot(self, text):
        self.label.setText(str(self.firstname.text()).strip()+" "+str(self.lastname.text()).strip())
    
    def createMainPropertiesWidget(self, parent):

        propertiesWidget = QWidget(parent)

        self.gridlayout = QGridLayout(propertiesWidget)
        self.gridlayout.setObjectName("gridlayout")
        
        self.firstname = QLineEdit(propertiesWidget)
        self.firstname.setObjectName("name")
        self.firstname.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        fnameBox = QGroupBox(i18n("First Name"))
        vbox = QVBoxLayout(fnameBox)
        vbox.addWidget(self.firstname)
        self.gridlayout.addWidget(fnameBox, 0, 0, 1, 1)
       
        
        self.lastname = QLineEdit(propertiesWidget)
        self.lastname.setObjectName("name")

        #update the label field automatically only if it's empty
        if self.editor.resource is None or len(self.editor.resource.property(Soprano.Vocabulary.NAO.prefLabel()).toString()) == 0:
            self.firstname.textEdited.connect(self.nameTextEditedSlot)
            self.lastname.textEdited.connect(self.nameTextEditedSlot)

        
        lnameBox = QGroupBox(i18n("Last Name"))
        vbox = QVBoxLayout(lnameBox)
        vbox.addWidget(self.lastname)
        self.gridlayout.addWidget(lnameBox, 1, 0, 1, 1)
        
        box = QGroupBox(i18n("E-mail"))
        vbox = QVBoxLayout(box)
        self.email = QLineEdit(propertiesWidget)
        self.email.setObjectName("email")
        vbox.addWidget(self.email)
        self.gridlayout.addWidget(box, 2, 0, 1, 1)


        box = QGroupBox(i18n("Phone"))
        vbox = QVBoxLayout(box)
        self.phone = QLineEdit(propertiesWidget)
        self.phone.setObjectName("phone")
        vbox.addWidget(self.phone)
        self.gridlayout.addWidget(box, 3, 0, 1, 1)

        spacerItem = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 4, 0, 1, 1)


        return propertiesWidget

    def updateFields(self):
        super(ContactEditorUi, self).updateFields()
        if self.editor.resource:
            self.firstname.setText(self.editor.resource.property(NCO.nameGiven).toString())
            self.lastname.setText(self.editor.resource.property(NCO.nameFamily).toString())
            self.email.setText(self.editor.resource.property(NCO.emailAddress).toString())
            self.phone.setText(self.editor.resource.property(NCO.phoneNumber).toString())


    