import hashlib


def computeMd5(string):
    m = hashlib.md5()
    m.update(string)
    digest = m.hexdigest()
    return digest