# -*- coding: utf-8 -*-
"""
Created on Tue Jun  3 14:50:25 2014

@author: john

ScopePy Channel definitions
===================================

ScopePy channels are a virtual version of an oscilloscope channel. They are
defined internally as a class.

Version
==============================================================================
$Revision:: 178                           $
$Date:: 2016-08-06 07:46:28 -0400 (Sat, 0#$
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


#======================================================================
#%% Imports
#======================================================================
import logging
import os
import inspect

from numpy.lib.recfunctions import stack_arrays

import bisect
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# Custom widgets
import ScopePy_graphs as graph
from ScopePy_widgets import *
from ScopePy_utilities import import_module_from_file


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


#======================================================================
#%% Constants
#======================================================================


DEBUG = False

# Define chunk mode constants
CHUNK_MODE_ALL = 'all'
CHUNK_MODE_LATEST = 'latest'
CHUNK_MODE_FIRST = 'first'
CHUNK_MODE_SELECTION = 'selection'
CHUNK_MODE_ROLLOVER = 'rollover'

CHUNK_MODES = [CHUNK_MODE_ALL,CHUNK_MODE_LATEST,CHUNK_MODE_FIRST,CHUNK_MODE_SELECTION,CHUNK_MODE_ROLLOVER]

# Functions for extracting the x and y columns (first & second) from a numpy
# structured array
Xdata = lambda array: array[array.dtype.names[0]]
Ydata = lambda array: array[array.dtype.names[1]]

#======================================================================
#%% plot linestyle class
#======================================================================
       
 
class plotLineStyle():
    """ Container class for carrying all data for the visual appearance
    of a plot:
        line colour, marker type, marker colour, marker fill colour
        
    This allows all these values to be passed around as one object
    """
    
    def __init__(self,lineColour='#0000ff',lineDashStyle = Qt.SolidLine,marker='o', markerColour='#0000ff',markerFillColour = '#0000ff',markerSize=2):
        # Plotting config
        self.lineColour = lineColour
        self.lineDashStyle = lineDashStyle
        self.markerColour = markerColour
        self.marker = marker
        self.markerFillColour = markerFillColour    
        self.markerSize = markerSize
        
    

    def __str__(self):
        """
        Display line styles - for debugging
        
        """
        
        txt = [
            "Plot Linestyle:",
            "-"*40,
            "Line colour = %s" % self.lineColour,
            "Marker = %s" % self.marker,
            "Marker outline colour = %s" % self.markerColour,
            "Marker fill colour = %s" % self.markerFillColour,
            ]
            
        return "\n".join(txt)
        
    def __repr__(self):
        return self.__str__()
        
        

#======================================================================
#%% scopePyChannel class
#======================================================================


class ScopePyChannel(QObject):
    """ 
    Virtual scope channel definition
    
    ScopePy can have multiple channels they are stored in a dictionary 
    channel_dict in the main GUI. Each dictionary value is an object of
    scopePyChannel class.
    
    This class holds the data for each channel as well as the plot line styles.
    It also has methods for controlling how the chunks are used.
    
    """
    
    
    
    
    def __init__(self,channelLabel="Unknown",lineStyle=plotLineStyle()):
        """ Create instance of a channel at the number specified
        
        Input
        -----
        channelLabel = string 
            label for the channel - appears in channel tree view
        lineStyle = plotLineStyle object - 
            see plotLineStyle and channelColours classes
        
        """
        
        # Initialise object
        # needs to be a QObject() to be able to emit signals
        super(ScopePyChannel,self).__init__()
        
        # Setup channel meta data
        # --------------------------
        
        self.name = channelLabel
        
        # Overall min and max values
        self.xMinValue = None
        self.xMaxValue = None
        
        self.yMinValue = None
        self.yMaxValue = None
        
        # x and y axis labels for referencing recarray columns
        self.x_axis = ''
        self.y_axis = ''
        
        # Column names of all data in a chunk
        self.column_names = []
        
        # Plotting config
        self.plot_lineStyle = lineStyle
  
        
        # Channel data storage
        # -------------------------
        # Channel data is stored as a list or numpy recarrays
        # these will also be known as chunks
        self.data_list = []
        
        # Number of chunks (= len(self.data_list))
        self.chunks = 0
        
        # Max number of chunks that can be used
        # Used for Rollover chunk mode
        self.rollover = np.inf
        
        # Chunk mode
        # How data is to be returned from chunks
        self.chunkMode = CHUNK_MODE_ALL
        
        
        
        # Data empty flag
        # Use this as a quick way to determine if any data has been 
        # added yet. This is to avoid searching the data list
        self.data_empty = True
        
        # Channel plot items
        # -------------------------------
        # When a channel is plotted in a tab the plotDataItem is 
        # stored in this class so that it can be easily reached
        # when updating.
        # This allows changing the attributes of a channel
        # and reflecting the change in every plot
        self.plotDataItemList = []
        
        
    def __str__(self):
        """
        Display channel on command line
        
        """
        
        txt = [
            "ScopePy channel: %s" % self.name,
            "="*40,
            "x axis name = %s" % self.x_axis,
            "y axis name = %s" % self.y_axis,
            "Chunks = %i" % self.chunks,
            "\n",
            str(self.plot_lineStyle)
            ]
            
        return "\n".join(txt)
        
        
    def __repr__(self):
        return self.__str__()
        
        
    @property
    def isEmpty(self):
        """
        Check if a channel contains any data. Used for graph plotting
        
        Output:
        --------
        isEmpty : bool
            True if empty
            
        """
        
        return self.data_list == []
        
        
        
        
    def clearChannelData(self):
        """
        Remove all data from channel and reset number of chunks
        
        """
        
        self.data_list = []
        self.data_empty = True
        self.chunks = 0
        
        
        
    def addData2Channel(self,recArray,update_signal=True):
        """ Add a chunk of data to the channel
        
        Check the data has the same column names as previous chunks
        Add chunk to the list
        Update min and max values
        
        Inputs
        ------
        recArray = numpy recarray with column names populated
        
        update_signal : bool
            Set to True to trigger an update signal (usually for plots)
            Set to False not to trigger update signal (where speed is needed)
        
        Outputs
        --------
        success = True or False
        
        """
        
        # Get column names
        column_names = recArray.dtype.names
            
        # Add x and y axis names
        x_axis = column_names[0]
        y_axis = column_names[1]
        
        # Create new array with a third column for transparency
        newArray = np.zeros(len(recArray),
                            dtype = [(x_axis,float),
                                    (y_axis,float),
                                    ('transparency',float)])
                                    
        newArray[x_axis] = recArray[x_axis]
        newArray[y_axis] = recArray[y_axis]
        # Initalise transparency with chunk number
        newArray['transparency'] = self.chunks
        
        
        
        # Set the min and max
        xmin = newArray[x_axis].min()
        xmax = newArray[x_axis].max()
        ymin = newArray[y_axis].min()
        ymax = newArray[y_axis].max()
        
        if not self.xMinValue or xmin < self.xMinValue:
            self.xMinValue = xmin
        
        if not self.xMaxValue or xmax > self.xMaxValue:
            self.xMaxValue = xmax
            
        if not self.yMinValue or ymin < self.yMinValue:
            self.yMinValue = ymin
        
        if not self.yMaxValue or ymax > self.yMaxValue:
            self.yMaxValue = ymax
            
        
        
        # Add new data
        if self.data_empty:
            # Set the axis names
            self.x_axis = x_axis
            self.y_axis = y_axis
        
            # Add chunk of data to the list
            self.data_list.append(newArray)
            
            # Log the column names
            self.column_names = column_names
            
            # No longer empty so set the flag
            self.data_empty = False
            
        else:
            # Check first two column names are the same
            # note 0:2 is interpreted as 0:1 in Python
            if self.column_names[0:2] == recArray.dtype.names:
                self.data_list.append(newArray)
                
                
            else:
                # Don't add data if the column names
                # don't match
                return False
                
        # Increment the number of chunks
        self.chunks += 1
        
        # Trigger any plot updates
        if update_signal:
            self.updatePlots()
        
        # If we get here then everything worked so return True
        return True
        
        
    def setAxisName(self,axis,newName):
        """ Set the name of an individual axis
        
        Inputs
        ------
        axis = 'x' or 'y'
        newName = string name for axis
        
        """
        axis = axis.lower()
        
        # Check axis
        if axis not in ['x','y']:
            return
            
        # The data is stored in recarrays. The axis names are stored in the
        # recarray names field as a tuple. Can't change individual elements
        # of a tuple so we have to replace the whole names field.
        if axis == 'x':
            newAxisNames = (newName,self.y_axis)
            # update axis field in class
            self.x_axis = newName
        else:
            newAxisNames = (self.x_axis,newName)
            # update axis field in class
            self.y_axis = newName
            
        # Replace existing names in all chunks
        for chunk in range(self.chunks):
            self.data_list[chunk].dtype.names = newAxisNames
            


            
    def data(self,chunkMode=None,chunkList = [0]):
        """
        Return scope data according to the chunk mode specified.
        
        Inputs
        ------------
        chunkMode = string giving the policy type
        chunkList = list of chunks to be returned
        
        Outputs
        -----------
        dataArray = numpy recarray containing all the chunks specified in two
                    columns
        
        """
        if DEBUG:
            print("data function\n-----------------------------\n")
            print("Chunk Policy = %s" % chunkMode)
            print("Chunks available %d" % self.chunks)
            
        if not chunkMode:
            chunkMode = self.chunkMode
        
        # Validate input policy
        # =============================           
        if chunkMode not in CHUNK_MODES:
            print("Policy is not in list - quit")
            return
            
        if self.chunks == 0:
            # Empty channel do nothing
            print("No chunks - quit")
            return
            
        # Select data according to the policy
        # =====================================
        if chunkMode == CHUNK_MODE_LATEST:
            chunkList = [self.chunks-1]
            
        elif chunkMode == CHUNK_MODE_FIRST:
            chunkList = [0]
            
        elif chunkMode == CHUNK_MODE_ALL:
            chunkList = list(range(self.chunks))
            
        elif chunkMode == CHUNK_MODE_ROLLOVER:
            # In this mode we return a maximum number of chunks up to the value
            # in self.rollover.
            if self.chunks < self.rollover:
                # Number of chunks is less than the rollover
                chunkList = list(range(self.chunks))
            else:
                # More chunks than rollover value, return the latest chunks
                chunkList = list(range(self.chunks-self.rollover,self.chunks))
            
        elif chunkMode == CHUNK_MODE_SELECTION:
            # Check chunkList is not empty
            if not chunkList:
                return
            if chunkList == [-1]:
                chunkList =[self.chunks-1]
                
        if DEBUG:
            print("Chunk list:",chunkList)
                
        # Extract the specified chunks and return
        return self.getDataFromChannel(chunkList)
            
            
            
            
    def getDataFromChannel(self,chunkList):
        """
        Basic extraction of data combining all specified chunks
        into one recarray
        
        Inputs
        ---------------
        chunkList: list
            list of numpy recarrays
        """
        
        if DEBUG:
            print("getDataFromChannel function\n-----------------------------\n")
            print("Chunk List = ",chunkList)
        
        # Exit if list is empty
        if not chunkList:
            return
        
        # Extract all the selected chunks into a separate list
        data2Return = []
        for index in chunkList:
            data2Return.append(self.data_list[index])
            
        totalData = stack_arrays(data2Return, asrecarray=True, usemask=False)
            
        if DEBUG:
            print("Selected data")
            print(totalData)
            
        # Stack all the selected rearrays together
        # and return
        return totalData
        
        
    @property
    def x(self):
        """
        Convenience function/property for getting all x data using the current
        chunk mode
        
        """
        
        return self.data()[self.x_axis]
        
        
    @property    
    def y(self):
        """
        Convenience function for getting all y data using the current
        chunk mode
        
        """
        
        return self.data()[self.y_axis]
    
        
        
    def updatePlots(self):
        """
        Trigger all plots that have this channel to update.
        
        This is used when a new data chunk arrives 
        
        Sends the signal "updateChannelPlot" with channel name
        
        """
        
          
        #  Trigger update to any connected plots
        self.emit(SIGNAL("updateChannelPlot"), self.name)
        
        
    # -----------------------------------------------------------
    # Importing/Exporting functions
    # -----------------------------------------------------------
    def to_dict(self):
        """
        Export the channel to a dictionary.
        
        This is useful for saving channels to files. It dumps the name, the
        data and the line styles into a dictionary
        
        Outputs
        ---------
        channel_export : dict
            Dictionary with the following keys:
                'name' : channel name
                'data' : all data as a list of chunks
                'plotstyle' : line and marker colours and styles
                
        """
        
        channel_export = {'name':self.name,
                          'data':self.data_list,
                          'plotstyle':self.plot_lineStyle
                          }
                          

        return channel_export
        
        
    def from_dict(self,channel_import):
        """
        Import channel from dictionary created by to_dict() method.
        
        Used for loading channels from files
        
        Input
        ------
        channel_import : dict
            Dictionary with the following keys:
                'name' : channel name
                'data' : all data as a list of chunks
                'plotstyle' : line and marker colours and styles
                
        Output
        -------
        success : bool
            True = successfully imported
            False = cannot import, dictionary probably doesn't have correct
            format.
                
        
        Example usage
        --------------
        >>> new_channel = ScopePyChannel()
        >>> new_channel.from_dict(imported_channel_dict)
        
        
        """
        
        # Validate input dictionary
        # ---------------------------
        if not all([x in channel_import for x in ['name','data','plotstyle']]):
            logger.debug("ScopePyChannel:from_dict : Missing keys in import dict")
            return False
            
        if len(channel_import['data']) == 0:
            logger.debug("ScopePyChannel:from_dict : No data in import dict")
            return False
            
        if not isinstance(channel_import['data'][0],np.ndarray):
            logger.debug("ScopePyChannel:from_dict : Data in import dict is not numpy array")
            return False
            
        column_names = channel_import['data'][0].dtype.names
        
        if len(column_names) < 2:
            logger.debug("ScopePyChannel:from_dict : Data array in import dict has less than 2 columns")
            return False
            
        # Import data from dictionary into channel properties
        # ----------------------------------------------------
            
            
        # Read data into channel
        self.name = channel_import['name']
        self.data_list = channel_import['data']
        self.plot_lineStyle = channel_import['plotstyle']
        
        # Update chunks
        self.chunks = len(self.data_list)
        self.data_empty = False
        
        # Update column names
        self.x_axis = column_names[0]
        self.y_axis = column_names[1]
        
        return True
            
  

#======================================================================
#%% Group channel
#======================================================================
class GroupChannel(ScopePyChannel):
    """
    Group channels are linked to data source tables. They represent two columns
    from a table.
    
    TODO : They will allow linking to the other columns in the table

    """
    
    
    def __init__(self,datasourceTableWrapper,x_column_name,y_column_name,*args,**kwargs):
        """
        
        Inputs
        ----------
        datasourceTableWrapper : DatasourceTable object or derivative
        
        
        """
        
        # Initialise as ScopePy channel
        super(GroupChannel,self).__init__(*args,**kwargs)
        
        # Check the input has the right methods
        assert hasattr(datasourceTableWrapper,'getColumnByName'), 'GroupChannel: Initialisation with an object that is not a table wrapper'
        assert hasattr(datasourceTableWrapper,'columnHeaders'), 'GroupChannel: Initialisation with an object that is not a table wrapper'
        
        
        # Input validation
        # ---------------------------
        headers = datasourceTableWrapper.columnHeaders()
        assert x_column_name in headers, 'GroupChannel: Datasource table does not have a column called %s' % x_column_name
        assert y_column_name in headers, 'GroupChannel: Datasource table does not have a column called %s' % y_column_name
        
        # Store links to data table
        # ----------------------------
        self.data_table = datasourceTableWrapper
        self.x_axis = x_column_name
        self.y_axis = y_column_name
        
        
        # Set Chunk handling
        # ------------------------------
        # This channel type doesn't support chunks, so just set here and forget
        
        # Number of chunks 
        self.chunks = 1
        
        # Chunk mode
        self.chunkMode = CHUNK_MODE_ALL
        
        
    
    @property
    def isEmpty(self):
        """
        Check if a channel contains any data. Used for graph plotting
        
        Note:
        This is here for compatibility. A group channel should always have
        data because it can only be created from an existing data set.
        
        Output:
        --------
        isEmpty : bool
            Always returns False
            
        """
        
        return False
        
        
    def data(self,**kwargs):
        """
        Return data from table as numpy recarray
        
        Outputs
        ---------
        data_array : numpy recarray
            Two column array
            
        """
        
        # The input **kwargs is to be the same as the ScopePyChannel.data() 
        # function, no action is taken
        
        # Get the two columns
        # ------------------------
        x_data = self.data_table.getColumnByName(self.x_axis)
        y_data = self.data_table.getColumnByName(self.y_axis)
        
        data_array = np.zeros(len(x_data),[(self.x_axis,float),(self.y_axis,float)])
        
        data_array[self.x_axis] = x_data
        data_array[self.y_axis] = y_data
        
        
        return data_array
        
        

                    
#======================================================================
#%% Math channel
#======================================================================

                    
class MathChannel(ScopePyChannel):
    """
    Math channels are derived from other channels, they apply a function
    to the source channel and return a transformed version of the data

    """
    
    
    def __init__(self,source_channels,math_function,*args,**kwargs):
        """
        
        Inputs
        ----------
        source_channels : list of ScopePyChannels
        
        channel_function : MathFunction() class object
            
            
        
        """
        
        # Initialise as ScopePy channel
        super(MathChannel,self).__init__(*args,**kwargs)
        
        
        # Store source channel and function
        self.source = source_channels
        self.mathFunction = math_function
        
        # Copy axis labels from first source channel
        self.x_axis = self.source[0].x_axis
        self.y_axis = self.source[0].y_axis     
        
        # Copy data from source channel
        self.updateFromSource()
        
        # Link to source channels for updates
        for channel in self.source:
            self.connect(channel,SIGNAL("updateChannelPlot"),self.updateAll)
        
        
        
        
    def updateFromSource(self):
        """
        Update data from source channel.
        this is usually triggered by the source channel
        """
        
        logger.debug("MathFunction [%s]: Updating from source" % self.name)
           
        self.chunks = self.source[0].chunks
        
        # TODO : Chunks will need careful handling to make sure all channels 
        # have the same number.
        
        
    def updateAll(self):
        """
        Update from the source channel and then send the updatePlots signal
        """
        
        self.updateFromSource()
        self.updatePlots()
        
        
    def data(self,**kwargs):
        """
        Re-implementation of the data() function 
        
        Returns an array with the transformed x and y values
        
        Output
        -------
        data_array : numpy structured array
            data_array[x] = x_out
            data_array[y] = y_out
        
        """               
        
        # Apply function to source channels
        x_out,y_out = self.mathFunction(self.source)
        
        dtype = [(self.x_axis,float),(self.y_axis,float)]
        
        data_array = np.zeros(len(x_out),dtype)
        
        data_array[self.x_axis] = x_out
        data_array[self.y_axis] = y_out
        
        return data_array
        
        
    def getSourceData(self,**kwargs):
        """
        Get the data from all source channels and put in a list
        
        """
        
        source_data = []
        
        for channel in self.source:
            source_data.append(channel.data(**kwargs))
            
        return source_data
            
        
    @property
    def isEmpty(self):
        
        check_empty = [chan.isEmpty for chan in self.source]
        
        
        return all(check_empty)
        
    
        
        
        
        
        
class MathFunction():
    """
    Base class for MathChannel functions
    Gives the basic methods and properties needed to define math functions
    This class is used as the basis for any Math channel functions
    
    Example usage for simple functions
    -----------------------------------
    >>> myFunc = MathFunction()
    >>> myFunc.name = "func1"
    >>> myFunc.description = "An example function"
    >>> myFunc.function = lambda channel : (channel.x,channel.y**2)

    For more complicated functions that have internal parameters then the class
    can be inherited.
    """
    
    # Define some validators for use in QLineEdits
    numeric_only = r"[\.0-9\-\+e\*\/]+"
    
    
    def __init__(self):
        """
        Make a Math channel function with the specified name
        
        """
        
        # Display name
        self.name = 'no function'
        
        # Description
        self.description = 'No description'
        
        # Function
        # Must be of the form:
        #   x_out,y_out = f(list_of_channels)
        # and it must be array friendly
        self._function = None
        self.function_inputs = None
        self.number_function_inputs = 0
        
        # For single inputs this sets whether it is a list of channels or just
        # a single one
        self.is_list_input = False
        
        # Parameters
        # Extra parameters that the function can use
        # Dictionary of [parameter_name,parameter_value] pairs
        self.parameters = {}
        
        
        # Set default validator
        self.validator = self.numeric_only
        
        
        
    def __repr__(self):
        
        return "<Math Channel function: %s>" % self.name
        
        
    def __call__(self,channel_list):
        """
        Execute the function on the list of source channels
        
        Inputs
        ------
        channel_list : list of ScopePy channels
            
        
        """
        
        if self.is_list_input:
            # Function requires list input
            return self._function(channel_list)
        else:
            # function requires individual inputs
            return self._function(*channel_list)
        
        
        
    def getFunction(self):
        """
        getter for the function
        """
        
        return self._function
        
        
    def setFunction(self,inputFunction):
        """
        The set method behind self.function
        
        """
        
        # Get number of input channels
        # = number of arguments
        arg_spec = inspect.getargspec(inputFunction)
        
        self.function_inputs = arg_spec.args
        self.number_function_inputs = len(self.function_inputs)
        
        # Store function
        self._function = inputFunction
        
    
        
    function = property(getFunction,setFunction)
    
        

def load_math_functions(path_list):
    """
    Load panels from a list of paths
    
    Checks through the paths given for modules that have the mathFunctions list 
    attribute. This gives a list of MathFunction class instances.
    This function will then extract them into a list of classes
    
    Inputs
    --------
    path_list : list of str
        list of paths where panel modules are located
        
    Outputs:
    ---------
    panel_classes : dict
        dictionary where the key is the name of the panel, to be used
        on menus etc and the value is a class reference
        
    """
    
    # Initialise return variable
    # ---------------------------
    math_functions = []
    
    
    # Handle null input case
    # ------------------------
    if not path_list:
        logger.debug("load_math_functions:Null path entered")
        return
    
    
    # Go through the path list finding math functions
    # ---------------------------------------
    
    for path in path_list:
        logger.debug("load_math_functions: Looking in [%s]" % path)
        
        # Check for non-existent paths
        if not os.path.exists(path):
            logger.debug("load_math_functions: unknown path [%s]" % path)
            continue
        
        # Get list of .py files in this path
        file_list = os.listdir(path)
        
        # Look for .py files and import them
        for file in file_list:
            logger.debug("load_math_functions: File [%s]" % file)
            module_name,ext = os.path.splitext(file)
            
            # If it's a .py file then look for an attribute called
            # mathFunctions which gives a dictionary of the available
            # panels. If exists then add to the return dictionary
            if ext == ".py":
                module = import_module_from_file(os.path.join(path,file))
                
                if hasattr(module,"mathFunctions"):
                    logger.debug("load_math_functions: Loading panels from [%s]" % file)
                    math_functions += module.mathFunctions
                    
    return math_functions 
    
     
          
    


        

#======================================================================
#%% channelColours class
#======================================================================
import ScopePy_colours_and_shapes as col_shapes

defaultColourList = col_shapes.default_palette()

class channelColours():
    """ Class for allocating default colours to each channel
    as they come in.
    
    Use to get default line and symbol colours, plus the symbol itself
    
    
    """
    

    lineColourList = defaultColourList 
    lineColourIndex = 0
    
    markerColourList = defaultColourList
    markerColourIndex = 0
    
    markerList = list(col_shapes.make_markers().keys())
    markerIndex = 1
    
    markerFillList = defaultColourList
    markerFillIndex = 1
    
    
    
    
    def __init__(self):
        """ Make channelColours class instance
        
        TODO : Add functions to read in longer colour lists
        """
        
        # For speed log the length of the colour list(s)
        # Other functions can use this instead of calling len() every time
        self.nLineColours = len(self.lineColourList)-1
        self.nMarkers = len(self.markerList)-1
        self.nMarkerColours = len(self.markerColourList)-1
        self.nMarkerFill = len(self.markerFillList)-1
        
    
    
    def incrementColours(self):
        """Increment to next set of colours
        """
        

        # Line colours
        # ---------------------        
        # Check colour index against number of colours
        if self.lineColourIndex < self.nLineColours:
            # increment if less than total
            self.lineColourIndex += 1
        else:
            # reset if reached last colour
            self.lineColourIndex = 0
            
        # Markers
        # ----------
        if self.markerIndex < self.nMarkers:
            # increment if less than total
            self.markerIndex += 1
        else:
            # reset if reached last colour
            self.markerIndex = 0
            
        # Marker colours
        # ------------------------
        if self.markerColourIndex < self.nMarkerColours:
            # increment if less than total
            self.markerColourIndex += 1
        else:
            # reset if reached last colour
            self.markerColourIndex = 0
            
        # Markers fill colours
        # ---------------------
        if self.markerFillIndex < self.nMarkerFill:
            # increment if less than total
            self.markerFillIndex += 1
        else:
            # reset if reached last colour
            self.markerFillIndex = 0
                  
            
            
    # Get functions
    # These are the main functions for getting a set of colours
    # for an incoming channel
    def getLineColour(self):
        """ Return line colour
        """
        return self.lineColourList[self.lineColourIndex]
        
    def getMarkerColour(self):
        """ Return marker colour
        """
        return self.markerColourList[self.markerColourIndex]
        
    def getMarker(self):
        """ Return marker type symbol
        """
        return self.markerList[self.markerIndex]
        
    def getMarkerFillColour(self):
        """ Return marker fill colour
        """
        return self.markerFillList[self.markerFillIndex]
        
        

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
#%% Channel Tree class
#======================================================================


CHANNEL = 0
LINESTYLE = 1
XAXIS = 0
YAXIS = 1
TREE = 0
SETTINGS = 1

class ChannelTreeModel(QAbstractItemModel):

    def __init__(self, channelDict, parent=None):
        super(ChannelTreeModel, self).__init__(parent)
        self.columns = 2
        self.root = BranchNode("")
        self.headers = ["Channel","Settings"]
        # Reference to channel dictionary
        #  where all the channel data is held
        self.channelDict = channelDict
        



    def addChannel(self, channel, callReset=True):
        """ 
        Add new channel or update existing channel
        
        Inputs
        --------
        channel = string name of channel, used as a key for channelDict
        """
        
        # Create new channel branch with channel name as the label
        # ---------------------------------------------------------
        root = self.root
        
        # Check if the channel already exists
        # TODO : This seems to be failing sometimes
        branch = root.childWithKey(channel.lower())
         
        if branch:
            
            # Channel exists, only update chunks
            # Note the key must be lower case
            chunksChild = branch.children[2][NODE]
            
            logger.debug("Existing Branch found:[%s]" % channel)
            logger.debug("Updating chunks: [%d]" % self.channelDict[channel].chunks)
          
            
            chunksChild.setField(1,"%d" % self.channelDict[channel].chunks)
            self.reset()
            return
            
        else:
            branch = BranchNode(channel)
            
       
        logger.debug("Adding new channel to tree: [%s]" % channel)
        if root.children:
            logger.debug("Current Channels are [%s]" % ",".join(root.getChildren()))
        
        # Add channel parameters:
        # -----------------------------------
        
        # x axis
        items = ['x axis',self.channelDict[channel].x_axis]
        branch.insertChild(LeafNode(items, branch))
        
        # y axis
        items = ['y axis',self.channelDict[channel].y_axis]
        branch.insertChild(LeafNode(items, branch))
        
        # Chunks
        items = ['Chunks',"%d" % self.channelDict[channel].chunks]
        branch.insertChild(LeafNode(items, branch))
        
        # Add branch to root
        root.insertChild(branch)       
        
        
        if callReset:
            self.reset()


    def deleteChannel(self,channel_name,callReset=True):
        """
        Delete channel from tree
        
        Input
        ------
        channel_name : str
        
        """        
        
        self.root.deleteChild(channel_name)
        
        if callReset:
            self.reset()
        
        
        

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
            if isinstance(node, BranchNode):
                if index.column() == CHANNEL:
                    return "Channel name"
                elif index.column() == LINESTYLE:
                    return "Line styles"
            else:
                if index.column() == SETTINGS and index.row() in [XAXIS,YAXIS]:
                    return "Double click or F2 to edit"
                    
                    
        if role == Qt.StatusTipRole:
            if isinstance(node, BranchNode):
                if index.column() == CHANNEL:
                    return "Double click or select and press F2 to edit"
                elif index.column() == LINESTYLE:
                    return "Double click or select and press F2 to edit"
                else:
                    return ""
            else:
                if index.column() == SETTINGS and index.row() in [XAXIS,YAXIS]:
                    return "Double click or select and press F2 to edit"
                else:
                    return ""    
            
                
        
        # Display role from here on
        # ==================================================================
                    
        if role != Qt.DisplayRole:
            return None          
        
        if isinstance(node, BranchNode):
            # TODO : This could be where to insert line colour editing
            if index.column() == CHANNEL:
                return node.toString()
            elif index.column() == LINESTYLE:
                # TODO : likely error place
                return self.channelDict[node.name].plot_lineStyle
            # old code
            #return node.toString() if index.column() == CHANNEL else "<line styles>"
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
        
#        if DEBUG:
#            print("\n\t Row,Col = (%d,%d) %s" % (index.row(),index.column(),type(node)))
        
        # Branch node:
        #   Both channel name and line style are selectable and editable
        if isinstance(node,BranchNode):
            # Separate the two columns
            # even though we return the same flags, this allows
            # them to be separately selected
            if index.column() == CHANNEL:
                return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable
                
            if index.column() == LINESTYLE:
                return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable
            
        # Leaf node :
        #  Only second column is editable and selectable and then only for
        #  first 2 rows : x and y axis names
        if isinstance(node,LeafNode):
            
                
            if index.column() == SETTINGS and index.row() in [XAXIS,YAXIS]:
                return Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable
            else:
                return Qt.ItemIsEnabled
                
                
    def setData(self,index,value,role=Qt.EditRole):
        """ Required method for changing data in tree model
        """
        
        if index.isValid() and 0<= index.row() < len(self.root):
            if DEBUG:
                print("\n\nSetting data")
                print("\tValue = %s" % type(value))
                
            if role == Qt.EditRole:
                # Get the node
                node = self.nodeFromIndex(index)
                column = index.column()
                
                if DEBUG:
                    print("Node = %s : column = %d" %(type(node),column))
                
                # Edit channel name and line style
                if isinstance(node,BranchNode):
                    if column == CHANNEL:
                        # Update channel dictionary with new name
                        self.channelDict[value] = self.channelDict.pop(node.name)
                        
                        # Update tree
                        node.name = value                        
                        
                        
                    elif column == LINESTYLE:
                        # TODO : Does this actually work?
                        
                        lineStyles = value
                        
                        # Update line styles into channel dict
                        self.channelDict[node.name].plot_lineStyle = lineStyles
                        
                        
                    
                # Edit channel x and y axis names
                elif isinstance(node,LeafNode):
                    # Get channel name for referencing in channel dictionary
                    channel = node.parent.name
                    
                    # edit x axis
                    if column == XAXIS:
                        # Update in channel dictionary
                        self.channelDict[channel].setAxisName('x',value)
                        
                        # Update in model
                        node.setField(XAXIS,value)
                        
                    # edit y axis
                    elif column == YAXIS:
                       # Update in channel dictionary
                        self.channelDict[channel].setAxisName('y',value)
                        
                        # Update in model
                        node.setField(YAXIS,value)
                        
                    
                self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),index,index)
                return True
                
        return False
                    
                
                
    def getSelectedChannelsFromIndex(self,modelIndexList):
        """ Get any channel names that have been selected
        
        Go through the selected items list, ignore anything that isn't a branch node
        If it is a branch node then extract the channel name.
        Return all the channel names in a list
        
        Output
        ------
        channelList = list of channel names selected
        """
        # Check the list is not empty
        if not modelIndexList:
            return
            
        channelList = []
        
        for index in modelIndexList:
            node = self.nodeFromIndex(index)
            
            # Add to list if the node is a branch and the first column
            # is selected
            if isinstance(node,BranchNode):
                if index.column() == CHANNEL:
                    channelList.append(node.name)
                
        return channelList
            
            
#======================================================================
#%% Channel Tree delegate class
#======================================================================
      
        
# TODO : Adapt this to the channel tree
        
class channelTreeDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        super(channelTreeDelegate, self).__init__(parent)
        



    def sizeHint(self, option, index):
        # Keep this here in case it's needed later
        return QStyledItemDelegate.sizeHint(self, option, index)
        
    

    def paint(self,painter,option,index):
        
        # Get node type
        node = index.model().nodeFromIndex(index)
                                                  
        # If this is the line style column do a custom paint
        if isinstance(node,BranchNode) and index.column() == LINESTYLE:
#            if DEBUG:
#                print("\n-------------------------------------")
#                print("channelTreeDelegate: paint method")
#                print("\tThis is where the legendLine is being painted\n")
#                print(painter)
#                print(option.rect)
#                print(index)
#                print("-------------------------------------\n")
                
            # Get selection status
            isSelected = option.state & QStyle.State_Selected
                
            # Draw the legend line    
            legend = legendLine()
            
            
            channel = node.name
            
            # Set line styles into legendLine widget
            painter.save()
            legend.lineStyles = index.model().channelDict[channel].plot_lineStyle

            
            legend.paint(painter,option.rect,isSelected)
            painter.restore()
            
            # Draw the test rectangle
            #painter.save()
            #painter.fillRect(option.rect,Qt.red)
            #painter.translate(option.rect.x(),option.rect.y())
            #painter.restore()
            
        else:
            # Use default paint functions
            QStyledItemDelegate.paint(self,painter,option,index)
           
            
        

    def createEditor(self, parent, option, index):
        """ Provide an editor for the line style of the currently selected
        channel
        """
        
        # Get node type
        node = index.model().nodeFromIndex(index)
      
        
        # Exit if this is not a branch node
        if not isinstance(node,BranchNode):
            return QStyledItemDelegate.createEditor(self, parent, option,
                                                    index)
        
        if index.column() == LINESTYLE:
            if DEBUG:
                print("\n-------------------------------------")
                print("channelTreeDelegate: createEditor")
                print("\nThis is where the legendLine is being called")
                print(parent)
                print("-------------------------------------\n")
                
            editor = legendLine(parent)
            
            # Connect change signal to commit and close editor
            self.connect(editor,SIGNAL("LegendLineChanged"),self.commitAndCloseEditor)
            self.connect(editor,SIGNAL("LegendLineEditFinished"),self.commitAndCloseEditor)
            
            return editor
        else:
            return QStyledItemDelegate.createEditor(self, parent, option,
                                                    index)


    def commitAndCloseEditor(self):
                    
        editor = self.sender()
        if isinstance(editor, legendLine):
            if DEBUG:
                print("\n-------------------------------------")
                print("channelTreeDelegate: commitAndCloseEditor")
                print("\nlegendLine commit is being called")
                print(parent)
                print("-------------------------------------\n")
            
            self.emit(SIGNAL("commitData(QWidget*)"), editor)
            self.emit(SIGNAL("closeEditor(QWidget*)"), editor)
            self.emit(SIGNAL("LineStyleChanged"))


    def setEditorData(self, editor, index):
        """ Set the line style editor of the current channel
        """
        
        # Get node type
        node = index.model().nodeFromIndex(index)
        
        # Exit if this is not a branch node
        if not isinstance(node,BranchNode):
            return  QStyledItemDelegate.setEditorData(self, editor, index)
                                                    
                                                    
        if index.column() == LINESTYLE:
            # Get line styles from channel dictionary
            channel = node.name
            
            # Set line styles into legendLine widget
            editor.lineStyles = index.model().channelDict[channel].plot_lineStyle
                   
            
        else:
            QStyledItemDelegate.setEditorData(self, editor, index)


    def setModelData(self, editor, model, index):
        """ Set data from widget back into the model
        
        """
        
        # Get node type
        node = index.model().nodeFromIndex(index)
        
        # Exit if this is not a branch node
        if not isinstance(node,BranchNode):
            QStyledItemDelegate.setModelData(self, editor, model, index)
            return
        
        if index.column() == LINESTYLE:
            # Copy editor line styles into model
            model.setData(index, editor.lineStyles)
        
        else:
            QStyledItemDelegate.setModelData(self, editor, model, index)
            
            
            


#======================================================================
#%% Group Tree
#======================================================================

class GroupTreeModel(QAbstractItemModel):
    """
    Model for the Group panel
    
    This might be overkill for the group selector, but it allows for expansion
    
    """

    def __init__(self, groupDict, parent=None):
        super(GroupTreeModel, self).__init__(parent)
        self.columns = 2
        self.root = BranchNode("")
        self.headers = ["Group","Information"]
        # Reference to group dictionary
        #  where all the group data is held
        self.groupDict = groupDict



    def addGroup(self, groupName, callReset=True):
        """ 
        Add new group or update existing group
        
        Inputs
        --------
        groupName : str
            string name of group, used as a key for groupDict
        """
        
        
        
        
        # Create new group branch with group name as the label
        # ---------------------------------------------------------
        root = self.root
        
        # Check if the channel already exists
        branch = root.childWithKey(groupName.lower())
        
        # Get group column names for adding or updating
        columnNames = self.groupDict[groupName].dtype.names
         
        if not branch == None:
            # Branch exists, remove list of children and replace with new one
            branch.children =[]
            add_branch = False
        else:
            branch = BranchNode(groupName)
            add_branch = True
            
        if DEBUG:
            print("Adding Group %s to tree" % groupName)
        
        # Add or update group columns:
        # -----------------------------------
   
        # Add names to branch
        for name in columnNames:
            items = [name,'']
            branch.insertChild(LeafNode(items,branch))
        
        
        
        # Add branch to root if required
        if add_branch:
            root.insertChild(branch)       
        
        
        if callReset:
            self.reset()



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
            if isinstance(node, BranchNode) and index.column==1:
                return int(Qt.AlignCenter|Qt.AlignHCenter)
            else:
                return int(Qt.AlignTop|Qt.AlignLeft)
              
        
        if role == Qt.ToolTipRole :
            if isinstance(node, BranchNode):
                if index.column() == 1:
                    return "Group name"
                
            
                    
                    
        if role == Qt.StatusTipRole:
            if isinstance(node, BranchNode):
                if index.column() == 1:
                    return "Groups contain multiple columns that can be used to make channels"
                
                else:
                    return ""
            else:
                return "Select and click 'Make x data' or 'Make y data' then click make channel"    
            
                
        
        # Display role from here on
        # ==================================================================
                    
        if role != Qt.DisplayRole:
            return None          
        
        if isinstance(node, BranchNode):
            # TODO : This could be where to insert line colour editing
            if index.column() == 0:
                return node.toString()
            elif index.column() ==1:
                # Return size of group
                nRows = len(self.groupDict[node.name])
                nCols = len(self.groupDict[node.name].dtype)
                return "%d rows x %d columns" % (nRows,nCols)
            
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
        """ 
        Function that returns whether items are 
        selectable, editable or read-only
        """
        
        # Check for invalid index
        if not index.isValid():
            return Qt.ItemIsEnabled
        
        # What type of node is this?
        node = self.nodeFromIndex(index)
        
     
        # Branch node:
        #   Not selectable
        if isinstance(node,BranchNode):
            # Separate the two columns
            # even though we return the same flags, this allows
            # them to be separately selected
            if index.column() == 0:
                return Qt.ItemIsEnabled 
                
            if index.column() == 1:
                return Qt.ItemIsEnabled 
            
        # Leaf node :
        #  Is selectable
        if isinstance(node,LeafNode):
            
           if index.column() == 0 :
                return Qt.ItemIsEnabled | Qt.ItemIsSelectable
           else:
                return Qt.ItemIsEnabled
                
                
    
                    
                
                
    def getSelectedGroupColumnsFromIndex(self,modelIndexList):
        """ 
        Get any Group columns names that have been selected
        
        Go through the selected items list, ignore anything that isn't a leaf node
        If it is a leaf node then extract the column name.
        Return all the column names in a list
        
        Output
        ------
        columnList: list of tuples
            Each tuple is of the form (groupName,columnName)
            where both groupName and columnName are strings
            
        """
        # Check the list is not empty
        if not modelIndexList:
            return
            
        columnList = []
        
        for index in modelIndexList:
            node = self.nodeFromIndex(index)
            
            # Add to list if the node is a branch and the first column
            # is selected
            if isinstance(node,LeafNode):
                if index.column() == 0:
                    columnList.append((node.parent.name,node.fields[0]))
                
        return columnList
        
        
