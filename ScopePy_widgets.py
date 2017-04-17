# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 21:11:38 2014

@author: john
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
import logging
import copy
import sqlite3

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from widgets.color import *

import numpy as np

#import pyqtgraph as pg

import ScopePy_channel as ch
import ScopePy_colours_and_shapes as col_shapes

#import mandatory as manargs


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

DEBUG = False

# TODO : Centralise colours and styles somewhere and make it modular
# enough that they could be customised in the future.

lineColours = col_shapes.COLOURS
lineStyles = [Qt.SolidLine, Qt.DashLine, Qt.DashDotLine, Qt.DashDotDotLine, Qt.NoPen]

# Symbols - adapted from pyqtgraph

Symbols = col_shapes.make_markers()


#=============================================================================
#%% New legendline alternative
#=============================================================================
class legendDialog(QDialog):
    def __init__(self,parent=None):
        """
Newer version of LegendLine, this dialog is to be used like this:
>>>form = legendDialog()
>>>if form.exec_():
...    print('linestyle:',form.lineStyle)
>>>"""
        super(legendDialog,self).__init__(parent)
        self.setWindowTitle('LineStyle Selector Dialog')
        mh = QVBoxLayout()
        self.stack = QStackedWidget()
        mh.addWidget(self.stack)
        bl = QVBoxLayout()
        p1 = QPushButton('>>')
        p1.clicked.connect(self.forward)
        p2 = QPushButton('<<')
        p2.clicked.connect(self.backward)
        p3 = QPushButton('Done')
        p3.clicked.connect(self.donePressed)
        bl.addWidget(p1)
        bl.addWidget(p3)
        bl.addWidget(p2)
        mh.addLayout(bl)
        self.setLayout(mh)
        self.markerSelect()
        self.lineselect()
        self.outline()
        self.stack.setCurrentIndex(0)

    def markerSelect(self):
        mw = QWidget()
        l = QVBoxLayout()
        label = QLabel('Please Select a type of marker, then select a color for the fill of the marker')
        #l.addWidget(l)
        self.markcombo = QComboBox()
        self.markcombo.addItems(['dot','square','circle','triangle','cross'])
        self.fillcolor = colorpicker()
        l.addWidget(label)
        l.addWidget(self.markcombo)
        l.addWidget(self.fillcolor)
        
        
        mw.setLayout(l)
        self.stack.addWidget(mw)

    def lineselect(self):
        mw = QWidget()
        l = QVBoxLayout(self)
        label = QLabel('Select a color for the lines')
        self.linecolor = colorpicker()
        l.addWidget(label)
        l.addWidget(self.linecolor)

        mw.setLayout(l)
        self.stack.addWidget(mw)

    def outline(self):
        mw = QWidget()
        l = QVBoxLayout(self)
        label = QLabel('Select a color for the outline of the marker')
        self.outcolor = colorpicker()
        l.addWidget(label)
        l.addWidget(self.outcolor)

        mw.setLayout(l)
        self.stack.addWidget(mw)

    def forward(self):
        index = self.stack.currentIndex()
        tobe = index+1
        if tobe == 3:
            tobe = 0

        self.stack.setCurrentIndex(tobe)

    def backward(self):
        index = self.stack.currentIndex()
        tobe = index-1
        if tobe < 0:
            tobe = 2

        self.stack.setCurrentIndex(tobe)

    def getMarkerType(self):
        txt = self.markcombo.currentText()
        if txt == 'dot':
            return '.'
        elif txt == 'square':
            return 's'

        elif txt == 'triangle':
            return '^'
        elif txt == 'circle':
            return 'c'
        elif txt == 'cross':
            return 'x'
        

    def donePressed(self):
        self.lineStyle = ch.plotLineStyle(lineColour=self.linecolor.name,marker=self.getMarkerType(),
                                          markerColour=self.outcolor.name,markerFillColour=self.fillcolor.name)
        self.accept()



        


#=============================================================================
#%% legendLine widget class definition
#=============================================================================


