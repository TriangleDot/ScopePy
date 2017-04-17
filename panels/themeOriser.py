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
import random

# Third party libraries
import numpy as np

from PyQt4.QtCore import *
from PyQt4.QtGui import *

# My libraries
import ScopePy_panels as panel
import simpleQt as sqt

#==============================================================================
#%% Constants
#==============================================================================



#==============================================================================
#%% Class definitions
#==============================================================================

class TestPanel(panel.PanelBase):
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
        self.testButton1 = QPushButton("Test button 1")
        self.testButton1.setIcon(QIcon('/home/john/Documents/Python/Projects/ScopePy_checkouts/ScopePy_reorg/images/data_source_folder.png'))
                
        
        testButton2 = QPushButton("Change button colour [C]")
        testButton2.setShortcut(QKeySequence("C"))
        self.connect(testButton2,SIGNAL("clicked()"),self.changeColour)
        
        
        
        
        
        # Add to layout
        panelLayout.addWidget(self.testButton1)
        panelLayout.addWidget(testButton2)
        
        
        
        
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
        
        

    # User defined functions go here
    # ==============================================

    def changeColour(self):
        
        css_template = """QPushButton{background:%s}"""
        
        colours = ['white','black','yellow','blue','red']
        
        css = css_template % colours[random.randint(0,len(colours)-1)]
        
        self.testButton1.setStyleSheet(css)
    
    




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


__panels__ = {"themeOriser":panel.PanelFlags(TestPanel,
                                                  open_on_startup=False,
                                                  location='main_area')}