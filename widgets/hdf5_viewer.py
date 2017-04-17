# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 14:19:25 2015

@author: john

HDF5 File viewer widget
===============================


Version
==============================================================================
$Revision:: 75                            $
$Date:: 2015-09-13 12:13:04 -0400 (Sun, 1#$
$Author::                                 $
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
import os,sys
import imp
import logging

# Third party libraries
import numpy as np
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import h5py

# My libraries
#from ScopePy_channel import BranchNode

#==============================================================================
#%% Constants
#==============================================================================



#======================================================================
#%% Tree handling classes
#======================================================================

# Taken from Rapid GUI Programming with Python and QT, Mark Summerfield

KEY, NODE = range(2)


class BranchNode(object):

    def __init__(self, name, parent=None):
        super(BranchNode, self).__init__()
        self.name = name
        self.parent = parent
        self.userData = None
        self.children = []


    def __lt__(self, other):
        if isinstance(other, BranchNode):
            return self.orderKey() < other.orderKey()
        return False

    def __str__(self):
        return "Branch node [%s]" % self.name

    def orderKey(self):
        return self.name.lower()


    def toString(self):
        return self.name


    def __len__(self):
        return len(self.children)


    def childAtRow(self, row):
        assert 0 <= row < len(self.children)
        return self.children[row][NODE]
        

    def rowOfChild(self, child):
        for i, item in enumerate(self.children):
            if item[NODE] == child:
                return i
        return -1
        
        
    def indexOfChildName(self,child_name):
        
        search_key = child_name.lower()
        
        for i, item in enumerate(self.children):
            if item[KEY] == search_key:
                return i
        return -1
        
    def getChildren(self):
        """
        Return a list of children
        """
        
        if not self.children:
            return None
            
            
        children = []
        for key,node in self.children:
            children.append(key)
            
        return children
            


    def childWithKey(self, key):
        if not self.children:
            return None
            
         # TODO Commented out this code because it doesn't work very well
         # when using multi-threaded server
            
#        # Causes a -3 deprecation warning. Solution will be to
#        # reimplement bisect_left and provide a key function.
#        i = bisect.bisect_left(self.children, (key, None))
#        if i < 0 or i >= len(self.children):
#            return None
#        if self.children[i][KEY] == key:
#            return self.children[i][NODE]
#        return None
        
        children = self.getChildren()
        
        if key in children:
            index = children.index(key)
            return self.children[index][NODE]
        else:
            return None


    def insertChild(self, child):
        child.parent = self
        #bisect.insort(self.children, (child.orderKey(), child))
        # don't want children stored in alphabetical order
        # just the order they come in
        self.children.append((child.orderKey(), child))
        
        
    
    def deleteChild(self,child_name):
        """
        Delete a child from branch
        
        """
        
        # Get index of child
        index = self.indexOfChildName(child_name)
        
        if index == -1:
            return
         
        # Remove from list of children
        self.children.pop(index)
        
        


    def hasLeaves(self):
        if not self.children:
            return False
        return isinstance(self.children[0], LeafNode)
        
        
    def asRecord(self):
        record = []
        branch = self.parent
        while branch is not None:
            record.insert(0, branch.toString())
            branch = branch.parent
        assert record and not record[0]
        record = record[1:]
        return record + self.fields


class LeafNode(object):

    def __init__(self, fields, parent=None):
        super(LeafNode, self).__init__()
        self.parent = parent
        self.fields = fields
        
    def __str__(self):
        string = "LeafNode\n\tParent = %s\n\tFields" % self.parent.name
        return string


    def orderKey(self):
        return self.fields[0].lower()


    def toString(self, separator="\t"):
        return separator.join(self.fields)


    def __len__(self):
        return len(self.fields)


    def asRecord(self):
        record = []
        branch = self.parent
        while branch is not None:
            record.insert(0, branch.toString())
            branch = branch.parent
        assert record and not record[0]
        record = record[1:]
        return record + self.fields


    def field(self, column):
        assert 0 <= column <= len(self.fields)
        return self.fields[column]
        
    def setField(self,column,value):
        assert 0 <= column <= len(self.fields)
        self.fields[column] = value
        
        

#======================================================================
#%% Viewer Tree class
#======================================================================


TREE = 0
SETTINGS = 1

class ViewerTreeModel(QAbstractItemModel):

    def __init__(self, filename, parent=None):
        super(ChannelTreeModel, self).__init__(parent)
        self.columns = 2
        self.root = BranchNode("/")
        self.headers = ["Directory","Attributes"]
        
        # Reference to channel dictionary
        #  where all the channel data is held
        self.channelDict = channelDict
        
        self.filename = filename
        self.hdf5_file = None
        
        #self.loadFile()
        
        
    
    def loadFile(self,filename=None):
        """
        Load HDF5 file
        
        """
        
        if not filename:
            filename = self.filename
            
        assert filename is not None,"ViewerTreeModel: filename is invalid"
        
        
        
        try:
            # Open filename for read/write (default option)
            # TODO : temporarily the file is opend as read-only
            self.hdf5_file = h5py.File(filename,'r')
            
        except IOError:
            raise IOError("ViewerTreeModel: Failed to load HDF5 file [%s]" % filename)
            
        
        
    def addBranch(self,parent,call_reset=False):
        """
        Add the next level from a given branch

        Inputs:
        ---------
        parent : BranchNode
        
        """
        # Get HDF5 path to parent
        parent_path = self.getHdf5Path(parent.name)
        
        # Get the parent branches children
        # assume this is a list of strings
        child_list = self.getHdf5Children(parent_path)
        
        
        
        # Add children if they don't already exist
        for child in child_list:
            key = child.lower()
            branch = parent.childWithKey(key)
            
            if branch is None:
                # Add a branch if this is a HDF5 group, otherwise add as a leaf
                if self.isGroup(parent_path+"/"+child):
                    branch = BranchNode(child)
                else:
                    # TODO: Leaf class needs some adjustment to define fields
                    branch = LeafNode([child,'dataset'])
                
                # Add the branch
                parent.insertChild(branch)
                
                
                
        # TODO add attributes as LeafNodes here
                
                
        if call_reset:
            self.reset()
        
        

    def isGroup(self,hd5_path):
        """
        Check if a path is a HDF5 group or not
        
        Output
        ------
        bool
        """
        
        return hasattr(self.hdf5_file[hd5_path],'keys')
        

    def getHdf5Attributes(self,hdf5_path):
        """
        Get a list of attributes at the given path
        
        Output
        -------
        attr_list : list of str
            List of the names of the attributes
            
        """
        
        try:
            attr_list = list(self.hdf5_file[hdf5_path].attrs.keys())
            return attr_list
        except:
            return None
        
        

    def getHdf5Children(self,hdf5_path):
        """
        Find out if this path has any children
        
        Output
        --------
        child_list : list of str
            List of children as strings
        """

        assert hdf5_path,"getHdf5Children:Path is None"

        try:        
            child_list = list(self.hdf5_file[hdf5_path].keys())
            return child_list
            
        except:
            # No children found
            return None
            
            
        
    
    
    def getHdf5Path(self,node):
        """
        Track back from the given node to the root and find the complete
        path
        
        Output
        ---------
        path : str
            HDF5 path e.g '/Data/Sweep/Values'
            
        """
        
        node_list = node.asRecord(node)
        
        return "/".join(node_list)
        
        
    
    def asRecord(self, index):
        leaf = self.nodeFromIndex(index)
        if leaf is not None and isinstance(leaf, LeafNode):
            return leaf.asRecord()
        return []    


       

    def rowCount(self, parent):
        node = self.nodeFromIndex(parent)
        if node is None or isinstance(node, LeafNode):
            return 0
        return len(node)


    def columnCount(self, parent):
        return self.columns


    def data(self, index, role):
        """ Return data from the model for different roles
        """
        
        # Get the node
        node = self.nodeFromIndex(index)
        assert node is not None
        
        # Deal with non-display roles
        # ================================================
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignTop|Qt.AlignLeft)
              
        
        if role == Qt.ToolTipRole :
            pass        
                    
        if role == Qt.StatusTipRole:
            pass
                
        
        # Display role from here on
        # ==================================================================
                    
        if role != Qt.DisplayRole:
            return None          
        
        if isinstance(node, BranchNode):
            
            if index.column() == 0:
                return node.toString()
            
            
        return node.field(index.column())



    def headerData(self, section, orientation, role):
        if (orientation == Qt.Horizontal and
            role == Qt.DisplayRole):
            assert 0 <= section <= len(self.headers)
            return self.headers[section]
        return None


    def index(self, row, column, parent):
        assert self.root
        branch = self.nodeFromIndex(parent)
        assert branch is not None
        return self.createIndex(row, column,
                                branch.childAtRow(row))


    def parent(self, child):
        node = self.nodeFromIndex(child)
        if node is None:
            return QModelIndex()
        parent = node.parent
        if parent is None:
            return QModelIndex()
        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex()
        row = grandparent.rowOfChild(parent)
        assert row != -1
        return self.createIndex(row, 0, parent)


    def nodeFromIndex(self, index):
        # Magic function that returns a node from an index
        # index.internalPointer returns the node
        # not exactly sure where from
        return (index.internalPointer()
                if index.isValid() else self.root)
                    
    def flags(self,index):
        """ Function that returns whether items are 
        selectable, editable or read-only
        """
        
        # Check for invalid index
        if not index.isValid():
            return Qt.ItemIsEnabled
        
        # What type of node is this?
        node = self.nodeFromIndex(index)
        
        
        # Branch node:
        if isinstance(node,BranchNode):
            # Separate the two columns
            # even though we return the same flags, this allows
            # them to be separately selected
            if index.column() == 0:
                return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable
                
            if index.column() == 1:
                return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable
            
        # Leaf node :
        #  Only second column is editable and selectable and then only for
        #  first 2 rows : x and y axis names
        if isinstance(node,LeafNode):
            
                
            if index.column() == 1:
                return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable
            else:
                return Qt.ItemIsEnabled
                
                
