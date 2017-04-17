# -*- coding: utf-8 -*-
"""
Created on Sun Jul 27 07:14:32 2014

@author: john
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
import os
import importlib
import numpy as np
import logging
import platform

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

#=========================================================================
#%% Range list <-> string conversion functions
#=========================================================================


def str2RangeList(inString):
    """ Converts a string to a list of numbers.
    The string contains only numbers,commas and dashes
    e.g. "1", "1,2,3", "1,3-5,6-10"
    
    Usage examples:
    ---------------
    >>> str2RangeList("1")
    [1]
    >>> str2RangeList("1,2,3")
    [1, 2, 3]
    >>> str2RangeList("1,3-5,8,9,12-15")
    [1, 3, 4, 5, 8, 9, 12, 13, 14, 15]
    >>> str2RangeList("")
    []
    
    
    """
    
    # Check for empty string
    if inString == "":
        return []
    
    
    # Check for comma separated list
    if "," in inString:
        # split the list
        strList = inString.split(",")
    else:
        # Make single element list
        strList = [inString]
        
    
    # Go through each item in strList
    # if the item is a number then convert it
    # if it's a range then convert to a list of numbers
    
    range_list = []
    
    for item in strList:
        
        # Is it a range? i.e. contains a dash "-"
        if "-" in item:
            # Split item around the dash
            strNums = item.split("-")
            
            if len(strNums) == 2:
                # Add range to list
                range_list.extend(range(int(strNums[0]),int(strNums[1])+1))

                
            
        else:
            # It's a single number, convert and add to list
            range_list.append(int(item))
    
    return range_list
    
    
def rangeList2str(listOfNumbers):
    """Converts a list of numbers into a string, with the numbers
    separated by commas
    
    Usage examples
    ---------------
    >>> rangeList2str([1,2,3])
    '1,2,3'
    
    """
    
    
    return ','.join(str(e) for e in listOfNumbers)
    

def filterList(listOfNumbers,minValue,maxValue):
    """Filter the values in a numeric list and return only
    values between two limits
    
    
    Inputs
    --------
    listOfNumbers = list e.g. [1,2,3,4]
    minValue = lowest allowed value
    maxValue = highest allowed value
    
    
    Output
    ------
    filteredList = list of numbers with outliers removed
    
    
    Usage examples:
    ----------------
    >>> filterList([1,2,3,4,5,6],2,5)
    [2, 3, 4, 5]
    >>> filterList([],0,10)
    []
    
    """
    
    # Check for empty lists
    if not listOfNumbers:
        return []
        
    filteredList = []
    
    for num in listOfNumbers:
        if minValue <= num <= maxValue:
            filteredList.append(num)
            
    return filteredList
    

#=========================================================================
#%% Array conversions
#=========================================================================    
    
def listOfDict2Recarray(listOfDicts):
    """
    Convert list of dictionaries into a numpy recarray
    
    This is mainly for reading in .CSV files using DictReader and converting
    to numpy arrays
    
    Inputs:
    -----------
    listOfDicts : list of dictionaries
        dictionaries are of the form:
        {'xdata':0,'y1data':1,'y2data':3 ....}
        
    Outputs
    ----------
    recarray : numpy recarray
        array with columns labelled 'xdata', 'y1data', 'y2data' ...
        i.e. accessing columns col = recarray['xdata']
        Individual elements recarray['y1data'][3]
        
    """

    # Get column names
    # -----------------------
    header = list(listOfDicts[0].keys())
    
    # Create output array
    # ------------------------
    # make a numpy data type with all floating point formats
    dtype = np.dtype({'names':header,'formats':[float]*len(header)})
    
    array = np.zeros(len(listOfDicts),dtype)
    
    # Populate the array
    # --------------------------
    for iRow,row in enumerate(listOfDicts):
        for col in row:
            array[col][iRow] = row[col]
        
    return array
    

#=========================================================================
#%% DebugPrintout
#=========================================================================

class DebugPrint():
    """
    Debug printout controller. 
    
    Allows printing out of comments for certain tags
    
    Example usage
    --------------
    Create the printout controller
    >>> dp = DebugPrint(['all','brief','verbose'])
    
    In the code the following can be used to make a printout
    >>> dp.dbg("Function call","The value is wrong","brief")
    
    If more than one tag is required to make a printout, eg in a function
    then use a list of tags
    
    Example
    >>> dp.dbg("myFunction)","doing something",tag=['brief','myFunction'])
    
    
    
    """
    
    
    def __init__(self,initialList = []):
        
        # List of tags that are accepted
        self.tagList = initialList
        
        # Flags
        # -----------
        # disable all printing
        self.disablePrinting = False
        
        # Print everything
        self.printAll = False
        
        
        
    def __call__(self,*args,**kwargs):
        
        self.dbg(*args,**kwargs)
        
        
        
    def addTag(self,newTag):
        """
        Add new tag to the list
        
        
        """
        
        self.tagList.append(newTag)
        
        
    def removeTag(self,tag):
        """
        Remove a tag from the list
        
        """
        
        if tag in self.tagList:
            self.tagList.pop(self.tagList.index(tag))
            
        
    
    
        
    def dbg(self,stage,comment,tag='all',disable=False):
        """
        Do a printout of the form: 
            <stage> : <comment>
            
        If the specified tag is in the list then the comment will be printed,
        if not then it won't
        
        Inputs
        ------
        stage: str or any object
            First string to be printed, if this is an object then the class
            name will be printed
            
        comment : str
            second string to be printed
            
        tag : str or list of str
            tag or list of tags that are required to force a printout.
            If a list of tags are given then all must be in the tagList.
            
        disable : bool
            local override, set to True to stop printing
            
        """
        
        # Check the override
        # ----------------------------
        if self.disablePrinting or disable:
            return
            
        
        # Check the stage
        # ------------------------
        # if stage is an object get the class name
        if not isinstance(stage,str):
            stage = stage.__class__.__name__
        
        
        # Check if a single tag or a list has been entered
        # -------------------------------------------------
        if not isinstance(tag,list):
            tag = [tag]
            
        
            
        # Check if any of specified tags are in the list
        # ----------------------------------------------
        inList = []
        
        for item in tag:
            if item in self.tagList:
                inList.append(True)
            else:
                inList.append(False)
        
        # Printout if ALL tags are in the main list
        # -------------------------------------------
        if all(inList) or self.printAll:
            print("> %s : %s" % (stage,comment))
            
            
        
#=========================================================================
#%% Number formats
#=========================================================================

def formatNumber(number):
    """
    Format a number into a string using sensible criteria
    
    Input
    --------
    number : float
    
    Output
    --------
    numberText : str
        string with number in a format suitable for displaying.
    """
    
    
    # Break number into exponent and fraction
    # ------------------------------------------
    # get absolute value
    abs_value = abs(number)
    
    exponent = np.floor(np.log10(abs_value))
    #fraction = number / np.power(10, exponent)
    
    
    
    # Select format to return
    # ----------------------------
    if abs(exponent) > 3:
        return "%+.3g" % number
        
    if abs_value > 100:
        return "%+.0f" % round(number,0)
        
    elif abs_value > 10:
        return "%+.1f" % round(number,1)
        
    elif abs_value > 1:
        return "%+.2f" % round(number,2)
        
    else:
        return "%+.3f" % round(number,4)
    
    
def getNumberFormat(number):
    """
    Return a format string for the magnitude of the number specified
    
    Inputs
    ---------
    number : float
    
    Output
    ---------
    format_st : str
        format string for the number specified
        
    """
    
    # Break number into exponent and fraction
    # ------------------------------------------
     # get absolute value
    abs_value = abs(number)
    
    exponent = np.floor(np.log10(abs_value))
    #fraction = number / np.power(10, exponent)
    
    # Select format to return
    # ----------------------------
    if abs(exponent) > 3:
        return "%.3g" 
        
    if abs_value > 100:
        return "%.0f" 
        
    elif abs_value > 10:
        return "%.1f" 
        
    elif abs_value > 1:
        return "%.2f" 
        
    else:
        return "%.3f" 
    
        
#=========================================================================
#%% Minidir
#=========================================================================
class minidir:
    def __init__(self,startdir = 'minidir'):
        self.cdir = '/'+startdir
        self.dirs = []
        self.sdir = startdir
        self.files = {}

    
    @property
    def pwd(self):
        return self.cdir
    def createfile(self,filename,value):
        if '/'+self.sdir in filename:
            self.files[filename]=value
        else:
            self.files[self.cdir+'/'+filename]=value

    def getfile(self,filename):
        if '/'+self.sdir in filename:
            return self.files[filename]
        else:
            return self.files[self.cdir+'/'+filename]

        
    def createdir(self,dirname):
        if dirname in self.dirs:
            pass
        else:
            if '/'+self.sdir in dirname:
                self._create(dirname)
            else:
                dirname = self.sdir+'/'+dirname
                self._create(dirname)


    def _create(self,dirname):
        d = dirname.split('/')
        dr = []
        for i in d:
            if i == '':
                pass
            else:
                dr.append(i)

        for i in dr:
            if i in self.dirs:
                pass
            else:
                self.dirs.append(i)

    def cd(self,dirname):
        if dirname in self.dirs:
            if '/'+self.sdir in dirname:
                self.cdir = dirname

            else:
                self.cdir = self.cdir+'/'+dirname

            return True

        else:
            return False

    def find(self,finddir):
        rl = []
        for i in self.dirs:
            if finddir in i:
                rl.append(i)
        for i in self.files:
            if finddir in i:
                rl.append(i)

        return rl


    def home(self):
        self.cdir = '/'+self.sdir


    def __repr__(self):
        return self.cdir
        
        
    def __getitem__(self,fileordir):
        return self.getfile(fileordir)

    def __setitem__(self,fileordir,value):
        if value == '':
            self.createdir(fileordir)

        else:
            self.createfile(fileordir,value)       
       
       

#=============================================================================
#%% Importer functions
#=============================================================================
#
# Functions for dynamically importing panels     

# Notes:
# For testing which python version:
# import platform
# version = platform.python_version()
        
def import_module_from_file(full_path_to_module):
    """
    Import module given full path/filename
    Select how this is done according to version of Python
    """
    
    # Get version of Python and convert to number with one decimal place
    version = float(platform.python_version()[:3])
    
    # Select the function to use
    if version >= 3.4:
        return import_module_from_file_py34(full_path_to_module)
        
    else:
        return import_module_from_file_py32(full_path_to_module)
    
    
    
    
def import_module_from_file_py34(full_path_to_module):
    """
    Import a module given the full path/filename of the .py file
    
    Python 3.4
    
    """
    
    module = None
    
    try:
    
        # Get module name and path from full path
        module_dir, module_file = os.path.split(full_path_to_module)
        module_name, module_ext = os.path.splitext(module_file)
        
        # Get module "spec" from filename
        spec = importlib.util.spec_from_file_location(module_name,full_path_to_module)
        
        module = spec.loader.load_module()
        
    except Exception as ec:
        logger.error("import error: message as follows:")
        print(ec)
        
    finally:
        return module
        
        
"""
Module importer for Python 3.2

