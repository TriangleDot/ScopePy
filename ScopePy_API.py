# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 21:21:23 2015

@author: john

ScopePy API library
=============================
Application Programming Interface for ScopePy


Version
==============================================================================
$Revision:: 179                           $
$Date:: 2017-04-01 15:35:54 -0400 (Sat, 0#$
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

# Standard library
import os
import sys
import imp
import logging
import socket
import datetime
import configparser
import pickle
import copy
from collections import OrderedDict

# Third party libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np

# ScopePy modules
import ScopePy_preferences as prefs
import ScopePy_network as nw
import ScopePy_panels as panels
import ScopePy_channel as ch
import ScopePy_utilities as ut
import ScopePy_widgets as wid
import data_sources.data_source_base_library as DS
import ScopePy_comms as comms
import csslib
import logger

#==============================================================================
#%% Logger
#==============================================================================
# create logger
logg = logging.getLogger(__name__)
logg.setLevel(logging.ERROR)

# Add do nothing handler
logg.addHandler(logging.NullHandler())

# create console handler and set level to debug
con = logging.StreamHandler()
#con.setLevel(logging.DEBUG)
con.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('[%(asctime)s:%(name)s:%(levelname)s]: %(message)s')

# add formatter to ch
con.setFormatter(formatter)

# add ch to logger
logg.addHandler(con)
#logging.basicConfig(filename=sys.stdout)
class loggerc:
    def __init__(self):
        pass
    def debug(self,msg):
        logg.info(msg)
        
#logger = loggerc()


#==============================================================================
#%% Constants
#==============================================================================

BASEPATH, dummy = os.path.split(os.path.abspath(__file__))


# Default directories
BUILTIN_PANELS_FOLDER = os.path.join(BASEPATH,"panels")
BUILTIN_MATHFUNCTIONS_FOLDER = os.path.join(BASEPATH,"math_functions")
BUILTIN_DATASOURCES_FOLDER = os.path.join(BASEPATH,"data_sources")
BUILTIN_THEMES_FOLDER = os.path.join(BASEPATH,"themes")
BUILTIN_ICONS_FOLDER = os.path.join(BASEPATH,"themes","default")
BUILTIN_HELP_FOLDER = os.path.join(BASEPATH,"helpdocs")

# Channel constants
# ====================
defaultColours = ch.channelColours()

# Length of data before making markers into dots
LONG_DATA = 50

# Supported file formats
# ==========================
FILE_FORMATS = ['*.csv','*.xlsx','*.ods','*.spc']
CHANNEL_SAVE_FILE_FORMATS = ['*.csv','*.spc']


# GUI labels
# ============
MAIN_AREA = 'main_area'
SIDEBAR = 'sidebar'


# Menu names
# ==============
# Standard names for the menus
# - shortcut indicated by &
FILE_MENU_NAME = "&File"
EDIT_MENU_NAME = "&Edit"
TAB_MENU_NAME = "Ta&b"
PANEL_MENU_NAME = "&Panels"
THEME_MENU_NAME = "The&mes"
HELP_MENU_NAME = "&Help"




#==============================================================================
#%% API class
#==============================================================================

class API(QObject,comms.SignalComms):
    """
    Core class of ScopePy
    * provides the interface to panels
    * provides interface to GUI
    * provides access to channel data


    Diagram of ScopePy's architecture:





                               +--------------+
                               | API()        |
                               |--------------|
   +--------+                  |              |       +-------------+
   |GUI     |     +----------> |              |<--+-->| Panels      |
   +--------+                  |              |       +-------------+
                               |              |
   +----------+                |              |
   |DataStore |   +----------> |              |
   +----------+                |              |
                               |              |
   +------------+              |              |       +--------------+
   |Preferences |  +-------->  |              |<--+-->| Panels       |
   +------------+              +--------------+       +--------------+
                                     +                             +
                                     |                             |
                                     |                             |
                                     |         +-------------+     |
                                     |         |Libraries    |     |
                                     |         |-------------|     |
                                     |         |             |     |
                                     +-------->|             |<----+
                                               |             |
                                               |             |
                                               +-------------+


    """    
    def __init__(self,gui,parent=None):
        
       # Initialise parent objects       
       super(API, self).__init__(parent)
       self.initialiseComms('API')
       
       logger.debug("API: Starting API")
       
       
       
       # File paths
       # =======================
       # Record the basepath
       self.add_panel_to_API('log',gui.logWidget)
       self.basepath = BASEPATH
       
       # Current path for open/save functions
       self.filePath = os.path.expanduser("~")
       
       
       # Recent files list
       self.recentFiles = []
       
       # Menu links
       # =================
       self.fileMenu = None
       self.helpMenu = None
       
       # Icon manager
       # ================
       self.icons = IconManager()
       
       # Load default icons
       self.icons.load(BUILTIN_ICONS_FOLDER)
       
       
       # Link to Mainwindow class
       # ===========================
       # This is the basic link, any functions that access GUI functionality 
       # should hide this from the user.
       self._gui = gui
       
       # Config
       import ScopePy_config as config

       self.conf = config.DataStorage()
       
       
       # Menus
       self.menu_manager = MenuManager()
       
       # Toolbars
       self.Fkey_toolbar = wid.FkeyToolbar()
       self.shiftFkeys = wid.FkeyToolbar(shift=True)
       self.Fkeys = []
       self.toolbar_manager = ToolbarManager()
       
       # Preferences
       # =====================
       self.preferences = prefs.Preferences()
       self.preferences.load(self.basepath)
       if self.preferences.lastPath:
           self.filePath = self.preferences.lastPath
           
       if self.preferences.recentFiles:
           self.recentFiles = self.preferences.recentFiles
       
       # Data storage
       # ===================
       self.dataStore = DataStore(self)
       self.load_data_sources()
       
       # Server
       # ===================
       # TODO : anything that needs starting
       
       
       
       # Standard File menu
       # ======================
       self.makeFileActions()
       
       # Panels
       # ==============
       self.load_panels()
       
       # Math functions
       # ==================
       self.load_math_functions()
       
       
       # Menus
       # ============
       # Plot menu
       self.makePlotActions()
       
       # Function key toolbar
       # ========================
       self.setupFkeys()
       self.setupShiftFkeys()
       
       
       # Themes
       # =============
       self.theme_dict = {}
       self.load_themes()
       
       # Separate themes for plots, held as csslib dictionaries
       self.plot_themes = {}
       self.load_plot_themes() # TODO is this needed now? Plot panels load their own themes
       
       
       if self.preferences.theme:
           logger.debug("INIT: Default theme is [%s]" % self.preferences.theme)
           if self.preferences.theme in self.theme_dict:
               logger.debug("INIT: Setting theme [%s]" % self.preferences.theme)
               self.setTheme(self.preferences.theme)
               
               
       # Help
       # ================
       self.makeHelpMenu()
               
               
       # Font measurements
       # ========================
       # This is a font that is used to estimate screen lengths in characters
       self.connector = ut.Connector()
       self.connector.start('API')
       self.font = QFont()
       self.fmt = QFontMetrics(self.font)
       self.charWidth_px = self.fmt.averageCharWidth()
       self.charHeight_px = self.fmt.height()
        
       
       

    #%%++++++++++Startup functions
    #======================================================================

    def load_data_sources(self):
        """
        Top level function for loading in data sources from any folders
        specified in the preferences
        
        """
        
        # Dynamically import data source classes
        # =========================================
        
        # Get any user folders from configuration
        if self.preferences.dataSourcePaths !=[]:
            folder_list = [BUILTIN_DATASOURCES_FOLDER] + self.preferences.dataSourcePaths
        else:
            folder_list = [BUILTIN_DATASOURCES_FOLDER]
        
        # load panel classes
        self.dataStore.loadSources(folder_list)
        
        
        
        

    # ********************************************************
    #               Panel loading
    # ********************************************************
    def load_panels(self):
        """
        Load all panels found on startup and create a panel menu
        
        """
        
       
        # Dynamically import panel classes
        # =========================================
        
        # Get any user folders from configuration
        if self.preferences.panelPaths !=[]:
            panel_folder_list = [BUILTIN_PANELS_FOLDER] + self.preferences.panelPaths
        else:
            panel_folder_list = [BUILTIN_PANELS_FOLDER]
        
        # load panel classes
        self.panel_classes,self.conf = panels.load_panels(panel_folder_list,self.conf)
        
        # Get out if no panels
        if self.panel_classes == {}:
            return
        
        # Make Panel menu actions
        # ====================================
        panel_actions = []
        
        # Add a panel update function
        panel_actions.append(self.createAction('Update Panels ...',self.updatePanelMenu))
        
        # Make a function to create a slot for each panel
        # it has to be a function that spits out separate functions
        # otherwise we run into Python referencing problems
        def makePanelSlot(panel_name):
            """
            Return a function to trigger a panel
            """
            return lambda :self.addPanel(panel_name)
        
        # Make the panel actions for panels that are allowed to be in 
        # the menu
        for panel in self.panel_classes:
            
            # Check if panel is to appear on menu
            if not self.panel_classes[panel].on_panel_menu:
                continue
            
            # Otherwise create an action for the panel
            logger.debug("load_panels: Creating menu action for [%s]" % panel)
            
            name = copy.deepcopy(panel)
            panel_actions.append(self.createAction(panel,makePanelSlot(name)))
            
            # Note: Experienced a lot of Python referencing problems here
            # had to create the slots with a separate function
            
        # Add panels menu
        self.menu_manager.addMenu(PANEL_MENU_NAME,panel_actions)
        
        
    def updatePanelMenu(self):
        """
        Update the panel menu - completely load in new panels
        
        This is useful for testing and debugging new panels
        
        """
        
        # Reload the panels
        self.load_panels()
        
        # Update the menu
        self.menu_manager.updateMenu(self._gui.menuBar(),PANEL_MENU_NAME)
    
    
        

    def sidebarTabChanged(a=False):
        pass
        
        
    # ********************************************************
    #               Menus and toolbars
    # ********************************************************
    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):

        """
        Action creator function
        borrowed from Mark Summerfield book
        """                         
                         
        action = QAction(text, self)
        
        # Icon can be a filename or a QIcon
        if isinstance(icon,str):
            action.setIcon(QIcon("/images/{0}.png".format(icon)))
        elif isinstance(icon,QIcon):
            action.setIcon(icon)
            
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action
        

    
        
    def addActions(self, target, actions):
        """
        Action adder
        borrowed from Mark Summerfield book
        """  
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)
        
        
    def makeFileActions(self):
        """
        Make standard file actions and add to menu and toolbars
        
        """
        
        # Get shortcuts
        # ================
        shortcuts = self.preferences.keyboard['main']

        # Create Actions
        # ===============        
        fileNewAction = self.createAction("&New...", self.fileNew,
                icon=QIcon.fromTheme("document-new"), tip="Create new channel")
        fileOpenAction = self.createAction("&Open...", self.fileOpen,
                shortcuts['open'], QIcon.fromTheme("document-open"),
                "Open an existing ScopePy data file")
        fileSaveAction = self.createAction("&Save", self.fileSave,
                shortcuts['save'], QIcon.fromTheme("document-save"), "Save Session")
        fileSaveAsAction = self.createAction("Save &As...",
                self.fileSaveAs, icon=QIcon.fromTheme("document-save-as"),
                tip="Save the image using a new name")
                
        reloadMathFunctions = self.createAction("Reload Math functions",
                self.load_math_functions, 
                tip="Reloads all math functions - useful if they have changed")
                
        clearSessionAction = self.createAction("Clear session",
                self.clearSession, 
                tip="Clear all tabs, channels and data sources")


        configAction = self.createAction("Conf&ig",
                self.openConfig,shortcuts['config'],
                                         tip="See ScopePy's own configuration panels")
                
        filePreferencesAction = self.createAction("Pre&ferences...", self.filePreferences)
        
        fileQuitAction = self.createAction("&Quit", self._gui.close,
                "Ctrl+Q", "filequit", "Close the application")

        
                
                
        # Add to menu
        # ===============
        file_menu = [fileNewAction,fileOpenAction,
                     fileSaveAction,fileSaveAsAction,
                     filePreferencesAction,configAction,
                     reloadMathFunctions,
                     clearSessionAction,
                     fileQuitAction ]

        self.menu_manager.addMenu(FILE_MENU_NAME,file_menu)
        
        


    def openConfig(self):
        self.addPanel('Config Viewer')

    def makePlotActions(self):
        """
        Make actions, menus and toolbars for the mainArea
        
        """
        
        # Actions
        # ===========
        addNewTabAction = self.createAction("New Tab",self.addNewTab,
                                            icon=QIcon.fromTheme('address-book-new'),
                                            shortcut="CTRL+T",
                                            tip='Add new tab to main area')
                                            
        nextTabAction = self.createAction("Next Tab",self.nextTab,
                                            shortcut=Qt.CTRL+Qt.Key_PageDown,
                                            tip='Move to next tab')
                                            
        previousTabAction = self.createAction("Previous Tab",self.previousTab,
                                            shortcut=Qt.CTRL+Qt.Key_PageUp,
                                            tip='Move to previous tab')
       
       
        # Menus
        # =====
        plot_menu = [addNewTabAction,nextTabAction,previousTabAction]
       
        self.menu_manager.addMenu(TAB_MENU_NAME,plot_menu)
        

        
        

    # ********************************************************
    #               Math function loading
    # ********************************************************
    # Dynamically import math functions

    def load_math_functions(self):
    
        # Get any user folders from configuration
        if self.preferences.mathFunctionPaths !=[]:
            math_folder_list = [BUILTIN_MATHFUNCTIONS_FOLDER] + self.preferences.mathFunctionPaths
        else:
            math_folder_list = [BUILTIN_MATHFUNCTIONS_FOLDER]
        
        # load panel classes
        self.math_functions = ch.load_math_functions(math_folder_list)
        logger.debug('GUI: Math functions loaded:')
        print([mf.name for mf in self.math_functions])        
        
        
    # ********************************************************
    #               Theme loading
    # ********************************************************
        
    def load_themes(self):
        """
        Top level function for loading in themes from any folders
        specified in the preferences
        
        Themes are folders with the file theme.css inside them.
        
        """
        
        # Get Paths that contain themes
        # =========================================
        
        # Get any user folders from configuration
        if self.preferences.dataSourcePaths !=[]: # TODO fix this
            path_list = [BUILTIN_THEMES_FOLDER] + self.preferences.themePaths
        else:
            path_list = [BUILTIN_THEMES_FOLDER]
        
        
        # Load themes
        # ========================
        # Look in each folder for sub folders with a 'theme.css' file in
        # there's no recursive search, only the most immediate sub folder
        
        self.theme_dict = {}
        
        for path in path_list:
            logger.debug("Theme loading: Path = [%s]" % path)
            # Get list of files/folders in this path
            contents = os.listdir(path)
            
            for item in contents:
                logger.debug("Theme loading: Item = [%s]" % item)
                if os.path.isdir(os.path.join(path,item)):
                    theme_file = os.path.join(path,item,'theme.css')
                    logger.debug("Theme loading: Looking for [%s]" % theme_file)
                    if os.path.exists(theme_file):
                        self.theme_dict[item] = theme_file
                        logger.debug("Themes: Found theme %s" % item)
                        
                        
        # Add themes menu
        # =========================================

        def makeThemeSlot(theme_name):
            """
            Return a function to set theme
            """
            return lambda :self.setTheme(theme_name)
            
            
        theme_actions = []
        for theme in self.theme_dict:            
            theme_actions.append(self.createAction(theme,makeThemeSlot(theme)))
        
        self.menu_manager.addMenu(THEME_MENU_NAME,theme_actions)
        


    def load_plot_themes(self):
        """
        Top level function for loading in plot themes from any folders
        specified in the preferences
        
        Themes are folders with the file theme.css inside them.
        
        """
        
        # Get Paths that contain themes
        # =========================================
        
        # Get any user folders from configuration
        if self.preferences.dataSourcePaths !=[]:
            path_list = [BUILTIN_THEMES_FOLDER] + self.preferences.themePaths
        else:
            path_list = [BUILTIN_THEMES_FOLDER]
        
        
        # Load themes
        # ========================
        # Look in each folder for a plot_themes.css file
        
        self.plot_themes = {}
        
        plot_theme_files =[]
        
        for path in path_list:
            logger.debug("Plot Theme loading: Path = [%s]" % path)
            
            # Get list of files/folders in this path
            contents = os.listdir(path)
            
            for item in contents:
                logger.debug("Plot Theme loading: Item = [%s]" % item)
                if os.path.isdir(os.path.join(path,item)):
                    # Read from sub directory
                    theme_file = os.path.join(path,item,'plot_themes.css')
                    logger.debug("Theme loading: Looking for [%s]" % theme_file)
                    if os.path.exists(theme_file):
                        plot_theme_files.append(csslib.passCss(theme_file))
                        
                else:
                    # Read from file
                    if item == 'plot_themes.css':
                        theme_file = os.path.join(path,item)
                        if os.path.exists(theme_file):
                            plot_theme_files.append(csslib.passCss(theme_file))
                            
                            
            # Assemble all the theme files together
            for css_dict in plot_theme_files:
                for key in css_dict:
                    if 'name' in css_dict[key]:
                        self.plot_themes.update(css_dict)
                    


    #%%++++++++++Help menu
    #======================================================================
    def makeHelpMenu(self):
        """
        Make the help menu
        
        """
        
        # Introduction link
        introLink = lambda : self.viewHelpFile('introduction.txt','Introduction')
        viewIntro = self.createAction("Introduction to ScopePy", introLink,
                "Alt+F1", "help", "view ScopePy introduction")
        
        # User manual link
        viewhelp = self.createAction("&User Manual", self.viewManual,
                "Ctrl+F1", "help", "view ScopePy user manual")
                
                
        
        # Add to menu
        # ===============
        help_menu = [
                     viewIntro,
                     viewhelp,
                      ]

        self.menu_manager.addMenu(HELP_MENU_NAME,help_menu)
                
    

    def viewHelpFile(self,filename,title='untitled Help'):
        """
        General function for viewing help files stored in the 'helpdocs' folder.
        
        This function will load a help file and set the Docs Browser as the 
        current sidebar tab, so that help is displayed immediately.
        
        Inputs
        ---------
        filename : str
            just the filename only, no path
            
        title : str
            Title of the help page
            
        """
        
        import refclass as rc
        
        # Get title
        title = self.getHelpTitle(filename)
        
        with  open(os.path.join(BUILTIN_HELP_FOLDER,filename)) as f:
            txt = f.read()
            
        # Remove first line
        lines = txt.split('\n')
        txt = "\n".join(lines[1:])
        
        
        w = rc.htmlWrapper(title)
        w.html = txt
        self.sendComms('setHtml',self.panelID('Docs Browser'),w)
        
        self.setSidebarTab('Docs Browser')      
        
        
    def getHelpTitle(self,filename):
        """
        Read help text file and get the title
        
        Input
        -------
        filename : str
            only the filename. The files should all be in the helpDocs folder
            
        Output
        --------
        title : str
            Title of the help taken from first line of the file
            
        """
        
        with open(os.path.join(BUILTIN_HELP_FOLDER,filename)) as file:
            line1 = file.readline()
            
        if line1.startswith('title :'):
            title = line1.split(':')[-1]
            title.strip()
        else:
            title = 'untitled help file'
            
        return title


    def viewManual(self):
        import refclass as rc
        f = open(os.path.join(BUILTIN_HELP_FOLDER,'userManual.txt')
                 )
        txt = f.read()
        f.close()
        w = rc.htmlWrapper('ScopePy User Manual')
        w.html = txt
        self.sendComms('setHtml',self.panelID('Docs Browser'),w)
        
        self.setSidebarTab('Docs Browser')
        
        
    def updateHelpMenu(self):
        """
        Dynamically create the help menu from files stored in the helpDocs
        folder
        
        """
        
        def makeLink(filename):
            """
            Make a function that displays help from a file
            """
            return lambda : self.viewHelpFile(filename)
        
        help_files = os.listdir(BUILTIN_HELP_FOLDER)
        
        # Set the order of import files
        # TODO
        
        # Create help menu actions
        actions = []
        
        for filename in help_files:
            title = self.getHelpTitle(filename)
            actions.append( self.createAction(title, makeLink(filename)) )
            
            
        # Clear and repopulate Help menu 
        self.helpMenu.clear()
        self.addActions(self.helpMenu, actions)
        
        
                
            
        
        
        
                  
        
        

    #%%++++++++++Property aliases
    #======================================================================

    @property
    def channel_dict(self):
        
        return self.dataStore.channel_dict
        
    @channel_dict.setter
    def channel_dict(self,key,value):
        
        self.dataStore.channel_dict[key] = value
        
    @property
    def channel_lock(self):
        return self.dataStore.channel_lock
        
    @property
    def statusBar(self):
        return self._gui.statusBar
        
        
    #%%++++++++++ Closing functions
    #======================================================================
    def closeApp(self):
        """
        Function called by GUI on closing.
        
        Saves preferences
        
        """
        
        self.preferences.lastPath = self.filePath
        self.preferences.recentFiles = self.recentFiles
        self.preferences.save()
        

    #%%++++++++++Channel functions
    #======================================================================
    
    def addChannelData(self,data4scope):
        """ 
        Receive data from server and add to channel
        
        Receives a tuple of (channelName,recarray) from the server or group
        Adds this into the channel dictionary as either a new
        channel or a new data chunk if it is an existing channel
        
        Any channels that are currently plotted will be updated according
        to their chunk mode setting.
        
        Inputs
        --------
        data4scope = (channelName,recarray)
        
        """
        
        # Unpack tuple
        channelName,dataArray = data4scope
        
        self.dataStore.channel_lock.lockForWrite()
        
        if channelName in self.channel_dict:
            self.statusBar().showMessage("Receiving data on channel %s ..." % channelName, 1000)
            
            # Existing channel, add the data to it
            self.channel_dict[channelName].addData2Channel(dataArray)
            
            logger.debug("Channel [%s] : No. chunks = %d" % (channelName,len(self.channel_dict[channelName].data_list)))
            
        else:
            self.statusBar().showMessage("Receiving new channel data : %s ..." % channelName, 1000)
            
            # Create new channel
            
            logger.debug("Creating new channel [%s]" % channelName)
                
            # Get colours for the channel from default colour set
            # -----------------------------------------------------
            lineStyle = self.getChannelLinestyle(len(dataArray))
            
            # Create new channel
            # -----------------------
            self.channel_dict[channelName] = ch.ScopePyChannel(channelName,lineStyle)                                
                                
            self.channel_dict[channelName].addData2Channel(dataArray)
            
        
        
        # Add channel to tree            
        self.emit(SIGNAL("channel_added"), channelName)
        
        
        self.dataStore.channel_lock.unlock()
        
        
        self.emit(SIGNAL("update_channel_selector"))
        


    def addGroupChannel(self,channel_name,table_wrapper,xcol,ycol):
        """
        Add a group channel into memory

        Inputs
        ----------
        channel_name : str
            Name of channel as it will appear in channel selector and legends
        
        table_wrapper : DatasourceTableWrapper or derivative
            link to underlying data table
            
        xcol,ycol : str
            column names of data table
            
        """
        
        # Get colours for the channel from default colour set
        # -----------------------------------------------------
        N = table_wrapper.rowCount()
        lineStyle = self.getChannelLinestyle(N)
        
        # Make a group channel
        # ------------------------
        group_channel = ch.GroupChannel(table_wrapper,xcol,ycol,
                                        channelLabel=channel_name,
                                        lineStyle=lineStyle)
        
        
        # Add to channel_dict
        # ----------------------
        self.dataStore.channel_lock.lockForWrite()
        self.channel_dict[channel_name] = group_channel
        self.emit(SIGNAL("channel_added"), channel_name)
        self.dataStore.channel_lock.unlock()
        self.emit(SIGNAL("update_channel_selector"))
        
        

    def getChannelLink(self,chname):
        if chname in list(self.channel_dict.keys()):
            cha = self.channel_dict[chname]
        else:
            raise NameError('No channel Named %s' % chname)
        chaw=ut.ConnectedChannel(self.connection)
        self.connector.addConnection(chaw,lambda self: self.channel_dict[chname],self)
        self.connect()
        
        
  
    def getChannelLinestyle(self,npoints):
        """
        Get default linestyle for a channel
        """
        
        # Get colours for the channel from default colour set
        # -----------------------------------------------------
        lineStyle = ch.plotLineStyle()
        lineStyle.lineColour = defaultColours.getLineColour()
        lineStyle.markerColour = defaultColours.getMarkerColour()
        lineStyle.markerFillColour = defaultColours.getMarkerFillColour()
        
        # If the number of data points is greater than a certain value
        # automatically make the marker a dot
        if npoints > LONG_DATA:
            lineStyle.marker = '.'
        else:
            lineStyle.marker = defaultColours.getMarker()
        
        # Increment colours for next channel
        defaultColours.incrementColours()
        
        return lineStyle
                
            

    def addChannel2Panel(self,selectedChannels=None,plot_name=None,tab_name=None):
        """
        Add data from selected channel(s) to the panel in the current
        tab.
        
        Input
        ---------
        selected_channels : list of str
            list of selected channels
        
        """    
        
        
        # Check if any channels are selected
        # if not then return
        if not selectedChannels:
            selectedChannels = self.channelSelector.getSelectedChannels()
            
        # If there are still no channels selected then exit
        if not selectedChannels :
            return
            
        # Handle single string input
        if isinstance(selectedChannels,str):
            selectedChannels = [selectedChannels]
            
        if not plot_name:    
            # Get current plot/tab
            currentPlot = self.getCurrentTabScreen(tab_name)
        else:
            # TODO : Don't think this works anymore
            currentPlot = self.getPlotOnTab(plot_name,tab_name)
            
        # TODO : Fix getting current plot on a tab with non-plot items
        if not hasattr(currentPlot,'addChannel'):
            logger.debug("addChannel2Panel: Non-plot item selected")
            return
            
        
        # Loop through selected channels
        # if the channel exists then
        # add data from channel to plot items for the current tab
        for channel in selectedChannels:
            if channel in self.channel_dict:
                currentPlot.addChannel(channel)
          
        # Update the chunk selector
        #self.updateChunkSelector()



    def removeChannelFromPlot(self,selectedChannels=None,plot_name=None,tab_name=None):
        """
        Remove selected channel(s) from plot in current tab
        
        """
        
        # Check if any channels are selected
        # if not then return
        if not selectedChannels:
            selectedChannels = self.channelSelector.getSelectedChannels()
            
        # If there are still no channels selected then exit
        if not selectedChannels :
            return
            
        # Handle single string input
        if isinstance(selectedChannels,str):
            selectedChannels = [selectedChannels]
            
        if not plot_name:    
            # Get current plot/tab
            currentPlot = self.getCurrentTabScreen(tab_name)
        else:
            currentPlot = self.getPlotOnTab(plot_name,tab_name)
            
        if currentPlot is None:
            return
            
        # TODO : Fix getting current plot on a tab with non-plot items
        if not hasattr(currentPlot,'deleteChannel'):
            logger.debug("removeChannelFromPlot: Non-plot item selected")
            return
            
        # Loop through selected channels
        # if the channel exists then remove from plot
        for channel in selectedChannels:
            if channel in self.channel_dict:
                currentPlot.deleteChannel(channel)
            
            
    def clearAllChannels(self):
        """
        Delete all channels from channel selector
        
        """

        ID = self.panelID('Channel selector')
        self.sendComms('deleteAllChannels',ID)
        
        
    
     
    #======================================================================
    #%% +++++ Plot functions ++++++
    #======================================================================

            
        
    def setCurrentPlot(self,plot_name,tab_name=None):
        """
        Set the current plot focus
        
        Inputs
        ---------
        plot_name : str
            name of plot on tab
            
        tab_name : str
            tab on which the plot resides, if None then this is the current
            tab
        """
        
        if not tab_name:
            tab_plot = self.getCurrentTabScreen()
        else:
            # TODO :
            # get the tab using tab_name
            pass
        
        # TODO : select plot by name
        pass
    
    
    def deletePlot(self,plot_name,tab_name=None):
        """
        delete named plot on specified or current tab
        
        Inputs
        ---------
        plot_name : str
            name of plot on tab
            
        tab_name : str
            tab on which the plot resides, if None then this is the current
            tab
        """
        
        if not tab_name:
            tab_plot = self.getCurrentTabScreen()
        else:
            # TODO :
            # get the tab using tab_name
            pass
        
        # TODO : select plot by name
        pass
    
    
    
    def deleteChannelFromPlot(self,channel_name,plot_name,tab_name=None):
        """
        delete named plot on specified or current tab
        
        Inputs
        ---------
        channel_name : str
            channel name to be removed from plot. Does not delete channel.
            
        plot_name : str
            name of plot on tab
            
        tab_name : str
            tab on which the plot resides, if None then this is the current
            tab
        """
        
        if not tab_name:
            tab_plot = self.getCurrentTabScreen()
        else:
            # TODO :
            # get the tab using tab_name
            pass
        
        # TODO : select plot by name
        pass
        
        
        
    
    #======================================================================
    #%% +++++ File menu functions ++++++
    #======================================================================
    
    
                
    
    
    def fileNew(self):
        print("Not implemented yet")
        
    
    def fileOpen(self,pathAndFilename=None):
        """
        Generic opening function. Passes filenames to other functions for
        parsing
        """
        
        # Check if the action sent a pathname (from recent files)
        if not pathAndFilename:
            
            action = self.sender()
            if isinstance(action, QAction):
                pathAndFilename = action.data()
                
        # No path name - use file dialog
        if not pathAndFilename:
            # Popup the file dialog
            if not os.path.exists(self.filePath):
                path = os.path.expanduser("~")
            else:
                path = self.filePath
                
            # Get supported file formats plus ScopePy channels storing format
            formatString ="Stored sessions (*.sps);;" + self.dataStore.fileExtensions + ";;Channel data files (*.spc)" 
                
            pathAndFilename = QFileDialog.getOpenFileName(self._gui,"Open data source file",
                                                   path,formatString)
                                                   
           
            if not pathAndFilename:
                return
           
        # Final sanity check on filename
        if not os.path.exists(pathAndFilename):
            return
            
        # Store path for next time    
        path, filename = os.path.split(pathAndFilename)
        self.filePath = path
        
        # Get type for file from extension and select the loading method
        dummy,ext = os.path.splitext(filename)
        ext = ext.lower()
        
        
        if ext == '.spc':
            self.loadChannels_from_spc(pathAndFilename)
        elif ext == '.sps':
            self.loadSession(pathAndFilename)
        else:
            # Send filename to DataStore for opening
            self.dataStore.fileOpen(pathAndFilename)
        
        
        # Log file to recent files
        self.addRecentFile(pathAndFilename)
                                               
        
        
        
    def fileSave(self):
        """
        Save selected channels to disk. Pops up a file selector box.
        
        
        """
        
        # Find out if any channels have been selected
        # selected place
