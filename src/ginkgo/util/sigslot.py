#
# sigslot2.py  python signals and slots with arguments
#
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Widget(QObject):

    def __init__(self, key):
        super(Widget, self).__init__()
        self.key = key
        
    def noArgument(self):
        self.emit(SIGNAL("sigNoArgument"), ())

    def oneArgument(self):
        self.emit(SIGNAL("sigOneArgument"), self.key)
        

    def twoArguments(self):
        self.emit(SIGNAL("sigTwoArguments"), (1, "two"))

class Application(QObject):

    def __init__(self):
        QObject.__init__(self)

        self.widget = Widget("hehe")


        #self.connect(self.widget, SIGNAL("sigNoArgument"), self.printNothing)
        self.connect(self.widget, SIGNAL("sigOneArgument"), self.printOneArgument)
        #self.connect(self.widget, SIGNAL("sigTwoArguments"), self.printTwoArguments)
        #self.connect(self.widget, SIGNAL("sigTwoArguments"), self.printVariableNumberOfArguments)

    def printNothing(self):
        print "No arguments"

    def printOneArgument(self, arg):
        print "One argument", arg

    def printTwoArguments(self, arg1):
        print "Two arguments", arg1

    def printVariableNumberOfArguments(self, *args):
        print "list of arguments", args

app=Application()
app.widget.noArgument()
app.widget.oneArgument()
app.widget.twoArguments()