"""





def import_module_from_file_py32(path):
    """
    Import module from a path/filename string
    
    Python 3.2 (Raspberry Pi)

    """
    
    # Only import this if we need it
    import imp
    

    module = None

    # Get module name and path
    # ==========================
    module_dir,module_file = os.path.split(path)
    module_name,ext = os.path.splitext(module_file)

    try:
        # Look for module
        module_info=imp.find_module(module_name,[module_dir])

        # Load module
        module = imp.load_module(module_name,*module_info)

    except Exception as ec:
        print(ec)

    finally:
        return module
        

#=========================================================
## Connections
#=========================================================
class FUtilError(Exception): pass

class Connector(object):
    '''
Can connect to connectables
'''
    def start(self,name="Unknown"):
        '''
Setup the connections
'''
        self.connections = {}
        self.name = name
    def _check(self):
        try:
            a = self.name
            return
        except AttributeError:
            pass
        raise FUtilError('Start the connectable!')
    def addConnection(self,var,func,*args,**kwargs):
        '''
var:
    Connectable object
func:
    Function used to get data to be put in connactable
*args:
    args for func
**kwargs:
    kwargs for func
    '''
        self._check()
        self.connections[var]=(func,args,kwargs)

    def connect(self):
        """
Updates the connections.
"""
        self._check()
        k = list(self.connections.items())
        
        for var,fak in k:
            #var = i
            r = False
            func = fak[0]
            args = fak[1]
            kwargs = fak[2]
            try:
                var.getconnect(func(*args,**kwargs),self.name)
            except AttributeError:
                r = True
            if r:
                raise FUtilError('%s Type is not a connectable.' % str(type(var)))

class Connectable(object):
    '''
Can be connected to by connectors
'''
    def start(self,connectable):
        self.connectable = connectable
        self.name = connectable.name
    def _check(self):
        try:
            a = self.name
            return
        except AttributeError:
            pass
        raise FUtilError('Start the connectable!')
    def getconnect(self,new_data,name):
        self._check()
        if name == self.name:
            self.setData(new_data)

    def setData(self,new_data):
        pass

    def deconnect(self):
        self.name = None

    def getData(self):
        self._check()
        c = self.connectable
        func = c.connections[self]
        fun = func[0]
        args = func[1]
        kwargs = func[2]
        data = fun(*args,**kwargs)
        return data

class Connection(Connector,Connectable):
    '''
Can be connected to, and connect to other connectables
'''
    def start(self,name='Unknown'):
        Connector.start(self,name)
        Connectable.start(self,self)
        
    
        
class DataStorage(Connection):
    '''
Ordered dict
'''
    
    def __init__(self,iterable=None,name='DataStorage'):
        self.start('DataStorage')
        if iterable:
            
            self.update(iterable)
        else:
            self._items = []
    def __getitem__(self,item):
        return self._get(item)
    def __setitem__(self,item,value):
        if self._get(item):
            self.delete(item)
        self._set(item,value)
        #self.update()

    def index(self,index):
        return self._items[int(index)]
    def getIndexOf(self,item):
       for e, i in enumerate(self._items):
            if i[0] == item:
                return e

    def _get(self,item):
        for i in self._items:
            if i[0] == item:
                return i[1]
    def checkFor(self,item,default):
        a = _get(item)
        if a == None:
            return default
        else:
            return item

    def _set(self,item,value):
        self._items.append([item,value])
        self.connect()

    def delete(self,item):
        index = self.getIndexOf(item)
        self._items.pop(index)
        self.connect()

    def __len__(self):
        return len(self._items)
    def __str__(self):
        return self.__repr__()
    def insert(self,index,item,value):
        self._items.insert(index,[item,value])
        self.connect()
    def __repr__(self):
        s = '{\n'
        for i in self._items:
            s += "%s:%s,\n" % (i[0],i[1])

        s += '\n}'
        return s

    def keys(self):
        el = []
        for i in self._items:
            el.append(i[0])
        cd = connectedData(el,self)
        self.addConnection(cd,self.keys)
        return cd

    def values(self):
        el = []
        for i in self._items:
            el.append(i[1])
        cd = connectedData(el,self)
        self.addConnection(cd,self.items)
        return cd

    def items(self):
        el = []
        for i in self._items:
            el.append((i[0],i[1]))
        cd = connectedData(el,self)
        self.addConnection(cd,self.both)
        return cd

    def getAll(self):
        return self._items
    def fromList(self,l):
        for i in l:
            r = False
            try:
                self._set(i[0],i[1])
            except TypeError:
                r = True
            if r:
                raise FUtilError('%s is not in any readable format.' % str(l))
 
    def toList(self):
        return self._itmes
            
    def update(self,d):
        '''
Takes a dict or a list of lists, or list of tuples, or list of any iterables
'''
        
        if type(d) != dict:
            self.fromList(d)
            return
        for i in d:
            self._set(i,d[i])
        self.connect()

    def __iter__(self):
        return self.items().__iter__()

    def clear(self):
        self._items = []
        self.connect()

    def setData(self,data):
        #print('Getting Data!')
        self.clear()
        self.update(data)

    def get(self,item,default=None):
        i = self._get(item)
        if i == None:
            return default
        return i
#import pickle
class connectedData(Connectable):
    def __init__(self,l,parent):
        self.start(parent)
        #self.name = connectable.name
        self.data = l
        self.on = 0

    def __iter__(self):
        return self
    def __repr__(self):
        return 'connectedData(%s)' % str(self.data)
    def setData(self,new_data):
        self.data = list(new_data)
    def __next__(self):
        try:
            rt = self.data[self.on]
        except IndexError:
            raise StopIteration
        self.on += 1
        return rt
        
class itemHolder(Connection):
    '''
DataStorage with fixed items
Options:
    Names of all 'items' to be accepted
    '''
    
    def __init__(self,*options,name='itemHolder'):
        self.start(name)
        self.options = options
        self._data = DataStorage()
        for i in options:
            self._data[i]=[] 

    def __getitem__(self,key):
        if type(key) == slice:
            k = key
            key = k.start
            l = True
        else:
            l = False
        
        if key in self.options:
            if l:
                index = k.stop
            else:
                index = len(self._data[key])-1

            try:
                return self._data[key][index]
            except IndexError:
                ras = True
            if ras:
                raise FUtilError('Index Out Of Range!')
        else:
            raise FUtilError('No Key Named %s' % key)
    def __setitem__(self,key,value):
        if key in self.options:
            self._data[key].append(value)
        else:
            raise FUtilError('No Key Named %s' % key)

    def __repr__(self):
        sq = 'FUtil.itemHolder:\n'
        for i in self.options:
            sq += '%s: %s\n' % (i,self._data[i])
        return sq

    
class ConnectedChannel(Connectable):
    def __init__(self,connector):
        self.start(connector)

    @property
    def x(self):
        return self.getData().x

    @property
    def y(self):
        return self.getData().y
#if __name__ == '__main__':
#   ds = DataStorage()
#    ds['name'] = 'Finn'
#    ds['age'] = 10
    
#=========================================================================
#%% Execute doctests if run
#=========================================================================


if __name__ == "__main__":
    import doctest
    doctest.testmod()
