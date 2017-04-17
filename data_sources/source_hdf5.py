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
import h5py

from PyQt4.QtCore import *
from PyQt4.QtGui import *

# My libraries
import data_sources.data_source_base_library as DS

#==============================================================================
#%% Constants
#==============================================================================

# Icons
# ============================
HDF5_icons = {"HDF5_FILE":"data_source_HDF5",
              "HDF5_GROUP":"data_source_folder",
              "HDF5_DATASET":"data_source_table",
              "HDF5_ATTRIBUTE":"data_source_attribute"}
              

#==============================================================================
#%% HDF5 Datasource setup class
#==============================================================================
# This class is a wrapper for functions that convert data sources to a node
# structure
#
# For each source defined, the wrapper class must have the following functions:
# * to_node(*parameters) : returns a DatasourceNode derivative class 
#

class HDF5_Datasource(DS.DatasourceCreator):
    """
    Creator class for HDF5 files
    
    """
    
    def __init__(self):
        super(HDF5_Datasource, self).__init__()
        
        # Name
        self.name = 'hdf5'
        
        # It's a file
        self.isFile = True
        
        # File extensions are
        self.fileTypes = ['h5','hd5','hdf5','hdf']
        
    
    def toNode(self,filename):
        """
        Convert HDF5 file into a DatasourceNode derivative class
        
        Input
        --------
        filename : str
            path/filename of HDF5 file
            
        Output
        ---------
        node : HDF5_File class instance
        
        """
        # Validate filename
        # ------------------------
        if not os.path.exists(filename):
            return
            
        # Open file
        # ------------------
        try:
            hdf5_file = h5py.File(filename,'r',driver='stdio')
            
            # Make an HDF5 file structure
            node = hdf5_tree(hdf5_file)
            node.sourceFile = filename
            
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
        
        return self.to_node(filename)
        
        
    

#==============================================================================
#%% HDF5 Nodes
#==============================================================================
# Node types for HDF5 files and their components

class HDF5_File(DS.DatasourceNode):
    
    def __init__(self, name, parent=None):
        super(HDF5_File, self).__init__(name, parent)
        self.isSource = True
        self._icon_name = HDF5_icons[self.typeInfo()]
        
        # Link to file
        self.isFile = True
        self._hdf5_file = None
        
    def close(self):
        """
        Closing function
        
        Closes the HDF5 file properly
        """
        
        self._hdf5_file.close()
        
        
    def typeInfo(self):
        return "HDF5_FILE"
        
    def data(self):
        """
        Return HDF5 file handle
        """
        return self._hdf5_file
        
    def setData(self,hdf5_file_handle):
        """
        Embed link to source HDF5 file into node structure
        
        Inputs
        ---------
        hdf5_file_handle : h5py File class
        
        """
        self._hdf5_file = hdf5_file_handle
        
    
    def path(self):
        """
        Return path of node names back to source node
        
        """
        return getPathFromNode(self)
        

class HDF5_Group(DS.DatasourceNode):
    
    def __init__(self, name, parent=None):
        super(HDF5_Group, self).__init__(name, parent)
        self._icon_name = HDF5_icons[self.typeInfo()]
        
    def typeInfo(self):
        return "HDF5_GROUP"
        
    
    def path(self):
        """
        Return path of node names back to source node
        
        """
        return getPathFromNode(self)
        


class HDF5_Dataset(DS.DatasourceTable):
    
    def __init__(self, name, parent=None):
        super(HDF5_Dataset, self).__init__(name, parent)
        self._icon_name = HDF5_icons[self.typeInfo()]
        
        # Set this node up as a table
        self.tableWrapper = DatasetTableWrapper
        
        # File
        self.isFile = True
        
        
    def typeInfo(self):
        return "HDF5_DATASET"
        
    def path(self):
        """
        Return path of node names back to source node
        
        """
        return getPathFromNode(self)
        
        
    def data(self):
        """
        Return an array-like object from the HDF5 dataset.
        This acts like a numpy array

        Output
        ---------
        dataset: HDF5 dataset        
        
        """
        
        path = self.path()
        hdf5_file_handle = self.source().data()
        
        return hdf5_file_handle[path]
        
     
