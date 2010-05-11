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
from dao import datamanager, PIMO, NCO
from os import listdir
from os.path import isfile, isdir, expanduser, join
from editors.resourceeditor import ResourceEditor, ResourceEditorUi
import codecs


class ContactEditor(ResourceEditor):
    def __init__(self, mainWindow=False, resource=None, nepomukType=None):
        super(ContactEditor, self).__init__(mainWindow=mainWindow, resource=resource, nepomukType=nepomukType)
        self.defaultIcon = ":/contact-large"
        
        self.ui = ContactEditorUi(self)
    
            
    def save(self):
        
        super(ContactEditor, self).save()
        
        
        self.resource.setProperty(NCO.nameGiven, Nepomuk.Variant(self.ui.firstname.text()))
        self.resource.setProperty(NCO.nameFamily, Nepomuk.Variant(self.ui.lastname.text()))
        self.resource.setProperty(NCO.emailAddress, Nepomuk.Variant(self.ui.email.text()))
        self.resource.setProperty(NCO.phoneNumber, Nepomuk.Variant(self.ui.phone.text()))
        
            

class ContactEditorUi(ResourceEditorUi):
    
    def createMainPropertiesWidget(self, parent):

        propertiesWidget = QWidget(parent)

        self.gridlayout = QGridLayout(propertiesWidget)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        
        self.gridlayout.setColumnStretch(0, 1)
        self.gridlayout.setColumnStretch(1, 20)


 
#        self.firstname_label = QLabel(propertiesWidget)
#        self.firstname_label.setObjectName("firstname_label")
#        self.firstname_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
#        self.gridlayout.addWidget(self.firstname_label, 0, 0, 1, 1)
        self.firstname = QLineEdit(propertiesWidget)
        self.firstname.setObjectName("name")
        self.firstname.setMinimumWidth(180)
        
        self.firstname.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
#        self.firstname_label.setBuddy(self.firstname)
        fnameBox = QGroupBox("First Name")
        #self.name_label = QLabel(propertiesWidget)
        #self.name_label.setObjectName("name_label")
        #self.gridlayout.addWidget(self.name_label, 1, 0, 1, 1)
        vbox = QVBoxLayout(fnameBox)
        vbox.addWidget(self.firstname)
        self.gridlayout.addWidget(fnameBox, 0, 0, 1, 1)
       
        
        self.lastname_label = QLabel(propertiesWidget)
        self.lastname_label.setObjectName("lastname_label")
        #self.gridlayout.addWidget(self.lastname_label, 1, 0, 1, 1)
        self.lastname = QLineEdit(propertiesWidget)
        self.lastname.setObjectName("name")
        #self.gridlayout.addWidget(self.lastname, 1, 1, 1, 1)
        #self.lastname_label.setBuddy(self.lastname)
        
        lnameBox = QGroupBox("Last Name")
        #self.name_label = QLabel(propertiesWidget)
        #self.name_label.setObjectName("name_label")
        #self.gridlayout.addWidget(self.name_label, 1, 0, 1, 1)
        vbox = QVBoxLayout(lnameBox)
        vbox.addWidget(self.lastname)
        self.gridlayout.addWidget(lnameBox, 1, 0, 1, 1)
       
        
        box = QGroupBox("Email")
        vbox = QVBoxLayout(box)
        self.email = QLineEdit(propertiesWidget)
        self.email.setObjectName("email")
        vbox.addWidget(self.email)
        self.gridlayout.addWidget(box, 2, 0, 1, 1)

        
#        self.email_label = QLabel(propertiesWidget)
#        self.email_label.setObjectName("email_label")
#        self.gridlayout.addWidget(self.email_label, 2, 0, 1, 1)
#        self.email = QLineEdit(propertiesWidget)
#        self.email.setObjectName("email")
#        self.gridlayout.addWidget(self.email, 2, 1, 1, 1)
#        self.email_label.setBuddy(self.email)
        
#        self.phone_label = QLabel(propertiesWidget)
#        self.phone_label.setObjectName("phone_label")
#        self.gridlayout.addWidget(self.phone_label, 3, 0, 1, 1)
#        self.phone = QLineEdit(propertiesWidget)
#        self.phone.setObjectName("phone")
#        self.gridlayout.addWidget(self.phone, 3, 1, 1, 1)
#        self.phone_label.setBuddy(self.phone)

        box = QGroupBox("Phone")
        vbox = QVBoxLayout(box)
        self.phone = QLineEdit(propertiesWidget)
        self.phone.setObjectName("phone")
        vbox.addWidget(self.phone)
        self.gridlayout.addWidget(box, 3, 0, 1, 1)

        spacerItem = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 4, 0, 1, 1)
        

        return propertiesWidget

    def updateFields(self):
        if self.editor.resource:
            self.firstname.setText(self.editor.resource.property(NCO.nameGiven).toString())
            self.lastname.setText(self.editor.resource.property(NCO.nameFamily).toString())
            self.email.setText(self.editor.resource.property(NCO.emailAddress).toString())
            self.phone.setText(self.editor.resource.property(NCO.phoneNumber).toString())
            self.description.setText(self.editor.resource.description())

    def retranslateUi(self):
        super(ContactEditorUi, self).retranslateUi()
#        self.firstname_label.setText(QApplication.translate("PersonEditDialog", "&First Name:", None, QApplication.UnicodeUTF8))
#        self.lastname_label.setText(QApplication.translate("PersonEditDialog", "&Last Name:", None, QApplication.UnicodeUTF8))
#        self.email_label.setText(QApplication.translate("PersonEditDialog", "&E-mail:", None, QApplication.UnicodeUTF8))        
#        self.phone_label.setText(QApplication.translate("PersonEditDialog", "&Phone:", None, QApplication.UnicodeUTF8))


    def resourceLabel(self):
        return self.firstname.text()+" "+self.lastname.text()
    