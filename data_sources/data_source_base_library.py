# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 12:38:21 2015

@author: john


ScopePy Datasource base class
===============================
Base library for ScopePy datasource classes


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
import logging
import inspect

# Third party libraries
import numpy as np

from PyQt4.QtCore import *
from PyQt4.QtGui import *

# My libraries
from ScopePy_utilities import import_module_from_file
import ScopePy_API as api

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
standard_icons = {"HOME":QIcon.fromTheme('user-home'),
                  "SOURCE":QIcon.fromTheme('drive-harddisk')}



#==============================================================================
#%% DatasourceNode Class definition
#==============================================================================

class DatasourceNode(object):
    """
    Basic ScopePy data sources node.
    This is the base class for all ScopePy data sources. Each different type
    of data source node class must inherit from this class.
    
    It provides all the methods needed by the DataSourcesTreeModel which is
    used to drive the source selector panel.
    
    DatasourceNodes supply menus for individual parts of the tree view so 
    customised context menus can be implemented via the menu() function.
    
    """
    
    def __init__(self, name, node_type='NODE',parent=None):
        """
        Nodes can be created with a minimum of just a name
        >>> DatasourceNode('root')
        
        Optionally a type can be specified
        >>> DatasourceNode('root',node_type ='ROOT')
        
        The usual practice is to create a class that inherits from DatasourceNode
        and set the type of node in the __init__() function of the new class.
        
        """
        
        # Base properties
        self._name = name
        self._children = []
        self._parent = parent
        self._type = node_type
        self._value = None
        
        # Flag to indicate if this node represents the source data
        # e.g. the file
        self.isSource = False
        
        # Flag to indicate is this source is derived from a file
        self.isFile = False
        self.sourceFile = None
        
        # Connection to main API 
        # Must be provisioned when the node is created.
        self._API = None
        
        # list of links to this source
        # - only used for source nodes
        self.links = []
        
        # Flag to indicate if this node is a table of data
        self.isTable = False
        
        # Wrapper function for the Table Editor panel
        self.tableWrapper = None
        
        # Table editor panel name
        self.tableEditorPanel = 'Table editor'
        
        # Creator type
        # label used to identify the creator class
        self.creator = None
        
        # Icons
        # --------------
        # Link to stored icons
        self._icon_manager = api.IconManager()
        
        # Name of the icon from the icon_manager store
        self._icon_name = ""
        
        if parent is not None:
            parent.addChild(self)
            
            # Link to stored icons
            #self.icon_manager = parent.icon_manager


    @property
    def icon(self):
        return self.icon_manager[self._icon_name]
        
    @icon.setter
    def icon(self,name):
        self._icon_name = name
        
    @property
    def icon_manager(self):
        """
        Return the icon manager from the source node
        """
        
        return getRoot(self)._icon_manager
        
    @icon_manager.setter
    def icon_manager(self,manager):
        """
        Set a new icon manager
        """
        self._icon_manager = manager
        
    @property
    def API(self):
        """
        Return the link to main API from the source node
        """
        
        return getRoot(self)._API
        
    @API.setter
    def API(self,link):
        """
        Set link to API
        
        Inputs
        ----------
        link : ScopePy API class
        
        """
        self._API = link
        

    def typeInfo(self):
        return self._type
        
    def setType(self,type_name):
        self._type = type_name
        

    def addChild(self, child):
        """
        Add a child to the parent, make parent the childs new parent and
        pass through the icon manager
        """
        
        # Link to parent
        child._parent = self
        
        self._children.append(child)
        
        
        

    def insertChild(self, position, child):
        
        if position < 0 or position > len(self._children):
            return False
        
        self._children.insert(position, child)
        child._parent = self
        
        return True

    def removeChild(self, position):
        
        if position < 0 or position > len(self._children):
            return False
        
        child = self._children.pop(position)
        child._parent = None

        return True


    def name(self):
        return self._name

    def setName(self, name):
        self._name = name
        
    def data(self):
        """
        Required method for returning data from node
        
        Re-implement for different types of node
        """
        return None

        
    def setData(self):
        """
        Required method for setting data from node
        
        Re-implement for different types of node
        """
        return True
        
        
    def child(self, row):
        return self._children[row]
    
    def childCount(self):
        return len(self._children)

    def parent(self):
        return self._parent
    
    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)
            
    def path(self):
        """
        Return path of node names back to source node
        
        """
        return None
        
    def value(self):
        """
        Return data from node
        
        """
        return self._value
        
        
    def setValue(self,value_string):
        """
        Put a value in the Node as a string
        
        """
        
        if isinstance(value_string,str):
            self._value = value_string
            
    def source(self):
        """
        Return data source node
        
        Output:
        ------------
        source_node : Node
            The data source node with isSource flag set.
        
        """
        
        return getSource(self)
        
    
        
        
    def addLink(self,link_widget):
        """
        Add any connected widgets here.
        
        Inputs
        ---------
        connection_widget : QWidget
            any widget that is connected to the source or its children
            Used for updating or deleting the widgets
        """
        
        self.links.append(link_widget)
        
        
    def tableData(self):
        """
        For nodes that have the isTable flag set then this function will
        return data suitable for the table editor.
        
        For this to work the tableWrapper field must be a reference to a
        function that will wrap the data with the appropriate methods.
        
        Output
        ---------
        wrapped_data : table wrapper class
            Depends on the type of data source
            sources that provide table data must have a wrapper class
            
        """
        
        if not self.isTable or self.tableWrapper is None:
            return
            
        return self.tableWrapper(self.data())
        
        
    
    def editTable(self):
        """
        Generic table editing function. Can be used with any node that has
        isTable flag set to True. It will launch a Table Editor panel with the
        table data from this node
        
        """
        if not self.isTable:
            return
            
            
        logger.debug('DataSourceSelector: Sending [%s] data to table editor' % self.typeInfo())
        data = self.tableData()
        source = self.source()
        path = self.path()
        
        if path:
            WindowTitle = "[%s] : %s" % (source.name(),path)
        else:
            WindowTitle = "Source: [%s] , Table: [%s]" % (source.name(),self.name())
        
        editor = self.API.addPanel(self.tableEditorPanel,WindowTitle)
        
        sourceLinkText = "%s:%s" % (source.name(),self.name())
        
        self.API.sendComms('addSource',editor.ID,data,sourceLinkText)
        
        # Get the MDI window for the editor panel
        if editor.window() is not None:
            logger.debug("Data source selector: Adding link [%s] to [%s]" % (source.name(),self.name()))
            source.addLink(editor.window())
            
            
            
            
    def valueToClipboard(self):
        """
        Generic clipboard copying function. Copies either the node path or value
        to the clipboard.
        
        """
        
        clipboard = QApplication.clipboard()
        if self.path():
            clipboard.setText(self.path())
        else:
            clipboard.setText(self.value())
            
            
        
       

    def menu(self):
        """
        Return a menu of actions that can be performed on this node.
        
        By default a 'copy path to clipboard' option is supplied for all nodes
        and if the node is a table of data then a 'Edit table' option is supplied.
        
        Output:
        -------
        menu : QMenu
            Populated menu of actions for this node. If there are no actions
            then return None
            
        """
        
        # Default menu
        # ----------------------
        menu = QMenu()
        if self.isTable:
            menu.addAction(menu.tr("Edit %s" % self.typeInfo()),self.editTable)
        menu.addAction(menu.tr("Copy path to clipboard" ),self.valueToClipboard)
        
        # Return 
        return menu


    def log(self, tabLevel=-1):

        output     = ""
        tabLevel += 1
        
        for i in range(tabLevel):
            output += " "*4
        
        output += "|---" + self._name 
        output += "[%s]\n" % self._type
        
        for child in self._children:
            output += child.log(tabLevel)
        
        tabLevel -= 1
        #output += "\n"
        
        return output

    def __repr__(self):
        return self.name()
        
    # -------------------------------------------------------------------------    
    # Storing and loading functions
    # -------------------------------------------------------------------------
    def saveData(self):
        """
        Return data needed to re-create this node after is has been saved
        to a ScopePy session file
        
        Output
        ----------
        save_dict : dict
            Dictionary with all data required to re-create the data source.
            Mandatory fields are:
            
            'creator' - self.creator
            'isFile' - self.isFile
            'filename' - only required if 'isFile' is True - then the node will
                         be re-created from the filename
                         
             Other keys can be used to store custom data
        """
        
        return self.standardSaveData
        
    
    def restoreData(self,save_dict):
        """
        Restore the data in the data source node.
        
        Input
        -------
        save_dict : dict
            Dictionary with all data required to re-create the data source.
            Mandatory fields are:
            
            'creator' - self.creator
            'isFile' - self.isFile
            'filename' - only required if 'isFile' is True - then the node will
                         be re-created from the filename
                         
             Other keys can be used to store custom data
        """
        
        pass
    
    
    @property
    def standardSaveData(self):
        """
        Return a dictionary with the mandatory keys for use with the saveData()
        function.
        
        Output
        ---------
        save_dict : dict
            Dictionary with all data required to re-create the data source.
            Mandatory fields are:
            
            'creator' - self.creator
            'isFile' - self.isFile
            'filename' - only required if 'isFile' is True - then the node will
                         be re-created from the filename
                         
             
        """
        
        save_dict= {}
        
        save_dict['creator'] = self.creator
        save_dict['isFile'] = self.isFile
        if self.isFile:
            save_dict['filename'] = self.sourceFile
            
        return save_dict
        
        
