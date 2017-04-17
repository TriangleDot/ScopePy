# -*- coding: utf-8 -*-
"""
Created on Sat May 24 20:32:58 2014

@author: john

ScopePy
==========
Main GUI window

Version
==============================================================================
$Revision:: 180                           $
$Date:: 2017-04-01 20:49:22 -0400 (Sat, 0#$
$Author::                                 $
==============================================================================


"""

#==============================================================================
#%% License
#==============================================================================

"""
Copyright 2016 John Bainbridge

This file is part of ScopePy.

ScopePy is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ScopePy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ScopePy.  If not, see <http://www.gnu.org/licenses/>.
"""

#==============================================================================
#%% Imports
#==============================================================================
import os
import sys
import time
import logging
import configparser
import pickle

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *

import numpy as np

import ScopePy_network as nw
import ScopePy_channel as ch
import ScopePy_panels as panels
import ScopePy_utilities as util
import ScopePy_widgets as wid
import ScopePy_graphs as graphs
import ScopePy_API as API
import ScopePy_preferences as prefs
import Macro as mcro


#==============================================================================
#%% Version number
#==============================================================================

__version__ = "$Revision:: 180        $"

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
con.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('[%(asctime)s:%(name)s:%(levelname)s]: %(message)s')

# add formatter to ch
con.setFormatter(formatter)

# add ch to logger
logger.addHandler(con)


#==============================================================================
#%% Constants
#==============================================================================
idle = False
if idle == True:
    __file__ = '/home/pi/python/ScopePy/ScopePy_GUI.py'

DEBUG = False
DEBUG_ON_CONSOLE = False
#DEBUG_ON_CONSOLE = True

BASEPATH, dummy = os.path.split(os.path.abspath(__file__))





#==============================================================================
#%% Main GUI class
#==============================================================================
class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        # Initialise parent object
        super(MainWindow, self).__init__(parent)
        
        
        #-------------------------------------
        #logger!
        #-------------------------------------
        try:
            f = open(os.path.join(os.path.expanduser('~'),'.ScopePy','log.html'),'w')
        except FileNotFoundError:
            os.mkdir(os.path.join(os.path.expanduser('~'),'.ScopePy'))
            f = open(os.path.join(os.path.expanduser('~'),'.ScopePy','log.html'),'w')
        f.write('''<html>
        <style>
        html {
        background-color: black;
        }
        </style>''')
        f.close()
        self.logWidget = QTextEdit(self)
        self.logWidget.setReadOnly(True)
        self.logWidget.clear = lambda : print('Somebody wanted to clear me!')
        self.logWidget.boldwrite = self.boldwrite
        self.logWidget.italicwrite = self.italicwrite
        self.logWidget.normalwrite = self.normalwrite
        self.logWidget.debug = self.debug
        self.logWidget.workes = self.workes
        self.logWidget.error = self.error
        self.logWidget.InsertHtml = self.bufferedInsert
        self.oldout = sys.stdout
        self.olderr = sys.stderr
        if not DEBUG_ON_CONSOLE:
            sys.stdout.write = self.debug
            sys.stderr.write = self.error

        self.onLog = True
        #self.onLog = False
            
        #logger.debug('this should be yellow')
        
        
        

        # ********************************************************
        #         Application Programming Interface (API)
        # ********************************************************
        self.workes('ScopePy starting on '+time.asctime()+'\n')
        self.workes("-"*50+'\n')
        self.API = API.API(self,parent=self)
        
        # Set the icon
        # Don't put a slash in front of images
        #self.setWindowIcon(QIcon(os.path.join(BASEPATH,'images/app_icon.png'))) 
        self.setWindowIcon(self.API.icons['app_icon']) 
      
        
        
        # ********************************************************
        #               GUI Layout
        # ********************************************************
        
        # Main widget is a horizontal splitter
        # Channel selector is on the left and the scope screen is on the right
        self.mainSplitter = QSplitter(Qt.Horizontal)
        
        # Function key toolbar
        self.addToolBar(self.API.Fkey_toolbar)
        self.addToolBar(Qt.BottomToolBarArea,self.API.shiftFkeys)
        
        self.setup_sidebar()
        self.setup_main_area()        

        # Setup the sizing stretch factor for sidebar and main area
        # sidebar should be smaller than main area
        self.mainSplitter.setStretchFactor(0,0)
        self.mainSplitter.setStretchFactor(1,3)
