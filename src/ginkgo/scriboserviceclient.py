#!/usr/bin/env python
# -*- coding: utf-8 -*-

## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE included in the packaging of
## this file. 
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
## See the NOTICE file distributed with this work for additional
## information regarding copyright ownership.


"A simple query service client that allows to perform queries against the Query Service"

import sys
import dbus
import gobject
from dbus.mainloop.glib import DBusGMainLoop
from PyQt4 import QtCore
from PyKDE4.nepomuk import Nepomuk

# The main event loop as a global var so we can end it in finishedListingHandler
loop = gobject.MainLoop()

def newEntityHandler(entityUri, occurrences):
    
    resource = Nepomuk.Resource(entityUri)
    label = u"%s" % resource.genericLabel()
    print label
    
    print occurrences

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

    sessionPath = iface.analyzeText(sys.argv[1])
    dobject = bus.get_object("org.kde.nepomuk.services.nepomukscriboservice", sessionPath)
    session = dbus.Interface(dobject, "org.kde.nepomuk.ScriboSession")

    session.connect_to_signal('newLocalEntity', newEntityHandler)
    session.connect_to_signal('finished', finishedHandler)
#    session.connect_to_signal('newEntity', newEntityHandler)

    session.start()

    # run the event loop until all results are in
    loop.run()

if __name__ == '__main__':
    main()
