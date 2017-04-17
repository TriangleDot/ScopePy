# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 13:03:01 2015

@author: john


ScopePy HDF5 Datasource  class
===============================
class for managing reading HDF5 files into the source selector


Version
==============================================================================
$Revision:: 77                            $
$Date:: 2015-09-26 08:48:15 -0400 (Sat, 2#$
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
import os


# Third party libraries
import numpy as np
import pandas as pd


from PyQt4.QtCore import *
from PyQt4.QtGui import *

# My libraries
import data_sources.data_source_base_library as DS

#==============================================================================
#%% Constants
#==============================================================================

# Icons
# ============================
ICONS = {"DATAFRANE":"data_source_table"}
              

#==============================================================================
#%% Pandas Dataframe Datasource setup class
#==============================================================================
# This class is a wrapper for functions that convert data sources to a node
# structure
#
# For each source defined, the wrapper class must have the following functions:
# * to_node(*parameters) : returns a DatasourceNode derivative class 
#

class Dataframe_Datasource(DS.DatasourceCreator):
    """
    Creator class for Numpy Array files
    
    """
    
    def __init__(self):
        super(Dataframe_Datasource, self).__init__()
        
        # Name
        self.name = 'Dataframe'
        
        # It's a file
        self.isFile = False
        
        # File extensions are
        self.fileTypes = []
        
    
    def toNode(self,array=np.zeros(5,[('x',float),('y',float)]),name='array'):
        """
        Convert Numpy Array file into a DatasourceNode derivative class
        
        Input
        --------
        array : numpy array
            recarray or normal array
            
        Output
        ---------
        node : Array_Node class instance
        
        """
        # Validate filename
        # ------------------------
        if not hasattr(array,'shape') and not hasattr(array,'dtype'):
            return
            
        # Open file
        # ------------------
        try:
            
            
            # Make a node structure
            node = dataframe_to_node(name,array)
            
            # Tag the base node with the creator name
            node.creator = self.name
            
            return node
            
        except Exception as ec:
            # TODO : log some kind of error here
            print("Dataframe failed to make node: ",ec)
            return None
            
            
            
    def file_open(self,filename):
        """
        Required class
        
        Inputs
        --------
        filename : str
            full path/filename
            
        Outputs
        -----------
        source_node : DatasourceNode or derivative
            HDF5 file structure converted to a node structure.
            
        """
        # TODO all for storing and opening arrays
        pass
    
    
    
    def makeSource(self,name,initial_data=None):
        """
        Make a numpy array data source node
        
        Inputs
        --------
        name : str
        
        initial_data : numpy array or None
            initial data to be populated into array
        
        Outputs
        ---------
        node : Array_Node class instance
            Node class for inserting in Data source selector panel
        """
        
        if initial_data is None:
            initial_data = np.zeros(5,[('x',float),('y',float)])
            
        node = self.toNode(initial_data,name)
        
        return node
        
        
#==============================================================================
#%% Numpy array Node
#==============================================================================
class Dataframe_Node(DS.DatasourceTable):
    
    def __init__(self, name, parent=None):
        super(Dataframe_Node, self).__init__(name, parent)
        self.isSource = True
        self._icon_name = ICONS[self.typeInfo()]
        
        # Link to array
        self._array = None
        
        # Set this node up as a table
        self.tableWrapper = DatasetTableWrapper
        
    def typeInfo(self):
        return "DATAFRANE"
        
    def data(self):
        """
        Return dataframe
        """
        return self._array
        
        
    def setData(self,array):
        """
        Store array in node
        
        Inputs
        ---------
        array : dataframe
        
        """
        # TODO : check array dimensions
        #       maybe accept lists
        assert hasattr(array,'columns'),'Dataframe_Node: Not a dataframe'
        
        self._array = array
        
        # Summary for value column in tree view
        self._value = "(%i,%i) Dataframe" % (len(array),len(array.columns))
        
        
        
def dataframe_to_node(name,array):
    # Make an array node
    arrayNode = Dataframe_Node(name)
    arrayNode.setData(array)
    
    return arrayNode   






    
#==============================================================================
#%% Dataset
#==============================================================================    

class DatasetTableWrapper(DS.BaseDatasetTableWrapper):
    """
    Wrapper for HDF5/numpy array datasets when sending to the TableEditor
    
    Makes standard functions for accessing rows and columns, inserting, 
    deleting
    
    """
    
    def __init__(self,array):
        """
        Create wrapper with the HDF5/numpy array
        
        Inputs
        ---------
        array : HDF5/numpy array
            e.g. Meas['Data/Measurement/dataset1']
        
        """
        
        # Initialise base class to get standard properties
        super(DatasetTableWrapper, self).__init__()
        
        # Check this is a numpy array
        assert hasattr(array,'shape'),"DatasetTableWrapper: Not a Dataframe - no 'shape' attribute"
        assert hasattr(array,'columns'),"DatasetTableWrapper: Not a Dataframe - no 'columns' attribute"
        
        # Store array
        self.array = array
        
        # Read only flag - for completness with other wrappers
        # - prevents insertions and deletions
        self.readOnly = False
        

        # Add formatter
        self.formatter = DS.makeNumpyFormatter()
            
        
    def rowCount(self):
        return len(self.array)
        
        
    def columnCount(self):
        """
        Return number of columns plus one for the index
        """
        return len(self.array.columns)+1       
            
        
        
    def cell(self,row,col):
        """
        Return contents of array element given row and column
        
        """
        
        # TODO : filter infs and NaNs
        
        # Account for the index
        if col==0:
            return self.array.index[row]
        
        if row<self.rowCount() and col<self.columnCount():
            return self.array.iloc[row,col-1]
        
        return
        
        
    def setCell(self,row,col,value):
        """
        Set contents of array element given row and column
        
        """
        
        # Don't allow editing of index
        if col == 0:
            return
        
        if row<self.rowCount() and col<self.columnCount():
            self.array.iloc[row,col-1] = value
            
            
    
    def insertRows(self,position,rows=1):
        """
        Insert a set of new rows, set to zero
        
        Inputs
        ---------
        position : int
            row index where new rows will be inserted
            
        rows : int
            Number of rows to be inserted
            
        """
        
        # TODO: can this be done with a Dataframe?
        dtype = self.array.dtype
        self.array = np.insert(self.array,position,np.zeros(rows,dtype))
        
        
        
    def removeRows(self,position,rows=1):
        """
        Remove a set of rows
        
        Inputs
        ---------
        position : int
            row index where rows will be removed
            
        rows : int
            Number of rows to be deleted
            
        """
        # TODO: can this be done with a Dataframe?
        
        rows2delete = list(range(position,position+rows))
        self.array = np.delete(self.array,rows2delete)
                
    
        
        
    def columnHeaders(self):
        """
        Return the names of the columns
        
        For recarrays this is the dtype.names field for normal arrays this
        returns a list of numbers converted to strings
        
        """
        
        return ['Index'] + self.array.columns.tolist()
        
        
        
    def columnFormat(self,column):
        """
        Return column format string
        
        Inputs
        --------
        column : int
            column number
            
        Outputs
        --------
        format : str
            format string such as "%.4f'. This should be appropriate to the
            data in the column.
            
        """
        
        if column==0:
            dtype = self.array.index.dtype
        else:
            dtype = self.array.iloc[:,column-1].dtype
        
        if dtype==np.dtype('O'):
            # Probably a string
            return "%s"
            
        elif dtype.name.startswith('datetime'):
            return "%s"
            
        # Default float format    
        return '%.4f'
        
            
            
            
    def getColumn(self,column_index):
        """
        Return a whole column as one numpy array
        
        """
        # check for valid column index
        if column_index > self.columnCount():
            return
            
            
        if column_index == 0:
            return self.array.index.values
                    
            
        return self.array.iloc[:,column_index-1].values


    
    def getColumnByName(self,column_name):
        """
        Get column using the header name
        
        """
        
        headers = self.columnHeaders()
        
        if column_name not in headers:
            return
            
        return self.array[column_name]
            
       

            


    
    
#==============================================================================
#%% Source declaration
#==============================================================================
# Put the names of any Datasource classes in the __sources__ variable. When
# ScopePy loads the source classes into memory it will create any class in
# the __sources__ variable
# 

__sources__ = [Dataframe_Datasource]