class legendLine(QWidget):
    """ Legend line/marker display item
    
    Displays a line with a marker, for inserting into legends or tables
    Allows changing of the colour, line style and shape of the line and the 
    marker by selecting either and rolling the mouse wheel over them.
    
    Actions are:
    Left button click - select line or marker
    
    Line options:
    roll wheel with no keys held down to change the line colour
    roll wheel with Ctrl key held down to change line style
    
    Marker options
    roll wheel with no keys to change colour
    roll wheel with Ctrl key down to change the marker shape
    
    
    """

    def __init__(self, parent=None,lineColour='#ff0000',
                 markerColour = '#0000ff',
                 markerFillColour='#ff00ff',
                 lineStyle = Qt.SolidLine):
                     
                     
        super(legendLine, self).__init__(parent)
        
        # selected flag
        self.selected = False
        self.changed = False
        
        
        # Physical lengths in pixels
        self.minBoxWidth_px = 40
        self.minBoxHeight_px = 10
        
        # Logical lengths
        self.LogicalWidth = 40.0
        self.LogicalHeight = 8
        
        # Line
        self.lineLength_lg = 30
        self.lineWidth = 1
        
        # Symbol/Marker
        self.marker = 'o'
        self.markerSize = 7
        self.markerScalingFactor = 2
        
        
        # Selection criteria
        self.lineSelectionTolerance_lg = 5
        self.lineSelected = False
        self.markerSelected = False
        
        # Colours & styles
        self.lineColour = lineColour
        self.lineColourList = incrementer(lineColours)
        self.lineDashStyle = lineStyle
        self.lineDashStyleList = incrementer(lineStyles)
        
        self.markerColour = markerColour
        self.markerColourList = incrementer(lineColours)
        
        self.markerFillColour = markerFillColour
        self.markerFillColourList = incrementer(lineColours)
        
        self.markerList = incrementer(list(Symbols.keys()))
        
        
        # Sizing
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,
                                       QSizePolicy.Fixed))
        #self.setMinimumSize(self.minimumSizeHint())
        
        # Focus 
        self.setFocusPolicy(Qt.WheelFocus)
        self.setMouseTracking(True)
        
        # Status bar function
        self.setStatusTip( "Click on line or marker, roll mouse wheel to change colour, CTRL+Mouse wheel to change shape, SHIFT + Mouse wheel to change marker outline colour")
        
        # Tool tip
        self.setToolTip("Line styles - double click or F2 to edit")
        
        

        self.update()
        
        
    def setLineStyles(self,lineStyleObject):
        """ Set all line colours and styles in one shot using a
        container such as the plotLineStyle class in ScopePy_channels.
        
        This is a convenience function for other parts of ScopePy
        
        Input
        ---------
        lineStyleObject = object with attributes:
            lineColour
            lineDashStyle
            marker
            markerColour
            markerFillColour
        """
        
        self.lineColour = lineStyleObject.lineColour
        self.lineDashStyle = lineStyleObject.lineDashStyle
        self.markerColour = lineStyleObject.markerColour
        self.marker = lineStyleObject.marker
        self.markerFillColour = lineStyleObject.markerFillColour   
        
        self.update()
    
    
    def getLineStyles(self):
        """ Return all line colours and styles in one shot using a
        container such as the plotLineStyle class in ScopePy_channels.
        
        This is a convenience function for other parts of ScopePy
        
        Output
        ---------
        lineStyleObject = object with attributes:
            lineColour
            lineDashStyle
            marker
            markerColour
            markerFillColour
        """
        
        lineStyleObject = ch.plotLineStyle()
        lineStyleObject.lineColour = self.lineColour 
        lineStyleObject.lineDashStyle = self.lineDashStyle 
        lineStyleObject.markerColour = self.markerColour 
        lineStyleObject.marker = self.marker 
        lineStyleObject.markerFillColour = self.markerFillColour   
        
        return lineStyleObject
        
    # Setup lineStyle as a property
    lineStyles = property(fget = getLineStyles, fset = setLineStyles)
    
    def getSelectionStatus(self):
        """ Returns the selection status of the line and marker items
        
        Outputs
        ---------
        (isLineSelected,isMarkerSelected) = boolean tuple
        """
        
        return (self.lineSelected,self.markerSelected)
        
        
    def setSelectionStatus(self,selectionFlags):
        """ Convenience function for delegates
        Sets the selected flags in one shot from outside
        
        Inputs
        ---------
        (isLineSelected,isMarkerSelected) = boolean tuple
        TODO : May not need this
        """
        
        (self.lineSelected,self.markerSelected) = selectionFlags
        
        self.update()
        
        
    selectionStatus = property(fget = getSelectionStatus, fset = setSelectionStatus)
            
        
    def sizeHint(self):
        return self.minimumSizeHint()
        
        
    def minimumSizeHint(self):
        
        return QSize(self.minBoxHeight_px,self.minBoxHeight_px)
        
        
    def mousePressEvent(self,event):
        """ Mouse clicked over widget
        Check if the line was clicked
        """
        
        if event.button() == Qt.LeftButton:
            # Check mouse coordinates
            # Convert from pixels to logical coordinates
            
            x_lg,y_lg = self.pix2logical(event.x(),event.y())
            
            # Define rectangle for line
            lineRect = QRectF(-self.lineLength_lg/2,
                             -self.lineSelectionTolerance_lg,
                             self.lineLength_lg,
                             2*self.lineSelectionTolerance_lg)
                             
            # Define rectangle for marker
            markerRect = QRectF(-2.0,-2.0,4.0,4.0)
            
            if DEBUG:
                print("--------------------\nMarker selection rectangle")
                print(markerRect)
                print('Mouse clicked at point:')
                print(QPointF(x_lg,y_lg))
                print("--------------------\n")
            
            
            # Check if mouse was clicked on the marker
            if markerRect.contains(QPointF(x_lg,y_lg)):
                self.markerSelected = not self.markerSelected
                
                if self.lineSelected == True:
                    self.lineSelected = False
                
            
            # Check if click was on the line
            #if  abs(y_lg -self.lineY_lg) <= self.lineSelectionTolerance_lg:  
            elif lineRect.contains(QPointF(x_lg,y_lg)):
                
                # invert the selected state if line was clicked on
                self.lineSelected = not self.lineSelected
                
                if self.markerSelected == True:
                    self.markerSelected = False
                
            else:
                self.lineSelected = False
                self.markerSelected = False
                
            
            self.update()
            event.accept()
            
        elif event.button() == Qt.RightButton:
            # Dump line styles to console
            print(self.lineStyles)
            
        else:
            QWidget.mousePressEvent(self,event)
            
            
    def wheelEvent(self,event):
        """ Mouse wheel turned over widget
        
        If mouse is over line or marker and the wheel is turning then
        change the colour, line style or shape
        
        See main class for the actions
        
        """
        
        # Get how much the wheel has turned
        numDegrees = event.delta()/8
        numSteps = numDegrees/15
        direction = np.sign(numSteps)
        
        
        # Get any keyboard modifiers
        modifiers = event.modifiers()
       
        # Change colours and styles according to what's selected
        # emit signals to tell other objects that the colours have changed
        if self.lineSelected and modifiers==Qt.NoModifier : # TODO : Put check on mouse coordinates as well
            self.lineColour = self.lineColourList.getNextItem(direction)
            self.changed = True
            event.accept()
            
        if self.lineSelected and modifiers==Qt.ControlModifier :
            self.lineDashStyle = self.lineDashStyleList.getNextItem(direction)
            self.changed = True 
            event.accept()
            
        elif self.markerSelected and modifiers==Qt.ControlModifier:
            self.marker = self.markerList.getNextItem(direction)
            self.changed = True
            event.accept()

            
        elif self.markerSelected and modifiers==Qt.ShiftModifier:
            self.markerColour = self.markerColourList.getNextItem(direction)
            self.changed = True
            event.accept()

            
        elif self.markerSelected and modifiers==Qt.NoModifier:
            self.markerFillColour = self.markerFillColourList.getNextItem(direction)
            self.changed = True   
            event.accept()
            
        else:
            #QWidget.wheelEvent(self,event)
            event.ignore()
            
        self.update()
        
        
    def focusOutEvent(self,event):
        """ When focus is lost, de-select everything and update
        
        This works!
        """
        
        if DEBUG:
            print('\n+++++++++++++++++++++++++++++++++++++++++++')
            print("lineLegend has lost focus")
            print("+++++++++++++++++++++++++++++++++++++++++++\n")
        
        self.lineSelected = False
        self.markerSelected = False
        
        self.update()
        self.leaveEvent(event)
            
          
          
    def leaveEvent(self,event):
        """ 
        signal end of editing
        
        """
        
        # Not exactly sure what to do with event, but it must be there
        # otherwise an error occurs
        
        if self.changed:
            self.emit(SIGNAL("LegendLineChanged"))   
        else:
            self.emit(SIGNAL("LegendLineEditFinished")) 
            
            
        
    def paintEvent(self, event=None):
        
        
        # Setup painter object
        # =================================
        painter = QPainter(self)
        
        if DEBUG:
            print("\n-------------------------------------")
            print("legendLine : paintEvent method")
            print("-------------------------------------\n")
        
        # sub contract to paint function
        self.paint(painter)
        
        

        
    def paint(self,painter,rect=None,selected=False):
        
        noRect = False # TODO : Temporary
        
        if not rect:
           noRect = True
           rect = QRect(0,0,self.width(),self.height())
                
                
        
        # Aspect ratio conversion factor
        # =============================================
        # multiply a vertical length by this to get the equivalent
        # number of pixels to the same distance in the horizontal plane
        pixConv = self.LogicalHeight*rect.width()/(self.LogicalWidth*rect.height())
        
        
        
        if DEBUG:
            print("\n-------------------------------------")
            print("legendLine : paint method")
            print("Pixel to logical = %0.4f" % pixConv)
            print("\nself.width = %d, self.height = %d" % (self.width(),self.height()))
            print("\nLegend line self rectangle")
            print(self.rect())
            print("\nSupplied rectangle:")
            print(rect)
            if noRect:
                print("<<< No rect supplied - using default>>>")
            print("-------------------------------------\n")
            
        
        # Setup painter
        # ========================
        painter.setRenderHint(QPainter.Antialiasing)
        #painter.setViewport(0,0,self.width(),self.height())
        painter.setViewport(rect)
        
        painter.setWindow(-self.LogicalWidth/2, -self.LogicalHeight/2, self.LogicalWidth, self.LogicalHeight)
        
        palette = QApplication.palette()
        handleColour = palette.highlight().color()
        backgroundColour = palette.background().color() if selected else Qt.black #palette.base().color()
        
        
        # Background
        # =========================        
        pen = QPen(Qt.SolidLine)
        pen.setWidth(1)
        pen.setColor(backgroundColour)            
        painter.setPen(pen)
        painter.setBrush(backgroundColour)
        painter.drawRect(-self.LogicalWidth/2, -self.LogicalHeight/2, self.LogicalWidth, self.LogicalHeight)
        
        
        # Line
        # ========================================================
        
        # Setup pen colours for line and draw it
        # ------------------------------------------
        pen = QPen(self.lineDashStyle)
        pen.setWidth(self.lineWidth)
        
        lineColour = QColor()
        #logger.debug("legendLine:Paint: Line colour = %s" % self.lineColour)
        lineColour.setNamedColor(self.lineColour)
        pen.setColor(lineColour)
        painter.setPen(pen)
        
        # Draw the line
        painter.drawLine(-self.lineLength_lg/2,0,self.lineLength_lg/2,0)
        
        # Handle line selection
        # -----------------------------------
        # If line is selected draw some handles
        if self.lineSelected:
            pen = QPen(Qt.SolidLine)
            pen.setWidth(1)
            pen.setColor(handleColour)            
            painter.setPen(pen)
            painter.setBrush(handleColour)
            
            # Set radius
            
            # Horizontal dimension of the handles
            radius = 1
            
            # Handle at start of line
            rs = QPoint(-self.lineLength_lg/2,0)
            painter.drawEllipse(rs,radius,radius*pixConv)
            
            # Handle at start of line
            re = QPoint(self.lineLength_lg/2,0)
            painter.drawEllipse(re,radius,radius*pixConv)
            
            
            
        # Symbol
        # ========================================================
        
        # Scale to make the marker a constant size in pixels
        # logical marker width = pixel width*logical widget width/actual pixel width
        # and the same for height
        xscale = self.markerSize*self.LogicalWidth/rect.width()
        yscale = self.markerSize*self.LogicalHeight/rect.height()
        
        # Colours and lines
        pen = QPen(Qt.SolidLine)
        pen.setWidth(0)
        
        markerColour = QColor()
        markerColour.setNamedColor(self.markerColour)
        pen.setColor(markerColour)
        
        markerFillColour = QColor()
        markerFillColour.setNamedColor(self.markerFillColour)
        brush = QBrush(markerFillColour)
                   
        painter.setPen(pen)
        painter.setBrush(brush)
        
        # Convert marker text symbol to a path
        markerPath = Symbols[self.marker] #.translated(symbolOrigin)
        
                
        # Draw the symbol, scaled up
        painter.save() # Store the state

        tr = QTransform()                   # Transform coordinate system
        tr.scale(xscale,yscale)             # Scale marker to constant pixel size
        finalPath = tr.map(markerPath)
        painter.drawPath(finalPath)
      
        
        if self.markerSelected:
            # Draw Handle line on marker
            pen = QPen(Qt.DashLine)
            pen.setWidth(0)
            pen.setColor(handleColour)            
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            
            markerHandleRect = QRectF(-4.5,-4.5*pixConv,9.0,9.0*pixConv)
            print(markerHandleRect)
            painter.drawRect(markerHandleRect)
           
        
        painter.restore()
        
        
        
    def pix2logical(self,x_px,y_px):
        """ Convert pixel coordinates to logical coordinates
        
        x_lg,y_lg = self.pix2logical(x_px,y_px)
        
        """
        
        x_lg = round( x_px*self.LogicalWidth/self.width() - self.LogicalWidth/2 )
        y_lg = round( y_px*self.LogicalHeight/self.height() - self.LogicalHeight/2)
        
        return x_lg,y_lg
        
        
    def logical2pix(self,x_lg,y_lg):
        """ Convert logical coordinates to pixel coordinates
        
        x_px,y_px = logical2pix(x_lg,y_lg)
        
        """
        
        # TODO : Calculation not correct for (0,0) in centre
        
        x_px = x_lg*self.width()//self.LogicalWidth
        y_px = y_lg*self.height()//self.LogicalHeight
        
        return x_px,y_px
        
       

