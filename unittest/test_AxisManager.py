# -*- coding: utf-8 -*-
"""
Created on Sat Jun 18 07:52:12 2016

@author: john

AxisManager Unit test script
=======================================
Non-graphical test of the AxisManger classes

"""


#==============================================================================
#%% Imports
#==============================================================================

# Standard library
import os,sys
import string
import unittest
import inspect

# Add main ScopePy folder to paths
CURRENTPATH, dummy = os.path.split(os.path.abspath(__file__))
BASEPATH = os.path.dirname(CURRENTPATH)
sys.path.append(BASEPATH)

# TODO Change this
sys.path.append(os.path.join(BASEPATH,'data_sources'))


# Third party libraries
import numpy as np


# My libraries
from ScopePy_graphs import AxisManager,NiceScale


#==============================================================================
#%% Constants
#==============================================================================



#==============================================================================
#%% Functions
#==============================================================================

def almostEqual(A,B,tol=1.0e-6):
    
    return all( (A-B)<tol )
    
    

#==============================================================================
#%% AxisManager baseclass test
#==============================================================================


class Test_BaseClass(unittest.TestCase):
    """
    Tests basic AxisManager class methods
    
    """
    
    
    #%% Setup teardown
    # ------------------------------------------------------------------------
    
    def setUp(self):
        """
        Setup HDF5 files for testing
        
        """
        pass
   
        
    def tearDown(self):
        pass
    
    
    #%% Coordinate conversion Tests
    # ------------------------------------------------------------------------
    # Check that the data and screen min and max can be reversed and still work
    # Uses simple scale.
    
    def test_scale_data_up_screen_up(self):
        """
        Test Coordinate calculation when the data and screen scales go in 
        same direction
        
        Data scale: min = low, max = high
        Screen scale: min = low, max = high
        
        """
        
        ax = AxisManager()
        
        # Set data limits
        ax.data_min_DC = 0
        ax.data_max_DC = 1
        
        # Set screen limits
        ax.screen_min_SC = 0
        ax.screen_max_SC = 100
        
        # Update
        ax.update()
        
        # Calculate a point
        Ps = ax.to_screen(0.25)
        
        self.assertEqual(Ps,25)
        
        
        
        
    def test_scale_data_up_screen_down(self):
        """
        Test Coordinate calculation when the data and screen scales go in 
        opposite directions
        
        Data scale: min = low, max = high
        Screen scale: min = high, max = low
        
        """
        
        ax = AxisManager()
        
        # Set data limits
        ax.data_min_DC = 0
        ax.data_max_DC = 1
        
        # Set screen limits
        ax.screen_min_SC = 100
        ax.screen_max_SC = 0
        
        # Update
        ax.update()
        
        # Calculate a point
        Ps = ax.to_screen(0.25)
        
        self.assertEqual(Ps,75)
        
        
        
    def test_scale_data_down_screen_up(self):
        """
        Test Coordinate calculation when the data and screen scales go in 
        opposite directions
        
        Data scale: min = high, max = low
        Screen scale: min = low, max = high
        
        """
        
        ax = AxisManager()
        
        # Set data limits
        ax.data_min_DC = 1
        ax.data_max_DC = 0
        
        # Set screen limits
        ax.screen_min_SC = 0
        ax.screen_max_SC = 100
        
        # Update
        ax.update()
        
        # Calculate a point
        Ps = ax.to_screen(0.25)
        
        self.assertEqual(Ps,75)
        
        
        
    def test_scale_data_down_screen_down(self):
        """
        Test Coordinate calculation when the data and screen scales go in 
        opposite directions
        
        Data scale: min = high, max = low
        Screen scale: min = high, max = low
        
        """
        
        ax = AxisManager()
        
        # Set data limits
        ax.data_min_DC = 1
        ax.data_max_DC = 0
        
        # Set screen limits
        ax.screen_min_SC = 100
        ax.screen_max_SC = 0
        
        # Update
        ax.update()
        
        # Calculate a point
        Ps = ax.to_screen(0.25)
        
        self.assertEqual(Ps,25)
        
        
    # Repeat scale tests with negative numbers
        
    def test_scale_neg_data_up_screen_up(self):
        """
        Test Coordinate calculation when the data and screen scales go in 
        same direction
        
        Data scale: min = low, max = high
        Screen scale: min = low, max = high
        
        """
        
        ax = AxisManager()
        
        # Set data limits
        ax.data_min_DC = -1
        ax.data_max_DC = 1
        
        # Set screen limits
        ax.screen_min_SC = -100
        ax.screen_max_SC = 100
        
        # Update
        ax.update()
        
        # Calculate a point
        Ps = ax.to_screen(0.25)
        
        self.assertEqual(Ps,25)
        
        
        
        
    def test_scale_neg_data_up_screen_down(self):
        """
        Test Coordinate calculation when the data and screen scales go in 
        opposite directions
        
        Data scale: min = low, max = high
        Screen scale: min = high, max = low
        
        """
        
        ax = AxisManager()
        
        # Set data limits
        ax.data_min_DC = -1
        ax.data_max_DC = 1
        
        # Set screen limits
        ax.screen_min_SC = 100
        ax.screen_max_SC = -100
        
        # Update
        ax.update()
        
        # Calculate a point
        Ps = ax.to_screen(0.25)
        
        self.assertEqual(Ps,-25)
        
        
        
    def test_scale_neg_data_down_screen_up(self):
        """
        Test Coordinate calculation when the data and screen scales go in 
        opposite directions
        
        Data scale: min = high, max = low
        Screen scale: min = low, max = high
        
        """
        
        ax = AxisManager()
        
        # Set data limits
        ax.data_min_DC = 1
        ax.data_max_DC = -1
        
        # Set screen limits
        ax.screen_min_SC = -100
        ax.screen_max_SC = 100
        
        # Update
        ax.update()
        
        # Calculate a point
        Ps = ax.to_screen(0.25)
        
        self.assertEqual(Ps,-25)
        
        
        
    def test_scale_neg_data_down_screen_down(self):
        """
        Test Coordinate calculation when the data and screen scales go in 
        opposite directions
        
        Data scale: min = high, max = low
        Screen scale: min = high, max = low
        
        """
        
        ax = AxisManager()
        
        # Set data limits
        ax.data_min_DC = 1
        ax.data_max_DC = -1
        
        # Set screen limits
        ax.screen_min_SC = 100
        ax.screen_max_SC = -100
        
        # Update
        ax.update()
        
        # Calculate a point
        Ps = ax.to_screen(0.25)
        
        self.assertEqual(Ps,25)
        
        
        
    #%% Axis tick marks and labels tests
        
    def test_axis_ticks_data_up_screen_up(self):
        """
        Test tick mark lables
        
        """
        
        ax = AxisManager()
        
        # Set data limits
        ax.data_min_DC = 0
        ax.data_max_DC = 1
        
        ax.plot_min_DC = 0
        ax.plot_max_DC = 1
        
        # Set screen limits
        ax.screen_min_SC = 0
        ax.screen_max_SC = 100
        
        # Update
        ax.update()
        
        # Calculate a point
        Ps = ax.to_screen(0.25)
        
        # Print axis information
        print(ax)
        

        # Check tick marks
        self.assertEqual(ax.major_tick_spacing_DC,0.1)
        self.assertTrue(all( ax.major_ticks_DC == np.arange(0,1,0.1) ))
        self.assertTrue(all( ax.minor_ticks_DC == np.arange(0,1,0.02) ))
        
        self.assertTrue(almostEqual( ax.major_ticks_SC, np.arange(0,100,10.0) ))
        self.assertTrue(almostEqual(ax.minor_ticks_SC, np.arange(0,100,2.0) ))
        
        # checks
        
        self.assertEqual(Ps,25)
        
    
        
        
        
        
#==============================================================================
#%% Runner
#==============================================================================

if __name__ == "__main__":
    unittest.main()

    