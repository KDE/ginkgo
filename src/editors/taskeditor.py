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
from dao import TMO
from dialogs.tasktreedialog import TaskTreeDialog
from editors.resourceeditor import ResourceEditor, ResourceEditorUi
from PyKDE4.kdecore import i18n

class TaskEditor(ResourceEditor):
    def __init__(self, mainWindow=False, resource=None, nepomukType=None, superTask=None):
        super(TaskEditor, self).__init__(mainWindow=mainWindow, resource=resource, nepomukType=nepomukType)
        
        self.defaultIcon = ""
        self.superTask = None
            
        if self.resource:
            superTask = self.resource.property(TMO.superTask)
            if superTask and superTask.toString():
                self.superTask = Nepomuk.Resource(superTask.toString())
        elif superTask:
            self.superTask = superTask

        self.ui = TaskEditorUi(self)
    
    def save(self):
        
        #TODO: validate that name trimmed is not empty
        super(TaskEditor, self).save()
        
        priority = TMO.TMO_Instance_Priority_Medium
        if self.ui.lowPriority.isChecked():
            priority = TMO.TMO_Instance_Priority_Low
        elif self.ui.highPriority.isChecked():
            priority = TMO.TMO_Instance_Priority_High
            
        dueDate = None
        if self.ui.dateBox.isChecked():
            dueDate = self.ui.dueDate.date()
        
        self.resource.setLabel(self.ui.name.text())
        self.resource.setProperty(TMO.priority, Nepomuk.Variant(priority))
        if dueDate:
            self.resource.setProperty(TMO.dueDate, Nepomuk.Variant(dueDate))
        else:
            self.resource.removeProperty(TMO.dueDate)
        
        if self.superTask is not None:
            self.resource.removeProperty(TMO.superTask)
            self.resource.setProperty(TMO.superTask, Nepomuk.Variant(self.superTask))
            self.mainWindow.emit(SIGNAL('taskHierarchyUpdated'))       
        else:
            #TODO: distinguish between the old and the new task attributes
            self.resource.removeProperty(TMO.superTask)
            self.mainWindow.emit(SIGNAL('taskHierarchyUpdated'))
                
        
    def selectSuperTask(self):
        #self.mainWindow.selectSuperTask(self.resource)
        dialog = TaskTreeDialog(self.mainWindow, hiddenTask=self.resource)
        if dialog.exec_():
            self.superTask = dialog.selectedTask
            self.ui.superTaskRadio.setText(self.superTask.genericLabel())
            self.ui.noSuperTaskRadio.toggled.disconnect()
            self.ui.superTaskRadio.setChecked(True)
            self.ui.noSuperTaskRadio.toggled.connect(self.superTaskToggled)
            

            
    def superTaskToggled(self):
        if self.ui.noSuperTaskRadio.isChecked():
            self.superTask = None
        else:
            self.selectSuperTask()
            

class TaskEditorUi(ResourceEditorUi):
    

    def updateFields(self):
        if self.editor.resource:
            self.name.setText(self.editor.resource.genericLabel())
            self.description.setText(self.editor.resource.description())
            property = self.editor.resource.property(TMO.priority)
            
            if property and len(property.toString())>0:
                if property.toString() == TMO.TMO_Instance_Priority_Low.toString():
                    self.lowPriority.setChecked(True)
                elif property.toString() == TMO.TMO_Instance_Priority_High.toString():
                    self.highPriority.setChecked(True)
                else:
                    self.mediumPriority.setChecked(True)
                    
            dueDate = self.editor.resource.property(TMO.dueDate)
            if dueDate and dueDate.toDate():
                self.dateBox.setChecked(True)
                self.dueDate.setDate(dueDate.toDate())
                
        
        if self.editor.superTask is not None:
            self.superTaskRadio.setChecked(True)
            self.superTaskRadio.setText(self.editor.superTask.genericLabel())
            

    def retranslateUi(self):
        super(TaskEditorUi, self).retranslateUi()
        #self.name_label.setText(QApplication.translate("TaskEditor", "&Name:", None, QApplication.UnicodeUTF8))
        self.noSuperTaskRadio.setText(i18n("Non&e"))
        self.superTaskRadio.setText(i18n("&Other"))
        self.lowPriority.setText(i18n("&Low"))
        self.mediumPriority.setText(i18n("&Medium"))
        self.highPriority.setText(i18n("&High"))
        

    def createMainPropertiesWidget(self, parent):
        propertiesWidget = QWidget(parent)

        self.gridlayout = QGridLayout(propertiesWidget)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        
        nameBox = QGroupBox("Name")
        #self.name_label = QLabel(propertiesWidget)
        #self.name_label.setObjectName("name_label")
        #self.gridlayout.addWidget(self.name_label, 1, 0, 1, 1)
        self.name = QLineEdit(propertiesWidget)
        self.name.setObjectName("name")
        vbox = QVBoxLayout(nameBox)
        vbox.addWidget(self.name)
        self.gridlayout.addWidget(nameBox, 1, 0, 1, 2)
        #self.name_label.setBuddy(self.name)
  
        parentBox = QGroupBox("Parent Task")
        self.noSuperTaskRadio = QRadioButton("None")
        self.superTaskRadio = QRadioButton("Other")
        self.noSuperTaskRadio.setChecked(True)
        vbox = QVBoxLayout()
        vbox.addWidget(self.noSuperTaskRadio)
        vbox.addWidget(self.superTaskRadio)
        button = QPushButton(propertiesWidget)
        button.setObjectName("Parent")
        button.setText("Select...")
        button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        vbox.addWidget(button)
        parentBox.setLayout(vbox)
        self.gridlayout.addWidget(parentBox, 2, 0, 1, 2)
        parentBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.noSuperTaskRadio.toggled.connect(self.editor.superTaskToggled)
        self.editor.connect(button, SIGNAL("clicked()"), self.editor.selectSuperTask)
        

        priorityBox = QGroupBox("Priority")
        self.lowPriority = QRadioButton("Low")
        self.mediumPriority = QRadioButton("Medium")
        self.highPriority = QRadioButton("High")
        vbox = QVBoxLayout()
        vbox.addWidget(self.lowPriority)
        vbox.addWidget(self.mediumPriority)
        vbox.addWidget(self.highPriority)
        priorityBox.setLayout(vbox)
        self.gridlayout.addWidget(priorityBox, 3, 0, 1, 2)
        priorityBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)


        self.dateBox = QGroupBox("Due date")
        self.dateBox.setCheckable(True)
        hbox = QHBoxLayout()
        self.dueDate = QDateEdit()
        hbox.addWidget(self.dueDate)
        self.dateBox.setLayout(hbox)
        self.gridlayout.addWidget(self.dateBox, 4, 0, 1, 2)
        self.dateBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.dateBox.setChecked(False)
        self.dueDate.setDate(QDate.currentDate())
        

        spacerItem = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 5, 0, 1, 1)
        
        return propertiesWidget
    
    def resourceLabel(self):
        return self.name.text()