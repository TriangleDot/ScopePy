# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 06:46:31 2015

@author: john

Built-in panels for ScopePy

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
import copy

# Third party libraries
import numpy as np

from PyQt4.QtCore import *
from PyQt4.QtGui import *

# My libraries
import ScopePy_panels as panel
import widgets.table_editor_lib as TE
import simpleQt as sqt

#==============================================================================
#%% Constants
#==============================================================================

NOT_SELECTED = 'None'


#==============================================================================
#%% Class definitions
#==============================================================================

class TableEditor(panel.PanelBase):
    """
    Table Editor for looking at data sources, channels etc.
    
    Can create channels from this
    
    
    
    No __init__() required as it must be the same as the base class
    Must reimplement the drawPanel() method
    
    """
    
    def drawPanel(self):
        """
        Draw the GUI elements of the panel
        
        This is a Mandatory function. It will be called by ScopePy when
        the panel is added to a tab.
        
        """
        # Internal variables
        # =============================
        self.groupNameText = 'Group 1:'
        
        
        # Panel layout code goes here
        # =============================
        
          
        
        # Source info
        # ---------------------
        sourceLabel = QLabel('Data source')
        self.sourceLink = QLabel("No source")
        self.sourceLink.setMaximumWidth(self.API.charHeight_px*80)
        
        
        
        # Column selector buttons
        # -----------------------------
        setXButton = QPushButton("Set X column [X]")
        setXButton.setShortcut(QKeySequence('X'))
        self.xLabel = QLabel(NOT_SELECTED)
        
        setYButton = QPushButton("Set Y column [Y]")
        setYButton.setShortcut(QKeySequence('Y'))
        self.yLabel = QLabel(NOT_SELECTED)
        
        self.columnSelector = QLineEdit()
        self.columnSelector.setMaximumWidth(self.API.charHeight_px*80)
        columnSelectorLabel = QLabel('Column selec&tor')
        columnSelectorLabel.setBuddy(self.columnSelector)
        
        self.connect(setXButton,SIGNAL("clicked()"),self.setXcolumn)
        self.connect(setYButton,SIGNAL("clicked()"),self.setYcolumn)
        self.connect(self.columnSelector,SIGNAL("returnPressed()"),self.selectColumnFromSelector)
        
        # Table editor widget
        # --------------------------
        self.table = TE.TableEditorWidget()

        # Top bar layout
        # ---------------------------
        topBar = sqt.frame(self)
        topBar.position([
        [sourceLabel, self.sourceLink ,sqt.empty(), setXButton,setYButton],
        [columnSelectorLabel,self.columnSelector,sqt.empty(),self.xLabel,self.yLabel]
        ])
        

        
        # Master layout
        panelLayout = QVBoxLayout()  
        
        # Add to layout
        panelLayout.addWidget(topBar)
        panelLayout.addWidget(self.table)
        
        
        # Add layout to master widget [Mandatory]
        # ========================================
        # mandatory
        self.setLayout(panelLayout)
        
        # Check preferences
        # =====================
        if self.preferences is None:
            print("Test Panel: has no preferences")
        else:
            print("Test Panel: Preferences are here")
            
            
        # Setup ScopePy comms signals
        # ================================
        self.addCommsAction('addSource',self.addSource)
        self.addCommsAction('makeChannel',self.makeChannel)
        
        
        # Keyboard shortcuts
        # =================================
