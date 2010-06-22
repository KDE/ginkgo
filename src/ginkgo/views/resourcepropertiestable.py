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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ginkgo.dao import datamanager
from ginkgo.ontologies import NFO, NIE, PIMO
from os import system
from os.path import join
from PyKDE4 import soprano
from PyKDE4.kdecore import i18n
from ginkgo.views.resourcestable import ResourcesTable, ResourcesTableModel
import os
import subprocess
from ginkgo.actions import *

class PropertyContextMenu(QMenu):
    def __init__(self, parent=None, propvalue=False):
        super(PropertyContextMenu, self).__init__(parent)
        self.propvalue = propvalue
        self.parent = parent
        self.createActions()
        self.triggered.connect(self.actionTriggered)
        QMetaObject.connectSlotsByName(self)
    
    def actionTriggered(self, action):
        key = action.property("key").toString()
        self.parent.processAction(key, self.propvalue)
        
    def createActions(self):
        if self.propvalue:
            copyAction = QAction(i18n("&Copy value to clipboard"), self)
            copyAction.setProperty("key", QVariant(COPY_TO_CLIPBOARD))
            #openInNewTabAction.setIcon(KIcon("tab-new-background-small"))
            self.addAction(copyAction)
        else:
            newPropertyAction = QAction(i18n("&Add property"), self)
            newPropertyAction.setProperty("key", QVariant(ADD_PROPERTY))
            self.addAction(newPropertyAction)

class ResourcePropertiesTableModel(ResourcesTableModel):
    def __init__(self, parent=None, data=None):
        super(ResourcePropertiesTableModel, self).__init__(parent)
        self.data = data
        
    def itemAt(self, index):
        column = index.column()
        if column == 0:
            propname = self.data[index.row()][0]
            propertyResource = Nepomuk.Resource(QUrl(propname))
            return propertyResource.genericLabel()
            #if propname.find("#") > 0:
            #    propname = propname[propname.find("#") + 1:]
            #return propname
        elif column == 1:
            value = self.data[index.row()][1]
            if value:
                return value.toString()
            return ""

    def rowCount(self, index):
        return len(self.data)
    
    def columnCount(self, index):
        return len(self.headers)

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        if role == Qt.TextAlignmentRole:
            if index.column() == 0:
                return Qt.AlignLeft | Qt.AlignVCenter
            elif index.column() == 1:
                return Qt.AlignLeft | Qt.AlignVCenter
            elif index.column() == 2:
                return Qt.AlignLeft | Qt.AlignVCenter
        elif role == Qt.DisplayRole:

            return self.itemAt(index)
            
        elif role == Qt.DecorationRole:
            if index.column() == 0:
                propuri = self.data[index.row()][0]
                propResource = Nepomuk.Resource(propuri)
                return self.editor.mainWindow.resourceQIcon(propResource)

        return QVariant()

    def headerData(self, section, orientation, role):
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            return self.headers[section]
        else:
            return None

    #bool QAbstractItemModel::insertRows ( int row, int count, const QModelIndex & parent = QModelIndex() )
    def addProperty(self, property):
        self.beginInsertRows(QModelIndex(), len(self.data), len(self.data))
        self.data.append(property)
        self.endInsertRows() 

        
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        if index.column() == 0 or index.column() == 1: 
            predicateUrl = self.data[index.row()][0]
            if predicateUrl in (Soprano.Vocabulary.NAO.identifier(), Soprano.Vocabulary.NAO.prefLabel(), Soprano.Vocabulary.NAO.description(), Soprano.Vocabulary.NAO.lastModified(), Soprano.Vocabulary.NAO.created(), Soprano.Vocabulary.RDFS.range(), Soprano.Vocabulary.RDFS.domain()):
                return Qt.ItemFlags(QAbstractTableModel.flags(self, index))
            
            return Qt.ItemFlags(QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)
            
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index))
    