#        selected = self.channelSelector.getSelectedChannels()
#        
#        if not selected:
#            self.statusBar().showMessage("No channels selected - cannot save", 5000)
#            return
        
        if not os.path.exists(self.filePath):
            path = os.path.expanduser("~")
        else:
            path = self.filePath
            
        #formatString = "Channel data files (%s)" % " ".join(CHANNEL_SAVE_FILE_FORMATS)
            
        formatString = "Stored sessions (*.sps);;Channel data files (*.spc);; CSV files (*.csv)"
        pathAndFilename = QFileDialog.getSaveFileName(self._gui,"Save to file",
                                               path,formatString)
                                               

        
        if not pathAndFilename:
            return
            
        # Store path for next time    
        path, filename = os.path.split(pathAndFilename)
        self.filePath = path
            
        name,ext = os.path.splitext(pathAndFilename)
        
        ext = ext.lower()
        
        if ext == '.spc':
            self.saveChannels_to_spc(pathAndFilename,selected)
        elif ext == '.sps':
            self.saveSession(pathAndFilename)
            
            
        # Log file to recent files
        self.addRecentFile(pathAndFilename)
        
        
        
    def fileSaveAs(self):
        print("Not implemented yet")
        
        
    def saveChannels_to_spc(self,filename,channel_names):
        """
        Save channels to custom ScopePy format
        
        This is basically a pickled dictionary of channels
        
        Inputs
        -----------
        filename : str
            string path/filename, usually from a filSave() function
            
        channel_names : list of str
            list of channel names to store
            
        """
        
        # Create dictionary of channels
        # ------------------------------
        # Export the channels into a dictionary, removing all the QObject()
        # stuff and only preserving the raw data.
        # Then put each dictionary into an overall saveChannels dictionary.
        # Use this to pickle
        saveChannels = {}
        
        for name in channel_names:
            saveChannels[name] = self.channel_dict[name].to_dict()
            
            
        # Store to file
        # --------------
        with open(filename,'wb') as file:
            pickle.dump(saveChannels,file,pickle.HIGHEST_PROTOCOL)
            
            
        # Log file to recent files
        self.addRecentFile(filename)
            
    
    def loadChannels_from_spc(self,filename):
        """
        Load channels back from custom ScopePy format
        
        Inputs
        -----------
        filename : str
            string path/filename, usually from a filSave() function
        
        """
        
        # File access
        # --------------------
        # check path exists        
        if not os.path.exists(filename):
            self.statusBar().showMessage("No file found [%s]" % filename, 5000)
            return
            
        # Load file
        with open(filename,'rb') as file:
            saveChannels = pickle.load(file)
          
        
        # Log file to recent files
        self.addRecentFile(filename)

        # Channel importing
        # ---------------------------
        # Channels are stored individually as dictionaries so we can use
        # the ScopePyChannel.from_dict() method to import them

        # lock against threads
        self.channel_lock.lockForWrite()
            
        # add to stored channels to channel dictionary
        for name,channel_import_dict in saveChannels.items():
            # First create a channel object and import data into it
            newChannel = ch.ScopePyChannel()
            OK = newChannel.from_dict(channel_import_dict)
            
            if not OK:
                logger.debug("loadChannels_from_spc: Failed to import channel [%s]" % name)
                continue
            
            # Now add to central channel dictionary
            logger.debug("loadChannels_from_spc: channel [%s] imported" % name)
            self.channel_dict[name] = newChannel
            
            
            # Add channel to tree [model version]            
            self.emit(SIGNAL("channel_added"), channelName)
        
        
        self.channel_lock.unlock()
            
        # Update channel selector tree 
        self.emit(SIGNAL("update_channel_selector"))
        
        
        
    def filePreferences(self):
        self.addPanel('Config Viewer',args=('Preferences',))

    def oldFilePreferences(self):
        form = prefs.PreferencesDialog(prefs=self.preferences)
        
        if form.exec_():
            self.preferences.save()
        
        
        
    def addRecentFile(self, fname):
        if fname is None:
            return
        if fname not in self.recentFiles:
            self.recentFiles = [fname] + self.recentFiles[:8]


    def updateFileMenu(self):
        """
        Add recent files to File menu
        
        Borrowed from Mark Summerfield
        
        """
        # Clear and repopulate file menu with all but last option
        self.fileMenu.clear()
        self.addActions(self.fileMenu, self.menu_manager.menus[FILE_MENU_NAME][:-1])
        
        
        # Make a recent file list
        recentFiles = []
        
        for fname in self.recentFiles:
            if QFile.exists(fname):
                recentFiles.append(fname)
                
                
        if recentFiles:
            self.fileMenu.addSeparator()
            for i, fname in enumerate(recentFiles):
                action = QAction(QIcon.fromTheme('text-x-generic'),
                        "&{} {}".format(i + 1, QFileInfo(fname).fileName()), 
                        self._gui)
                        
                action.setData(fname)
                self.connect(action, SIGNAL("triggered()"),
                             self.fileOpen)
                self.fileMenu.addAction(action)
                
        # Add Quit option to bottom
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.menu_manager.menus[FILE_MENU_NAME][-1])
        
        
    def setMainWindowTitle(self,new_title="Unsaved session" ):
        """
        Set the title on the main window. Whatever title is entered will
        be prefixed by 'ScopePy :'
        
        Input
        ------
        new_title : str
            string to be put in the title
            
        """
        
        title = "ScopePy : %s" % new_title
        
        self._gui.setWindowTitle(title)
        
        
        
    #======================================================================
    #%% +++++ Session saving functions
    #======================================================================
    def saveSession(self,filename=None):
        """
        Save a Session to a file
        
        This is the main session saving function that does all the heavy 
        lifting.
        
        Implementation details
        ---------------------------
        The entire ScopePy session is saved into a SessionStore class and then
        this is pickled
        
        Input
        -----------
        filename : str
            full path/filename of the file to save
        
        """
        
        if filename is None or filename=='':
            return
            
        
        # Create container for all the session data
        session = SessionStore()
        
        # Store tabs
        # --------------------
        session.tabs = self.getTabList()
        
        
        # Store channels
        # ------------------------------
        # Export the channels into a dictionary, removing all the QObject()
        # stuff and only preserving the raw data.
        # Then put each dictionary into an overall saveChannels dictionary.
        # Use this to pickle
        session.channels = OrderedDict()
        
        for name,channel in self.channel_dict.items():
            session.channels[name] = channel.to_dict()
        
        
        # Store data sources
        # -----------------------------
        self.dataStore.saveSourcesToSession(session)
            
            
            
        # Store panels
        # --------------------------
        # Store all the panels for each tab
            
        for tab in session.tabs:
            panel_name_list = self.getAllPanelsOnTab(tab,return_comms_name=False)
            
            for panel_name in panel_name_list:
                panel = self.getPanelOnTab(panel_name,tab)
                if panel.isSaveable:
                    session.panels[panel_name] = panel.saveData()
            
        
        # Store data to file
        # -----------------------------
        with open(filename,'wb') as file:
            pickle.dump(session,file,pickle.HIGHEST_PROTOCOL)
            
            
        # Change the title of the main window to add the session filename
        # -----------------------------------------------------------------
        path, filename = os.path.split(filename)
        self.setMainWindowTitle(filename)
            
            
        
        
    def loadSession(self,filename=None):
        """
        Load a session from file
        
        This loads the session data from file and restores the tabs, channels
        data sources, panels and anything else stored in session
        
        Input
        -----------
        filename : str
            full path/filename of the file to save
            
        Output
        --------
        session : SessionStore
            For debugging return the Session storage structure
            
        """
        
        # Input validation
        # ------------------------
        if filename is None or filename=='':
            return
            
        # Check file exists
        if not os.path.exists(filename):
            return
            
            
        # Load the session data
        # --------------------------------
        with open(filename,'rb') as file:
            session = pickle.load(file)
        
        
        # Open tabs
        # ------------------
        current_tabs = self.getTabList()
        
        if session.tabs != []:
            for tab in session.tabs:
                if tab not in current_tabs:
                    self.addNewTab(tab)
                    
        # Update tab list for later
        current_tabs = self.getTabList()
                    
                    
        # Restore Channels
        # ---------------------------
        # Channels are stored individually as dictionaries so we can use
        # the ScopePyChannel.from_dict() method to import them
        saveChannels = session.channels

        if saveChannels is not None:
            # lock against threads
            self.channel_lock.lockForWrite()
                
            # add to stored channels to channel dictionary
            for name,channel_import_dict in saveChannels.items():
                # First create a channel object and import data into it
                newChannel = ch.ScopePyChannel()
                OK = newChannel.from_dict(channel_import_dict)
                
                if not OK:
                    logger.debug("loadChannels from session: Failed to import channel [%s]" % name)
                    continue
                
                # Now add to central channel dictionary
                logger.debug("loadChannels_from_spc: channel [%s] imported" % name)
                self.channel_dict[name] = newChannel
                
                
                # Add channel to tree [model version]            
                self.emit(SIGNAL("channel_added"), name)
            
            
            self.channel_lock.unlock()
                
            # Update channel selector tree 
            self.emit(SIGNAL("update_channel_selector"))
            
            
        # Restore data sources
        # -----------------------------
        self.dataStore.restoreSourcesFromSession(session)
            
            
        # Restore panels
        # --------------------------
        if session.panels != {}:
            
            for panel_name,panel_data in session.panels.items():
                
                # Check the correct keys are in the data dict
                if not all([key in panel_data for key in panels.PANEL_SAVE_KEYS]):
                    # Skip this panel if it doesn't have the correct keys
                    continue

                # Check for tab availability                
                if panel_data['panel_tab'] not in current_tabs:
                    # Skip if no tab
                    continue
                
                # Make a new panel on the correct tab
                panel = self.addPanel(panel_data['panel_type'],panel_data['panel_name'],
                              panel_data['panel_tab'])
                              
                # Restore panel data
                panel.restoreData(panel_data)
                
                
                
        # Change the title of the main window to add the session filename
        # -----------------------------------------------------------------
        path, filename = os.path.split(filename)
        self.setMainWindowTitle(filename)
                    
                
            
        return session
        
        
        
    def clearSession(self):
        """
        Wipe everything from the current session:
        * close panels
        * remove all channels and data sources
        * close all but one tab
        
        """
        
        # Delete main area tabs
        self.deleteAllTabs()
        
        # Clear all channels
        ID = self.panelID('Channel selector')
        self.sendComms('deleteAllChannels',ID)
        
        
        # Clear all data sources
        # TODO: This doesn't work yet - problems in the data source selector
        ID = self.panelID('Data Source Selector')
        self.sendComms('deleteAllDataSources',ID)
        
        # Reset window title
        self.setMainWindowTitle()
        
    
    #======================================================================
    #%% +++++ Tab View port functions
    #======================================================================
    
    # Functions for handling the tabs
    
    def addNewTab(self,name=None,add_plot=False):
        """ 
        Add a new tab/View port to the main window
        
        Inputs
        -------
        name : str
            name of tab, if not specified then "Page n" will be used
        """
        
        # Add a MDI area to the table
        mdi = wid.TabWorkspace(defaultName="Plot")
        
        # Make the graph if requested
        if add_plot:
            scopeScreen = self.createNewPlot()
            
            # Add plot to sub window with default name
            mdi.addWindow(scopeScreen)
      
        

        # Get current number of tabs so we can set
        # the tab title to a default of "Plot <tabNumber>"
        tabIndex = self._gui.mainArea.count() + 1
        
        # Make the tab name
        if not name:
            name = "Page %d" % tabIndex
        
        # Add new tab to tabWidget 
        tabIndex = self._gui.mainArea.addTab(mdi, name ) 
        
        # Make added tab the current one
        # Note the actual index is one less than the displayed value
        # because the actual index starts at zero
        self._gui.mainArea.setCurrentWidget(self._gui.mainArea.widget(tabIndex))
        
        # Add tooltips
        self._gui.mainArea.setTabToolTip(tabIndex,'Double click to edit name')
        self._gui.mainArea.setTabWhatsThis(tabIndex,"tab what's this")
       

         
    def getTabList(self):
        """
        Return a list of tab names in the correct order
         
        Outputs
        -------
        tab_list: list of str
            list of the tab label names
             
        """
         
        nTabs = self._gui.mainArea.count()
         
        tab_list = [self._gui.mainArea.tabText(index) for index in range(nTabs)]
         
        return tab_list
        
    
    
    def getTabIndexFromName(self,tab_name):
        
        tab_list = self.getTabList()
        
        if tab_name not in tab_list:
            logger.debug("getTabIndexFromName: Failed to find tab called [%s]" % tab_name)
            return
         
        # Get Index of the requested tab and make it current
        tab_index = tab_list.index(tab_name)
        
        return tab_index
        
        
    def tabExists(self,tab_name):
        """
        Return True or False if tab exists or not
        
        Input
        ---------
        tab_name: str
            Name of tab to search for
            
        Output
        ---------
        exists : bool
            True - tab exists
            False - tab does not exist
            
        """

        if tab_name in self.getTabList():
            return True
        
        return False
        
            
            
    def deleteTab(self,indexOrName):
        """ 
        Delete tab/view port
        
        Input
        ------
        indexOrName : int or str
            tab index or tab name to be deleted
        
        """
        
        if isinstance(indexOrName,str):
            index = self.getTabIndexFromName(indexOrName)
        else:
            index = indexOrName
        
        tab_name = self._gui.mainArea.tabText(index)
        
        logger.debug("deleteTab: Delete tab [%s] requested" % tab_name)

        # Delete tab if it's not the last one        
        if len(self.getTabList())>1:
            self._gui.mainArea.removeTab(index)
            
            
    def deleteAllTabs(self):
        """
        Delete all main area tabs
        
        Leave one blank tab
        """

        # Get number of tabs        
        tab_list = self.getTabList()
        
        # Remove all tabs
        for tab_name in tab_list:
            # Get the MDI area
            mdi = self.getTabDockArea(tab_name)
            
            # Close all panels in MDI area
            mdi.closeAllSubWindows()
            
            # Delete tab
            index = self.getTabIndexFromName(tab_name)
            self._gui.mainArea.removeTab(index)
            
        # Add blank tab
        self.addNewTab()
        
        
        
        
    def setCurrentTab(self,tab_name):
        """
        Select the current tab by name
        
        Input:
        ---------
        tab_name : str
        
        """
        
        # Get Index of the requested tab and make it current
        tab_index = self.getTabIndexFromName(tab_name)
        
        if tab_index:
            self._gui.mainArea.setCurrentIndex(tab_index)
    
            
            
    def getCurrentTabScreen(self,tab_name=None):
        """ 
        Return the current Panel of the current tab
        
        Output
        ------------
        scopeScreen = current plot item on the current tab
        
        """
        
        # Get current tab index and return current panel item
        # 
        if not tab_name:
            DockArea = self._gui.mainArea.currentWidget()
        else:
            DockArea = self.getTabDockArea(tab_name)
            
        currentPlot = DockArea.getCurrentWidget()
        
        return currentPlot
        
    
    def getCurrentTabName(self):
        """
        Convenience function to get the name of the current tab
        
        Output:
        -------
        tab_name : str
        
        """
        
        return self._gui.mainArea.tabText(self._gui.mainArea.currentIndex())
        
        
        
        
    def previousTab(self):
        """
        Move to previous tab
        
        """
        
        currentTabIndex = self._gui.mainArea.currentIndex()
        num_tabs = self._gui.mainArea.count()
        
        if currentTabIndex==0:
            self._gui.mainArea.setCurrentIndex(num_tabs-1)
        else:
            self._gui.mainArea.setCurrentIndex(currentTabIndex-1)
        
        
    def nextTab(self):
        """
        Move to next tab
        
        """
        
        currentTabIndex = self._gui.mainArea.currentIndex()
        num_tabs = self._gui.mainArea.count()
        
        if currentTabIndex==num_tabs-1:
            self._gui.mainArea.setCurrentIndex(0)
        else:
            self._gui.mainArea.setCurrentIndex(currentTabIndex+1)
        
        
    
    def getTabDockArea(self,tab_name):
        """
        Return the MDI area on the named tab
        
        Input
        -------
        tab_name : str
        
        Output
        --------
        dock : QMDIArea 
            reference to MDI area widget that is on the tab
            
        """
        
        # Get Index of the requested tab 
        tab_index = self.getTabIndexFromName(tab_name) 
        
        if tab_index is None:
            return
        
        # Return the MDIArea
        return self._gui.mainArea.widget(tab_index)
        
        
    def getAllPanels(self,return_comms_name=False):
        """
        Gets ALL Panel objects on ALL tabs
        
        Input
        ------
            
        return_comms_name : bool
            If True then the ID will be returned otherwise the name
            that appears on the window will be returned.
        
        Output:
        -------
        panel_names : list of str
        """
        
        tabs = self.getTabList()
        panels = []
        for i in tabs:
            panels.append(self.getAllPanelsOnTab(i,return_comms_name))
        return panels
    
        
    def getAllPanelsOnTab(self,tab_name,return_comms_name=False):
        """
        Gets  all Panel objects from the specified tab
        
        Input
        ------
        tab_name : str
            Name of tab, as it appears on screen
            
        return_comms_name : bool
            If True then the ID will be returned otherwise the name
            that appears on the window will be returned.
        
        Output:
        -------
        panel_names : list of str
        
        """
        
        # Get the MDI area
        mdi = self.getTabDockArea(tab_name)
        
        if not mdi:
            return
        
        # Search through the sub windows and return titles
        # of any that contain plots
        panel_names = []
        
        for window in mdi.subWindowList():
            if return_comms_name and hasattr(window.widget(),'ID'):
                panel_names.append(window.widget().ID)
            else:
                panel_names.append(window.windowTitle())
        
                
        return panel_names
        
        
        
    def getPanelOnTab(self,panel_name,tab_name=None):
        """
        Get specified Panel on tab
        
        Input
        ------
        panel_name: str
            name of Dock with plot in it
            
        Output
        ------
        panel_object:
            object contained in dock
            
        """
        
        # Handle tab name = None
        if tab_name is None:
            tab_name = self.getCurrentTabName()
            
        
        # Get Dock Area on tab
        dockArea = self.getTabDockArea(tab_name)
            
        # Look for plot on the tab
        if panel_name not in self.getAllPanelsOnTab(tab_name):
            logger.debug("getPanelOnTab: Unknown panel [%s]" % panel_name)
            return
            
        # TODO: check this works
        dock = dockArea.getSubWindowByTitle(panel_name)
        
        return dock.widget()
        
    def getPanel(self,panel_name):
        tabs = self.getTabList()
        panels = []
        for i in tabs:
            t = self.getPanelOnTab(panel_name,i)
            if t != None:
                return t
            
            
        return None
       
    
    def addNewPlot(self,plotName=None):
        """
        Add new plot to current tab
        
        """
        
        self.addPanel('Plot',plotName)
        
        
        

        
    #======================================================================
    #%% +++++ Panels functions
    #======================================================================   
    def getCurrentPanel(self):
        '''
Get The current panel object.
'''
        tabs = self.getTabList()
        for i in tabs:
            area = self.getTabDockArea(i)
            sub = area.activeSubWindow()
            if sub == 0 or sub == None:
                pass
            else:
                return sub.widget()

    def getCurrentPanelName(self):
        panel = self.getCurrentPanel()
        if panel != None:
            return panel.name


    def addPanel(self,panel_type,panel_name=None,tab_name=None,args=()):
        """
        Master function for adding new panels.
        
        Selects between sidebar and main area according to the panel type.
        
        Sets up Signal comms between API and panel
        
        Inputs
        ----------
        panel_type : str
            Type of panel to create
            
        panel_name : str
            The name of the panel to appear on the window title
            
        tab_name : str
            The name of the tab where the panel is to go. If None then the 
            current tab is used.
        
        """
        logger.debug("addPanel: Panel [%s] being added" % panel_type)
        #print(args)
        
        if self.panel_classes[panel_type].location == MAIN_AREA:
            newPanel = self.addPanel2MainArea(panel_type,panel_name,tab_name,args=args)
        else:
            newPanel = self.addPanel2Sidebar(panel_type)
            
            
        # Connect panel to comms
        # ------------------------------------
        # API to Panel connection
        logger.debug("API/addPanel : Adding panel [%s] to API receiver list" % newPanel.ID)
        self.addCommsReceiver(newPanel.ID,newPanel)
        self.connect(self,SIGNAL(comms.SCOPEPY_SIGNAL),newPanel.receiveComms)
        
        # Panel to API connection
        self.connect(newPanel,SIGNAL(comms.SCOPEPY_SIGNAL),self.receiveComms)
        
        return newPanel
        
        
        
    def addPanel2MainArea(self,panel_type,panel_name=None,tab_name=None,args=()):
        """
        Add a panel to the current tab
        
        Inputs
        ------
        panel_type : str
            Type of panel, used as a key for self.panel_classes dict
        
        panel_name : str
            Name to go in the window
            
        tab_name : str
            The name of the tab where the panel is to go. If None then the 
            current tab is used.

        args : list or tuple
            Arguments for the panel
        
        """
        #print(args)
        if not panel_name:
            panel_name = "%s %i" % (panel_type,self.panel_classes[panel_type].count)
            
        
        logger.debug("addPanel2MainArea: Adding panel [%s]" % panel_type)
        
        # Get the current MDI window
        tab_list = self.getTabList()
        if not tab_name or tab_name not in tab_list:
            currentDockArea = self._gui.mainArea.currentWidget()
        else:
            currentDockArea = self.getTabDockArea(tab_name)
        
        # Create new panel,
        # -------------------
        # passing the API and current tab FlexiDock
        # check for arguments
        if not args:
            newPanel = self.panel_classes[panel_type].panel_class(self,currentDockArea)
            newPanel.type = panel_type
        else:
            newPanel = self.panel_classes[panel_type].panel_class(self,currentDockArea,args=tuple(args))
            newPanel.type = panel_type
        
        # Set panel name
        # -----------------
        # increment count for this panel
        self.panel_classes[panel_type].count +=1
        
        # Set the name and comms ID
        newPanel.name = panel_name
        newPanel.ID = "%s %i" % (panel_type,self.panel_classes[panel_type].count)
        
        
        # Connect channel delete signal
        self.connect(self.channelSelector,SIGNAL("DeleteChannel"),newPanel.deleteChannel)
                
    
        # Add title to window
        window = currentDockArea.addWindow(newPanel,title=newPanel.name)
        
        # Add tab name to panel
