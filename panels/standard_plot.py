# -*- coding: utf-8 -*-
"""
Created on Sat Sep 12 07:34:41 2015

@author: john


Standard 2D Plot panel
==============================
A built-in panel for ScopePy. Main plotting window for 2D plots.


Version
==============================================================================
$Revision:: 20                            $
$Date:: 2015-04-11 08:50:53 -0400 (Sat, 1#$
$Author:: john                            $
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
import imp
import logging

# Third party libraries
import numpy as np

from PyQt4.QtCore import *
from PyQt4.QtGui import *

# My libraries
import ScopePy_panels as panel
import ScopePy_channel as ch
import ScopePy_graphs as graphs
import ScopePy_utilities as util
import simpleQt as sqt
import csslib

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




#==============================================================================
#%% Class definitions
#==============================================================================

class StandardPlotPanel(panel.PanelBase):
    """
    Standard Plot panel
    
    No __init__() required as it must be the same as the base class
    Must reimplement the drawPanel() method
    
    """
    
    #======================================================================
    #%% +++++ Standard panel functions
    #======================================================================
    
    
    def initialise(self):
        
        # Link to plot data
        self.channel_dict = self.API.dataStore.channel_dict
        
        # Load plot themes
        self.API.load_plot_themes()
        
        
        # Last selected plot
        self.selectedPlot = None
    
    
    def drawPanel(self):
        """
        Set the layout for the PlotScreen
        
        Plot + chunk selector
        
        """
        
        # Set this panel to be save-able in a session file
        # ======================================================
        # must implement the saveData() and restoreData() functions
        self.isSaveable = True
        
        # Widgets
        # ====================
        topBox = sqt.frame(self)
        topBoxSizePolicy = QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed)
        topBoxSizePolicy.horizontalStretch = 1
        topBoxSizePolicy.verticalStretch = 1
        topBox.setSizePolicy(topBoxSizePolicy)
        
        self.addChannelList = sqt.combobox(topBox)
        addChannelLabel = QLabel("Add Cha&nnel")
        addChannelLabel.setBuddy(self.addChannelList.widget)
        self.addChannelButton = QPushButton("Add [A]")
        self.addChannelButton.setShortcut(QKeySequence('A'))
        
        
        self.deleteChannelList = sqt.combobox(topBox)
        deleteChannelLabel = QLabel("Dele&te Channel")
        deleteChannelLabel.setBuddy(self.deleteChannelList.widget)
        self.deleteChannelButton = QPushButton("Delete [D]")
        self.deleteChannelButton.setShortcut(QKeySequence('D'))
        
        self.plot = graphs.GraphWidget(self.preferences)
        plotSizePolicy = QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
        plotSizePolicy.horizontalStretch = 3
        plotSizePolicy.verticalStretch = 3
        self.plot.setSizePolicy(plotSizePolicy)
        self.plot.setStyleSheet(self.API.getDefaultPlotThemeCss())
        
        self.chunkToolbar = self.chunkSelector()
        
        self.plot_theme = sqt.combobox(topBox)
        plot_themes = [self.API.plot_themes[key]['name'] for key in self.API.plot_themes.keys()]
        plot_themes.sort()
        self.plot_theme.addItems(plot_themes)    
        self.plot_theme.bindChanged(self.localThemeChanged)
        themeLabel = QLabel('Set Theme')
        
        # Set default theme
        default_theme = self.API.getDefaultPlotThemeName()
        self.plot_theme.currentText = default_theme
        #themeLabel.setBuddy(self.plot_theme)        
        
        # Layout
        # =================
        
        topBox.position([
            [addChannelLabel,self.addChannelList,self.addChannelButton,themeLabel],
            [deleteChannelLabel,self.deleteChannelList,self.deleteChannelButton,self.plot_theme]
            ])
            
        
        cc = {'addChannel':self.addChannel,
              'autoscale':self.autowrapper,
              'channelsOnPlot':self.channelsOnPlot,
              'dumpChannelData':self.dumpChannelData,
              'setTheme':self.setTheme,
              'addHorizMarker':lambda a: self.addHorizMarker(),
              'addVertMarker':lambda a: self.addVertMarker(),
              'updatePlot':lambda a :self.updatePlots()
                }
              
        self.console = sqt.MiniConsole(commands=cc)
        layout = QVBoxLayout()
        layout.addWidget(topBox)
        layout.addWidget(self.plot)
        layout.addWidget(self.chunkToolbar)
        layout.addWidget(self.console)
        
        
        self.setLayout(layout)
        
        # Connections
        # =====================
        self.connect(self.addChannelButton,SIGNAL("clicked()"),self.addChannelFromButton)
        self.connect(self.deleteChannelButton,SIGNAL("clicked()"),self.deleteChannelFromButton)
        
        # Comms connections
        # ======================
        self.addCommsAction('addChannel',self.addChannel)
        self.addCommsAction('deleteChannel',self.deleteChannel)
        
        
        # Initialisation
        # =========================
        self.updateChannelList()
        
        

    def autowrapper(self,t):
        '''
        Autoscale Wrapper for Miniconsole
        t: type of autoscale (all,x,y)
        '''
        t = t.lower()
        t = t.strip()
        if t == 'all':
            self.autoscaleXY()
        elif t == 'x':
            self.autoscaleX()

        elif t == 'y':
            self.autoscaleY()

        elif t == '-help':
            return 'autoscale(all, x or y)'
        else:
            raise Exception('No known type %s use --help to see all types' % t)


    def setFkeys(self):
        """
        Set function keys for plotting
        
        """
        
        self.Fkeys = [
                     ['F4','Horiz Marker',self.addHorizMarker],
                     ['F5','Vert Marker',self.addVertMarker],
                     ['F6','Select Plot',self.selectPlot],
                     ['F8','Autoscale XY',self.autoscaleXY],
                     ['F9','Autoscale X',self.autoscaleX],
                     ['F10','Autoscale Y',self.autoscaleY],
                     ]
        
        
    
    def setTheme(self,theme_name):
        styleSheet = self.API.getPlotThemeByName(theme_name)
        
        if styleSheet is not None:
            # Convert styles data into a CSS string and send to the plot widget
            d = {}
            d["standard_plot"] = styleSheet
            
            self.plot.setStyleSheet(csslib.dictToCss(d))
            self.plot_theme.currentText = theme_name
            self.plot.update()


    def localThemeChanged(self):
        """
        Change plot theme locally
        
        """
        
        theme_name = self.plot_theme.currentText
        
        # Get the styles data
        styleSheet = self.API.getPlotThemeByName(theme_name)
        
        if styleSheet is not None:
            # Convert styles data into a CSS string and send to the plot widget
            d = {}
            d["standard_plot"] = styleSheet
            
            self.plot.setStyleSheet(csslib.dictToCss(d))
            self.plot.update()
        
    
    #======================================================================
    #%% +++++ Plot functions
    #======================================================================
        
        
    def updateChannelList(self):
        """
        Update channel add and delete combo boxes
        
        """
        
        # Add channel combo
        # ====================
        if self.addChannelList.count>0:
            self.addChannelList.clear()
        
        channel_names = list(self.API.dataStore.channel_dict.keys())
        channel_names.sort()
        
        self.addChannelList.addItems(channel_names)
        
        
        # delete channel combo
        # =========================
        if self.deleteChannelList.count>0:
            self.deleteChannelList.clear()
            
        # Get channels from the graph widget
        if len(self.plot.channelSeries)>0:
            self.deleteChannelList.addItems(self.channelsOnPlot)
        
    @property   
    def channelsOnPlot(self):
        """
        Return list of channels that are currently plotted
        
        Output
        ---------
        channel_name_list: list of str
            list of channel names being plotted
            
        """
        
        current_channels = list(self.plot.channelSeries.keys())
        current_channels.sort()
        
        return current_channels
        
        
        
    def addChannelFromButton(self):
        """
        Add channel from a button click on the panel
        
        """
        
        # Get selected channel from combo
        channel_name = self.addChannelList.currentText
        
        if channel_name:
            self.addChannel(channel_name)
            self.updateChannelList()
            
        
    def deleteChannelFromButton(self):
        """
        Delete channel from a button click on panel
        """
        
        # Get selected channel from combo
        channel_name = self.deleteChannelList.currentText
        
        if channel_name:
            self.deleteChannel(channel_name)
            self.updateChannelList()
            
            
        
        
    def addChannel(self,channel):
        """ 
        Add channel data as new plotItem or update existing plot item
        Create meta-data for the plot
        
        Inputs
        --------
        channel : string 
            channel name
        
        """
        
        
        # Check for valid channel
        # =================================
        if channel not in self.channel_dict:
            return
            
        # Add meta-data structure
        # ==================================
        if channel not in self.plot.channelSeries:
            
            # If this is the first series to be plotted, automatically label
            # the axes with the x and y from this channel
            if len(self.plot.channelSeries)==0:
                self.plot.xlabel = self.API.channel_dict[channel].x_axis
                self.plot.ylabel = self.API.channel_dict[channel].y_axis
                
            
            # Add channel to plot
            self.plot.addChannel(self.API.channel_dict[channel])
            
            # Create link between channel and plot
            # using signal from channel
            self.connect(self.API.channel_dict[channel],SIGNAL("updateChannelPlot"),self.plot.updateChannel)
        
        
        # Make this the selected plot
        self.selectedPlot = channel
        
        # Update chunk selector for new channel
        self.updateChunkSelector()
        
        # Update lists
        self.updateChannelList()
        
     
        
    def deleteChannel(self,channel_name):
        """
        Remove a channel from the plot
        
        Inputs
        ------
        channel_name :str
        
        """
        
        if channel_name in self.plot.channelSeries:
            logger.debug("PlotScreen: Delete channel %s" % channel_name)
            self.plot.deleteChannel(channel_name)
        
        
    def setChunkMode(self,channel,chunkMode):
        """Set the chunk mode for a specified channel
        """
        
        # TODO: check chunk mode is valid
        
        # Change chunk mode if channel is valid
        if channel in self.plot.channelSeries:
            self.plot.channelSeries[channel].setChunkMode(chunkMode)
            
     
       
    def getChunkMode(self,channel):
        
        if channel in self.plot.channelSeries:
            return self.plot.channelSeries[channel].chunkMode
            
        
        
    def setChunkRange(self,channel,chunkRange):
        """
        Set the chunk range for a specified channel
        
        Input
        -------
        channel : str
            channel name
            
        chunkRange : list of int
            chunk indices selected
            
        """
        
        # TODO: check chunk mode is valid
        
        # Change chunk mode if channel is valid
        if channel in self.plot.channelSeries:
            self.plot.channelSeries[channel].setChunkSelection(chunkRange)
            
            
    
    def getChunkRange(self,channel):
        
        if channel in self.plot.channelSeries:
            return self.plot.channelSeries[channel].chunkSelection
            
            
        
        
        
    def updatePlots(self):
        """ 
        Update data in all plots according to chunk mode
        
        """
        
        
        # Update plots
        # =======================
        self.plot.update()
        
        
    def dumpChannelData(self,channel):
        """
        Debugging function
        
        Inputs
        ------
        channel : str
             name of channel
             
         Outputs
         --------
         data : numpy recarray
             data from channel
             
        """
        if channel in self.plot.channelSeries:
            return self.plot.channelSeries[channel].data()
        
        
    #======================================================================
    #%% +++++ Session saving functions
    #======================================================================
    
    def saveData(self):
        """
        Return data needed for current panel state
        
        Output
        ---------
        panel_data : dict
        
        """
        
        # Make a standard panel_data dictionary so it can be added to
        panel_data = self.standardSaveData
        
        # Add the channels currently being plotted
        panel_data['channel list'] = self.channelsOnPlot
        
        # Add current theme
        panel_data['theme'] = self.plot_theme.currentText
        
        # X and Y axis titles
        panel_data['x axis title'] =  self.plot.xlabel
        panel_data['y axis title'] =  self.plot.ylabel
        
        
        # Return customised dictionary
        return panel_data
        
        
        
    def restoreData(self,panel_data):
        """
        Restore plot from a previous state
        
        """
        
        # Restore the theme
        theme_name = panel_data.get('theme','Deep plot')
        self.setTheme(theme_name)
        
        # Restore channels
        if 'channel list' in panel_data:
            for channel_name in panel_data['channel list']:
                self.addChannel(channel_name)
                
        # Restore x and y axis titles
        self.plot.xlabel = panel_data['x axis title']
        self.plot.ylabel = panel_data['y axis title']
        
        self.plot.update()
        
    
        
    #======================================================================
    #%% +++++ Fkey functions
    #======================================================================
    def addHorizMarker(self):
        
        self.plot.addHorizMarker()
        
    
    def addVertMarker(self):
        
        self.plot.addVertMarker()
        
        
    def autoscaleXY(self):
        self.plot.autoscale()
        
        
    def autoscaleX(self):
        self.plot.autoscaleX()
    
    
    def autoscaleY(self):
        self.plot.autoscaleY()
        
    def selectPlot(self):
        self.plot.focusOnPlot()
        
    #======================================================================
    #%% +++++ Chunk selector functions
    #======================================================================
    
    
    def chunkSelector(self):
        """ 
        Chunk selector panel 
        
        Draws the GUI elements
        
        """
        
        
        
        # Chunk selector actions
        # ==============================
        self.chunkChannelSelectorBox = QComboBox()
        self.chunkChannelSelectorBox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.chunkChannelSelectorBox.setStatusTip("Select channel from current plot to adjust which chunks to plot")
        # TODO : replace this with the current plot's channels        
        self.addChannel2chunkSelector(list(self.channel_dict.keys()))
        
        chunkPlayButton = QToolButton() 
        playIcon = self.style().standardIcon(QStyle.SP_MediaPlay)
        chunkPlayButton.setIcon(playIcon)    
        chunkPlayButton.setToolTip("Not implemented")

        
        chunkFastFwdButton = QToolButton() 
        ffIcon = self.style().standardIcon(QStyle.SP_MediaSeekForward)
        chunkFastFwdButton.setIcon(ffIcon)  
        chunkFastFwdButton.setToolTip("Forward one chunk")
        
        chunkRewindButton = QToolButton() 
        rewindIcon = self.style().standardIcon(QStyle.SP_MediaSeekBackward)
        chunkRewindButton.setIcon(rewindIcon) 
        chunkRewindButton.setToolTip("Back one chunk")
        
        chunkFirstButton = QToolButton() 
        firstIcon = self.style().standardIcon(QStyle.SP_MediaSkipBackward)
        chunkFirstButton.setIcon(firstIcon) 
        chunkFirstButton.setToolTip("Select first chunk")
        
        chunkLastButton = QToolButton() 
        lastIcon = self.style().standardIcon(QStyle.SP_MediaSkipForward)
        chunkLastButton.setIcon(lastIcon) 
        chunkLastButton.setToolTip("Select last chunk")
        
        chunkAllButton = QToolButton() 
        allIcon = self.style().standardIcon(QStyle.SP_ArrowUp)
        chunkAllButton.setIcon(allIcon) 
        chunkAllButton.setToolTip("Select all chunks")
        
        self.chunkRangeText = QLineEdit()
        # Only allow numbers, commas and dashes
        regex = QRegExp(r"[0-9,-]*")
        self.chunkRangeText.setValidator(QRegExpValidator(regex))
        self.chunkRangeText.setStatusTip("Enter chunk range, e.g. 1-4 or 1,3,5,100")
        self.chunkRangeText.setToolTip("Enter range of chunks to display")
        self.chunkRangeText.setMaximumWidth(80)
        
        
#             QStyle.SP_MediaPlay   
#        QStyle.SP_MediaSeekForward
#        chunkFastFwdAction = self.createAction("Next Chunk", self.chunkNext,
#                icon = QStyle.SP_MediaSeekForward, tip="Display next chunk")
                
                
        # Chunk selector buttons and widgets
        # ===================================
                
        
        # Chunk selector layout
        # ==============================
        chunkToolbar = QFrame() #self.addToolBar("chunkSelector")
        chunkToolbar.setFrameStyle(QFrame.Panel | QFrame.Raised)
        chunkToolbar.setLineWidth(3)
        chunkToolbar.setMaximumHeight(chunkLastButton.sizeHint().height()*2)
        
        chunkToolbarLayout = QHBoxLayout()
        chunkToolbarLayout.addWidget(QLabel("Chunk Selection"))
        chunkToolbarLayout.addWidget(self.chunkChannelSelectorBox)
        chunkToolbarLayout.addWidget(chunkFirstButton)
        chunkToolbarLayout.addWidget(chunkRewindButton)
        chunkToolbarLayout.addWidget(chunkPlayButton)
        chunkToolbarLayout.addWidget(chunkFastFwdButton)
        chunkToolbarLayout.addWidget(chunkLastButton)
        chunkToolbarLayout.addWidget(chunkAllButton)
        
        chunkToolbarLayout.addWidget(QLabel("Range"))
        chunkToolbarLayout.addWidget(self.chunkRangeText)
        
        chunkToolbar.setLayout(chunkToolbarLayout)
        
        #self.addActions(chunkToolbar,(chunkPlayAction,chunkFastFwdAction))
        # TODO : this is not showing up, revert to Toolbar and icons don't show either
        self.connect(chunkPlayButton, SIGNAL("clicked()"),self.chunkPlay)
        self.connect(chunkFastFwdButton, SIGNAL("clicked()"),self.chunkNext)
        
        self.connect(chunkRewindButton, SIGNAL("clicked()"),self.chunkPrevious)
        self.connect(chunkLastButton, SIGNAL("clicked()"),self.chunkLast)
        self.connect(chunkFirstButton, SIGNAL("clicked()"),self.chunkFirst)
        self.connect(chunkAllButton, SIGNAL("clicked()"),self.chunkAll)
        self.connect(self.chunkRangeText,SIGNAL("editingFinished()"),self.chunkSelection)
       
        
        return chunkToolbar
        
        
    def addChannel2chunkSelector(self,channelList):
        """ Add a list of channels to the chunk selector
        
        TODO : Temporary, needs doing properly
        """
        
        # TODO : Check what's already in the list
        self.chunkChannelSelectorBox.addItems(channelList) 
        self.chunkChannelSelectorBox.adjustSize()
        
        
        
    def chunkPlay(self):
        logger.debug("chunkPlay: Not implemented yet")
        
        
        
    def chunkNext(self):
        """
        Move to next chunk
        
        """
        

        # Get channel
        channel = self.chunkChannelSelectorBox.currentText()
        
        # Get the current range of chunks plotted
        currentChunkRange = self.plot.channelSeries[channel].chunkSelection
        
        # This function only works when one chunk is selected
        if len(currentChunkRange) > 1:
            return
            
        # Check the current chunk is not the last
        if currentChunkRange[0] == self.channel_dict[channel].chunks-1:
            return
            
        # Finally if all conditions are satisfied then increment the chunk
        # index
        self.setChunkRange(channel,[currentChunkRange[0]+1])
        self.setChunkMode(channel,ch.CHUNK_MODE_SELECTION)
        
        
        logger.debug("chunkNext: chunk = %d" % self.plot.channelSeries[channel].chunkSelection[0] )
            
        
        # update plot
        self.updatePlots()
        self.updateChunkSelector()
        
        
        
    def chunkPrevious(self):
        """
        Move to previous chunk
        
        """
        

        # Get channel
        channel = self.chunkChannelSelectorBox.currentText()
        
        # Get the current range of chunks plotted
        currentChunkRange = self.plot.channelSeries[channel].chunkSelection
        
        # This function only works when one chunk is selected
        if len(currentChunkRange) > 1:
            return
            
        # Check the current chunk is not the first
        if currentChunkRange[0] <= 0:
            return
            
        # Finally if all conditions are satisfied then decrement the chunk
        # index
        self.setChunkRange(channel,[currentChunkRange[0]-1])
        self.setChunkMode(channel,ch.CHUNK_MODE_SELECTION)
        
        
        logger.debug("chunkPrevious: chunk = %d" % self.plot.channelSeries[channel].chunkSelection[0] )
            
        
        # update plot
        self.updatePlots()
        self.updateChunkSelector()
        
        
    def chunkLast(self):
        """ 
        Move to last chunk
        
        """
        
        
        # Get channel
        channel = self.chunkChannelSelectorBox.currentText()
        
        # Set to last chunk
        self.setChunkRange(channel,[self.channel_dict[channel].chunks-1])
        self.setChunkMode(channel,ch.CHUNK_MODE_SELECTION)
        
        # update plot
        self.updatePlots()
        self.updateChunkSelector()
        
        
        
    def chunkFirst(self):
        """ 
        Move to first chunk
        
        """
        

        # Get channel
        channel = self.chunkChannelSelectorBox.currentText()
        
        # Set to first chunk
        self.setChunkRange(channel,[0])
        self.setChunkMode(channel,ch.CHUNK_MODE_SELECTION)
        
        # update plot
        self.updatePlots()
        self.updateChunkSelector()
        
        
        
    def chunkSelection(self):
        """
        Get the chunk range from the Range text entry box
        Convert into a list and set the chunk range for this channel
        on the current plot
        
        """
        

        # Get channel
        channel = self.chunkChannelSelectorBox.currentText()
        
        txt = self.chunkRangeText.text()
        logger.debug("chunkSelection: Range = %s" % txt)
        
        if txt=='':
            return
        
        # Parse range string into list
        # remove any values that are out of range
        newList = util.filterList(util.str2RangeList(txt),0,self.channel_dict[channel].chunks-1)
        
        if newList:
            # Update chunk list        
            self.setChunkRange(channel,newList)
            
            # update plot
            self.updatePlots()
            self.updateChunkSelector()
            
    
    def chunkAll(self):
        """
        Select all chunks
        
        """
        

        # Get channel
        channel = self.chunkChannelSelectorBox.currentText()
        
        # Set chunk mode
        self.setChunkMode(channel,ch.CHUNK_MODE_ALL)
        
        
        # update plot
        self.updatePlots()
        self.updateChunkSelector()
        
        
        
    
    def updateChunkSelector(self):
        """ Update the chunk selector with the current plot
        
        """
        
        
        
        channelList = list(self.plot.channelSeries.keys())
        
        if not channelList:
            # clear list and
            # Exit if no channels
            self.chunkChannelSelectorBox.clear()
            return
            
        channelList.sort()
        
        self.chunkChannelSelectorBox.clear()
        self.chunkChannelSelectorBox.insertItems(0,channelList)
        
        # Set currently selected channel
        if self.selectedPlot == None:
            self.chunkChannelSelectorBox.setCurrentIndex(0)
            self.selectedPlot = channelList[0]
        else:
            index = channelList.index(self.selectedPlot)
            self.chunkChannelSelectorBox.setCurrentIndex(index)
            
        # Update the range line edit
        
        # Get number of chunks for selected channel
        chunkRange = self.getChunkRange(self.selectedPlot)
        
        # Update text in line edit
        self.chunkRangeText.setText(util.rangeList2str(chunkRange))
        
        

#==============================================================================
#%% Help docs
#==============================================================================

help_doc = """

%*% Standard 2D Plot

++<
This is the standard 2D plotting panel in ScopePy
>++

%*% Usage

++<
--<
--+ Make a channel
--+ Add channel to plot
>--
>++

"""




#==============================================================================
#%% Panels to export
#==============================================================================
# Put any panels to be imported from this file here
# Note: this must go after the class definitions
#
# Panels are passed in a dictionary where:
#   key = the name to be used on menus
#   value = PanelFlags class from ScopePy_panels.py

__panels__ = {"Plot":panel.PanelFlags(StandardPlotPanel,
                                                  open_on_startup=False,
                                                  location='main_area',
                                                  docs=help_doc)}
