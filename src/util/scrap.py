#! /usr/bin/env python
# -*- coding: utf-8 -*-


from PyKDE4.soprano import Soprano
from PyKDE4.nepomuk import Nepomuk

from PyKDE4.kio import KDirModel, KRun
from PyQt4.QtCore import QUrl, QVariant, QString
from PyQt4.QtGui import *

from dao import NCO

import sys
from PyKDE4.kdecore import ki18n, KAboutData, KCmdLineArgs
from PyKDE4.kdeui import KApplication
from PyKDE4.kio import KRun
from PyKDE4.kdecore import KUrl
 

 
#appName     = "KApplication"
#catalog     = ""
#programName = ki18n ("KApplication")
#version     = "1.0"
#description = ki18n ("KApplication/KMainWindow/KAboutData example")
#license     = KAboutData.License_GPL
#copyright   = ki18n ("(c) 2007 Jim Bublitz")
#text        = ki18n ("none")
#homePage    = "www.riverbankcomputing.com"
#bugEmail    = "jbublitz@nwinternet.com"
# 
#aboutData   = KAboutData (appName, catalog, programName, version, description,
#                        license, copyright, text, homePage, bugEmail)
# 
# 
#KCmdLineArgs.init (sys.argv, aboutData)
# 
#app = KApplication ()
#
#widget = QWidget()
#
#url = KUrl(QString("/home/arkub/F/ASU.INRIA.Valudriez.Lamarre.200902.pdf"))
##url = KUrl(QString("http://www.google.com"))
#run = KRun(url, widget, 0, False)

text = _('Bookmark has been added successfully')
print text

#file = Nepomuk.Resource("file:///home/arkub/F/2010-04 OSS Industry Savings.pdf")
#print file.resourceUri()
#
#for key, value in file.allProperties().iteritems():
#    print str(key), value.toString() , value.isResource()


#file = Nepomuk.Resource("<filex://c4fd-7c27/home/arkub/F/RIAO-2010.odt>")
#print file.resourceUri()




if False:
    tag = Nepomuk.Tag("mandriva")
    res = Nepomuk.Resource("gonzo")
    res.addTag(tag)
    
    res.setProperty(NCO.nameGiven, Nepomuk.Variant("Test"))
    #res.setRating(12)
    
    print res.resourceUri()
    print res.genericLabel()
    print res.types()
    
    if False:
        tags = res.property(Soprano.Vocabulary.NAO.hasTag()).toResourceList();
        for atag in tags:
            print atag.genericLabel()
        
        
        tagTerm = Nepomuk.Query.ResourceTerm(Nepomuk.Tag("mandriva"));
        #hasTagProperty =  Nepomuk.Types.Property(Soprano.Vocabulary.NAO.hasTag())
        #term = Nepomuk.Query.ComparisonTerm(hasTagProperty, tagTerm);
        
        tagType = Nepomuk.Types.Class(Soprano.Vocabulary.NAO.Tag())
        term = Nepomuk.Query.ResourceTypeTerm(tagType)
        
        query = Nepomuk.Query.Query(term);
        queryString = query.toSparqlQuery();
        print queryString
        #dirModel =  KDirModel()
        #searchUrl = query.toSearchUrl();
        #dirModel.dirLister().openUrl( searchUrl );
        
        queryString = "select distinct ?r  where { ?r a ?v1 . ?v1 <http://www.w3.org/2000/01/rdf-schema#subClassOf> <http://www.semanticdesktop.org/ontologies/2007/11/01/pimo#Person> .   }"
        
        model = Nepomuk.ResourceManager.instance().mainModel()
        iter = model.executeQuery(queryString, Soprano.Query.QueryLanguageSparql)
        
        bindingNames = iter.bindingNames()
        
        while iter.next() :
            bindingSet = iter.current()
            for i in range(len(bindingNames)) :
                v = bindingSet.value(bindingNames[i])
                ares = Nepomuk.Resource(v.uri())
                print ares.genericLabel()
        
        
        
        #print res