#        if not tab_name or tab_name not in tab_list:
#            newPanel.tab = self.getCurrentTabName()
#        else:
#            newPanel.tab = tab_name
        
        # Setup activator switch
        self.connect(window,SIGNAL("aboutToActivate()"),newPanel.onActivation)
        
        self.connect(window,SIGNAL("windowStateChanged(Qt::WindowStates,Qt::WindowStates)"),newPanel.windowStateChange)
        
        newPanel.onActivation()
        
        
        # Add to API if required
        if self.panel_classes[panel_type].add_to_API and self.panel_classes[panel_type].single_instance:
            self.add_panel_to_API(self.panel_classes[panel_type].API_attribute_name,newPanel)
            
        return newPanel
        
        
        
    def addPanel2Sidebar(self,panel_type):
        """
        Add a panel to the sidebar
        
        Inputs
        ------
        panel_type : str
        
        """
        
        # Check if the sidebar already has this panel
        sidebar_tab_names = self._gui.get_sidebar_tab_list()
        
        if panel_type in sidebar_tab_names:
            return
        
        logger.debug("addPanel2Sidebar: Adding panel [%s]" % panel_type)       
        
        
        # Create new panel, passing the API 
        panel = self.panel_classes[panel_type].panel_class

        newPanel = panel(self)
        newPanel.name = panel_type
        newPanel.ID = panel_type # TODO make this better
        
        self._gui.add_to_sidebar(newPanel,panel_type)
        
        # Add to API if required
        if self.panel_classes[panel_type].add_to_API and self.panel_classes[panel_type].single_instance:
            self.add_panel_to_API(self.panel_classes[panel_type].API_attribute_name,newPanel)
        
        return newPanel
    
    
    def open_startup_panels(self):
        """
        Open any panels that are flagged as startup panels when loaded
        
        """
        logger.debug("API/open_startup_panels: Is being called")
        
        sidebar_tab_names = self._gui.get_sidebar_tab_list()
        
        for panel_name in self.panel_classes:

            if self.panel_classes[panel_name].open_on_startup:
                # Panels can only appear in the sidebar once, if a
                # panel is already in it then reject.
                if self.panel_classes[panel_name].location==SIDEBAR :
                    if panel_name not in sidebar_tab_names:
                        logger.debug("Opening panel [%s] in sidebar" % panel_name)                    
                        #self.addPanel2Sidebar(panel_name)
                        self.addPanel(panel_name)
                else:
                    logger.debug("Opening panel [%s] in main area" % panel_name)
                    #self.addPanel2MainArea(panel_name)
                    self.addPanel(panel_name)
        
    

    def add_panel_to_API(self,attribute_name,panel):
        """
        Add a panel to the API as an attribute, so that the API can
        have direct access.
        
        It uses the panel class attribute "API_attribute_name" to define
        the name.
        
        """
        
        self.__dict__[attribute_name] = panel
        
    
    def panelID(self,panel_name):
        """
        Get the panel comms name from the name
        
        Inputs
        -------
        panel_name : str
            corresponds to the 'name' field in a panel class
            
        Output
        -------
        panel_ID: str
            return ID field from panel class
            
        """
        
        # Go through the _receivers attribute and find the ID corresponding
        # to the panel name specified
        
        # Get a dictionary of panel IDs and names
        strip = lambda s: s.replace('&','')
        name2ID = {strip(self._receivers[ID].name):ID for ID in self._receivers}
        
        if panel_name not in name2ID:
            logger.debug("panelID: Cannot find an ID for panel [%s]" % panel_name)
            return
            
        return name2ID[panel_name]
        
        
    def allPanels(self):
        """
        Get a dicitonary of all the open panels and their IDs
        
        Output
        -------
        panels_dict: dict
            [panel_name:panel_ID]
            
        """
        return {self._receivers[ID].name:ID for ID in self._receivers}
        
        
        
    def setSidebarTab(self,tab_name):
        """
        Set the current tab on the sidebar
        
        Input
        -------
        tab_name :str
            Name of current tab
            
        """
        
        self._gui.set_sidebar_by_name(tab_name)
            
            

    #======================================================================
    #%% +++++ Main Area functions
    #======================================================================
    def deleteMainAreaWindow(self,window_widget):
        """
        Delete a window from main area
        
        * Find the window on any tab
        * Delete
        
        Inputs
        -------
        window_widget : QMDISubWindow 
        
        """
        
        
        # Go through each tab and look for the widgets
        
        # Get number of tabls
        nTabs = self._gui.mainArea.count()
        
        for tabIndex in range(nTabs):
            # Get MDI area
            MDIarea = self._gui.mainArea.widget(tabIndex)
            
            # Get a list of windows
            window_list = MDIarea.subWindowList()
            
            # If the window to be deleted is here then delete it
            if window_widget in window_list:
                MDIarea.removeSubWindow(window_widget)
                
                # We're done get out of the loop
                break
            
            
                
        
            

    #======================================================================
    #%% +++++ File opening functions
    #======================================================================       

    def loadCSV(self,filename):
        """
        Load data from CSV file
        
        Inputs:
        -----------
        filename : str
            full path/filename of CSV file
            
        """
        
        # Split up filename
        # ----------------------
        path,file = os.path.split(filename)
        
        # Load the file into a list of dictionary
        # ----------------------------------------
        with open(filename,'r') as f:
            reader = csv.DictReader(f)
            
            txtRows = []
            for row in reader:
                txtRows.append(row)
                
        # Convert to a recarray
        array = util.listOfDict2Recarray(txtRows)
        
        # Add to groups dictionary
        self.addGroup(file,array)
        
        
        
        #channelData = (file,array)
        #self.addChannelData(channelData)
        
    #======================================================================
    #%% +++++ Group functions
    #======================================================================

    def addGroup(self,group_name,group_array):
        """
        Add a new group into memory
        
        """
        
        # Add group data into dictionary
        self.group_dict[group_name] = group_array
        
        # Signal to Group panel to update
        self.groupModel.addGroup(group_name)
        
        # Adjust first column of group tree panel size of contents
        self.groupTree.resizeColumnToContents(0)
        self.groupTree.resizeColumnToContents(1)
        
     
    def getSelectedGroupColumns(self):
        """
        Get selected columns from the Groups panel tree view
        Returns the group and channel
        
        Output:
        ---------
        group_column : tuple of strings
            (groupName,columnName)
        
        """
        
        selection = self.groupTree.selectedIndexes()
        selectedColumns = self.groupModel.getSelectedGroupColumnsFromIndex(selection)
        
        print("Groups Tree: Selected column:",selectedColumns)
        
        
        # There should only be one item in the list so return that
        if selectedColumns:
            return selectedColumns[0]
        else:
            return
        
        
    
    def channelFromGroupData(self,channel_name,x_data,y_data):
        """
        Create a channel from a two columns of a group
        
        Inputs
        -------
        channel_name : str
            new channel name
            
        x_data : tuple
            (group_name,column_name) reference to data column in group
            
        y_data : tuple
            (group_name,column_name) reference to data column in group
            
        """
        
        # Validate the group data
        # ------------------------------
        x_group,x_column = x_data
        y_group,y_column = y_data
        
        if x_column not in self.group_dict[x_group].dtype.names:
            self.statusBar().showMessage("Invalid column %s in group: %s" %(x_column,x_group), 5000)
            return
            
        if y_column not in self.group_dict[y_group].dtype.names:
            self.statusBar().showMessage("Invalid column %s in group: %s" %(y_column,y_group), 5000)
            return
        
        
        # Data validation
        # -----------------------
        # Allow data from different groups but check the lengths are the same

        col_length = len(self.group_dict[x_group][x_column])        
        
        if len(self.group_dict[y_group][y_column]) != col_length:
            self.statusBar().showMessage("Cannot make channel from %s and %s they are different lengths" %(x_column,y_column), 5000)
            return
            
            
        # Prepare channel data
        # ------------------------
        dtype = [(x_column,float),(y_column,float)]
        
        recarray = np.zeros(col_length,dtype)
        
        recarray[x_column] = self.group_dict[x_group][x_column]
        recarray[y_column] = self.group_dict[y_group][y_column]
        
        self.addChannelData((channel_name,recarray))
        
            
        
    #======================================================================
    #%% +++++ Theme functions
    #======================================================================

    def setTheme(self,theme_name):
        """
        Set the application theme from CSS file
        
        Read CSS file and apply to main window 
        
        Input
        -------
        theme_name : str
            name in self.theme_dict
            
        """
        
        if theme_name not in self.theme_dict:
            logger.debug("Theme: tried to set unknown theme [%s]" % theme_name)
            return
        
        css_file = self.theme_dict[theme_name]
        self.preferences.theme = theme_name
        
        if os.path.exists(css_file):
            
            with open(css_file,'r') as file:
                style_sheet = file.read()
                
            # Load any icons that are with the theme
            path, filename = os.path.split(css_file)
            self.icons.load(path)

                
            logger.debug("Set theme from [%s]" % css_file)
            self.setThemeStyleSheet(style_sheet)
