

from PyKDE4.nepomuk import Nepomuk
from PyKDE4.soprano import Soprano
from PyKDE4.kdecore import KRandom
from PyQt4.QtCore import QUrl

PIM = QUrl('http://www.semanticdesktop.org/ontologies/2007/11/01/pimo#PersonalInformationModel')
THING = QUrl('http://www.semanticdesktop.org/ontologies/2007/11/01/pimo#Thing')

def pimoContext():
    sparql = "select ?c ?onto where {?c a <%s> . OPTIONAL {?c a ?onto . FILTER(?onto=<%s>). } } " % (str(PIM.toString()), str(Soprano.Vocabulary.NRL.Ontology().toString()))
    model = Nepomuk.ResourceManager.instance().mainModel()
    it = model.executeQuery(sparql, Soprano.Query.QueryLanguageSparql)
    if it.next():
        pimoContext = it.binding(0).uri()
        if not it.binding(1).isValid():
            stmt = Soprano.Statement(Soprano.Node(pimoContext), Soprano.Node(Soprano.Vocabulary.RDF.type()), Soprano.Node(Soprano.Vocabulary.NRL.Ontology()), Soprano.Node(pimoContext))
            model.addStatement(stmt)

    else:
        pimoContext = QUrl(Nepomuk.ResourceManager.instance().generateUniqueUri())
        stmt = Soprano.Statement(Soprano.Node(pimoContext), Soprano.Node(Soprano.Vocabulary.RDF.type()), Soprano.Node(PIM), Soprano.Node(pimoContext))
        model.addStatement(stmt)
        stmt = Soprano.Statement(Soprano.Node(pimoContext), Soprano.Node(Soprano.Vocabulary.RDF.type()), Soprano.Node(Soprano.Vocabulary.NRL.Ontology()), Soprano.Node(pimoContext))
        model.addStatement(stmt)
    it.close()
    return pimoContext

#source: see pimomodel.cpp
def newClassUri(name):
    
    if len(name)>0:
        normalizedName = str(name).replace( r"[^\\w\\.\\-_:]", "" )
        s = "nepomuk:/" + normalizedName
        sparql = "ask where { { <%1> ?p1 ?o1 . } UNION { ?r2 <%1> ?o2 . } UNION { ?r3 ?p3 <%1> . } }" % s
        model = Nepomuk.ResourceManager.instance().mainModel()
        while True:
            sparql = "ask where { { <%1> ?p1 ?o1 . } UNION { ?r2 <%1> ?o2 . } UNION { ?r3 ?p3 <%1> . } }" % s
            result = model.executeQuery(sparql, Soprano.Query.QueryLanguageSparql).boolValue()
            if not result:
                return s
            s = "nepomuk:/" + normalizedName + "_" +  KRandom.randomString(20)
    else:
        return Nepomuk.ResourceManager.instance().generateUniqueUri()


#Ported from C++ from svn://anonsvn.kde.org/home/kde/trunk/playground/base/nepomuk-kde/nepomukutils/pimomodel.cpp
def createPimoClass(parentClassUri, label):
    
    if label is None or len(unicode(label).strip()) == 0:
        print "Class label cannot be empty."
        return None
    
    parentClass = Nepomuk.Types.Class(parentClassUri)
    pimoThingClass = Nepomuk.Types.Class(THING)
    if parentClassUri != THING and not parentClass.isSubClassOf(pimoThingClass):
        print "New PIMO class needs to be subclass of pimo:Thing."
        return None

    classUri = Nepomuk.ResourceManager.instance().generateUniqueUri()

    ctx = Soprano.Node(pimoContext())
    model = Nepomuk.ResourceManager.instance().mainModel()
    stmt = Soprano.Statement(Soprano.Node(QUrl(classUri)), Soprano.Node(Soprano.Vocabulary.RDF.type()), Soprano.Node(Soprano.Vocabulary.RDFS.Class()), ctx)
    model.addStatement(stmt)
    stmt = Soprano.Statement(Soprano.Node(QUrl(classUri)), Soprano.Node(Soprano.Vocabulary.RDFS.subClassOf()), Soprano.Node(QUrl(parentClassUri)), ctx)
    model.addStatement(stmt)
    
    #TODO: check why all classes in the db are subclass of themselves
    stmt = Soprano.Statement(Soprano.Node(QUrl(classUri)), Soprano.Node(Soprano.Vocabulary.RDFS.subClassOf()), Soprano.Node(QUrl(classUri)), ctx)
    model.addStatement(stmt)
    
    stmt = Soprano.Statement(Soprano.Node(QUrl(classUri)), Soprano.Node(Soprano.Vocabulary.RDFS.label()), Soprano.Node(Soprano.LiteralValue(label)), ctx)
    model.addStatement(stmt)
    return Nepomuk.Resource(classUri)

def printPimoThingSubClasses():
    thing = Nepomuk.Types.Class(THING)
    for sc in thing.subClasses():
        print Nepomuk.Resource(sc.uri()).genericLabel()

printPimoThingSubClasses()
print "-------------"

createPimoClass(THING, "new-pimo-xx-12")

printPimoThingSubClasses()
