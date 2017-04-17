# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 06:46:31 2015

@author: john

WL3 ADC snapshot viewer
===========================
Panel for viewing ADC snapshots in a scope style


Version
==============================================================================
$Revision:: 20                            $
$Date:: 2015-04-11 08:50:53 -0400 (Sat, 1#$
$Author:: john                            $
==============================================================================

"""




#==============================================================================
#%% Imports
#==============================================================================

# Standard library
import os


# Third party libraries
import numpy as np

from PyQt4.QtCore import *
from PyQt4.QtGui import *

# My libraries
import ScopePy_panels as panel
from ScopePy_graphs import GraphWidget
from ScopePy_channel import ScopePyChannel,plotLineStyle
import simpleQt as sqt

# Python Instrument library


#==============================================================================
#%% Constants
#==============================================================================

ROLLOVER = 200

DEFAULT_IP_ADDRESS = 'Not used yet'

DEFAULT_TIMER_INTERVAL_SECONDS = 1

#==============================================================================
#%% Class definitions
#==============================================================================

class RolloverExample(sqt.SimpleBase):
    """
    ADC snapshot viewer panel for ScopePy
    
    
    
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
          
 
        
        
        
        
        # Make the channels for holding the data
        # -------------------------------------------
        
        channel_colours = {'ADC0':"#0489B1",'ADC1':'#DF7401',
        'ADC2':"#0489B1",'ADC3':'#DF7401'}
        
        self.adc_channels = {}
        
        for ch in channel_colours:
            linestyle = plotLineStyle(lineColour=channel_colours[ch],
                                      marker='o',markerSize=2)
            self.adc_channels[ch] = ScopePyChannel(ch,linestyle)
            self.adc_channels[ch].rollover = ROLLOVER
            
            

        
        
        # Graph display
        # -----------------
        
        self.graph_x = GraphWidget(self.preferences)
        #self.graph_x.horiz_size = 700
        self.graph_x.xlabel = 'Sample'
        self.graph_x.ylabel = 'ADC Count [LSB]'
        self.graph_x.xmin = 0
        self.graph_x.xmax = ROLLOVER
        self.graph_x.ymin = 0.0
        self.graph_x.ymax = 32.0
        
        for channel in self.adc_channels:
            self.graph_x.addChannel(self.adc_channels[channel],chunkMode='rollover')
        
     
        
        
        # Buttons
        # ------------
        # Run/Stop
        # Single shot
        # clear
        # IP address (Text edit)
        # Connect
        
        # Run/Stop button
        self.button_run_stop = sqt.ToggleButton(self,"Run")
        self.button_run_stop.setButtonTextForState('Stop',True)
        self.button_run_stop.setButtonTextForState('Run',False)
        self.button_run_stop.bindStateChanged(self.run_stop)

        # Single shot button        
        self.button_single_shot = sqt.button(self,'Single shot')
        self.button_single_shot.bindClicked(self.single_shot)
        
        # clear button
        self.button_clear = sqt.button(self,'Clear')
        self.button_clear.bindClicked(self.clear)
        
        # Connect button
        self.button_connect = sqt.button(self,'Connect')
        self.button_connect.bindClicked(self.connect_card)
        
        # IP address
        IP_label = QLabel('IP Address')
        self.IP_address_text = sqt.entry(self)
        self.IP_address_text.setText(DEFAULT_IP_ADDRESS)
        self.IP_address_text.widget.setMaxLength(15)
        self.IP_address_text.widget.setMinimumWidth(self.API.charWidth_px*20)
        self.IP_address_text.widget.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        
        
        spacer = sqt.empty()
        
        
        # Connections
        # ================
        # Plot updates
        for channel in self.adc_channels:
            self.connect(self.adc_channels[channel],SIGNAL("updateChannelPlot"),self.graph_x.updateChannel)
        
        
        # Timer for when the panel is in 'Run' mode
        self.timer = QTimer()
        QObject.connect(self.timer,SIGNAL('timeout()'),self.run)
        

        
        # Layout
        # =======================
        button_frame = sqt.frame(self)
        button_frame.position([ [self.button_run_stop,
                                 self.button_single_shot,
                                 self.button_clear,
                                 spacer,
                                 IP_label,
                                 self.IP_address_text,
                                 self.button_connect]])
                                 
        
        plot_frame = sqt.frame(self)
        plot_frame.position( [ [self.graph_x]])
                              
          
        # Add to main layout                    
        self.position([ [button_frame],
                       [plot_frame]])
       
       
        # Panel variables
        # ================
        self.sample_count = 0
        
        self.running = False
       
        
        
        

    # User defined functions go here
    # ==============================================

    # Scope button callbacks
    def run_stop(self,state):
        """
        Start/Stop sample acquisition
        """
        
        if state:
            print('Run/Stop True state')
            self.running = True
            self.timer.start(DEFAULT_TIMER_INTERVAL_SECONDS)
        else:
            print('Run/Stop False state')
            self.running = False
            self.timer.stop()
            
            
            
    def run(self):
        
        if self.running:
            self.make_test_data()
            self.updatePlots()
        
    
    def stop(self):
        pass
    
    def single_shot(self):
        self.make_test_data()
        self.updatePlots()
    
    
    def clear(self):
        """
        Clear all plots
        """

        for ch in self.adc_channels:        
            self.adc_channels[ch].clearChannelData()
            
        # Reset sample count
        self.sample_count = 0
                            
        self.updatePlots()
        
            
    
    def connect_card(self):
        pass
            
            

    def make_test_data(self):
        """
        Function to generate dummy data for testing without a real card
        
        """
        
        N = 1
        
        dummy_data = 32*np.random.random((N,4))
        
        # Data for X,Y time plots
        for iCh,ch in enumerate(self.adc_channels):
            dtype = [('Samples',float),(ch,float)]
            array = np.zeros(N,dtype)
            array['Samples'] = self.sample_count
            array[ch] = dummy_data[:,iCh]
        
            self.adc_channels[ch].addData2Channel(array,update_signal=False)
            
        # Increment sample count
        self.sample_count += 1
        
        # Adjust x axis
        if self.sample_count > ROLLOVER:
            new_max = np.ceil(self.sample_count/ROLLOVER)*ROLLOVER
            self.graph_x.xmin = new_max - ROLLOVER
            self.graph_x.xmax = new_max
            
        
        
        

    


    # GUI actions
    # +++++++++++++++++++++++++++++++++++++++++++++++++
    
        
        
    def updatePlots(self):
        """
        Trigger update of plots
        
        """
        
        self.graph_x.update()
        #self.graph_x.autoscaleX()
        
        
        
        
        
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

__panels__ = {"Rollover plot example":panel.PanelFlags(RolloverExample,
                                                  open_on_startup=False,
                                                  location='main_area')}

