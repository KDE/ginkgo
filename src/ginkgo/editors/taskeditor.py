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
from ginkgo.ontologies import TMO
from ginkgo.dialogs.tasktreedialog import TaskTreeDialog
from ginkgo.editors.resourceeditor import ResourceEditor, ResourceEditorUi
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

        state = TMO.TMO_Instance_TaskState_New
        if self.ui.stateRunning.isChecked():
            state = TMO.TMO_Instance_TaskState_Running
        elif self.ui.stateCompleted.isChecked():
            state = TMO.TMO_Instance_TaskState_Completed
            
        dueDate = None
        if self.ui.dateBox.isChecked():
            dueDate = self.ui.dueDate.date()
        
        self.resource.setLabel(self.ui.label.text())
        self.resource.setProperty(TMO.priority, Nepomuk.Variant(priority))
        self.resource.setProperty(TMO.taskState, Nepomuk.Variant(state))
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
        super(TaskEditorUi, self).updateFields()
        
        if self.editor.resource:
            property = self.editor.resource.property(TMO.priority)
            if property and len(property.toString())>0:
                if property.toString() == TMO.TMO_Instance_Priority_Low.toString():
                    self.lowPriority.setChecked(True)
                elif property.toString() == TMO.TMO_Instance_Priority_High.toString():
                    self.highPriority.setChecked(True)
                else:
                    self.mediumPriority.setChecked(True)

            state = self.editor.resource.property(TMO.taskState).toUrl()
            if not state or state.isEmpty():
                state = TMO.TMO_Instance_TaskState_New
            if state == TMO.TMO_Instance_TaskState_Completed:
                self.stateCompleted.setChecked(True)
            elif state == TMO.TMO_Instance_TaskState_Running:
                self.stateRunning.setChecked(True)
            else:
                self.stateNew.setChecked(True)
                    
            dueDate = self.editor.resource.property(TMO.dueDate)
            if dueDate and dueDate.toDate():
                self.dateBox.setChecked(True)
                self.dueDate.setDate(dueDate.toDate())
                
        
        if self.editor.superTask is not None:
            self.superTaskRadio.setChecked(True)
            self.superTaskRadio.setText(self.editor.superTask.genericLabel())
        

    def createMainPropertiesWidget(self, parent):
        propertiesWidget = QWidget(parent)

        self.vboxl = QVBoxLayout(propertiesWidget)
        
        parentBox = QGroupBox(i18n("Parent Task"))
        self.noSuperTaskRadio = QRadioButton(i18n("Non&e"))
        self.superTaskRadio = QRadioButton(i18n("&Other"))
        self.noSuperTaskRadio.setChecked(True)
        vbox = QVBoxLayout()
        vbox.addWidget(self.noSuperTaskRadio)
        vbox.addWidget(self.superTaskRadio)
        button = QPushButton(propertiesWidget)
        button.setObjectName("Parent")
        button.setText(i18n("Select..."))
        button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        vbox.addWidget(button)
        parentBox.setLayout(vbox)
        self.vboxl.addWidget(parentBox)
        parentBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.noSuperTaskRadio.toggled.connect(self.editor.superTaskToggled)
        self.editor.connect(button, SIGNAL("clicked()"), self.editor.selectSuperTask)

        priorityBox = QGroupBox(i18n("Priority"))
        self.lowPriority = QRadioButton(i18n("&Low"))
        self.mediumPriority = QRadioButton(i18n("&Medium"))
        self.highPriority = QRadioButton(i18n("&High"))
        vbox = QVBoxLayout()
        vbox.addWidget(self.lowPriority)
        vbox.addWidget(self.mediumPriority)
        vbox.addWidget(self.highPriority)
        priorityBox.setLayout(vbox)
        self.vboxl.addWidget(priorityBox)
        priorityBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.dateBox = QGroupBox(i18n("Due date"))
        self.dateBox.setCheckable(True)
        hbox = QHBoxLayout()
        self.dueDate = QDateEdit()
        hbox.addWidget(self.dueDate)
        self.dateBox.setLayout(hbox)
        self.vboxl.addWidget(self.dateBox)
        self.dateBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.dateBox.setChecked(False)
        self.dueDate.setDate(QDate.currentDate())

        stateBox = QGroupBox(i18n("State"))
        self.stateNew = QRadioButton(i18n("New"))
        self.stateRunning = QRadioButton(i18n("Running"))
        self.stateCompleted = QRadioButton(i18n("Completed"))
        vbox = QVBoxLayout()
        vbox.addWidget(self.stateNew)
        vbox.addWidget(self.stateRunning)
        vbox.addWidget(self.stateCompleted)
        stateBox.setLayout(vbox)
        self.vboxl.addWidget(stateBox)
        stateBox.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        spacerItem = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.vboxl.addItem(spacerItem)
        
        return propertiesWidget
