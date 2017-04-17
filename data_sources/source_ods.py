# -*- coding: utf-8 -*-
"""
Created on Sat Nov 14 15:07:37 2015

@author: john
"""


#==============================================================================
#%% Imports
#==============================================================================

# Standard library
import os


# Third party libraries
import numpy as np

# My libraries
import data_sources.data_source_base_library as DS
from data_sources.source_numpyArray import DatasetTableWrapper
import odslib


#==============================================================================
#%% Constants
#==============================================================================


# Icons
# ============================
CSV_icons = {"CSV_FILE":"data_source_csv","TABLE":"data_source_table"}
              

#==============================================================================
#%% CSV Datasource setup class
#==============================================================================
# This class is a wrapper for functions that convert data sources to a node
# structure
#
# For each source defined, the wrapper class must have the following functions:
# * to_node(*parameters) : returns a DatasourceNode derivative class 
#

class CSV_Datasource(DS.DatasourceCreator):
    """
    Creator class for HDF5 files
    
    """
    
    def __init__(self):
        super(CSV_Datasource, self).__init__()
        
        # Name
        self.name = 'ods'
        
        # It's a file
        self.isFile = True
        
        # File extensions are
        self.fileTypes = ['ods']
        
    
    def toNode(self,filename):
        """
        Convert CSV file into a DatasourceNode derivative class
        
        Input
        --------
        filename : str
            path/filename of CSV file
            
        Output
        ---------
        node : csv class instance
        
        """
        
        # Validate filename
        # ------------------------
        if not os.path.exists(filename):
            return
            
        # Open file
        # ------------------
        try:
            print("Making CSV node")
            node = ODS_File(filename)
            
            #node.addChild(data_node)
            node.read_data(filename)
            
            print("Tagging CSV node with filename")
            node.sourceFile = filename
            
            # Tag the base node with the creator name
            node.creator = self.name
            
            return node
            
        except Exception as ex:
            # TODO : log some kind of error here
            print(ex)
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
            CSV file structure converted to a node structure.
            
        """
        
        return self.toNode(filename)
        
        
#==============================================================================
#%% CSV Nodes
#==============================================================================
# Node types for CSV files and their components

class ODS_File(DS.DatasourceNode):
    
    def __init__(self, name, parent=None):
        
        # Make name field just the filename
        path, filename = os.path.split(name)
        
        super(ODS_File, self).__init__(filename, parent)
        self.isSource = True
        self._icon_name = CSV_icons[self.typeInfo()]
        
        # Link to file
        self.isFile = True
        self.sourceFile = name
        
        
        self.setName(filename)
        
    def close(self):
        """
        Closing function
        
        Closes the CSV file properly
        """
        
        pass
        
        
    def typeInfo(self):
        return "CSV_FILE"
        
        
    def data(self):
        """
        Return CSV file handle
        """
        return self.sourceFile
        
        
    def setData(self,csv_file_path):
        """
        Embed link to source HDF5 file into node structure
        
        Inputs
        ---------
        hdf5_file_handle : h5py File class
        
        """
        self.sourceFile = csv_file_path
        
    
    def path(self):
        """
        Return path of node names back to source node
        
        """
        
        pass

    def read_data(self,filename):
        data = odslib.load(filename).data
        for i in data:
            dn = dataNode(i,self,data[i])
            self.addChild(dn)
            
    
#    @property
#    def sourceFile(self):
#        return self._csv_file
    
    

class dataNode(DS.DatasourceNode):
    def __init__(self,name,parent,data):
        self._data = data
        #self.titles = titles
        super(dataNode,self).__init__(name,parent)
        self._icon_name = CSV_icons[self.typeInfo()]
        self.isTable = True
        self.tableWrapper = tableWrapper
    def typeInfo(self):
        return 'TABLE'

    def data(self):
        return self._data

class tableWrapper(DS.BaseDatasetTableWrapper):
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
        super(tableWrapper, self).__init__()
        
        # Check this is a numpy array
        #assert hasattr(array,'shape'),"DatasetTableWrapper: Not a numpy array - no 'shape' attribute"
        #assert hasattr(array,'dtype'),"DatasetTableWrapper: Not a numpy array - no 'dtype' attribute"
        
        # Store array
        self._data = array
        #self.titles = array.titles
        # Read only flag - for completness with other wrappers
        # - prevents insertions and deletions
        self.readOnly = True
        
        # Determine if this is a normal array or a recarray
        #shape = array.shape
        
        #self.isRecarray = False
        
        #if len(shape)==1 and array.dtype.names is not None:
        #    self.isRecarray = True

        self.formatter.addFormat(None,"NULL")
        

            
        self.setData(array)
        
        
        

    def setData(self,lol):
        self._data = lol
        self.rows = []
        self.cols = []
        for e, i in enumerate(self._data):
                self.rows.append(i)

        for e,i in enumerate(self.rows[0]):
           
                
            
            c = []
            for i in self.rows:
                c.append(i[e])
            self.cols.append(c)

            
    def columnFormat(self,column):
        c = self.cols[column]
        if type(c[0]) == int or type(c[0]) == float:
            return '%.4f'
        else:
            return '%s'



        
    def rowCount(self):
        return len(self.rows)
        
        
    def columnCount(self):
         return len(self.cols)
        
            
        
    def cell(self,row,col):
        """
        Return contents of array element given row and column
        
        """
        
        # TODO : filter infs and NaNs
        
        return self.rows[row][col]
        
        
    def columnHeaders(self):
        """
        Return the names of the columns
        
        For recarrays this is the dtype.names field for normal arrays this
        returns a list of numbers converted to strings
        
        """
        #print(self.titles)
        return [str(i) for i in range(len(self._data[0]))]
        
            
            
            
    def getColumn(self,column_index):
        """
        Return a whole column as one numpy array
        
        """
        
        return self.cols[column_index]
        
        
        
    def getColumnByName(self,column_name):
        """
        Get column using the header name
        
        """
        
        headers = self.columnHeaders()
        
        if column_name not in headers:
            return
            
        
        return self.getColumn[headers.index(column_name)]


#==============================================================================
#%% Source declaration
#==============================================================================
# Put the names of any Datasource classes in the __sources__ variable. When
# ScopePy loads the source classes into memory it will create any class in
# the __sources__ variable
# 

__sources__ = [CSV_Datasource]
