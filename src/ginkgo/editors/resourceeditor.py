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



from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyKDE4.kdeui import *
from PyKDE4.kdecore import i18n
from ginkgo.views.resourcepropertiestable import ResourcePropertiesTable
from PyKDE4.kdecore import KUrl
from ginkgo.util.krun import krun
from PyKDE4.soprano import Soprano 
from PyKDE4.nepomuk import Nepomuk
from ginkgo.util import util
from ginkgo.views.relationstable import RelationsTable
from ginkgo.views.sparqlview import SparqlResultsTable
from ginkgo.views.suggestionview import SuggestionsTable
from ginkgo.dialogs.typechooserdialog import TypeChooserDialog
from ginkgo.ontologies import NIE, PIMO, NCO
import os

def getClass(clazz):
    parts = clazz.split('.')
    module = ".".join(parts[:-1])
    module = __import__(module)
    for comp in parts[1:]:
        module = getattr(module, comp)            
    return module


class ResourceEditor(QWidget):
    def __init__(self, mainWindow=False, resource=None, nepomukType=None):
        super(ResourceEditor, self).__init__()
        self.mainWindow = mainWindow
        self.defaultIcon = ":/nepomuk-large"
        self.resource = resource
        self.nepomukType = nepomukType
        
#        print self.__class__
#        print ResourceEditor.__class__
        if self.__class__ == getClass("ginkgo.editors.resourceeditor.ResourceEditor"):
            self.ui = ResourceEditorUi(self)
        

    def resourceIcon(self):
        if self.resource:
            return self.mainWindow.resourceIcon(self.resource, 64)
        elif self.nepomukType:
            return self.mainWindow.typeIcon(self.nepomukType, 64)   
        else:
            return KIcon(self.defaultIcon)

    def selectIcon(self):
        path = QFileInfo("~/").path()
        fname = QFileDialog.getOpenFileName(self, i18n("Select Icon - Ginkgo"), path, i18n("Images (*.png *.jpg *.jpeg *.bmp)"))
        
        if fname and len(fname) > 0 and os.path.exists(fname):
            #save the resource to create it if it doesn't exist yet
            if not self.resource:
                self.save()
            self.resource.setSymbols([fname])
            self.ui.iconButton.setIcon(KIcon(fname))
            


    def save(self):
        self.setCursor(Qt.WaitCursor)
        if self.resource is None:
            self.resource = self.mainWindow.createResource(self.ui.resourceLabel(), self.nepomukType)
        
        else:
            #TODO: remove an editor when the edited resource was deleted externally
            if len(self.resource.types()) == 0:
                self.resource = self.mainWindow.createResource(self.ui.resourceLabel(), self.nepomukType)      
        

        self.ui.relationsTable.setResource(self.resource)
        self.ui.propsTable.setResource(self.resource)
        
        if hasattr(self.ui, "typePropertiesTable"):
            self.ui.typePropertiesTable.setResource(self.resource)
        
        
