# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 06:46:31 2015

@author: john

Channel selector Panel
==============================
A built-in panel for ScopePy. Central widget for adding channels to plots
and generally viewing the channels in memory


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

from qt_imports import *

# My libraries
import ScopePy_panels as panel
import ScopePy_channel as ch
import ScopePy_widgets as wid
import simpleQt as sqt

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
con.setLevel(logging.ERROR)

# create formatter
formatter = logging.Formatter('[%(asctime)s:%(name)s:%(levelname)s]: %(message)s')

# add formatter to ch
con.setFormatter(formatter)

# add ch to logger
logger.addHandler(con)


#==============================================================================
#%% Constants
#==============================================================================

# Channel selector pages
CHANNEL_LIST_PAGE = 0
GROUP_LIST_PAGE = 1
CHANNEL_EDIT_PAGE = 2



#==============================================================================
#%% Class definitions
#==============================================================================

class ChannelSelectorPanel(panel.PanelBase):
    """
    Channel Selector panel
    -------------------------

    This panel displays the channels that are currently in memory and their
    plot style.

    It appears in the sidebar, usually as the current tab



    """

    # No __init__() required as it must be the same as the base class
    # Must reimplement the drawPanel() method

    def drawPanel(self):
        """
        Draw the GUI elements of the panel

        This is a Mandatory function. It will be called by ScopePy when
        the panel is added to a tab.

        """

        # ********************************************************
        #               Channel selector Layout
        # ********************************************************
        # TODO channel editor might need to be another panel

        # Channel operations buttons
        #=================================
        channelSelectorWidget = QWidget()
        channelSelectorWidget.setMaximumSize(QSize(275,455))
        channelSelectorWidget.setMinimumSize(QSize(240,300))
        channelSelectorWidget.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)


        addChannelButton = QPushButton("Add &Channel to plot  -->")

        removeChannelButton = QPushButton("Remo&ve Channel from plot  <--")
        newChannelButton = QPushButton("New Channel")
        editChannelButton = QPushButton("Edit Channel")
        deleteChannelButton = QPushButton("Delete Channel")
        addMathChannelButton = QPushButton("Add &Math Channel ...")
        dumpChannelButton = QPushButton("Dump Channel")

        selectAllChannelsButton = QPushButton("Select &All")
        unSelectAllChannelsButton = QPushButton("&Unselect All")

        # Connections
        # TODO : check over. Some of these may need to be implemented here
        self.connect(addChannelButton, SIGNAL("clicked()"),self.API.addChannel2Panel)
        self.connect(addMathChannelButton, SIGNAL("clicked()"),self.addMathChannel)
        self.connect(removeChannelButton, SIGNAL("clicked()"),self.API.removeChannelFromPlot)
        self.connect(newChannelButton, SIGNAL("clicked()"),self.createNewChannel)
        self.connect(editChannelButton, SIGNAL("clicked()"),self.editChannel) # ???
        self.connect(deleteChannelButton, SIGNAL("clicked()"),self.deleteChannel)
        self.connect(selectAllChannelsButton, SIGNAL("clicked()"),self.selectAllChannels)
        self.connect(unSelectAllChannelsButton, SIGNAL("clicked()"),self.unSelectAllChannels)
        self.connect(dumpChannelButton, SIGNAL("clicked()"),self.dumpChannel)

        # Options for displaying channels
        # -------------------------------------



        # Tree model setup
        self.channelTreeModel = ch.ChannelTreeModel(self.API.dataStore.channel_dict)

        # Tree - more info
        self.channelTree = QTreeView() #QTreeWidget()
        self.channelTree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.channelTree.setSelectionBehavior(QTreeView.SelectItems)
        self.channelTree.setItemsExpandable(True)
        self.channelTree.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding))
        self.channelTree.header().setStretchLastSection(False)
        self.channelTree.header().setResizeMode(QHeaderView.Stretch)

        # Model version setup
        self.channelTree.setModel(self.channelTreeModel)
        self.channelTreeDelegate = ch.channelTreeDelegate(self)
        self.channelTree.setItemDelegate(self.channelTreeDelegate)





        # labels
        # ====================
        channelSelectorTitle = QLabel("<h2><b>Channel Selector</b></h2>")
        #channelSelectorTitle.setBuddy(addChannelButton)
        channelListTitle = QLabel("Channel &List")
        #channelListTitle.setBuddy(self.channelList)
        channelListTitle.setBuddy(self.channelTree)

        # Layout
        # ============

        # Button frame
        buttonFrame = sqt.frame(self)

        buttonFrame.position([
            [newChannelButton,addChannelButton],
            [editChannelButton,removeChannelButton],
            [deleteChannelButton,addMathChannelButton],
            [dumpChannelButton,sqt.empty()]])

