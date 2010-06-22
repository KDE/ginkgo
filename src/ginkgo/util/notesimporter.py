from ginkgo.dao import datamanager
import httplib2
import os
import time
import re

from PyKDE4.nepomuk import Nepomuk
from PyQt4.QtCore import QUrl
from urllib import urlencode
from urllib import quote

def read_as_string(file):
    # read the file
    f = open(file, "r")
    content = f.read()
    f.close()
    return content


def importNotes(root):
    counter = 0
    newResources = []
    oldResources = []

    for filename in os.listdir(root):
        filepath = os.path.join(root, filename)
        if os.path.isfile(filepath):
                counter += 1
                pcontent = read_as_string(filepath)
                pcontent = pcontent.replace("%Types", "")
                pcontent = pcontent.replace("[[FrNet]]", "")
                pcontent = pcontent.replace("[FrNet]", "")
                content = ""
                lineCounter = 0
                for line in pcontent.split("\n"):
                    if lineCounter == 0 and line.find("1:") == 0:
                        lineCounter += 1
                        continue
                    content = content+line+"\n"
                    lineCounter += 1
                content = content.strip()

                

                res = datamanager.findResourceByLabel(filename, match=Nepomuk.Query.ComparisonTerm.Equal)
                if not res:
                    #newWord = datamanager.createResource(filename, QUrl("nepomuk:/res/c7f1509b-3eaa-4127-b28f-42f459678bcb"))

                    newWord = datamanager.createResource(filename, QUrl("nepomuk:/res/36e59e2e-409a-40a8-9175-c929792383d2"))
                    try:
                        newWord.setDescription(unicode(content))
                    except Exception, e:
                        print filename
                        print e

                    newResources.append(filename)

                else:
#                    print filename
#                    print res.genericLabel()
                    #oldResources.append(res.genericLabel())
                    oldResources.append(filename)
                
                #print oldResources
    
    
    print len(newResources)
    print len(oldResources)
    print counter

def importToXWiki(pcontent, filename):
    data = dict(content= pcontent)
    h = httplib2.Http(".cache")
    resp, content = h.request("http://xwiki:8080/xwiki/rest/wikis/xwiki/spaces/beagle/pages/" + quote(filename),
                          "PUT", urlencode(data),
                          headers={'content-type':'application/x-www-form-urlencoded'})
    print "Response: %s" % resp
#            resp, content = h.request("http://xwiki:8080/xwiki/rest/wikis/xwiki/spaces/beagle/pages/" + name,
#                                  "DELETE")

                

#h.add_credentials('Admin', 'admin')

#print "Content: %s" % content

if __name__ == "__main__":
    root = "/home/arkub/FrNet"
    importNotes(root)