#        w = self.mainSplitter.width()
#        print('Mainsplitter width = %i' % w)
#        self.mainSplitter.setSizes([round(w/4),round(3*w/4)])
        
        # Set central widget
        self.setCentralWidget(self.mainSplitter)
        
        
        
            
        
        # ********************************************************
        #               Panels
        # ********************************************************
        #self.API.load_panels()
        self.API.open_startup_panels()

        
        # Setup menus and toolbars
        self.setup_menus()
        self.setup_toolbars()
        
        
        # ********************************************************
        #               Server
        # ********************************************************
        self.setup_server()
        


        # ********************************************************
        #               Application startup
        # ********************************************************
        self.setWindowTitle("ScopePy - Interactive Data Plotter : Unsaved session")
        self.statusBar().showMessage("Ready...", 5000)
        self.show()
        
        self.API.addNewTab()
        
        
        
    
    #======================================================================
    #%%Log functions
    #======================================================================
    
    # <font color="red">This is some text!</font> 
    def error(self,string):
        
        #print(string[0])
        if string[0] == '[':
            l = True
            self.debug(string)
            return
#
        if self.checkIf(self.olderr,string):
            string = string.replace('\n','<br>')
        #if l:
        #   self.logWidget.insertHtml('<font color="#e4b320">%s</font>' % string) 
        #else:
        #if not l:
            self.logWidget.InsertHtml('<b><font color="red">%s</font></b>' % string) 
            
    def bufferedInsert(self,msg):
        f = open(os.path.join(os.path.expanduser('~'),'.ScopePy','log.html'),'a')
        f.write(msg)
        f.flush()
        f.close()

        self.logWidget.insertHtml(msg)
        
        

    def checkIf(self,w,string):
        if not self.onLog:
            print(string,file=w)
            return False
        else:
            return True
    def workes(self,string):
        
        if self.checkIf(self.oldout,string):
            string = string.replace('\n','<br>')
            self.logWidget.InsertHtml('<em><font color="green">%s</font></em>' % string) 
        
    def debug(self,string):
        
        if self.checkIf(self.oldout,string):
            string = string.replace('\n','<br>')

            self.logWidget.InsertHtml('<font color="#e4b320">%s</font>' % string) 
        
    def boldwrite(self,string):
        string = string.replace('\n','<br>')
        if self.checkIf(self.oldout,string):
            self.logWidget.InsertHtml('<b>%s</b>' % string)
        
    def italicwrite(self,string):
        string = string.replace('\n','<br>')
        if self.checkIf(self.oldout,string):

            self.logWidget.InsertHtml('<em>%s</em>' % string) 
        
    def normalwrite(self,string):
        string = string.replace('\n','<br>')
        if self.checkIf(self.oldout,string):
            self.logWidget.InsertHtml('%s' % string) 
        
    """
    ======================================================================
    #%%Helper functions
    ======================================================================
    """
        
    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
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
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)


    
    def closeEvent(self,event):
        """
        Call API closing function
        """
        self.API.closeApp()
        
        

    # ********************************************************
    #               GUI objects
    # ********************************************************
    def setup_sidebar(self):
        """
        Setup the tab stack at the side of the screen
        
        """
        
        # Master sidebar tab stack
        self.sidebar = QTabWidget()
        self.sidebar.sizePolicy().setHorizontalPolicy(QSizePolicy.Minimum)
        self.sidebar.setMinimumSize(200,600)
        
        # Add log widget by default
        self.sidebar.addTab(self.logWidget,'Log')
        
        # Frame to go around the tab stack
        sidebarPane = QFrame()
        sidebarPane.setFrameStyle(QFrame.Panel | QFrame.Raised)
        sidebarPane.setLineWidth(3)
        #sidebarPane.setMinimumSize(QSize(200,600))