#        shortcut_list = [
#            ['insertRowBelow',Qt.ALT+Qt.Key_Down,self.insertRowBelow],
#            ['insertRowAbove',Qt.ALT+Qt.Key_Up,self.insertRowAbove],
#            ]
#        self.addKeyboardShortcuts(shortcut_list)
        
        
    def setFkeys(self):
        """
        Set function keys for plotting
        
        """
        
        self.Fkeys = [
                     ['F10','Group channel',self.groupChannelMaker],
                     ]
        

    # User defined functions go here
    # ==============================================
    

    def addSource(self,data_wrapper,name='No source'):
        """
        Add data source to the table
        
        The data must be wrapped to have suitable methods for use with the
        TableEditorModel class.
        
        See TODO [numpy wrapper in table_editor_lib] for the methods required
        
        Input
        -----
        data_wrapper : wrapper class
            class with appropriate methods
        """
        
        # TODO check for methods
        
        self.table.setModel(TE.TableEditorModel(data_wrapper))
        
        # Put column headers into column selector combo box using a completer
        completer = QCompleter(data_wrapper.columnHeaders())
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.columnSelector.setCompleter(completer)
        
        self.sourceLink.setText(name)
        self.sourceTableWrapper = data_wrapper
        
        self.groupNameText = name
        
        self.table.update()
        
        
        
        
    def addChannel(self,channel):
        # TODO ability to drop a channel in for editing
        pass
    
    
    
    def makeChannel(self,channel_name,xcol,ycol):
        """
        Make a channel from two names columns and add to the channel
        selector.
        
        This is intended for remote control operation
        
        Inputs
        -------
        channel_name : str
            name of channel
            
        xcol,ycol : str
            column names to be used as x and y data
        
        """
        
        # Check columns exist
        if not all([self.table.isColumnInTable(xcol),self.table.isColumnInTable(ycol)]):
            logger.debug("table_editor panel:makeChannel: Cannot find one or both columns [%s,%s]" % (xcol,ycol))    
            return
        
        
        # Make a numpy recarray
        # ---------------------------
        xdata = self.table.getColumnByName(xcol)
        ydata = self.table.getColumnByName(ycol)
        
        dtype = [(xcol,float),(ycol,float)]
        
        # remove link to existing data
        # TODO is this necessary?
        recarray = np.zeros(len(xdata),dtype)
        recarray[xcol] = copy.deepcopy(xdata)
        recarray[ycol] = copy.deepcopy(ydata)
        
        # Make a new channel
        self.API.addChannelData((channel_name,recarray))
        
        
    
    def makeGroupChannel(self,channel_name,xcol,ycol):
        """
        Make a group channel from two names columns and add to the channel
        selector.
        
        This is intended for remote control operation
        
        Inputs
        -------
        channel_name : str
            name of channel
            
        xcol,ycol : str
            column names to be used as x and y data
        
        """
        
        # Check columns exist
        if not all([self.table.isColumnInTable(xcol),self.table.isColumnInTable(ycol)]):
            logger.debug("table_editor panel:makeGroupChannel: Cannot find one or both columns [%s,%s]" % (xcol,ycol))    
            return
      
        
        # Make a new group channel
        self.API.addGroupChannel(channel_name,self.sourceTableWrapper,xcol,ycol)
     
     
    def groupChannelMaker(self):
        """
        Make a group channel
        
        Temporary method for testing group channels
        
        """
        
        # Get x and y columns
        xcol = self.xLabel.text()
        ycol = self.yLabel.text()
        
        name,ok = QInputDialog.getText(self.API._gui,'Group channel',
                                       'Please Enter a name for this channel:',
                                       QLineEdit.Normal,self.groupNameText)
        
        if ok:
            self.groupNameText = name
            self.makeGroupChannel(name,xcol,ycol)
        
        
    
    
    def setXcolumn(self):
        """
        Set the x column from the currently selected column
        
        """
        
        col_name = self.table.getSelectedColumnName()
        
        # Nothing selected
        if not col_name:
            return
            
        self.xLabel.setText(col_name) # TODO remove later
        
        data = self.table.getColumnByName(col_name)
        
        ID = self.API.panelID("Channel selector")
        self.API.sendComms('addXdata',ID,data,col_name,self.sourceLink.text())
        
        
        
    
    def setYcolumn(self):
        """
        Set the y column from the currently selected column
        
        """
        
        col_name = self.table.getSelectedColumnName()
        
        # Nothing selected
        if not col_name:
            return
            
        self.yLabel.setText(col_name)
        
        data = self.table.getColumnByName(col_name)
        
        ID = self.API.panelID("Channel selector")
        self.API.sendComms('addYdata',ID,data,col_name,self.sourceLink.text())
        
        
        
    def selectColumnFromSelector(self):
        """
        Select column using text in the column selector
        
        """
        
        
        # Get text from column selector
        col_text = self.columnSelector.text()
        
        # Check if it is in the column headers
        col_index = self.table.getColumnIndexFromName(col_text)
        
        if not col_index:
            
            return
            
        
        self.table.selectColumn(col_index)
        
        
        
        
    
        
    
    
        
        
        
        
    




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
#   value = PanelFlags class from ScopePy_panels.py


__panels__ = {"Table editor":panel.PanelFlags(TableEditor,
                                                  open_on_startup=False,
                                                  location='main_area')}