#        #save generic properties
        self.resource.setLabel(unicode(self.ui.resourceLabel()))
        
        desc = unicode(self.ui.description.toPlainText())
        
        self.resource.setDescription(desc)
        if hasattr(self.ui, "url"):
            self.resource.setProperty(NIE.url, Nepomuk.Variant(QUrl(unicode(self.ui.url.text()))))
        
        #TODO: catch Except and print warning
        #reply = QMessageBox.warning(self, i18n("Warning", ), i18n("An error ocurred when saving the resource. You should copy and paste this resource's contents to a distinct editor. Please report a bug."))

        #update the fields only if we are not in a sbuclass, otherwise, the fields get updated
        #before their actual value are saved (see the contacteditor for instance)
        if self.__class__ == getClass("ginkgo.editors.resourceeditor.ResourceEditor"):
            self.ui.updateFields()
        
        self.unsetCursor()
                            
    def focus(self):
        self.ui.label.setFocus(Qt.OtherFocusReason)
        
    def focusOnLabelField(self):
        self.ui.label.setFocus(Qt.OtherFocusReason)
        self.ui.label.selectAll()
        
    def showResourceTypesDialog(self):
        #save the resource to create it if it doesn't exist yet
        if not self.resource:
            self.save()
                
        dialog = TypeChooserDialog(mainWindow=self.mainWindow, typesUris=self.resource.types())
        if dialog.exec_():
            chosenTypes = dialog.chosenTypes()
            types = []
            for type in chosenTypes:
                types.append(type.resourceUri())
            
            self.resource.setTypes(types)
            self.ui.updateFields()
    
    def executeInlineQuery(self):
        cursor = self.ui.description.textCursor()
        selection = cursor.selectedText()

        #Note: If the selection obtained from an editor spans a line break, the text will contain a 
        #Unicode U+2029 paragraph separator character instead of a newline \n character. 
        #Use QString::replace() to replace these characters with newlines. 
        
        sparqlViewTabIndex = -1
        for index in range(self.ui.relationsWidget.count()):
            tab = self.ui.relationsWidget.widget(index)
            if tab.__class__ == getClass("ginkgo.views.sparqlview.SparqlResultsTable"):
                sparqlViewTabIndex = index
                break
        
        if sparqlViewTabIndex < 0:
            self.sparqlView = SparqlResultsTable(mainWindow=self.mainWindow, sparql=selection)
            self.ui.relationsWidget.addTab(self.sparqlView , i18n("Query results"))
            self.ui.relationsWidget.setCurrentWidget(self.sparqlView)
        else:
            self.sparqlView.setSparql(selection)
            self.sparqlView.installModels()
            self.ui.relationsWidget.setCurrentIndex(sparqlViewTabIndex)
            
    def suggestRelations(self):
        suggestionViewTabIndex = -1
        text = u"%s" % self.ui.description.toPlainText()
        title = u"%s" % self.ui.label.text()
        
        for index in range(self.ui.relationsWidget.count()):
            tab = self.ui.relationsWidget.widget(index)
            if tab.__class__ == getClass("ginkgo.views.suggestionview.SuggestionsTable"):
                suggestionViewTabIndex = index
                break

        
        if suggestionViewTabIndex < 0:
            self.suggestionView = SuggestionsTable(mainWindow=self.mainWindow, editor=self.ui.description, resource=self.resource, title=title, text=text)
            self.ui.relationsWidget.addTab(self.suggestionView , i18n("Suggestions"))
            self.ui.relationsWidget.setCurrentWidget(self.suggestionView)
            self.suggestionView.runAnalyzis()
        else:
            self.suggestionView.setText(text)
            self.suggestionView.installModels()
            self.ui.relationsWidget.setCurrentIndex(suggestionViewTabIndex)
            self.suggestionView.runAnalyzis()    


class ResourceEditorUi(object):
    
    def __init__(self, editor):
        self.editor = editor
        self.labelEdited = False
        self.setupUi()
        
    def onLabelEdited(self, text):
        self.labelEdited = True
#        if text and len(text) > 0:
#            p = QPalette()
#            p.setColor(QPalette.Text, p.color(QPalette.Normal, QPalette.Text))
#            self.label.setPalette(p)
#            f = self.label.font()
#            f.setItalic(False)
#            self.label.setFont(f)
    
    def setupUi(self):
        #create the card sheet on the left
        card = QWidget(self.editor)
        vlayout = QVBoxLayout(card)
        vlayout.addWidget(self.createIconWidget(card))
        vlayout.addWidget(self.createMainPropertiesWidget(card))
        
        #create the right pane: description + relations
        self.rightpane = QSplitter(self.editor)
        self.rightpane.setOrientation(Qt.Horizontal)
        
#        button = KPushButton()
#        button.setIcon(KIcon("edit-rename"))
#        button.setStyleSheet("border:none;")
#        hbox.addWidget(button)
        
        descriptionWidget = QWidget(self.rightpane)

        infoWidget = QWidget(descriptionWidget)

        hbox = QHBoxLayout(infoWidget)
        self.label = KLineEdit()
        shortcut = QShortcut(QKeySequence("Ctrl+L"), self.label);
        shortcut.activated.connect(self.editor.focusOnLabelField)
        
        self.label.setMinimumWidth(400)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
