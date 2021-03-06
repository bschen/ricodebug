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

from variables.variable import Variable

class PendingVariable(Variable):
    """ Variable-Class holding a pending Variable """

    def __init__(self, variablepool, exp=None, gdbname=None, uniquename=None, type=None, value=None, inscope=None, haschildren=None, access=None):
        """ Constructor
        @param variablepool    variables.variablepool.VariablePool, the VariablePool-Instance
        """
        Variable.__init__(self, variablepool, exp, gdbname, uniquename, type, value, inscope, haschildren, access)
    
    def getPending(self):
        return True
    
    def makeWrapper(self, vwFactory):
        """ Returns a VariableWrapper for the Variable. <br>
            The Type of the VariableWrapper depends on the Type of the Variable and the vwFactory.
        @param vwFactory   variables.varwrapperfactory.VarWrapperFactory, Factory to create the VariableWrapper 
        @return            variables.variablewrapper.VariableWrapper, VariableWrapper for the Variable
        """
        return vwFactory.makePendingVarWrapper(self)
    
    def dereference(self):
        """ Dereferences the Variable, if possible.
        @return    dereferenced Variable if the Variable can be dereferenced,
                   None in this Case.
        """
        return None