#            self._gui.setStyleSheet(style_sheet)
#            self._gui.update()
#            
#            # Send out a themeChanged signal through ScopePy comms
#            self.sendComms("themeChanged",self.BROADCAST)
            
            
            
    def setThemeStyleSheet(self,style_sheet):
        """
        Set application theme using CSS stylesheet
        
        Input
        ---------
        style_sheet : str
            Application level style sheet to be used. Follows CSS conventions 
            and those used by QT
            
        """
        
        self._gui.setStyleSheet(style_sheet)
        self._gui.update()
        
        # Send out a themeChanged signal through ScopePy comms
        self.sendComms("themeChanged",self.BROADCAST)
        
            
            
    def getThemePath(self,theme_name):
        """
        Return path/filename to theme.css file
        
        Output
        ------
        path : str
        """
        
        if theme_name not in self.theme_dict:
            logger.debug("Theme: tried to set unknown theme [%s]" % theme_name)
            return
        
        path = self.theme_dict[theme_name]
        
        if os.path.exists(path):
            return path
            
        return
        
        
    def getThemeCss(self):
        """
        Return application theme as a Cascaded Style Sheet, CSS.
        
        Output
        --------
        css : str
            text of application style sheet
            
        """
        
        return self._gui.styleSheet()
        
        
    def getThemeSettings(self):
        """
        Return application theme as a dictionary.
        
        This is the application stylesheet converted into a dictionary for
        easier manipulation.
        
        Output
        -------
        theme_settings : dict
            Dictionary where every item in the CSS becomes a key
            TODO: more detail
            
        """
        
        
        return csslib.getCss(self.getThemeCss())
        
        
        
    def getPlotThemeByName(self,theme_name):
        """
        Get the plot theme by the name that appears in the GUI plots
        
        Input
        -----
        theme_name : str
            Name of theme, e.g. "Deep plot" or "Ghost plot"
            
        Output
        --------
        styleSheet_dict : dict
            dictionary as produced by csslib
            
            None if nothing found
            
        """
        
        selected_theme = None
        #self.plot_themes.pop("csslib_vars")
        
        for key in self.plot_themes:
            if self.plot_themes[key]['name'].lower() == theme_name.lower():
                selected_theme = key
                
        if not selected_theme:
            return
            
        return self.plot_themes[selected_theme]
    
    def getDefaultPlotThemeName(self):
        """
        Return name of default plot theme
        
        Output
        ------------
        name : str
            display name of theme
            
        """
        main_css = self.getThemeSettings()
        
        if "standard_plot" not in main_css:
            return None
            
        if 'name' not in main_css['standard_plot']:
            return None
            
        return main_css['standard_plot']['name']
        
        
        
        
    def getDefaultPlotThemeCss(self):
        """
        Get the default plot theme as specified in the main application theme
        
        Output
        -------
        css : str
            CSS description of plot theme
            
        """
      
        # Define a default CSS theme for the plot
        # ------------------------------------------
        default_plot_css = """
        standard_plot{
                plot-background-color: #000000;
                grid-color: #003400;
                axis-color: #444444;
                axis-label-color: #444444;
                axis-title-color:#666666;
                axis-limits-color: #666666;
                axis-limits-background:#303030;
                horiz-marker-color: #88a02f;
                vert-marker-color: #18a02f;
                border-color: #212121;
                border-grid:1;
                border-grid-color: #a00000;
            }
            """
        
        main_css = self.getThemeSettings()
        
        if "standard_plot" not in main_css:
            return default_plot_css
            
        if 'name' not in main_css['standard_plot']:
            return default_plot_css
        
        # Get name of theme that's in the main css file
        theme_name = main_css['standard_plot']['name']
        
        # Get settings for that theme
        theme_settings = self.getPlotThemeByName(theme_name)
        
        if theme_settings is None:
            return default_plot_css
            
        # Convert settings to CSS and return
        d = {}
        d['standard_plot'] = theme_settings
        return csslib.dictToCss(d)
        

    #======================================================================
    #%% +++++ Function key toolbar
    #======================================================================
    def setupFkeys(self):
        """
        Setup the API Function key options
        
        """
        
        # Define the list of Fkeys
        self.defineFkeys()
        
        # Change the keys
        self.Fkey_toolbar.setFkeyFunctions(self.Fkeys)
        
        # Update the toolbar
        self.Fkey_toolbar.update()
        

    def defineFkeys(self):
        """
        Define the API Function keys for the toolbar
        
        """
        
        def dummyFunction():
            print("Dummy function - Not implemented yet")
        
        self.Fkeys = [
                    ['F1','Help',dummyFunction],
                    ['F2','Edit',dummyFunction],
                    ['F3','Plot',self.addNewPlot],
                    ['F7','Python Editor',self.addPythonEditor]]

    def setupShiftFkeys(self):
        """
        Setup the API Function key options
        
        """
        
        # Define the list of Fkeys
        self.defineShiftFkeys()
        
        # Change the keys
        self.shiftFkeys.setFkeyFunctions(self.ShiftFkeys)
        
        # Update the toolbar
        self.shiftFkeys.update()
        

    def defineShiftFkeys(self):
        """
        Define the API Function keys for the toolbar
        
        """
        
        def dummyFunction():
            print("Dummy function - Not implemented yet")
        
        self.ShiftFkeys = [
            
                    ]
                    
                    
    #======================================================================
    #%% +++++ Python editor
    #======================================================================               
    def addPythonEditor(self,name=None):
        """
        Add new plot to current tab
        
        """
        
        self.addPanel('Python Editor',name)
        
        
    #======================================================================
    #%% +++++ Data sources
    #======================================================================
    def addDataSource(self,source_type,source_name,initial_data=None):
        """
        Inputs
        --------
        source_type: str
            source label, e.g. 'NumpyArray'
            
        source_name: str
            name of source that will appear in data source selector tree
            
        initial_data : source data, e.g. numpy array etc
        
        """
        # Validate inputs
        # -----------------------
        if source_type not in self.dataStore.source_creators:
            logger.debug("API.addDataSource: Unknown source [%s]" % source_type)
            return
            
        if not hasattr(self.dataStore.source_creators[source_type],'makeSource'):
            logger.debug("API.addDataSource: Source [%s] cannot make source" % source_type)
            return
        
        if not isinstance(source_name,str):
            logger.debug("API.addDataSource: Incorrect name for source [%s]" % source_type)
            return
        
        # Create the source node
        # ---------------------------------------
        node = self.dataStore.source_creators[source_type].makeSource(source_name,initial_data)
        
        
        # Add to data source selector
        # -------------------------------
        source_selector = self.panelID("Data Source Selector")
        
        if source_selector is not None:
            self.sendComms('addSource',source_selector,node)
            
    @property        
    def data_sources(self):
        """
        Return a list of the currently loaded data sources.
        
        Output
        --------
        source_list : list of str
            This is a list of the string labels for all the supported data 
            sources. These are the source_types that are used with the 
            addDataSource() function
            
        Example
        -----------
        >>> API.data_sources
        ['NumpyArray', 'hdf5', 'Dataframe', 'csv']
        
        """
        
        return list(self.dataStore.source_creators.keys())
        
        
    #======================================================================
    #%% +++++ Server functions
    #======================================================================
    def getCmdFromServer(self):
        # TODO
        pass
        
    
    #======================================================================
    #%% +++++ Debugging functions
    #======================================================================
    
    
    def ThisDidSomething(self,string="This"):
        """ Dummy function that prints a string.
        Use it to test if something is getting into the GUI
        """
        
        print("\n-----------------------")
        print("%s did something!" % string)
        print("\n-----------------------\n")
        
        
    def RunTest1(self):
        """ Function for testing things out
        Put testing code in here. This test is triggered by the 
        "Run Test 1" button in the test panel
        """
        
        channelName = "Test data %d" % 0
        
        print("\n\n=======================================================")
        print("Testing chunk extraction")
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("Extracting all chunks from [%s]" % channelName )
        
        chData = self.channel_dict[channelName].data('all')
        
        print("\nWhole array")
        print(chData.shape)
        print(chData)
        
        print("\nX axis data")
        print(chData["x axis text"])
        
    def RunTest2(self):
      """ Function for test things out
      """
      
      print("\n\n=======================================================")
      print("Testing channel selector size")
      print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
      print("Size of channel selector:",self.channel )
      
      
    def dumpChannels(self):
      """
      Print out a list of channels and chunks
      
      """
      
      print("\n\nChannel Dict contents:\n----------------------------\n\n")
      
      for name,channel in self.channel_dict.items():
          
          print("Name: %s" % name)
          print("\tChunks:%d" % channel.chunks )
          print("+"*20)
          
    def addMacro(self):
        namew = QInputDialog()
        name , wabblepop = namew.getText(self,"Macro","Type name of Macro")
        fname = QFileDialog.getOpenFileName(self,"Select Python Script For Macro",os.path.expanduser("~"),"Python Files (*.py)")
        mcro.addMacro(name,fname)
        self.setMacroMenu()
        
    def setMacroMenu(self):
        macros = mcro.getMacros()
        print("Macros = "+str(macros))
        alist = []
        _locals = {"API":API.API()}
        #try:
        for i in macros:
            print('i = '+str(i))
            #try:
            print(macros[i])
            filename = macros[i]
            print(filename)
            a = self.createAction(i,lambda: self.run(filename))
