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


from qt_imports import *

# My libraries
import data_sources.data_source_base_library as DS

#==============================================================================
#%% Constants
#==============================================================================

# Icons
# ============================
ICONS = {"NUMPY_ARRAY":"data_source_table"}


#==============================================================================
#%% Numpy array Datasource setup class
#==============================================================================
# This class is a wrapper for functions that convert data sources to a node
# structure
#
# For each source defined, the wrapper class must have the following functions:
# * to_node(*parameters) : returns a DatasourceNode derivative class
#

class NumpyArray_Datasource(DS.DatasourceCreator):
    """
    Creator class for Numpy Array files

    """

    def __init__(self):
        super(NumpyArray_Datasource, self).__init__()

        # Name
        self.name = 'NumpyArray'

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


            # Make an array node
            node = numpy_array_to_node(name,array)

            # Tag the base node with the creator name
            node.creator = self.name

            return node

        except:
            # TODO : log some kind of error here
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
class Array_Node(DS.DatasourceTable):

    def __init__(self, name, parent=None):
        super(Array_Node, self).__init__(name, parent)
        self.isSource = True
        self._icon_name = ICONS[self.typeInfo()]

        # Link to array
        self._array = None

        # Set this node up as a table
        self.tableWrapper = DatasetTableWrapper

    def typeInfo(self):
        return "NUMPY_ARRAY"

    def data(self):
        """
        Return numpy array
        """
        return self._array


    def setData(self,array):
        """
        Store array in node

        Inputs
        ---------
        array : numpy array

        """
        # TODO : check array dimensions
        #       maybe accept lists
        assert hasattr(array,'shape'),'Array_Node: Not a numpy array'

        self._array = array

        # Summary for value column in tree view
        if len(array.shape)==1 and array.dtype.names is not None:
            self._value = "(%i,%i) array" % (len(array),len(array.dtype.names))
        elif len(array.shape)==1:
            self._value = "(%i,%i) array" % (len(array),1)
        else:
            self._value = "%s array" % str(array.shape)



def numpy_array_to_node(name,array):
    # Make an array node
    arrayNode = Array_Node(name)
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
        assert hasattr(array,'shape'),"DatasetTableWrapper: Not a numpy array - no 'shape' attribute"
        assert hasattr(array,'dtype'),"DatasetTableWrapper: Not a numpy array - no 'dtype' attribute"

        # Store array
        self.array = array

        # Read only flag - for completness with other wrappers
        # - prevents insertions and deletions
        self.readOnly = False

        # Determine if this is a normal array or a recarray
        shape = array.shape

        self.isRecarray = False

        if len(shape)==1 and array.dtype.names is not None:
            self.isRecarray = True


        # Add formatter
        self.formatter = DS.makeNumpyFormatter()




    def columnFormat(self,column):
        c = self.getColumn(column)
        if type(c[0]) == int or type(c[0]) == float:
            return '%.4f'
        else:
            return '%s'




    def rowCount(self):
        return len(self.array)


    def columnCount(self):
        if self.isRecarray:
            return len(self.array.dtype.names)
        else:
            if len(self.array.shape)==1:
                return 1
            else:
                return self.array.shape[1]



    def cell(self,row,col):
        """
        Return contents of array element given row and column

        """

        # TODO : filter infs and NaNs

        if row<self.rowCount() and col<self.columnCount():
            return self.array[row][col]

        return


    def setCell(self,row,col,value):
        """
        Set contents of array element given row and column

        """

        if row<self.rowCount() and col<self.columnCount():
            self.array[row][col] = value



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

        rows2delete = list(range(position,position+rows))
        self.array = np.delete(self.array,rows2delete)




    def columnHeaders(self):
        """
        Return the names of the columns

        For recarrays this is the dtype.names field for normal arrays this
        returns a list of numbers converted to strings

        """

        if self.isRecarray:
            return self.array.dtype.names
        else:
            return [str(n) for n in range(self.columnCount())]



    def getColumn(self,column_index):
        """
        Return a whole column as one numpy array

        """

        # check for valid column index
        if column_index > self.columnCount():
            return

        # Check for recarrays
        if self.isRecarray:
            # Translate index to label
            col_label = self.array.dtype.names[column_index]
            return self.array[col_label]

        else:
            return self.array[:,column_index]


    def getColumnByName(self,column_name):
        """
        Get column using the header name

        """

        headers = self.columnHeaders()

        if column_name not in headers:
            return

        if self.isRecarray:
            return self.array[column_name]

        else:
            return self.array[headers.index(column_name)]








#==============================================================================
#%% Source declaration
#==============================================================================
# Put the names of any Datasource classes in the __sources__ variable. When
# ScopePy loads the source classes into memory it will create any class in
# the __sources__ variable
#

__sources__ = [NumpyArray_Datasource]