class HDF5_Attribute(DS.DatasourceNode):
    
    def __init__(self, name, parent=None):
        super(HDF5_Attribute, self).__init__(name, parent)
        self._icon_name = HDF5_icons[self.typeInfo()]
        
    def typeInfo(self):
        return "HDF5_ATTRIBUTE"
        
    def path(self):
        """
        Return path of node names back to source node
        
        """
        # TODO : This might need tweaking
        return getPathFromNode(self)
        



#==============================================================================
#%% HDF5 Functions
#==============================================================================

def hdf5_dir(hdf5_file,starting_path="/",tab_level=1):
    """
    debugging function
    """
    
    if starting_path == "/":
        print(starting_path)
    
    current_dir = list(hdf5_file[starting_path].keys())
    
    for item in current_dir:
        print("\t"*tab_level,item)
        new_path = starting_path+"/"+item
        
        if hasattr(hdf5_file[new_path],'keys'):
            hdf5_dir(hdf5_file,new_path,tab_level+1)
        

def hdf5_tree(hdf5_file,starting_path="/",parent=None):
    """
    Make an HDF5 directory into a node structure
    
    Inputs
    --------
    hdf5_file : h5py File object
        Link to file
        
    starting_path : str
        HDF5 internal path to start from.
        
    parent : Node or derivative
    
    Output
    ---------
    source_node : HDF5_File node
        "root" or source node for the file
        
    """
        
    
    # Check for root directory
    # ====================================
    if parent is None:
        path, filename = os.path.split(hdf5_file.filename)
        
        # Make the first node
        # Label with the filename minus the path
        parent = HDF5_File(filename)        
        parent.setValue(hdf5_file.filename)
        
        # Add link to file
        parent.setData(hdf5_file)
        parent.isSource = True
        
        
    # Add attributes to the tree
    # ======================================    
    if len(hdf5_file[starting_path].attrs.keys()) > 0:
    
        # Add attributes to tree
        for attr in hdf5_file[starting_path].attrs.keys():
            att_node = HDF5_Attribute(attr)
            
            # Convert attribute value to a string and put it in the
            # tree
            att_node.setValue(str(hdf5_file[starting_path].attrs[attr]))
            parent.addChild(att_node)
    
    # Add groups and datasets
    # ==============================================
    
    # Get all sub directories in this path
    current_dir = list(hdf5_file[starting_path].keys())
    
    # Go through all sub directories adding them to the parent node
    # recurse through deeper levels
    for item in current_dir:
        # Set new path
        new_path = starting_path+"/"+item
       
        
        # Is this a directory, then recurse through it
        if hasattr(hdf5_file[new_path],'keys'):
            new_node = HDF5_Group(item)
            parent.addChild(new_node)
            
            new_node.setValue(new_node.path())
            hdf5_tree(hdf5_file,new_path,new_node)     
            
        # if Dataset, set type
        if hasattr(hdf5_file[new_path],'shape'):
            new_node = HDF5_Dataset(item)
            parent.addChild(new_node)
            
            new_node.setType('DATASET')
            
            # Set the value column with the array dimensions
            # Have to check if this is a recarray of single column array in
            # order to report the dimensions correctly
            shape = hdf5_file[new_path].shape
            
            if len(shape)==1:
                if hdf5_file[new_path].dtype.names is None:
                    # Single column array
                    array_shape = (shape[0],1)
                else:
                    # Recarray
                    array_shape = (shape[0],len(hdf5_file[new_path].dtype.names))
                    
            else:
                # 2D array
                array_shape = shape
            
            new_node.setValue('<%s Array>' % str(array_shape))
            
            # Add dataset attributes:
            if len(hdf5_file[new_path].attrs.keys()) > 0:
    
                # Add attributes to tree
                for attr in hdf5_file[new_path].attrs.keys():
                    att_node = HDF5_Attribute(attr)
                    
                    # Convert attribute value to a string and put it in the
                    # tree
                    att_node.setValue(str(hdf5_file[new_path].attrs[attr]))
                    new_node.addChild(att_node)
    
            
            
            
    return parent
    

