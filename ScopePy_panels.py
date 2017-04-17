# -*- coding: utf-8 -*-
"""
Created on Sat Jun 14 06:09:04 2014

@author: john

Scope Py Panel definitions
====================================

This library defines the panels used in Scope Py

Version
==============================================================================
$Revision:: 171                           $
$Date:: 2016-03-05 08:53:55 -0500 (Sat, 0#$
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


#=============================================================================
#%% Imports
#=============================================================================
import os
import logging
import importlib
from collections import OrderedDict
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import ScopePy_API as API
from ScopePy_utilities import import_module_from_file
import ScopePy_comms as comms
from ScopePy_keyboard import Shortcuts

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



#=============================================================================
#%% Constants
#=============================================================================

PANEL_SAVE_KEYS = ['panel_type', 'panel_name','panel_tab']



#=============================================================================
#%% Importer functions
#=============================================================================
#
# Functions for dynamically importing panels     
        
#def import_module_from_file(full_path_to_module):
#    """
#    Import a module given the full path/filename of the .py file
#    
#    Python 3.4
#    
#    """
#    
#    module = None
#    
#    try:
#    
#        # Get module name and path from full path
#        module_dir, module_file = os.path.split(full_path_to_module)
#        module_name, module_ext = os.path.splitext(module_file)
#        
#        # Get module "spec" from filename
#        spec = importlib.util.spec_from_file_location(module_name,full_path_to_module)
#        
#        module = spec.loader.load_module()
#        
#    except Exception as ec:
#        logger.error("import error: message as follows:")
#        print(ec)
#        
#    finally:
#        return module
#    
    
 
       
