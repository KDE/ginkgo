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

from PyKDE4.nepomuk import Nepomuk
from PyKDE4.soprano import Soprano 
from PyQt4.QtCore import *


class ClassNode:
    
    def __init__(self, clazz, row, parentNode = None):
        self.clazz = clazz
        self.row = row
        self.parent = parentNode

    def getChild(self, row):
        if row < len(self.children):
            return self.children[row]


    def updateChildren(self):
        
        for child in self.clazz.subClasses():
            self.children.append(ClassNode(child))
            
#    // although classes can have multiple parents in this tree they always have one
#    // but one type can occure in different nodes then
#    ClassNode* parent;
#
#    // if true updateClass is currently running on this node
#    bool updating;
#
#    int row;
#    Nepomuk::Types::Class type;
#    QList<ClassNode*> children;
#};