def hdf5_to_node(filename):
    """
    Create node from HDF5 file
    
    """
    
    # Validate filename
    # ------------------------
    if not os.path.exists(filename):
        return
        
    # Open file
    # ------------------
    hdf5_file = h5py.File(filename,'r')
    
    # Make an HDF5 file structure
    node = hdf5_tree(hdf5_file)
    
    return node
    
    


def getPathFromNode(node):
    """
    Return full HDF5 path from a starting node back to source
    
    """
    #print("Node = %s " % node.name())
    parent = node.parent()
    
    if parent is None:
        return ""
        
    elif node.isSource:
        return "/"
    
        
    
    return  getPathFromNode(parent)  + node.name() + "/"
    
#==============================================================================
#%% Dataset
#==============================================================================    

class DatasetTableWrapper(DS.BaseDatasetTableWrapper):
    """
    Wrapper for HDF5 datasets when sending to the TableEditor
    
    Makes standard functions for accessing rows and columns, inserting, 
    deleting
    
    """
    
    # Maximumu Buffer size
    BUFFER_ROWS = 500
    BUFFER_COLUMNS = 1000
    
    def __init__(self,array):
        """
        Create wrapper with the HDF5 array
        
        Inputs
        ---------
        array : HDF5 array
            e.g. Meas['Data/Measurement/dataset1']
        
        """
        
        # Initialise base class to get standard properties
        super(DatasetTableWrapper, self).__init__()
        
        # Check this is a numpy array
        assert hasattr(array,'shape'),"DatasetTableWrapper: Not a numpy array - no 'shape' attribute"
        assert hasattr(array,'dtype'),"DatasetTableWrapper: Not a numpy array - no 'dtype' attribute"
        
        # Store array in a buffer
        self.array = Hdf5Buffer(array,0,0,self.BUFFER_ROWS,self.BUFFER_COLUMNS)
        self.array.read()
        
        self._rowCount = self.array.sourceRowCount
        self._columnCount = self.array.sourceColumnCount
        
        
        # Read only flag - for completness with other wrappers
        # - prevents insertions and deletions
        self.readOnly = True
        
        # Add formatter
        self.formatter = DS.makeNumpyFormatter()
            
        
    def rowCount(self):
        return self._rowCount
        
        
    def columnCount(self):
        return self._columnCount
        
            
        
    def cell(self,row,col):
        """
        Return contents of array element given row and column
        
        """
        
        # TODO : filter infs and NaNs
        
        if row<self.rowCount() and col<self.columnCount():
            return self.array.index(row,col)
        
        return
        
        
    def setCell(self,row,col,value):
        """
        Set contents of array element given row and column
        
        """
        
        # Not implemented for HDF5
        pass
    
        #if row<self.rowCount() and col<self.columnCount():
        #    self.array[row][col] = value
            
            
    
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
        # Not implemented for HDF5
        pass
    
        #dtype = self.array.dtype
        #self.array = np.insert(self.array,position,np.zeros(rows,dtype))
        
        
        
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
        
        # Not implemented for HDF5
        pass
    
        #rows2delete = list(range(position,position+rows))
        #self.array = np.delete(self.array,rows2delete)
                
    
        
        
    def columnHeaders(self):
        """
        Return the names of the columns
        
        For recarrays this is the dtype.names field for normal arrays this
        returns a list of numbers converted to strings
        
        """
        
        return self.array.columnHeaders()
            
            
            
    def getColumn(self,column_index):
        """
        Return a whole column as one numpy array
        
        """
        
        return self.array.column(column_index)
        
        
        
    def getColumnByName(self,column_name):
        """
        Get column using the header name
        
        """
        
        headers = self.columnHeaders()
        
        if column_name not in headers:
            return
            
       
        return self.array.column(column_name)
            
            
            
    def tableChanged(self,visibleRows,visibleColumns):
        """
        Slot called by TableEditorModel, to tell the wrapper that the size of
        the table displayed on screen has changed.
        
        If the underlying data is buffered then this can be used to signal to
        refresh the buffer.
        
        Inputs
        ---------
        visibleRows : list of 2 ints
            [top_row_index,bottom_row_index]
            
        visibleColumns  : list of 2 ints
            [left_column_index, right_column_index]
            
        """
        
        nRows = visibleRows[1]-visibleRows[0]
        nCols = visibleColumns[1]-visibleColumns[0]
        #print("Wrapper:Table changed:\n\t%i rows x %i cols" % (nRows,nCols))
        
        # See if we need to reload buffer
        self.array.reload(visibleRows,visibleColumns)
        
        
        
        