#    def setData(self,index,value,role=Qt.EditRole):
#        """ 
#        Required method for changing data in tree model
#        """
#        
#        if index.isValid() and 0<= index.row() < len(self.root):
#            if DEBUG:
#                print("\n\nSetting data")
#                print("\tValue = %s" % type(value))
#                
#            if role == Qt.EditRole:
#                # Get the node
#                node = self.nodeFromIndex(index)
#                column = index.column()
#                
#                if DEBUG:
#                    print("Node = %s : column = %d" %(type(node),column))
#                
#                # Edit channel name and line style
#                if isinstance(node,BranchNode):
#                    if column == TREE:
#                        # Update channel dictionary with new name
#                        self.channelDict[value] = self.channelDict.pop(node.name)
#                        
#                        # Update tree
#                        node.name = value                        
#                        
#                        
#                    elif column == LINESTYLE:
#                        # TODO : Does this actually work?
#                        
#                        lineStyles = value
#                        
#                        # Update line styles into channel dict
#                        self.channelDict[node.name].plot_lineStyle = lineStyles
#                        
#                        
#                    
#                # Edit channel x and y axis names
#                elif isinstance(node,LeafNode):
#                    # Get channel name for referencing in channel dictionary
#                    channel = node.parent.name
#                    
#                    # edit x axis
#                    if column == XAXIS:
#                        # Update in channel dictionary
#                        self.channelDict[channel].setAxisName('x',value)
#                        
#                        # Update in model
#                        node.setField(XAXIS,value)
#                        
#                    # edit y axis
#                    elif column == YAXIS:
#                       # Update in channel dictionary
#                        self.channelDict[channel].setAxisName('y',value)
#                        
#                        # Update in model
#                        node.setField(YAXIS,value)
#                        
#                    
#                self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,index)
#                return True
#                
#        return False
                    
                
                
