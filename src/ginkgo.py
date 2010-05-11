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


import mimetypes
import os
import sys
from PyKDE4.nepomuk import Nepomuk
from PyKDE4.soprano import Soprano
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from dao import PIMO, TMO, NFO, NCO, datamanager, NIE
from dialogs.resourcechooserdialog import ResourceChooserDialog
from editors.resourceeditor import ResourceEditor
from editors.resourcesbytypetable import ResourcesByTypeTable
from editors.taskeditor import TaskEditor
from editors.tasktree import TaskTree
import resources_rc



class Ginkgo(QMainWindow):
    def __init__(self, parent=None):
        super(Ginkgo, self).__init__(parent)

        self.editors = QTabWidget()
        self.setCentralWidget(self.editors)
        
        mainTypes = [
                     [NCO.Contact, "&Contact", "&Contact", "actions/contact-new.png", "Create new contact"],
                     [PIMO.Task, "&Task", "&Task", "actions/view-task-add.png", "Create new task"],
                     [PIMO.Project, "&Project", "&Project", "apps/nepomuk.png", "Create new project"],
                     [PIMO.Organization, "&Organization", "&Organization", "apps/nepomuk.png", "Create new organization"],
                     [PIMO.Location, "&Location", "&Location", "apps/nepomuk.png", "Create new location"],
                     [PIMO.Event, "&Event", "&Event", "apps/nepomuk.png", "Create new event"],
                     [PIMO.Topic, "&Topic", "&Topic", "apps/nepomuk.png", "Create new topic"],
                     [NFO.Website, "&WebPage", "&Web Page", "mimetypes/text-html.png", "Create new Web page"]
                     ]
                
        
        placesWidget = self.createPlacesWidget(mainTypes)
        self.createActions(mainTypes)

        
        self.addDockWidget(Qt.LeftDockWidgetArea, placesWidget)


        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.showMessage("Ready", 5000)

        
        self.applySettings()
        self.setWindowTitle("Ginkgo")

