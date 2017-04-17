# -*- coding: utf-8 -*-
"""
Created on Sat May 24 20:32:58 2014

@author: finn

ScopePy
==========

Config dialog and creation

This is how to create a config:
Create a class that inherits from ConfigBase.

Like a panel, it must have a drawPanel function.

It must also have a onSave function that saves its configs (using save(panelname,dictofdict))

In drawPanel, It must create some QFrames or sqt.frames, put them in a DataStorage,
and use the following command (d is the DataStorage)

self.setupTabs(d) 

Version
==============================================================================
$Revision:: 121                           $
$Date:: 2015-11-28 16:44:33 -0500 (Sat, 2#$
$Author::   finn                              $
==============================================================================


"""

#==============================================================================
## License
#==============================================================================

__licence__ = """
Copyright 2015 Finn Bainbridge

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
## Imports
from configparser import ConfigParser as conp
import os
import json
## Save Function
def save(panelname,dictofdict):
    if os.path.exists(os.path.join(os.path.expanduser('~'),'.ScopePy',panelname)):
        path = os.path.join(os.path.expanduser('~'),'.ScopePy',panelname)
    else:
        os.mkdir(os.path.join(os.path.expanduser('~'),'.ScopePy',panelname))
        path = os.path.join(os.path.expanduser('~'),'.ScopePy',panelname)

##    parser = conp()
##    parser.update(dictofdict)
    dtw = json.dumps(dictofdict,indent=True)

    with open(os.path.join(path,'config.json'), 'w') as configfile:
            #config.write(configfile)
            #parser.write(configfile)
            configfile.write(dtw)

## Load function
def load(panelname):
    if os.path.exists(os.path.join(os.path.expanduser('~'),'.ScopePy',panelname,'config.json')):
        path = os.path.join(os.path.expanduser('~'),'.ScopePy',panelname)
    else:
        #os.mkdir(os.path.join(os.path.expanduser('~'),'.ScopePy',panelname))
        #path = os.path.join(os.path.expanduser('~'),'.ScopePy',panelname)
        return None
    
    with open(os.path.join(path,'config.json'), 'r') as configfile:
            #config.write(configfile)
            #parser.write(configfile)
            r = configfile.read()
    
    return json.loads(r)

## check function
import logger
def check(p,loi,default):
    '''
loi: ['first item in config',"second item in config']
'''
    try:
        a = p[loi[0]][loi[1]]
        return a
    except Exception as ec:
        logger.debug(ec)
        return default
## Main Workes

class DataStorage(object):
    '''
Orderd dict
'''
    
    def __init__(self):
        self._items = []
    def __getitem__(self,item):
        return self._get(item)
    def __setitem__(self,item,value):
        self._set(item,value)

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

    def _set(self,item,value):
        self._items.append([item,value])

    def delete(self,item):
        index = self.getIndexOf(item)
        self._items.pop(index)

    def __len__(self):
        return len(self._items)
    def __str__(self):
        return self.__repr__()
    def insert(self,index,item,value):
        self._items.insert(index,[item,value])
    def __repr__(self):
        s = '{'
        for i in self._items:
            s += "%s:%s,\n" % (i[0],i[1])

        s += '}'
        return s

    def keys(self):
        el = []
        for i in self._items:
            el.append(i[0])
        return el

    def items(self):
        el = []
        for i in self._items:
            el.append(i[1])
        return el

    def both(self):
        el = []
        for i in self._items:
            el.append((i[0],i[1]))
        return el

    def getAll(self):
        return self._items

    def __iter__(self):
        return self.both().__iter__()
    
## Gui Importes
from PyQt4.QtGui import *
## ScopePy imports
import ScopePy_panels as panel
from widgets.color import *
import simpleQt as sqt
## GUI
class ConfigBase(panel.PanelBase):
    def __init__(self,API):
        panel.PanelBase.__init__(self,API)
        

    def initialise(self):
        self._tabs = QTabWidget()
        self._tabs.show()
        l = QVBoxLayout(self)
        l.addWidget(self._tabs)
        self.setLayout(l)

    def setupTabs(self,tabs):
        '''
Tabs: DataStorage
        '''
        for i in tabs.keys():
            self._tabs.addTab(tabs[i],i)

    def onSave(self):
        pass



class baseWidget(object):
    def __init__(self,attribute_name,**kwargs):
        self.inputs = kwargs
        self.name = attribute_name
        self.type = self.__class__.__name__

    
    
    def create(self,parent):
        pass
    
class entryWidget(baseWidget):
    '''
Arguments for Entry:
* attribute_name
* text = Text to go in the entry
    '''
    def create(self,parent):
        l = QLineEdit(self.inputs.get('text',''),parent)
        return l

class creator(object):
    def __init__(self,parent,panel_name):
        self.parent = parent
        #self.frame = sqt.frame(parent)
        self.widgets = []
        self.name = panel_name

    def addWidgets(self,widgets):
        frame = sqt.frame(self.parent)
        toadd = []
        
        for i in widgets:
            w = i.create()
            self.widgets.append(w)
            toadd.append([sqt.label(frame,i.name),w])

        frame.position(toadd)
        return frame
    def onSave(self):
        for i in self.widgets:
            #save
            pass
            