#        channelSelectorLayout.addWidget(newChannelButton)
#        channelSelectorLayout.addWidget(editChannelButton)
#        channelSelectorLayout.addWidget(addChannelButton)
#        channelSelectorLayout.addWidget(removeChannelButton)
#        channelSelectorLayout.addWidget(deleteChannelButton)
#        channelSelectorLayout.addWidget(addMathChannelButton)
#        channelSelectorLayout.addWidget(dumpChannelButton)


        channelSelectorLayout = QVBoxLayout()
        channelSelectorLayout.addWidget(channelSelectorTitle)
        channelSelectorLayout.addWidget(buttonFrame)
        channelSelectorLayout.addWidget(channelListTitle)
        channelSelectorLayout.addWidget(self.channelTree)

        # Select/un select buttons
        channelSelectUnSelectLayout = QHBoxLayout()
        channelSelectUnSelectLayout.addWidget(selectAllChannelsButton)
        channelSelectUnSelectLayout.addWidget(unSelectAllChannelsButton)

        channelSelectorLayout.addLayout(channelSelectUnSelectLayout)

        #
        channelSelectorWidget.setLayout(channelSelectorLayout)

        # Channel editing layout
        # =============================
        channelEditWidget = QWidget()

        channelEditAddButton = QPushButton("Add Channel")
        channelEditCancelButton = QPushButton("Cancel")

        # Button connections
        self.connect(channelEditAddButton, SIGNAL("clicked()"),self.channelEditAdd)
        self.connect(channelEditCancelButton, SIGNAL("clicked()"),self.channelEditCancel)

        channelEditButtonLayout = QHBoxLayout()
        channelEditButtonLayout.addWidget(channelEditAddButton)
        channelEditButtonLayout.addWidget(channelEditCancelButton)


        # Channel name box
        channelEditLabel = QLabel("Channel Name")
        self.channelEditNameEntry = QLineEdit()

        # editing table
        self.channelEditTable = QTableWidget()
        self.channelEditTable.clear()
        self.channelEditTable.setSortingEnabled(False)
        self.channelEditTable.setRowCount(10)
        headers = ["x values", "y value"]
        self.channelEditTable.setColumnCount(len(headers))
        self.channelEditTable.setHorizontalHeaderLabels(headers)

        # Channel Edit layout
        channelEditLayout = QVBoxLayout()
        channelEditLayout.addWidget(channelEditLabel)
        channelEditLayout.addWidget(self.channelEditNameEntry)
        channelEditLayout.addWidget(self.channelEditTable)
        channelEditLayout.addLayout(channelEditButtonLayout)

        channelEditWidget.setLayout(channelEditLayout)

        # Channel crafter
        # ===========================================

        # Variables
        # --------------
        self.craftXdata = None
        self.craftYdata = None
        self.craftXname = None
        self.craftYname = None
        self.craftXsource = None
        self.craftYsource = None


        # Widgets
        # ------------
        self.channelName_txtEd = QLineEdit("New channel")
        channelNameLabel = QLabel("Chann&el name")
        channelNameLabel.setBuddy(self.channelName_txtEd)
        self.xdata_txtEd = QLineEdit("x data")
        self.ydata_txtEd = QLineEdit("y data")
        self.xdata_source = QLabel('x data source')
        self.ydata_source = QLabel('y data source')

        # Buttons
        # ----------
        switchXY_button = QPushButton("Switch X & Y")
        self.makeChannel_button = QPushButton("Ma&ke Channel")
        #self.makeChannel_button.setDisabled(True)

        # Connections
        self.connect(switchXY_button, SIGNAL("clicked()"),self.switchXY)
        self.connect(self.makeChannel_button, SIGNAL("clicked()"),self.makeChannel)


        # Channel crafter layout
        # ----------------------
        craftFrame = QFrame()
        craftFrame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        craftFrame.setLineWidth(3)

        craftLayout = QGridLayout()

        craftLayout.addWidget(QLabel("<h2><b>Channel Crafter</b></h2>"),0,1)

        craftLayout.addWidget(channelNameLabel,1,1)
        craftLayout.addWidget(self.channelName_txtEd,1,2)

        craftLayout.addWidget(QLabel("<b><em>source</em></b>"),2,1)
        craftLayout.addWidget(QLabel("<b><em>data</em></b>"),2,2)

        craftLayout.addWidget(QLabel("<b><em>x axis</em></b>"),3,0)
        craftLayout.addWidget(self.xdata_source,3,1)
        craftLayout.addWidget(self.xdata_txtEd,3,2)

        craftLayout.addWidget(QLabel("<b><em>y axis</em></b>"),4,0)
        craftLayout.addWidget(self.ydata_source,4,1)
        craftLayout.addWidget(self.ydata_txtEd,4,2)


        craftLayout.addWidget(switchXY_button,5,1)
        craftLayout.addWidget(self.makeChannel_button,5,2)

        craftFrame.setLayout(craftLayout)
        channelSelectorLayout.addWidget(craftFrame)


        # Add layout to master widget [Mandatory]
        # ========================================
        # mandatory
        self.setLayout(channelSelectorLayout)


        # Add toolbar button for test channels
        # =====================================
        testChannelsAction = self.API.createAction("T&est channels", self.makeTestChannel,
                icon=QIcon.fromTheme("system-run"), tip="Create test channels for debugging")

        self.API.toolbar_manager.addButton('top',[testChannelsAction])

        # Setup signals to external sources
        # ====================================
        self.connect(self.API, SIGNAL("channel_added"),self.updateChannelTreeModel)
        self.connect(self.API, SIGNAL("update_channel_selector"),self.updateChannelSelector)


        # Add SignalComms actions
        # ============================
        self.addCommsAction('addXdata',self.addXdata)
        self.addCommsAction('addYdata',self.addYdata)
        self.addCommsAction('deleteAllChannels',self.deleteAllChannels)


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

        self.Fkeys = [
                        ['F1','Help',self.showHelp],
                        ['F9','Make test channels',self.makeTestChannel]]


    # User defined functions go here
    # ==============================================

    def updateChannelTreeModel(self,channelName):


        # Add channel to tree [model version]
        self.channelTreeModel.addChannel(channelName,True)

        # Resize columns

        #logger.debug("Resizing channel selector")
        #self.channelTree.resizeColumnToContents(0)
        #self.channelTree.resizeColumnToContents(1)



    def updateChannelSelector(self):
        """
        General update of channel selector TreeView
        Forces resizing of the columns

        """

        # Resize columns

        logger.debug("Resizing channel selector")
        self.channelTree.resizeColumnToContents(0)
        self.channelTree.resizeColumnToContents(1)

        self.channelTree.reset()







    def createNewChannel(self):
        """
        Display channel editing page a new channel.

        """

        # Clear channel editing table
        self.channelEditTable.clear()
        self.channelEditTable.setSortingEnabled(False)
        self.channelEditTable.setRowCount(10)
        headers = ["x values", "y value"]
        self.channelEditTable.setColumnCount(len(headers))
        self.channelEditTable.setHorizontalHeaderLabels(headers)

        # Clear channel name
        self.channelEditNameEntry.setText("<Enter Channel name>")

        # Change to channel editing page
        self.channelStack.setCurrentIndex(CHANNEL_EDIT_PAGE)



    def editChannel(self):
        """
        Edit existing channel data.
        TODO : Still under construction
        """

        # Get selected channels
        selectedChannels = self.getSelectedChannels()

        # Return if nothing selected
        if not selectedChannels:
            return

        if len(selectedChannels) > 1:
            # TODO : Warn user that only one channel can be edited
            print("Multiple channels selected - choosing first one")

        # Extract channel name of first selected channel
        chan2Edit = selectedChannels[0]

        # Populate editing table
        self.channelData2EditTable(chan2Edit)


        # Change to channel editing page
        self.channelStack.setCurrentIndex(CHANNEL_EDIT_PAGE)

        print("Not implemented yet")


    def channelData2EditTable(self,chan2Edit):
        """ Populate the channel Edit table with data from the
        specified channel

        Input
        --------
        chan2Edit = channel label for the channel that is to be populated

        """

        # Get parameters for setting up the table
        rowCount = len(self.API.dataStore.channel_dict[chan2Edit].data_list)

        # Setup table to receive data
        # -----------------------------------

        # Setup rows
        self.channelEditTable.clear()
        self.channelEditTable.setSortingEnabled(False)
        self.channelEditTable.setRowCount(rowCount)

        # Setup columns
        headers = [self.API.dataStore.channel_dict[chan2Edit].x_axis, self.API.dataStore.channel_dict[chan2Edit].x_axis]
        self.channelEditTable.setColumnCount(len(headers))
        self.channelEditTable.setHorizontalHeaderLabels(headers)

        # Populate the data into the columns
        # -------------------------------------
        # TODO : Get data out of recArray, convert to strings
        # TODO : Handle chunks


        # Set channel name
        # -----------------
        self.channelEditNameEntry.setText(chan2Edit)


    def EditTable2channelData(self):
        """ Transfer data from channel Edit table to channel dictionary

        """

        # Validate data
        # ======================

        # Do both columns have the same number of rows

        # Is data numeric?

        # Read out data into recArray
        # ================================

        print("Not implemented yet")



    def deleteChannel(self,channel_names=None):
        """
        Delete  channel(s). This can be either the channel specified
        in the input argument or the currently selected channels.

        The channels are deleted from everywhere, the channel selector
        and any plots where they occur.

        Input
        ------
        channel_name : str or list of str
            Names of the channels to delete

        """

        # Handle no input
        # ----------------------
        # Take selected channels
        if channel_names is None:
            channel_names = self.getSelectedChannels()

        # Deal with string input
        # ------------------------
        if isinstance(channel_names,str):
            channel_names = [channel_names]


        # Check we have a list
        assert isinstance(channel_names,list),"GUI: deleteChannel input is not a list or a string"

        # Validate channel names
        valid_names = [name for name in channel_names if name in self.API.dataStore.channel_dict]

        if valid_names ==[]:
            logger.debug("GUI: deleteChannel - No valid names found")
            return


        # Delete channels
        # -----------------
        self.API.dataStore.channel_lock.lockForWrite()

        for name in valid_names:
            # Send out a signal to say the channel is being deleted
            self.emit(SIGNAL("DeleteChannel"), name)

            # Remove from channel from tree
            self.channelTreeModel.deleteChannel(name)

            # Remove channel from dictionary
            self.API.dataStore.channel_dict.pop(name)


        self.API.dataStore.channel_lock.unlock()


    def deleteAllChannels(self):
        """
        Clear the channel selector

        """

        channel_names = list(self.API.dataStore.channel_dict.keys())

        for name in channel_names:
            self.deleteChannel(name)





    def getSelectedChannels(self):
        """
        Return a list of the selected channels from the list box
        in the main screen

        Outputs:
        ---------
        selectedChannels : list of str
            list of selected channel names

        """

        # Get selected items
        # returns a list of QListWidgetItems
        #selection = self.channelTree.selectedItems()
        selection = self.channelTree.selectedIndexes()
        selectedChannels = self.channelTreeModel.getSelectedChannelsFromIndex(selection)

        return selectedChannels


    def selectAllChannels(self):
        """ Select all channels from channel tree
        """
        # QTreeView method
        self.channelTree.selectAll()



    def unSelectAllChannels(self):
        """ Unselect all channels from channel tree view
        """

        # QTreeView method
        self.channelTree.clearSelection()



    """
    ======================================================================
    Channel Edit functions
    ======================================================================
    """
    def channelEditAdd(self):
        """ Add a new or edited channel back into the channel dictionary

        """

        # TODO : Not implemented yet

        # Set back to channel selector page
        self.channelStack.setCurrentIndex(CHANNEL_LIST_PAGE)


    def channelEditCancel(self):
        """ Exit from channel editing page without storing data

        """


        # Set back to channel selector page
        self.channelStack.setCurrentIndex(CHANNEL_LIST_PAGE)


    def addMathChannel(self,channel_name="New Math channel",sourceChannels=None,math_function=None):
        """
        Add a new Math channel based on the supplied channel name or the
        selected channels.

        Inputs
        ---------
        channel_name : str
            name of new math channel

        sourceChannels : str or list of str
            name of channel(s) that provide the source data

        math_function : MathFunction
            Function to use

        """

        # If no inputs then use a dialog box to get them
        if any([sourceChannels is None,math_function is None]):

            selected_channels = self.getSelectedChannels()

            # Pop-up dialog box to select Math function
            channelList = list(self.API.dataStore.channel_dict.keys())
            channelList.sort()
            form = wid.MathDialog(selected_channels[0],self.API.math_functions,channelList)

            if form.exec_():
                channel_name = form.mathChannelName
                # TODO this is broken here, a list will be returned
                source_channels = [self.API.dataStore.channel_dict[ch] for ch in form.sourceChannels]
                math_function = form.mathFunction

            else:
                # Cancel pressed
                return
        else:
            source_channels = [self.API.dataStore.channel_dict[ch] for ch in sourceChannels]

        # Check source channels exist
        #source_channels = sourceChannels
        if any([ch.name not in self.API.dataStore.channel_dict for ch in source_channels]):
            # Abandon ship
            raise RuntimeError("addMathChannel:Channel Does Not Exist")


        # Make new MathChannel
        # -----------------------
        lineStyle = self.API.getChannelLinestyle(len(source_channels[0].data(ch.CHUNK_MODE_ALL)))

        new_channel = ch.MathChannel(source_channels,math_function,
                                     channelLabel=channel_name,
                                     lineStyle=lineStyle)

        # Store channel
        # ---------------------
        self.API.dataStore.channel_lock.lockForWrite()

        self.API.dataStore.channel_dict[channel_name] = new_channel


        # Make math channel
        #logger.debug("addMathChannel: New channel [%s] based on [%s] with function [%s]" % (channel_name,sourceChannel,math_function.name))

        # Add channel to tree [model version]
        self.channelTreeModel.addChannel(channel_name,False)


        self.API.dataStore.channel_lock.unlock()

        self.updateChannelSelector()


    def dumpChannel(self):
        """
        Print channel data to command line

        debugging tool
        """

        # Get selected channels
        selectedChannels = self.getSelectedChannels()

        # Return if nothing selected
        if not selectedChannels:
            return

        channel_name = selectedChannels[0]

        logger.debug("Printing channel: [%s]" % channel_name)
        ch_data = self.API.channel_dict[channel_name].data()

        print('Columns: [%s]' % ",".join(ch_data.dtype.names) )
        print('Number of rows = %i' % len(ch_data))
        print(ch_data)



    def makeTestChannel(self):
        """
        Generate a test channel for testing out the GUI.
        The data is a 1:1 straight line for checking where
        the graph points are being plotted.

        """

        # Make the data
        #--------------------------
        dtype = [("x data",float),("y data",float)]
        npoints = 21

        name = "Test channel"
        recarray = np.zeros(npoints,dtype)
        recarray["x data"] = np.arange(-10,11,1)
        recarray["y data"] = recarray["x data"]
        self.API.addChannelData((name,recarray))

        name = "1:1 neg slope"
        recarray["x data"] = -np.arange(-10,11,1)
        self.API.addChannelData((name,recarray))

        name = "Offset 1:1"
        recarray["x data"] = np.arange(-10,11,1)+100
        self.API.addChannelData((name,recarray))

        name = "Horiz line"
        recarray = np.zeros(50,dtype)
        recarray["x data"] = np.linspace(-10,11,50)
        recarray["y data"] = 5*np.ones(50)
        self.API.addChannelData((name,recarray))

        name = "Vert line"
        recarray = np.zeros(50,dtype)
        recarray["x data"] = 5*np.ones(50)
        recarray["y data"] = np.linspace(-10,11,50)
        self.API.addChannelData((name,recarray))

        name = "sine wave"
        recarray = np.zeros(200,dtype)
        recarray["x data"] = np.linspace(-10,11,200)
        recarray["y data"] = 5*np.sin(recarray["x data"])
        self.API.addChannelData((name,recarray))

        name = "sine wave offset"
        recarray = np.zeros(200,dtype)
        recarray["x data"] = np.linspace(-10,11,200)
        recarray["y data"] = 2*(np.sin(recarray["x data"])+3.01)
        self.API.addChannelData((name,recarray))

        name = "random noise"
        recarray = np.zeros(200,dtype)
        recarray["x data"] = np.linspace(-10,11,200)
        recarray["y data"] = 5*np.random.rand(200)
        self.API.addChannelData((name,recarray))

    # -----------------------------------------------------------------------
    # Channel crafter functions
    # -----------------------------------------------------------------------
    def addXdata(self,data,name,source=None):
        """
        Add x axis data to channel crafter

        Inputs
        -------
        data : numpy single column array or list
            data for new channel

        name : str
            Name of x axis column

        source : str
            name of data source
            TODO : could be a link


        """

        # Store the new data
        self.craftXdata = np.asarray(data)
        self.craftXname = name
        self.craftXsource = source

        # Update the display
        self.xdata_txtEd.setText(name)
        if self.craftXsource:
            self.xdata_source.setText(source)


        # Check if y data is present and the same size
        # If it is then enable the makeChannel button
        if self.craftYdata is not None:
            if len(self.craftYdata)==len(self.craftXdata):
                self.makeChannel_button.setEnabled(True)
            else:
                self.makeChannel_button.setDisabled(True)

        else:
            self.makeChannel_button.setDisabled(True)


    def addYdata(self,data,name,source=None):
        """
        Add y axis data to channel crafter

        Inputs
        -------
        data : numpy single column array or list
            data for new channel

        name : str
            Name of x axis column

        source : str
            name of data source
            TODO : could be a link


        """

        # Store the new data
        self.craftYdata = np.asarray(data)
        self.craftYname = name
        self.craftYsource = source

         # Update the display
        self.ydata_txtEd.setText(name)
        if self.craftYsource:
            self.ydata_source.setText(source)

        # Check if y data is present and the same size
        # If it is then enable the makeChannel button
        if self.craftXdata is not None:
            if len(self.craftYdata)==len(self.craftXdata):
                self.makeChannel_button.setEnabled(True)
            else:
                self.makeChannel_button.setDisabled(True)

        else:
            self.makeChannel_button.setDisabled(True)




    def makeChannel(self):
        """
        Make a new channel from the selections in the channel crafter

        """


        # Validate input data
        # =================================
        if self.craftXdata is None or self.craftYdata is None:
            self.API.statusBar().showMessage("Channel crafter: No data selected", 5000)
            return

        if len(self.craftXdata) != len(self.craftYdata):
            self.API.statusBar().showMessage("Channel crafter:X and Y data are different lengths", 5000)
            return

        if self.channelName_txtEd=="New channel":
            self.API.statusBar().showMessage("Channel crafter: Please name the channel", 5000)
            return

        # Make a channel
        # =======================

        # Make a numpy recarray
        # ---------------------------
        dtype = [(self.craftXname,float),(self.craftYname,float)]

        name = self.channelName_txtEd.text()
        recarray = np.zeros(len(self.craftXdata),dtype)
        recarray[self.craftXname] = self.craftXdata
        recarray[self.craftYname] = self.craftYdata

        # Make a new channel
        self.API.addChannelData((name,recarray))


        pass


    def switchXY(self):
        """
        Switch X and Y channels on the channel crafter

        """

        # Validate input data
        # =================================
        if self.craftXdata is None or self.craftYdata is None:
            self.API.statusBar().showMessage("Channel crafter: No data selected", 5000)
            return


        # Switch channels
        # ===============================

        # Store temporary data

        tmp_xdata = self.craftXdata
        tmp_xname = self.craftXname
        tmp_xsource = self.craftXsource

        tmp_ydata = self.craftYdata
        tmp_yname = self.craftYname
        tmp_ysource = self.craftYsource

        # Update
        self.addXdata(tmp_ydata,tmp_yname,tmp_ysource)
        self.addYdata(tmp_xdata,tmp_xname,tmp_xsource)





#==============================================================================
#%% Functions
#==============================================================================



#==============================================================================
#%% Panels to export
#==============================================================================
# Put any panels to be imported from this file here
# Note: this must go after the class definitions
#
# Panels are passed in a dictionary where:
#   key = the name to be used on menus
#   value = class reference

__panels__ = {"Cha&nnel selector":panel.PanelFlags(ChannelSelectorPanel,
                                                  open_on_startup=True,
                                                  single_instance=True,
                                                  on_panel_menu=False,
                                                  location='sidebar',
                                                  API_attribute_name='channelSelector')}