#                except Exception as ec:
#                     print('error: %s' % ec)
            print(a)
            alist.append(a)
            self.addAction(a)
        #except:
         #   print('error')
        print("alist = "+str(alist))
        self.addActions( self.macroMenu, (alist))
          
    def run(self,filename):
        print(filename)
        try:
            exec(open(filename,'r').read(),globals(),{'API':self.API})
        except Exception as ec:
            print('Error in Macro %s: '+str(ec) % filename)
       
       


#==============================================================================
#%% DataStore class
#==============================================================================

class DataStore():
    """
    Class for holding all the plotting data used by ScopePy.
    This can be channel or group data or anything else
    
    """
    
    def __init__(self,API_reference):
        """
        Set up intial storage structure
        """
        
        # API connection
        self.API = API_reference
        
        # ********************************************************
        #               Channels
        # ********************************************************
        # Initialise dictionary of channels, (x,y) data
        # Channel name will be the key
        self.channel_dict = {}
        
        # Thread lock for reading/writing common data
        self.channel_lock = QReadWriteLock()
        
        # ********************************************************
        #               Groups
        # ********************************************************
        # Dictionary to hold 'Groups' which are multiple column arrays
        # that can be used to create channels. Files read in are
        # put into groups. The user can then select columns from the 
        # group to make into channels for plotting.
        self.group_dict = {}
        # TODO : replace groups when Sources are working
        
        # ********************************************************
        #               Sources
        # ********************************************************
        # ScopePy can have many different 'sources' of data in memory.
        # This structure holds them in a tree structure. The reason for
        # this is that the main way to access sources is through the 
        # source selector panel, which is a QTreeView, so a tree structure
        # is needed for that.
        #
        # The structure of the sources tree is:
        # root node
        #   - Home node (displayed in source selector)
        #       - Datasource node
        #       - Datasource node
        #       - Datasource node
        #
        # Where Datasource nodes can represent a variety of different types
        # of source such as CSV and HDF5 files, numpy arrays, pandas dataframes
        # etc. These sources are defined in the data_sources folder inside 
        # the main ScopePy folder.
        #
        # Here we create the root and Home nodes then the loadSources() method
        # is used to load in any sources that it can find in the data_sources
        # folder.
        self.sources = DS.DatasourceNode('root',node_type='root')
        self.sources.API = self.API
        self.sources.icon_manager = self.API.icons
        self.HomeNode = DS.Home('Home',parent=self.sources)
        self.sources.addChild(self.HomeNode)
        
        # Initialise a dictionary for source creator classes
        # These will set up links to different sources
        # The classes used are defined in the data_sources folder.
        self.source_creators = {}
        
        #self.loadSources(BUILTIN_DATASOURCES_FOLDER)
        
        
        
        
    def loadSources(self,directory_list):
        """
        Load source creator objects
        
        This can either be used to initialise the dictionary of source_creators
        from scratch or to update it.
        
        Inputs
        ---------
        directory_list : list
            list of directories to search for sources
            
        """
        
        # Load the sources
        new_sources = DS.load_sources(directory_list)
        
        # Update the internal dictionary with an sources that have not already
        # been loaded
        for src in new_sources:
            if src not in self.source_creators:
                logger.debug("DataStore: loading source [%s]" % src)
                self.source_creators[src] = new_sources[src]
        
    @property
    def fileExtensions(self):
        """
        Return a list of file extensions for any data sources that are
        file based, e.g. CSV, HDF5.
        The file extensions are supplied by the source_creators
        
        Output
        ------------
        format_str : str
            format string for QFileDialog
        
        """
        
        file_ext = {}
        
        for name,creator in self.source_creators.items():
            # If it's a file and it has extensions then add them to
            # the dictionary as a string list
            if creator.isFile and creator.fileTypes != []:
                file_ext[creator.name] = "*."+" *.".join(creator.fileTypes)
                
        
        if file_ext == {}:
            return "*.*"
            
        # Create the format string
        ext_list  = []
        
        for name,ext in file_ext.items():
            ext_list.append('%s files (%s)' % (name,ext) )
            
        return ";;".join(ext_list)
                        
            
            
    def fileOpen(self,filename):
        """
        Select source to use for opening this filename based on extension.
        Otherwise pop up an alert box to say this can't be opened.
        
        If successful then add the file as a Datasource
        
        Input
        --------
        filename: str
            path/filename/extension
            
        """
        logger.debug("DataStore:fileOpen: Received [%s]" % filename)
        
        # Get type for file from extension and select the loading method
        dummy,ext = os.path.splitext(filename)
        ext = ext.lower()
        
        # Remove leading '.'
        if ext.startswith('.'):
            ext = ext[1:]
        
        selected_creator = None
        
        for name,creator in self.source_creators.items():
            # Find the creator for this type of file
            if creator.isFile and creator.fileTypes != []:
                if ext in creator.fileTypes:
                    selected_creator = creator
                    break
                
        if selected_creator is None:
            # TODO: Pop up a box here
            logger.debug("No data source for files of type %s" % ext)
            return
            
        # Create a node and add to home node
        logger.debug("Creating new source node with %s" % str(selected_creator))
        new_node = selected_creator.toNode(filename)
        #self.sources.child(0).addChild(new_node)
        
        # Update data source selector
        source_selector = self.API.panelID("Data Source Selector")
        
        assert source_selector is not None,"DataStore/fileOpen: Cannot find data source selector"
        
        self.API.sendComms('addSource',source_selector,new_node)
        
        return new_node
        
        
        
    def addSource(self,source_type,initial_data=None,name=None):
        """
        Add a source to the data source selector
        
        Inputs
        --------
        source_type : str
            An entry in the DataStore.source_creators{} dict
            
        initial_data : appropriate data to the source type
            initial data to go in source, can be None, then an empty
            source is created.
            
        """
        
        # Validate source type
        # ==========================
        if source_type not in self.source_creators:
            logger.debug("DataStore: source type [%s] cannot be found" % source_type)
            return
            
        
        creator = self.source_creators[source_type]
        
        if not hasattr(creator,'makeSource'):
            logger.debug("DataStore: source [%s] cannot add new sources" % source_type)
            return
            
            
        # Create a source
        # ==========================
        if not name:
            name = source_type
            
        new_node = creator.makeSource(name,initial_data)
        
        
        # Update data source selector
        # ====================================
        source_selector = self.API.panelID("Data Source Selector")
        
        assert source_selector is not None,"DataStore/addSource: Cannot find data source selector"
        
        self.API.sendComms('addSource',source_selector,new_node)
        
        return new_node
        
            

    def restoreSource(self,save_dict):
        """
        Restore a data source from a saved session.
        
        Take the data that was saved and use it to re-create the data source
        
        Input:
        ----------
        save_dict : dict
            Dictionary stored by the source node saveData() function.
            
        """
        
        if save_dict is None:
            logger.debug("save_dict is None")
            return
        
        # Validate input dict
        # --------------------------
        assert "creator" in save_dict, "Source dictionary does not specify creator"
        assert "isFile" in save_dict, "Source dictionary does not specify 'isFile' flag"
        
        
        # Create data source
        # --------------------------
        if save_dict['isFile'] == True:
            if 'filename' in save_dict:
                logger.debug("Loading source from file [%s]" % save_dict['filename'] )
                source_node = self.fileOpen(save_dict['filename'])
            else:
                return
                
        else:
            # Non-file source
            source_node = self.addSource(save_dict['creator'])
            
            
        # Re-store source data
        # -------------------------
        if hasattr(source_node,'restoreData'):
            logger.debug("Restoring source [%s]" % source_node.name)
            source_node.restoreData(save_dict)
        
        
        return source_node
        
        
    def saveSourcesToSession(self,session):
        """
        Store data sources into a session structure
        
        Input
        -----------
        session : SessionStore class object
            session in which to store the sources
            
        """
        logger.debug("Saving sources")
        # Validate sources
        nSources = self.HomeNode.childCount()
        logger.debug("Found %i sources" % nSources)
        
        if nSources == 0:
            return
            
        # Clear sources list
        session.data_sources = []
        
        # Run through all the children of the home node and store them
        for child_index in range(nSources):
            source = self.HomeNode.child(child_index)
            print("\tSource = ",source)
            if hasattr(source,'saveData'):
                logger.debug("Storing source [%s][%s]" % (source.creator,source.name()))
                session.data_sources.append(source.saveData())
        
        
        
    def restoreSourcesFromSession(self,session):
        """
        Restore data sources that have been saved in a session
        
        Input
        -----------
        session : SessionStore class object
            session in which to store the sources
            
        """
        
        # No source case
        if session.data_sources is None or session.data_sources == []:
            return
            
        # Restore all saved data sources
        for save_dict in session.data_sources:
            self.restoreSource(save_dict)
        
            
            
        
        