# Buffer class
class Hdf5Buffer():
    """
    Buffer for HDF5 data
    Basically an array, usually smaller than the HDF5 table

    """


    def __init__(self,source_hd5_array,start_row,start_column,number_rows,number_columns):
        """
        Inputs
        -------
        source_hd5_array: HDF5 array
        
        start_row,start_column: int
            starting point in the source array
            
        number_rows,number_columns: int
            size of buffer in rows and columns
            
        """
        
        # Link to source
        # ====================
        self._source = source_hd5_array
        
        # Internal array for holding the data in memory
        # ================================================
        self.array = None # Create later
        
        
        # Internal size variables
        # ==============================
        self._start_row = start_row
        self._start_column = start_column
        
        self._rows = number_rows
        self._columns = number_columns
        
        self.buffer_fits = False
        
        
        # Source size
        # ==================
        # Determine if this is a normal array or a recarray
        
        self._column_names = self._source.dtype.names
        self._column_dtypes = self._source.dtype
        
        self.isRecarray = False
        ndimensions = len(self._source.shape)
        if ndimensions==1 and self._column_names is not None:
            self.isRecarray = True
            
            
        # Get number of rows
        self.sourceRowCount = len(self._source)
        
        # Get number of columns, depending on type of array
        if self.isRecarray:
            self.sourceColumnCount = len(self._source.dtype.names)
            self.read = self.read_recarray
        else:
            if ndimensions == 1:
                self.sourceColumnCount = 1
            else:
                self.sourceColumnCount = self._source.shape[1]
            self.read = self.read_array
            
            
        # Reload thresholds
        self.rowThreshold = 20
        self.columnThreshold = 20
        
        # TODO : shrinking buffer for small arrays
    

    def __repr__(self):
        
        out = []
        out.append("Source: %i rows x %i columns" % (self.sourceRowCount,self.sourceColumnCount))
        out.append("Buffer: %i rows x %i columns" % (self._rows,self._columns))
        out.append("\t[%i,%i] -> [%i,%i]" % (self.start_row,self.start_column,self.start_row,self.end_column))
        out.append("\t[%i,%i] -> [%i,%i]" % (self.end_row,self.start_column,self.end_row,self.end_column))
        
        return "\n".join(out)
        
        
    def __getitem__(self,key):
        """
        Pass the key to the array, so that the whole class can be used
        like a numpy array
        
        Input
        --------
        key : multiple
            anything that would be used with a numpy array
            
        """
        return self.array[key]
        
        
    def fitInBuffer(self):
        """
        Check if whole array will fit in the buffer. If it does then adjust
        the size of the buffer accordingly
        
        Output
        ---------
        does_it_fit : bool
            True if source is smaller or same size as buffer
            
        """
        
        if all([self.sourceColumnCount<=self._columns,
                    self.sourceRowCount<=self._rows]):
                        
            # Resize buffer to fit everything
            self._start_column = 0
            self._columns = self.sourceColumnCount
            
            self._start_row = 0
            self._rows = self.sourceRowCount
            
            # Set flag to tell if buffer fits
            self.buffer_fits = True
            
        else:
            # TODO : temporary fix to make the buffer work
            self._columns = self.sourceColumnCount


    # -----------------------------------------------------------------------
    # Read methods
    # -----------------------------------------------------------------------
    def read_recarray(self):
        """
        Read the buffer into memory if it is a recarray
        
        """
        
        # Check if buffer fits data
        # =============================
        self.fitInBuffer()

        # Get column names and dtypes
        # =====================================        
        col_names = [self._column_names[n] for n in range(self._start_column,self._start_column+self._columns)]        
        dtypes2copy = [(name,self._column_dtypes.fields[name][0]) for name in col_names]
        
        # Get rows
        # ===================
        rows2copy = np.arange(self._start_row,self._start_row+self._rows,1,dtype=int)
        
        # Create buffer
        # ========================
        self.array = np.zeros(self._rows,dtypes2copy)
        
        for name in col_names:
            self.array[name] = self._source[name][rows2copy]
        
        
        
        
        
    def read_array(self):
        """
        Read the buffer into memory
        
        """
        
        # Check if buffer fits data
        # =============================
        self.fitInBuffer()
        
        # Columns 
        # ============
        if self.sourceColumnCount==1:
            cols2copy = np.arange(self._start_column,self._start_column)
        else:
            cols2copy = np.arange(self._start_column,self._start_column+self._columns)
        
        # Get rows
        # ===================
        rows2copy = np.arange(self._start_row,self._start_row+self._rows)
        
        # Create buffer
        # ===============
        self.array = np.zeros((self._rows,self._columns),self._source.dtype)
        
        for iCol,col in enumerate(cols2copy):
            self.array[:,iCol] = self._source[rows2copy,col]
        
        
        
        
    # -----------------------------------------------------------------------
    # Conversions
    # -----------------------------------------------------------------------
    def src2bufRows(self,src_row_index):
        """
        Convert source row index to buffer row index
        
        Input
        -------
        src_row_index : int
            
        Output
        ---------
        buf_row_index : int
        
        """
        
        return src_row_index - self._start_row
        
        
    
    def src2bufCols(self,src_col_index):
        """
        Convert source row index to buffer row index
        
        Input
        -------
        src_col_index : int
            
        Output
        ---------
        buf_col_index : int
        
        """
        
        return src_col_index - self._start_column
        
        
        
    def buf2srcRows(self,buf_row_index):
        """
        Convert buffer row index to source row index
        
            
        Input
        ---------
        buf_row_index : int
        
        Output
        -------
        src_row_index : int
        
        
        """
        
        return buf_row_index + self._start_row
        
        
    def buf2srcCols(self,buf_col_index):
        """
        Convert buffer row index to source row index
        
            
        Input
        ---------
        buf_col_index : int
        
        Output
        -------
        src_col_index : int
        
        
        """
        
        return buf_col_index + self._start_column
        
        
    @property
    def start_row(self):
        return self._start_row
        
    @start_row.setter
    def start_row(self,value):
        self._start_row = int(value)
        
    @property
    def start_column(self):
        return self._start_column
        
    @start_column.setter
    def start_column(self,value):
        self._start_column = int(value)
        
        
    @property
    def end_row(self):
        return self._start_row + self._rows -1
        
    @property
    def end_column(self):
        return self._start_column + self._columns - 1
        
    @property
    def end_buffer_row(self):
        return self._rows-1
        
    @property
    def end_buffer_column(self):
        return self._columns-1
        
        
    def reload(self,visibleRows,visibleColumns):
        """
        Reload buffer based on whether the visible rows and columns are
        outside of the thresholds
        
        Inputs
        ---------
        visibleRows : list of 2 ints
            [top_row_index,bottom_row_index]
            
        visibleColumns  : list of 2 ints
            [left_column_index, right_column_index]
            
        """
        # Break out of lists for readability
        # =====================================
        v_top = visibleRows[0]
        v_bottom = visibleRows[1]
        
        v_left = visibleColumns[0]
        v_right = visibleColumns[1]
        
        # Check columns
        # ========================
        # Negative values mean outside buffer boundary
        toLeftSide = v_left - self.start_column
        toRightSide = self.end_column - v_right 
        
        closeToLeft = toLeftSide < self.columnThreshold
        closeToRight = toRightSide < self.columnThreshold
        
        # Check rows
        # ===============
        toTop = v_top - self.start_row
        toBottom = self.end_row - v_bottom
        
        closeToTop = toTop < self.rowThreshold
        closeToBottom = toBottom < self.rowThreshold