class ResourcePropertiesTable(ResourcesTable):
    
    def __init__(self, mainWindow=False, resource=None, dialog=None):
        self.resource = resource
        super(ResourcePropertiesTable, self).__init__(mainWindow=mainWindow, dialog=dialog)
        self.resource = resource
        self.table.horizontalHeader().setResizeMode(0, QHeaderView.Interactive)
        self.table.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)
        #self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.SelectedClicked | QTableWidget.DoubleClicked | QTableWidget.EditKeyPressed)
        self.table.setSelectionBehavior(QTableWidget.SelectItems)
        self.table.setItemDelegate(PropertyDelegate(self))


    def createModel(self):
        urisExclude = [Soprano.Vocabulary.NAO.prefLabel(), Soprano.Vocabulary.NAO.description()]
        
        data = datamanager.findResourceLiteralProperties(self.resource, urisExclude)
        if self.resource:
            uriprop = (Soprano.Vocabulary.NAO.identifier(), self.resource.resourceUri())
            data.append(uriprop)
        self.model = ResourcePropertiesTableModel(self, data=data)
        
        self.model.setHeaders([i18n("Property"), i18n("Value")])


    def showContextMenu(self, points):
        index = self.table.indexAt(points)
        if index.isValid():
            #convert the proxy index to the source index
            #see http://doc.trolltech.com/4.6/qsortfilterproxymodel.html
            sourceIndex = self.table.model().mapToSource(index)
            propvalue = self.table.model().sourceModel().data[sourceIndex.row()]
            if index.column() == 1 and propvalue:
                menu = self.createContextMenu(index, propvalue)
            else:
                return
        else:
            menu = self.createContextMenu(index, None)
        
        pos = self.table.mapToGlobal(points)
        menu.exec_(pos)
                
                
    def createContextMenu(self, index, propvalue):
        return PropertyContextMenu(self, propvalue)

    def setResource(self, resource):
        self.resource = resource
        self.installModels()
        self.table.resizeColumnsToContents()
        #without the line below, the table does not use the space available
        self.table.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)

            
    def isActivableColumn(self, column):
        return False
    
    def processAction(self, key, propvalue):
        if key == COPY_TO_CLIPBOARD:
            clipboard = QApplication.clipboard()
            clipboard.setText(propvalue[1].toString())
        elif key == ADD_PROPERTY:
            elt = (Soprano.Vocabulary.RDFS.comment(), Nepomuk.Variant(""))
            self.table.model().sourceModel().addProperty(elt)
            

            
class PropertyDelegate(QItemDelegate):

    def __init__(self, parent=None):
        super(PropertyDelegate, self).__init__(parent)
        self.table = parent
        

    def paint(self, painter, option, index):
        QItemDelegate.paint(self, painter, option, index)


    def sizeHint(self, option, index):
        fm = option.fontMetrics
        if index.column() == 0:
            return QSize(fm.width("is organization member"), fm.height())
        return QItemDelegate.sizeHint(self, option, index)


    def createEditor(self, parent, option, index):
        if index.column() == 0:
            combobox = QComboBox(parent)
            combobox.setEditable(False)
            props = []
            
            #we list the properties that are compatible with the subject type
            #the subject type depends on the direction of the relation: current resource 
            #is subject or is object of the relation?
            

            for property in datamanager.resourceTypesProperties(self.table.resource, False, True):
                item = property.label("en") + " [" + datamanager.ontologyAbbreviationForUri(property.uri(), True) + "]"
                props.append((property, item))
                 
            self.sortedProps = sorted(props, key=lambda tuple: tuple[1])            
            
            
            for tuple in self.sortedProps: 
                combobox.addItem(tuple[1], QVariant(str(tuple[0].uri().toString())))
            
            return combobox
        elif index.column() == 1:
            #edition of a property value
            #identify the range of the property
            sindex = self.table.table.model().mapToSource(index)
            propertyUrl = index.model().sourceModel().data[sindex.row()][0]
            
            #TODO: see why property.range() won't return the expected range URI.
            #Until then,  we use a the property as a resource
            #property = Nepomuk.Types.Property(QUrl(propertyStr))
            
            propertyResource = Nepomuk.Resource(propertyUrl)
            range = str(propertyResource.property(Soprano.Vocabulary.RDFS.range()).toString())
            
            #"boolean", "integer", "dateTime", "date", "duration", "float",  "int", "nonNegativeInteger", "string"]:
            #"http://www.w3.org/2000/01/rdf-schema#Literal"

            if range in ("http://www.w3.org/2001/XMLSchema#duration", "http://www.w3.org/2001/XMLSchema#integer", "http://www.w3.org/2001/XMLSchema#int", "http://www.w3.org/2001/XMLSchema#nonNegativeInteger"):
                spinbox = QSpinBox(parent)
                spinbox.setRange(0, 100000000)
                spinbox.setSingleStep(1)
                spinbox.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
                spinbox.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                return spinbox
            
            elif range in ("http://www.w3.org/2001/XMLSchema#float"):
                dspinbox = QDoubleSpinBox(parent)
                dspinbox.setRange(0, 100000000)
                return dspinbox
            
            elif range == "http://www.w3.org/2001/XMLSchema#date":
                dateEdit = QDateEdit(parent)
                return dateEdit
            
            elif range == "http://www.w3.org/2001/XMLSchema#dateTime":
                dateEdit = QDateTimeEdit(parent)
                return dateEdit
            else:
                editor = QLineEdit(parent)
                editor.returnPressed.connect(self.commitAndCloseEditor)
                return editor
            
                
                 
            
        else:
            return None


    def commitAndCloseEditor(self):
        editor = self.sender()
