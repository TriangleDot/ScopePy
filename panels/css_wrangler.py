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
import re

# Third party libraries
import numpy as np

from PyQt4.QtCore import *
from PyQt4.QtGui import *

# My libraries
import ScopePy_panels as panel
import ScopePy_widgets as wid
import simpleQt as sqt

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
        
        # Load CSS file for current theme
        # ====================================
        #filename = os.path.join(self.API.basepath,"ScopePy_styles.css")

        filename = self.API.getThemePath(self.API.preferences.theme)        
        
        with open(filename, "r") as f:
            self.default_stylesheet = f.read()
            
    
        # Store current path
        path,css_file = os.path.split(filename)
        self.currentPath = path
        
        
        
        # Make the widgets
        # ==================================
        
        self.themeName = QLabel(filename)
        self.cssEdit = QPlainTextEdit()
        self.cssEdit.setMinimumSize(700,500)
        self.cssEdit.setPlainText(self.default_stylesheet)
        
        # Find and replace
        self.findLineEdit = QLineEdit()
        self.replaceLineEdit = QLineEdit()
        replaceAllButton = QPushButton('Replace all')
        
        self.connect(self.findLineEdit,SIGNAL("returnPressed()"),self.findButton_clicked)
        
        
        # Colour selector widget
        self.colourPicker = wid.colorpicker()
        
        # Example buttons
        self.updateButton = QPushButton("&Update")
        defaultButton = QPushButton("Set back to default")
        dumpButton = QPushButton("Dump CSS")
        saveButton = QPushButton("Sa&ve CSS")
        openButton = QPushButton("&Open CSS")
        
        self.connect(self.updateButton,SIGNAL("clicked()"),self.changeColour)
        self.connect(defaultButton,SIGNAL("clicked()"),self.setDefault)
        self.connect(dumpButton,SIGNAL("clicked()"),self.dumpCSS)
        self.connect(saveButton,SIGNAL("clicked()"),self.saveCSS)
        self.connect(openButton,SIGNAL("clicked()"),self.openCSS)
        
        
        # Panel layout code goes here
        # =============================
     
        self.position(
            [
            [self.themeName,self.updateButton],
            [QLabel("Find"),self.findLineEdit],
            [QLabel("Replace"),self.replaceLineEdit],
            [sqt.empty(),replaceAllButton],
            [self.cssEdit,self.colourPicker],
            [defaultButton,dumpButton],
            [openButton,saveButton]
            ])
        
        
        
        
        # Add layout to master widget [Mandatory]
        # ========================================
        # mandatory
        #self.setLayout(panelLayout)
        
        # Check preferences
        # =====================
        if self.preferences is None:
            print("Test Panel: has no preferences")
        else:
            print("Test Panel: Preferences are here")
        
        
    def setFkeys(self):
        
        self.Fkeys = [
                     ['F8','Find',self.focus_find],
                     ]
        

    # User defined functions go here
    # ==============================================

    def changeColour(self):
        
        # Get text
        css = self.cssEdit.document().toPlainText()
        
        self.API.setThemeStyleSheet(css)
        
    
    
    def dumpCSS(self):
        
        # Get text
        css = self.cssEdit.document().toPlainText()

        print("\nCSS dump")
        print("*"*70)
        print(css)        
        print("*"*70)
        
    
    def setDefault(self):
        self.cssEdit.setPlainText(self.default_stylesheet)
        
        
    
    def saveCSS(self):
        """
        Save CSS file
        
        """
        
        path = self.currentPath
        
        formatString = "CSS files (*.css)"
        pathAndFilename = QFileDialog.getSaveFileName(self,"Save CSS to file",
                                               path,formatString)
                                               

        
        if not pathAndFilename:
            return
            
        # Get CSS
        css = self.cssEdit.document().toPlainText()
        
        with open(pathAndFilename,'w') as file:
            file.write(css)
        
        # Update current path
        path, filename = os.path.split(pathAndFilename)
        self.currentPath = path
        
        self.themeName.setText(pathAndFilename)
        
        
    def openCSS(self):
        """
        Open CSS file
        
        """
        
        path = self.currentPath
        
        formatString = "CSS files (*.css)"
        pathAndFilename = QFileDialog.getOpenFileName(self,"Open CSS file",
                                               path,formatString)

        
        if not pathAndFilename:
            return
            
        # Get CSS
        
        
        with open(pathAndFilename,'r') as file:
            css = file.read()
            
        self.cssEdit.setPlainText(css)
        
        # Update current path
        path, filename = os.path.split(pathAndFilename)
        self.currentPath = path
        
        self.themeName.setText(pathAndFilename)
        
        # Update colours
        self.changeColour()
        
        
    # ------------------------------------------------------------------------
    # Find and replace
    # ------------------------------------------------------------------------
    def focus_find(self):
        self.findLineEdit.setFocus()
        
        
    @property
    def __text(self):
        return self.cssEdit.document().toPlainText()
        
    @__text.setter
    def __text(self,text):
        self.cssEdit.setPlainText(text)
        
        
    def makeRegex(self):
        findText = self.findLineEdit.text()      
        return re.compile(findText, flags)


    
    def findButton_clicked(self):
        self.cssEdit.moveCursor(QTextCursor.Start)
        findText = self.findLineEdit.text()  
        self.cssEdit.find(findText)
        self.cssEdit.setFocus()
        
        
    
    def replaceButton_clicked(self):
        regex = self.makeRegex()
        self.__text = regex.sub(self.replaceLineEdit.text(),
                                self.__text, 1)
        

    
    def replaceAllButton_clicked(self):
        regex = self.makeRegex()
        self.__text = regex.sub(self.replaceLineEdit.text(),
                                self.__text)
    




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


__panels__ = {"CSS Wrangler":panel.PanelFlags(TestPanel,
                                                  single_instance=True,
                                                  open_on_startup=False,
                                                  location='main_area')}