# Support functions
# -------------------------

def getSource(node):
    """
    Find the data source node for this node.
    
    Track back through the tree to find the node where the isSource flag is
    set
    
    Input
    ----------
    node : Node or derivative
    
    Output
    ------
    source_node : Node or derivative
    
    """
    
    # Check if this is the source
    if node.isSource:
        return node
    
    # Back up the tree
    if node.parent is not None:
        return getSource(node.parent())
        
        
def getRoot(node):
    """
    Find root node of tree
    
    """
    
    
    # Back up the tree until we reach 'root'
    if node.name()=='root':
        return node
    else:
        return getRoot(node.parent())
    
        
    
 
#==============================================================================
#%% Base Nodes
#==============================================================================
# Root and Home nodes

class Home(DatasourceNode):
    
    def __init__(self, name, parent=None):
        super(Home, self).__init__(name, parent)
        self._icon_name = 'data_source_home'
        
        # Make default display value = 'Home'
        self._value = 'Datasource Home'
        
    def typeInfo(self):
        return "HOME"


class DatasourceTable(DatasourceNode):
    """
    Special version of DatasourceNode for nodes that contain tabular data
    
    This is just a shell, specific data sources will need this to be 
    reimplemented
    
    """
    
    def __init__(self,*args,**kwargs):
        
        super(DatasourceTable, self).__init__(*args,**kwargs)
        
        self.isTable = True
    
    
    
    def tableData(self):
        """
        For nodes that have the isTable flag set then this function will
        return data suitable for the table editor.
        
        For this to work the tableWrapper field must be a reference to a
        function that will wrap the data with the appropriate methods.
        
        Output
        ---------
        wrapped_data : table wrapper class
            Depends on the type of data source
            sources that provide table data must have a wrapper class
            
        """
        
        if not self.isTable or self.tableWrapper is None:
            return
            
        return self.tableWrapper(self.data())
        
        
    
    def editTable(self):
        """
        Generic table editing function. Can be used with any node that has
        isTable flag set to True. It will launch a Table Editor panel with the
        table data from this node
        
        """
        if not self.isTable:
            return
            
            
        logger.debug('DataSourceSelector: Sending [%s] data to table editor' % self.typeInfo())
        data = self.tableData()
        source = self.source()
        path = self.path()
        
        if path:
            WindowTitle = "[%s] : %s" % (source.name(),path)
        else:
            WindowTitle = "Source: [%s] , Table: [%s]" % (source.name(),self.name())
        
        editor = self.API.addPanel(self.tableEditorPanel,WindowTitle)
        
        if source.name() == self.name():
            sourceLinkText = "%s" % (self.name())
        else:
            sourceLinkText = "%s:%s" % (source.name(),self.name())
        
        self.API.sendComms('addSource',editor.ID,data,sourceLinkText)
        
        # Get the MDI window for the editor panel
        if editor.window() is not None:
            logger.debug("Data source selector: Adding link [%s] to [%s]" % (source.name(),self.name()))
            source.addLink(editor.window())
            
            
    def menu(self):
        """
        Return a menu of actions that can be performed on this node.
        
        By default a 'copy path to clipboard' option is supplied for all nodes
        and if the node is a table of data then a 'Edit table' option is supplied.
        
        Output:
        -------
        menu : QMenu
            Populated menu of actions for this node. If there are no actions
            then return None
            
        """
        
        # Default menu
        # ----------------------
        menu = QMenu()
        
        menu.addAction(menu.tr("Edit %s" % self.typeInfo()),self.editTable)
        menu.addAction(menu.tr("Copy path to clipboard" ),self.valueToClipboard)
        
        # Return 
        return menu

            
            
    