def load_panels(path_list,conf):
    """
    Load panels from a list of paths
    
    Checks through the paths given for modules that have the __panels__ 
    attribute. This gives a list of panel classes contained in that module.
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
    
    # Initialise return variables
    # ---------------------------
    panel_classes = OrderedDict()
    startup_panels = []
    
    
    # Handle null input case
    # ------------------------
    if not path_list:
        logger.debug("load_panels:Null path entered")
        return
    
    
    # Go through the path list finding panels
    # ---------------------------------------
    
    for path in path_list:
        logger.debug("load_panels: Looking in [%s]" % path)
        
        # Check for non-existent paths
        if not os.path.exists(path):
            logger.error("Panel loading: unknown path [%s]" % path)
            continue
        
        # Get list of .py files in this path
        file_list = os.listdir(path)
        
        # Look for .py files and import them
        for file in file_list:
            logger.debug("Panel loading: File [%s]" % file)
            module_name,ext = os.path.splitext(file)
            
            # If it's a .py file then look for an attribute called
            # __panels__ which gives a dictionary of the available
            # panels. If exists then add to the return dictionary
            if ext == ".py":
                module = import_module_from_file(os.path.join(path,file))
                
                if hasattr(module,"__panels__"):
                    logger.info("load_panels: Loading panels from [%s]" % file)
                    panel_classes.update(module.__panels__)
                if hasattr(module,"__config__"):
                    logger.info('loading configs from file %s' % module_name)
                    for i in module.__config__:
                        logger.info('loading config: %s' % i)
                        conf[i] = module.__config__[i]
                    
                    
    return panel_classes,conf
    
                
        
        
#=============================================================================
#%% Panel class
#=============================================================================
class PanelBase(QWidget,comms.SignalComms):
    """ 
    This class is the base for all plugins. Needs 'super'
    Inputs:
    --------
    api:    API Class.
        
    """
        
    def __init__(self,api,tab=None,name='unknown',parent = None,args=tuple()):
        
        # Initialise parent classes
        super(PanelBase, self).__init__(parent)
        self.initialiseComms(name)
        
        # Name and ID
        self.name = name
        #self.ID = ''
        
        # Panel type - provided when the panel is created by the API
        self.type = ''
        
        # Link to internal ScopePy API
        self.API = api
        
        
        # Link to internal preferences
        self.preferences = self.API.preferences
        
        # Link to the tab where the panel is placed
        self.tab = tab
        
        # Function key list
        self.Fkeys = None
        self.ShiftFKeys = None
        
        # Keyboard shortcuts
        self.keyboardActions = {}
        self._shortcuts = Shortcuts()      
        
        # Session saving
        self.isSaveable = False     # Can this panel be saved as a session?
        
        
        # Setup standard QT signals
        # ===========================
        self.connect(self.API,SIGNAL("addChannel"),self.addChannel)
        self.connect(self.API,SIGNAL("deleteChannel"),self.deleteChannel)
        self.connect(self.API,SIGNAL("updateChannel"),self.updateChannel)
        
        
        # Setup ScopePy comms signals
        # ================================
        self.addCommsAction('update',self.update)
        self.addCommsAction('themeChanged',self.whenThemeChanged)
        self.addCommsAction('activated',self.onActivation)
        
        # Run starting up functions
        self.initialise()
        self.drawPanel(*args)
    
     # ======================================================================
    # Built-in panel methods
    # ======================================================================

    #@property
    def window(self):
        """
        Return MDI window widget if it exists
        
        Output
        ---------
        window_widget : QMDIsubWindow
            link to widget
        
        """
        if self.tab is not None:
            return self.tab.getSubWindowByTitle(self.name)    
    
    
    def onActivation(self):
        """
        Runs code before panel is activated.
        
        If the user wants to put anything in here then use the whenActivated()
        method below
        
        """
        
        
        # Setup Function key toolbar with options for this panel
        self.setFkeys()
        
        if self.Fkeys is not None:
            self.setupFkeys()
            self.setupShiftFKeys()
            
            
        # Run user code
        self.whenActivated()
        
        
        
    def windowStateChange(self,oldState,newState):
        """
        Detect window change
        
        """
        
        # Window goes to be inactive
        if oldState==Qt.WindowActive and newState==Qt.WindowNoState:
            # Clear the function keys and reset API keys
            self.API.Fkey_toolbar.clearFkeys()
            self.API.shiftFkeys.clearFkeys()
            self.API.setupFkeys()
            
            
            
    def focusOutEvent(self,event):
        """
        Function that is run when focus is lost. This is primarily aimed at
        sidebar panels. So that they can clear their function keys.
        
        """
        
        # Clear the function keys and reset API keys
        self.API.Fkey_toolbar.clearFkeys()
        self.API.setupFkeys()
        
        # Call parent focus event
        super().focusOutEvent(event)
        
            
            
    def statusBarMessage(self,message,time_ms=6000):
        """
        Show message on the main status bar for a specified time period
        
        Inputs
        --------
        message : str
            text to show on the status bar
            
        time_ms : int
            How long to show the message for
            
        """
        
        self.API.statusBar().showMessage(message,time_ms)
    
    def closeEvent(self,event):
        m = self.onClose()
        if m == True:
            event.ignore()
        else:
            super(PanelBase,self).closeEvent(event)
        

    # ======================================================================
    # Standard methods that need re-implimented by new panels
    # ======================================================================
        
    def initialise(self):
        """
        If a panel needs to do some initialisation it can be done in this
        function.
        """
        pass
    
    
    
        
    def drawPanel(self):
        """
        Required method. The panel must provide this itself
        
        """
        pass
    
    
    def addChannel(self,channel):
        """
        Required method : For accepting channels
        """
        pass
    
    
    def deleteChannel(self,channel):
        """
        Required method : For removing channels
        """
        pass
    

    def updateChannel(self,channel):
        """
        Required method : For updating channels
        """
        pass
    
    
    def addKeyboardShortcuts(self,shortcut_list):
        """
        Add keyboard shortcuts to the panel.
        
        The shortcuts are entered as a list of lists with the format
        [name,key combination, action ]
        
        Inputs
        shortcut_list : list of lists
            [name,key combination, action ]
            
            where
                name : str
                    name of action, 
                key combination: str or Qt key list
                    e.g. "Ctrl+t" or Qt.CTRL+Qt.Key_T
                action : function reference
                    the function that will be called, e.g. self.load
                
        """
        
        # TODO : validation of list
        
        # Add shortcuts
        # -------------------
        for name,keys,action in shortcut_list:
            # Add to action list
            self.keyboardActions[name] = action
            
            # Add to shortcut list
            self._shortcuts[name] = keys
        
        
        

    def keyPressEvent(self,event):
        """
        Handle key presses
        
        Check if the panel has defined any keypresses and handle them,
        otherwise used default keypress event
        
        """

        
        # Check if this is a panel keyboard shortcut
        action = self._shortcuts.getActionFromEvent(event)        
        
        #logger.debug("%s: Keyboard Action: %s" % (self.name,action))
        
        # If this is a panel action, accept the event and call the action
        # function
        if action is not None and action in self.keyboardActions:
            event.accept()
            self.keyboardActions[action]()
            return
            
            
        # Not this panels actions, call parent keyPressEvent
        super().keyPressEvent(event)
            
       
    
    
   
    def setupFkeys(self):
        """
        Required method: Updates function key toolbar
        
        """
        
        if not self.Fkeys:
            return
            
        # Setup Fkeys
        self.API.Fkey_toolbar.setFkeyFunctions(self.Fkeys)

    def setupShiftFKeys(self):
        """
        Required method: Updates function key toolbar
        
        """
        self.setShiftFkeys()
        if not self.ShiftFkeys:
            return
            
        # Setup Fkeys
        self.API.shiftFkeys.setFkeyFunctions(self.ShiftFkeys)
        
        
        
    def setFkeys(self):
        """
        Required method: sets list of function keys
        
        Basically the function should be a list definition like this:
        
        self.Fkeys = [
                     ['F4','Select',self.selectFunction],
                     ['F6','Process',self.processFunction],
                     ['F9','Make Plot',self.makePlotFunction],
                     ]
        
        """
        
        pass

    def setShiftFkeys(self):
        """
        Required method: sets list of function keys
        
        Basically the function should be a list definition like this:
        
        self.ShiftFkeys = [
                     ['Shift+F4','Select',self.selectFunction],
                     ['Shift+F6','Process',self.processFunction],
                     ['Shift+F9','Make Plot',self.makePlotFunction],
                     ]
        
        """
        
        self.ShiftFkeys = []
    
    
    def whenActivated(self):
        """
        Required method: Performs this code before the panel becomes active
        
        """
        pass
   
   
    def whenThemeChanged(self):
        """
        Required method: Performs this code when the application theme is 
        changed.
        
        Use the self.API.getThemeCss() or self.API.getThemeSettings() to get 
        updated theme settings
       
        """
        pass
    
    
    
    def showHelp(self):
        """
        Show help in the docs browser
        
        """
        self.API.sendComms('setDocs',self.API.panelID('Docs Browser'),self)
        #logger.debug("[%s] Panel Showing help" % self.name)

    def onClose(self):
        '''
Runs on close.

Return True to stop it from closing
'''
        pass
    
    @property
    def tabName(self):
        """
        Get the name of the tab where this panel is located
        
        """
        
        # Return nothing if the tab property is None
        # sidebar panels do not use the tab property
        if self.tab is None:
            return

        # Mind bendingly convoluted method for getting the name of the tab that
        # this panel is on.
        # We have to back up two levels to the tab widget that 
        #
        # TabWidget (mainArea)   [Get tab title from this using tabText()]
        #   - QStackedWidget
        #       - TabWorkspace (MDI area)
        
        # Get index of the tab from the parent TabWidget
        w = self.tab
        index = self.tab.parent().parent().indexOf(w)
        
        # Use index to get the text from the tab
        return self.tab.parent().parent().tabText(index)
        
        
        
        
    def saveData(self):
        """
        Return all the data necessary to reconstruct this panel.
        
        The data return should be standard python and not include any classes or
        variables that can't be pickled, e.g. QT objects, except QLineF.
        
        This function will only be called if the self.isSaveable flag is set 
        to True.
        
        Outputs
        ------------
        panel_data : dict
            data that can be used to re-open a panel in exactly the same state
            as the current panel.
            
            Must have the following keys:
            'panel_type': str
            'panel_name': str
            'panel_tab' : str
            
            These keys are used to re-create the actual panel
            
        """
        
        return self.standardSaveData
        
        
    @property   
    def standardSaveData(self):
        """
        Make a dictionary for containing the required data for the saveData()
        function. This can be added to by panels to customise the data that is
        stored
        
        Outputs
        ------------
        panel_data : dict
            data that can be used to re-open a panel in exactly the same state
            as the current panel.
            
            Must have the following keys:
            'panel_type': str
            'panel_name': str
            'panel_tab' : str
            
            These keys are used to re-create the actual panel
            
        """
        
        panel_data = {}
        panel_data['panel_type'] = self.type
        panel_data['panel_name'] = self.name
        panel_data['panel_tab'] = self.tabName
        
        # Panel specific data can be added as extra keys
        # e.g. panel_data['my data'] = self.my_data
        
        return panel_data
        
        
        
    def restoreData(self,panel_data):
        """
        Restore panel from a saved session. Takes the data that was stored in
        saveData() and restores the panel to its previous state.
        
        Input
        ---------
        panel_data : anything that can be pickled
            data that can be used to re-open a panel in exactly the same state
            as a previous session
            
        """
        
        pass
        
    
    
    
    
    
        
        
        
        

    
    
#=============================================================================
#%% Panel flags class
#=============================================================================

class PanelFlags():
    """
    Structure that is used to determine properties of a Panel when it is
    loaded.

    """

    def __init__(self,panel_class,open_on_startup=False,
                 has_gui=True,
                 location='main_area',
                 on_panel_menu=True,
                 single_instance=False,
                 API_attribute_name=None,
                 docs=None):
        
        # Panel class
        self.panel_class = panel_class
        
        # Flag to highlight if the panel is to be opened on startup
        self.open_on_startup = open_on_startup
        
        # Has its own GUI window?
        self.has_gui = has_gui
        
        # Location on screen, sidebar or main area?
        self.location = self.check_location(location)
        
        # Can only one instance be created?
        self.single_instance = single_instance
        
        # Does it appear in the Panels menu?
        self.on_panel_menu = on_panel_menu
        
        # Make this panel directly available on the API
        # Caution this should only be used for a single instance panel
        # Trigger this automatically if an API attribute name has been given
        self.add_to_API = API_attribute_name is not None
        
        # Name to be used for the attribute
        # e.g. 'channelSelector'
        # Then this panel can be accessed by API.channelSelector
        self.API_attribute_name = API_attribute_name

        # Counter
        # used to count number of panels of this type created so far
        self.count = 0
        
        self.docs = docs
        
        
    def check_location(self,location):
        
        if location.lower() in ['sidebar','main_area']:
            return location.lower()
            
        else:
            return "main_area"
            

#=============================================================================
#%% Panel Functions
#=============================================================================
