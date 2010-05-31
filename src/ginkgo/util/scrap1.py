from PyKDE4.nepomuk import Nepomuk
from PyKDE4.soprano import Soprano
from ginkgo.ontologies import PIMO
from PyQt4.QtCore import QUrl

pimoContext = Nepomuk.ResourceManager.instance().generateUniqueUri()
pimoContext = QUrl(pimoContext)
model = Nepomuk.ResourceManager.instance().mainModel()
stmt = Soprano.Statement(Soprano.Node(pimoContext), Soprano.Node(Soprano.Vocabulary.RDF.type()), Soprano.Node(PIMO.PersonalInformationModel), Soprano.Node(pimoContext))
model.addStatement(stmt)

print "done"


