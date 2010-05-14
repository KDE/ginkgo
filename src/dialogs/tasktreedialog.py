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
from editors.tasktree import TaskTree
from PyKDE4 import nepomuk
from PyKDE4.kdecore import i18n

class TaskTreeDialogUi(object):

    def setupUi(self, dialog, hiddenTask=None):
        
        dialog.setObjectName("dialog")
        dialog.resize(300, 300)
        self.gridlayout = QGridLayout(dialog)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.taskTreeWidget = TaskTree(mainWindow=dialog.parent(), makeActions=False, hiddenTask=hiddenTask)
        self.gridlayout.addWidget(self.taskTreeWidget, 0, 0, 1, 1)
      
        self.buttonBox = QDialogButtonBox(dialog)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.NoButton | QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridlayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(dialog)
        QObject.connect(self.buttonBox, SIGNAL("accepted()"), dialog.accept)
        QObject.connect(self.buttonBox, SIGNAL("rejected()"), dialog.reject)
        QMetaObject.connectSlotsByName(dialog)
        

        
    def retranslateUi(self, dialog):
        dialog.setWindowTitle(QApplication.translate("TaskTreeDialog", i18n("Task Selection"), None, QApplication.UnicodeUTF8))

class TaskTreeDialog(QDialog, TaskTreeDialogUi):

    def __init__(self, parent=None, hiddenTask=None):
        super(TaskTreeDialog, self).__init__(parent)
        self.setupUi(self, hiddenTask)
        QObject.connect(self.taskTreeWidget.tasktree.selectionModel(), SIGNAL("selectionChanged(QItemSelection, QItemSelection)"), self.slot) 
        self.validate()

    def slot(self, selected, deselected):
        self.validate()
        
    def validate(self):
        index = self.taskTreeWidget.tasktree.selectionModel().currentIndex()
        self.selectedTask = self.taskTreeWidget.tasktree.model().getItem(index).data(0)
        
        if type(self.selectedTask) is nepomuk.Nepomuk.Resource:
            #flag = self.selectedTask.uri() == self.unselectableTask.uri()
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        else:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def accept(self):
        
        index = self.taskTreeWidget.tasktree.selectionModel().currentIndex()
        self.selectedTask = self.taskTreeWidget.tasktree.model().getItem(index).data(0)
        QDialog.accept(self)

    def getPerson(self):
        return [self.firstname.text(), self.lastname.text(), self.email.text(), self.notes.toPlainText()]

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    form = TaskTreeDialog()
    form.show()
    app.exec_()

