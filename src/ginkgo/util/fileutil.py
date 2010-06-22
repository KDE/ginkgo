import gzip
import os
from logging import codecs


def writeStringToFile(content, file, encoding="utf-8", gzip=False):
    if os.path.exists(file):
        # ensure that we can write the file
        os.chmod(file, 0644)
    # write the string
    f=codecs.open(file, "w", encoding)
    #f = open(file,'a+')    
    f.write(content)
    f.close()
    if gzip:
        compressFile(file)

def appendStringToFile(content, file):
    if os.path.exists(file):
        # ensure that we can write the file
        os.chmod(file, 0644)
    # write the string
    #f=open(file, "w")
    f = codecs.open(file, 'a+', encoding='utf-8')    
    f.write(content)
    f.close()
        
def compressFile(file):
    #if config.get('global', 'gzip') == True:
    rfile = open(file, 'r')
    wfile = gzip.GzipFile(file + '.gz', 'w', 9)
    wfile.write(rfile.read())
    wfile.flush()
    wfile.close()
    rfile.close()
    os.unlink(file) #We don't need the file now
