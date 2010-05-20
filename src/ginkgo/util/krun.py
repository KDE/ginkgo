from PyKDE4.kio import *
from PyKDE4.kdecore import *

# source http://code.google.com/p/lilykde/source/browse/trunk/lilykde/py/lilykde/util.py
class krun(KRun):
    """
    A wrapper around KRun that keeps a pointer to itself until
    a finished() signal has been received
    """
    __savedInstances = []

    def __init__(self, url, widget, isLocal):
        KRun.__init__(self, KUrl(url), widget, 0, isLocal)
        self.setAutoDelete(False)
        krun.__savedInstances.append(self)
        self.finished.connect(self._slotExit)

    def _slotExit(self):
        krun.__savedInstances.remove(self)