#        p = QPalette()
#        p.setColor(QPalette.Text, p.color(QPalette.Disabled, QPalette.Text))
#        self.label.setPalette(p)
#        f = self.label.font()
#        f.setItalic(True)
#        self.label.setFont(f)
#        self.label.setText(i18n("Title..."))
#        self.label.setCursorPosition(0)
        
        
        self.label.textEdited.connect(self.onLabelEdited)
        hbox.setContentsMargins(0, 0, 0, 0)
        
        hbox.addWidget(self.label)
        
        spacerItem = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Minimum)
        hbox.addItem(spacerItem)
        
        #typesInfo = QLabel(i18n("Type(s): "))
        self.typesInfo = KPushButton() 
        self.typesInfo.clicked.connect(self.editor.showResourceTypesDialog)
        
        hbox.addWidget(self.typesInfo)
        
        vboxlayout = QVBoxLayout(descriptionWidget)
        #gridlayout = QGridLayout(descriptionWidget)
        
#        descriptionLabel = QLabel(descriptionWidget)
#        descriptionLabel.setText(i18n("&Description:")) 
        self.description = KTextEdit(self.editor)
        self.description.setTabChangesFocus(False)
        self.description.setCheckSpellingEnabled(False)
        #self.description.setLineWrapMode(QTextEdit.NoWrap)
        self.description.setAcceptRichText(False)
        self.description.setObjectName("Notes")
        self.description.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
#        descriptionLabel.setBuddy(self.description)

        shortcut = QShortcut(QKeySequence("Ctrl+Alt+X"), self.description);
        shortcut.activated.connect(self.editor.executeInlineQuery)

        shortcut = QShortcut(QKeySequence("Ctrl+Alt+Y"), self.description);
        shortcut.activated.connect(self.editor.suggestRelations)

        
        #hline = QFrame(descriptionWidget)
        #hline.setGeometry(QRect(150, 190, 118, 3))
        #hline.setFrameShape(QFrame.HLine)
        #hline.setFrameShadow(QFrame.Sunken)
        
        vboxlayout.addWidget(infoWidget)
        #vboxlayout.addWidget(hline)
#        gridlayout.addWidget(infoWidget, 0, 0, 1, 1)
#        gridlayout.addWidget(hline, 1, 0, 1, 1)
        
        infoWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        
#        vboxlayout.addWidget(descriptionLabel)
        vboxlayout.addWidget(self.description)
        
        self.relationsWidget = KTabWidget(self.rightpane)
        #vboxlayout = QVBoxLayout(relationsWidget)
        #self.relationsLabel = QLabel(relationsWidget)
        
        self.relationsTable = RelationsTable(mainWindow=self.editor.mainWindow, editor=self.description)
        self.propsTable = ResourcePropertiesTable(mainWindow=self.editor.mainWindow)
        
        self.relationsWidget.addTab(self.relationsTable , i18n("Relations"))
        self.relationsWidget.addTab(self.propsTable, i18n("Properties"))
        
