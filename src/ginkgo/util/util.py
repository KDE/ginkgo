from ginkgo.dao import datamanager
import hashlib


def computeMd5(string):
    m = hashlib.md5()
    m.update(string)
    digest = m.hexdigest()
    return digest

def createDictFromResourceDescription(resourceLabel, separator="=", commentSign="#"):
    mapperResource = datamanager.findResourceByLabel(resourceLabel)
    mapperContent = unicode(mapperResource.description())
    lines = mapperContent.splitlines()
    mapping = dict()
    for line in lines:
        if line.find(commentSign) == 0 or len(line.strip()) == 0:
            continue
        words = line.split(separator)
        mapping[words[0].strip()] = words[1].strip()
    return mapping

