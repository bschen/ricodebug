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

""" @package datagraph.datagraphcontroller    the DataGraphController """

from PyQt4.QtCore import QObject, SIGNAL, Qt
from PyQt4.QtGui import QDockWidget
from datagraphvwfactory import DataGraphVWFactory
from datagraphview import DataGraphView
from variables.variablelist import VariableList
from pointer import Pointer

class DataGraphController(QObject):
    """ the Controller for the DataGraph """

    def __init__(self, distributedObjects):
        """ Constructor <br>
            Creates a DataGraphView, a DataGraphVWFactory and a VariableList <br>
            Listens to the following Signals: SignalProxy::insertDockWidgets() and SignalProxy::cleanupModels()
        @param distributedObjects    distributedobjects.DistributedObjects, the DistributedObjects-Instance
        """
        QObject.__init__(self)
        
        # controllers
        ## @var distributedObjects
        # distributedobjects.DistributedObjects, the DistributedObjects-Instance
        self.distributedObjects = distributedObjects
        ## @var signalProxy
        # signalproxy.SignalProxy, the SignalProxy-Instance from the DistributedObjects
        self.signalProxy = distributedObjects.signal_proxy
        ## @var debug_controller
        # debugcontroller.DebugController, the DebugController-Instance from the DistributedObjects
        self.debug_controller = distributedObjects.debug_controller
        ## @var variablePool
        # variables.variablepool.VariablePool, the variablePool-Instance from the DistributedObjects
        self.variablePool = distributedObjects.variable_pool
        
        # views
        ## @var data_graph_view
        # datagraph.datagraphview.DataGraphView, private, self-created DataGraphView <br>
        # GUI-Element that shows the DataGraphView
        self.data_graph_view = DataGraphView(None, self)
        
        # models
        ## @var vwFactory
        # datagraph.datagraphvwfactory.DataGraphVWFactory, private, self-created DataGraphVWFactory
        self.vwFactory = DataGraphVWFactory(self.distributedObjects)
        ## @var variableList
        # variables.variablelist.VariableList, private, self-created VariableList
        self.variableList = VariableList(self.vwFactory, self.distributedObjects)
        
        self.pointerList = []
        
        #register with session manager to save Graph
        self.signalProxy.emitRegisterWithSessionManager(self, "Graph")
        
        # connect signals
        #QObject.connect(self.variableList, SIGNAL('reset()'), self.repaintDataGraph)
        QObject.connect(self.signalProxy, SIGNAL('insertDockWidgets()'), self.insertDockWidgets)
        QObject.connect(self.signalProxy, SIGNAL('cleanupModels()'), self.clearDataGraph)
        
    def insertDockWidgets(self):
        """ adds the Datagraph-DockWidget to the GUI <br>
            this function is connected to the signal SignalProxy::insertDockWidgets() """
        self.dataGraphDock = QDockWidget("Graph")
        self.dataGraphDock.setObjectName("DataGraphView")
        self.dataGraphDock.setWidget(self.data_graph_view)
        self.signalProxy.addDockWidget(Qt.LeftDockWidgetArea, self.dataGraphDock, True)
        
    def getVarByWatch(self, watch):
        """
        @param watch    string, the watch-Expression of the desired Variable
        @return         variables.variable.Variable, the desired Variable with var.getExp() == watch
        """ 
        for var in self.variableList:
            if var.getExp() == watch:
                return var
        # in case that no var was found, return None
        return None
    
    def addWatch(self, watch, xPos=0, yPos=0):
        """ adds the Variable watch to the VariableList and its wrapper to the DataGraph
        @param watch    variables.variable.Variable, the Variable to watch to add
        @param xPos     Integer, the X-Coordinate of the Position where to add the Variable
        @param yPos     Integer, the Y-Coordinate of the Position where to add the Variable
        """
        vw = self.variableList.addVarByName(watch)
        self.addVar(vw, xPos, yPos, False)
    
    def addVar(self, varWrapper, xPos=0, yPos=0, addVarToList=True):
        """ adds the given VariableWrapper varWrapper to the DataGraph and - if addVarToList is true -
            also to the VariableList
        @param varWrapper      variables.variablewrapper.VariableWrapper, the VariableWrapper to add
        @param xPos            Integer, the X-Coordinate of the Position where to add the VariableWrapper
        @param yPos            Integer, the Y-Coordinate of the Position where to add the VariableWrapper
        @param addVarToList    Boolean, tells if varWrapper should be added to the VariableList too
        """
        varWrapper.setXPos(xPos)
        varWrapper.setYPos(yPos)
        self.data_graph_view.addItem(varWrapper.getView())
        if addVarToList == True:
            self.variableList.addVar(varWrapper)
        QObject.connect(varWrapper, SIGNAL('replace(PyQt_PyObject, PyQt_PyObject)'), self.replaceVariable)
    
    def replaceVariable(self, pendingVar, newVar):
        """ replaces existing variable in list with new one
        @param pendingVar    variables.variable.Variable, the pending Variable to replace with newVar
        @param newVar        variables.variable.Variable, the new Variable pendingVar is replaced with
        """
        self.removeVar(pendingVar)
        newVW = newVar.makeWrapper(self.vwFactory)
        self.addVar(newVW, pendingVar.getXPos(), pendingVar.getYPos())
        #for pointer in pendingVar.getView().getIncomingPointers():
        #    self.addPointer(pointer.getFromView(), newVW.getView())
        #for pointer in pendingVar.getView().getOutgoingPointers():
        #    self.addPointer(newVW.getView(), pointer.getToView())
    
    def removeVar(self, varWrapper):
        """ removes the given varWrapper from the DataGraphView and the PointerList
        @param varWrapper    variables.variablewrapper.VariableWrapper, the VariableWrapper to remove
        """
        varWrapper.getView().onDelete()
        self.variableList.removeVar(varWrapper)
        self.data_graph_view.removeItem(varWrapper.getView())
    
    def addPointer(self, fromView, toView):
        """ fromView and toView are QGraphicsWebViews
        @param fromView  datagraph.htmlvariableview.HtmlVariableView, starting point of the Pointer  
        @param toView    datagraph.htmlvariableview.HtmlVariableView, end point of the Pointer
        """
        pointer = Pointer(None, fromView, toView, self.distributedObjects)
        self.data_graph_view.addItem(pointer)
        self.pointerList.append(pointer)
    
    def removePointer(self, pointer):
        """ removes the given pointer from the DataGraphView and the PointerList
        @param pointer    datagraph.pointer.Pointer, pointer to remove
        """
        self.data_graph_view.removeItem(pointer)
        self.pointerList.remove(pointer)
    
    def clearDataGraph(self):
        """ clears the DataGraphView and the VariableList <br>
            this function is connected to the signal SignalProxy::cleanupModels()
        """
        self.variableList.clear()
        self.data_graph_view.clear()
    
    def saveSession(self, xmlHandler):
        """ Insert session info to xml file
        @param xmlHandler    sessionmanager.XmlHandler, handler to write to the session-xml-file
        """
        dgWatches = xmlHandler.createNode("GraphWatches")
        for vw in self.variableList:
            xmlHandler.createNode("Watch", dgWatches, { 'expression': vw.getExp(), 'xPos': vw.getXPos(), 'yPos': vw.getYPos()})
        #dgPointers = xmlHandler.createNode("Pointers")
        #for pointer in self.pointerList:
        #    xmlHandler.createNode("Pointer", dgPointers, { 'expFrom': pointer.fromView.var.getExp(), 'expTo': pointer.toView.var.getExp() })
             
    def loadSession(self, xmlHandler): 
        """ load session info to xml file
        @param xmlHandler    sessionmanager.XmlHandler, handler to read from the session-xml-file
        """
        dgParent = xmlHandler.getNode("GraphWatches")
        if dgParent != None:
            childnodes = dgParent.childNodes()
            for i in range(childnodes.size()):
                attr = xmlHandler.getAttributes(childnodes.at(i))
                self.addWatch(attr["expression"], int(attr["xPos"]), int(attr["yPos"]))
        #dgParent = xmlHandler.getNode("Pointers")
        #if dgParent != None:
        #    childnodes = dgParent.childNodes()
        #    for i in range(childnodes.size()):
        #        attr = xmlHandler.getAttributes(childnodes.at(i))
        #        fromVar = self.getVarByWatch(attr["expFrom"])
        #        fromView = None
        #        if fromVar != None:
        #            fromView = fromVar.getView()
        #        toVar = self.getVarByWatch(attr["expFrom"])
        #        toView = None
        #        if toVar != None:
        #            toView = toVar.getView()
        #        if (fromView != None and toView != None):
        #            self.addPointer(fromView, toView)