#        self.relationsLabel.setBuddy(relationsTable)
#        vboxlayout.addWidget(self.relationsLabel)
#        vboxlayout.addWidget(relationsTable)
        
        self.rightpane.addWidget(descriptionWidget)
        self.rightpane.addWidget(self.relationsWidget)
        self.rightpane.setSizes([100, 300])
        self.rightpane.restoreState(self.editor.mainWindow.descriptionSplitterState)
        
        #self.tabs.addTab(self.description, "Description")
        #self.tabs.setTabPosition(QTabWidget.North)
        
        splitter = QSplitter(self.editor)
        hlayout = QHBoxLayout(self.editor)
        hlayout.addWidget(splitter)
        splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        splitter.addWidget(card)
        splitter.addWidget(self.rightpane)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        self.updateFields()

        #update the description field only here since we actually don't want it to be updated
        #on save, unless we carefully make sure that all the ui is kept unchanged after resetting
        #the text: scrollbar position, caret position, selected text.
        if self.editor.resource:
            cursor = self.description.textCursor()
            pos = cursor.position()
            self.description.setText(self.editor.resource.description())
            cursor.setPosition(pos)
            self.description.setTextCursor(cursor)


    def updateFields(self):
        if self.editor.resource:
            if hasattr(self, "name"):
                self.name.setText(self.editor.resource.property(Soprano.Vocabulary.NAO.prefLabel()).toString())


            if hasattr(self, "url"):
                if len(self.editor.resource.property(NIE.url).toString()) > 0:
                    self.url.setText(self.editor.resource.property(NIE.url).toString())
                else:
                    self.url.setText(self.editor.resource.uri())
                
            prefLabel = self.editor.resource.property(Soprano.Vocabulary.NAO.prefLabel()).toString()
            p = QPalette()
            p.setColor(QPalette.Text, p.color(QPalette.Normal, QPalette.Text))
            self.label.setPalette(p)
            f = self.label.font()
            f.setItalic(False)
            self.label.setFont(f)
            self.label.setText(prefLabel)
            
            types = ""
            for type in self.editor.resource.types():
                if type == Soprano.Vocabulary.RDFS.Resource():
                    continue
                typestr = str(type.toString())
                if typestr.find("#") > 0:
                    typestr = typestr[typestr.find("#") + 1:]
                elif typestr.find("nepomuk:/") == 0:
                    #this is a custom type, we need to get the label of the ressource
                    typeResource = Nepomuk.Resource(typestr)
                    typestr = typeResource.genericLabel()
                else:
                    typestr = typestr[typestr.rfind("/") + 1:]
                types = types + i18n(typestr) + ", "
            
            if len(types) > 0:
                types = types[0:len(types) - 2]
            self.typesInfo.setText(i18n("Type(s): ") + types)
            
            self.relationsTable.setResource(self.editor.resource)
            self.propsTable.setResource(self.editor.resource)
        

    def createIconWidget(self, parent):
        iconWidget = QWidget(parent)
        iconWidgetLayout = QHBoxLayout(iconWidget)
        self.iconButton = QPushButton();
        self.iconButton.setIcon(self.editor.resourceIcon())
        size = QSize(80, 80)
        self.iconButton.setIconSize(size)
        self.iconButton.setContentsMargins(40, 40, 40, 40)
        #button.setStyleSheet("border: 20px solid #fff;")
        self.iconButton.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.editor.connect(self.iconButton, SIGNAL("clicked()"), self.editor.selectIcon)
        iconWidgetLayout.addStretch(1)
        iconWidgetLayout.addWidget(self.iconButton)
        iconWidgetLayout.addStretch(1)
        return iconWidget

    def createMainPropertiesWidget(self, parent):
        propertiesWidget = QWidget(parent)

        self.gridlayout = QGridLayout(propertiesWidget)
#        self.gridlayout.setMargin(9)
#        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")
        
#        tagBox = QGroupBox(i18n("Tags"))
#        self.tags = Nepomuk.TagWidget()
#        vbox = QVBoxLayout(tagBox)
#        vbox.addWidget(self.tags)
#        self.gridlayout.addWidget(tagBox, 0, 0, 1, 2)

        #TODO: move this to a config panel so that types whose editor contains a dedicated URL field can be defined by the user
        classesWithUrlField = [Nepomuk.Types.Class(PIMO.Organization), Nepomuk.Types.Class(PIMO.Project),
                               Nepomuk.Types.Class(PIMO.Person),
                               Nepomuk.Types.Class(NCO.PersonContact),
                               Nepomuk.Types.Class(QUrl("http://purl.org/dc/dcmitype/Software"))]
        if self.editor.resource:
            flag = False
            for type in self.editor.resource.types():
                typeClass = Nepomuk.Types.Class(type)
                for parentClass in typeClass.allParentClasses():
                    if typeClass in classesWithUrlField or parentClass in classesWithUrlField:
                        self.addUrlBox(propertiesWidget)
                        flag = True
                        break
                if flag:
                    break
        else:
            typeClass = Nepomuk.Types.Class(self.editor.nepomukType)
            for parentClass in typeClass.allParentClasses():
                if typeClass in classesWithUrlField or parentClass in classesWithUrlField:
                    self.addUrlBox(propertiesWidget)
                    break
            
                
        spacerItem = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 1, 0, 1, 1)
        
        return propertiesWidget

    def addUrlBox(self, propertiesWidget):
        box = QGroupBox(i18n("&URL"))
        
        vbox = QVBoxLayout(box)
        self.url = QLineEdit(propertiesWidget)
        self.url.setObjectName("url")
        
        
        vbox.addWidget(self.url)
        
        button = QPushButton(propertiesWidget)
        button.setText(i18n("Open"))
        button.clicked.connect(self.openWebPage)
        vbox.addWidget(button)
        self.gridlayout.addWidget(box, 0, 0, 1, 1)
        

    def openWebPage(self):
        kurl = KUrl(self.url.text())
        krun(kurl, QWidget(), False)
    
    def resourceLabel(self):
        return self.label.text()