#    def getSelectedChannelsFromIndex(self,modelIndexList):
#        """ Get any channel names that have been selected
#        
#        Go through the selected items list, ignore anything that isn't a branch node
#        If it is a branch node then extract the channel name.
#        Return all the channel names in a list
#        
#        Output
#        ------
#        channelList = list of channel names selected
#        """
#        # Check the list is not empty
#        if not modelIndexList:
#            return
#            
#        channelList = []
#        
#        for index in modelIndexList:
#            node = self.nodeFromIndex(index)
#            
#            # Add to list if the node is a branch and the first column
#            # is selected
#            if isinstance(node,BranchNode):
#                if index.column() == TREE:
#                    channelList.append(node.name)
#                
#        return channelList
#            
     


#==============================================================================
#%% Viewer Tree widget
#==============================================================================       
class ViewerTreeWidget(QTreeView):
    """
    Widget for viewing HDF5 file structure in a tree view
    
    """
    def __init__(self,filename,parent=None):
        """
        Inputs
        ------------
        filename : str
            HDF5 file
        """
        super(ViewerTreeWidget,self).__init__(parent)
        
        self.setSelectionBehavior(QTreeView.SelectItems)
        self.setUniformRowHeights(True)
        
        model = ViewerTreeModel(filename)
        self.setModel(model)
        
        # Connect to file
        model.loadFile()
        
        # Setup first level of tree
        model.addBranch(model.root,call_reset=True)

        # Connections        
        self.connect(self,SIGNAL("activated(QModelIndex)"),self.activated)
        self.connect(self,SIGNAL("expanded(QModelIndex)"),self.expanded)
        
        
        
    def activated(self,index):
        # TODO : Think this is sending a path to the model
        self.emit(SIGNAL("activated"),self.model().asRecord(index))
        
        
    def expanding(self,index):
        # TODO : Need to populate tree here I think!
        self.activated(index)


#==============================================================================
#%% MainForm for testing
#==============================================================================
class MainForm(QDialog):
    """ Class for testing graph widgets
    """

    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)

        filename = '/home/john/Documents/Python/Misc/work_related/test_Meas.hd5'

        

        self.tree = ViewerTreeWidget(filename)
        
        #self.table.setItemDelegate(TableEditorDelegate(self))
        
        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        
        
        self.setLayout(layout)
        
        
        
        
        


#=============================================================================
#%% Code runner
#=============================================================================


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = MainForm()
    rect = QApplication.desktop().availableGeometry()
    print("Screen rect",rect)
    form.resize(int(rect.width() * 0.4), int(rect.height() * 0.5))
    #form.resize(800, 600)
    form.show()
    app.exec_()