#=============================================================================
#%% Support functions/classes
#=============================================================================


class incrementer():
    """ Class for containing a finite list that spits out a current
    value and then increments to the next
    """
    
    def __init__(self,listOfItems,initialIndex = 0):
        
        self.items = listOfItems
        self.index = initialIndex
        
        self.itemCount = len(self.items)
        
        
    def getItem(self):
        """ Get current item in list
        
        """
        return self.items[self.index]        
        
        
    def getNextItem(self,direction = 1):
        """ Get next item on the list
        
        Optional direction specifies whether to get next or previous 
        item
        """       
        
        # increment to next index depending on direction
        if direction == 1:
            self.increment()
        else:
            self.decrement()
            
        # Get item to return
        item = self.items[self.index]
        
        return item
        
        
    def increment(self):
        """ circular incrementation of internal index, self.index
        If it's greater than the number of items in the list it
        goes back to zero
        """
        
        if self.index < self.itemCount-1:
            self.index +=1
        else:
            self.index = 0
            
    def decrement(self):
        """ circular incrementation of internal index, self.index
        If it's less than zero it goes to max items
        
        """
        
        if self.index > 0:
            self.index -=1
        else:
            self.index = self.itemCount-1
            

#=============================================================================
#%% multiple plot widget class definition
#=============================================================================


# Constants
MAX_COLUMNS = 2


class FlexiDock(QSplitter):
    """ Flexible Dock widget
    Widgets can be put in their own dock 
    The layout of the widgets can be adjusted with the mouse using
    splitter bars
    
    Widgets can be inserted to fill from top down or to fill across
    
    Creating a dock area
    ------------------------
    dock = FlexiDock(fillDirection = 'fill across')
    or 
    dock = FlexiDock(fillDirection = 'fill down')
    
    Adding widgets
    ------------------
    dock.addDock(widget2add,title = 'My dock')
    
    Get currently selected dock
    ------------------------------
    widget = dock.getCurrentWidget()
    
    
    """
    
    def __init__(self,parent=None,fillDirection = 'fill across',groupName = "new group"):
        
        # Initialise base class
        super(FlexiDock, self).__init__(parent)
        
        self.setOpaqueResize(False)
        
        # Group name
        # This gets added to all Dock objects so that Docks attached
        # to this FlexiDock can be identified in drag and drop operations
        self.groupName = groupName
        
        # Allow drag and drop on this widget
        self.setAcceptDrops(True)
        
        # Set default orientation based on how the widgets are
        # populated into the dock grid,
        if fillDirection == 'fill across':
            self.topLevelSplit = Qt.Horizontal
            self.subLevelSplit = Qt.Vertical
        else: # 'fill down'
            self.topLevelSplit = Qt.Vertical
            self.subLevelSplit = Qt.Horizontal
        
        self.setOrientation(self.topLevelSplit)
        
            
        
        # Dictionary to hold plot positions
        # the key is a tuple of coordinates (row,column)
        # TODO : Is this used?
        self.widgetTable = []
        
        # Separate variables to hold table dimensions
        self.nColumns = 0
        self.nRows = 0
        
        # List of Dock objects contained in the FlexiDock
        # use this to find the current dock
        self.dockWidgetList = []
        
        
        # Count of how many widgets are in the dock
        self.dockCount = 0
        
        # Current widget and its index
        self.currentWidget = None
        self.currentIndex = None
        
        # Next plot tuple
        # This determines where the next plot goes
        self.nextPlot = (1,1)
        
        
    def addDock(self,Widget,row=None,col=None,title="untitled",userData=None):
        """
        Add a widget in a dock at the row,column specified or just place it
        
        Inputs
        -----------
        row,col = optional row column coordinates, if not specified then the 
                    dock will be added according to the fillDirection
        title = title shown on the dock label
        group = string for the group that 
        
        """
        
        
        # Add plotWidget to plotTable
        # ---------------------------------
        
        # If nothing specified then use next plot
        if row==None or col==None:
            (row,col) = self.nextPlot
            
        # If no title then add one
        if title == "untitled":
            title = "%s %d" % (self.groupName,self.dockCount)
        
            
        
        # Create a docking widget
        # ----------------------------------
        # this is to give the dock a border, title and any other
        # decorations

        dockWidget = Dock(Widget,title,ID=self.dockCount,groupName = self.groupName)
        self.connect(dockWidget, SIGNAL("clicked()"),self.selectWidget)
        
        # add user data
        dockWidget.userData = userData
        
        
        # Log dock and widget to their lists
        # ---------------------------------------
        # This allows them to track each other
            
        # Add dockLabel to list
        self.dockWidgetList.append(dockWidget)
        
        # Add to widgetTable at row,column
        self.widgetTable.append(Widget)
        
        
        # Make this dock the current one
        self.currentIndex = self.dockCount
        self.currentWidget = Widget
        
        # Make this the selected widget
        self.selectWidget(sender = dockWidget)
        
        
        
        # Increment dockCount
        self.dockCount += 1
        
        
        # Find the position of the new widget
        # ------------------------------------
        # Expand if necessary
        
        # Check if we need a new column
        if col > self.nColumns:
            # Add a new column, containing a vertical splitter
            columnWidget = QSplitter(self.subLevelSplit)
            columnWidget.setOpaqueResize(False)
            
            self.addWidget(columnWidget)
                      
            
            # Increment column count
            self.nColumns +=1
            
             # Update the sizes of the horizontal widgets
            if self.nColumns > 1:
                col_sizes = [round(0.9*self.width()/self.nColumns)]*self.nColumns
                self.setSizes(col_sizes)
                
        else:
            columnWidget = self.widget(col-1)
            
        # check if we need a new row
        rowCount = columnWidget.count()
        
        if row > rowCount:
            # add a new row
            columnWidget.addWidget(dockWidget)
            
            
            # Increment rows
            self.nRows += 1
            
             # Update vertical heights
            if self.nRows > 1:
                row_sizes = [round(0.9*columnWidget.height()/self.nRows)]*self.nRows
                columnWidget.setSizes(row_sizes)
            
        else:
            columnWidget.insertWidget(row-1,dockWidget)
        
        
        # Increment next plot
        if col < MAX_COLUMNS:
            self.nextPlot = (row,col+1)
        else:
            # Move to next row
            self.nextPlot = (row+1,col-1)
        
        
        
        
    def getCurrentWidget(self):
        """ Return widget displayed in current Dock
        
        Outputs
        --------------
        plotWidget = reference to plot widget in current plot
        
        """
        
        currentWidget = None
        
        # Find which button is clicked
        for index,dock in enumerate(self.dockWidgetList):
            flag = dock.isChecked()