#==============================================================================
#%% Datasource Wrapper
#==============================================================================
class DatasourceCreator():
    """
    This class is contains methods for creating datasources,
    flags to set certain properties, e.g. is the data source a file,
    It is used by the API as a resource to go to for loading functions
    file types etc.
    
    This class defines the skeleton and the required methods
    
    TODO : Make abstract class
    
    """
    
    def __init__(self):
        
        # Internal name used for referencing this source
        self.name = '<source name>'
        
        # Flags
        # =============
        self.isFile = False
        
        
        # Filetypes
        # ===================
        # list of file extensions that this source may use
        self.fileTypes = []
        
    # ========================================================================    
    # Required methods
    # ========================================================================
    
    def toNode(self,*parameters,**kwargs):
        """
        Function to convert source to DatasourceNode or derivative
        
        """
        
        pass
    
    def fileOpen(self,*parameters,**kwargs):
        """
        For files, a function to open the file.
        This will be accessed when the user chooses File/Open from
        menus
        
        """
        pass


#==============================================================================
#%% Datasource Table Wrapper
#==============================================================================

class BaseDatasetTableWrapper():
    """
    Wrapper for datasource datasets when sending to the TableEditor
    
    Makes standard functions for accessing rows and columns, inserting, 
    deleting
    
    """
    
    def __init__(self,array=None):
        """
        Create wrapper 
        
        Inputs
        ---------
        array : dataset type
        
        """
        
        
        # Store array
        self.array = array
        
        # Read only flag 
        # - prevents insertions and deletions
        self.readOnly = False
        
        # Formatter for the table editor
        self.formatter = DatasourceFormatter()
        

            
        
    def rowCount(self):
        pass
        
        
    def columnCount(self):
        pass
            
        
        
    def cell(self,row,col):
        """
        Return contents of array element given row and column
        
        """
        pass
        
        
    def setCell(self,row,col,value):
        """
        Set contents of array element given row and column
        
        """
        
        pass    
            
    
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
        
        pass
        
        
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
        pass        
    
        
        
    def columnHeaders(self):
        """
        Return the names of the columns
        
        For recarrays this is the dtype.names field for normal arrays this
        returns a list of numbers converted to strings
        
        """
        
        return self.array.columns.tolist()
        
        
        
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
        
        # Default format for floats
        return '%.4f'
            
            
            
    def getColumn(self,column_index):
        """
        Return a whole column as one numpy array
        
        """
        
        # check for valid column index
        if column_index > self.columnCount():
            return
            
        pass
    
    