#==============================================================================
#%% MenuManager and ToolbarManager classes
#==============================================================================
# These classes are proxies for the menu and toolbars, they allow anything in
# the API to add menus, menu items and toolbar buttons.
# The GUI then uses the final versions of each class to draw the menu and toolbars.

class MenuManager():
    """
    Class that stores menus
    
    The basic structure is:
    
    * <Menu 1 name> : list
        - <Menu item 1>  QAction
        - <Menu item 2>  QAction

    * <Menu 2 name> : list
        - <Menu item 1>  QAction
        - <Menu item 2>  QAction        
        
    This is implemented in the class as a dictionary of lists. 
    Then there are extra class methods for convenient access.
    
    """
    
    def __init__(self):
        """
        Create the basic structure for the menu
        
        """
        
        # Dictionary for storing menus
        # Use an ordered dictionary because the order of entry will correspond
        # to the order of the menus
        self.menus = OrderedDict()
        
        
    def addMenu(self,menu_name,menu_action_list):
        """
        Add a new menu
        
        Inputs
        --------
        menu_name : str
            name of menu as it appears on the menu bar
            
        menu_action_list : list
            list of menu items (QActions) in the order that they will appear
            
            
        """
        
        self.menus[menu_name] = menu_action_list
        
        # Store a dictionary link to each menu
        self._menu_objects = {}
        

    def makeMenus(self,menu_bar):
        """
        Make all menus from the data in MenuManager
        
        Inputs
        -------
        menu_bar : QMenuBar
            Menu bar (of main window)
        
        """
        
        for menu in self.menus:
            # Must make a menu using the menu_bar.addMenu() function
            # this keeps the ownership with the main window
            new_menu = menu_bar.addMenu(menu)
            addActions( new_menu, self.menus[menu])
            self._menu_objects[menu] = new_menu
            
            
            
    def updateMenu(self,menu_bar,menu_name):
        """
        Update a single menu on a menu bar
        
        Assumes the actions have been updated elsewhere
        
        """
        
        if menu_name not in self._menu_objects:
            return
            
        # Get the menu that is to be updated
        menu = self._menu_objects[menu_name]
        
        # Clear the menu
        menu.clear()
        
        # Reconstruct the menu
        addActions( new_menu, self.menus[menu])
        
            
            
            
    def getMenu(self,menu_name):
        """
        Return a link to the menu object
        
        Inputs
        ------
        menu_name : str
            Name of menu e.g. "&File"
            
        Outputs
        ---------
        menu_object : QMenu()

        """
        if menu_name in self._menu_objects:
            return self._menu_objects[menu_name]

        return            
        
            


