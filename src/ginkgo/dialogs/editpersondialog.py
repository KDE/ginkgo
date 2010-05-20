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

from PyQt4.QtCore import Qt, SIGNAL, QObject, QMetaObject, QString
from PyQt4.QtGui import QGridLayout, QLabel, QLineEdit, QTextEdit, QDialogButtonBox, QApplication, QDialog

class EditPersonDialogUi(object):
    def setupUi(self, dialog):
        dialog.setObjectName("dialog")
        dialog.resize(300, 300)
        self.gridlayout = QGridLayout(dialog)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        
        self.firstname_label = QLabel(dialog)
        self.firstname_label.setObjectName("firstname_label")
        self.gridlayout.addWidget(self.firstname_label, 0, 0, 1, 1)
        self.firstname = QLineEdit(dialog)
        self.firstname.setObjectName("firstname")
        self.gridlayout.addWidget(self.firstname, 0, 1, 1, 5)
        self.firstname_label.setBuddy(self.firstname)

        
        self.lastname_label = QLabel(dialog)
        self.lastname_label.setObjectName("lastname_label")
        self.gridlayout.addWidget(self.lastname_label, 1, 0, 1, 1)
        self.lastname = QLineEdit(dialog)
        self.lastname.setObjectName("lastname")
        self.gridlayout.addWidget(self.lastname, 1, 1, 1, 5)
        self.lastname_label.setBuddy(self.lastname)
        
        self.email_label = QLabel(dialog)
        self.email_label.setObjectName("email_label")
        self.gridlayout.addWidget(self.email_label, 2, 0, 1, 1)
        self.email = QLineEdit(dialog)
        self.email.setObjectName("email")
        self.gridlayout.addWidget(self.email, 2, 1, 1, 5)
        self.email_label.setBuddy(self.email)
        
        self.phone_label = QLabel(dialog)
        self.phone_label.setObjectName("phone_label")
        self.gridlayout.addWidget(self.phone_label, 3, 0, 1, 1)
        self.phone = QLineEdit(dialog)
        self.phone.setObjectName("phone")
        self.gridlayout.addWidget(self.phone, 3, 1, 1, 5)
        self.phone_label.setBuddy(self.phone)

        #spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        #self.gridlayout.addItem(spacerItem, 1, 5, 1, 1)
        

        self.notes_label = QLabel(dialog)
        self.notes_label.setObjectName("notes_label")
        self.gridlayout.addWidget(self.notes_label, 4, 0, 1, 3)

        
        self.notes = QTextEdit(dialog)
        self.notes.setTabChangesFocus(True)
        self.notes.setLineWrapMode(QTextEdit.NoWrap)
        self.notes.setAcceptRichText(False)
        self.notes.setObjectName("notes")
        self.gridlayout.addWidget(self.notes, 5, 0, 1, 6)
        self.notes_label.setBuddy(self.notes)

        self.buttonBox = QDialogButtonBox(dialog)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.NoButton | QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridlayout.addWidget(self.buttonBox, 6, 4, 1, 2)

        self.retranslateUi(dialog)
#        self.buttonBox.accepted(dialog.accept)
#        self.buttonBox.rejected(dialog.reject)
        QMetaObject.connectSlotsByName(dialog)
        
        #dialog.setTabOrder(self.firstname, self.yearSpinBox)
        #dialog.setTabOrder(self.yearSpinBox, self.minutesSpinBox)
        
    def retranslateUi(self, dialog):
        dialog.setWindowTitle(QApplication.translate("PersonEditDialog", "New Contact", None, QApplication.UnicodeUTF8))
        self.firstname_label.setText(QApplication.translate("PersonEditDialog", "&First Name:", None, QApplication.UnicodeUTF8))
        self.lastname_label.setText(QApplication.translate("PersonEditDialog", "&Last Name:", None, QApplication.UnicodeUTF8))
        self.email_label.setText(QApplication.translate("PersonEditDialog", "&E-mail:", None, QApplication.UnicodeUTF8))        
        self.notes_label.setText(QApplication.translate("PersonEditDialog", "&Notes:", None, QApplication.UnicodeUTF8))
        self.phone_label.setText(QApplication.translate("PersonEditDialog", "&Phone:", None, QApplication.UnicodeUTF8))



class EditPersonDialog(QDialog, EditPersonDialogUi):

    def __init__(self, person=None, parent=None):
        super(EditPersonDialog, self).__init__(parent)
        self.setupUi(self)

        self.person = person
        
        if person is not None:
            #self.titleLineEdit.setText(person.title)
            #self.notesTextEdit.setPlainText(person.notes)
            #self.buttonBox.button(QDialogButtonBox.Ok).setText(
            #        "&Accept")
            self.setWindowTitle("Edit Contact")
        else:
            pass
        self.validate()



    def on_firstname_textEdited(self, text):
        self.validate()
        
    def on_lastname_textEdited(self, text):
        self.validate()

    def on_email_textEdited(self, text):
        self.validate()

    def validate(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(
                not self.firstname.text().isEmpty() or not self.lastname.text().isEmpty()
                or not self.email.text().isEmpty())


    def accept(self):
        QDialog.accept(self)


    def getPerson(self):
        return [self.firstname.text(), self.lastname.text(), self.email.text(), self.notes.toPlainText()]
    

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = EditPersonDialog(0)
    form.show()
    app.exec_()

