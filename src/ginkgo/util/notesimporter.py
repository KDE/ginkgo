import httplib2
import os
import time

from urllib import urlencode
from urllib import quote

def read_as_string(file):
    # read the file
    f = open(file, "r")
    content = f.read()
    f.close()
    return content

h = httplib2.Http(".cache")


print url

counter = 0
for filename in os.listdir(root):
    filepath = os.path.join(root, filename)
    if os.path.isfile(filepath):
            counter += 1
            pcontent = read_as_string(filepath)
            pcontent = pcontent.replace("[EnFr]","[[Wnet]]")
            pcontent = pcontent.replace("1:","=")
            
            data = dict(content= pcontent)
            resp, content = h.request("http://xwiki:8080/xwiki/rest/wikis/xwiki/spaces/beagle/pages/" + quote(filename),
                                  "PUT", urlencode(data),
                                  headers={'content-type':'application/x-www-form-urlencoded'})
            print "Response: %s" % resp
#            resp, content = h.request("http://xwiki:8080/xwiki/rest/wikis/xwiki/spaces/beagle/pages/" + name,
#                                  "DELETE")
            
            

#h.add_credentials('Admin', 'admin')

#print "Content: %s" % content