class ToolbarManager():
    """
    Class that stores actions to be placed in toolbars. Any of the 4 positions
    of the toolbars can be used.
    
    The basic structure is:
    
    * <toolbar1 e.g 'top'> : list
        - <button 1>  QAction
        - <button 2>  QAction

    * <toolbar1 e.g 'bottom'> : list
        - <button 1>  QAction
        - <button 2>  QAction      
        
    This is implemented in the class as a dictionary of lists. 
    Then there are extra class methods for convenient access.
    
    """
    
    # TODO : Setting different types of toolbar doesn't work yet
    names = {'top':Qt.TopToolBarArea,'bottom':Qt.BottomToolBarArea,
             'left':Qt.LeftToolBarArea,'right':Qt.RightToolBarArea}
    
    def __init__(self):
        """
        Create the basic structure for the menu
        
        """
        
        # Dictionary for storing menus
        # Use an ordered dictionary because the order of entry will correspond
        # to the order of the menus
        self.toolbars = {}
        
        
    def addButton(self,toolbar_name,button_actions):
        """
        Add 
        
        Inputs
        --------
        toolbar_name : str
            name of toolbar ['top','bottom','left','right']
            
        button_action: list of QAction
            list of actions to add to toolbar
            
            
        """
        # Convert to lower case
        toolbar_name = toolbar_name.lower()
        
        # Check correct name
        if toolbar_name not in self.names:
            logger.debug('ToolbarManager:Unknown Toolbar name [%s]' % toolbar_name)
            return
        
        # Check if toolbar has already been created, if not create it
        if toolbar_name not in self.toolbars:
            self.toolbars[toolbar_name] = []
            
        # Add actions to toolbar list
        for action in button_actions:
            self.toolbars[toolbar_name].append(action)
        
        

    def makeToolbars(self,main_window):
        """
        Make all toolbars from the data in ToolbarManager
        
        Inputs
        -------
        main_window : QMainWindow
            link to main window
        
        """
        
        for toolbar_name in self.toolbars:
            
            toolbar = QToolBar()
            #toolbar.setObjectName("topToolBar")
            addActions(toolbar, self.toolbars[toolbar_name])
            main_window.addToolBar(self.names[toolbar_name],toolbar)
            
            
            