#            if DEBUG:
#                print("Button %d : isActiveWindow %d" % (index,flag))
                
            if flag:
                currentWidget = dock.widget
                if DEBUG:
                    print("Button %d selected" % index)
                
        return currentWidget
        
       
       
    def getDockByName(self,name):
        """ 
        Return widget with specified title
        
        Outputs
        --------------
        plotWidget = reference to widget 
        
        """
        
        foundWidget = None
        
        # Find which button is clicked
        for index,dock in enumerate(self.dockWidgetList):
            if dock.title == name:
                foundWidget = dock
           
                
        return foundWidget
    
     

    def deleteDock(self,dock_title):
        """
        Delete a dock
        
        Input
        -------
        dock_title: str
            the name that appears in the title bar of the dock
            
        """
        
        foundDock = self.getDockByName(dock_title)
        dock_parent = foundDock.parent
        
        if foundDock:
            dock_parent.removeWidget(foundDock)
            
        
        
        
    def removeWidget(self,row,column):
        """ 
        Remove a widget at specified row,column
        
        """
        
        raise NotImplemented("removePlot")
        
        
        
    def selectWidget(self,sender = None):
        """ Function passed to each dockLabel button
        When a button is clicked it comes here, where the button
        is traced to find which dock was clicked
        
        Input
        ------------
        sender = optional input to force this function to run
        """
        
        if not sender:
            # Function was called by a button press
            selectedButton = self.sender()
        else:
            # Function was called from another function
            # probably addDock
            selectedButton = sender
        
        #print("Button clicked = %s" % selectedButton.text())
        
        # Deselect all buttons and then select the current button
        
        for index,button in enumerate(self.dockWidgetList):
            button.setChecked(False)
            button.lookInactive()
            
            # Get the current widget
            if button == selectedButton:
                self.currentWidget = self.widgetTable[index]
                self.currentIndex = index
            
        
        selectedButton.setChecked(True)
        selectedButton.lookActive()
        
        # Send out a signal to say dock has been selected
        self.emit(SIGNAL("NewPlotSelected"))
        
        
        
    # Drag and drop functions
    # =======================================
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-dockDrag"):
            event.accept()
        else:
            event.ignore()


    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat("application/x-dockDrag"):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()


    def dropEvent(self, event):
        if event.mimeData().hasFormat("application/x-dockDrag"):
            data = event.mimeData().data("application/x-dockDrag")
            stream = QDataStream(data, QIODevice.ReadOnly)
            text = stream.readQString()
            group = stream.readQString() # TODO for validation
            # Read ID from stream
            # ID = Index in dockWidgetList
            dockIndex = stream.readInt16()
            
            event.setDropAction(Qt.MoveAction)
            event.accept()
            
            # Do dock specific stuff here
            
            if DEBUG:
                print("FlexiDock : Drop from %s" % text)
                
            # Get source Dock
            # TODO : This is not robust need a better way to pass sourceDock
            sourceDock = self.dockWidgetList[dockIndex]
            
            # Find the nearest Dock
            nearestDock = self.nearestDock(event.pos())
            
            
            if (nearestDock != None) and (sourceDock != None):
                # Insert source above nearest Dock
                self.insertDockAbove(sourceDock,nearestDock)
            
            
        else:
            event.ignore()
            
            
            
    # Location functions
    # ===================================
    def nearestDock(self,pos):
        """ Find the nearest dock to the specified position
        
        Inputs
        --------------
        pos = position coordinates to be checked [QPoint()]
        
        Outputs
        ----------
        widgetIndex = (row,column)
        
        """
        
        nearestWidget = None
        
        if DEBUG:
            print("FlexiDock:nearestDock: Input position")
            print(pos)
                
        
        # check all widgets
        for widget in self.dockWidgetList:
            if widget.dockAreaRect().contains(pos):
                nearestWidget = widget
                
            if DEBUG:
                print(widget.text())
                print("\tGeometry",widget.geometry())
                print("\tdockRect",widget.dockAreaRect())
                print("\tParent",widget.parentWidget().geometry())
        
        
        if not nearestWidget:
            if DEBUG:
                print("FlexiDock:nearestDock: No widget found")
            return
          
        if DEBUG:
            print("FlexiDock:nearestDock: Found %s" % nearestWidget.text())
            
        # Return the Dock widget that was found
        return nearestWidget
        
        
    
    
    
    def dockFromLabel(self,dockLabel):
        """ Get Dock widget from label text
        
        Input
        ------------
        dockLabel = string with the Dock title in
        
        Output
        -------------
        dock = Dock widget with the correct label or None
        
        """
        
        dockFound = None
        
        for dock in self.dockWidgetList:
            if dock.text() == dockLabel:
                dockFound = dock
                
        return dockFound
    
    
    
    def insertDockAbove(self,sourceDock,nearestDock):
        """ Insert a Dock above another
        Remove sourceDock from it's parent and repatriate it
        into a new splitter at the position of the nearest Dock
        
        Inputs
        ------------
        sourceDock = The Dock to move into a new position
        nearestDock = The Dock that is nearest to the new position
        
        """
        
        
        # Get index and parent of nearest Dock
        nearestParent = nearestDock.parentWidget()
        nearestIndex = nearestParent.indexOf(nearestDock)
        
        # Insert source Dock into new location
        # above nearest
        nearestParent.insertWidget(nearestIndex,sourceDock)
        
        # Remove source Dock from it's parent
        # No code needed the splitter does this for us
        
    
    
    def getCurrentDockIndex(self):
        """ Return index of current Dock
        
        Outputs
        --------------
        currentDockIndex = index of current Dock in self.dockWidgetList
        
        """
        
        currentDockIndex = None
        
        # Find which button is clicked
        for index,dock in enumerate(self.dockWidgetList):
            
            if flag:
                currentDockIndex = index
                
        return currentDockIndex
        
        
    
    def getAllUserData(self):
        """
        Get all the user data from the docks
        
           
        Outputs
        --------
        userData : dict
            dictionary of user data with dock name as the key
            
        """
        userData = {}
        
        for dock in self.dockWidgetList:
            userData[dock.title] = dock.userData
            
        return userData
        
        
        
  
dockLabelStyleSheet = """
QPushButton:{Text-align:left;
            border: 2px solid #8f8f91;
            padding: 0;
            padding-left: 5px;
            }
            
QPushButton:pressed{Text-align:left;
                    padding:0;}
                    
QPushButton:checked{Text-align:left;
                    padding:0;
                    background-color:green;}

"""      
       
class Dock(QFrame):
    """ 
    Dock widget for use with FlexiDock
    This widget is a frame with a title that gets put into the FlexiDock
    
    The main reason for creating this separate to FlexiDock is to enable
    drag and drop moving of the docks.
    
    """
    
    def __init__(self,displayWidget,title = "untitled",parent=None,ID=0,groupName = None):
        """ Create the dock widget
        """
        
        # Initialise baseclass
        super(Dock, self).__init__(parent)
        
        # Create a docking widget
        # ----------------------------------
        # this is to give the dock a border, title and any other
        # decorations
        
        # Store a pointer to the widget contained by the Dock
        self.widget = displayWidget
        
        # ID for using with drag and drop
        self.ID = ID
        
        # Store the title
        self.title = title
        
        # Group identifier
        self.groupName = groupName
        
        # User data
        # Place where specific data can be stored. This will be passed
        # in by FlexiDock.addDock
        self.userData = None
        
        
        # Layout the Dock
        # -----------------------------
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setFocusPolicy(Qt.StrongFocus)
               
        self.dockLabel = QPushButton()
        self.dockLabel.setCheckable(True)
        self.dockLabel.setText(title)
        #self.dockLabel.setStyleSheet("Text-align:left;padding-left: 5px;")
        self.dockLabel.setStyleSheet(dockLabelStyleSheet)
        #self.dockLabel.setFlat(True)
        self.dockLabel.setBackgroundRole(QPalette.Highlight)
        
        # Connect "clicked" signal to the outside world
        self.connect(self.dockLabel, SIGNAL("clicked()"),self.sendClickedSignal)
      
        dockWidgetLayout = QVBoxLayout()
        dockWidgetLayout.addWidget(self.dockLabel)
        dockWidgetLayout.addWidget(displayWidget)
        self.setLayout(dockWidgetLayout)
        
        
    def lookActive(self):
        """
        Do something to the appearance of the button to make
        it look like the active one
        
        """
        
        self.dockLabel.setText("*" + self.title)
        #self.dockLabel.setPalette(QPalette.Active)
        
        
    def lookInactive(self):
        """
        Make the button look inactive
        
        """
        
        self.dockLabel.setText(self.title)
        #self.dockLabel.setPalette(QPalette.Inactive)
        
        
    # Button access
    def setDown(self,boolean):
        """ Reimplement setDown function for button
        """
        self.dockLabel.setDown(boolean)
        
    def isDown(self):
        """Reimplement ischecked for button
        """
        
        return self.dockLabel.isDown()
        
    def setChecked(self,boolean):
        """ Reimplement setDown function for button
        """
        self.dockLabel.setChecked(boolean)
        
    def isChecked(self):
        """Reimplement ischecked for button
        """
        
        return self.dockLabel.isChecked()
        
        
    def text(self):
        """Reimplement text() method
        """
        
        return self.dockLabel.text()
        
    def sendClickedSignal(self):
        """Reimplement "clicked" signal
        """
        self.emit(SIGNAL("clicked()"))
        
        
    # Functions needed for dragging:
    def mouseMoveEvent(self,event):
        self.startDrag()
        QWidget.mouseMoveEvent(self,event)
        
    
    def startDrag(self):
        """ Initiate dragging the dock
        """
       
        icon = QIcon(QPixmap.grabWidget(self.dockLabel,self.dockLabel.rect()))
        
        # TODO : The icon is null
        if icon.isNull():
            if DEBUG:
                print("Dock drag: No Icon - exiting" )
            return
            
        if DEBUG:
            print("Dock drag: started")
            
        data = QByteArray()
        stream = QDataStream(data, QIODevice.WriteOnly)
        # Add Dock label to stream
        stream.writeQString(self.text())
        # Add group name to stream
        stream.writeQString(self.groupName)
        
        # Add Dock ID to stream
        stream.writeInt16(self.ID)
        
        # Put data in MIME packet for drag and dropping
        mimeData = QMimeData()
        mimeData.setData("application/x-dockDrag", data)
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        pixmap = icon.pixmap(24, 24)
        drag.setHotSpot(QPoint(12, 12))
        drag.setPixmap(pixmap)
        drag.exec_(Qt.MoveAction)
        
        
    def dockAreaRect(self):
        """ Return rectangle of Dock widget in coordinates
        relative to the top left hand corner of the FlexiDock area
        
        Output
        --------------
        rect = QRect [x,y,w,h]
        
        """
        
        # Get coordinates of parent
        parentRect = self.parentWidget().geometry()
        
        # Get coordinates of this Dock object
        dockRect = self.geometry()
        
        return QRect(parentRect.left()+dockRect.left(),
                     parentRect.top()+dockRect.top(),
                     dockRect.width(),dockRect.height())
        
#=============================================================================
#%% Tab bar
#=============================================================================
        
  

