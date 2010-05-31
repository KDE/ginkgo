#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
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
from ginkgo.editors.propertyeditor import PropertyEditor
import traceback


import mimetypes
import os
import sys
import dbus
from PyKDE4.nepomuk import Nepomuk
from PyKDE4.soprano import Soprano
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdeui import *
from PyKDE4.kdecore import *
from ginkgo.dao import datamanager
from ginkgo.ontologies import NFO, NIE, PIMO, NCO, TMO
from ginkgo.util.krun import krun
from ginkgo.dialogs.livesearchdialog import LiveSearchDialog
from ginkgo.dialogs.resourcechooserdialog import ResourceChooserDialog
from ginkgo.views.typesview import TypesView
from ginkgo.views.resourcesbytypetable import ResourcesByTypeTable
from ginkgo.views.tasktree import TaskTree
from ginkgo.views.resourcestable import ResourcesTable
from ginkgo.editors.classeditor import ClassEditor
from ginkgo.editors.resourceeditor import ResourceEditor
from ginkgo.editors.taskeditor import TaskEditor
from ginkgo.actions import *

from ginkgo import resources_rc


class Ginkgo(KMainWindow):
    def __init__(self, parent=None, uris=None):
        super(Ginkgo, self).__init__(parent)

        self.workarea = KTabWidget()
        #we cannot connect the signal using self.workarea.currentChanged.connect since currentChanged is a method of KTabWidget
        QObject.connect(self.workarea, SIGNAL("currentChanged(int) "), self.currentTabChangedSlot)
        self.workarea.setMovable(True)
        #self.workarea.setCloseButtonEnabled(True)
        self.setCentralWidget(self.workarea)
        
        self.loadPlacesData()
        
        self.createActions()
        
        
        self.createPlacesWidget()
        
        
        
        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.showMessage("Ready", 5000)
        self.currentTabChangedSlot(-1)
        
        #self.restoreSettings(uris is None or len(uris)==0)
        self.restoreSettings()
        self.setWindowTitle("Ginkgo")
        
        if uris and len(uris) > 0:
            for uri in uris:
                try:
                    self.openResource(uri, True, False)
                except Exception, e:
                    print "[Ginkgo] Error while trying to open %s." % uri
                                      

    def createActions(self):

        newResourceActions = []

        for type in self.placesData:
            newResourceActions.append(self.createAction(type[1], getattr(self, "newResourceSlot"), None, type[3], type[4], type[0]))
        
        self.saveAction = self.createAction(i18n("&Save"), self.save, QKeySequence.Save, "document-save", i18n("Save"))
        
        openResourceAction = self.createAction(i18n("&Open"), self.showOpenResourcesDialog, QKeySequence.Open, None, i18n("Open a resource"))
        newTabAction = self.createAction(i18n("New &Tab"), self.newTab, QKeySequence.AddTab, "tab-new-background-small", i18n("Create new tab"))
        closeTabAction = self.createAction(i18n("Close Tab"), self.closeCurrentTab, QKeySequence.Close, "tab-close", i18n("Close tab"))
        quitAction = self.createAction(i18n("&Quit"), self.close, "Ctrl+Q", "application-exit", i18n("Close the application"))

        self.linkToButton = QToolButton()
        self.linkToButton.setToolTip(i18n("Link to..."))
        self.linkToButton.setStatusTip(i18n("Link to..."))
        #linkToButton.setIcon(QIcon(":/nepomuk-small"))
        self.linkToButton.setIcon(KIcon("nepomuk"))
        self.linkToButton.setPopupMode(QToolButton.InstantPopup)
        #linkToButton.setEnabled(False)
        self.linkToMenu = QMenu(self)
        self.linkToMenu.setTitle(i18n("Link to"))
        self.linkToMenu.setIcon(KIcon("nepomuk"))
        self.linkToMenu.addAction(self.createAction(i18n("&Resource"), self.linkTo, None, None, None, None))
        self.linkToMenu.addAction(self.createAction(i18n("&File"), self.linkToFile, None, None, None, NFO.FileDataObject))
        