#        sidebarPane.setMaximumSize(QSize(450,2000))
        
        sidebarPane.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Preferred)
        
        
        sidebarPaneLayout = QVBoxLayout()
        sidebarPaneLayout.addWidget(self.sidebar)
        
        sidebarPane.setLayout(sidebarPaneLayout)

        # Add sidebar to the main screen splitter
        self.mainSplitter.addWidget(sidebarPane)
        
        
        # Connect changed signal to API
        self.connect(self.sidebar, SIGNAL("currentChanged(int)"),self.API.sidebarTabChanged)
        
        
        
    def add_to_sidebar(self,widget,tab_name):
        """
        Add a widget to the sidebar tab stack
        
        Inputs
        -------
        widget : A QT widget
        
        tab_name: str
            name of the tab
            
        """
        
        #self.sidebar.addTab(widget,tab_name)
        
        # Insert new widget at the front and make it current
        self.sidebar.insertTab(0,widget,tab_name)
        self.sidebar.setCurrentIndex(0)
        
    
    def get_sidebar_tab_list(self):
        """
        Return a list of tab names in the correct order
         
        Outputs
        -------
        tab_list: list of str
            list of the tab label names
             
        """
         
        nTabs = self.sidebar.count()
         
        tab_list = [self.sidebar.tabText(index) for index in range(nTabs)]
         
        return tab_list
        
        
    def get_sidebar_current_tab_widget(self):
        """
        Get the current tab widget from sidebar
        
        """
        
        return self.sidebar.currentWidget()
        
        
    def set_sidebar_by_name(self,tab_name):
        """
        Set current sidebar tab
        
        """
        strip = lambda s: s.replace('&','')
        
        tab_name_list = [strip(name) for name in self.get_sidebar_tab_list()]
        
        if tab_name not in tab_name_list:
            return
            
        index = tab_name_list.index(tab_name)
        
        self.sidebar.setCurrentIndex(index)
        

        

    def setup_main_area(self):
        """
        Setup the Main area where plots and panels are displayed
        
        """
        
        # Create Tabs
        # =======================
        # Empty Tabs to start
        self.mainArea = QTabWidget()
        self.mainArea.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        
        # Add Tab bar with editable tab names
        tabBar = wid.TabBar(self.mainArea)
        tabBar.setTabsClosable(True)
        self.mainArea.setTabBar(tabBar)
                        
        # Add an empty scope screen
#        self.addNewTab(add_plot=True)
        
        
        # Add Scope tab to the main screen
        self.mainSplitter.addWidget(self.mainArea)
        
        # Tab signals
        # ====================
        # Update chunk selector panel when tab changes
        self.connect(self.mainArea,SIGNAL("tabCloseRequested (int)"),self.API.deleteTab)
        

    def add_tab_to_main_area(self,widget,tab_name):
        """
        Add a widget/tab to the main area tab stack
        
        Inputs
        -------
        widget : A QT widget
        
        tab_name: str
            name of the tab
            
        """
        
        self.mainArea.addTab(widget,tab_name)
        
        
    def load_macros(self):
        """
        Load all macros found at startup
        
        """
        
        pass
    
    def load_math_functions(self):
        """
        Load existing math functions
        
        """

        # ********************************************************
        #               Math function loading
        # ********************************************************
        # Dynamically import math functions
        
        # Get any user folders from configuration
        if self.preferences.mathFunctionPaths !=[]:
            math_folder_list = [BUILTIN_MATHFUNCTIONS_FOLDER] + self.preferences.mathFunctionPaths
        else:
            math_folder_list = [BUILTIN_MATHFUNCTIONS_FOLDER]
        
        # load panel classes
        self.math_functions = ch.load_math_functions(math_folder_list)
        logger.debug('GUI: Math functions loaded:')
        print([mf.name for mf in self.math_functions])        


    def setup_actions(self):
        """
        Create actions for menus and toolbars
        
        """
        # TODO : temporary dump for the code that does actions, menus and toolbars
        # needs sorting out        
        
        
        # ********************************************************
        #               Actions
        # ********************************************************
        shortcuts = self.API.preferences.keyboard['main']
        
        # File Menu TODO : What do we want to save? channel data
        # ================
        fileNewAction = self.createAction("&New...", self.fileNew,
                icon=QIcon.fromTheme("document-new"), tip="Create new channel")
        fileOpenAction = self.createAction("&Open...", self.fileOpen,
                shortcuts['open'], QIcon.fromTheme("document-open"),
                "Open an existing channel data file")
        fileSaveAction = self.createAction("&Save", self.fileSave,
                shortcuts['save'], QIcon.fromTheme("document-save"), "Save the channel")
        fileSaveAsAction = self.createAction("Save &As...",
                self.fileSaveAs, icon=QIcon.fromTheme("document-save-as"),
                tip="Save the image using a new name")
                
        filePreferencesAction = self.createAction("Pre&ferences...", self.filePreferences)
        
        fileQuitAction = self.createAction("&Quit", self.close,
                "Ctrl+Q", "filequit", "Close the application")