class TabBar(QTabBar):
    """
    TabBar class that implements making the tab names editable
    
    Taken from StackOverflow.com
    
    
    """
    def __init__(self, parent):
        QTabBar.__init__(self, parent)
        
        # Make a QLineEdit object to popup over the tab name
        # to create the illusion of editing the name directly
        self._editor = QLineEdit(self)
        self._editor.setWindowFlags(Qt.Popup)
        self._editor.setFocusProxy(self)
        self._editor.editingFinished.connect(self.handleEditingFinished)
        self._editor.installEventFilter(self)
        

    def eventFilter(self, widget, event):
        if ((event.type() == QEvent.MouseButtonPress and
             not self._editor.geometry().contains(event.globalPos())) or
            (event.type() == QEvent.KeyPress and
             event.key() == Qt.Key_Escape)):
            self._editor.hide()
            return True
            
        return QTabBar.eventFilter(self, widget, event)
        

    def mouseDoubleClickEvent(self, event):
        index = self.tabAt(event.pos())
        if index >= 0:
            self.editTab(index)
            

    def editTab(self, index):
        rect = self.tabRect(index)
        self._editor.setFixedSize(rect.size())
        self._editor.move(self.parent().mapToGlobal(rect.topLeft()))
        self._editor.setText(self.tabText(index))
        self._editor.selectAll()
        
        if not self._editor.isVisible():
            self._editor.show()
            

    def handleEditingFinished(self):
        index = self.currentIndex()
        if index >= 0:
            self._editor.hide()
            
            # Check for duplicate names
            # Only update tab name if it is not a duplicate
            tab_names = [self.tabText(ind) for ind in range(self.count())]
            
            new_name = self._editor.text()
            
            if new_name not in tab_names:
                self.setTabText(index, new_name)
            
#=============================================================================
#%% Tab workspace
#=============================================================================


class TabWorkspace(QMdiArea):
    """
    Wrapper for QMdiArea.
    
    Implements an area with windows where plots and panels can be
    placed.
    
    """
    
    MAX_WINDOWS = 12 # = Number of function keys
    
    
    def __init__(self,parent=None,defaultName="untitled"):
        
        # Initialise parent object
        super(TabWorkspace, self).__init__(parent) 
        
        self.defaultName = defaultName
        
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.setLineWidth(3)
        self.setMidLineWidth(3)
        
        
    @property
    def numWindows(self):
        
        return len(self.subWindowList())
        
        
    def addWindow(self,widget,title=None):
        """
        Add a window with a name and widget
        
        Inputs
        --------
        widget : Any widget
            The widget that goes inside the window
            
        title: str
            title of the window
            
        """
        
        # Check we have not exceeded the max number of windows
        if self.numWindows == self.MAX_WINDOWS:
            QMessageBox.warning(self,"Too many windows",
                                "Maximum number of windows exceeded. Cannot add any more",
                                buttons=QMessageBox.Ok)
            return
            
        # Add the window
        if title is None:
            title = self.makeDefaultWindowName()
        
        subWindow = self.addSubWindow(widget)
        subWindow.setAttribute(Qt.WA_DeleteOnClose)
        subWindow.setWindowTitle(title)
        subWindow.show()
        
        return subWindow
        
        
        
        
        
    def deleteWindow(self,windowTitle):
        """
        Delete window and everything in it
        
        """
        window = self.getSubWindowByTitle(windowTitle)
        if window:
            self.removeSubWindow(window)
            
    
    
    def getSubWindowByTitle(self,windowTitle):
        """
        Get the sub window widget using its title
        
        Input
        ------
        windowTitle: str
        
        """
        
        foundWindow = None
        
        for window in self.subWindowList():
            if window.windowTitle() == windowTitle:
                foundWindow = window
                
        return foundWindow
        
        
    def getCurrentWidget(self):
        """
        Get current widget from the active window
        
        """
        
        # Get active window
        activeWindow = self.activeSubWindow()
        
        # Return widget from active window
        return activeWindow.widget()
        
        
        
    def makeDefaultWindowName(self):
        """
        Return a default name for a new window e.g. untitled-01
        
        """
        
        # Count number of windows
        suffix = "-%02d" % (len(self.subWindowList())+1)
        
        return self.defaultName + suffix
        
        
      


         
        
#=============================================================================
#%% Math functions
#=============================================================================
class MathDialog(QDialog):
    """
    Dialog box for setting Math functions on a channel
    
    """
    
    def __init__(self,sourceChannel,functionList,channelList,parent=None):
        """
        
        Inputs
        --------
        sourceChannel : str
            name of source channel
            
        functionList : list
            list of MathFunction class object
            
        channelList : list
            list of channels
            
        """
        
        # TODO: Check lengths of channels for any multiple channel functions.
        
        # Initialise base class
        super(MathDialog,self).__init__(parent)
        
        # Internal variables
        # ======================
        self.functionList = functionList
        self.functionNameList = [mf.name for mf in functionList]
        
        # Get defaults
        # ==================
        self.sourceChannelIndex = channelList.index(sourceChannel)
        
        # Fudge a width in pixels
        # 10 pixels/char seems a good estimate, make it a double
        textWidth_pix = len(sourceChannel)*10*2
        
        # Make the widgets
        # =========================
        
        # New channel name
        self.nameEdit = QLineEdit("Math_" + sourceChannel)        
        self.nameEdit.setFixedWidth(textWidth_pix)
        nameLabel = QLabel('Channel &name')        
        nameLabel.setBuddy(self.nameEdit)
        
        
        # Function selector combo
        self.funcCombo = QComboBox()
        self.funcCombo.addItems(self.functionNameList)
        funcLabel = QLabel('Math &Function')
        funcLabel.setBuddy(self.funcCombo)
        
        # Function description
        self.funcDescription = QLabel("No description")
        self.funcDescription.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.funcDescription.setLineWidth(2)
        
        # Source channel selector
        self.srcSelector = FunctionInputSelector(channelList,self.sourceChannelIndex)
        srcLabel = QLabel('&Source channel')
        srcLabel.setBuddy(self.srcSelector)
        
        
        # OK/Cancel button
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        buttonBox.button(QDialogButtonBox.Ok).setDefault(True)
        
        
        # Set the layout
        # ==================
        layout = QGridLayout()
        layout.addWidget(nameLabel,0,0)
        layout.addWidget(self.nameEdit,0,1)
                
        layout.addWidget(funcLabel,1,0)
        layout.addWidget(self.funcCombo,1,1)

        layout.addWidget(QLabel("Description"),2,0)        
        layout.addWidget(self.funcDescription,3,0,2,2)
        
        layout.addWidget(srcLabel,5,0)
        layout.addWidget(self.srcSelector,6,0,2,2)
        
        layout.addWidget(buttonBox,8,0,2,1)
        
        self.setLayout(layout)
        
        self.nameEdit.setFocus()
        self.setWindowTitle("Math function selector")
        
        self.switchFunction(self.functionNameList[0])
        
        
        # Connections
        # =================
        # Function combo changes
        self.connect(self.funcCombo,SIGNAL("currentIndexChanged(QString)"),self.switchFunction)        
        
        # Exit buttons
        self.connect(buttonBox,SIGNAL("accepted()"),self.exitDialog)
        self.connect(buttonBox,SIGNAL("rejected()"),self,SLOT("reject()"))
        
    
        # Output variables
        self.mathChannelName = ''
        self.sourceChannel = ''
        self.mathFunction = None
        
        
    
    def switchFunction(self,function_name):
        """
        Set the FunctionInputSelector according to the function that has been
        selected
        
        """

        # Get selected function
#        funcIndex = self.functionNameList.index(self.funcCombo.currentText())
        funcIndex = self.functionNameList.index(function_name)
        math_function = self.functionList[funcIndex]
        
        # Change description label
        self.funcDescription.setText(math_function.description)
        
        if math_function.is_list_input:
            # List input - show a list box
            self.srcSelector.setSelector(True)
            logger.debug("Source selector: list selected for [%s]" % function_name)
            
        else:
            # Individually named inputs - show a table
            self.srcSelector.setSelector(False,math_function.function_inputs)
            logger.debug("Source selector: table selected for [%s]" % function_name)
            
    
    def exitDialog(self):
        
        # Read channel names direct from widgets
        self.mathChannelName = self.nameEdit.text()
        self.sourceChannels = self.srcSelector.getList()
        
        # For the function get the name and then return the function object
        funcIndex = self.functionNameList.index(self.funcCombo.currentText())
        self.mathFunction = self.functionList[funcIndex]
        
        logger.debug('MathDialog: New channel [%s]' % self.mathChannelName)
        logger.debug('MathDialog: source channels [%s]' % ",".join(self.sourceChannels))
        logger.debug('MathDialog: Function [%s]' % self.functionNameList[funcIndex])
        
        # Exit dialog
        self.accept()
        
        
        
class FunctionInputSelector(QFrame):
    """
    Selector widget for MathFunction inputs. 
    
    Can either select named inputs or a list
    
    """
    
    def __init__(self,source_list,current_index=0,parent=None):
        """
        Inputs
        ------
        source_list : list
            list of strings
            
        """
        
        # Initialise base class
        super(FunctionInputSelector,self).__init__(parent)
        
        # Settings
        # ===============
        self.source_list = source_list
        self.isList = True
        self.current_index = current_index
        
        
        # Make the widgets
        # ================================
        
        # List pane
        # ----------------
        # Source list box        
        self.source_listBox = QListWidget()
