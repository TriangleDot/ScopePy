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


#==============================================================================
#%% Constants
#==============================================================================


# Icons
# ============================
CSV_icons = {"CSV_FILE":"data_source_csv","CSV_DATASET":"data_source_table"}
              

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
        self.name = 'csv'
        
        # It's a file
        self.isFile = True
        
        # File extensions are
        self.fileTypes = ['csv']
        
    
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
            node = CSV_File(filename)
            data_node = CSV_Dataset("Data")
            node.addChild(data_node)
            data_node.read_data()
            
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

class CSV_File(DS.DatasourceNode):
    
    def __init__(self, name, parent=None):
        
        # Make name field just the filename
        path, filename = os.path.split(name)
        
        super(CSV_File, self).__init__(filename, parent)
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
    
#    @property
#    def sourceFile(self):
#        return self._csv_file
    
    
class CSV_Dataset(DS.DatasourceTable):
    
    def __init__(self, name, parent=None):
        super(CSV_Dataset, self).__init__(name, parent)
        self._icon_name = CSV_icons[self.typeInfo()]
        
        # Set this node up as a table
        self.tableWrapper = DatasetTableWrapper
        
        
    def read_data(self):
        # Read data from csv file
        self._data = np.recfromcsv(self.parent().sourceFile)
        
        
    def typeInfo(self):
        return "CSV_DATASET"
        
    def path(self):
        """
        Return path of node names back to source node
        
        """
        return "CSV data"
        
        
    def data(self):
        """
        Return an array-like object from the CSV dataset.
        This acts like a numpy array

        Output
        ---------
        dataset: numpy recarray
        
        """        
        return self._data



#==============================================================================
#%% Source declaration
#==============================================================================
# Put the names of any Datasource classes in the __sources__ variable. When
# ScopePy loads the source classes into memory it will create any class in
# the __sources__ variable
# 

__sources__ = [CSV_Datasource]
