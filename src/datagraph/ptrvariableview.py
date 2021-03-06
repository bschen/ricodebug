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

from mako.template import Template
from datagraph.datagraphvw import DataGraphVW, HtmlTemplateHandler
import sys

class PtrVariableTemplateHandler(HtmlTemplateHandler):
    """ TemplateHandler for Pointer-Variables """
    
    def __init__(self, var, distributedObjects):
        """ Constructor
        @param var    datagraph.datagraphvw.DataGraphVW, holds the Data to show """
        HtmlTemplateHandler.__init__(self, var)
        self.distributedObjects = distributedObjects
        self.htmlTemplate = Template(filename=sys.path[0] + '/datagraph/ptrvariableview.mako')
    
    def execLinkCommand(self, commandStr, mainView):
        """ handles the given Command
        @param commandStr  String, the Command to handle
        @param mainView    datagraph.datagraphvw.HtmlVariableView, the View of the top-level-Variable """
        if (commandStr == "close"):
            print "... closing ptrvariableview ..."
            self.distributedObjects.datagraph_controller.removeVar(self.var)
        if (commandStr == "dereference"):
            print "... dereferencing var ..."
            dgvw = self.var.dereference()
            if (dgvw != None):
                print "-> exp: " + dgvw.getExp()
                self.distributedObjects.datagraph_controller.addVar(dgvw)
                self.distributedObjects.datagraph_controller.addPointer(mainView, dgvw.getView())
            else:
                print "Null-Pointer wasn't dereferenced."


class PtrDataGraphVW(DataGraphVW):
    """ VariableWrapper for Pointer-Variables """
    
    def __init__(self, variable, distributedObjects, vwFactory):
        """ Constructor
        @param variable            variables.variable.Variable, Variable to wrap with the new DataGraphVW
        @param distributedObjects  distributedobjects.DistributedObjects, the DistributedObjects-Instance
        """
        DataGraphVW.__init__(self, variable, distributedObjects)
        self.factory = vwFactory
    
    def getTemplateHandler(self):
        """ returns the TemplateHandler for the html-Template
        @return    datagraph.htmlvariableview.HtmlTemplateHandler, the TemplateHandler for the html-Template
        """
        if (self.templateHandler == None):
            self.templateHandler = PtrVariableTemplateHandler(self, self.distributedObjects)
        return self.templateHandler
    
    def dereference(self):
        """ dereferences the Variable
        @return     datagraph.datagraphvw.DataGraphVW or None,
                    the Wrapper of the dereferenced Variable if the Variable can be dereferenced,
                    None otherwise
        """
        dereferencedVar = self.variable.dereference()
        if (dereferencedVar != None):
            return dereferencedVar.makeWrapper(self.factory)
        else:
            return None