# TODO : restore this later                
#        # Tabs/View ports
#        # ====================
#        tabAddNewAction = self.createAction("New &Tab", self.addNewTab,
#                shortcuts['newTab'],tip = "Add New tab")
#                
#        tabDeleteAction = self.createAction("Delete Tab", self.deleteTab,
#                tip= "Delete current tab")
#                
#        # Plots
#        # ==============
#        plotAddNewAction = self.createAction("New P&lot", self.addNewPlot2Tab,
#                shortcuts['newPlot'],tip = "Add New plot to current tab")
#                
#        # Testing
#        # =================
#        testChannelAction = self.createAction("Test Channel", self.makeTestChannel,
#                tip = "Make a test channel")
#                
#        dumpChannelsAction = self.createAction("Dump Channel list", self.dumpChannels,
#                tip = "Dump list of channels to console")
                
                
        # ********************************************************
        #               Menus
        # ********************************************************
                
        # File menu
        # ----------------
        self.fileMenu = self.menuBar().addMenu("&File")
        self.addActions( self.fileMenu, (fileNewAction, fileOpenAction,
                fileSaveAction, fileSaveAsAction,filePreferencesAction,  
                fileQuitAction))
        

# TODO : restore this later                
#        self.macroMenu = self.menuBar().addMenu("&Macro")
#        macroAction = self.createAction("&Add Macro...", self.addMacro,
#                  tip = "Add new Macro option")
#                  
#        def nothing():
#            pass
#        nothing = self.createAction("", nothing,
#                  tip = "")
#                
#        self.addActions( self.macroMenu, (macroAction,nothing))
                
        

                
        # ********************************************************
        #              Toolbars
        # ********************************************************
                
        # File functions
        # ---------------
#        topToolbar = self.addToolBar("top")
#        topToolbar.setObjectName("topToolBar")
#        self.addActions(topToolbar, (fileNewAction, fileOpenAction,
#                                      fileSaveAsAction))
#                                      
# TODO : restore this later
#                                      tabAddNewAction,tabDeleteAction,
#                                      plotAddNewAction,
#                                      testChannelAction,dumpChannelsAction))   