#        self.source_listBox.addItems(source_list)
        self.source_listBox.setSelectionMode(QListWidget.MultiSelection)
        
        # Table pane
        # --------------
        self.input_table = QTableWidget()
        
        
        # Stacked widget
        # ----------------------
        self.panes = QStackedWidget()
        self.panes.addWidget(self.input_table)
        self.panes.addWidget(self.source_listBox)
        
        # Layout
        # ----------
        layout = QVBoxLayout()
        layout.addWidget(self.panes)
        self.setLayout(layout)
        
        # Connections
        self.connect(self.source_listBox,SIGNAL('currentItemChanged54 (QListWidgetItem*,QListWidgetItem*)'),self.changeCurrentIndex)
        
        
    def setSelector(self,showList,input_list=None):
        """
        Select whether to display a table of list box
        
        """
        
        if showList:
            # Select list box pane
            self.isList = True
            self.panes.setCurrentIndex(1)
            self.showList()
            
            
        else:
            self.isList = False
            self.panes.setCurrentIndex(0)
            self.showTable(input_list)
            
            
    def showList(self):
        """
        Populate list box with available channels
        """
        self.source_listBox.clear()
        self.source_listBox.addItems(self.source_list)
        self.source_listBox.setCurrentIndex(self.current_index)
    
    
    def showTable(self,input_list):
        
        # Clear table
        self.input_table.clear()
        
        # Setup table
        self.input_table.setRowCount(len(input_list))
        self.input_table.setColumnCount(2)
        self.input_table.setHorizontalHeaderLabels(['Input','Channel'])
        
        
        # Add items
        for row,input_name in enumerate(input_list):
            # Input parameter name in first column
            item = QLabel(input_name)
            self.input_table.setCellWidget(row,0,item)     
            
            # Channel combo box in second column
            srcCombo =QComboBox()
            srcCombo.addItems(self.source_list)
            srcCombo.setCurrentIndex(0)
            
            #item2 = QTableWidgetItem(srcCombo)
            self.input_table.setCellWidget(row,1,srcCombo)
            
     
    def getList(self):
        """
        Return selected channels as a list of channel names
        
        """
        
        if self.isList:
            return self.getListFromListBox()
            
        else:
            return self.getListFromTable()
            
            
    
    def getListFromTable(self):
        """
        Get the selected channels from the table of QComboBoxes
        
        """
        
        
        
        return_list = []
        
        for row in range(self.input_table.rowCount()):
            return_list.append(self.input_table.cellWidget(row,1).currentText())
        
        return return_list
        
        
        
    def getListFromListBox(self):
        
        # Get selection
        selectedItems = self.source_listBox.selectedItems()
        
        return_list = []
        
        logger.debug("Selected items:")
        print(selectedItems)
        
        for item in selectedItems:
            return_list.append(item.text())
            
        return return_list
        
        
    def changeCurrentIndex(self,new_list_item,*args):
        """
        Change list box current index
        
        """
        
        txt = new_list.text()
        self.current_index = self.source_list.index(txt)
        
        
        

#=============================================================================
#%% Color Picker
#=============================================================================
import os
class colorpicker(QWidget):
    """
About:
-----------------
This is a color WIDGET that is like the tkinter one.
It is built to be more keybord friendly.

Use:
-----------------
You use the colorpicker as a normal widget.
Its varibles
colorpicker.name = str of rgb color: '#ff0000'
colorpicker.r>
colorpicker.g>> RGB : r,g,b : 255,0,0
colorpicker.b>
are how you get colors from the widget.
"""
    def __init__(self):
        
        super(colorpicker,self).__init__()
        hl = QHBoxLayout()
        self.stack = QStackedWidget()
        b = QPushButton('<<>>')
        b.clicked.connect(self.changeStack)
        hl.addWidget(self.stack)
        hl.addWidget(b)
        self.setLayout(hl)
        self.selectorstart()
        self.paletteSelector()
        self.stack.setCurrentIndex(0)
        

    def selectorstart(self):
        l = QVBoxLayout()
        self.setWindowTitle("Color Dialog")
        self.rline = QGraphicsScene()
        self.rview = QGraphicsView()
        self.rview.setScene(self.rline)
        self.rslider = QSlider(Qt.Horizontal)
        self.rslider.setMinimum(0)
        self.rslider.setMaximum(255)
        self.connect(self.rslider,SIGNAL("sliderMoved(int)"),self.rupdatecolors)
        self.connect(self.rslider,SIGNAL("valueChanged(int)"),self.rupdatecolors)
        #self.setcolors()
        self.gline = QGraphicsScene()
        self.gview = QGraphicsView()
        self.gview.setScene(self.gline)
        self.gslider = QSlider(Qt.Horizontal)
        self.gslider.setMinimum(0)
        self.gslider.setMaximum(255)
        self.connect(self.gslider,SIGNAL("sliderMoved(int)"),self.gupdatecolors)
        self.connect(self.gslider,SIGNAL("valueChanged(int)"),self.gupdatecolors)

        #self.setcolors()
        self.bline = QGraphicsScene()
        self.bview = QGraphicsView()
        self.bview.setScene(self.bline)
        self.bslider = QSlider(Qt.Horizontal)
        self.bslider.setMinimum(0)
        self.bslider.setMaximum(255)
        self.connect(self.bslider,SIGNAL("sliderMoved(int)"),self.bupdatecolors)
        self.connect(self.bslider,SIGNAL("valueChanged(int)"),self.bupdatecolors)
        l.addWidget(self.rview)
        l.addWidget(self.rslider)
        l.addWidget(self.gview)
        l.addWidget(self.gslider)
        l.addWidget(self.bview)
        l.addWidget(self.bslider)
        #**********************
        #valueChanged (int)
        self.r = 0
        self.b = 0
        self.g = 0
        nl = QVBoxLayout()
        self.rspin = QSpinBox()
        self.rspin.setReadOnly(False)
        self.rspin.setMaximum(255)
        self.connect(self.rspin,SIGNAL("valueChanged(int)"),self.update)

        self.gspin = QSpinBox()
        self.gspin.setReadOnly(False)
        self.gspin.setMaximum(255)
        self.connect(self.gspin,SIGNAL("valueChanged(int)"),self.update)

        self.bspin = QSpinBox()
        self.bspin.setReadOnly(False)
        self.bspin.setMaximum(255)
        self.connect(self.bspin,SIGNAL("valueChanged(int)"),self.update)
        self.namebox = QLineEdit()
        self.namebox.setReadOnly(False)
        self.connect(self.namebox,SIGNAL("editingFinished()"),self.setnamed)
        nl.addWidget(self.rspin)
        nl.addWidget(self.gspin)
        nl.addWidget(self.bspin)
        nl.addWidget(self.namebox)
        
        #************************
        labl = QVBoxLayout()
        rl = QLabel('Red:')
        gl = QLabel('Green:')
        bl = QLabel('Blue:')
        to = QLabel('Color:')
        labl.addWidget(rl)
        labl.addWidget(gl)
        labl.addWidget(bl)
        labl.addWidget(to)
        self.colorbox = QGraphicsView()
        self.incolor = QGraphicsScene()
        self.colorbox.setScene(self.incolor)
        l.addWidget(self.colorbox)
        #ml = QHBoxLayout(self)
        ml = QHBoxLayout()
        ml.addLayout(labl)
        ml.addLayout(l)
        ml.addLayout(nl)
        
        w = QWidget(self)
        w.setLayout(ml)
        self.stack.addWidget(w)
        self.setcolors(0,0,0)

    def setcolors(self,r,g,b):
        #manargs.check([r,g,b],[int,int,int])
        self.rline.clear()
        self.gline.clear()
        self.bline.clear()
        self.r = r
        self.g = g
        self.b = b
        w = 5
        h = 20
        x = 0
        y = 0
        c = 0
        for i in range(32):
            rcolor = QColor(c,g,b)
            #color.setNamedColor('#ff00ff')
            brush = QBrush(rcolor,Qt.SolidPattern)
            
            rec = self.rline.addRect(x,y,w,h,rcolor,brush)
            x += 5
            c+=7

        c = 0
        for i in range(32):
            gcolor = QColor(r,c,b)
            #color.setNamedColor('#ff00ff')
            brush = QBrush(gcolor,Qt.SolidPattern)
            
            rec = self.gline.addRect(x,y,w,h,gcolor,brush)
            x += 5
            c+=7

        c = 0
        for i in range(32):
            bcolor = QColor(r,g,c)
            #color.setNamedColor('#ff00ff')
            brush = QBrush(bcolor,Qt.SolidPattern)
            
            rec = self.bline.addRect(x,y,w,h,bcolor,brush)
            x += 5
            c+=7

        mcolor = QColor(r,g,b)
        brush = QBrush(mcolor,Qt.SolidPattern)
        
        self.incolor.addRect(0,0,50,50,mcolor,brush)
        self.name = mcolor.name()
        
        self.namebox.setText(mcolor.name())


    def rupdatecolors(self,r):
        self.r = r
        self.rspin.setValue(r)
        self.setcolors(r,self.g,self.b)
    def gupdatecolors(self,g):
        self.g = g
        self.gspin.setValue(g)
        self.setcolors(self.r,g,self.b)

    def bupdatecolors(self,b):
        self.b = b
        self.bspin.setValue(b)
        self.setcolors(self.r,self.g,b)

    def update(self,dummy):
        self.r = self.rspin.value()
        self.g = self.gspin.value()
        self.b = self.bspin.value()
        self.rslider.setValue(self.r)
        self.gslider.setValue(self.g)
        self.bslider.setValue(self.b)
        self.setcolors(self.r,self.g,self.b)

    def setnamed(self):
        txt = self.namebox.text()
        self.setNamedColor(txt)

    def setNamedColor(self,color):
        #manargs.check([color],[str])
        r,g,b = HTMLColorToRGB(color)
        self.rslider.setValue(r)
        self.gslider.setValue(g)
        self.bslider.setValue(b)
        self.setcolors(r,g,b)

    def changeStack(self):
        index = self.stack.currentIndex()
        if index == 1:
            self.stack.setCurrentIndex(0)
        else:
            self.stack.setCurrentIndex(1)

    def paletteSelector(self):
        self.palettes = ScopePyPalettes()
        l = QVBoxLayout()
        names = []
        for i in self.palettes.PaletteDict:
            names.append(i)
        self.combo = QComboBox()
        self.combo.addItems(names)
        self.connect(self.combo,SIGNAL("currentIndexChanged(int)"),self.changeColors)
        self.colors = QListWidget()
        print(names)
        bcn = None
        c = 0
        for i in names:
            if i == "BasicColors":
                
                bcn = c

            if bcn != None:

                c+= 1

        self.combo.setCurrentIndex(bcn)
        allcols = self.palettes.PaletteDict['BasicColors'].getAllColors()
        self.colors.addItems(allcols)
        p1 = QPushButton('Add New Palette!')
        p2 = QPushButton('Add New Color!')
        p3 = QPushButton('Set Selector Color!')
        p4 = QPushButton('Refresh!')
        p4.clicked.connect(self.refresh)
        p2.clicked.connect(self.newColor)
        p1.clicked.connect(self.newPalette)
        p3.clicked.connect(self.setSelectorColor)
        l.addWidget(self.combo)
        l.addWidget(self.colors)
        l.addWidget(p1)
        l.addWidget(p2)
        l.addWidget(p3)
        l.addWidget(p4)
        w = QWidget()
        w.setLayout(l)
        self.stack.addWidget(w)

    def changeColors(self,index):
        c = 0
        self.palettes.refresh()
        a = []
        for i in self.palettes.PaletteDict:
            a.append(i)
            c += 1

        self.colors.clear()
        allcols = self.palettes.PaletteDict[a[index]].getAllColors()
        self.colors.addItems(allcols)

    def refresh(self):
        self.combo.clear()
        names = []
        print(self.palettes.PaletteDict)
        
        for i in self.palettes.PaletteDict:
            names.append(i)
        print(names)
        self.combo.addItems(names)
        index = self.combo.currentIndex()
        self.changeColors(index)

    def newPalette(self):
        name,dummy = QInputDialog.getText(self,'QInputDialog.getText','Enter the name of your new palette')
        text = self.combo.currentText()
        palette = Palette()
        self.palettes.addPalette(name,palette)
        palette.save(os.path.join(os.path.expanduser('~'),'.ScopePy','Palette-Bin',name))
        self.refresh()

    def newColor(self):
        name,dummy = QInputDialog.getText(self,'QInputDialog.getText','Enter the name of your new color')
        text = self.combo.currentText()
        palette = self.palettes.PaletteDict[text]
        print(palette)
        palette.addColor(name,self.name)
        palette.save(os.path.join(os.path.expanduser('~'),'.ScopePy','Palette-Bin',text))
        self.refresh()

    def setSelectorColor(self):
        colurs2 = self.colors.selectedItems()
        colorname = colurs2[0].text()
        text = self.combo.currentText()
        palette = self.palettes.PaletteDict[text]
        rgbcolor = palette.getColor(colorname)
        color = rgb_to_hex(rgbcolor)
        self.setNamedColor(color)
        
        

        

