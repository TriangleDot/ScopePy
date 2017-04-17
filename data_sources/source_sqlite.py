# -*- coding: utf-8 -*-
"""
Created on Sat Nov 14 15:07:37 2015

@author: finn
"""


#==============================================================================
#%% Imports
#==============================================================================

# Standard library
import os
import sqlite3
import types


# Third party libraries
import numpy as np
import PyQt4.QtGui as qt

# My libraries
import data_sources.data_source_base_library as DS
from data_sources.source_numpyArray import DatasetTableWrapper,Array_Node


#==============================================================================
#%% Constants
#==============================================================================


# Icons
# ============================
icons = {"SQLITE_DATABASE":"database_home","TABLE":"data_source_table",
         "QUERY":"database_query"}
              

#==============================================================================
#%% CSV Datasource setup class
#==============================================================================
# This class is a wrapper for functions that convert data sources to a node
# structure
#
# For each source defined, the wrapper class must have the following functions:
# * to_node(*parameters) : returns a DatasourceNode derivative class 
#
FILE_VERSION = 3

class sqlite_Datasource(DS.DatasourceCreator):
    """
    Creator class for HDF5 files
    
    """
    
    def __init__(self):
        super(sqlite_Datasource, self).__init__()
        
        # Name
        self.name = 'sqlite3'
        
        # It's a file
        self.isFile = True
        
        # File extensions are
        self.fileTypes = ['db','sqlite','sqlite3']
        
    
    def toNode(self,filename):
        """
        Convert sqlite file into a DatasourceNode derivative class
        
        Input
        --------
        filename : str
            path/filename of sqlite database
            
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
            print("Making SQLite node")
            node = dbhome(filename)
            #data_node = dataset("Data")
            #node.addChild(data_node)
            #node.read_data()
            
            print("Tagging SQLite node with filename")
            #node.sourceFile = filename
            
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
        
        return self.to_node(filename)
        
        
#==============================================================================
#%% CSV Nodes
#==============================================================================
# Node types for CSV files and their components

class  dbhome(DS.DatasourceNode):
    
    def __init__(self, name, parent=None):
        
        # Make name field just the filename
        path, filename = os.path.split(name)
        
        super(dbhome, self).__init__(filename, parent)
        self.isSource = True
        self._icon_name = icons[self.typeInfo()]
        
        # Link to file
        self.isFile = True
        self.sourceFile = name
        self.database = sqlite3.connect(name)
        self.queries = []
        
        self.setName(filename)

    def saveData(self):
        data = self.standardSaveData
        data['queries'] = self.queries
        data['version'] = FILE_VERSION
        return data

    def restoreData(self,data):
        if data['version'] != FILE_VERSION:
            return data
        queries = data['queries']
        #print(self.queries)

        for i in queries:
            print(i)
            self.addQuery(i)
        return data
            
        
        
        
    def close(self):
        """
        Closing function
        
        Closes the CSV file properly
        """
        
        self.database.close()
        
        
    def typeInfo(self):
        return "SQLITE_DATABASE"
        
        
    def data(self):
        """
        Return CSV file handle
        """
        return self.database
        
        
    def setData(self,csv_file_path):
        """
        Embed link to source HDF5 file into node structure
        
        Inputs
        ---------
        hdf5_file_handle : h5py File class
        
        """
        self.close()
        self.sourceFile = csv_file_path
        self.database = sqlite.connect(csv_file_path)
        
    
    def path(self):
        """
        Return path of node names back to source node
        
        """
        
        return "Sqlite Database"

    
    def menu(self):
        # Default menu
        # ----------------------
        menu = qt.QMenu()
        menu.addAction(menu.tr('Run Query'),self.runQuery)
        menu.addAction(menu.tr("Copy path to clipboard" ),self.valueToClipboard)
        
        # Return 
        return menu

    def runQuery(self):
        #print(self)
        qu,ok = qt.QInputDialog.getText(self.API._gui,'Query Dialog','Please Enter Query:')
        print(qu)
        print(ok)
        if ok:
            self.addQuery(qu)

    def addQuery(self,qu):
            self.queries.append(qu)
            qnode = query('%s:Query' % qu,self,qu)
            self.addChild(qnode)
            #self.log()
            #self.API.dataSourceSelector.model.reset()
        
        
    
#    @property
#    def sourceFile(self):
#        return self._csv_file


    
    
class query(DS.DatasourceNode):
    
    def __init__(self, name, parent=None,Query=None):
        super(query, self).__init__(name, parent)
        self._icon_name = icons[self.typeInfo()]
        if not Query:
            Query = ''
        self.query = Query
        self.db = parent.database
        self.querynum = 0
        
        
        # Set this node up as a table
        self.isTable = False
        #self.tableWrapper = DatasetTableWrapper
        
        
    def read_data(self):
        # Read data from csv file
        try:
            c = self.db.execute(self.query)
        except Exception as ec:
            qt.QMessageBox.warning(self.API._gui,"Error:",str(ec))
            return
        fall = c.fetchall()
        if fall == [()]:
            return
        self._cursor = c
        self._data = fall
        
        
    def typeInfo(self):
        return "QUERY"
        
    def path(self):
        """
        Return path of node names back to source node
        
        """
        return self.query
        
        
    def data(self):
        """
        Return an array-like object from the CSV dataset.
        This acts like a numpy array

        Output
        ---------
        dataset: numpy recarray
        
        """        
        return self._data

    
    def menu(self):
        # Default menu
        # ----------------------
        menu = qt.QMenu()
        menu.addAction(menu.tr('Activate!'),self.activate)
        menu.addAction(menu.tr("Copy path to clipboard" ),self.valueToClipboard)
        
        # Return 
        return menu

    def activate(self):
        self.read_data()
        try:
            d = self._cursor.description
        except AttributeError:
            return
        if self._data:
            for i in self._data:
                if not i:
                    #self._parent = None
                    return
        else:
            return
        if d == None:
            return
        titles = []
        for i in d:
            titles.append(i[0])
        #array = np.array(self._data)
        node = dataNode('Data: %i' % self.querynum,self,self._data,titles) 
        #node._array=array
        self.querynum += 1
        self.addChild(node)
        #self.API.dataSourceSelector.model.reset()
        

class dataWrapper(object):
    
    def __init__(self,data,titles):
        self.data = data
        self.titles = titles
        
class dataNode(DS.DatasourceTable):
    def __init__(self,name,parent,data,titles):
        self._data = data
        self.titles = titles
        super(dataNode,self).__init__(name,parent)
        self._icon_name = icons[self.typeInfo()]
        self.isTable = True
        self.tableWrapper = tableWrapper
        
    def typeInfo(self):
        return 'TABLE'

    def data(self):
        return dataWrapper(self._data,self.titles)
        

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
        self._data = array.data
        self.titles = array.titles
        # Read only flag - for completness with other wrappers
        # - prevents insertions and deletions
        self.readOnly = True
        
        # Determine if this is a normal array or a recarray
        #shape = array.shape
        
        #self.isRecarray = False
        
        #if len(shape)==1 and array.dtype.names is not None:
        #    self.isRecarray = True

        self.formatter.addFormat(None,"NULL")
        

            
        self.setData(array.data)
        
        
        

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
        return self.titles
        
            
            
            
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
        
        


class list_Datasource(DS.DatasourceCreator):
    """
    Creator class for HDF5 files
    
    """
    
    def __init__(self):
        super(list_Datasource, self).__init__()
        
        # Name
        self.name = 'List-Of-List'
        
        # It's a file
        self.isFile = False
        
        # File extensions are
        #self.fileTypes = ['db','sqlite','sqlite3']
        
    
    def toNode(self,data,titles=None):
        """
        Convert sqlite file into a DatasourceNode derivative class
        
        Input
        --------
        filename : str
            path/filename of sqlite database
            
        Output
        ---------
        node : HDF5_File class instance
        
        """
        
        # Validate filename
        # ------------------------
        #if not os.path.exists(filename):
        #    return
            
        # Open file
        # ------------------
        if not titles:
            titles = []
            for e,i in enumerate(data):
                titles.append(e)
                
        try:
            #print("Making SQLite node")
            created_data = types.new_class('dataWrapper')
            created_data.data = data
            created_data.titles = titles
            node = dataNode(None,None,data,titles)
            #data_node = dataset("Data")
            #node.addChild(data_node)
            #node.read_data()
            
            #print("Tagging SQLite node with filename")
            #node.sourceFile = filename
            
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
        
        return self.to_node(filename)
#==============================================================================
#%% Source declaration
#==============================================================================
# Put the names of any Datasource classes in the __sources__ variable. When
# ScopePy loads the source classes into memory it will create any class in
# the __sources__ variable
# 

__sources__ = [sqlite_Datasource,list_Datasource]
