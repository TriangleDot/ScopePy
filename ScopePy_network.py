# -*- coding: utf-8 -*-
"""
Created on Sun May 25 20:38:12 2014

@author: john

Scope Py Server/Client interface
=================================

Contains the functions to perform the networking side of the Scope Py application.

Version
==============================================================================
$Revision:: 33                            $
$Date:: 2015-04-25 09:08:23 -0400 (Sat, 2#$
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


#=============================================================================
#%% Imports
#=============================================================================

import socket
import logging

from qt_imports import *

import numpy as np


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



#=============================================================================
#%% Constants
#=============================================================================


# Magic number for identifying Scope Py packets
MAGIC_NUMBER = 7616893

# Packet type identifiers
DATA_PACKET = 4001
COMMAND_PACKET = 3456

# uint64 size in bytes
SIZEOF_UINT64 = 8

SOCKET_PORT = 63406

DEBUG = True


#=============================================================================
#%% Data Packet Constructor
#=============================================================================
#Functions for packaging arrays of numbers to be sent to the scope GUI



def makeDataPacket(channelLabel,xdata,ydata,columnNamesList = None):
    """
    Convert a numpy array into a packet for sending to Scope Py GUI

    Inputs
    ------
    channelLabel = Label for scope channel  [string]
    xdata,ydata = input data may list or 1D arrays
    columnNamesList = list of column names

    Outputs
    -----------
    Packet in string form

    The format:
    * Packet type number [UINT16] 0-65536
    * No. rows [UINT64]
    * No. columns [UINT64]
    * length of column name text [UINT64]
    * Column name text comma delimited [Bytes]
    * Data - 2D array float64 converted to byte string

    """

    # Get shape of array
    # ----------------------

    # Check size of input data
    assert len(xdata)==len(ydata), "x and y data must be the same length"

    # Create numpy array from input data
    # make sure the data is arranged in columns
    array_in = np.array([xdata,ydata]).transpose()


    # Get dimensions
    nRows,nCols = array_in.shape

    # Check Column names
    # ----------------------
    if columnNamesList == None:
        # Assign default column names
        # 'dataset1', 'dataset2' etc
        columnNamesList = []
        for iCol in range(nCols):
            columnNamesList.append('dataset%d' % iCol+1)

    # Check column names list is same length as number of columns
    assert len(columnNamesList)==nCols, "Column names list does not have the same number of entries as there are columns"

    # Add channel Label to column list
    # want to put all strings to be transmitted in the same place
    columnNamesList.insert(0,channelLabel)

    # Construct the data packet
    # --------------------------
    # Make everything into a string and then pack it together

    # initialise packet list
    dataPacket = []

    # Add Packet type as 64 bit unsigned integer
    dataPacket.append( np.uint64(DATA_PACKET).tostring() )

    # Add Number of rows as 64 bit unsigned integer
    dataPacket.append( np.uint64(nRows).tostring() )

    # Add Number of columns as 64 bit unsigned integer
    dataPacket.append( np.uint64(nCols).tostring() )

    # Add Column names

    # Package the column names into a comma delimited list
    # Add the length of the column name package first and then the list itself.
    colNamePackage = ','.join(columnNamesList)

    # Add length of package as 64 bit int
    dataPacket.append(np.uint64(len(colNamePackage)).tostring() )

    # Add column name package as bytes
    dataPacket.append(colNamePackage.encode())

    # Add data
    dataPacket.append( np.float64(array_in).tostring())

    # Return byte string packet by joining all the items in the list
    return b''.join(dataPacket)

def getPacketType(packet):
    """ packetType,remainingPacket = getPacketType(packet)

    Read first unit64 from unwrapped packet string to identify which
    packet has been sent. Then return the rest of the packet for extraction
    by other functions

    Input
    --------
    packet = byte string packet

    Outputs
    ----------
    packetType = numerical packet type as defined at top of this file
    remainingPacket = packet with type stripped off

    """

    packetType = np.fromstring(packet[0:SIZEOF_UINT64],dtype = 'uint64')

    return int(packetType),packet[SIZEOF_UINT64:]



def extractDataPacket(packet):
    """
    Extract 2D array data from packet

    Inputs
    --------
    packet = byte string packet as returned by by getPacketType

    Outputs
    --------
    (channelNumber,array_out) = tuple of outputs

    Where
        channelLabel : str
            Scope channel to add data to
        array_out = 2D numpy recarray with column names included

    """

    # Extract integer data (No. Rows, columns and header string)
    # -----------------------------------------------------------------------
    # Get all 4 numbers in one shot
    # Gives array with [Channel, No. Rows,No. Cols,Length of Column header string]

    nH = 3 # Number of integers to extract first

    numData = np.fromstring(packet[0:SIZEOF_UINT64*nH],dtype = 'uint64')
    nRows = numData[0]
    nCols = numData[1]
    headerLength = int(numData[2])


    # Extract header
    # ----------------
    # Slice out header, convert from bytes to string and separate by delimiters
    headerList = packet[SIZEOF_UINT64*nH:SIZEOF_UINT64*nH+headerLength].decode().split(',')

    # Extract channel label as the first item
    channelLabel = headerList[0]

    # Extract the numerical data
    # ---------------------------
    # extract the remaining string and convert to float64
    # this produces a 1D array
    array_out = np.fromstring(packet[SIZEOF_UINT64*nH+headerLength:],dtype='float64')

    # resize to original dimensions
    array_out = array_out.reshape((nRows,nCols))

    # convert to recarray and add column headers
    recarray_out = np.core.records.fromarrays(array_out.transpose(),
                                             names = headerList[1:])

    return (channelLabel,recarray_out)



#=============================================================================
# %% Client side for sending data
#=============================================================================


def wrapDataPacket(dataPacket):
    """ Wrap the data packet for sending over TCIP connection
    This just adds the length of the total packet to the front of
    the data packet. The server can then read this first and will
    then know how long to read data from the connection.

    Input
    ------
    dataPacket : str or bytes
        output of makeDataPacket()

    """

    # Convert to bytes if necessary
    # -----------------------------
    if not isinstance(dataPacket,bytes):
        dataPacket = dataPacket.encode()

    # Get length of packet
    # ------------------------
    pkLen = len(dataPacket)

    # Check for empty packets
    # return without error for now

    if pkLen == 0:
        return


    # Add to packet
    # ------------------------
    # Add the total length of the packet including the size of the integer
    # that is being added
    wrappedPacket = b''.join([np.uint64(pkLen+SIZEOF_UINT64).tostring(),dataPacket])

    # Return bytes packet
    return wrappedPacket



def sendPacket(hostIP,dataPacket):
    """ Send the packet over a TCIP link to the GUI server

    Wrap data packet and send. Then close connection.

    Inputs
    -----------
    hostIP = IP address of host
    dataPacket = output of makeDataPacket()
    TODO : May change this to array in future

    Outputs
    ---------
    successFlag = True if packet sent, otherwise False

    """

    # Wrap the data packet
    # ----------------------------
    wrappedPacket = wrapDataPacket(dataPacket)

    # Check it worked, otherwise return
    if wrappedPacket == None:
        return False


    # Send packet
    # ------------------------------

    # Create socket object
    s = socket.socket()

    # Connect socket to port on server
    s.connect((hostIP, SOCKET_PORT))


    if DEBUG:
        print("SendPacket:Connected to server")
        print("SendPacket:Peername : ",s.getpeername())
        print("SendPacket:Socket name : ",s.getsockname())
        print("SendPacket: Packet length = %d" % len(wrappedPacket))


    # Send command as bytes
    s.send(wrappedPacket)

    #  Read reply
    reply = readPacket(s)
    logger.debug("SendPacket: Reply from server [%s]" % reply)

    # Close the socket
    s.close()


    logger.debug("SendPacket: Connection is closed")

    # Return if everything worked
    # return reply?
    return reply



def send2scope(channel_name,x_data,y_data,x_label,y_label,scope_IP=None):
    """
    Send x,y data to a scope channel

    This is the basic "plot" command

    Inputs
    --------
    channel_name : str
        The channel name under which the data will appear in on the scope
        screen.

    x_data : list or 1D numpy array
        x axis data

    y_data : list or 1D numpy array
        y axis data

    x_label : str
        label for x axis

    y_label : str
        label for y axis

    scope_IP : str
        IP address of the computer where ScopePy is running.
        If not specified then it is assumed that it is the same computer.


    Outputs
    --------
    success : bool
        returns True if a successful transfer

    """

    # Get Scope IP address
    # ----------------------
    if not scope_IP:
        scope_IP = socket.gethostname()


    # Validate data TODO
    # -------------------

    assert len(x_data)==len(y_data), "ScopePy: x and y data are different lengths"


    # Make data packet
    # ------------------
    dataPacket = makeDataPacket(channel_name,x_data,y_data,[x_label,y_label])


    # Send data to scope
    # -------------------
    return sendPacket(scope_IP,dataPacket)


#=============================================================================
#%% Test server
#=============================================================================


def testServer():
    """
    Simple non-QT4 server for testing the client functions

    Prints output to console for debugging

    TODO : Is out of date with packets now

    """

    # Setup the socket
    # -------------------------------------------------
    s = socket.socket()         # Create a socket object
    host = socket.gethostname() # Get local machine name
    s.bind((host, SOCKET_PORT))        # Bind to the port

    print("Initialising ScopePy test server\n---------------------")


    s.listen(5)                 # Now wait for client connection.


    # Main Server loop
    # -----------------------------------------------
    while True: # Loop forever, listening for client connections
       print("Listening\n")

       c, addr = s.accept()     # Establish connection with client.
       print('Got connection from', addr)

       # Read packet from connection
       # TODO : this should be passed to a thread
       readPacket(c)


       # Close the connection
       # TODO should this be done here or in readPackets ?

       c.close()
       print("Closing connection")



def testPacket(channel = "Test Packet"):
    """ Generate a test packet for testing client/server connection

    Input
    ------
    channel = string for channel name

    """



    # Make standard data array
    x = np.arange(0,10)
    y = (x**2)*1.27 + np.random.random_sample(x.shape)*5

    columnNamesList = ['x axis text','y axis text']

    return makeDataPacket(channel,x,y,columnNamesList)




#=============================================================================
#%% Server Packet reading
#=============================================================================


def readDataPacket(conn):
    """
    Read packet from client connection.

    First get the length of the data, then read the rest of the packet

    Input
    -----------
    conn : socket
        socket passed from server

    Output
    ----------


    """

    if DEBUG:
        print("Reading packet ...")

    # Read packet length
    # ---------------------
    # Keep reading until we have the first uint64 number from
    # the packet
    packet = b''

    while len(packet) < SIZEOF_UINT64:
        # Get data from socket
        chunk = conn.recv(SIZEOF_UINT64-len(packet))

        # If we received nothing then assume socket
        # has been lost
        if chunk == b'':
            raise RuntimeError("socket connection broken : reading packet length")

        # Data received - add it to the packet
        packet = packet + chunk

    # Packet should now contain the length of the total packet
    # decode the length
    packetLength = np.fromstring(packet[0:SIZEOF_UINT64],dtype = 'uint64')

    if DEBUG:
        print("\tPacket Length = %d" % packetLength)
        print("\tReading rest of packet ...")

    # Read the rest of the packet
    # -------------------------------
    while len(packet) < packetLength:
        # Get data from socket
        chunk = conn.recv(packetLength-len(packet))

        # If we received nothing then assume socket
        # has been lost
        if chunk == b'':
            raise RuntimeError("socket connection broken : reading packet")

        # Data received - add it to the packet
        packet = packet + chunk

    # TODO : translate packet back into numbers
    if DEBUG:
        print("\tPacket received [%d bytes]:" % len(packet))
        #print(packet)

    # Extract data from packet
    array_out = extractDataPacket(packet[SIZEOF_UINT64:])

    if DEBUG:
        print("Numerical data extracted:")
        print(array_out)



def readPacket(conn):
    """
    Read packet from socket.

    First get the length of the data, then read the rest of the packet

    Input
    -----------
    conn = socket passed from server

    Output:
    ----------
    packet : str
        received packet in string form

    """

#    # Read Magic number
#    # ---------------------
#    # Keep reading until we have the first uint64 number from
#    # the packet
#    packet_magic_number = b''
#
#    while len(packet_magic_number) < SIZEOF_UINT64:
#        # Get data from socket
#        chunk = conn.recv(SIZEOF_UINT64-len(packet_magic_number))
#
#        # If we received nothing then assume socket
#        # has been lost
#        if chunk == b'':
#            raise RuntimeError("socket connection broken : reading magic number")
#
#        # Data received - add it to the packet
#        packet_magic_number = packet_magic_number + chunk
#
#    # Check this is the correct number
#    # if not then drop the connection
#    magic_number = np.fromstring(packet_magic_number[0:SIZEOF_UINT64],dtype = 'uint64')
#
#    if magic_number != MAGIC_NUMBER:
#        if DEBUG:
#            print("Unknown packet [%d] : dropping connection" % magic_number)
#        return
#
#
#    if DEBUG:
#        print("Reading packet ...")

    # Read packet length
    # ---------------------
    # Keep reading until we have the first uint64 number from
    # the packet
    packet = b''

    while len(packet) < SIZEOF_UINT64:
        # Get data from socket
        chunk = conn.recv(SIZEOF_UINT64-len(packet))

        # If we received nothing then assume socket
        # has been lost
        if chunk == b'':
            raise RuntimeError("readPacket: socket connection broken : reading packet length")

        # Data received - add it to the packet
        packet = packet + chunk

    # Packet should now contain the length of the total packet
    # decode the length
    packetLength = np.fromstring(packet[0:SIZEOF_UINT64],dtype = 'uint64')

    logger.debug("readPacket: Packet Length = %d" % packetLength)
    logger.debug("readPacket: Reading rest of packet ...")

    # Read the rest of the packet
    # -------------------------------
    while len(packet) < packetLength:
        # Get data from socket
        chunk = conn.recv(packetLength-len(packet))

        # If we received nothing then assume socket
        # has been lost
        if chunk == b'':
            raise RuntimeError("socket connection broken : reading packet")

        # Data received - add it to the packet
        packet = packet + chunk



    logger.debug("readPacket: Packet received [%d bytes]:" % len(packet))
    if DEBUG:
        logger.debug("Packet=\n%s" % packet[SIZEOF_UINT64:])

    return packet[SIZEOF_UINT64:].decode('utf-8')

#=============================================================================
#%% QT4 Server
#=============================================================================


class TcpServer(QTcpServer):
    """ Derived server class used to overload the 'incomingConnection' method
    so that it points to a socket class that handles the reading of
    custom packets

    Ref : Mark Summerfield, "Rapid GUI Programming in Python and QT4"

    """

    def __init__(self,parent=None):
        # Initialise the base class
        super(TcpServer,self).__init__(parent)

    def incomingConnection(self,socketId):
        """ Re-implementation of method.
        This gets called when a connection is available at the server
        """

        if DEBUG:
            print("IncomingConnection detected")

        # Straight from the book
        socket = Socket(self,upLoadFunction = self.uploadDataArray)
        socket.setSocketDescriptor(socketId)


    def uploadDataArray(self,dataArray):
        """ Emit a signal with the uploaded data array in order to
        send the data back to the main GUI.

        This is the method of getting the data out of the server and back
        to the main GUI.

        The basic flow is:
        * Server receives connection
        * Server passes connection to Socket class, plus a reference to this function
        * Socket class reads the data and converts it to an output form
        * Socket calls this function, which makes the server emit a signal
          back to the main GUI.

        It's a bit convoluted,but it was all I could think of for passing the
        data back up!
        """

        if DEBUG:
            print("Sending UpLoad data array signal")

        self.emit(SIGNAL("UpLoadChannelData"), dataArray)



class Socket(QTcpSocket):
    """
    Custom socket handler for our packet format

    """

    def __init__(self, parent=None,upLoadFunction=None):
        super(Socket, self).__init__(parent)

        # Connect socket to custom read response method
        self.connect(self, SIGNAL("readyRead()"),self.readPacket)
        self.connect(self, SIGNAL("disconnected()"), self.deleteLater)
        self.nextBlockSize = 0
        self.upLoadFunction = upLoadFunction


    def readPacket(self):
        """ Read wrapped packet using QT4 functions

        Output
        ------
        dataPacket = byte string packet ready for extractDataPacket()

        """
        if DEBUG:
            print("Reading packet")

        # Create a stream object to read bytes into
        # ------------------------------------------
        stream = QDataStream(self)
        stream.setVersion(QDataStream.Qt_4_2)

        # Read first uint64 from packet to get the packet length
        # -------------------------------------------------------
        # Wait until we have enough bytes to make a 64bit Unsigned integer
        if self.nextBlockSize == 0:
            if self.bytesAvailable() < SIZEOF_UINT64:
                print("\tBytes less than SIZEOF_UINT64")
                # Not enough bytes accumulated, so return
                return

            # Read in enough bytes to make a uint64
            plBytes = stream.readRawData(SIZEOF_UINT64)
            print("Bytes read:")
            print(plBytes)

            # Convert bytes to uint64 using numpy
            packetLength = int(np.fromstring(plBytes, dtype=np.uint64))

            # Read the size of the rest of the packet
            self.nextBlockSize = packetLength - SIZEOF_UINT64

            print("Packet length = %i" % packetLength)
            print("Reading rest of packet [%i]" % self.nextBlockSize)

        # Read rest of packet
        # --------------------------------------------
        # Wait for all the bytes to arrive
        if self.bytesAvailable() < self.nextBlockSize:
            print("\tBytes less than packet size")
            return

        # Read the packet
        # Read in the raw bytes
        packet = stream.readRawData(self.nextBlockSize)

        # Get the packet type
        packetType,remainingPacket = getPacketType(packet)

        if DEBUG:
            print("\tPacket type = %d" % packetType)

        # Select the action for each packet type
        if packetType == DATA_PACKET:


            # Extract numerical data and channel label
            data4scope = extractDataPacket(remainingPacket)


            if DEBUG:
                print("Data packet received [size = %d bytes]" % len(remainingPacket))
                print(remainingPacket)
                print("\n\nNumerical data is:")
                print(data4scope[1])

            # Upload the array to calling function
            self.upLoadFunction(data4scope)



#=============================================================================
#%% QT4 Threaded Server
#=============================================================================
# Threaded version of TcpServer
# intended as the main server when complete
#
# ref: Mark Summerfield, Rapid GUI programming with Python & QT4, Chap 19


class ThreadedTcpServer(QTcpServer):



    def __init__(self, parent=None,channel_lock=None,
                 upload_function=None):

        super(ThreadedTcpServer, self).__init__(parent)

        #self.uploadFunction = None

        # Thread locking variable for channel dictionary
        self.channel_lock = channel_lock
        self.upload_function = upload_function



    def incomingConnection(self, socketId):

        # Create a thread to process the incoming socket
        thread = SocketThread(socketId, self,upLoadFunction=self.uploadDataArray,
                              lock=self.channel_lock,
                              commandUploadFunction=self.sendCmd2API)

        self.connect(thread, SIGNAL("finished()"),
                     thread, SLOT("deleteLater()"))

        # Start the thread - eventually executes the threads run method
        thread.start()


    def uploadDataArray(self,dataArray):
        """ Emit a signal with the uploaded data array in order to
        send the data back to the main GUI.

        This is the method of getting the data out of the server and back
        to the main GUI.

        The basic flow is:
        * Server receives connection
        * Server passes connection to Socket class, plus a reference to this function
        * Socket class reads the data and converts it to an output form
        * Socket calls this function, which makes the server emit a signal
          back to the main GUI.singlePacket(hostIP)

        It's a bit convoluted,but it was all I could think of for passing the
        data back up!
        """


        logger.debug("Sending UpLoad data array signal")

        self.emit(SIGNAL("UpLoadChannelData"), dataArray)



    def sendCmd2API(self,socket,command_packet):
        """
        Emit signal to ScopePy API

        This is to pass a command packet to the main program

        Basic flow:
        * Command comes in to server
        * Server receives packet on a thread and sends it to this function
        * Signal is emitted to main program
        * Ends the thread

        Input
        ------
        socket : QTcpSocket
            connection to the client

        command_packet : byte string
            raw command packet

        TODO : pass socket here

        """

        logger.debug("Send command from server to main API")
        self.emit(SIGNAL("UpLoadCommandPacket"),socket,command_packet)



class SocketThread(QThread):
    """
    Class for handling incoming data in a separate thread

    """



    # TODO : Could try a QMutex instead.

    def __init__(self, socketId, parent,upLoadFunction=None,lock=None,
                 commandUploadFunction=None):
        super(SocketThread, self).__init__(parent)
        self.socketId = socketId



        # Store upload function
        self.upLoadFunction = upLoadFunction

        # Channel dictionary thread locker
        self.channel_lock = lock

        # Command upload
        self.commandUploadFunction = commandUploadFunction



    def run(self):
        """
        Process the data from the socket

        """

        # Create a socket and check its ID
        # --------------------------------------
        socket = QTcpSocket()
        if not socket.setSocketDescriptor(self.socketId):
            self.emit(SIGNAL("error(int)"), socket.error())
            return

        # Read packet data from socket
        # --------------------------------

        while socket.state() == QAbstractSocket.ConnectedState:


            nextBlockSize = 0

            # Create a stream to read the packet
            stream = QDataStream(socket)
            stream.setVersion(QDataStream.Qt_4_2)

            # Read packet length from first 64bit integer
            if (socket.waitForReadyRead() and
                socket.bytesAvailable() >= SIZEOF_UINT64):

                # Read the 64 bits in byte form
                plBytes = stream.readRawData(SIZEOF_UINT64)

                # Convert bytes to uint64 using numpy
                packetLength = int(np.fromstring(plBytes, dtype=np.uint64))

                # Read the size of the rest of the packet
                nextBlockSize = packetLength - SIZEOF_UINT64

            else:
                #self.sendError(socket, "Cannot read client request")
                return


            # Read in the rest of the packet
            # ------------------------------------------
            # Wait for all the data to accumulate
            # this is required for large amounts of data
            while socket.bytesAvailable() < nextBlockSize:

                if not socket.waitForReadyRead(60000):
                    logger.debug("Socket closed while reading client payload data")
                    return



            # Read the packet
            # Read in the raw bytes
            packet = stream.readRawData(nextBlockSize)


            # Process the packet
            # ---------------------------

            # Get the packet type
            packetType,remainingPacket = getPacketType(packet)


            logger.debug("Incoming packet : Type = %d" % packetType)


            # Select the action for each packet type
            if packetType == DATA_PACKET:

                # TODO : send reply back to client
                # something like this:
                socket.writeData(wrapDataPacket("Packet received"))

                # Extract numerical data and channel label
                data4scope = extractDataPacket(remainingPacket)



                logger.debug("Data packet received [size = %d bytes]" % len(remainingPacket))
                logger.debug("Data label : [%s]" % data4scope[0])


                # Upload data - lock for this thread
                # ++++++++++++++++++++++++++++++++++++++
                try:
                    self.channel_lock.lockForWrite()


                    logger.debug("Locking channel dict for [%s]" % data4scope[0])

                    # Upload the array to calling function
                    self.upLoadFunction(data4scope)

                finally:
                    self.channel_lock.unlock()
                    logger.debug("unlocking channel dict for [%s]\n" % data4scope[0])

                    # Close the socket
                    # TODO



            elif packetType == COMMAND_PACKET:
                logger.debug("A command packet has arrived at the server")

                dummy = "dummy"
                self.commandUploadFunction(dummy,remainingPacket)

                socket.writeData(wrapDataPacket("success|dummy return"))
                # TODO pass socket back as well