#==============================================================================
#%% Datasource Table Wrapper - formatting class
#==============================================================================            



class DatasourceFormatter():
    """
    This class is for use with DatasourceTableWrapper classes.
    
    It provides a class that is used to return individual data values that are
    formatted into strings for displaying in a table.
    
    For example when data is displayed in a table editor, the table editor
    will get a DatasourceFormatter class from the table wrapper class, which
    it will use to display the data in the cells of the table.
    
    
    Example usage
    ------------------
    Create a formatter
    
    >>> fmt = DatasourceFormatter()
    
    Add format for a type of variable
    
    >>> fmt.addFormat(float,"%.3f")
    
    Add more complicated format using a function for a complex number
    
    >>> format_function = lambda z: "%.3f + j%.3f" % (z.real,z.imag)
    >>> fmt.addFormat(complex,function=format_function)
    
    Apply format to a variable
    
    >>> z = complex(1,2)
    >>> fmt.format(z)
    1.000 + j2.000
    
    """
    
    
    def __init__(self):
        
        
        # Formats are stored as a dictionary of Format() objects        
        self.formats = {}
        
        # Create standard 'built-in' formats
        self.addStandardFormats()
        
        
        
    def addStandardFormats(self):
        """
        Add standard formats to the class
        
        """
        
        # Add standard formats:
        # derived classes can just do add statements
        self.addFormat(float,'%.3f')
        self.addFormat(str,'%s')
        self.addFormat(int,'%i')
        format_function = lambda z: "%.3f + j%.3f" % (z.real,z.imag)
        self.addFormat(complex,function=format_function)
        
        format_function = lambda byteString: byteString.decode()
        self.addFormat(bytes,function=format_function)
        
        
        
    def addFormat(self,variable_type,format_string="",function=None):
        """
        Add a format to the stored format list
        
        Inputs
        ---------
        variable_type : type
            Type of variable to be formatted, basically the output of 
            type(var)
            
        format_string : str
            string giving the format to be returned
            
        function : function reference
            function used to format a variable
            
        """
        
        self.formats[variable_type] = Format(format_string,function)
        
        
    def format(self,variable):
        """
        Return variable as a formatted string
        
        Input:
        -------
        variable : anything
            
        Output
        ---------
        var_as_string : str
            string version of input variable
            
        """
        
        if variable is None:
            return ""
        
        var_type = type(variable)
        
        if var_type in self.formats:
            return self.formats[var_type].applyFormat(variable)
        else:
            return "Unknown type [%s]" % var_type.__name__
        
        
        
        
        