#        for type in self.placesData:
#            if type[0] != NFO.FileDataObject:
#                self.linkToMenu.addAction(self.createAction(type[1], self.linkTo, None, type[3], None, type[0]))
#            else:
#                self.linkToMenu.addAction(self.createAction(type[1], self.linkToFile, None, type[3], None, type[0]))
                
        self.linkToButton.setMenu(self.linkToMenu)

        #icon: code-context possibly
        self.setContextAction = self.createAction(i18n("Set resource as context"), self.setCurrentResourceAsContext, None, "code-context", i18n("Set the current resource as context"))

        self.stopQueryAction = self.createAction(i18n("Stop query"), self.closeCurrentQuery, None, "process-stop", i18n("Stop query"))
        

        showTypesAction = self.createAction(i18n("View data types"), self.showTypes, None, "code-class", i18n("Display the available data types"))

        showRecentlyModifiedResourceAction = self.createAction(i18n("Recent"), self.showRecentlyModifiedResources, None, "document-open-recent", i18n("Show recently modified resources"))

        mainMenu = self.menuBar().addMenu(i18n("&File"))
        newResourceMenu = QMenu(mainMenu)
        newResourceMenu.setObjectName("menuNewResource")
        newResourceMenu.setTitle(i18n("&New"))
        
        for action in newResourceActions:
            newResourceMenu.addAction(action)
        
        mainMenu.addAction(newResourceMenu.menuAction())
        mainMenu.addAction(openResourceAction)
        mainMenu.addSeparator()
        mainMenu.addAction(self.saveAction)
        mainMenu.addSeparator()
        mainMenu.addAction(newTabAction)
        mainMenu.addAction(closeTabAction)
        mainMenu.addAction(quitAction)
        
        editMenu = self.menuBar().addMenu(i18n("&Edit"))
        self.deleteAction = self.createAction(i18n("&Delete"), self.delete, None, None, i18n("Delete"))
        editMenu.addMenu(self.linkToMenu)
        editMenu.addAction(self.deleteAction)
        
        viewMenu = self.menuBar().addMenu(i18n("&View"))
        for type in self.placesData:
            viewMenu.addAction(self.createAction(type[2], self.showResourcesByType, None, type[3], None, type[0]))
        
        #viewMenu.addAction(self.createAction("Files", self.showResourcesByType, None, None, None, NFO.FileDataObject))
        viewMenu.addSeparator()
        viewMenu.addAction(self.createAction(i18n("Types"), self.showTypes, None, "nepomuk", None, None))
        

        self.menuBar().addMenu(self.helpMenu())
        

        
        mainToolbar = self.addToolBar(i18n("Toolbar"))
        mainToolbar.setIconSize(QSize(18, 18))
        #mainToolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        mainToolbar.setObjectName("MainToolBar")
        
        newResourceButton = QToolButton()
        newResourceButton.setToolTip(i18n("New"))
        newResourceButton.setStatusTip(i18n("New"))
        newResourceButton.setIcon(KIcon("document-new"))
        newResourceButton.setPopupMode(QToolButton.InstantPopup)
        newResourceButton.setMenu(newResourceMenu)
        
#        toolbarWidget = QWidget()
#        hbox = QHBoxLayout(toolbarWidget)
#        hbox.addWidget(newResourceButton)
        
        mainToolbar.addWidget(newResourceButton)
        

        #mainToolbar.addAction(action)
        
        mainToolbar.addAction(self.saveAction)
        mainToolbar.addAction(newTabAction)
        mainToolbar.addAction(self.stopQueryAction)
        mainToolbar.addSeparator()
        
        mainToolbar.addWidget(self.linkToButton)
        mainToolbar.addAction(self.setContextAction)
        mainToolbar.addSeparator()
        mainToolbar.addAction(showRecentlyModifiedResourceAction)
        mainToolbar.addSeparator()
        mainToolbar.addAction(showTypesAction)
        
        searchWidget = QWidget()
        hbox = QHBoxLayout(searchWidget)
        spacerItem = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding)
        hbox.addItem(spacerItem)
        
        self.search = QLineEdit("")
        shortcut = QShortcut(QKeySequence("Ctrl+K"), self.search);
        shortcut.activated.connect(self.focusOnSearchField)
        
        
        self.search.returnPressed.connect(self.runSearch)
        self.search.setMaximumWidth(150)
        hbox.addWidget(self.search)
        
        searchButton = QToolButton()
        searchButton.setToolTip(i18n("Search"))
        searchButton.setIcon(KIcon("system-search"))
        searchButton.setPopupMode(QToolButton.InstantPopup)
        searchMenu = QMenu(self)
        searchMenu.setTitle(i18n("Search"))
        self.fullTextSearchOption = self.createAction(i18n("Full-text search"), checkable=True)
        self.fullTextSearchOption.setChecked(True)
        searchMenu.addAction(self.fullTextSearchOption)
        searchButton.setMenu(searchMenu)

        mainToolbar.addWidget(searchWidget)
        mainToolbar.addWidget(searchButton)
        
    def focusOnSearchField(self):
        self.search.setFocus(Qt.OtherFocusReason)
        self.search.selectAll()

    # source: http://www.qtrac.eu/pyqtbook.html
    def createAction(self, text, slot=None, shortcut=None, icon=None, tip=None, key=None,
                        iconSize=16, checkable=False, signal="triggered()"):
        
        
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(KIcon(icon))
                
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)

        if checkable:
            action.setCheckable(True)
        
        if key:
            action.setProperty("nepomukType", QVariant(key))
        if text:
            action.setProperty("label", text)
        
        return action

    def closeCurrentTab(self):
        
    
        """
        Remove the current tab
        """
        index = self.workarea.currentIndex()
        # delete URL history
        try:
            del self.history[index]
            del self.future[index]
        except:
            pass

        self.closeCurrentQuery()
        
        self.workarea.removeTab(index)
        if index == 0:
            pass
