# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 06:46:31 2015

@author: john

Data source selector Panel
==============================
A built-in panel for ScopePy. Central widget for viewing data sources like
arrays, CSV, HDF5, Pandas dataframes etc


Version
==============================================================================
$Revision:: 20                            $
$Date:: 2015-04-11 08:50:53 -0400 (Sat, 1#$
$Author:: john                            $
==============================================================================

"""

#==============================================================================
#%% License
#==============================================================================

"""
Copyright 2015 John Bainbridge

This file is part of ScopePy.

ScopePy is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ScopePy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ScopePy.  If not, see <http://www.gnu.org/licenses/>.
"""


#==============================================================================
#%% Imports
#==============================================================================

# Standard library
import os
import imp
import logging

# Third party libraries
import numpy as np

from PyQt4.QtCore import *
from PyQt4.QtGui import *

# My libraries
import ScopePy_panels as panel
import ScopePy_channel as ch
import ScopePy_widgets as wid

#==============================================================================
#%% Logger
#==============================================================================
# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add do nothing handler
logger.addHandler(logging.NullHandler())

# create console handler and set level to debug
con = logging.StreamHandler()
con.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('[%(asctime)s:%(name)s:%(levelname)s]: %(message)s')

# add formatter to ch
con.setFormatter(formatter)

# add ch to logger
logger.addHandler(con)


#==============================================================================
#%% Constants
#==============================================================================




#==============================================================================
#%% Class definitions
#==============================================================================

class DataSourceSelectorPanel(panel.PanelBase):
    """
    Channel Selector panel
    
    It appears in the sidebar, usually as the current tab
    
    No __init__() required as it must be the same as the base class
    Must reimplement the drawPanel() method
    
    """
    
    def drawPanel(self):
        """
        Draw the GUI elements of the panel
        
        This is a Mandatory function. It will be called by ScopePy when
        the panel is added to a tab.
        
        """
        
        
        # Setup model
        # Take the global sources structure in the API.dataStore 
        self.model = DataSourcesTreeModel(self.API.dataStore.sources)
        self.model.source2node_function = self.API.dataStore.source_creators
        
        # Setup tree view
        self.treeView = QTreeView()
        self.treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView.setSelectionBehavior(QTreeView.SelectItems)
        self.treeView.setItemsExpandable(True)
        self.treeView.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding))
        self.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.openMenu)
        
        self.treeView.setModel(self.model)
        self.treeView.setColumnWidth(0,150)
        self.treeView.setColumnWidth(1,50)
        self.treeView.setWordWrap(True)
        #self.treeView.header().setStretchLastSection(False)
        
        
        
        # Expand the Home node by default
        self.treeView.expand(self.model.index(0,0,QModelIndex()))
        
#        addSourceButton = QPushButton("Add Source")
#        self.connect(addSourceButton,SIGNAL("clicked()"),self.addSource)
        
        deleteSourceButton = QPushButton("Delete Source")
        self.connect(deleteSourceButton,SIGNAL("clicked()"),self.deleteSource)
        
        
        topLabel = QLabel("Data &source selector")
        topLabel.setBuddy(self.treeView)
        
        
        layout = QVBoxLayout()
        layout.addWidget(topLabel)
        layout.addWidget(self.treeView)
        layout.addWidget(deleteSourceButton)
        
        # Setup connections
        self.addCommsAction('update',self.update)
        self.addCommsAction('addSource',self.addSource)
        self.addCommsAction('deleteAllDataSources',self.deleteAllSources)
        
        
        self.setLayout(layout)   
        
        
    def update(self):
        """
        Update tree view
        
        """
        
        self.treeView.update(QModelIndex())
        
        
        
    def openMenu(self, position):
        """
        Context menu for tree view items
        Selects the content of the menu depending on the type of node.
        
        From 
        https://wiki.python.org/moin/PyQt/Creating%20a%20context%20menu%20for%20a%20tree%20view
        """
    
        # Get selected indices, but be careful it returns an index for 
        # each column.
        indexes = self.treeView.selectedIndexes()
        #print("Number of indices selected: %i" % len(indexes))
        
        if len(indexes) == 0:
            return
        
        # TODO: check the correct column
              
        node = self.model.getNode(indexes[0])        
        
        # Get menu from the node if it has one
        menu = node.menu()
        
        # Display menu if it exists
        # To facilitate nodes that can dynamically add children we call the 
        # beginInsertRows/endInsertRows functions from the model. This means
        # that any command executed by the menus can add or remove child node
        # at this row of the TreeView.
        # This saves having to require that DataSourceNodes have references
        # to the DataSourcesTreeModel.
        if menu is not None:
            # Get the position of a new node, in case the menu actions
            # insert one
            nRows = node.childCount()
            
            # Prepare the tree view for the data structure to change
            self.model.beginInsertRows(indexes[0], nRows, nRows)
            
            # Execute a menu action
            menu.exec_(self.treeView.viewport().mapToGlobal(position))    
            
            # Tell tree view everything is done
            self.model.endInsertRows()
        
        
        
    def addSource(self,node,*parameters):
        """
        Add a data source to list of data sources
        
        Inserts as a new child on the Home node
        
        Inputs
        ----------
        node : DatasourceNode derivative
            Node to be added to the tree
            
        *parameters: anything
            any parameters needed to create the source
        
        """
        
        
        if node is None:
            return
            
        # Connect node to API
        # ----------------------------
        node.API = self.API
            
        # Add source to home node
        # ------------------------------
        
        # Get the home node
        homeNode_index = self.model.index(0,0,QModelIndex())
        homeNode = self.model.getNode(homeNode_index)
        position = homeNode.childCount()
        
        self.model.beginInsertRows(homeNode_index, position, position )
        
        homeNode.addChild(node)
        
        self.model.endInsertRows()
        


    def deleteSource(self):
        """
        Delete selected source
        
        """
        
        # Get selected indices, but be careful it returns an index for 
        # each column.
        indexes = self.treeView.selectedIndexes()
        
        if len(indexes) == 0:
            return
        
        # TODO: check the correct column
              
        node = self.model.getNode(indexes[0])
        print("Node = %s, type = %s" % (node.name(),node.typeInfo()))
        
        # Only proceed if a source is selected
        if not node.isSource:
            return
            
        print("Datasource to delete: [%s]" % node.name())
        
        # Delete any table editors associated with this source
        for link in node.links:
            self.API.deleteMainAreaWindow(link)
            
        # Now delete the source from the tree
        parent_index = self.model.parent(indexes[0])
        
        self.model.removeRows(indexes[0].row(),1,parent_index)
        
        
        
    def deleteAllSources(self):
        """
        Clear the Data source selector
        
        """
        
        HomeNode_index = self.model.homeNode_index
        nRows = self.model.rowCount(HomeNode_index)
        
        # Remove data sources in the reverse order
        # this is necessary otherwise the model.index() function gets confused
        for row_index in range(nRows-1,-1,-1):
            # Get index of the node
            index = self.model.index(row_index,0,HomeNode_index)
            
            # Get the actual node
            node = self.model.getNode(index)
            
            # Delete any table editors associated with this source
            try:
                for link in node.links:
                    self.API.deleteMainAreaWindow(link)
            except:
                logger.debug("Data source selector/deleteAllSources: Error when deleting source")
                
                    
            self.model.removeRows(index.row(),1,HomeNode_index)
            
        
        


#==============================================================================
#%% Data sources Tree model
#==============================================================================

# Columns
TREE = 0
ATTRIBUTE_VALUE = 1

class DataSourcesTreeModel(QAbstractItemModel):
    """
    Tree model for representing various data sources:
    HDF5 files, CSV, numpy arrays, pandas datasets
    
    """
    
    
    def __init__(self, root, parent=None):
        """
        INPUTS:
        ---------
        root : Node
            root of the tree
            
            
        parent : QObject
        
        """
        super(DataSourcesTreeModel, self).__init__(parent)
        self._rootNode = root
        
        # Dictionary containing functions for converting different sources
        # into nodes
        # Supplied from API in the selector panel class
        self.source2node_function = {}
        
        

    
    def rowCount(self, parent):
        """INPUTS: QModelIndex"""
        """OUTPUT: int"""
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()

        return parentNode.childCount()

    
    def columnCount(self, parent):
        """INPUTS: QModelIndex"""
        """OUTPUT: int"""
        # 2 column display
        return 2
    
    
    def data(self, index, role):
        """INPUTS: QModelIndex, int"""
        """OUTPUT: QVariant, strings are cast to QString which is a QVariant"""
        
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role ==  Qt.DisplayRole or role ==  Qt.EditRole:
            if index.column() == TREE:
                return node.name()
            elif index.column()==ATTRIBUTE_VALUE:
                return node.value()
            
        # Return any icons that come with each node
        if role ==  Qt.DecorationRole:
            
            # Only use icons in the tree display
            if index.column() == TREE:
                if node.icon is not None:
                    return node.icon


    
    def setData(self, index, value, role= Qt.EditRole):
        """INPUTS: QModelIndex, QVariant, int (flag)"""

        if index.isValid():
            
            if role ==  Qt.EditRole:
                
                node = index.internalPointer()
                node.setName(value)
                
                return True
        return False

    
    
    def headerData(self, section, orientation, role):
        """INPUTS: int, Qt::Orientation, int"""
        """OUTPUT: QVariant, strings are cast to QString which is a QVariant"""
        if role ==  Qt.DisplayRole:
            if section == TREE:
                return "Data source"
            else:
                return "Value"

        
    
    
    def flags(self, index):
        """INPUTS: QModelIndex"""
        """OUTPUT: int (flag)"""
        return  Qt.ItemIsEnabled |  Qt.ItemIsSelectable |  Qt.ItemIsEditable

    

    
    def parent(self, index):
        """INPUTS: QModelIndex"""
        """OUTPUT: QModelIndex"""
        """Should return the parent of the node with the given QModelIndex"""
        
        node = self.getNode(index)
        parentNode = node.parent()
        
        if parentNode == self._rootNode:
            return  QModelIndex()
        
        return self.createIndex(parentNode.row(), 0, parentNode)
        
    
    def index(self, row, column, parent):
        """INPUTS: int, int, QModelIndex"""
        """OUTPUT: QModelIndex"""
        """Should return a QModelIndex that corresponds to the given row, column and parent node"""
        
        parentNode = self.getNode(parent)

        childItem = parentNode.child(row)


        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return  QModelIndex()



    
    def getNode(self, index):
        """CUSTOM"""
        """INPUTS: QModelIndex"""
        
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
            
        return self._rootNode

    
    # TODO : insert and remove rows functions not implemented yet
    
    def insertRows(self, position, rows, parent= QModelIndex()):
        """INPUTS: int, int, QModelIndex"""
        
        parentNode = self.getNode(parent)
        
        self.beginInsertRows(parent, position, position + rows - 1)
        
        for row in range(rows):
            
            childCount = parentNode.childCount()
            childNode = DatasourceNode("untitled" + str(childCount))
            success = parentNode.insertChild(position, childNode)
        
        self.endInsertRows()

        return success
    
    

    
    def removeRows(self, position, rows, parent= QModelIndex()):
        """INPUTS: int, int, QModelIndex"""
        
        parentNode = self.getNode(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)
        
        for row in range(rows):
            success = parentNode.removeChild(position)
            
        self.endRemoveRows()
        
        return success
        
    # -------------------------------------------------------------------------
    # Custom functions
    # -------------------------------------------------------------------------
    @property
    def homeNode_index(self):
        """
        Return the home node as a QModelIndex
        
        Output
        --------
        index : QModelIndex
        
        """
        return self.index(0,0,QModelIndex())
        
        
    @property
    def homeNode(self):
        """
        Return the Home node itself
        
        Output
        -------
        node : DatasourceNode()
        
        """
        
        return self.getNode(self.homeNode_index)
        


    def addSource(self,source_type,*parameters):
        """
        Add a data source to list of data sources
        
        Inserts as a new child on the Home node
        
        Inputs
        -------
        source_type : str
            label for the type of source
            
        *parameters: anything
            any parameters needed to create the source
        
        """
        
        return 
        
        
            
        # Call specific function for this source
        # ---------------------------------------
        
        # Make node from the source
        node = self.source2node_function[source_type](*parameters)
        
        if node is None:
            return
            
        # Add source to home node
        # ------------------------------
        
        # Get the home node
        homeNode_index = self.homeNode_index
        homeNode = self.getNode(homeNode_index)
        position = homeNode.childCount()
        
        self.beginInsertRows(homeNode_index, position, position )
        
        homeNode.addChild(node)
        
        self.endInsertRows()

#==============================================================================
#%% Help docs
#==============================================================================

help_doc = """

%*% Data sources browser

++<
This panel displays "data sources" that have been loaded into ScopePy. A data source
is a container for tabular data. The data in data source can usually be viewed
in a table, via the table editor panel. From here it can be selected and made into
channels for plotting.
>++

++<
Data sources can be files, data sent over the network, or created programmatically.
Each different type of source appears as a different branch in the tree diagram.
Some data sources, e.g. HDF5 files, contain multiple tables or datasets. These
can be accessed by expanding sub branches on the tree. Other sources, e.g. CSV files
have only one entry on the tree.
>++

%*% Tree diagram description
++<
The tree diagram display has a root node, called 'Home'. When a data source is
accessed, either by loading a file, receiving a network packet, or being created
from a script, then a new branch will appear under the Home node, with an icon
that represents the type of source.
>++

++<
Depending on the type of source, some branches will have sub branches. These can
be either
--<

--+ Tag: Usually a text string contained in the file. Its value is displayed in the left hand column.
--+ Table: A table of numeric data that can be opened using the table editor by right clicking.
--+ Folder: A sub folder of the data source
>--
>++



"""


#==============================================================================
#%% Panels to export
#==============================================================================
# Put any panels to be imported from this file here
# Note: this must go after the class definitions
#
# Panels are passed in a dictionary where:
#   key = the name to be used on menus
#   value = class reference

__panels__ = {"&Data Source Selector":panel.PanelFlags(DataSourceSelectorPanel,
                                                  open_on_startup=True,
                                                  single_instance=True,
                                                  on_panel_menu=False,
                                                  location='sidebar',
                                                  API_attribute_name='dataSourceSelector',
                                                  docs=help_doc)}