class Format():
    """
    Support class for DatasourceFormatter()
    
    This is an individual format store. It stores the data needed to create
    the formats that will be applied by the format() method in the 
    DatasourceFormatter class
    
    Example usage
    --------------
    
    Create a format
    
    >>> f = Format(var_type)
    
    """
    
    def __init__(self,formats="",function=None):
        
        self.format_strings = formats
        
        self.single_argument = False
        
        if function is None:
            self.function = lambda v,f: f % v
        else:
            self.function = function 
            if len(inspect.getfullargspec(function).args)==1:
                self.single_argument = True
            
        
        
    def applyFormat(self,variable):
        """
        Apply formatting function
        
        """
        # TODO This doesn't catch Nones, not sure why
        # Deal with None case
        if variable is None:
            return ""
        
        # Now do the normal case
        if self.single_argument:
            return self.function(variable)
        else:
            return self.function(variable,self.format_strings)
        
        
        
#==============================================================================
#%% Numpy data formatter
#==============================================================================
# Numpy data types are used in other multiple sourced so a dedicated formatter 
# is defined here.

def makeNumpyFormatter():
    """
    Make a formatter with all the numpy types in it
    
    Output
    -------
    formatter : DatasourceFormatter()
        
    """
    
    # Create a standard formatter
    # -------------------------------
    numpyFormatter = DatasourceFormatter()
    
    # Add numpy ints
    # ----------------------
    int_types = [np.int,np.int8,np.int16,np.int32,np.int64]
    
    for typ in int_types:
        numpyFormatter.addFormat(typ,'%i')
        
        
    # Add numpy floats
    # ----------------------
    float_types = [np.float,np.float16,np.float32,np.float64]
    
    for typ in float_types:
        numpyFormatter.addFormat(typ,'%.3g')
        
    # Add numpy complex
    # --------------------------
    complex_types = [np.complex,np.complex64,np.complex128]
    format_function = lambda z: "%.3g + j%.3g" % (z.real,z.imag)
    
    for typ in complex_types:
        numpyFormatter.addFormat(typ,function=format_function)
        
        
    # Add numpy strings
    # -------------------------
    string_types = [np.str_]
    
    for typ in string_types:
        numpyFormatter.addFormat(typ,'%s')
        
    # Add numpy bytes
    # ------------------------
    format_function = lambda byteString: byteString.decode()
    numpyFormatter.addFormat(typ,function=format_function)
        
        
    return numpyFormatter        
    

#==============================================================================
#%% Functions
#==============================================================================
def load_sources(path_list):
    """
    Load datasource creator classes from a list of paths
    
    Checks through the paths given for modules that have the __sources__ 
    attribute. This gives a list of source creator classes contained in that module.
    This function will then extract them into a list of instantiated class instances
    
    Inputs
    --------
    path_list : list of str
        list of paths where panel modules are located
        
        
    Outputs:
    ---------
    source_creators : dict
        dictionary where the key is the name of the source and the value is
        a class instance of the source creator class
        
    """
    
    # Initialise return variables
    # ---------------------------
    source_creators = {}
    
    
    
    # Handle null input case
    # ------------------------
    if not path_list:
        logger.debug("load_sources:Null path entered")
        return
    
    
    # Go through the path list finding panels
    # ---------------------------------------
    
    for path in path_list:
        logger.debug("load_sources: Looking in [%s]" % path)
        
        # Check for non-existent paths
        if not os.path.exists(path):
            logger.debug("Source loading: unknown path [%s]" % path)
            continue
        
        # Get list of .py files in this path
        file_list = os.listdir(path)
        
        # Look for .py files and import them
        for file in file_list:
            logger.debug("Datasource loading: File [%s]" % file)
            module_name,ext = os.path.splitext(file)
            
            # If it's a .py file then look for an attribute called
            # __sources__ which gives a dictionary of the available
            # panels. If exists then add to the return dictionary
            if ext == ".py":
                module = import_module_from_file(os.path.join(path,file))
                
                if hasattr(module,"__sources__"):
                    logger.debug("load_sources: Loading sources from [%s]" % file)
                    
                    # Create the source creator classes
                    for creator_class in module.__sources__:
                        # Instantiate an instance of the class
                        creator = creator_class()
                        
                        # Add instance to dict using the class name field
                        source_creators[creator.name] = creator
                        
                        logger.debug("load_sources: Loaded [%s]" % creator.name)
                    
                    
    return source_creators
    
    