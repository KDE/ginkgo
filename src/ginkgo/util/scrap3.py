#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyKDE4.nepomuk import Nepomuk
from PyKDE4.soprano import Soprano

resource = Nepomuk.Resource("test-10")

desc = u"à%1"
resource.setDescription(desc)
resource.setDescription(u"ààà81818")
print resource.uri()


sparql = "select ?b ?c where {<%s> ?b ?c}" % resource.uri()
model = Nepomuk.ResourceManager.instance().mainModel()

iter = model.executeQuery(sparql, Soprano.Query.QueryLanguageSparql)
bindingNames = iter.bindingNames()
while iter.next() :
    bindingSet = iter.current()
    for i in range(len(bindingNames)) :
        v = bindingSet.value(bindingNames[i])
        if not v.isLiteral():
            print v.uri()
        else:
            value = v.literal().toString()
            print value

    

print "done"


