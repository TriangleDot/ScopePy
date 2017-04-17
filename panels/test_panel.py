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
import imp

# Third party libraries
import numpy as np

from PyQt4.QtCore import *
from PyQt4.QtGui import *

# My libraries
import simpleQt as sqt
import ScopePy_panels as panel
from widgets.sqlite import sqliteConsole

#==============================================================================
#%% Constants
#==============================================================================



#==============================================================================
#%% Class definitions
#==============================================================================

class TestPanel(sqt.SimpleBase):
    """
    Test panel for ScopePy
    
    No __init__() required as it must be the same as the base class
    Must reimplement the drawPanel() method
    
    """
    
    def drawPanel(self):
        """
        Draw the GUI elements of the panel
        
        This is a Mandatory function. It will be called by ScopePy when
        the panel is added to a tab.
        
        """
        
        # Panel layout code goes here
        # =============================
        
        # Master layout
        panelLayout = QVBoxLayout()    
        
        # Example buttons
        testButton1 = QPushButton("Test button 1")

        testButton3 = QPushButton("get selection")
        testButton3.clicked.connect(self.getSelected)
        
        testButton2 = QPushButton("Add channel data")
        self.connect(testButton2,SIGNAL("clicked()"),self.addChannel)
        
        # Get plot names
        getPlotsButton = QPushButton("Get Plot names")
        self.connect(getPlotsButton,SIGNAL("clicked()"),self.updatePlotNames)
        
        self.plotNamesCombo = QComboBox()
        
        self.console = sqt.MiniConsole(commands={'getData':self.getData,'addChannel':self.addChannel,
                                                 'getSelected':self.getSelected})
        self.tbmodel = sqt.TableArray([['1','2','3','4','5'],
                                       ['a','b','c','d','e']])
        #print(self.tbmodel._data)
        self.tb = sqt.Table(self,self.tbmodel)
        
        
        # Add to layout
        self.position([[testButton1],[testButton2],[testButton3],[getPlotsButton],[self.console],[self.tb]])
        
        
        
        # Check preferences
        # =====================
        if self.preferences is None:
            print("Test Panel: has no preferences")
        else:
            print("Test Panel: Preferences are here")
        
        

    # User defined functions go here
    # ==============================================

    def updatePlotNames(self):
        """
        Test getting the plot names from the tab
        
        """
        
        plotNames = self.getAllPlotsOnTab()
        
        self.plotNamesCombo.addItems(plotNames)
        

    def getSelected(self,*args):
        print(self.tb.getSelection())
        return (None,'$'+args[0],self.tb.getSelection())
    def addChannel(self,*args):
        
        # Make a numpy recarray
        # ---------------------------
        dtype = [("x data",float),("y data",float)]
        
        name = "From Test panel"
        recarray = np.zeros(200,dtype)
        recarray["x data"] = np.linspace(-10,11,200)
        recarray["y data"] = 5*np.random.rand(200) + 3*recarray["x data"]
        
        # Make a new channel
        self.API.addChannelData((name,recarray))

    def getData(self,var):
        # Make a numpy recarray
        # ---------------------------
        dtype = [("x data",float),("y data",float)]
        
        name = "From Test panel"
        recarray = np.zeros(200,dtype)
        recarray["x data"] = np.linspace(-10,11,200)
        recarray["y data"] = 5*np.random.rand(200) + 3*recarray["x data"]

        return ('Added data to $%s' % var,'$'+var,recarray)
        
        
    def setFkeys(self):
        
        self.Fkeys = [
                     ['F4','Select',self.selectFunction],
                     ['F6','Process',self.processFunction],
                     ['F9','Make Plot',self.makePlotFunction],
                     ]
        
    def echo(self,item):
        print(item)
        return item
    def selectFunction(self):
        print("This is the select function")

    def processFunction(self):
        print("This is the process ")
    def makePlotFunction(self):
        print("This is the make plot function")



        
        

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


__panels__ = {"Test Panel":panel.PanelFlags(TestPanel,
                                                  open_on_startup=False,
                                                  location='main_area'),
              "SQLite Console":panel.PanelFlags(sqlitePanel,
                                                  open_on_startup=False,
                                                  location='main_area')}
