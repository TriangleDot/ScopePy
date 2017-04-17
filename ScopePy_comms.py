# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 21:21:23 2015

@author: john

ScopePy Communications library
=============================
Signaling system between different parts of ScopePy


Version
==============================================================================
$Revision:: 78                            $
$Date:: 2015-09-30 21:43:30 -0400 (Wed, 3#$
$Author::                                 $
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
import logging
import inspect

# Third party libraries
from PyQt4.QtCore import *


# My libraries

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

SCOPEPY_SIGNAL = 'scopepy_signal'


#==============================================================================
#%% Class definitions
#==============================================================================
class SignalPacket():
    """
    Simple data class that represents the information sent in a ScopePy signal.
    
    Contains:
        The signal name
        Sender
        arguments to be sent
        keyword arguments to be sent
        relay flag - tells the receiver to re-send this packets
        
    """
    
    def __init__(self):
        
        self.name = ''
        self.sender = '' 
        self.receiver = ''
        self.args = []
        self.kwargs = {}
        self.relay = False
        self.broadcast = False
        
        
        
        

class SignalComms():
    """
    This class is designed to be inherited, i.e. it is a 'mixin' class. (This
    means it can't have an __init__() method)
    
    It provides methods for sending and receiving signals and links to the 
    actions to perform.
    
    Basic usage
    --------------------
    Two objects can be connected by inheriting from SignalComms
    
        class object_A(QObject,SignalComms):
            # First class
            def __init__()
                # Initialise base class
                super(object_A,self).__init__()
                
                # Initialise SignalComms
                self.initialiseComms('A')
            
        class object_B(QObject,SignalComms):
            # Second class
            def __init__()
                # Initialise base class
                super(object_B,self).__init__()
                
                # Initialise SignalComms
                self.initialiseComms('B')
            
    Instances must be connected with a single QT signal
    
        import ScopePyComms as comms
        
        # Create objects
        A = object_A()
        B = object_B()
        
        # Add A -> B connections
        
        # Add B as a receiver to A, use a string label, in this case B.name is a string
        A.addCommsReceiver(B.name,B)
        A.connect(A,SIGNAL(comms.SCOPEPY_SIGNAL),B.receiveComms)
            
        # Add B -> A connection
        B.connect(A,SIGNAL(comms.SCOPEPY_SIGNAL),A.receiveComms)
    
    This gives a two communication between A and B
    
    
    ScopePy comms setup
    --------------------------
    ScopePy is setup so that all panels have a SignalComms link back to the
    API. Every time a panel is created the API establishes a SignalComms link
    to it. Panels however only have a link to the API. If one panel wants to
    communicate with another then it must send the its signal through the 
    API.
    

    Diagram of ScopePy SignalComms setup
    
     +-----------------+
     |    API          |
     |-----------------|                  +-------------------------+
     |                 |                  | Panel 1                 |
     |                 |                  |-------------------------|
     |     +----------+|                  | +------------------+    |
     |     | Signal   ||                  | | SignalComms      |    |
     |     |-Comms----||                  | |------------------|    |
     |     |+-------->||             +----->|                  |    |
     |     |          ||             |    | +------------------+    |
     |     |          ||             |    +-------------------------+
     |     |          |<-------------+
     |     |          ||
     |     |          ||
     |     |          |<----------+       +-------------------------+
     |     |          ||          |       | Panel 2                 |
     |     +----------+|          |       |-------------------------|
     |                 |          |       | +------------------+    |
     |                 |          |       | | SignalComms      |    |
     +-----------------+          |       | |------------------|    |
                                  +-------->|                  |    |
                                          | +------------------+    |
                                          +-------------------------+
                                          

    Sending signals between SignalComms objects
    -----------------------------------------------
    A can send a signal to B using the command
    
    >>> A.sendComms("my signal",'B',*args,**kwargs)
    
    The type of signal, in this case "my signal" is user defined. It must have
    been setup in B previously.
    
    To setup B to receive this signal 
    
    >>> B.addCommsAction("my signal",B.respond_to_my_signal)
    
    B.respond_to_my_signal is a method of the object B in this case, but it
    can be any function reference.
        
    
    """
    # TODO: There is a name clash with the variable 'name' in the panel class
    # It's messing up the signal comms
    
    # SignalComms constants
    BROADCAST = "broadcast"
    
    
    
    def initialiseComms(self,name=''):
        """
        Setup the variable names associated with SignalComms objects
        
        This function must be called explicitly before using the SignalComms
        features.
        
        It exists because a mixin class that is inherited with a QObject
        cannot have an __init__() method. Or at least I can't get it to work.
        
        """
        
        # Name of this instance
        # - used to filter signals
        self.ID = name
        
        # Dictionary of actions to do when receiving signals
        # -use addSignal() method to add to this
        self._actions = {}
        
        # Receivers
        # dictionary of receivers
        self._receivers = {}
        
        
    def addCommsAction(self,signal_name,function_to_call):
        """
        Add an action for a signal
        
        Inputs
        -------
        signal_name : str
            The name of the signal that performs this actions
            
        function_to_call: function reference
            The function that will be called
            
        """
        
        # Add to the internal dictionary
        if signal_name not in self._actions:
            self._actions[signal_name] = function_to_call
        else:
            logger.debug("SignalComms: Tried to add duplicate signal [%s]" % signal_name)
            



    def addCommsReceiver(self,receiver_name,receiver_instance):
        """
        Add a receiver to the internal dictionary
        
        Inputs
        --------
        receiver_name: str
        
        receiver_instance : panelBase instance or other ScopePy things
        
        """

        # Check the receiver can actually receive things
        assert hasattr(receiver_instance,'receiveComms'), "SignalComms: Tried to add a receiver that cannot receive anything"        
        
        logger.debug("SignalComms: [%s] Adding Receiver [%s]" % (self.ID,receiver_name))
        self._receivers[receiver_name] = receiver_instance
        
                
            
        
    def sendComms(self,signal_name,receiver,*args,**kwargs):
        """
        Send a signal to the receiver
        
        Inputs
        ---------
        signal_name : str
            Name of signal that is being sent
            
        receiver : str
            Name label of receiver where the packet is being sent, if set to
            self.BROADCAST then the packet will be received by every receiver
            
        *args : arguments to be passed to signal function
        
        **kwargs : keyword arguments to be sent to signal function.
            
        
        """
        
        # Make packet
        # ========================
        packet = SignalPacket()
        packet.name = signal_name
        packet.sender = self.ID
        packet.receiver = receiver
        packet.args = args
        packet.kwargs = kwargs
        packet.relay = False
        
        # Check for broadcasting
        packet.broadcast = packet.receiver == self.BROADCAST 
        
        
        # Send the signal
        # ============================
        logger.debug("SignalComms: [%s] Sending signal[%s] to [%s]" % (self.ID,signal_name,receiver))
        self.emit(SIGNAL(SCOPEPY_SIGNAL),packet)
        
        
        
        
    
        
        
    def relayComms(self,signal_name,receiver,*args,**kwargs):
        """
        Send a signal to the receiver and ask it to relay the packet to its
        own receivers.
        
        Note: This is how to communicate between panels in ScopePy
        
        Inputs
        ---------
        signal_name : str
            Name of signal that is being sent
            
        receiver : str
            Name label of receiver where the packet is being sent
            
        *args : arguments to be passed to signal function
        
        **kwargs : keyword arguments to be sent to signal function.
            
        HEALTH WARNING: CAUSES FATAL CRASHES DON'T USE
        TODO : FIX THIS!!!!!!!!!
        
        """
        
        # Make packet
        # ========================
        packet = SignalPacket()
        packet.name = signal_name
        packet.sender = whoCalledMe()
        packet.receiver = receiver
        packet.args = args
        packet.kwargs = kwargs
        packet.relay = True
        
        
        
        # Send the signal
        # ============================
        logger.debug("SignalComms: [%s] Sending signal[%s] to [%s]" % (self.ID,signal_name,receiver))
        self.emit(SIGNAL(SCOPEPY_SIGNAL),packet)
        
        # This will send the signal to all receivers
        
        
        
    def relayCommsPacket(self,signal_packet):
        """
        Re-send a packet to the receivers of this SignalComms instance
        
        Inputs
        --------
        signal_packet : SignalPacket() instances
            packet to forward on
            
        """
        signal_name = signal_packet.name
        receiver = signal_packet.receiver
        
        logger.debug("SignalComms: [%s] Relaying signal[%s] to [%s]" % (self.ID,signal_name,receiver))
        self.emit(SIGNAL(SCOPEPY_SIGNAL),signal_packet)
        
    
    
    
    def receiveComms(self,signal_packet):
        
        assert isinstance(signal_packet,SignalPacket),"SignalComms: Received unidentified packet"
        
        
        logger.debug("SignalComms: [%s] Receiving signal[%s] from [%s]" % (self.ID,signal_packet.name,signal_packet.sender))
        
        # Check for a broadcast
        if signal_packet.broadcast and signal_packet.name in self._actions:
            logger.debug("SignalComms: [%s] ACCEPTING BROADCAST signal[%s] from [%s]" % (self.ID,signal_packet.name,signal_packet.sender))
            # Run the function
            self._actions[signal_packet.name](*signal_packet.args,**signal_packet.kwargs)
            return
            
        # Check the signal is for me
        if signal_packet.receiver != self.ID and signal_packet.relay == False:
            # Signal is for somebody else
            logger.debug("SignalComms: [%s] IGNORING signal[%s] from [%s]" % (self.ID,signal_packet.name,signal_packet.sender))
            return
            
        # Check if the signal is to be relayed
        elif signal_packet.receiver != self.ID and signal_packet.relay == True:
            # Signal is to be relayed on to my receivers
            logger.debug("SignalComms: [%s] RELAYING signal[%s] from [%s]" % (self.ID,signal_packet.name,signal_packet.sender))
            self.relayCommsPacket(signal_packet)
            return
            
        
        if signal_packet.name in self._actions:
            logger.debug("SignalComms: [%s] ACCEPTING signal[%s] from [%s]" % (self.ID,signal_packet.name,signal_packet.sender))
            # Run the function
            self._actions[signal_packet.name](*signal_packet.args,**signal_packet.kwargs)
            
            
    
    def connectSignal(self,receiver):
        
        # TODO : This might be redundant
        #dest = self._receivers[receiver].receive
        #self.connect(self,SIGNAL(SCOPEPY_SIGNAL),dest,packet)
        pass
    
    
    
    

#==============================================================================
#%% Functions
#==============================================================================

def whoCalledMe():
    """
    Black magic function for finding who called the function that called
    whocalledme()
    """
    
    return inspect.stack()[2][3]