#        url = KUrl(QString("file:///home/arkub/F/ASU.INRIA.Valudriez.Lamarre.200902.pdf"))
#        url = KUrl(QString("http://www.google.com"))
#        run = KRun(url, self, 1, False)
#        print run


    def createActions(self, mainTypes):

        newResourceActions = []

        for type in mainTypes:
            newResourceActions.append(self.createAction(type[1], getattr(self, "newResource"), None, type[3], type[4], type[0]))
        
        saveAction = self.createAction("&Save", self.save, QKeySequence.Save, "document-save", "Save")
        
        
        openResourceAction = self.createAction("&Open", self.showOpenResourceDialog, QKeySequence.Open, "open", "Open a resource")
        newTabAction = self.createAction("New &Tab", self.newTab, QKeySequence.AddTab, "tab-new-background-small", "Create new tab")
        closeTabAction = self.createAction("Close Tab", self.closeCurrentTab, QKeySequence.Close, "tab-close", "Close tab")
        quitAction = self.createAction("&Quit", self.close, "Ctrl+Q", "quit", "Close the application")


        linkToButton = QToolButton()
        linkToButton.setToolTip("Link to...")
        linkToButton.setStatusTip("Link to...")
        #linkToButton.setIcon(QIcon(":/nepomuk-small"))
        linkToButton.setIcon(self.kdeIcon("apps/nepomuk.png", 16))
        linkToButton.setPopupMode(QToolButton.InstantPopup)
        #linkToButton.setEnabled(False)
        self.linkToMenu = QMenu(self)
        self.linkToMenu.setTitle("Link to")
        self.linkToMenu.setIcon(QIcon(":/nepomuk-small"))
        for type in mainTypes:
            self.linkToMenu.addAction(self.createAction(type[1], self.linkTo, None, type[3], None, type[0]))
        
        self.linkToMenu.addAction(self.createAction("File", self.linkToFile, None, None, "Link to file"))
        linkToButton.setMenu(self.linkToMenu)

        mainMenu = self.menuBar().addMenu("&File")
        newResourceMenu = QMenu(mainMenu)
        newResourceMenu.setObjectName("menuNewResource")
        newResourceMenu.setTitle("&New")
        
        for action in newResourceActions:
            newResourceMenu.addAction(action)
        
        mainMenu.addAction(newResourceMenu.menuAction())
        mainMenu.addAction(openResourceAction)
        mainMenu.addSeparator()
        mainMenu.addAction(saveAction)
        mainMenu.addSeparator()
        mainMenu.addAction(newTabAction)
        mainMenu.addAction(closeTabAction)
        mainMenu.addAction(quitAction)
        
        
        viewMenu = self.menuBar().addMenu("&View")
        for type in mainTypes:
            viewMenu.addAction(self.createAction(type[1]+"s", self.showResourcesByType, None, type[3], None, type[0]))
        
        viewMenu.addAction(self.createAction("Files", self.showResourcesByType, None, None, None, NFO.FileDataObject))
        
        mainToolbar = self.addToolBar("Toolbar")
        mainToolbar.setIconSize(QSize(18, 18))
        #mainToolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        mainToolbar.setObjectName("MainToolBar")
        
        newResourceButton = QToolButton()
        newResourceButton.setToolTip("New")
        newResourceButton.setStatusTip("New")
        #linkToButton.setIcon(QIcon(":/nepomuk-small"))
        newResourceButton.setIcon(self.kdeIcon("actions/document-new.png", 16))
        newResourceButton.setPopupMode(QToolButton.InstantPopup)
        newResourceButton.setMenu(newResourceMenu)

        
        mainToolbar.addWidget(newResourceButton)
        
        
        

        #mainToolbar.addAction(action)
        
        mainToolbar.addAction(saveAction)
        mainToolbar.addAction(newTabAction)
        
        
        mainToolbar.addWidget(linkToButton)
        

    def kdeIcon(self, icon, size):
        path = "/usr/share/icons/oxygen/%dx%d/%s"% (size, size, icon)
        if os.path.exists(path):
            return QIcon(path)
        return QIcon()
        
    # source: http://www.qtrac.eu/pyqtbook.html
    def createAction(self, text, slot=None, shortcut=None, icon=None, tip=None, key=None, 
                        iconSize=16, checkable=False, signal="triggered()"):
        
        
        action = QAction(text, self)
        if icon is not None:
            if icon.find(".png") < 0:
                action.setIcon(QIcon(":/%s" % icon))
            else:
                action.setIcon(self.kdeIcon(icon, iconSize))
                
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        
        action.setProperty("nepomukType", QVariant(key))
        action.setProperty("label", text)
        
        return action

    def about(self):
        """
        Show app info
        """
        message = QMessageBox(self)
        message.setTextFormat(Qt.RichText)
        message.setText(u'<b>Ginkgo 0.1</b><br><b>License</b>: LGPL')
        message.setWindowTitle('Ginkgo 0.1')
        message.setIcon(QMessageBox.Information)
        message.addButton('Ok', QMessageBox.AcceptRole)
        #message.setDetailedText('Unsaved changes in: ' + self.ui.url.text())
        message.exec_()


    def closeCurrentTab(self):
        """
        Remove the current tab
        """
        index = self.editors.currentIndex()
        # delete URL history
        try:
            del self.history[index]
            del self.future[index]
        except:
            pass
        self.editors.removeTab(index)
        if index == 0:
            pass