#        if closeToLeft:
#            print("Close to left")
#            
#        if closeToRight:
#            print("Close to right")
#            
#        if closeToTop:
#            print("Close to top")
#            
#        if closeToBottom:
#            print("Close to bottom")
        
        
        # Get offset from centre of display to centre of buffer
        # =======================================================
        centre_row = round(self.start_row + self._rows/2)
        centre_col = round(self.start_column + self._columns/2)
        
        disp_centre_row = round( (v_top+v_bottom)/2 )
        disp_centre_col = round( (v_left+v_right)/2 )
        
        row_offset = disp_centre_row - centre_row
        col_offset = disp_centre_col - centre_col
        
        
        # Calculate new buffer position
        # =================================
        # Don't change size of buffer at this point
        
        # Calculate the basic position 
        #   clip to zero and the highest end value
        new_start_row = np.clip(self.start_row + row_offset,0,self.sourceRowCount-self._rows)
        new_start_col = np.clip(self.start_column + col_offset,0,self.sourceColumnCount-self._columns)
        
        new_rowSpan = self.end_row - self.start_row
        new_colSpan = self.end_column - self.start_column
        
        # TODO : What happens when buffer is smaller than visible area?
        
        
        # Adjust for clipping to sides
        # ==================================
        
        # Set up some flags to indicate clipping
        clipLeft = False
        clipRight = False
        clipTop = False
        clipBottom = False
        

        # Check rows for clipping
        # ---------------------------------        
        if new_rowSpan < self._rows:
            # Only care if the start row is above zero, this means
            # that we got clipped on bottom edge
            if new_start_row > 0:
                # Back off the start row
                new_start_row = self.sourceRowCount-self._rows
                clipBottom = True
            elif new_start_row == 0:
                clipTop = True
        
        
        # Check columns for clipping
        # -----------------------------------
        if new_colSpan < self._columns:
            
            if new_start_col >0 :
                new_start_col = self.sourceColumnCount-self._columns
                clipRight = True
            elif new_start_col == 0:
                clipLeft = True
                
        # Set new end rows and columns
        # --------------------------------
        new_end_row = new_start_row + self._rows -1
        new_end_col = new_start_col + self._columns - 1
                