# TODO : restore this later                
#        # Add panels combo box
#        if self.panel_classes:
#            self.panelCombobox = QComboBox()
#            
#            
#            items = list(self.panel_classes.keys())
#            items.sort()
#            items.insert(0,"Add Panel")
#            
#            maxLength = max([len(x) for x in items])
#            self.panelCombobox.setMinimumContentsLength(maxLength+1)
#            
#            self.panelCombobox.addItems(items)
#            
#            topToolbar.addWidget(self.panelCombobox)
#            
#            # Connect panel selections to addPanel2tab
#            # note : have to specify the type of return
#            self.connect(self.panelCombobox,SIGNAL("activated (const QString&)"),self.addPanel2tab)
        
    

    def setup_menus(self):
        """
        Setup starting menus
        
        """

        # Get all the menus from the API      
        menuBar = self.menuBar()  
        self.API.menu_manager.makeMenus(menuBar)
        
        # Make link to file menu
        # This is needed to dynamically update it with recent files
        self.API.fileMenu = self.API.menu_manager.getMenu(API.FILE_MENU_NAME)
        self.connect(self.API.fileMenu,SIGNAL('aboutToShow()'),self.API.updateFileMenu)
        
        # Make link to help menu
        # This is needed to dynamically update it with recent files
        self.API.helpMenu = self.API.menu_manager.getMenu(API.HELP_MENU_NAME)
        self.connect(self.API.helpMenu,SIGNAL('aboutToShow()'),self.API.updateHelpMenu)
        
        # Show menu bar
        # Need to do this otherwise nothing happens
        #self.menuBar().show()
        
    
    def setup_toolbars(self):
        """
        Setup toolbars
        
        """
        self.API.toolbar_manager.makeToolbars(self)
    
    
    def setup_server(self):
        """
        Start the server that receives data from sources on the network
        
        """

        # ********************************************************
        #               Server
        # ********************************************************
        # Setup server
        #self.tcpServer = nw.TcpServer()
        
        # Create threaded server for processing incoming data in the
        # background. Give it a thread locking variable for writing
        # to channel dictionary
        self.tcpServer = nw.ThreadedTcpServer(channel_lock=self.API.dataStore.channel_lock)
                                              
        
        
        # Check server is working and set it to listen
        # from Mark Summerfield book
        if not self.tcpServer.listen(QHostAddress("0.0.0.0"), nw.SOCKET_PORT):
            QMessageBox.critical(self, "ScopePy Server",
            "Failed to start server: %s" % self.tcpServer.errorString())
            
            self.close()
            return

        logger.debug("Server started")
        
        # Connect server's upload data signal to function in main GUI
        self.connect(self.tcpServer, SIGNAL("UpLoadChannelData"), self.API.addChannelData)
        
        # Connect channel update to tree mode update
        #self.connect(self, SIGNAL("UpdateChannelTree"),self.updateChannelTreeModel)
        
        # connect server's CommandPacket upload to API
        self.connect(self.tcpServer, SIGNAL("UpLoadCommandPacket"), self.API.getCmdFromServer)

    #======================================================================
    #%% +++++ File menu functions ++++++
    #======================================================================
    
    
    def fileNew(self):
        print("Not implemented yet")
        
    def fileOpen(self):
        """
        Generic opening function. Passes filenames to other functions for
        parsing
        """
        
        if not os.path.exists(self.filePath):
            path = os.path.expanduser("~")
        else:
            path = self.filePath
            
        #formatString = "Data files (%s)" % " ".join(self.fileFormats)
        formatString = "Channel data files (*.spc);; CSV files (*.csv)"
            
        pathAndFilename = QFileDialog.getOpenFileName(self,"Open data file",
                                               path,formatString)
                                               

        
        if not pathAndFilename:
            return
            
        # Store path for next time    
        path, filename = os.path.split(pathAndFilename)
        self.filePath = path
            
        # Get type for file from extension and select the loading method
        dummy,ext = os.path.splitext(filename)
        ext = ext.lower()
        
        if ext == '.csv':
            self.loadCSV(pathAndFilename)
        elif ext == '.spc':
            self.loadChannels_from_spc(pathAndFilename)
        
        
                                               
        
        
        
    def fileSave(self):
        """
        Save selected channels to disk. Pops up a file selector box.
        
        
        """
        
        # Find out if any channels have been selected
        selected = self.getSelectedChannels()
        
        if not selected:
            self.statusBar().showMessage("No channels selected - cannot save", 5000)
            return
        
        if not os.path.exists(self.filePath):
            path = os.path.expanduser("~")
        else:
            path = self.filePath
            
        #formatString = "Channel data files (%s)" % " ".join(CHANNEL_SAVE_FILE_FORMATS)
            
        formatString = "Channel data files (*.spc);; CSV files (*.csv)"
        pathAndFilename = QFileDialog.getSaveFileName(self,"Save channel to file",
                                               path,formatString)
                                               

        
        if not pathAndFilename:
            return
            
        name,ext = os.path.splitext(pathAndFilename)
        
        print(pathAndFilename)
        print("Extension = ",ext)
        
        if ext.lower() == '.spc':
            self.saveChannels_to_spc(pathAndFilename,selected)
        
        
        
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
            self.channelTreeModel.addChannel(name,False)
        
        
        self.channel_lock.unlock()
            
        # Update channel selector tree 
        self.updateChannelSelector()
        
        
        
    def filePreferences(self):
        
        form = prefs.PreferencesDialog(prefs=self.preferences)
        
        if form.exec_():
            self.preferences.save()
            
        
        
#==============================================================================
#%% Main function
#==============================================================================
    
   

def main():
    
    
    app = QApplication(sys.argv)
    
    app.setOrganizationName("Triangle Dot")
    app.setOrganizationDomain("TriangeDot.com")
    app.setApplicationName("ScopePy")
    
    
    rect = QApplication.desktop().availableGeometry()
    
    form = MainWindow()
    
    form.resize(int(rect.width() * 0.9), int(rect.height() * 0.8))
    form.show()
    
    app.exec_()

if __name__ == '__main__':
    main()