def HTMLColorToRGB(colorstring):
    # from stack overflow
    """ convert #RRGGBB to an (R, G, B) tuple """
    colorstring = colorstring.strip()
    if colorstring[0] == '#': colorstring = colorstring[1:]
    if len(colorstring) != 6:
        raise ValueError("input #%s is not in #RRGGBB format" % colorstring)
    r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
    r, g, b = [int(n, 16) for n in (r, g, b)]
    return (r, g, b)


    for i in range(len(re)):
        re[i] = uniformLength(re[i])
    return re
    
    
    
    
import pickle
class Palette:
    """
    Made for ScopePy.
    A way of storing colors
    """
    def __init__(self):
        self._colorDict = {}

    def addColor(self,name,*args):
        """
        Name: Name of color
        Args Can be R, G, B or #RRGGBB
        """
        if isinstance(args[0],str):
            print('string!')
            color = HTMLColorToRGB(args[0])
        else:
            print('not string:',args)
            color = (args[0],args[1],args[2])

        self._colorDict[name]=color

    def deleteColor(self,name):
        self._colorDict.pop(name)

    def getColor(self,name):
        """
        In R, G, B format
        """
        return self._colorDict[name]

    def getAllColors(self):
        names = []
        for i in self._colorDict:
            names.append(i)

        return names
    def save(self,filename):
        f = open(filename,'wb')
        pickle.dump(self._colorDict,f)
        f.flush()
        f.close()

    def load(self,filename):
        f = open(filename,'rb')
        data = pickle.load(f)
        f.close()
        rp = Palette()
        rp._colorDict = data
        return rp

class ScopePyPalettes:
    def __init__(self):
        self.worker = Palette()
        self.PaletteDict = {}
        try:
            ex = self.worker.load(os.path.join(os.path.expanduser('~'),'.ScopePy','Palette-Bin','BasicColors'))
        except:
            print('Cannot find Standard Palette: Creating a new one')
            if not os.path.exists(os.path.join(os.path.expanduser('~'),'.ScopePy','Palette-Bin')):
                os.mkdir(os.path.join(os.path.expanduser('~'),'.ScopePy','Palette-Bin'))
            ex = Palette()
            ex.addColor('Red','#ff0000')
            ex.addColor('Green','#00ff00')
            ex.addColor('Blue','#0000ff')
            ex.addColor('Purple','#9300ff')
            ex.addColor('Yellow','#ffff41')
            ex.addColor('Pink','#ffa6ff')
            ex.addColor('Orange','#ffbc7c')
            ex.addColor('Brown','#b16a2d')
            ex.addColor('White','#ffffff')
            ex.addColor('Black','#000000')
            ex.save(os.path.join(os.path.expanduser('~'),'.ScopePy','Palette-Bin','BasicColors'))
            
                                  
        #self.PaletteDict['Basic Colors']=ex
        for i in os.listdir(os.path.join(os.path.expanduser('~'),'.ScopePy','Palette-Bin')):
            ex = self.worker.load(os.path.join(os.path.expanduser('~'),'.ScopePy','Palette-Bin',i))
            name,path = os.path.split(os.path.join(os.path.expanduser('~'),'.ScopePy','Palette-Bin',i))
            self.PaletteDict[path] = ex

    def addPalette(self,name,palette):
        #manargs.check([palette],[Palette])
        self.PaletteDict[name] = palette

    def refresh(self):
        self.PaletteDict

    def deletePalette(self,name):
        self.PaletteDict.pop(name)


    def getPalette(self,name):
        return self.PaletteDict[name]
        
        
def rgb_to_hex(rgb):
   return '#%02x%02x%02x' % rgb
        
"""
Basic Colors:
Red:#ff0000
Green:#00ff00
blue:#0000ff
Purple:#9300ff
Yellow:#ffff41
Pink:#ffa6ff
orange:#ffbc7c
brown:#b16a2d
black:#000000
white:#ffffff
"""
class ColorSquare(QWidget):
    
    def __init__(self,parent=None):
        super(ColorSquare, self).__init__(parent)
        
        self.initUI()
        
        
    def initUI(self):      

        self.setGeometry(300, 300, 350, 100)
        self.setWindowTitle('Colours')
        self.show()
        self.color = (0,0,0)

    def setColor(self,r,g,b):
        self.color = (r,g,b)
        

    def paintEvent(self, e):

        qp = QPainter()
        qp.begin(self)
        self.drawRectangles(qp)
        qp.end()
        
    def drawRectangles(self, qp):
      
        color = QColor(0,0,0)
        color.setNamedColor('#d4d4d4')
        qp.setPen(color)

        qp.setBrush(QColor(self.color[0],self.color[1],self.color[2]))
        qp.drawRect(100, 15, 90, 60)
        
        

#=============================================================================
#%% Function key widgets
#=============================================================================



class FkeyButton(QPushButton):
    """
    Particular type of button used for Function keys
    
    Displays the function key with the label underneath.
    It is a fixed size.
    
    """
    
    Fkeys = ['F%i' % n for n in range(1,11)]
    
    
    def __init__(self,key,label,parent=None):
        QPushButton.__init__(self, parent)
        
        self.key = key
        self._label = label
        self.label_format = "[ %s ]\n%s"
        
        self.setMinimumWidth(90)
        self.setMinimumHeight(40)
        
        self.setText(self.displayLabel())
        
        if key in self.Fkeys:
            print("setting shortcut to %s" % key)
            self.setShortcut(key)
     
        
        
    def displayLabel(self):
        
        return self.label_format % (self.key,self._label)
        
    def label(self):
        return self._label
        
        
    def setLabel(self,label_text):
        
        self._label = label_text
        self.setText(self.displayLabel())
        