#        # Debugging printout
#        out = []
#        out.append("New buffer position")
#        out.append("\t[%i,%i] -> [%i,%i]" % (new_start_row,new_start_col,new_start_row,new_end_col))
#        out.append("\t[%i,%i] -> [%i,%i]" % (new_end_row,new_start_col,new_end_row,new_end_col))
#        print("\n".join(out))
        
        # Recheck the 'closeTo' flags against the 'clip' flags
        # ------------------------------------------------------
        if closeToTop and clipTop:
            closeToTop = False
            
        elif closeToBottom and clipBottom:
            closeToBottom = False
            
        elif closeToRight and clipRight:
            closeToRight = False
            
        elif closeToLeft and clipLeft:
            closeToLeft = False
        
        
        # Decide if buffer needs reloading
        # =================================
        
        # Basic test - not close to any edges
        if not any([closeToBottom,closeToTop,closeToLeft,closeToRight]):
            #print("Hd5Buffer.reload: Not close to any boundaries - No need to reload")
            return
            
        # Everything clipped - buffer is bigger than visible size
        if all([clipLeft,clipRight,clipTop,clipBottom]):
            #print("Hd5Buffer.reload: Everything clipped")
            return
            
        # Buffer size and position is the same
        if all([self.start_column==new_start_col,
                self.start_row==new_start_row,
                self.end_column==new_end_col,
                self.end_row==new_end_row]):
            #print("Hd5Buffer.reload: No change in buffer detected")
            return
        
        
        # Reset the buffer boundaries
        # ================================
        #print("Hd5Buffer.reload: reloading")
        
        self.start_row = new_start_row
        self.start_column = new_start_col
        
        self.read()
        
        
    def columnHeaders(self):
        """
        Return the names of the columns
        
        For recarrays this is the dtype.names field for normal arrays this
        returns a list of numbers converted to strings
        
        """
        
        if self.isRecarray:
            return self._column_names
        else:
            return [str(n) for n in range(self.sourceColumnCount)]
        
        
    def index(self,source_row,source_col):
        """
        Return single value from source
        
        Input
        --------
        source_row,source_col: int
            row and column coordinates for value, specified in absolute
            source coordinate system.
            
        Output
        --------
        value : float
            returned value
            
        """
        
        # Convert to buffer row/col coordinates
        # --------------------------------------
        buf_row = self.src2bufRows(source_row)
        buf_col = self.src2bufCols(source_col)
        
        
        # If data is within buffer, return value
        # -----------------------------------------
        if (0<=buf_row<=self.end_buffer_row) and (0<=buf_col<=self.end_buffer_column):
            #print("Reading from internal")
            return self.array[buf_row][buf_col]
            
        # Get data from source
        # ------------------------
        #print("Reading from file")
        return self._source[source_row][source_col]
        
        
    def column(self,column_name_or_index):
        """
        Get Whole column, given name or index
        
        Input
        ------
        column_name_or_index : str or int
            name or index of the column
            
        """
        
        if isinstance(column_name_or_index,str):
            return self.columnFromName(column_name_or_index)
        elif isinstance(column_name_or_index,int):
            return self.columnFromIndex(column_name_or_index)
            
        
        
    def columnFromName(self,name):
        """
        Return whole column given the column name
        
        Inputs
        --------
        name : str
            Name of column
            
        Output
        -------
        column_array : numpy 1D array
            array of all data in column
            
        """
        
        # Check for rejection criteria
        # -------------------------------
        if not self.isRecarray:
            return
            
        if name not in self._column_names:
            return
            
        # Check if the internal array can do the whole column
        # -----------------------------------------------------
        if self.buffer_fits:
            return self.array[name]
            
            
        if self._rows == self.sourceRowCount:
            return self.array[name]
            
        # If all else fails, return from source
        # -----------------------------------------
        return self._source[name]
        
        
    
    
    def columnFromIndex(self,index):
        """
        Return whole column given the column index
        
        Inputs
        --------
        index : int
            index of column
            
        Output
        -------
        column_array : numpy 1D array
            array of all data in column
            
        """
        
        # Check for rec array
        # ---------------------------
        if self.isRecarray:
            # Get the column name and outsource
            if index < len(self._column_names):
                return self.columnFromName(self._column_names[index])
            else:
                return
                
        # Check if the internal array can do the whole column
        # -----------------------------------------------------
        if self.buffer_fits:
            
            return self.array[:,index]
        
                    
        
    
    
#==============================================================================
#%% Source declaration
#==============================================================================
# Put the names of any Datasource classes in the __sources__ variable. When
# ScopePy loads the source classes into memory it will create any class in
# the __sources__ variable
# 

__sources__ = [HDF5_Datasource]

