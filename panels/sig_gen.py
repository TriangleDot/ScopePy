# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 06:46:31 2015

@author: john

Example panel for ScopePy

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
import ScopePy_panels as panel
from ScopePy_graphs import GraphWidget
from ScopePy_channel import ScopePyChannel,plotLineStyle

#==============================================================================
#%% Constants
#==============================================================================



#==============================================================================
#%% Class definitions
#==============================================================================

class SineWaveGeneratorPanel(panel.PanelBase):
    """
    Signal Generator panel for ScopePy
    
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
        
        
        # Panel widgets
        # ================================
          
        # Editable Settings 
        # -----------------------
          
        # Number validation
        float_regex = QRegExp(r"[\.0-9\-\+e\*\/]+")
        float_validator = QRegExpValidator(float_regex)
        
        int_regex = QRegExp(r"[0-9]+")
        int_validator = QRegExpValidator(int_regex)
        
        
        self.frequency_txtEd = QLineEdit("1.0")
        self.frequency_txtEd.setValidator(float_validator)
        
        self.phase_txtEd = QLineEdit("0.0")
        self.phase_txtEd.setValidator(float_validator)
        
        self.amplitude_txtEd = QLineEdit("1.0")
        self.amplitude_txtEd.setValidator(float_validator)
        
        self.start_txtEd = QLineEdit("-6.0")
        self.start_txtEd.setValidator(float_validator)
        
        self.stop_txtEd = QLineEdit("6.0")
        self.stop_txtEd.setValidator(float_validator)
        
        self.step_txtEd = QLineEdit("0.05")
        self.step_txtEd.setValidator(float_validator)
        
        self.numPoints_txtEd = QLineEdit("500")
        self.numPoints_txtEd.setValidator(int_validator)
        
        
        # Channel info 
        # ---------------
        self.channelName_txtEd = QLineEdit("New channel")
        self.xaxis_txtEd = QLineEdit("x axis label")
        self.yaxis_txtEd = QLineEdit("y axis label")
        
        # Buttons
        # ----------
        makeChannel_button = QPushButton("Make Channel")
        
        # Graph display
        # -----------------
        
        # Make a channel for displaying the signal that will respond to changes
        linestyle = plotLineStyle(lineColour="#F7D358",marker='.')
        self.testChannel = ScopePyChannel("TestSignal",linestyle)
        
        # Calculate initial signal and put it in the channel
        # This creates self.x_data & self.y_data
        self.makeSignal()
        self.testChannel.addData2Channel(self.data)
        
        
        self.graph = GraphWidget(self.preferences)
        self.graph.addChannel(self.testChannel,chunkMode='latest')
        
        
        # Connections
        # ================
        
        # Buttons
        self.connect(makeChannel_button, SIGNAL("clicked()"),self.makeChannel)
        
        # Text edit boxes
        
        # step and number of points are interlinked
        self.connect(self.step_txtEd,SIGNAL("textEdited (const QString&)"),self.updatePoints)
        self.connect(self.numPoints_txtEd,SIGNAL("textEdited (const QString&)"),self.updateStep)
        
        # Other parameters trigger automatic update of the signal
        self.connect(self.start_txtEd,SIGNAL("textEdited (const QString&)"),self.updateSignal)
        self.connect(self.stop_txtEd,SIGNAL("textEdited (const QString&)"),self.updateSignal)
        self.connect(self.frequency_txtEd,SIGNAL("textEdited (const QString&)"),self.updateSignal)
        self.connect(self.amplitude_txtEd,SIGNAL("textEdited (const QString&)"),self.updateSignal)
        self.connect(self.phase_txtEd,SIGNAL("textEdited (const QString&)"),self.updateSignal)
        
        
        # Internal
        self.connect(self.testChannel,SIGNAL("updateChannelPlot"),self.graph.updateChannel)
        
        
        # Layout
        # =======================
        
        
        # Settings layout in a grid
        # ----------------------------
        settingsLayout = QGridLayout()  
        
        # Add to layout
        
        
        
        # First column
        settingsLayout.addWidget(QLabel("Setting"),0,0)
        
        settingsLayout.addWidget(QLabel("Frequency"),1,0)
        settingsLayout.addWidget(self.frequency_txtEd,1,1)
        
        settingsLayout.addWidget(QLabel("Amplitude"),2,0)
        settingsLayout.addWidget(self.amplitude_txtEd,2,1)
        
        settingsLayout.addWidget(QLabel("Phase"),3,0)
        settingsLayout.addWidget(self.phase_txtEd,3,1)
        
        
        # Second column
        settingsLayout.addWidget(QLabel("Range"),0,2)
        
        settingsLayout.addWidget(QLabel("Start"),1,2)
        settingsLayout.addWidget(self.start_txtEd,1,3)
        
        settingsLayout.addWidget(QLabel("Stop"),2,2)
        settingsLayout.addWidget(self.stop_txtEd,2,3)
        
        settingsLayout.addWidget(QLabel("Step"),3,2)
        settingsLayout.addWidget(self.step_txtEd,3,3)
        
        settingsLayout.addWidget(QLabel("Number of points"),4,2)
        settingsLayout.addWidget(self.numPoints_txtEd,4,3)
        
        
        # Channel info layout
        # ----------------------
        channelLayout = QGridLayout()
        
        channelLayout.addWidget(QLabel("Channel name"),0,0)
        channelLayout.addWidget(self.channelName_txtEd,0,1)
        
        channelLayout.addWidget(QLabel("x axis label"),1,0)
        channelLayout.addWidget(self.xaxis_txtEd,1,1)
        
        channelLayout.addWidget(QLabel("y axis label"),2,0)
        channelLayout.addWidget(self.yaxis_txtEd,2,1)
        
        # Main panel layout
        # --------------------
        panelLayout = QVBoxLayout()
        
        # Header row
        panelLayout.addWidget(QLabel("ScopePy Signal Generator"))
        panelLayout.addWidget(self.graph)
        panelLayout.addLayout(settingsLayout)
        panelLayout.addLayout(channelLayout)
        panelLayout.addWidget(makeChannel_button)
        
        
        # Add layout to master widget [Mandatory]
        # ========================================
        # mandatory
        self.setLayout(panelLayout)
        
        

    # User defined functions go here
    # ==============================================

    # Data extraction as properties
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    

    @property
    def Range(self):
        """
        Get the range = stop - start
        
        Outputs
        --------
        range : float
            stop - start
            
        """
        
        return self.stop - self.start
        
        
    @property
    def frequency(self):
        
        return eval_text(self.frequency_txtEd.text())
            
        
    @property
    def amplitude(self):
        
        return eval_text(self.amplitude_txtEd.text())
        
        
    @property
    def phase(self):
        
        return eval_text(self.phase_txtEd.text())
        
    @property
    def start(self):
        
        return eval_text(self.start_txtEd.text())
        
    @property
    def stop(self):
        
        return eval_text(self.stop_txtEd.text())
        
    @property
    def step(self):
        
        return eval_text(self.step_txtEd.text())
        
    @property
    def number_points(self):
        
        return int(eval_text(self.numPoints_txtEd.text()))


    # GUI actions
    # +++++++++++++++++++++++++++++++++++++++++++++++++
    def updatePoints(self,newStepSize_str):
        """
        Update the number of points according to the new step size
        
        Inputs
        -------
        newStepSize_str : str
            new step size that has been edited, in string form
        
        """
        
        if newStepSize_str is None or newStepSize_str=='':
            return
        
        newStepSize = float(newStepSize_str)
        
        # Ignore zero
        if newStepSize==0:
            return
        
        
        # Get range
        xrange = self.Range
        
        # Get new number of points
        nPoints = round(xrange/newStepSize)
        
        # Recalculate the step size (because of rounding)
        stepSize = xrange/nPoints
        
        # Set adjusted step size back into GUI
        self.step_txtEd.setText(str(stepSize))
        
        # Set new number of points
        self.numPoints_txtEd.setText("%i" % nPoints)
        
        # Update signal 
        self.updateSignal()
        
        
        
    
    def updateStep(self,nPoints_str):
        """
        Update the step size according to a new number of points
        
        Inputs
        -------
        nPoints_str : str
            new number of points that has been entered.
        """
        
        if nPoints_str is None or nPoints_str=='':
            return
            
            
        # Get range
        xrange = self.Range
        
        nPoints = int(nPoints_str)
        
        if nPoints==0:
            return
        
        # Recalculate the step size (because of rounding)
        stepSize = xrange/nPoints
        
        # Set adjusted step size back into GUI
        self.step_txtEd.setText(str(stepSize))
        
        # Update signal 
        self.updateSignal()
        
        
    def makeSignal(self):
        """
        Calculate the signal and update x and y data
        
        """    
        # Check the parameters are all good
        # --------------------------------------
        # If the user has half edited them then there may be bad values
        # which should show up as None in the properties
        parameters = [self.frequency,self.amplitude,self.phase,
                      self.start,self.stop,self.step,self.number_points]
                      
        bad_parameters = [x is None for x in parameters ]
        
        if any(bad_parameters):
            return
        
        # Calculate the data
        # ----------------------
        x_data = np.linspace(self.start,self.stop,self.number_points)
        y_data = self.amplitude*np.sin(2*np.pi*self.frequency*x_data + self.phase)
        
        # Put in a recarray
        self.data = np.zeros(len(x_data),[('x',float),('y',float)])
        
        self.data['x'] = x_data
        self.data['y'] = y_data
        
        
    def updateSignal(self):
        """
        Trigger update of channel data and through that the plot
        
        """
        
        self.makeSignal()
        self.testChannel.addData2Channel(self.data)
        
        
        
        
    def makeChannel(self):
        """
        Calculate the channel data values and add to main scopePy channel selector
        
        """
        
        # Get all the labels
        # ----------------------
        channel_name = self.channelName_txtEd.text()
        x_label = self.xaxis_txtEd.text()
        y_label = self.yaxis_txtEd.text()
        
        
        # Calculate the data
        # ----------------------
        self.makeSignal()

        
    
        # Copy self.data into new numpy recarray
        # ----------------------------------------
        # Rename the columns from the labels
        dtype = [(x_label,np.float),(y_label,np.float)]

        # Copy the data        
        recarray = np.zeros(len(self.data),dtype)
        recarray[x_label] = self.data['x']
        recarray[y_label] = self.data['y']
        
        # Make a new channel
        # -----------------------
        self.API.addChannelData((channel_name,recarray))




#==============================================================================
#%% Functions
#==============================================================================

def eval_text(text_str):
    """
    Perform eval() function on string if it is not empty
    
    Convenience function for parsing LineEdits
    
    Input
    -----
    text_str : str
        string that is expected to yield a numeric value when eval()'ed
        
    Output
    ------
    value : float
        resulting value from eval() or None if the string is empty
        
    """
    
    if text_str is '':
        return None
        
    try:
        return eval(text_str)
        
    except:
        return None
        
        


#==============================================================================
#%% Panels to export
#==============================================================================
# Put any panels to be imported from this file here
# Note: this must go after the class definitions
#
# Panels are passed in a dictionary where:
#   key = the name to be used on menus
#   value = PanelFlags class from ScopePy_panels.py

__panels__ = {"Sine wave Generator":panel.PanelFlags(SineWaveGeneratorPanel,
                                                  open_on_startup=False,
                                                  location='main_area')}