#            self.history[self.editors.currentIndex()] = [unicode(self.currentEditor.ui.url.text())]
#            self.future[self.editors.currentIndex()] = []
#            self.tab.ui.back.setEnabled(False)
#            self.tab.ui.next.setEnabled(False)

    def newTab(self):
        """
        Create a new tab
        """
        self.addTab(QWidget(), "Ginkgo", True, False)
        
        #self.history[self.editors.currentIndex()] = [unicode(self.currentEditor.ui.url.text())]
        #self.future[self.editors.currentIndex()] = []
        #		self.currentEditor.ui.back.setEnabled(False)
        #		self.currentEditor.ui.next.setEnabled(False)


    def newTask(self, superTaskUri=None):
        #dialog = EditPersonDialog(None, self)
        
        #person = Nepomuk.Resource()
        superTask = None
        if superTaskUri:
            superTask = Nepomuk.Resource(superTaskUri)
            
        newTaskEditor = TaskEditor(resource=None, superTask=superTask, mainWindow=self, nepomukType=PIMO.Task)
        self.addTab(newTaskEditor, "New Task", True, False)


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
    
    
        
    def newResource(self):
        action = self.sender()
        nepomukType = action.property("nepomukType")
        
        if nepomukType is None:
            return
        
        else:
            nepomukType = QUrl(nepomukType.toString())

        if nepomukType == PIMO.Task:
            self.newTask(None)
        else:
            
            resource = Nepomuk.Resource(nepomukType.toString())
            #todo: add a property for associating an editor to a nepomukType dynamically
            label = str(resource.genericLabel())+"Editor"
            className = "editors."+label.lower()+"."+label
            try:
                newEditor = getClass(className)(mainWindow=self, resource=None, nepomukType=nepomukType)
            except ImportError:
                newEditor = ResourceEditor(mainWindow=self, resource=None, nepomukType=nepomukType)
                
            self.addTab(newEditor, "New "+str(resource.genericLabel()), True, False)
                

    def openResource(self, uri=False, newTab=False):

        resource = Nepomuk.Resource(uri)
        
        editor = self.findResourceEditor(resource)
        if editor:
            self.editors.setCurrentWidget(editor)
            return

        #TODO: add a property for associating an editor to a nepomukType dynamically
        newEditor = None
        for type in resource.types():
            if type != Soprano.Vocabulary.RDFS.Resource() and newEditor is None:
                typeResource = Nepomuk.Resource(type.toString())
                label = str(typeResource.genericLabel())+"Editor"
                if label == "fileEditor":
                    label = "FileEditor"
                className = "editors."+label.lower()+"."+label
                try:
                    newEditor = getClass(className)(mainWindow=self, resource=resource, nepomukType=type)
                except ImportError:
                    newEditor = ResourceEditor(mainWindow=self, resource=resource, nepomukType=type)


        if newEditor is None:
            newEditor = ResourceEditor(mainWindow=self, resource=resource, nepomukType=Soprano.Vocabulary.RDFS.Resource())
            
        self.addTab(newEditor, resource.genericLabel(), newTab)



    def findResourceEditor(self, resource):
        """Finds an editor where the resource is being edited. If no editor is found, returns None."""
        for index in range(self.editors.count()):
            editor = self.editors.widget(index)
            if hasattr(editor, "resource") and editor.resource and editor.resource.resourceUri() == resource.resourceUri():
                return editor
        return None

    def addTab(self, editor, label, newTab=False, inBackground=True):
        if newTab:
            index = self.editors.addTab(editor, label)
            #tab in foreground
            if not inBackground:
                self.editors.setCurrentIndex(index)
        else:
            index = self.editors.currentIndex()
            self.editors.removeTab(index)
            self.editors.insertTab(index, editor, label)
            self.editors.setCurrentIndex(index)

        
    def removeResource(self, uri):
        datamanager.removeResource(uri)
        self.emit(SIGNAL('resourceRemoved'), uri)
        
    def showOpenResourceDialog(self):
        
        text, ok = QInputDialog.getText(self, 'Open Resource', 'Name:')
        
        if ok:
            resources = datamanager.findResourcesByLabel(text)
            if resources and len(resources) > 0:
                self.openResource(resources[0].resourceUri(), True)


    

    def linkTo(self):
        action = self.sender()
        nepomukType = QUrl(action.property("nepomukType").toString())
        
        widget = self.editors.currentWidget()
        #exclude items already linked to current resource
        if hasattr(widget,"resource") and widget.resource:
            excludeList = datamanager.findRelations(widget.resource.resourceUri())
            #exclude the current resource itself for avoiding creating a link to itself
            excludeList.add(widget.resource)
            dialog = ResourceChooserDialog(self, nepomukType, excludeList)
            if dialog.exec_():
                #save the current resource to make sure it exists in the db, then draw the relations
                widget.save()
                selection = dialog.selection
                for id in selection:
                    item = QUrl(id)
                    widget.resource.addProperty(Soprano.Vocabulary.NAO.isRelated(), Nepomuk.Variant(item))
                
    def linkToFile(self):
        path = QFileInfo(".").path()
        fname = QFileDialog.getOpenFileName(self, "Select File - Ginkgo", path, "*")
        
        if not fname.isEmpty():
            widget = self.editors.currentWidget()
            widget.save()
            #check if any file exists with the given path
            
            #print type(fname)
            fname = str(fname)
            file = datamanager.getFileResource(fname)
            widget.save()
            widget.resource.addProperty(Soprano.Vocabulary.NAO.isRelated(), Nepomuk.Variant(file))
            
        
       
    def unlink(self, predicateUrl, resourceUris, bidirectional=False):
        widget = self.editors.currentWidget()
        resource = widget.resource
        
        if resource and resourceUris and len(resourceUris) > 0:
            for uri in resourceUris:
                target = Nepomuk.Resource(uri)
                resource.removeProperty(predicateUrl, Nepomuk.Variant(target.resourceUri()))
                if bidirectional:
                    target.removeProperty(predicateUrl, Nepomuk.Variant(resource.resourceUri()))
        
        
    def closeEvent(self, event):
        settings = QSettings()
        settings.setValue("Ginkgo/Size", QVariant(self.size()))
        settings.setValue("Ginkgo/Position",
                QVariant(self.pos()))
        settings.setValue("Ginkgo/State",
                QVariant(self.saveState()))
            
    def createPlacesWidget(self, mainTypes):
        placesWidget = QDockWidget("Places", self)
        placesWidget.setObjectName("Places")
        placesWidget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        widget = QWidget()
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        verticalLayout = QVBoxLayout(widget)
        verticalLayout.setObjectName("placeslayout")
        
        for type in mainTypes:
            button = self.createPlaceButton(type[0], type[1]+"s", widget)
            verticalLayout.addWidget(button)
        
        button = self.createPlaceButton(NFO.FileDataObject, "Files", widget)
        verticalLayout.addWidget(button)
        
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        verticalLayout.addItem(spacerItem)
        
        placesWidget.setWidget(widget)
        
        
        return placesWidget
    
    
    
    def createPlaceButton(self, nepomukType, label, widget):
        button = QPushButton(widget)
        button.setObjectName(label)
        button.setText(QApplication.translate("Ginkgo", label, None, QApplication.UnicodeUTF8))
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        button.setProperty("nepomukType",nepomukType)
        button.setProperty("label", label)
        button.clicked.connect(self.showResourcesByType)
        return button
    
    def showResourcesByType(self):
        nepomukType = QUrl(self.sender().property("nepomukType").toString())
        label = self.sender().property("label").toString()
        if nepomukType == PIMO.Task:
            currentEditor = TaskTree(mainWindow=self, makeActions=True)
            index = self.editors.currentIndex()
            self.editors.removeTab(index)
            self.editors.insertTab(index, currentEditor, label)
            self.editors.setCurrentIndex(index)
        
        else:
            currentEditor = ResourcesByTypeTable(mainWindow=self, nepomukType=nepomukType)
            index = self.editors.currentIndex()
            self.editors.removeTab(index)
            self.editors.insertTab(index, currentEditor, label)
            self.editors.setCurrentIndex(index) 

        
    def applySettings(self): 
        settings = QSettings()
        size = settings.value("Ginkgo/Size", QVariant(QSize(600, 500))).toSize()
        self.resize(size)
        position = settings.value("Ginkgo/Position", QVariant(QPoint(200, 100))).toPoint()
        self.move(position)
        self.restoreState(settings.value("Ginkgo/State").toByteArray())


    def save(self):
        currentEditor = self.editors.currentWidget()
        index = self.editors.currentIndex()
        currentEditor.save()
        if currentEditor.resource:
            self.editors.setTabText(index, currentEditor.resource.genericLabel())
        
    
    
    def typeIcon(self, nepomukType, size=16):
        if nepomukType == NFO.Website:
            return self.kdeIcon("mimetypes/text-html.png", size)
        elif nepomukType == PIMO.Task:
            return QIcon(":/task-large")
        elif nepomukType == NCO.Contact:
                return QIcon(":/contact-large")
        else:
            return QIcon(":/nepomuk-large")
        
    
    def resourceIcon(self, resource, size=16):
        types = resource.types()

        if size == 16:
            if NCO.Contact in types:
                return QIcon(":/contact-small")
            elif PIMO.Task in types:
                return QIcon(":/task-small")
            elif NFO.Website in types:
                return QIcon(self.kdeIcon("mimetypes/text-html.png", 16))
            elif NFO.FileDataObject in types:
                mimetype = mimetypes.guess_type(str(resource.property(NIE.url).toString()))
                elt = mimetype[0]
                if elt:
                    elt = elt.replace("/","-")
                    return self.kdeIcon("mimetypes/"+elt+".png", 16)
                return QIcon(":/nepomuk-small")
            else:
                return QIcon(":/nepomuk-small")
        else:
            iconPath = resource.genericIcon()
            if iconPath and len(iconPath) > 0 and os.path.exists(iconPath):
                return QIcon(iconPath)
            elif PIMO.Task in types:
                return QIcon(":/task-large")
            elif NCO.Contact in types:
                return QIcon(":/contact-large")
            
            elif NFO.FileDataObject in types:
                mimetype = mimetypes.guess_type(str(resource.property(NIE.url).toString()))
                elt = mimetype[0]
                if elt:
                    elt = elt.replace("/","-")
                    icon = "/usr/share/icons/oxygen/48x48/mimetypes/"+elt+".png"
                    if os.path.exists(icon):
                        return QIcon(icon)
                return QIcon(":/nepomuk-large")
            else:
                return QIcon(":/nepomuk-large")

#http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname
def getClass( clazz ):
    parts = clazz.split('.')
    module = ".".join(parts[:-1])
    module = __import__( module )
    for comp in parts[1:]:
        module = getattr(module, comp)            
    return module


if __name__ == "__main__":
    app = QApplication(sys.argv)
    #app.setOrganizationName("KDE")
    #app.setOrganizationDomain("kde.org")
    app.setApplicationName("Gingko")
    app.setWindowIcon(QIcon(":/nepomuk"))
    ginkgo = Ginkgo()
    ginkgo.show()
    sys.exit(app.exec_())