#            self.history[self.workarea.currentIndex()] = [unicode(self.currentEditor.ui.url.text())]
#            self.future[self.workarea.currentIndex()] = []
#            self.tab.ui.back.setEnabled(False)
#            self.tab.ui.next.setEnabled(False)

    def newTab(self):
        
        
        
        """
        Create a new tab
        """
        self.addTab(QWidget(), "   ", True, False)
        
        #self.history[self.workarea.currentIndex()] = [unicode(self.currentEditor.ui.url.text())]
        #self.future[self.workarea.currentIndex()] = []
        #		self.currentEditor.ui.back.setEnabled(False)
        #		self.currentEditor.ui.next.setEnabled(False)


    def newTask(self, superTaskUri=None):

        superTask = None
        if superTaskUri:
            superTask = Nepomuk.Resource(superTaskUri)
            
        newTaskEditor = TaskEditor(resource=None, superTask=superTask, mainWindow=self, nepomukType=PIMO.Task)
        self.addTab(newTaskEditor, i18n("New Task"), True, False)
        return newTaskEditor


    def newType(self, superClassUri=Soprano.Vocabulary.RDFS.Resource()):

        newEditor = ClassEditor(resource=None, superClassUri=superClassUri, mainWindow=self)
        self.addTab(newEditor, i18n("New Type"), True, False)
        newEditor.focus()
        return newEditor


    def newProperty(self, domainUri=PIMO.Thing):

        newEditor = PropertyEditor(resource=None, domainUri=domainUri, mainWindow=self)
        self.addTab(newEditor, i18n("New Property"), True, False)
        newEditor.focus()
        return newEditor


    def createResource(self, label, ntype):
        resource = datamanager.createResource(label, ntype)
        #self.emit(SIGNAL('resourceCreated'), resource)
        return resource

    def createSubTask(self, uri):
        resource = datamanager.createResource("", PIMO.Task)
        #parentTask = Nepomuk.Resource(uri)
        resource.setProperty(TMO.superTask, Nepomuk.Variant(uri))
        #self.emit(SIGNAL('resourceCreated'), resource)
        return resource
    
    
        
    def newResourceSlot(self):
        action = self.sender()
        nepomukType = action.property("nepomukType")
        
        if nepomukType is None:
            return
        
        else:
            #nepoomukType is a variant at this stage
            nepomukType = QUrl(nepomukType.toString())

        self.newResource(nepomukType)

    def newResource(self, classUri):
        newEditor = None 
        if classUri == PIMO.Task:
            newEditor = self.newTask(None)
        else:
            
            resource = Nepomuk.Resource(classUri.toString())
            #todo: add a property for associating an editor to a nepomukType dynamically
            label = unicode(resource.genericLabel()) + "Editor"
            if resource.genericLabel() == "file":
                label = "FileEditor"
            elif label == "PersonContactEditor":
                label = "ContactEditor"

            className = "ginkgo.editors." + label.lower() + "." + label
            
            try:
                newEditor = getClass(className)(mainWindow=self, resource=None, nepomukType=classUri)
            except ImportError:
                newEditor = ResourceEditor(mainWindow=self, resource=None, nepomukType=classUri)
                
            self.addTab(newEditor, i18n("New %1", unicode(resource.genericLabel())), True, False)
         
        if newEditor:   
            newEditor.focus()        

    def openResource(self, uri=False, newTab=False, inBackground=True):
        self.workarea.setCursor(Qt.WaitCursor)
        resource = Nepomuk.Resource(uri)
        if not resource.exists():
            self.workarea.unsetCursor()
            return
        
        editor = self.findResourceEditor(resource)
        
        if editor:
            self.workarea.setCurrentWidget(editor)
        else:
            #TODO: add a property for associating an editor to a nepomukType dynamically
            newEditor = None
            for type in resource.types():
                if type != Soprano.Vocabulary.RDFS.Resource() and newEditor is None:
                    typeResource = Nepomuk.Resource(type.toString())
                    label = unicode(typeResource.genericLabel()) + "Editor"
                    if label == "fileEditor":
                        label = "FileEditor"
                    elif label == "PersonContactEditor":
                        label = "ContactEditor"
                    
                    className = "ginkgo.editors." + label.lower() + "." + label

                    try:
                        newEditor = getClass(className)(mainWindow=self, resource=resource, nepomukType=type)
                    except ImportError:
                        newEditor = ResourceEditor(mainWindow=self, resource=resource, nepomukType=type)
    
    
            if newEditor is None:
                newEditor = ResourceEditor(mainWindow=self, resource=resource, nepomukType=Soprano.Vocabulary.RDFS.Resource())
            
            label = resource.genericLabel()
            if label and len(label) > self.maxTabTitleLength():
                label = label[:self.maxTabTitleLength()] + "..."
            self.addTab(newEditor, label, newTab, inBackground)
        
        self.workarea.unsetCursor()
    
    def openResourceExternally(self, uri, isLocal=True):
        """Launches a file or opens a Web page."""
        resource = Nepomuk.Resource(uri)
        url = resource.property(NIE.url)
        if url and len(url.toString()) > 0:
            kurl = KUrl(url.toString())
            krun(kurl, self, isLocal)
        elif resource.resourceUri() and len(resource.resourceUri().toString()) > 0:
            kurl = KUrl(resource.resourceUri().toString())
            krun(kurl, self, isLocal)
            
    
    def writeEmail(self, uris):
        mailto = ""
        for uri in uris:
            res = Nepomuk.Resource(uri)
            emailAddress = res.property(NCO.emailAddress)
            if emailAddress and len(emailAddress.toString()) > 0:
                emailAddress = emailAddress.toString()
                #don't add twice the same address
                if mailto.find(emailAddress + ",") == -1:
                    mailto = mailto + unicode(emailAddress) + ","
            else:
                warning = QMessageBox(QMessageBox.Warning, i18n("Warning"), "No e-mail address was found for %s." % res.genericLabel(), QMessageBox.NoButton, self)
                warning.addButton("&Continue", QMessageBox.AcceptRole)
                warning.exec_()

        if len(mailto) > 1:
            krun("mailto:%s" % mailto, self, False)

    def findResourceEditor(self, resource):
        """Finds an editor where the resource is being edited. If no editor is found, returns None."""
        for index in range(self.workarea.count()):
            editor = self.workarea.widget(index)
            if hasattr(editor, "resource") and editor.resource and editor.resource.resourceUri() == resource.resourceUri():
                return editor
        return None

    def addTab(self, editor, label, newTab=False, inBackground=True):
        if newTab:
            index = self.workarea.addTab(editor, label)
            #tab in foreground
            if not inBackground:
                self.workarea.setCurrentIndex(index)
        else:
            self.replaceCurrentTab(editor, label)

        
    def removeResource(self, uri):
        
        resource = Nepomuk.Resource(uri)
        reply = QMessageBox.question(self, i18n("Resource removal"),
                i18n("Are you sure you want to delete <i>%1</i>?", resource.genericLabel()),
                QMessageBox.Yes | QMessageBox.Cancel)
        if reply == QMessageBox.Yes:
            self.workarea.setCursor(Qt.WaitCursor)
            datamanager.removeResource(uri)
    
            #TODO: check
            if resource:
                editor = self.findResourceEditor(resource)
                if editor:
                    for index in range(0, self.workarea.count()):
                        if editor == self.workarea.widget(index):
                            self.workarea.removeTab(index)
            self.workarea.unsetCursor()
            
        elif reply == QMessageBox.No:
            pass
        else:
            pass
        
        
        
        
    def showOpenResourcesDialog(self):
        dialog = LiveSearchDialog(mainWindow=self)
        if dialog.exec_():
            if dialog.selectedResources():
                for resource in dialog.selectedResources():
                    self.openResource(resource.resourceUri(), True, False)

    def currentTabChangedSlot(self, index):
        resource = self.currentResource()
        if resource:
            flag = True
        else:
            flag = False
            
        self.linkToButton.setEnabled(flag)
        self.linkToMenu.setEnabled(flag)
        self.setContextAction.setEnabled(flag)
        self.deleteAction.setEnabled(flag)
            
        currentWorkWidget = self.workarea.currentWidget()
        #test on save, not on resource since the resource can be new
        if (hasattr(currentWorkWidget, "save")):
            self.saveAction.setEnabled(True)
        else:
            self.saveAction.setEnabled(False)

        if (hasattr(currentWorkWidget, "_query")):
            if currentWorkWidget.query() != None:
                self.stopQueryAction.setEnabled(True)
            else:
                self.stopQueryAction.setEnabled(False)
        else:
            self.stopQueryAction.setEnabled(False)



        

    def linkTo(self):
        widget = self.workarea.currentWidget()
        
        #if the resource was just created and not yet saved, save it before creating the link,
        #so that it exists
        if hasattr(widget, "resource") and not widget.resource:
            self.save()

        
        if hasattr(widget, "resource") and widget.resource:
            #exclude items already linked to current resource
            #excludeList = datamanager.findRelateds(widget.resource.resourceUri())
            #exclude the current resource itself for avoiding creating a link to itself
            #excludeList.add(widget.resource)
            self.setCursor(Qt.WaitCursor)
            dialog = LiveSearchDialog(mainWindow=self, resource=widget.resource, title=i18n("New Relation"))
            self.unsetCursor()
            if dialog.exec_():
                #save the current resource to make sure it exists in the db, then draw the relations
                self.setCursor(Qt.WaitCursor)
                widget.save()
                
                for resource in dialog.selectedResources():
                    #Soprano.Vocabulary.NAO.isRelated()
                    widget.resource.addProperty(dialog.selectedPredicate(), Nepomuk.Variant(resource))
                
                self.unsetCursor()
                
    def linkToFile(self):
        path = QFileInfo(".").path()
        fname = QFileDialog.getOpenFileName(self, i18n("Select File - Ginkgo"), path, "*")
        
        if not fname.isEmpty():
            widget = self.workarea.currentWidget()
            widget.save()
            #check if any file exists with the given path
            
            #print type(fname)
            fname = unicode(fname)
            file = datamanager.getFileResource(fname)
            widget.save()
            widget.resource.addProperty(Soprano.Vocabulary.NAO.isRelated(), Nepomuk.Variant(file))
            

    def currentResource(self):
        widget = self.workarea.currentWidget()
        if widget and hasattr(widget, "resource"):
            return widget.resource
        else:
            return None

    def currentWorkWidget(self):
        return self.workarea.currentWidget()
       
    def removeRelation(self, subject, predicate, object):
        self.workarea.setCursor(Qt.WaitCursor)
        subject.removeProperty(predicate.uri(), Nepomuk.Variant(object.resourceUri()))
        self.workarea.unsetCursor()
        
    def closeEvent(self, event):
        try:
            self.saveSettings()
        except Exception, e:
            print "[Ginkgo] An error occurred while saving the preferences: '%s.'" % str(e)
            
            
    def createPlacesWidget(self):
        self.placesWidget = QDockWidget(i18n("Places"), self)
        self.placesWidget.setObjectName("Places")
        self.placesWidget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        self.installPlaces()
        
        self.addDockWidget(Qt.LeftDockWidgetArea, self.placesWidget)


    def loadPlacesData(self):
        """Try to restore the places from the settings, otherwise set default places."""    
        
        try:
        
            config = KConfig("ginkgo")
            ggroup = KConfigGroup(config, "places")
            
                    
            placesTypes = ggroup.readEntry("types", QStringList()).toStringList()
            
            
            if placesTypes and len(placesTypes) > 0:
                self.placesData = []
                for type in placesTypes:
                    self.placesData.append([QUrl(type)])
                
                placesLabels = ggroup.readEntry("labels", QStringList()).toStringList()
                placesLabelsPlural = ggroup.readEntry("labels-plural", QStringList()).toStringList()
                placesIcons = ggroup.readEntry("icons", QStringList()).toStringList()
                placesTips = ggroup.readEntry("tips", QStringList()).toStringList()
                
                for index in range(0, len(self.placesData)):
                    
                    self.placesData[index].append(placesLabels[index])
                    self.placesData[index].append(placesLabelsPlural[index])
                    self.placesData[index].append(placesIcons[index])
                    self.placesData[index].append(placesTips[index])
                return
        except Exception, e:
            print "[Ginkgo] An error occurred while restoring the places: %s. " % str(e)
            #traceback.print_exc(file=sys.stdout)
        
        self.placesData = [
                         [NCO.PersonContact, i18n("&Contact"), i18n("&Contacts"), "contact-new", i18n("Create new contact")],
                         [PIMO.Project, i18n("&Project"), i18n("&Projects"), "nepomuk", i18n("Create new project")],
                         [PIMO.Task, i18n("&Task"), i18n("&Tasks"), "view-task-add", i18n("Create new task")],
                         [PIMO.Organization, i18n("&Organization"), i18n("&Organizations"), "nepomuk", i18n("Create new organization")],
                         [PIMO.Topic, i18n("&Topic"), i18n("&Topics"), "nepomuk", i18n("Create new topic")],
                         [PIMO.Event, i18n("&Event"), i18n("&Events"), "nepomuk", i18n("Create new event")],
                         [PIMO.Location, i18n("&Location"), i18n("&Locations"), "nepomuk", i18n("Create new location")],
                         [NFO.Website, i18n("&WebPage"), i18n("&Web Pages"), "text-html", i18n("Create new Web page")],
                         [PIMO.Note, i18n("&Note"), i18n("&Notes"), "text-plain", i18n("Create new note")],
                         [NFO.FileDataObject, i18n("&File"), i18n("&Files"), "text-plain", i18n("Create new file")]
                         ]
