# ricodebug - A GDB frontend which focuses on visually supported
# debugging using data structure graphs and SystemC features.
#
# Copyright (C) 2011  The ricodebug project team at the
# Upper Austrian University Of Applied Sciences Hagenberg,
# Department Embedded Systems Design
#
# This file is part of ricodebug.
#
# ricodebug is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# For further information see <http://syscdbg.hagenberg.servus.at/>.

from PyQt4.QtCore import QObject, SIGNAL

class Variable(QObject):
    """ Class holding a Variable. <br>
        This is the Parent of all Variable-Classes and the Core of all VariableWrappers.
        It holds the most basic Elements of a Variable-Object, that are useful for all (or at least the most) purposes.
    """

    def __init__(self, variablepool, exp=None, gdbname=None, uniquename=None, type=None, value=None, inscope=None, haschildren=None, access=None, pending=False):
        """ Constructor
        @param variablepool    variables.variablepool.VariablePool, the VariablePool-Instance
        """
        QObject.__init__(self)
        
        self.variablepool = variablepool
        
        # initialize all attributes with default values
        self.exp = exp
        self.gdbname = gdbname
        self.uniquename = uniquename
        self.type = type
        self.value = value
        self.inscope = inscope
        self.haschildren = haschildren
        self.access = access
        self.pending = pending
        self.childItems = []
        
        
    def getExp (self):
        return self.exp
    
    def setExp (self, exp):
        self.exp = exp
        
    def getGdbName (self):
        return self.gdbname
    
    def setGdbName (self, gdbname):
        self.gdbname = gdbname
        
    def getUniqueName (self):
        return self.uniquename
    
    def setUniqueName (self, uniquename):
        self.uniquename = uniquename       
        
    def getType (self):
        return self.type
    
    def setType (self, type):
        self.type = type        
        
    def getValue (self):
        return self.value
    
    def setValue (self, value):
        self.variablepool.assignValue(self.gdbname, value)
        self.value = value
        
    def getInScope (self):
        return self.inscope
    
    def setInScope (self, inscope):
        self.inscope = inscope 
        
    def getAccess(self):
        return self.access
    
    def setAccess(self, access):
        self.access = access
    
    def getPending(self):
        return False
    
    def _getChildItems (self):
        """ Returns a list of childs as Variables.
            This is a pure private Method!
        @return    List of Variables, children of the variable.
        """
        if self.haschildren == True and self.childItems.__len__() == 0:
            self.variablepool.getChildren(self.gdbname, self.childItems, self.access, self.uniquename)
        return self.childItems
    
    def makeWrapper(self, vwFactory):
        """ Returns a VariableWrapper for the Variable. <br>
            The Type of the VariableWrapper depends on the Type of the Variable and the vwFactory.
        @param vwFactory   variables.varwrapperfactory.VarWrapperFactory, Factory to create the VariableWrapper 
        @return            variables.variablewrapper.VariableWrapper, VariableWrapper for the Variable
        """
        raise "pure virtual Function Variable::makeWrapper() called"
    
    def changed(self):
        self.emit(SIGNAL('changed()'))
        
    def replace(self, var):
        self.emit(SIGNAL('replace(PyQt_PyObject)'), var)