def addActions(target, actions):
    """
    Function for adding actions to either a toolbar or a menu
    borrowed from Mark Summerfields book.
    
    """
    
    for action in actions:
        if action is None:
            target.addSeparator()
        else:
            target.addAction(action)
            
            


class IconManager():
    """
    Class for loading, storing and serving icons to all parts of the ScopePy
    that require them.
    
    Usage
    --------
    
    Create icon manager
    >>> IM = IconManager()
    
    Load Icons from a path
    >>> IM.load(path)
    
    Get a stored icon
    >>> icon = IM[icon_name]
    
    icon_name is usually the filename of the icon
    
    Store an icon
    >>> IM[new_icon_name] = filename
    >>> IM[new_icon_name] = QIcon(...)
    >>> IM[new_icon_name] = QPixmap(...)
    
    """
    
    def __init__(self):
        
        # Icon store
        # =====================
        # This is a dictionary that contains the icons
        # The format is {icon_name:QIcon}
        # Used by the __getitem__ method
        self.icons = {}
        
        # File types
        # ===============
        # Acceptable file types for icons
        # Read this from QT
        self.file_types = ["."+fmt.data().decode().lower() for fmt in QImageReader.supportedImageFormats()]
        
        
    def __getitem__(self,icon_name):
        """
        Return a QIcon that corresponds to the specified name. If the name
        does not exist then an empty QIcon is returned.
        
        """
        if icon_name in self.icons:
            return self.icons[icon_name]
        else:
            return QIcon()
            

    
    def __setitem__(self,icon_name,icon_link):
        """
        Add a new icon to the store. The icon is specified as either a full
        path/filename, a QIcon or a QPixmap
        
        Inputs
        -------
        icon_name : str
            The name to which this icon will be referenced
            
        icon_link: str, QIcon, QPixmap
            type of icon source
        
        """
        # Deal with QIcon and QPixmap cases first
        # -----------------------------------------
        if isinstance(icon_link,QIcon):
            self.icons[icon_name] = icon_link
            return
            
        if isinstance(icon_link,QPixmap):
            self.icons[icon_name] = QIcon(icon_link)
            return
            
        # Check this is a string
        if not isinstance(icon_link,str):
            logger.debug("IconManager:Tried to add icon with unknown link type %s" % str(type(icon_link)))
            return
        
        # Load icon from file
        # ---------------------------
        
        # Does file exist
        if not os.path.exists(icon_link):
            logger.debug("IconManager:Unknown icon file [%s]" % icon_link)
            return
            
        # What type of file
        name,ext = os.path.splitext(icon_link)
        
        if ext.lower() not in self.file_types:
            logger.debug("IconManager: Unsupported image format [%s] for file [%s]" % (ext,icon_link))
            return
            
        # Load the icon
        self.icons[icon_name] = QIcon(icon_link)
        
        
        
    def load(self,path):
        """
        Load all icons from a path
        
        Any image files on the path will be loaded into the icon store
        
        Input
        --------
        path : str
            full path
        
        """
        
        if not os.path.exists(path):
            return
            
        # Get all files
        # ----------------------
        all_files = os.listdir(path)
        
        # Load any image files
        for file in all_files:
            logger.debug("IconManager: File [%s]" % file)
            
            # Check for valid extensions
            name,ext = os.path.splitext(file)
            
            if ext.lower() in self.file_types:
                try:
                    self.__setitem__(name,os.path.join(path,file))
                    
                except:
                    logger.debug("IconManager: Failed to load [%s]" % file)
                    
                    
                        
        
        
        
#==============================================================================
#%% Session save/load classes
#==============================================================================
# The classes defined here are used for storing the 'state' of the current 
# ScopePy session, i.e. all the tabs that are open, all the channels in the
# channel selector, all the data sources
        

class SessionStore():
    """
    Class that stores the current session of ScopePy, all channels, data sources
    open panels* etc.
    
    *If that makes sense
    
    It is basically a storage structure that will be saved into a pickle file.
    
    """
    
    # Reference
    version = 1
    
    def __init__(self):
        """
        Initialise the instance variables
        
        """
        
        
        self.tabs = None          # List of open tabs
        self.channels = None      # dict of channels
        self.data_sources = None  # List of data_sources
        self.panels = {}          # dict of panel data
        
        