#        if isinstance(editor, (QTextEdit, QLineEdit)):
#            self.emit(SIGNAL("commitData(QWidget*)"), editor)
#            self.emit(SIGNAL("closeEditor(QWidget*)"), editor)


    def setEditorData(self, editor, index):

        if index.column() == 0:
            sindex = self.table.table.model().mapToSource(index)
            propUrl = index.model().sourceModel().data[sindex.row()][0]

            i = 0
            for propElt in self.sortedProps:
                if propUrl == propElt[0].uri():
                    editor.setCurrentIndex(i)
                    break
                i = i + 1
           
        elif index.column() == 1:
            sindex = self.table.table.model().mapToSource(index)
            value = index.model().sourceModel().data[sindex.row()][1]
            #TODO: fix that (class comparison won't work since QSpinBox.__class__ is a pyqtWrapperType
            if str(editor.__class__) == "<class 'PyQt4.QtGui.QSpinBox'>":
                editor.setValue(value.toInt())
            
            elif str(editor.__class__) == "<class 'PyQt4.QtGui.QDoubleSpinBox'>":    
                editor.setValue(value.toDouble()) 
                
            elif str(editor.__class__) == "<class 'PyQt4.QtGui.QDateEdit'>":
                editor.setDate(value.toDate())
            
            elif str(editor.__class__) == "<class 'PyQt4.QtGui.QDateTimeEdit'>":
                editor.setDateTime(value.toDateTime())
            
            elif str(editor.__class__) == "<class 'PyQt4.QtGui.QLineEdit'>":
                editor.setText(value.toString())

    def setModelData(self, editor, model, index):
        if index.column() == 0:
            sindex = self.table.table.model().mapToSource(index)
            cindex = editor.currentIndex()
            predicateUrl = index.model().sourceModel().data[sindex.row()][0]
            value = index.model().sourceModel().data[sindex.row()][1]
            
            newPredicate = self.sortedProps[cindex][0]
            if newPredicate.uri() != predicateUrl:
                self.table.setCursor(Qt.WaitCursor)
                self.table.resource.addProperty(newPredicate.uri(), Nepomuk.Variant(value))
                self.table.resource.removeProperty(predicateUrl, Nepomuk.Variant(value))
                self.table.unsetCursor()
            #here we need to update the model since it won't get updated by signal emission
            index.model().sourceModel().data[sindex.row()] = (newPredicate.uri(), value)
            
        elif index.column() == 1:
            sindex = self.table.table.model().mapToSource(index)
            predicateUrl = index.model().sourceModel().data[sindex.row()][0]
            value = index.model().sourceModel().data[sindex.row()][1]

            #TODO: fix that (class comparison won't work since QSpinBox.__class__ is a pyqtWrapperType
            if str(editor.__class__) in ("<class 'PyQt4.QtGui.QSpinBox'>", "<class 'PyQt4.QtGui.QDoubleSpinBox'>"):
                newValue = editor.value()
                
            elif str(editor.__class__) == "<class 'PyQt4.QtGui.QDateEdit'>":
                newValue = editor.date()
            
            elif str(editor.__class__) == "<class 'PyQt4.QtGui.QDateTimeEdit'>":
                newValue = editor.dateTime()
            
            elif str(editor.__class__) == "<class 'PyQt4.QtGui.QLineEdit'>":
                newValue = editor.text()

            
            self.table.setCursor(Qt.WaitCursor)
            self.table.resource.addProperty(predicateUrl, Nepomuk.Variant(newValue))
            self.table.resource.removeProperty(predicateUrl, Nepomuk.Variant(value))
            self.table.unsetCursor()
            #here we need to update the model since it won't get updated by signal emission
            index.model().sourceModel().data[sindex.row()] = (predicateUrl, Nepomuk.Variant(newValue))
            
