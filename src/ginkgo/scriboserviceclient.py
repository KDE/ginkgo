#!/usr/bin/env python
"A simple query service client that allows to perform queries against the Query Service"

import os
import sys
import dbus
import gobject
from dbus.mainloop.glib import DBusGMainLoop
from PyQt4 import QtCore


# The main event loop as a global var so we can end it in finishedListingHandler
loop = gobject.MainLoop()

def newEntityHandler(entity, occurrences):
    print entity, occurrences

def textExtractedHandler(text):
    print "Extracted text from image: '%s'" % text
    
def finishedHandler():
    print "finished"
    loop.quit()

def main():
    # register the event loop
    DBusGMainLoop(set_as_default=True)

    # get the connection to the service
    bus = dbus.SessionBus()
    dobject = bus.get_object("org.kde.nepomuk.services.nepomukscriboservice", '/nepomukscriboservice')
    iface = dbus.Interface(dobject, "org.kde.nepomuk.Scribo")

    if os.path.exists(sys.argv[1]):
        sessionPath = iface.analyzeResource(sys.argv[1])
    else:
        sessionPath = iface.analyzeText(sys.argv[1])
        
    dobject = bus.get_object("org.kde.nepomuk.services.nepomukscriboservice", sessionPath)
    session = dbus.Interface(dobject, "org.kde.nepomuk.ScriboSession")

    session.connect_to_signal('newLocalEntity', newEntityHandler)
    session.connect_to_signal('textExtracted', textExtractedHandler)
    session.connect_to_signal('finished', finishedHandler)
#    session.connect_to_signal('newEntity', newEntityHandler)

    session.start()

    # run the event loop until all results are in
    loop.run()

if __name__ == '__main__':
    main()