class Fkey():
    """
    Class that contains the label and function for a single Function key.
    FkeyToolbar uses a dictionary of these to keep track of the function
    key functions.

    """

    def __init__(self,label='inactive',function=None):
        
        self.label = label
        self.function = function
        
        
        
        
    
class FkeyToolbar(QToolBar):
    """
    Toolbar that uses Function key buttons (FkeyButton) instead of the regular
    QToolButtons.
    
    The idea is that the toolbar will change depending on what panels are
    displayed.
    
    """
    
    def __init__(self,parent=None,shift=False):
        
        QToolBar.__init__(self, parent)
        
        # Number of function keys to use
        self.num_fkeys = 12        
        
        # Function key dictionary
        # This holds the label and function associated with each function key
        # it is a dictionary of Fkey() classes
        self.Fkey_functions ={}
        
        self.FkeyButtons ={}
        
        # Create a function that returns a custom function for each key
        # This is to get every key press to point to the buttonClicked method
        # but also telling it which key was pressed
        def key_function(keyName):
            return lambda :self.buttonClicked(keyName)
        
        # Generate the toolbar
        if shift:
            for key_num in range(1,self.num_fkeys+1):
                key_name = 'Shift+F%i' % key_num
               
                self.Fkey_functions[key_name] = Fkey()
                self.FkeyButtons[key_name] = FkeyButton(key_name,"inactive")
                self.connect(self.FkeyButtons[key_name],SIGNAL('clicked()'),key_function(key_name))
                self.addWidget(self.FkeyButtons[key_name])
        else:
            for key_num in range(1,self.num_fkeys+1):
                key_name = 'F%i' % key_num
                   
                self.Fkey_functions[key_name] = Fkey()
                self.FkeyButtons[key_name] = FkeyButton(key_name,"inactive")
                self.connect(self.FkeyButtons[key_name],SIGNAL('clicked()'),key_function(key_name))
                self.addWidget(self.FkeyButtons[key_name])

        
            
        
        #self.update()
        
        
    def buttonClicked(self,key):
        logger.debug("%s key was pressed" % key)
        
        # Now choose action based on the key that was pressed.
        
        
        if key not in self.Fkey_functions:
            logger.debug("FkeyToolbar/buttonClicked: Key [%s] is not supported" % key)
            return
            
        # Run function
        if self.Fkey_functions[key].function is not None:
            self.Fkey_functions[key].function()
        else:
            logger.debug("%s : No function attached" % key) 
        
        
        
        
    def setFkeyFunctions(self,key_list):
        """
        Add list of function keys, their labels and their functions to the
        FkeyToolbar.
        
        
        Input
        ---------
        fkey_list : list of lists
            Format  [<key>, <label>, <function>]
            e.g. 
                [
                ['F1','Help',self.help]
                ['F2','Edit',self.edit]
                ]
                
        """
        
        for key_def in key_list:
            self.setFkeyFunction(key_def[0],key_def[1],key_def[2])
            
            
    
    
    def setFkeyFunction(self,key,label,function):
        """
        Assign a label and function to a function key
        
        Populates the internal dictionary.
        
        """
        
        if key not in self.Fkey_functions:
            logger.debug("FkeyToolbar/setFkeyFunction: Key [%s] is not supported" % key)
            return
            
        self.Fkey_functions[key].label = label
        self.Fkey_functions[key].function = function
        
        if self.Fkey_functions[key].label == "inactive" or self.Fkey_functions[key].function is None:
            self.FkeyButtons[key].setDisabled(True)
        else:
            self.FkeyButtons[key].setEnabled(True)
            
        # Set the label text
        self.FkeyButtons[key].setLabel(self.Fkey_functions[key].label)
        
        # Update the shortcut
        # - For some reason this has to be done otherwise the shortcut doesn't
        #   work after the label is changed!!!!
        self.FkeyButtons[key].setShortcut(key)
        
        
        
    def update(self):
        """
        Check for inactive buttons and disable them
        
        """
        
        # Go through each key
        # Check the label and function in the Fkey_functions dict
        # If the label is inactive or there is no function, make the key inactive
        for fkey in self.FkeyButtons:
            if self.Fkey_functions[fkey].label == "inactive" or self.Fkey_functions[fkey].function is None:
                self.FkeyButtons[fkey].setDisabled(True)
            else:
                self.FkeyButtons[fkey].setEnabled(True)
                
            # Set the label text
            self.FkeyButtons[fkey].setLabel(self.Fkey_functions[fkey].label)
        
        
        #super().update()
        
        
    def clearFkeys(self):
        """
        Clear all Fkeys
        
        """
        
        for key in self.FkeyButtons:
            self.setFkeyFunction(key,"inactive",None)
            
        self.update()
    
        

#=============================================================================
#%% Test functions
#=============================================================================

        

#=============================================================================
#%% Main window - for testing
#=============================================================================
       
        
        
class MainWindow(QMainWindow):

    def __init__(self, parent=None,test = 'legendLine'):
        # Initialise parent object
        super(MainWindow, self).__init__(parent)         
        
        mainWidget = QWidget()
        
        if test == 'legendLine':
            layout = QGridLayout()
            
            line1 = legendLine()
            line2 = legendLine()
            line3 = legendLine()
            line4 = legendLine()
            line5 = legendLine()
            line6 = legendLine()
            
            layout.addWidget(line1,0,0)
            layout.addWidget(line2,0,1)
            layout.addWidget(line3,0,2)
          
            layout.addWidget(line4,1,0)
            layout.addWidget(line5,1,1)
            layout.addWidget(line6,1,2)
            
        elif test == 'FlexiDock':
            
            layout = QGridLayout()
            dock = FlexiDock(fillDirection = "fill across")
            #dock = FlexiDock(fillDirection = "fill down")
            
            for iDock in range(6):
                title = "XY Graph %d" % iDock
                #plot1 = pg.PlotWidget(title=title,labels = {'left':'Y','bottom':'X'})
                #dock.addDock(plot1)
           
            
            layout.addWidget(dock,0,0)
            
        elif test == 'dialog':
            
            layout = QGridLayout()
            dialogButton = QPushButton('Dialog', self)
            dialogButton.clicked.connect(self.dialogTest)
            
            layout.addWidget(dialogButton)
            
        elif test == 'FunctionInputSelector':
            source_list = ['Channel %i' % ch for ch in range(10)]
            input_list = ['Input %i' % n for n in range(3)]
            
            
            
            fis1 = FunctionInputSelector(source_list)
            fis1.setSelector(True)
            fis2 = FunctionInputSelector(source_list)
            fis2.setSelector(False,input_list)
            
            layout = QGridLayout()
            layout.addWidget(fis1)
            layout.addWidget(fis2)
            
        elif test == 'FkeyButton':
            
            self.toolbar = FkeyToolbar()
            
            
            def dummyFunction():
                print('Fkey was pressed')
            
            Fkeys = [
                ['F1','Help',dummyFunction],
                ['F2','Edit',dummyFunction],
                ['F5','Plot',dummyFunction],
                ['F7','Open',dummyFunction],
                ['F10','Save',dummyFunction],
                ]
                
            self.toolbar.setFkeyFunctions(Fkeys)
            self.toolbar.update()
                
            
            self.addToolBar( self.toolbar)
            button1 = FkeyButton('H','Help')            
            
            layout = QGridLayout()
            
            layout.addWidget(button1)
            
            

            
            
        
        
        mainWidget.setLayout(layout)
        
        # Set central widget
        # =======================================
        self.setCentralWidget(mainWidget)
        
        # ********************************************************
        #               Application startup
        # ********************************************************
        self.setWindowTitle("Scope Py - Widget tests")
        
        
    
        


    def dialogTest(self):
        
        test = 'MathDialog'
        
        if test == 'MathDialog':
            
            class MFunction():
                def __init__(self,name):
                    self.name = name
                    self.description = 'This is a dummy function'
                    self.is_list_input = True
                    self.function_inputs = ["Input %i" % n for n in range(3)]
                
            channels = ['Channel #%i' % ch for ch in range(10)]
            functions = [MFunction('Function #%i' % f) for f in range(10)]
            for n,func in enumerate(functions):
                if n % 2 == 0:
                    functions[n].is_list_input = False
                    functions[n].description = 'This is #%i dummy function' % n
                
            
            form = MathDialog(channels[0],functions,channels)
        
            if form.exec_():
                channel_name = form.mathChannelName
                source_channels = form.sourceChannels
                math_function = form.mathFunction
                
                print("New channel name",channel_name)
                print("Function name",math_function.name)
                print("Source channels",source_channels)
                
            else:
                print('Math dialog Cancel')

                
                
                
#=============================================================================
#%% Main loop - for testing
#=============================================================================

if __name__ == "__main__":
    import sys

    DIALOG_TEST = True
    

    app = QApplication(sys.argv)
    app.setStyle("gtk+") 
    #form = MainWindow(test='legendLine')
    #form = MainWindow(test='FlexiDock')
    #form = MainWindow(test='dialog')
    #form = MainWindow(test='FunctionInputSelector')
    form = MainWindow(test='FkeyButton')
#    form = legendDialog(None)
#    form.exec_()
#    
#    print('linestyle:',form.lineStyle)
    
    form.show()
    form.resize(1200, 800)
    app.exec_()
    
    
        
        
        
