# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 20:53:48 2015

@author: john

ScopePy Keyboard shortcut library
=====================================
Central place for defining keyboard shortcut infrastructure


Version
==============================================================================
$Revision:: 54                            $
$Date:: 2015-06-28 10:25:47 -0400 (Sun, 2#$
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
import logging

# Third party libraries
import numpy as np

from qt_imports import *


# My libraries
from ScopePy_utilities import minidir

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


#==============================================================================
#%% Constants
#==============================================================================



#==============================================================================
#%% Class definitions
#==============================================================================

class Shortcuts():
    """
    Class for holding a collection of keyboard shortcut reference to the name
    of an action. Basically it's a dictionary of keyboard shortcuts with some
    extra functions

    Example
    ----------
    mainShortcuts = ShortCuts()
    mainShortcuts['NewPlot'] = 'Ctrl+n'
    shortCut = mainShortcuts['NewPlot']
    shortCut = mainShortcuts.NewPlot

    event = QKeyPressEvent()
    action = mainShortcuts.getActionFromEvent(event)

    """

    def __init__(self):


        # Main dictionary for holding shortcuts
        # key = action name
        # item = QKeySequence
        self.action2key = {}

        # Reverse lookup dictionary
        self.key2action = {}

    def __str__(self):

        lines = []

        for action,keySeq in self.action2key.items():
            lines.append("%s : %s" % (action,keySeq.toString()))

        return '\n'.join(lines)


    def __repr__(self):

        return "Shortcuts() object"


    def addShortCut(self,actionName,shortcut):
        """
        Add new shortcut to internal dictionary

        Inputs
        -------
        actionName : str
            Name label for the action represented by this shortcut

        shortcut : str or Qt key list
            e.g. "Ctrl+t" or Qt.CTRL+Qt.Key_T

            This will be converted into a QKeySequence

        """
        # Convert shortcut to key sequence
        if isinstance(shortcut,QKeySequence):
            keySeq = shortcut
        else:
            # Anything else just QKeySequence it
            keySeq = QKeySequence(shortcut)



        # Add to dictionaries
        self.action2key[actionName] = keySeq
        self.key2action[self.action2key[actionName].toString().lower()] = actionName

        # Try to add as an attribute
        try:
            setattr(self,actionName,self.action2key[actionName])
        finally:
            pass



    def __getitem__(self,actionName):

        assert actionName in self.action2key,"Shortcuts: Unknown action [%s]" % actionName

        return self.action2key[actionName]


    def __setitem__(self,actionName,shortcut):

        self.addShortCut(actionName,shortcut)



    def getActionFromEvent(self,event):
        """
        Check if the event is the same as any of the shortcuts contained
        in this Shortcuts() class

        Example usage
        ---------------
        >>> S = Shortcuts()
        >>> S['new'] = 'Ctrl+n'
        >>> event = QKeyEvent(QEvent.KeyPress,Qt.Key_N,Qt.ControlModifier)
        >>> S.getActionFromEvent(event)
        'new'

        """

        # Convert event into a QKeySequence string
        # ------------------------------------------
        keySeq = QKeySequence(event.modifiers()|event.key()).toString().lower()


        # Cross reference key sequence
        # ------------------------------
        if keySeq in self.key2action:
            return self.key2action[keySeq]
        else:
            return



#==============================================================================
#%% Default Keyboard shortcuts
#==============================================================================

def makeDefaultKeyboardShortcuts():
    """
    Make defaults and return in one collected variable

    """

    # Programming note:
    # --------------------
    # Would really like to use the QKeySequence.StandardKey to generate the
    # "standard" shortcuts like "Open" but doing this, for example
    #   QKeySequence(QKeySequence.Print)
    # As given in the documentation crashes the program with no explanation

    # Main window
    # ----------
    mainShortcuts = Shortcuts()
    mainShortcuts['open'] = "Ctrl+o"
    mainShortcuts['save'] = "Ctrl+s"
    mainShortcuts['newPlot'] = "Ctrl+n"
    mainShortcuts['newTab'] = "Ctrl+t"
    mainShortcuts['config'] = "Ctrl+Alt+i"
    mainShortcuts['panels'] = Qt.Key_Meta # windows key


    # Plot
    plotShortcuts = Shortcuts()
    plotShortcuts['autoscale'] = 'Ctrl+A'
    plotShortcuts['autoscale_x'] = 'Alt+X'
    plotShortcuts['autoscale_y'] = 'Alt+Y'
    plotShortcuts['pan_up'] = Qt.Key_Up
    plotShortcuts['pan_down'] = Qt.Key_Down
    plotShortcuts['pan_left'] = Qt.Key_Left
    plotShortcuts['pan_right'] = Qt.Key_Right
    plotShortcuts['zoom_in'] = 'alt+i'
    plotShortcuts['zoom_out'] = 'alt+o'
    plotShortcuts['scale_y_out'] = Qt.CTRL+Qt.Key_Up
    plotShortcuts['scale_y_in'] = Qt.CTRL+Qt.Key_Down
    plotShortcuts['scale_x_out'] = Qt.CTRL+Qt.Key_Right
    plotShortcuts['scale_x_in'] = Qt.CTRL+Qt.Key_Left


#    wholeTable = {'main':mainShortcuts,'plot':plotShortcuts}
    wholeTable = minidir()
    wholeTable['main'] = mainShortcuts
    wholeTable['plot'] = plotShortcuts

    return wholeTable