#        else:
#            self.placesData =  placesData
    #viewMenu.addAction(self.createAction("Files", self.showResourcesByType, None, None, None, NFO.FileDataObject))
    
    def createPlaceButton(self, parent, nepomukType, label):
        button = KPushButton(parent)
        button.setStyleSheet("text-align:left")
        button.setObjectName(label)
        button.setText(label)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        button.setProperty("nepomukType", nepomukType)
        button.setProperty("label", label)
        button.clicked.connect(self.showResourcesByType)
        button.setContextMenuPolicy(Qt.CustomContextMenu)
        button.customContextMenuRequested.connect(self.showPlacesContextMenu)
        return button
    
    def installPlaces(self):
        placesInternalWidget = QWidget()
        placesInternalWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        verticalLayout = QVBoxLayout(placesInternalWidget)
        verticalLayout.setObjectName("placeslayout")
        
        for type in self.placesData:
            button = self.createPlaceButton(placesInternalWidget, type[0], type[2])
            verticalLayout.addWidget(button)
        
#        button = self.createPlaceButton(placesInternalWidget, NFO. Object, "Files")
#        verticalLayout.addWidget(button)
        
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        verticalLayout.addItem(spacerItem)
        
        self.placesWidget.setWidget(placesInternalWidget)

    def addToPlaces(self, uri):
        resource = Nepomuk.Resource(uri)
        #button = self.createPlaceButton(uri.toString(), resource.genericLabel() + "s")
        newPlaceData = [uri, i18n(resource.genericLabel()), i18n(resource.genericLabel()), "nepomuk", None]
        self.placesData.append(newPlaceData)
        self.installPlaces()
        
    def removeFromPlaces(self, nepomukType):
        index = 0
        for placeData in self.placesData:
            if placeData and placeData[0] == nepomukType:
                self.placesData.pop(index)
                break
            index = index + 1
        self.installPlaces()
    
    def movePlaceUp(self, nepomukType):
        index = 0
        for placeData in self.placesData:
            if placeData and placeData[0] == nepomukType:
                self.placesData.pop(index)
                self.placesData.insert(index - 1, placeData)
                break
            index = index + 1
        self.installPlaces()
        
    def movePlaceDown(self, nepomukType):
        index = 0
        for placeData in self.placesData:
            if placeData and placeData[0] == nepomukType:
                self.placesData.pop(index)
                self.placesData.insert(index + 1, placeData)
                break
            index = index + 1
        self.installPlaces()
        
        
    def showPlacesContextMenu(self, points):
        button = self.sender()
        nepomukType = button.property("nepomukType")
        menu = PlacesContextMenu(self, nepomukType=nepomukType)
        pos = button.mapToGlobal(points)
        menu.exec_(pos)
         
    
    def showResourcesByType(self):
        nepomukType = QUrl(self.sender().property("nepomukType").toString())
        label = self.sender().property("label").toString()
        if nepomukType == PIMO.Task:
            currentEditor = TaskTree(mainWindow=self, makeActions=True)
            self.replaceCurrentTab(currentEditor, label)
        
        else:
            currentEditor = ResourcesByTypeTable(mainWindow=self, nepomukType=nepomukType)
            self.replaceCurrentTab(currentEditor, label)

        
    def setCurrentResourceAsContext(self):
        resource = self.currentResource()
        self.setResourceAsContext(resource)
        
    def setResourceAsContext(self, resource):
        sbus = dbus.SessionBus()
        self.dobject = sbus.get_object("org.kde.nepomuk.services.nepomukusercontextservice", '/nepomukusercontextservice')
        
        if resource:
            self.dobject.setCurrentUserContext(str(resource.resourceUri().toString()))
            if self.dobject.currentUserContext() == str(resource.resourceUri().toString()):
                reply = QMessageBox.information(self, i18n("Context - Ginkgo"), i18n("The context has been succesfully updated to <i>%1</i>.", resource.genericLabel()))
            else:
                reply = QMessageBox.information(self, i18n("Context - Ginkgo"), i18n("An error occurred while updating the context."))
        #self.iface = dbus.Interface(self.dobject, "org.kde.nepomuk.Strigi")

    def saveSettings(self):
        config = KConfig("ginkgo")
        ggroup = KConfigGroup(config, "general")
        ggroup.writeEntry("size", QVariant(self.size()))

        ggroup.writeEntry("position", QVariant(self.pos()))
        
        currentEditor = self.workarea.currentWidget()
        
        if currentEditor and hasattr(currentEditor, "ui"):
            try:
                ggroup.writeEntry("description-splitter-state", QVariant(currentEditor.ui.rightpane.saveState()))
            except Exception, e:
                pass
        
        
        ggroup.writeEntry("state", QVariant(self.saveState()))
        currentResourcesUris = QStringList()
        for i in range(self.workarea.count()):
            editor = self.workarea.widget(i)
            if hasattr(editor, "resource") and editor.resource:
                currentResourcesUris.append(editor.resource.resourceUri().toString())
        ggroup.writeEntry("active-resources", QVariant(currentResourcesUris))
        
        
        ggroup = KConfigGroup(config, "places")
        self.savePlacesSettings(ggroup, 0, "types")
        self.savePlacesSettings(ggroup, 1, "labels")
        self.savePlacesSettings(ggroup, 2, "labels-plural")
        self.savePlacesSettings(ggroup, 3, "icons")
        self.savePlacesSettings(ggroup, 4, "tips")

        config.sync()
        
    def savePlacesSettings(self, ggroup, index, label):
        places = QStringList()
        for place in self.placesData:
            #place[0] is of type QUrl
            if index == 0:
                places.append(unicode(place[index].toString()))
            else:
                places.append(unicode(place[index]))
        ggroup.writeEntry(label, QVariant(places))
        
       
    def restoreSettings(self): 
        try: 
            config = KConfig("ginkgo")
            ggroup = KConfigGroup(config, "general")
            size = ggroup.readEntry("size", QSize(800, 500)).toSize()
            self.resize(size)
            
            position = ggroup.readEntry("position", QPoint(200, 100)).toPoint()
            self.move(position)
            self.restoreState(ggroup.readEntry("state", QByteArray()).toByteArray())
            
            self.descriptionSplitterState = ggroup.readEntry("description-splitter-state", QByteArray()).toByteArray()
            

            resourcesUris = ggroup.readEntry("active-resources", QStringList()).toStringList()
            for uri in resourcesUris:
                self.openResource(uri, True, True)
        except Exception, e:
            print "[Ginkgo] An error occurred while restoring the settings: '%s'." % str(e)
            
        

    def save(self):
        
        currentEditor = self.workarea.currentWidget()
        if (hasattr(currentEditor, "save")):
            self.setCursor(Qt.WaitCursor)
            index = self.workarea.currentIndex()
            currentEditor.save()
            if self.currentResource():
                label = currentEditor.resource.genericLabel()
                if label and len(label) > self.maxTabTitleLength():
                    label = label[:self.maxTabTitleLength()] + "..."
                self.workarea.setTabText(index, label)
                self.currentTabChangedSlot(index)
            self.unsetCursor()

    def delete(self):
        resource = self.currentResource()
        if resource:
            self.removeResource(resource.uri())


    def showTypes(self):
        self.setCursor(Qt.WaitCursor)
        currentEditor = TypesView(mainWindow=self)
        self.replaceCurrentTab(currentEditor, "Types")
        self.unsetCursor()
        
    def showRecentlyModifiedResources(self):
        recentlyModifiedResourcesView = ResourcesTable(mainWindow=self, sortColumn= -1)
        datamanager.listResourcesOrderedByDate(recentlyModifiedResourcesView.model.queryNextReadySlot, recentlyModifiedResourcesView.queryFinishedSlot, recentlyModifiedResourcesView)
        self.replaceCurrentTab(recentlyModifiedResourcesView, i18n("What's New"))


    def runSearch(self):
        #str() for converting a QString to str
        term = unicode(self.search.text())
        searchView = ResourcesTable(mainWindow=self)
        
        if self.fullTextSearchOption.isChecked():
            datamanager.fullTextSearch(term, searchView.model.queryNextReadySlot, searchView.queryFinishedSlot, searchView)
        else:
            datamanager.findResourcesByLabel(term, searchView.model.queryNextReadySlot, searchView.queryFinishedSlot, searchView)
            
        
        self.replaceCurrentTab(searchView, i18n("Search Results"))

    def replaceCurrentTab(self, widget, label):
        index = self.workarea.currentIndex()

        self.closeCurrentQuery()
        
        self.workarea.removeTab(index)
        self.workarea.insertTab(index, widget, label)
        self.workarea.setCurrentIndex(index) 
        


    def closeCurrentQuery(self):
        """
        Makes sure the query used by the current tab view is closed and that its signals get disconnected 
        before destroying the view.
        """
        
        if hasattr(self.workarea.currentWidget(), "_query"):
            query = self.workarea.currentWidget().query()
            #query is set to None by the controller when the query has finished
            if query != None:
                query.nextReady.disconnect()
                query.finished.disconnect()
                query.close()
                #for making sure a second call to closeCurrentQuery won't crash the app
                self.workarea.currentWidget().setQuery(None)
                self.stopQueryAction.setEnabled(False)

    
    def typeIcon(self, nepomukType, size=16):
        if nepomukType == NFO.Website:
            return KIcon("text-html")
        elif nepomukType == PIMO.Task:
            return KIcon("view-task")
        elif nepomukType == NCO.PersonContact:
            if size == 16:
                return KIcon("x-office-contact")
            else:
                return QIcon("/usr/share/icons/oxygen/48x48/mimetypes/x-office-contact.png")
        elif nepomukType == PIMO.Note:
            return KIcon("text-plain")
        elif nepomukType ==Soprano.Vocabulary.RDF.Property():
            return KIcon("code-function")
        else:
            return KIcon("nepomuk")

    #TODO: for table icons, for which KIcon won't work..
    def typeQIcon(self, nepomukType, size=16):
        if nepomukType == NFO.Website:
            return QIcon("/usr/share/icons/oxygen/16x16/mimetypes/text-html.png")
        elif nepomukType == PIMO.Task:
            return QIcon("/usr/share/icons/oxygen/16x16/actions/view-task.png")
        elif nepomukType == NCO.PersonContact:
            return QIcon("/usr/share/icons/oxygen/16x16/mimetypes/x-office-contact.png")
        elif nepomukType == PIMO.Note:
            return QIcon("/usr/share/icons/oxygen/16x16/mimetypes/text-plain.png")
        
        elif nepomukType ==Soprano.Vocabulary.RDF.Property():
            return QIcon("/usr/share/icons/oxygen/16x16/actions/code-function.png")
        else:
            return QIcon(":/nepomuk-small")

        
    #TODO: for table icons, for which KIcon won't work..
    def resourceQIcon(self, resource):
        types = resource.types()
        #custom type instances raise an issue with the call to genericIcon which crashes the application
        #TODO: fix bug in libnepomuk with Nepomuk.Resource.genericIcon()
