# -*- coding: utf-8 -*-
"""
Created on Sun Jun  1 14:31:34 2014

@author: john

Test script for scopePy network functions
=============================================

This code is meant to be executed using cell mode

"""


#%% Setup paths
# ===================
 # Adding to the system path
import sys
sys.path.append('/home/john/Documents/Python/scopePy')
sys.path.append('/home/john/Documents/Python/scopePy/unittest')

# Imports
# ================

import numpy as np

from ScopePy_network import *

#%%

#%% Test server interface
""" 
=================================================================
Setup Server [Run in separate console]
=================================================================
"""

# Setup paths
# =============
 # Adding to the system path
import sys
sys.path.append('/home/john/Documents/Python/scopePy')
sys.path.append('/home/john/Documents/Python/scopePy/unittest')

# Imports
# ===========

import numpy as np

from ScopePy_network import *

# Run server
# =============
testServer()


#%% Test Client interface
""" 
=================================================================
Setup Client [Run in separate console]
=================================================================
"""

# Setup paths
# =============
 # Adding to the system path
import sys
import time
sys.path.append('/home/john/Documents/Python/Projects/ScopePy_checkouts/ScopePy_reorg')
sys.path.append('/home/john/Documents/Python/Projects/ScopePy_checkouts/ScopePy_reorg/unittest')

# Imports
# ===========
import socket

import numpy as np

from ScopePy_network import *

# Get IP address of host
hostIP = socket.gethostname() 

def singlePacket(hostIP):
    dataPacket = testPacket()

    sendPacket(hostIP,dataPacket)
    
def testPackets(hostIP,n=4):
    for n in range(n):    
        dataPacket = testPacket("Test data %d" % n)
        sendPacket(hostIP,dataPacket)
    

def spitPackets(hostIP,num_packets=10,delay=2):
    """
    Send packets at intervals
    """
    
    for p in range(num_packets):
        testPackets(hostIP,n=4)
        time.sleep(delay)
        
 
       
def send_data():
    """
    Test the send2scope() function
    
    """
    
    t = np.linspace(-2*np.pi,2*np.pi,20000)
    si = np.sin(2.*np.pi*t)
    co = np.cos(2.*np.pi*t)
    
    send2scope("Sine test",t,si,'time','amplitude')
    send2scope("Cos test",t,co,'time','amplitude')
    
    
        

#%% Send packet to server
# ===========================

dataPacket = testPacket()

sendPacket(hostIP,dataPacket)

#%%

#%% Send multiple packets to server
# ========================================

for n in range(4):    
    dataPacket = testPacket("Test data %d" % n)
    sendPacket(hostIP,dataPacket)

#%%

#%% Test API interface
""" 
=================================================================
Setup API [Run in separate console]
=================================================================
"""

# Setup paths
# =============
 # Adding to the system path
import sys

sys.path.append('/home/john/Documents/Python/Projects/ScopePy')
sys.path.append('/home/john/Documents/Python/Projects/ScopePy/unittest')

import ScopePy_API

API = ScopePy_API.API()

#API.sendCommand("newTab",["myTab"])

