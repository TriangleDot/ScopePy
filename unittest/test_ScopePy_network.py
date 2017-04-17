# -*- coding: utf-8 -*-
"""
Created on Mon May 26 07:02:07 2014

@author: john

Unit test for ScopePy networking functions

"""

#%% Setup paths
# ===================
 # Adding to the system path
import sys
sys.path.append('/home/john/Documents/Python/scopePy')
sys.path.append('/home/john/Documents/Python/scopePy/unittest')

# Imports
# ================
import unittest
import numpy as np

from ScopePy_network import *


#%% Unit tests
class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        # Setup the paths to use for checking the copying
        self.src = '/home/john/Documents/Python/unit_test/filecopy/src'
        self.dest = '/home/john/Documents/Python/unit_test/filecopy/dest'
        
        # Make standard packet info
        x = np.arange(0,10)
        y = (x**2)*1.27
        
        channelLabel = "MyChannel"
        columnNamesList = ['x axis','y axis']
        
        self.standardArray = np.column_stack((x,y))
        self.standardColumnNames = columnNamesList




    def test_template(self):
        # Put test here
        
        

        # test condition
        self.assertTrue(True)
        
        
    def test_makeDataPacket(self):
        #%%
        # Create a simple packet
        channelLabel = "MyChannel"
        array_in = self.standardArray
        columnNamesList = self.standardColumnNames
        
        # Make the data packet
        packet = makeDataPacket(channelLabel,array_in[:,0],array_in[:,1],columnNamesList)
        
        #%%
        
        # test condition
        self.assertTrue(len(packet)==215)
        


    def test_extractDataPacket(self):
        # Create a simple packet
        channelLabel = "MyChannel"
        array_in = self.standardArray
        columnNamesList = self.standardColumnNames
        
        # Make the data packet
        packet = makeDataPacket(channelLabel,array_in[:,0],array_in[:,1],columnNamesList)
        
        
        #%%
        packetType,remainingPacket = getPacketType(packet)
        channelLabel,recArray_out = extractDataPacket(remainingPacket)
        
        # Compare against input array
        check = (recArray_out['x axis']-array_in[:,0] ) + (recArray_out['y axis']-array_in[:,1] )

        # test condition
        self.assertTrue(np.sum(check)==0.0)
        
       
    def test_wrapDataPacket(self):
        # Create a simple packet
        channelLabel = "MyChannel"
        array_in = self.standardArray
        columnNamesList = self.standardColumnNames
        
        # Make the data packet
        packet = makeDataPacket(channelLabel,array_in[:,0],array_in[:,1],columnNamesList)
        
        
        wrappedPacket = wrapDataPacket(packet)
        
         # test condition
        self.assertTrue(len(wrappedPacket) == 223)



if __name__ == '__main__':
    unittest.main()