#        for type in types:
#            if str(type.toString()).find("nepomuk:/") == 0:
#                return QIcon(":/nepomuk-small")
        
        iconPath = resource.genericIcon()
        if iconPath and len(iconPath) > 0 and os.path.exists(iconPath):
            return QIcon(iconPath)
        elif NCO.PersonContact in types:
            return QIcon("/usr/share/icons/oxygen/16x16/mimetypes/x-office-contact.png")
        elif PIMO.Task in types:
            return QIcon("/usr/share/icons/oxygen/16x16/actions/view-task.png")
        elif NFO.Website in types:
            return QIcon("/usr/share/icons/oxygen/16x16/mimetypes/text-html.png")
        elif NFO.FileDataObject in types:
            try:
                path = str(resource.property(NIE.url).toString())
                mimetype = mimetypes.guess_type(path)
                elt = mimetype[0]
                if elt.find("image/") == 0:
                    return QIcon("/usr/share/icons/oxygen/16x16/mimetypes/image-x-generic.png")
                if elt:
                    elt = elt.replace("/", "-")
                    return QIcon("/usr/share/icons/oxygen/16x16/mimetypes/%s.png" % elt)
            except Exception, e:
                #TODO: log error, fix error
                return QIcon(":/nepomuk-small")
        elif PIMO.Note in types:
            return QIcon("/usr/share/icons/oxygen/16x16/mimetypes/text-plain.png")
        elif Soprano.Vocabulary.RDF.Property() in types:
            return QIcon("/usr/share/icons/oxygen/16x16/actions/code-function.png")        
        else:
            return QIcon(":/nepomuk-small")
    
    def resourceIcon(self, resource, size=16):
        types = resource.types()
        if size == 16:
            if NCO.PersonContact in types:
                return KIcon("x-office-contact")
            elif PIMO.Task in types:
                return KIcon("view-task")
            elif NFO.Website in types:
                return KIcon("text-html")
            elif NFO.FileDataObject in types:
                mimetype = mimetypes.guess_type(str(resource.property(NIE.url).toString()))
                elt = mimetype[0]
                if elt:
                    elt = elt.replace("/", "-")
                    return KIcon(elt)
                return KIcon("nepomuk")
            elif PIMO.Note in types:
                return KIcon("text-plain")
            elif Soprano.Vocabulary.RDF.Property() in types:
                return KIcon("code-function")
            else:
                return KIcon("nepomuk")
        else:
            #custom type instances raise an issue with the call to genericIcon which crashes the application
            #TODO: fix bug in libnepomuk with Nepomuk.Resource.genericIcon()

            for type in types:
                if str(type.toString()).find("nepomuk:/") == 0:
                    return KIcon("nepomuk")
            
            iconPath = resource.genericIcon()
            if iconPath and len(iconPath) > 0 and os.path.exists(iconPath):
                return QIcon(iconPath)
            elif PIMO.Task in types:
                return KIcon("view-task")
            elif NCO.PersonContact in types:
                #TODO: replace with KIcon, but with proper size
                return QIcon("/usr/share/icons/oxygen/48x48/mimetypes/x-office-contact.png")
            
            elif NFO.FileDataObject in types:
                mimetype = mimetypes.guess_type(unicode(resource.property(NIE.url).toString()))
                elt = mimetype[0]
                if elt:
                    elt = elt.replace("/", "-")
                    #icon = "/usr/share/icons/oxygen/48x48/mimetypes/"+elt+".png"
                    #if os.path.exists(icon):
                    return KIcon(elt)
                return KIcon("nepomuk")
            elif Soprano.Vocabulary.RDF.Property() in types:
                return KIcon("code-function")
            else:
                return KIcon("nepomuk")



    def maxTabTitleLength(self):
        return 30




    def processAction(self, key, nepomukType):
        if key == MOVE_PLACE_UP:
            self.movePlaceUp(nepomukType)
        elif key == MOVE_PLACE_DOWN:
            self.movePlaceDown(nepomukType)
        elif key == REMOVE_PLACE_ENTRY:
            self.removeFromPlaces(nepomukType)
        


class PlacesContextMenu(QMenu):
    def __init__(self, parent=None, nepomukType=None):
        super(PlacesContextMenu, self).__init__(parent)
        self.nepomukType = nepomukType
        self.parent = parent
        self.createActions()
        self.triggered.connect(self.actionTriggered)
        QMetaObject.connectSlotsByName(self)
    
    def actionTriggered(self, action):
        key = action.property("key").toString()
        self.parent.processAction(key, self.nepomukType)
        
    def createActions(self):
        action = QAction(i18n("Move &up"), self)
        action.setProperty("key", QVariant(MOVE_PLACE_UP))
        self.addAction(action)
        action = QAction(i18n("Move &down"), self)
        action.setProperty("key", QVariant(MOVE_PLACE_DOWN))
        self.addAction(action)
        action = QAction(i18n("&Remove entry"), self)
        action.setProperty("key", QVariant(REMOVE_PLACE_ENTRY))
        self.addAction(action)



#http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname
def getClass(clazz):
    parts = clazz.split('.')
    module = ".".join(parts[:-1])
    module = __import__(module)
    for comp in parts[1:]:
        module = getattr(module, comp)            
    return module
