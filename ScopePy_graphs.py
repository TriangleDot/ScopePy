# -*- coding: utf-8 -*-
"""
Created on Sat Aug 16 20:19:52 2014

@author: john

ScopePy Graph library
=========================
Graph plotting and asscociated widgets are defined here

Version
==============================================================================
$Revision:: 177                           $
$Date:: 2016-07-31 21:09:08 -0400 (Sun, 3#$
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

#=============================================================================
#%% TODO list:
#=============================================================================
"""

* GraphSeries - implement transparency
* GraphSeries - Change marker colours
* Chunk handling
* Log scale
* Marker lines : horiz and vertical [done]
    - Delta positions with respect to other markers
* Context menus :
    - Turning on/off axes
    - setting lin/log scale
* Manually editing axis scales
        

"""

#=============================================================================
#%% Imports
#=============================================================================
import sys
import logging
import copy
from collections import OrderedDict

import numpy as np

from PyQt4.QtCore import *
from PyQt4.QtGui import *

# ScopePy libraries
import ScopePy_channel as ch
import ScopePy_utilities as util
import csslib
import ScopePy_colours_and_shapes as col_shapes

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



#=============================================================================
#%% Constants
#=============================================================================
global KEYBOARD


PLOT_HORIZ_SIZE = 350
PLOT_VERT_SIZE = 400

# Size of scene, must be 500 or greater to give the range in
# text sizes
SCENESIZE = 500

DEFAULT_AXIS_MIN = -10.0
DEFAULT_AXIS_RANGE = 20.0
DEFAULT_GRID = np.arange(-10.0,10.0,2)

# Maximum number of markers
MAX_MARKERS = 4


DEBUG = False

# Debug printout
dbg = util.DebugPrint(['all','brief','verbose','HorizMarkerLine'])

"""
Note: QGraphicsItems for this application need to be drawn using
floating point coordinates such as QPointF(), QRectF()

"""


#=============================================================================
#%% Graph widget class definition
#=============================================================================


class GraphWidget(QGraphicsView):
    """
    Basic 2D plot widget for ScopePy
    
    Features:
    * Autoscaling, X,Y or both
    * Panning & zooming with mouse or keyboard
    * Horiz & vertical markers
    * On screen editable axis limits
    
    
    """

    def __init__(self,preferences, parent=None):
        super(GraphWidget, self).__init__(parent)

        # Link to preferences
        # ---------------------
        self.preferences = preferences

        # Setup Scene
        # -------------------------
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(-SCENESIZE/2, -SCENESIZE/2, SCENESIZE, SCENESIZE)
        self.scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        
        #self.setRenderHint(QPainter.Antialiasing) # Has a big effect on performance, turn off by default
        self.setScene(self.scene)
        self.setFocusPolicy(Qt.StrongFocus)

        self.fitInView(self.scene.sceneRect())
        self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.setMouseTracking(True)
        
        # Turn off scroll bars
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        
        
        # add coordinate manager 
        # ----------------------------
        self.coordinateManager = CoordinateManager(self.scene,self)
        
        # Set default axis range
        self.coordinateManager.x_min_DC = DEFAULT_AXIS_MIN
        self.coordinateManager.x_max_DC = DEFAULT_AXIS_MIN + DEFAULT_AXIS_RANGE
        
        self.coordinateManager.y_min_DC = DEFAULT_AXIS_MIN
        self.coordinateManager.y_max_DC = DEFAULT_AXIS_MIN + DEFAULT_AXIS_RANGE
        
        self.coordinateManager.x_grid_major_DC = DEFAULT_GRID
        self.coordinateManager.y_grid_major_DC = DEFAULT_GRID
        
        # Colours
        # ----------------
        self.backgroundColor = QColor(69,65,65)
        #self.backgroundColor.darker(600)
        self.vertMarkerColor = '#FFFF00'
        self.horizMarkerColor = '#81F781'
        
        # Data series traceability
        # ------------------------------
        # Dictionaries for keeping a record of the data series
        # items that are on the graph.
        # Used for re-drawing
        
        # One list for graph series
        self.graphSeries = OrderedDict()
        
        # Separate list of ScopePy channels
        self.channelSeries = OrderedDict()
        
        # Markers
        # -----------
        # dictionary for recording any markers added to the plot
        self.horizontalMarkers = {}
        self.verticalMarkers = {}
        
        
        
        # Axis scales
        # -------------------
        # Used for autoscaling the graph
#        # These are updated every time a series is added
#        self.xmin = DEFAULT_AXIS_MIN
#        self.xmax = DEFAULT_AXIS_MIN + DEFAULT_AXIS_RANGE
#        
#        self.ymin = DEFAULT_AXIS_MIN
#        self.ymax = DEFAULT_AXIS_MIN + DEFAULT_AXIS_RANGE
        
        # draw the widget
        self.draw()
        
        # Minimum sizes
        self.horiz_size = PLOT_HORIZ_SIZE
        self.vert_size = PLOT_VERT_SIZE
        
        
        # Debug dot
#        self.dot = Dot(Qt.red,QPointF(0,0))
#        self.scene.addItem(self.dot)
#        
#        self.scene.addLine(-200,0,200,0,QPen(Qt.red))
#        self.scene.addLine(0,-200,0,200,QPen(Qt.red))
#    
    
     

    def minimumSizeHint(self):
        """
        Set the minimum size
        
        """
        
        return QSize(self.horiz_size,self.vert_size)
        
    
    def sizeHint(self):
        """
        Minimum is the size hint
        
        """
        
        return self.minimumSizeHint()
        
        
        
    def draw(self):
        """
        Initial drawing of widget
        
        """
      

        # Background
        self.background = Background(self.backgroundColor,self.coordinateManager)
        self.scene.addItem(self.background)
        
            
        # Plot box
        self.plotBox = PlotBox(self.coordinateManager)
        

        
        self.scene.addItem(self.plotBox)
        if DEBUG:
            print("PlotBox:",self.plotBox.pos())
         
        
        
        # Axes
        # -----------------
        
        # Centre axes
        self.xCentreAxis = Axis('origin y',self.coordinateManager)
        self.xCentreAxis.tickLabelsEnabled = True 
        #self.xCentreAxis.minorTicksEnabled = False
        self.xCentreAxis.axisTitle_position = "middle"
        
        self.yCentreAxis = Axis('origin x',self.coordinateManager)
        self.yCentreAxis.tickLabelsEnabled = True 
        #self.yCentreAxis.minorTicksEnabled = False
        self.yCentreAxis.axisTitle_position = "middle"
        self.yCentreAxis.axisTitle_end_offset_NC = 0.10
        
        self.scene.addItem(self.xCentreAxis)
        #print("self.xCentreAxis:",self.xCentreAxis.pos())
        self.scene.addItem(self.yCentreAxis)
        
        # Box axes
        self.xBottomAxis = Axis('bottom',self.coordinateManager)
        self.xBottomAxis.tickLabelsEnabled = True
        self.xBottomAxis.axisTitle_position = "middle"
        self.xBottomAxis.setMinorTickPosition("above")
        self.scene.addItem(self.xBottomAxis)
        
        self.xTopAxis = Axis('top',self.coordinateManager)
        self.xTopAxis.tickLabelsEnabled = False
        self.xTopAxis.setMinorTickPosition("below")
        self.xTopAxis.showAxisTitle = False
        self.scene.addItem(self.xTopAxis)
        
        self.yLeftAxis = Axis('left',self.coordinateManager)  
        self.yLeftAxis.tickLabelsEnabled = True
        self.yLeftAxis.setMinorTickPosition("right")
        self.scene.addItem(self.yLeftAxis)
        
        self.yRightAxis = Axis('right',self.coordinateManager) 
        self.yRightAxis.tickLabelsEnabled = False
        self.yRightAxis.setMinorTickPosition("left")
        self.scene.addItem(self.yRightAxis)
        
        
        # Add legend but hide it first
        self.addLegend()
        self.hideLegend()
        
    
    # Axis limits
    # ================
    # TODO: These need to update the plot    
    
    # x axis
    # ---------------
    @property
    def xmin(self):
        return self.coordinateManager.x_data_min_DC
        
    @xmin.setter
    def xmin(self,value):
        if value != self.coordinateManager.x_data_min_DC:
            self.coordinateManager.x_data_min_DC = value
            self.coordinateManager.autoscale(axis='x')
        
        
    @property
    def xmax(self):
        return self.coordinateManager.x_data_max_DC
        
    @xmax.setter
    def xmax(self,value):
        if value != self.coordinateManager.x_data_max_DC:
            self.coordinateManager.x_data_max_DC = value
            self.coordinateManager.autoscale(axis='x')
            
        
    # y axis
    # ---------------
    @property
    def ymin(self):
        return self.coordinateManager.y_data_min_DC
        
    @ymin.setter
    def ymin(self,value):
        if value != self.coordinateManager.y_data_min_DC:
            self.coordinateManager.y_data_min_DC = value
            self.coordinateManager.autoscale(axis='y')
        
        
        
    @property
    def ymax(self):
        return self.coordinateManager.y_data_max_DC
        
    @ymax.setter
    def ymax(self,value):
        if value != self.coordinateManager.y_data_max_DC:
            self.coordinateManager.y_data_max_DC = value
            self.coordinateManager.autoscale(axis='y')
        
        
        
        
    @property
    def xlabel(self):
        """
        Return x axis title
        
        """
        
        return self.xBottomAxis.getAxisTitle()
        
        
    @xlabel.setter   
    def xlabel(self,axis_label):
        """
        Set the text in axis label
        
        Input
        --------
        axis_label : str
        
        """
        
        # Change all the x axis labels
        #self.xCentreAxis.setAxisTitle(axis_label)
        self.xTopAxis.setAxisTitle(axis_label)
        self.xBottomAxis.setAxisTitle(axis_label)
        self.update()
        
        
    @property
    def ylabel(self):
        """
        Return x axis title
        
        """
        
        return self.yLeftAxis.getAxisTitle()
        
        
    @ylabel.setter    
    def ylabel(self,axis_label):
        """
        Set the text in axis label
        
        Input
        --------
        axis_label : str
        
        """
        
        # Change all the y axis labels
        #self.yCentreAxis.setAxisTitle(axis_label)
        self.yLeftAxis.setAxisTitle(axis_label)
        self.yRightAxis.setAxisTitle(axis_label)
        self.update()
        
        
        
    def addSeries(self,graph_series):
        """
        Add graph series to plot
        
        Input
        -----------
        graph_series : GraphSeries object
        
        """
        
        # TODO need to add data as x & y plus marker specs
        # can't add series externally because they need coordinate manager
        
        # Add to graph series list
        self.graphSeries[graph_series.name] = graph_series
        
        # Add to scene
        self.scene.addItem(self.graphSeries[graph_series.name] )
        
        # Update scaling
        self.updateScaling(graph_series.x_DC,graph_series.y_DC)
        
        # Update legend
        self.legend.updateLegend()
    
    
    def addChannel(self,channel,chunkMode='all'):
        """
        Add ScopePy channel to graph
        
        Inputs:
        --------------
        channel : ScopePy_channel
        
        chunkMode : str
            
        Output
        ---------
        channel_series: ChannelGraphSeries object
        
        
        """
        
        # Add channel to the list
        self.channelSeries[channel.name] = ChannelGraphSeries(channel,self.coordinateManager,chunkMode=chunkMode)
        
        # Add channel series object to the scene
        self.scene.addItem(self.channelSeries[channel.name])
        
        #self.channelSeries[channel.name].drawMarkers = False
        
        # Update scaling
        data = channel.data(chunkMode=chunkMode)
        
        if not channel.isEmpty:
            self.updateScaling(data[channel.x_axis],data[channel.y_axis])
            
        # Update legend
        self.legend.updateLegend()
        
        # Return pointer to the ChannelGraphSeries
        return self.channelSeries[channel.name]
        
        
    
    def deleteChannel(self,channel_name):
        """
        Remove channel from plot
        
        """
        
        if channel_name not in self.channelSeries:
            return
            
        # Remove ChannelGraphSeries object from plot
        self.scene.removeItem(self.channelSeries[channel_name])
        
        # Remove channel from internal dictionary
        self.channelSeries.pop(channel_name)
        
        # Update the scaling values with the remaining channels
        self.clearScaling()
        
        for ch_series in self.channelSeries.values():
            channel = ch_series.channel
            data = channel.data(chunkMode=ch_series.chunkMode)
            self.updateScaling(data[channel.x_axis],data[channel.y_axis])
            
            
        
        
    
    def addHorizMarker(self):
        """
        Add a horizontal marker to the plot
        
        Marker is named automatically: H1, H2 ...
        
        """
        
        marker_name = "H%d" % (len(self.horizontalMarkers)+1)
        
        horiz_marker = HorizMarkerLine(self.coordinateManager,
                                       name=marker_name,
                                       markerDict=self.horizontalMarkers)
                                       
        horiz_marker.lineColour = self.horizMarkerColor
        
        self.scene.addItem(horiz_marker)    
        
        # Add marker to the list
        self.horizontalMarkers[marker_name] = horiz_marker
        
        logger.debug('Adding new horizontal marker [%s] at y = %.3f' % (marker_name,horiz_marker.position_DC))
        
        self.update()
        
        
    def addVertMarker(self):
        """
        Add a Vertical marker to the plot
        
        Marker is named automatically: V1, V2 ...
        
        """
        
        marker_name = "V%d" % (len(self.verticalMarkers)+1)
        
        vert_marker = VertMarkerLine(self.coordinateManager,
                                     name=marker_name,
                                     markerDict=self.verticalMarkers)
        
        vert_marker.lineColour = self.vertMarkerColor
        
        self.scene.addItem(vert_marker)    
        
        # Add marker to the list
        self.verticalMarkers[marker_name] = vert_marker
        
        logger.debug('Adding new vertical marker [%s] at x = %.3f' % (marker_name,vert_marker.position_DC))
        
        self.update()
        
        
        
    def deleteHorizMarker(self,marker_name):
        """
        Remove horiz marker
        """
        
        # Extract from dictionary
        marker = self.horizontalMarkers.pop(marker_name,None)
        
        if marker:
            self.scene.removeItem(marker)
            
    
    def deleteVertMarker(self,marker_name):
        """
        Remove vert marker
        """
        
        # Extract from dictionary
        marker = self.verticalMarkers.pop(marker_name,None)
        
        if marker:
            self.scene.removeItem(marker)
        
        
        
    
    def updateScaling(self,xdata,ydata):
        """
        Update the min and max axis values.
        
        Check the min and max x and y values, if they are outside the
        range of the internal values then update them.
        
        Inputs
        -----------
        xdata, ydata : numpy array or list
            x and y data of a new series
            
        """
        
        # Update x
        # ----------------
        update_x = False
        
        # Get min and max for x
        xdata_min = min(xdata)
        xdata_max = max(xdata)
        
        
        if xdata_min < self.coordinateManager.x_data_min_DC:
            self.coordinateManager.x_data_min_DC = xdata_min
            update_x = True
            
        if xdata_max > self.coordinateManager.x_data_max_DC:
            self.coordinateManager.x_data_max_DC = xdata_max
            update_x = True
            
        if update_x:
            self.coordinateManager.autoscale('x')
            
        
            
            
        # Update y
        # ----------------
        update_y = False
        
        # Get min and max for x
        ydata_min = min(ydata)
        ydata_max = max(ydata)
        
        
        if ydata_min < self.coordinateManager.y_data_min_DC:
            self.coordinateManager.y_data_min_DC = ydata_min
            update_y = True
            
        if ydata_max > self.coordinateManager.y_data_max_DC:
            self.coordinateManager.y_data_max_DC = ydata_max
            update_y = True
            
            
        # Trigger updates
        if update_y:
            self.coordinateManager.autoscale('y')
            
            
    def clearScaling(self):
        """
        Reset the graph scaling min and max values
        
        """
        
        self.coordinateManager.reset_data_min_max()
        
        
            
            
    def update(self):
        """ 
        Reimplement update function to check if any plots are on screen
        but not visible
        """
        
        
        
        # Check GraphSeries
        # -------------------------
        for name in self.graphSeries:
            self.graphSeries[name].recalculate = True
            self.graphSeries[name].update()
          
        # Check channels
        # -------------------------
        for name in self.channelSeries: 
            self.channelSeries[name].recalculate = True
            self.channelSeries[name].updateFromChannel()
            self.channelSeries[name].forceUpdate()
            
        # Update legend
        # -------------------
        if hasattr(self,'legend'):
            self.legend.updateLegend()
        
            
        # Check Horizontal marker lines
        # -------------------------------
        for line in self.horizontalMarkers.values():
            line.update()
            
        # Check Vertical marker lines
        # -------------------------------
        for line in self.verticalMarkers.values():
            line.update()
            
        # Axis limit editors
        # --------------------
        #self.xMinEditor.update(self.coordinateManager.plotBox2scene()) 
                
        # Run normal update
        super().update()
        
        
    def updateChannel(self,channel_name):
        """
        Force a channel to re-draw
        
        This is normally connected to a signal from the ScopePy_channel class
        
        Input
        -------
        channel_name: str
        
        """
        
        if not channel_name in self.channelSeries:
            return
            
        
        self.channelSeries[channel_name].updateFromChannel()
        self.channelSeries[channel_name].forceUpdate()


    def recalculate_graphs(self):
        """ 
        Tell all GraphSeries and derivatives to recalculate their coordinates.
        This is called by Coordinate manager when the axis limits change
        """
      
        # Check GraphSeries
        # -------------------------
        for name in self.graphSeries:
            self.graphSeries[name].recalculate = True
            
          
        # Check channels
        # -------------------------
        for name in self.channelSeries: 
            self.channelSeries[name].recalculate = True
            
                    
        
        
    def plot2image(self):
        """
        Copy plot to an image
        
        Output
        -------
        image : QImage()
        
        """
        #imageRect = self.coordinateManager.plotBox2scene()
        imageRect = self.coordinateManager.viewport2sceneRect()
        coords = (imageRect.x(),imageRect.y(),imageRect.width(),imageRect.height())
        logger.debug("plot2image: x = %d, y = %d, w = %d, h = %d" % coords)
        
        
        image_size = QSize(imageRect.width(),imageRect.height())
        image = QImage(image_size,QImage.Format_RGB16)
        logger.debug("Image dimensions:")
        #print(image.rect())
        
        self.scene.render(QPainter(image),target=QRectF(image.rect()),
                          source=imageRect,mode=Qt.KeepAspectRatio)
        
        
        return image
        
        
        
    def plot2clipboard(self):
        """
        Copy plot to clipboard
        
        """
        
        image = self.plot2image()
        
        clipboard = QApplication.clipboard()
        
        clipboard.setImage(image)
        
        
    def focusOnPlot(self):
        """
        Put keyboard focus on the plot area. This allows panning and zooming
        with the keyboard.
        
        """
        self.setFocus()
        self.plotBox.setFocus()
        self.plotBox.grabKeyboard()

    
    # Autoscaling functions:
    # ---------------------------------
        
    def autoscale(self):
        
        logger.debug("Autoscale selected")
        
        self.coordinateManager.autoscale()
        
        
    def autoscaleX(self):
        
        logger.debug("Autoscale X selected")
        
        self.coordinateManager.autoscale('x')
        
        
    def autoscaleY(self):
        
        logger.debug("Autoscale Y selected")
        
        self.coordinateManager.autoscale('y')
        
        
        
    # StyleSheet functions
    # ---------------------------------------
    def setStyleSheet(self,css_str):
        """
        Set the style of the graphs using a CSS stylesheet.
        
        Input
        ----------
        css_str : str
            CSS stylesheet which has the following entries (others are ignored):
            
            standard_plot{
                plot-background-color: #000000;
                grid-color: #003400;
                axis-color: #444444;
                axis-label-color: #444444;
                axis-title-color:#666666;
                axis-limits-color: #666666;
                axis-limits-background:#303030;
                horiz-marker-color: #88a02f;
                vert-marker-color: #18a02f;
                border-color: #212121;
                border-grid:1;
                border-grid-color: #a00000;
                vert-marker-color:#FFFF00;
                horiz-marker-color:#81F781;
                legend-outlineColor:
                legend-outlineWidth: 3
                legend-outlineMargin: 4
                legend-cellBorderColor:
                legend-cellBackgroundColor:
                legend-cellBorderWidth: 1
                legend-backgroundColor:
                legend-textColor:
                legend-fontsize: 8;
            }
            
        TODO: selected
        
        """
        
        # Convert CSS to dictionary
        # --------------------------------
        styles = csslib.getCss(css_str)
        
        # Check for the 'standard_plot' key
        if 'standard_plot' not in styles:
            return
        
        # Extraction Function
        def getColor(key,default_colour):
            return QColor(styles['standard_plot'].get(key,default_colour))
        
        # Set styles
        # -----------------------
        
        # Background/border colour
        self.background.color = getColor('border-color',QColor(Qt.darkGray).name())
        self.background.gridEnabled = styles['standard_plot'].get('border-grid',0)==1
        self.background.gridColor = getColor('border-grid-color',QColor(Qt.red).name())
        
        # actual plot background
        self.plotBox.borderColor = getColor('grid-color',QColor(Qt.green).name())
        self.plotBox.gridColor = getColor('grid-color',QColor(Qt.green).name())
        self.plotBox.backgroundColor = getColor('plot-background-color',QColor(Qt.black).name())    
        
        
        # Change axis colours
        for axis in [self.xCentreAxis,self.xBottomAxis,self.xTopAxis,
                     self.yCentreAxis,self.yLeftAxis,self.yRightAxis]:
        
            axis.axisColor = getColor('axis-color',QColor(Qt.gray).name())
            axis.tickLabelColor = getColor('axis-label-color',QColor(Qt.gray).name())
            axis.axisTitle_color = getColor('axis-title-color',QColor(Qt.gray).name())        
            
      

        # Markers
        # TODO: Not consistent with other colours - Fix this
        self.vertMarkerColor = styles['standard_plot'].get('vert-marker-color','#FFFF00')
        self.horizMarkerColor = styles['standard_plot'].get('horiz-marker-color','#81F781')
        
        
        # Legend
        self.legend.outlineColour = getColor('legend-outlineColor',QColor(Qt.darkGray).name())
        self.legend.outlineWidth = int(styles['standard_plot'].get('legend-outlineWidth',2))
        self.legend.outlineMargin = int(styles['standard_plot'].get('legend-outlineMargin',3))
        self.legend.cellBorderColour = getColor('legend-cellBorderColor',QColor(Qt.black).name())
        self.legend.cellBackgroundColour = getColor('legend-cellBackgroundColor',QColor(Qt.black).name())
        self.legend.cellWidth = int(styles['standard_plot'].get('legend-cellBorderWidth',1))
        self.legend.backgroundColour = getColor('legend-backgroundColor',QColor(Qt.black).name())
        self.legend.textColour = getColor('legend-textColor',QColor(Qt.lightGray).name())
        self.legend.fontsize = int(styles['standard_plot'].get('legend-fontsize',8))
      
      

          
    def addLegend(self):
        """
        Add legend to plot
        
        """
        
        self.legend = GraphLegend(self.coordinateManager,self.channelSeries)
        self.scene.addItem(self.legend)     
        
        # Set default position
        self.legend.upper_right()
        
        
        
    def hideLegend(self):
        """
        Hide legend
        """
        
        if hasattr(self,'legend'):
            self.legend.hide()
            
            
            
    def showLegend(self):
        """
        show legend
        """
        
        
        if hasattr(self,'legend'):
            self.legend.show()
            self.legend.upper_left()
        
        
        
        


#=============================================================================
#%% Graphics items
#=============================================================================


# QGraphicsItems need the following methods
# *boundingRect
# *shape
# *paint

class Dot(QGraphicsItem):

    Rect = QRectF(-5, 5, 10, 10)

    def __init__(self, color, position):
        super(Dot, self).__init__()
        self.color = color
        
        self.setPos(position)
        


    def boundingRect(self):
        return Dot.Rect


    def shape(self):
        path = QPainterPath()
        path.addEllipse(QPointF(0,0),10,10)
        return path


    def paint(self, painter, option, widget=None):
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(Dot.Rect)
        

       


#=============================================================================
#%% Axis classes
#=============================================================================
# Axis label positions
LEFT = -1
RIGHT = 1
ABOVE = -1
BELOW = 1  

# Standard axis positions
# key is used for testing inputs, value is used to determine orientation
AXIS_POSITIONS = {'left':'vert','right':'vert',
                  'top':'horiz','bottom':'horiz',
                  'origin x':'vert','origin y':'horiz'}
                  

                           
DEFAULT_AXIS_SETUP = {
    'left':{'type':'vert','title side position':'left','title position':'middle','visible':True,'limitEditors':True},
    'right':{'type':'vert','title side position':'right','title position':'middle','visible':True,'limitEditors':False},
    'top':{'type':'horiz','title side position':'above','title position':'middle','visible':True,'limitEditors':False},
    'bottom':{'type':'horiz','title side position':'below','title position':'middle','visible':True,'limitEditors':True},
    'origin x':{'type':'vert','title side position':None,'title position':None,'visible':False,'limitEditors':False},
    'origin y':{'type':'horiz','title side position':None,'title position':None,'visible':False,'limitEditors':False}
    }
      
class Axis(QGraphicsItem):
    """Draw an axis at any position on the graph
    
    
    TODO
    --------
    * Sort out coordinate system used
        - specified in data coordinates
    * Tick label font sizes
    * major and minor ticks
    
    """
   

    def __init__(self, position,coordinateManager):
        """
        Axis object with position
      
        
        Inputs
        -----------
        position: str
            'left', 'right', 'top','bottom', 'origin x', 'origin y'
        
        """
        super(Axis, self).__init__()
        
        # Coordinates
        # ------------------
        self.coordinateManager = coordinateManager
        
        # Colours
        # --------------
        self.axisColor = Qt.gray
        self.axisTransparency = 255
        
        self.tickLabelColor = Qt.gray
        self.tickLabelTransparency = 255
        
        
        # Position and orientation
        # -------------------------------
        assert position in DEFAULT_AXIS_SETUP,"Axis:Unknown axis position [%s]" % position
        self.position = position
        self.axis_type = DEFAULT_AXIS_SETUP[position]['type']
          
        
        if self.axis_type == "horiz":
            # This is a horizontal axis
            self.clipRectFunction = self.horizClipRect
            self.drawTickFunction = self.drawHorizontalAxisTicks
            self.get_tick_labels = self.coordinateManager.x_grid_major_labels
            self.which_end = self.which_end_horiz
            
            # Axis limit editors
            self.minLimitEditor = AxisLimitEditor(self.coordinateManager,'x min',norm_coords=False,parent=self)
            self.maxLimitEditor = AxisLimitEditor(self.coordinateManager,'x max',norm_coords=False,parent=self)
        else:
            # Vertical axis
            self.clipRectFunction = self.vertClipRect
            self.drawTickFunction = self.drawVerticalAxisTicks
            self.get_tick_labels = self.coordinateManager.y_grid_major_labels
            self.which_end = self.which_end_vert
            
            # Axis limit editors
            self.minLimitEditor = AxisLimitEditor(self.coordinateManager,'y min',norm_coords=False,parent=self)
            self.maxLimitEditor = AxisLimitEditor(self.coordinateManager,'y max',norm_coords=False,parent=self)

        # Special case for clipping rectangle function for origin axis types
#        if self.position.startswith("origin"):
#            self.clipRectFunction = self.originClipRect
# TODO : This doesn't work

        # Initialise clipping rectangle            
        self.clipRect = QRect()
            
        # intialise position coordinates
        # position_DC = [x1,y1,x2,y2]
        # This is where the axis is drawn in Data coordinates
        self.position_DC = [0,0,0,0]
        self.getPosition()
        
        # Ticks
        # ---------------
        self.tickLength = 0.02
        self.tickSpacing = 2
        self.tickValues = [-10,-5,0,5,10]
        
        # Minor ticks
        # -----------------
        self.minorTickSpacing = 2
        self.minorTickLength = self.tickLength/4
        self.minorTickPosition = "above"
        self.minorTickValues = []
        # See method setMinorTickPosition for options
        
        
        
        # Tick labels
        # ------------------
        self.tickLabelOffset_NC = 0.01
        
        # Set default positions
        if self.axis_type == "vert":
            self.tickLabelPosition = LEFT
        else:
            self.tickLabelPosition = BELOW
            
            
        self.tickLabelWidth_NC = 0.05
        self.tickLabelHeight_NC = 0.05
        self.tickFontSize_PX = 11
        self.font = QFont() #QFont('Decorative', 2) #QFont("courier new",self.tickFontSize)
        
        # Axis limit editors
        # --------------------
        self.minLimitEditor.setVisible(DEFAULT_AXIS_SETUP[position]['limitEditors'])
        self.maxLimitEditor.setVisible(DEFAULT_AXIS_SETUP[position]['limitEditors'])
        
        # Axis title
        # --------------------
        self.axisTitle_item = QGraphicsTextItem(parent=self)
        self.axisTitle_item.setTextInteractionFlags(Qt.TextEditable)
        
        
        self.axisTitle_side_position = DEFAULT_AXIS_SETUP[position]['title side position']
        self.axisTitle_position = DEFAULT_AXIS_SETUP[position]['title position']
        self.showAxisTitle = DEFAULT_AXIS_SETUP[position]['visible']
        
        
        if self.axis_type == "vert":
            self.axisTitle = "y axis"
            self.axisTitle_gap_offset_NC = 0.08   # gap between title and axis
        else:
            self.axisTitle = "x axis"
            self.axisTitle_gap_offset_NC = 0.08   # gap between title and axis
            
        
        self.axisTitle_end_offset_NC = 0.1 # gap from end of axis to title
        self.axisTitle_font = QFont()
        self.axisTitle_fontSize_PX = 14
        self.axisTitle_color = Qt.white
        
        self.axisTitle_item.setPlainText(self.axisTitle)
        
        # TODO : This is for testing
        #self.axisTitle = "%s : %s : %s" % (self.axis_type,self.position,self.axisTitle_side_position)
        
        
        
        
        
        # Flags
        # ------------
        self.tickLabelsEnabled = True
        self.minorTicksEnabled = True
      
      

    def setAxisTitle(self,title_text):
        """
        Change the text in the axis title
        
        Inputs
        -------
        title_text : str
            new text to go in the axis
            
        """
        self.axisTitle = title_text
        self.axisTitle_item.setPlainText(self.axisTitle)
        
        
        
    def getAxisTitle(self):
        """
        Return axis title text
        
        Output
        -------
        title : str
        
        """
        
        return self.axisTitle_item.toPlainText()


    def boundingRect(self):
        
        
        x1,y1,x2,y2 = self.position2scene()
        
        # Get width of bounding rectangle
        if self.axis_type == "vert":
            tl = 2*self.coordinateManager.normWidth2scene(self.tickLength)
            rect = QRectF(x1 - tl/2,y1, tl,abs(y2-y1))
            #print("%s rect: " % self.axis_type,rect)
        else:
            tl = 2*self.coordinateManager.normHeight2scene(self.tickLength)
            rect = QRectF(x1,y1 - tl/2, abs(x2-x1),tl)
            
            
        
        return rect


    def shape(self):
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path
        
    
        


    def paint(self, painter, option, widget=None):
        
        x1,y1,x2,y2 = self.position2item()
        
        # Calculate tick labels
        # This is a calculation from the coordinate manager, only want
        # to do this once per paint event. So we calculate the values
        # here, put them in class variables so the functions called here can
        # use them without recalculating.
        self.tickValues = self.calcTickValues("major")
        self.minorTickValues = self.calcTickValues("minor")
        
        # Set clip rectangle 
        # -----------------------
        
        painter.setClipRect(self.clipRect)
        painter.setClipping(True)
        
        
        
        if DEBUG:
            painter.setPen(QColor(Qt.green))
            painter.drawRect(self.clipRect)
        
        
        # Set composition mode
        # to overwrite
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        
        
        
        # Draw axis line
        axisColour = QColor(self.axisColor)
        axisColour.setAlpha(self.axisTransparency)
        pen = QPen(axisColour)
        pen.setWidth(0)
        painter.setPen(pen)
        painter.drawLine(QPointF(x1,y1),QPointF(x2,y2))
        painter.setFont(self.font)
      
        
        # Draw ticks
        self.drawTickFunction(painter)
        
        # Draw tick labels
        if self.tickLabelsEnabled:
            labelColour = QColor(self.tickLabelColor)
            labelColour.setAlpha(self.tickLabelTransparency)
            pen = QPen(labelColour)
            pen.setWidth(0)
            painter.setPen(pen)
            self.drawAxisTickLabels(painter)
            
            
        # Draw axis title
        self.drawAxisTitle(painter)
        
        if DEBUG:
            painter.save()
            painter.setPen(QColor(Qt.red))
            painter.drawRect(self.mapRectFromScene(self.boundingRect()))
            painter.restore()
        
        

    def drawHorizontalAxisTicks(self,painter):
        """ Draw all vertical ticks on horizontal axis major and minor
        
        """
        
        x1,y1,x2,y2 = self.position2item()
        yc = (y1+y2)/2
        
        # Calculate tick length
        tickLength = self.coordinateManager.normHeight2item(self,self.tickLength)
        
        
        # Draw major ticks
        for tick in self.tickValues:
            # Draw tick line
            painter.drawLine(QPointF(tick,yc-tickLength/2),
                             QPointF(tick,yc+tickLength/2))
        
            
        # Draw minor ticks
        if self.minorTicksEnabled:
            
            # Calculate tick length
            minorTickLength = self.coordinateManager.normHeight2item(self,self.minorTickLength)
            
            # Set tick position
            if self.minorTickPosition in ["above","right"]:
                ybottom = yc
                ytop = yc-minorTickLength
                
            elif self.minorTickPosition in ["centre","center"]:
                ybottom = yc-minorTickLength/2
                ytop = yc+minorTickLength/2
                
            else: # "below" or "left"
                ybottom = yc+minorTickLength
                ytop = yc
            
            for minorTick in self.minorTickValues:
                painter.drawLine(QPointF(minorTick,ybottom),
                                 QPointF(minorTick,ytop))
                    
            
        
    
    def drawVerticalAxisTicks(self,painter):
        """ Draw all ticks on vertical axis major and minor
        
        """
        
        x1,y1,x2,y2 = self.position2item()
        xc = (x1+x2)/2
        
        # Calculate tick length
        tickLength = self.coordinateManager.normWidth2item(self,self.tickLength)
        
        for tick in self.tickValues:
            # Draw tick line
            painter.drawLine(QPointF(xc-tickLength/2,tick),
                             QPointF(xc+tickLength/2,tick))
            
        # Draw minor ticks
        if self.minorTicksEnabled:
            
            # Calculate tick length
            minorTickLength = self.coordinateManager.normWidth2item(self,self.minorTickLength)
            
            # Set tick position
            if self.minorTickPosition in ["above","right"]:
                xleft = xc
                xright = xc+minorTickLength
                
            elif self.minorTickPosition in ["centre","center"]:
                xleft = xc-minorTickLength/2
                xright = xc+minorTickLength/2
                
            else: # "below" or "left"
                xleft = xc-minorTickLength
                xright = xc
            
            for minorTick in self.minorTickValues:
                painter.drawLine(QPointF(xleft,minorTick),
                                 QPointF(xright,minorTick))
                                 
           

    
            
        
            
        
    def drawAxisTickLabels(self,painter):
        """Draw the tick labels on the axis
        The label text comes from the coordinate manager fully formatted
        """
        
        # Setup
        # -------------------------------------
        x1,y1,x2,y2 = self.position2item()      
        
        
        # Calculate preferred width and height of text rect
        tickLabelWidth_IC = self.coordinateManager.normWidth2item(self,self.tickLabelWidth_NC)
        tickLabelHeight_IC = self.coordinateManager.normHeight2item(self,self.tickLabelHeight_NC)

        # Define a template rectangle in which to draw text
        # This is used to get the actual text rectange later
        tickLabelRect = QRectF(0,0,tickLabelWidth_IC,tickLabelHeight_IC)
        #print("Initial Tick label rect : \n",tickLabelRect )
        
        # Setup font height
        # TODO : Scale this for when widget gets resized?
        self.font.setPixelSize(self.tickFontSize_PX)
        painter.setFont(self.font)        
        
        
        # Calculate offset from axis
        if self.axis_type == "vert":
            tickLabelOffset_IC = self.coordinateManager.normHeight2item(self,self.tickLabelOffset_NC)
        else:
            tickLabelOffset_IC = self.coordinateManager.normWidth2item(self,self.tickLabelOffset_NC)
             
        # Set Alignment
        tickLabelAlignment = Qt.AlignVCenter | Qt.AlignHCenter
        
        # Get labels from coordinate manager
        tickLabelList = self.get_tick_labels()
        
        # Checkpoint - this should always be true
        assert len(tickLabelList)==len(self.tickValues),"Tick labels and tick values are different lengths [%s]" % self.axis_type
        
        
               
        # Draw tick labels
        # --------------------------------------------------
               
        for index,tick in enumerate(self.tickValues):
            # Exclude first 
            #if index == 0:
            #    continue
            
            # Create label text
            tickLabel = tickLabelList[index]
            
            # Get actual label width and height
            labelRect = painter.boundingRect(tickLabelRect,tickLabelAlignment
                ,tickLabel)

            txtWidth = labelRect.width()
            txtHeight = labelRect.height()
            
            if self.axis_type == "vert":
                xpos = x1 + self.tickLabelPosition*(labelRect.width()+ tickLabelOffset_IC)
                ypos = tick - labelRect.height()/2
            else:
                xpos = tick - labelRect.width()/2 
                ypos = y1 + self.tickLabelPosition*(labelRect.height()/2 + tickLabelOffset_IC)
                
            
            tickLabelRect = QRectF(xpos,ypos,tickLabelWidth_IC,tickLabelHeight_IC)
            
#            if DEBUG:
#                print("Tick [%0.1f] : [%.1f,%.1f, %.1f,%.1f ]" % (tick,
#                      tickLabelRect.x(),tickLabelRect.y(),
#                      tickLabelRect.width(),tickLabelRect.height()))
            
            
            
            painter.drawText(QRectF(xpos,ypos,txtWidth,txtHeight),
                             tickLabelAlignment,tickLabel)
            
            if DEBUG:
                painter.setPen(QColor(Qt.red))
                painter.drawRect(tickLabelRect)
                
                painter.setPen(QColor(Qt.green))
                painter.drawRect(QRectF(xpos,ypos,txtWidth,txtHeight))


        # Set position of AxisLimitEditors
        editorRect = self.minLimitEditor.boundingRect()
        if self.axis_type == 'horiz':
            ypos = y1 + self.tickLabelPosition*(editorRect.height()/2 + tickLabelOffset_IC)
            self.minLimitEditor.setPosition(QPointF(x1,ypos),'centre top')
            self.maxLimitEditor.setPosition(QPointF(x2,ypos),'centre top')
        else:
            xpos = x1 + self.tickLabelPosition*(editorRect.width()+ tickLabelOffset_IC)
            self.minLimitEditor.setPosition(QPointF(xpos,y2),'bottom left')
            self.maxLimitEditor.setPosition(QPointF(xpos,y1),'bottom left')


    def setTickLabelPosition(self,position_string):
        """ Set Axis label position
        
        Inputs
        ------------
        position_string = "above","below" for horizontal axis
                          "left","right" for vertical axis

        """
        
        positions = {"above":ABOVE,"below":BELOW,"left":LEFT,"right":RIGHT}
        
        # If unknown position just ignore it
        if position_string not in positions:
            return
            
        self.tickLabelPosition = positions[position_string]
        
        
        
    def setFont(self,font):
        """ Set new font and get font metrics for it
        """
        
        self.font = font
        
        
        
    def setMinorTickPosition(self,position):
        """Set the minor tick positions
        The options are:
        "above" = above axis line (horizontal axis)
        "below" = below axis line (horizontal axis)
        "left" = left of axis line (vertical axis)
        "right" = right of axis line (vertical axis)
        "centre" or "center" = line either side of axis line
        """
        
        if position.lower() in ["above","below","left","right","center","centre"]:
            self.minorTickPosition = position.lower()
            
     

    def drawAxisTitle(self,painter):
        """ Draw the axis title next to the axis
        
        """
        
        # Check title is visible
        # ---------------------------
        if self.axisTitle_position==None or self.axisTitle_side_position==None or self.showAxisTitle==False:
            # Don't show title
            self.axisTitle_item.setVisible(False)
            return
        
        # Get axis position
        # ---------------------------
        x1,y1,x2,y2 = self.position2item()
        
        
        # QGraphicsTextItem version
        # ==============================================================
        # Setup text item
        # ------------------------------
        #self.axisTitle_item.setPlainText(self.axisTitle)
        
        self.axisTitle_item.setFont(self.axisTitle_font)
        self.axisTitle_item.setDefaultTextColor(QColor(self.axisTitle_color))
        
              
        # Position axis title
        # ----------------------------
        
        # Get bounding rectangle
        txtRect = self.axisTitle_item.boundingRect()

        axisTitlePos = self.calcAxisTitlePosition(txtRect)
        
        # Draw axis using QGraphicsTextItem
        # -----------------------------------------
        # final rectangle
#        rect = QRect(axisTitlePos.x()-txtRect.width()/2,
#                     axisTitlePos.y()-txtRect.height()/2,
#                     txtRect.width(),txtRect.height())
        if self.axis_type == "vert":
            self.axisTitle_item.setRotation(-90)
            
        self.axisTitle_item.setPos(axisTitlePos)
        
        
        # Draw axis using painter
        # ==============================================================
        # 
#        self.axisTitle_font.setPixelSize(self.axisTitle_fontSize_PX)
#        # Set Alignment
#        txtAlignment = Qt.AlignVCenter | Qt.AlignHCenter
#        
#        # Get bounding rectangle
#        txtRect = painter.boundingRect(QRect(0,0,0,0),
#                                       txtAlignment,self.axisTitle)
#                                       
#
#        axisTitlePos = self.calcAxisTitlePosition(txtRect)
#        
#        # Store painter state
#        painter.save()
#        
#        painter.setFont(self.axisTitle_font)
#        painter.setPen(QColor(self.axisTitle_color))
#        
#        # Draw axis text
#        if self.axis_type == "vert":
#            # Rotate text by 90 degrees
#            #painter.rotate(-90.0)
#            
#            # Rotation has affected the whole painter coordinate system
#            # flip x and y, then negate y to get back to correct position
#            painter.drawText(QPointF(axisTitlePos.x(),axisTitlePos.y()),self.axisTitle)
#        else:
#            painter.drawText(axisTitlePos,self.axisTitle)
#            
#        
#        
#        
#        # Restore painter state - remove rotations, colours etc
#        painter.restore()
        
        

    def calcAxisTitlePosition(self,text_rect):
        """ Calculate the axis title position in local coordinates 
        based on settings
        
        Input
        ----------
        text_rect = bounding rectangle of Axis title
        
        Output
        --------
        axisTitlePosition_IC = QPointF()
        
        """
        
        # Get axis position
        # ---------------------------
        x1,y1,x2,y2 = self.position2item()
        
        
            
        # Calculate axis position
        # --------------------------
        gap_IC = self.calcAxisTitleGap()
        offset_from_end_IC = self.calcAxisTitleOffsetFromEnd(text_rect)
        
        # Return position of title
        # -------------------------
        if self.axis_type == "vert":
            xt_IC = x2 - gap_IC - text_rect.height()*0.5
            yt_IC = y1 + offset_from_end_IC
            #print("Vert Axis title pos = [%.1f,%.1f]" % (xt_IC,yt_IC))
        else:
            xt_IC = x2 - offset_from_end_IC
            yt_IC = y2 - gap_IC - text_rect.height()*0.5
            #print("Horiz Axis title pos = [%.1f,%.1f]" % (xt_IC,yt_IC))
            
        return QPointF(xt_IC,yt_IC)
        
    
    def calcAxisTitleGap(self):
        """ Calculate the gap between the axis title and the axis
        Based on the specified positions like "above", "below", "left" and "right"
        
        Output
        --------
        gap_IC = gap between axis title and axis in item coordinates
        
        """
        
        # Get direction factor
        # -------------------------
        dir_dict = {"above":1,"below":-1,"left":1,"right":-1}
        
        if self.axisTitle_side_position in dir_dict:
            dirFactor = dir_dict[self.axisTitle_side_position]
        else:
            dirFactor = 1
            
        # Calculate gap
        # -------------------
        if self.axis_type == "vert":
            gap_IC = dirFactor*self.coordinateManager.normWidth2item(self,self.axisTitle_gap_offset_NC)
        else:
            gap_IC = dirFactor*self.coordinateManager.normHeight2item(self,self.axisTitle_gap_offset_NC)
            
        return gap_IC
        
        
    def calcAxisTitleOffsetFromEnd(self,text_rect_IC):
        """Calculate the axis title offset from the end of the axis
        
        Input
        ----------
        text_rect_IC = bounding rectangle of Axis title in local coordinates
        
        Output
        ---------
        end_offset_IC = in item coordinates
        """
        
        # Get axis position
        # ---------------------------
        x1,y1,x2,y2 = self.position2item()
    
            
        # AxisTitle in middle case
        # ------------------------------
        if self.axisTitle_position == "middle":
            # Set to a middle of plotBox in either horizontal or vertical
            
            if self.axis_type == "vert":
                offset_IC = self.coordinateManager.normHeight2item(self,0.5)
            else:
                offset_IC = self.coordinateManager.normWidth2item(self,0.5)
            
            
        else:
            # Numeric offsets in normalised units
            if self.axis_type == "vert":
                offset_IC = self.coordinateManager.normHeight2item(self,
                                                   self.axisTitle_end_offset_NC)

                
            else:
                offset_IC = self.coordinateManager.normWidth2item(self,
                                                   self.axisTitle_end_offset_NC)
                                                   
                                                   
        # Make sure the offset does not put the text outside plotbox
        # offset must not be less than half the length of the text
        end_offset_IC = max(offset_IC-text_rect_IC.width()/2,text_rect_IC.width()/2)
        
        
        return end_offset_IC
        
      
    def getPosition(self):
        """
        Update position of axis in Data coordinates from coordinate manager 
        according to current axis limits.
        
        """
    
        # Setup length of axis according to axis type
        if self.axis_type == "vert":
            # Note the min and max are flipped because of the
            # inversion between data and item coordinates on the y axis
            self.position_DC[3] = self.coordinateManager.y_min_DC
            self.position_DC[1] = self.coordinateManager.y_max_DC
        else:
            self.position_DC[0] = self.coordinateManager.x_min_DC
            self.position_DC[2] = self.coordinateManager.x_max_DC
        
        # Setup position
        if self.position == "left":
            self.position_DC[0] = self.coordinateManager.x_min_DC
            self.position_DC[2] = self.coordinateManager.x_min_DC
            
        elif self.position == "right":
            self.position_DC[0] = self.coordinateManager.x_max_DC
            self.position_DC[2] = self.coordinateManager.x_max_DC
            
        elif self.position == "origin x":
            self.position_DC[0] = 0
            self.position_DC[2] = 0
            
        elif self.position == "bottom":
            self.position_DC[1] = self.coordinateManager.y_min_DC
            self.position_DC[3] = self.coordinateManager.y_min_DC
            
        elif self.position == "top":
            self.position_DC[1] = self.coordinateManager.y_max_DC
            self.position_DC[3] = self.coordinateManager.y_max_DC
            
        elif self.position == "origin y":
            self.position_DC[1] = 0
            self.position_DC[3] = 0
            
        
        
    def position2item(self):
        """Convert axis position from Data to item coordinates
        
        Output
        -------------
        position_IC = (x1,y1,x2,y2) position in item coordinates
        
        """
        
        
        # Update position
        self.getPosition()
        
        # Convert position property into two lists
        x_DC = [self.position_DC[0],self.position_DC[2]]
        y_DC = [self.position_DC[1],self.position_DC[3]]
        
        x_IC,y_IC = self.coordinateManager.data2item(self,x_DC,y_DC)
        
        # Recalculate clip rect
        self.clipRectFunction(x_IC,y_IC)
        
        
        # Return a tuple of item coordinates (x1,y1,x2,y2) 
        return (x_IC[0],y_IC[0],x_IC[1],y_IC[1])
        
        
        
    def position2scene(self):
        """Convert axis position from Data to scene coordinates
        
        Output
        -------------
        position_SC = (x1,y1,x2,y2) position in scene coordinates
        
        """
        # Update position
        self.getPosition()
        
        
        # Convert position property into two lists
        x_DC = [self.position_DC[0],self.position_DC[2]]
        y_DC = [self.position_DC[1],self.position_DC[3]]
        
        x_SC,y_SC = self.coordinateManager.data2scene(x_DC,y_DC)
             
        # Return a tuple of scene coordinates (x1,y1,x2,y2) 
        return (x_SC[0],y_SC[0],x_SC[1],y_SC[1])
        
        
    def vertClipRect(self,x_IC,y_IC):
        """
        Calculate clip rectangle for vertical axis
        """
        
        # Get width of rectangle from tick spacing
        width_IC = 10*self.coordinateManager.normWidth2item(self,self.tickLength)
        
        self.clipRect = QRectF(x_IC[0]-width_IC/2,min(y_IC),width_IC,abs(max(y_IC)-min(y_IC)))
        
        if self.position == "origin y":
            print("\nAxis %s %s: Updating vertical clipRect"  % (self.axis_type,self.position))
            print("\t",self.clipRect)
            
    
    def horizClipRect(self,x_IC,y_IC):
        """
        Calculate clip rectangle for vertical axis
        """
        
        # Get width of rectangle from tick spacing
        height_IC = 6*self.coordinateManager.normHeight2item(self,self.tickLength)
        
        self.clipRect = QRectF(x_IC[0],y_IC[0]-height_IC/2,abs(x_IC[1]-x_IC[0]),height_IC)
        
        
        
    def originClipRect(self,x_IC,y_IC):
        """
        Return clip rectangle for origin axis types. This is just the plotBox
        clipping rectange
        
        """
        # TODO : This doesn't work
        return self.coordinateManager.itemClipRect(self)
        
        
        
        
    def calcTickValues(self,tick_type):
        """ Gets tick values from coordinate manager and translates
        to local coordinates
        
        Inputs
        ---------
        tick_type = "major" or "minor"
        """
        # Validate inputs
        assert tick_type in ["major","minor"], "tick_type [%s] is unknown" % tick_type
        
        # Function selector
        # equivalent of switch/case
        tickFunctionDict = {
            ("horiz","major"):self.coordinateManager.get_xGridMajor_IC,
            ("horiz","minor"):self.coordinateManager.get_xGridMinor_IC,
            ("vert","major"):self.coordinateManager.get_yGridMajor_IC,
            ("vert","minor"):self.coordinateManager.get_yGridMinor_IC}
            
        # Get tick values
        tickValues_IC = tickFunctionDict[(self.axis_type,tick_type)](self)
        
        return tickValues_IC
        
            
    def calcTest(self):
        """Test calculations - debugging
        """
        
        x1,y1,x2,y2 = self.position2item()
        
        tmp = self.axis_type
        
        self.axis_type = "horiz"
        ht = self.calcTickValues("major")
        
        self.axis_type = "vert"
        vt = self.calcTickValues("major")
        
        self.axis_type = tmp
        
        print("\n\n------------------------------")
        print("Position",x1,y1,x2,y2)
        print("horiz ticks",ht)
        print("vert ticks",vt)
        
        return ht,vt
       
    # ------------------------------------------------------------------   
    # Wheel Event handling
    # ------------------------------------------------------------------
        
    def wheelEvent(self,event):
        """ Mouse wheel turned over widget
        
        zoom the scales of both axes in the graph
        
        """
        
        # Get how much the wheel has turned
        numDegrees = event.delta()/8
        numSteps = numDegrees/15
        direction = -np.sign(numSteps)
        
        if self.axis_type == "vert":
            self.coordinateManager.zoom_y_axis(direction)
        else:
            self.coordinateManager.zoom_x_axis(direction)
            
    # ------------------------------------------------------------------   
    # Axis limit editing
    # ------------------------------------------------------------------   
    # Axis limits can be double-clicked to edit
            
    
        

    def mouseDoubleClickEvent(self, event):
        #index = self.tabAt(event.pos())
        logger.debug("Axis : mouseDoubleClickEvent returned coordinates:")
        print(event.pos())
        
        x_DC,y_DC = self.coordinateManager.scene2data([event.pos().x()],[event.pos().y()])
        logger.debug("Axis : Data coordinates [%.3f,%.3f]" % (x_DC[0],y_DC[0]))
        
        limit = self.which_end(event.pos())   
        logger.debug("Axis : selected limit = %s" % limit)
        
        # Return if neither min or max
        if not limit:
            return
        
        
        self.coordinateManager.viewport.editLimit(self.min_value(),limit,event.pos())
            

            

    
                
    def which_end_horiz(self,mousePos_SC):
        """
        Determine which end of an axis a mouse position is closest to
        
        Inputs
        -------
        mousePos_SC : QPointF
            Position of mouse
            
        Outputs
        --------
        which_limit: str
            String indicating which axis limit the mouse is nearest to
            'min' or 'max'. If neither then None is returned
            
        """
        
        # Convert mouse position to Data coordinates
        # ----------------------------------------------
        x_DC,y_DC = self.coordinateManager.scene2data([mousePos_SC.x()],[mousePos_SC.y()])
        
        # Find which end is closest
        # ----------------------------
        # TODO : need some limits here
        
        norm_pos = (x_DC[0]-self.coordinateManager.x_min_DC)/(self.coordinateManager.x_max_DC-self.coordinateManager.x_min_DC)
        
        if 0 <= norm_pos <= 0.1:
            which_limit = 'min'
        elif 0.9 <= norm_pos <= 1.0:
            which_limit = 'max'
        else:
            which_limit = None
            
        return which_limit
        
        
        
    def which_end_vert(self,mousePos_SC):
        """
        Determine which end of an axis a mouse position is closest to
        
        Inputs
        -------
        mousePos_SC : QPointF
            Position of mouse
            
        Outputs
        --------
        which_limit: str
            String indicating which axis limit the mouse is nearest to
            'min' or 'max'. If neither then None is returned
            
        """
        
        # Convert mouse position to Data coordinates
        # ----------------------------------------------
        x_DC,y_DC = self.coordinateManager.scene2data([mousePos_SC.x()],[mousePos_SC.y()])
        
        # Find which end is closest
        # ----------------------------
        # TODO : need some limits here
        
        norm_pos = (y_DC[0]-self.coordinateManager.y_min_DC)/(self.coordinateManager.y_max_DC-self.coordinateManager.y_min_DC)
        
        if 0 <= norm_pos <= 0.1:
            which_limit = 'min'
        elif 0.9 <= norm_pos <= 1.0:
            which_limit = 'max'
        else:
            which_limit = None
            
        return which_limit
        
        
        
    def min_value(self):
        """
        Return axis minimum value
        
        """
        
        if self.axis_type == 'vert':
            return self.coordinateManager.y_min_DC
        else:
            return self.coordinateManager.x_min_DC
            
    
    def max_value(self):
        """
        Return axis minimum value
        
        """
        
        if self.axis_type == 'vert':
            return self.coordinateManager.y_max_DC
        else:
            return self.coordinateManager.x_max_DC
        
        

class AxisLimitEditor(QGraphicsItem):
    """
    Editable text field for a GraphicsScene.
    
    Used for putting editable axis limits on the plot. 
    It uses a QLineEdit wrapped in a QGraphicsProxyWidget
    
    
    """
    
    def __init__(self,coordinateManager,limitType='x min',norm_coords=False,parent=None):
        
        super(AxisLimitEditor, self).__init__(parent)
        
        # Coordinate manager
        # --------------------
        self.coordinateManager = coordinateManager
        
        # Limit type
        # ------------------------------------
        self.limitType = limitType
        self.value = 0
        
        
        # Position
        # -----------
        # if being used from inside an Axis object, this should be False
        self.useNormalisedCoordinates = norm_coords
        
        self.pos_SC = QPointF(0,0)
        
        # Text
        # --------
        # This will get updated during the paint function
        self.text = ''

        # Editor widget
        # -------------------    
        self.lineEdit = QGraphicsProxyWidget(parent=self)
        
        # Number validation
        float_regex = QRegExp(r"[\.0-9\-\+e\*\/]+")
        float_validator = QRegExpValidator(float_regex)
        
        self._editor = QLineEdit()
        self._editor.setValidator(float_validator)
        self._editor.setFrame(False)
        
        self._editor.setText(self.text)
        
        self.lineEdit.setWidget(self._editor)
        
        
        self.setFlag(QGraphicsItem.ItemIsFocusable)
        
        # Font
        # ---------------
        self.editorFont = QFont()        
        self.editorFont.setPointSize(8)
        # Note: font size needs to be before the next line otherwise it doesn't
        # have any effect
        self._editor.setFont(self.editorFont)
        
        #self._editor.setMaxLength(len('999.99'))
        
        self.fmt = QFontMetrics(self.editorFont)
        
        self.getLimitValue()
        self.getText()
        self.setRect()
        self.calcPosition()
        #self.setPosition()
        
        
    def boundingRect(self):
        """
        Bounding rectangle is the size of the box around the text mapped to
        scene coordinates
        """
        
        # convert to scene coordinates
        txtRect_IC = self.lineEdit.boundingRect()
        
        rect_SC = QRectF(self.pos_SC,txtRect_IC.size())
        
        return rect_SC
        
        
    def shape(self):
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path
    
        
        
    def setRect(self):
        """
        Work out the dimensions of the rectangle around the text
        
        """
        
        # Get size of rectangle in pixels
        #rect_px = self.fmt.boundingRect(self.text)
        #rect_sc = self.coordinateManager.viewport.mapToScene(rect_px).boundingRect()
        
        width_px = self.fmt.boundingRect(self.text).width()
        
        charWidth = self.fmt.boundingRect('A').width()
        #size = self.fmt.size(Qt.TextSingleLine,self.text)
#        logger.debug("AxisLimitEditor: charWidth %i" % charWidth)
#       logger.debug("AxisLimitEditor: text width %i" % width_px)
        
        
        
        # Set the LineEdit to this size
        # TODO : This is a fudge because the Font metrics stuff is always wrong!
        #        Needs fixing properly.
        #self._editor.setFixedWidth(charWidth*len(self.text)*1.5)
        self._editor.setFixedWidth(width_px + 4 + charWidth)
        #self._editor.setFixedWidth(rect_sc.width())
        #rect_SC = self.coordinateManager.viewport.mapToScene(rect_px)
        
        
    def calcPosition(self):
        """
        Calculate the position of the axis limit editor from normalised corner 
        positions supplied by the coordinateManager
        
        """
        
        # Only do this function if using normalised coordinates
        if not self.useNormalisedCoordinates:
            return
        
        # Get corner positions
        # -----------------------
        corners = {'x min':self.coordinateManager.xMinEditorPos,
                   'x max':self.coordinateManager.xMaxEditorPos,
                   'y min':self.coordinateManager.yMinEditorPos,
                   'y max':self.coordinateManager.yMaxEditorPos}
                   
        assert self.limitType in corners
        xc_NC,yc_NC = corners[self.limitType]
        logger.debug("AxisLimitEditor [%s]: x,y (norm) = (%.3f,%.3f)" % (self.limitType,xc_NC,yc_NC))
        
        # Convert to scene coordinate
        x,y = self.coordinateManager.norm2scene([xc_NC],[yc_NC])
        xc_SC = x[0]
        yc_SC = y[0]
        
        #logger.debug("AxisLimitEditor: x,y (SC) = (%.3f,%.3f)" % (xc_SC,yc_SC))
        
        # Get width of the GraphicsProxy item
        # ------------------------------------
        size = self.boundingRect().size()
        rect = QRectF(QPointF(0,0),size)
        
        # Set the top left hand cornder depending on which limit type
        # -------------------------------------------------------------
        # QRectF() functions to set specific corners on rect
        # then take the top left hand corner of the resulting rect
        
        if self.limitType == 'x min':
            # Set top left
            rect.moveTopLeft(QPointF(xc_SC,yc_SC))
            
        elif self.limitType == 'x max':
            # Set top right
            rect.moveTopRight(QPointF(xc_SC,yc_SC))
            
        elif self.limitType == 'y min':
            # Set top right
            rect.moveTopRight(QPointF(xc_SC,yc_SC))
            
        elif self.limitType == 'y max':
            # Set bottom right
            rect.moveBottomRight(QPointF(xc_SC,yc_SC))

        self.pos_SC = rect.topLeft()
            

    def setPosition(self,point_xy,position_spec='top left'):
        """
        Set position of AxisLimitEditor by a specific vertex, e.g. top left
        
        Example usage
        ----------------
        # Set top left corner to a specific position
        >>> self.setPosition(QPointF(3,4),'top left')
        
        Inputs
        --------
        point_xy : QPointF()
            coordinates where specific vertex is to go
            
        position_spec : str
            string giving the vertex. The options are:
                'top left'
                'top right'
                'bottom left'
                'bottom right'
                'centre'
                'centre left'
                'centre right'
                'centre top'
                'centre bottom'
                
        """
        
        # Get width of the GraphicsProxy item
        # ------------------------------------
        size = self.boundingRect().size()
        
        # Make a QRectF for manipulating
        rect = QRectF(QPointF(0,0),size)
        
        # Set the top left corner based on the position spec
        # ----------------------------------------------------
        position_spec = position_spec.lower()
        
        if position_spec == 'top left':
            rect.moveTopLeft(point_xy)
            
        elif position_spec == 'top right':
            rect.moveTopRight(point_xy)
            
        elif position_spec == 'bottom right':
            rect.moveBottomRight(point_xy)
            
        elif position_spec == 'bottom left':
            rect.moveBottomLeft(point_xy)
            
        elif position_spec == 'centre':
            rect.moveCenter(point_xy)
            
        elif position_spec == 'centre left':
            rect.moveCenter(point_xy)
            rect.moveLeft(point_xy.x())
            
        elif position_spec == 'centre right':
            rect.moveCenter(point_xy)
            rect.moveRight(point_xy.x())
            
        elif position_spec == 'centre top':
            rect.moveCenter(point_xy)
            rect.moveTop(point_xy.y())
            
        elif position_spec == 'centre bottom':
            rect.moveCenter(point_xy)
            rect.moveBottom(point_xy.y())
            

        # Take the top left corner of the manipulated rect            
        self.pos_SC = rect.topLeft()
        
        #logger.debug('AxisLimitEditor [%s]: pos_SC = [%f,%f]' % (self.limitType,self.pos_SC.x(),self.pos_SC.y()))
        #logger.debug('AxisLimitEditor [%s]: Visible = %i' % (self.limitType,self.isVisible()))
        
            
    def getLimitValue(self):
        """
        Make self.value into a function that returns the appropriate
        limit.
        
        This is run once in __init__()
        
        """
        limitType = self.limitType.lower()
        
        if limitType == 'x min':
            self.value = lambda : self.coordinateManager.x_min_DC 
            self.updateFunction = self.coordinateManager.set_x_min_DC
            self.formatFunction = lambda s : self.coordinateManager.x_label_format % s
            
            
        elif limitType == 'x max':
            self.value = lambda :self.coordinateManager.x_max_DC 
            self.updateFunction = self.coordinateManager.set_x_max_DC
            self.formatFunction = lambda s : self.coordinateManager.x_label_format % s
            
        elif limitType == 'y min':
            self.value = lambda :self.coordinateManager.y_min_DC 
            self.updateFunction = self.coordinateManager.set_y_min_DC
            self.formatFunction = lambda s : self.coordinateManager.y_label_format % s
            
        elif limitType == 'y max':
            self.value = lambda :self.coordinateManager.y_max_DC 
            self.updateFunction = self.coordinateManager.set_y_max_DC
            self.formatFunction = lambda s : self.coordinateManager.y_label_format % s
            
        else:
            logger.debug('AxisLimitEditor: Unknown limit type %s' % limitType)

        self.lineEdit.connect(self._editor,SIGNAL('returnPressed()'),self.getValue)

        #logger.debug('AxisLimitEditor: First limit value = %f' % self.value)
    
    
    def getText(self,force=False):
        """
        Convert the axis limit value into text using a suitable
        conversion
        """

        # TODO format needs to adapt to x and y
        new_text = self.formatFunction(self.value())
        
        if new_text != self.text or force:
            self.text = new_text
            self._editor.setText(self.text)
            
        #logger.debug('AxisLimitEditor: limit value = %f' % self.value)
        #logger.debug('AxisLimitEditor: limit text = %s' % self.text)
        

    def getValue(self):
        """
        Convert text in the line edit to a float and trigger an axis update
        
        """
        
        # Get the new value out of the line edit and convert to float
        new_value = float(self._editor.text())
        
        logger.debug('AxisLimitEditor [%s]: value changed [%f]' % (self.limitType, new_value))
        
        # Trigger an update of the axis
        self.updateFunction(new_value)
        
        # Clear keyboard focus to force an update to the plot
        self.lineEdit.clearFocus()
        
        self.coordinateManager.viewport.update()
        
        self.getText(True)
        
    
    def paint(self,painter, option, widget=None):    
        """
        Refresh the text and position of the editor
        """
        
        
        
        self.getText()
        self.setRect()
        self.calcPosition()
        
        
        if DEBUG :
            painter.setPen(QColor(Qt.green))
            painter.drawRect(self.boundingRect())
            painter.drawEllipse(self.pos_SC,5,5)
        
        
        self.lineEdit.setPos(self.pos_SC)
        
        
        

#=============================================================================
#%% Graph backgrounds
#=============================================================================

class Background(QGraphicsItem):
    """Background class
    This is just a rectangle that fills the background.
    The only reason for making it a class is to make it change dimensions
    with the viewport.
    It always gets its dimensions directly from the viewport rectangle
    """
    

    def __init__(self, color, coordinateManager):
        super(Background, self).__init__()
        self.color = color
        
        self.coordinateManager = coordinateManager
        
        self.gridEnabled = False
        
        self.xgrid_NC = np.linspace(0,1,11)
        self.ygrid_NC = np.linspace(0,1,11)
        
        self.gridColor = QColor("#000045") #Qt.red
        self.gridTransparency = 100
        

    @property
    def rect(self):
        """Get viewport rectangle in scene coordinates
        """
        return self.coordinateManager.viewport2sceneRect()
        

    def boundingRect(self):
        return self.rect


    def shape(self):
        path = QPainterPath()
        path.addRect(self.rect)
        return path


    def paint(self, painter, option, widget=None):
        """
        Draw the background
        """        
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.color))
        painter.drawRect(self.rect)
        
        
        
        # Draw gridlines
        # ---------------------
        # These are in normalised coordinates e.g. 0.1, 0.2,.. 1.0 of the screen
        # width or height. They are primarily for debugging positioning.
        if self.gridEnabled:
            
            # Get coordinates of box
            x1,y1,x2,y2 = self.rect.getCoords()
            
            # calculate gridline positions
            xgrid_SC,ygrid_SC = self.coordinateManager.norm2scene(self.xgrid_NC,self.ygrid_NC)
            
            # Set gridline colour and style
            gridLineColour = QColor(self.gridColor)
            gridLineColour.setAlpha(self.gridTransparency)
            pen = QPen()
            pen.setColor(gridLineColour)
#            pen.setStyle(self.gridStyle)
            painter.setPen(pen)
            
            # Draw vertical gridlines
            for pos in xgrid_SC:
                painter.drawLine(QPointF(pos,y1),QPointF(pos,y2))
                
            # Draw horizontal gridlines
            for pos in ygrid_SC:
                painter.drawLine(QPointF(x1,pos),QPointF(x2,pos))
        
                
        
"""
Note: possible way to get viewing rectangle
sceneRect = graphicsView.mapToScene(graphicsView.rect()).boundingRect()
"""

class PlotBox(QGraphicsItem):
    """ 
    Background rectangle where data is plotted
    Includes axes, borders
    
    
    """


    def __init__(self,coordinateManager):
        super(PlotBox, self).__init__()
        
        self.setAcceptedMouseButtons(Qt.LeftButton)
        self.setFlag(QGraphicsItem.ItemIsFocusable)
        self.setCursor(Qt.CrossCursor)
        
        
        # Set coordinate manager
        # -----------------------
        self.coordinateManager = coordinateManager
        
        # Set colours to defaults
        # ------------------------------
        self.backgroundColor = Qt.black
        self.borderColor = Qt.green
        
        
        # Grid lines
        # ----------------
        self.gridColor = Qt.green
        self.gridTransparency = 64 # 0 = transparent, 255 = opaque
        self.gridStyle = Qt.SolidLine
        self.gridEnabled = True
        
        self.xGridMajorPositions = []
        self.yGridMajorPositions = []
        
        
        # Rectangle size and position
        # --------------------------------
        #self.calcGridlines()
        
        # Event handling flags
        self.pan = False
        
        # KeyPress event actions
        # ------------------------
        self.keyPressActions = {
            'pan_up':lambda : self.coordinateManager.pan_y_axis(1),
            'pan_down':lambda : self.coordinateManager.pan_y_axis(-1),
            'pan_right':lambda : self.coordinateManager.pan_x_axis(1),
            'pan_left':lambda : self.coordinateManager.pan_x_axis(-1),
            'zoom_in':lambda : self.coordinateManager.zoom_all(-1),
            'zoom_out':lambda : self.coordinateManager.zoom_all(1),
            'autoscale':lambda : self.coordinateManager.autoscale(),
            'autoscale_x':lambda : self.coordinateManager.autoscale('x'),
            'autoscale_y':lambda : self.coordinateManager.autoscale('y'),
            'scale_y_out': lambda : self.coordinateManager.zoom_y_axis(1),
            'scale_y_in': lambda : self.coordinateManager.zoom_y_axis(-1),
            'scale_x_out': lambda : self.coordinateManager.zoom_x_axis(1),
            'scale_x_in': lambda : self.coordinateManager.zoom_x_axis(-1)}
      

    
    @property
    def rect(self):
        return self.coordinateManager.plotBox2scene()
        
        
    def setRect(self,rect):
        """ 
        Set rectangle for PlotBox
        Also calculate grid line positions
        """
        # TODO calculate grid 
        
        # Set rectangle
        self.rect = rect
        
        

    def boundingRect(self):
        return self.rect


    def shape(self):
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path


    def paint(self, painter, option, widget=None):
        """ Draw PlotBox
        """
        
        # Get rectangle coordinates
        # ----------------------------
        rect = self.rect
        
        # Get clip rectangle
        # -----------------------
        clipRect = self.coordinateManager.itemClipRect(self)
        painter.setClipRect(clipRect)
        painter.setClipping(True)
        
        # Draw the background
        # ------------------------
        
        painter.setPen(self.borderColor)
        painter.setBrush(QBrush(self.backgroundColor))
        painter.drawRect(rect)
        
        # Draw gridlines
        # ---------------------
        if self.gridEnabled:
            pb_rect = self.coordinateManager.plotBox2scene()
            
            # Get coordinates of plot box
            x1,y1,x2,y2 = pb_rect.getCoords()
            
            # calculate gridline positions
            self.calcGridlines()
            
            # Set gridline colour and style
            gridLineColour = QColor(self.gridColor)
            gridLineColour.setAlpha(self.gridTransparency)
            pen = QPen()
            pen.setColor(gridLineColour)
            pen.setStyle(self.gridStyle)
            painter.setPen(pen)
            
            # Draw vertical gridlines
            for pos in self.xGridMajorPositions:
                painter.drawLine(QPointF(pos,y1),QPointF(pos,y2))
                
            # Draw horizontal gridlines
            for pos in self.yGridMajorPositions:
                painter.drawLine(QPointF(x1,pos),QPointF(x2,pos))
            
        
        if self.hasFocus():
            focusColour = QPalette.color(QPalette(QPalette.Active),QPalette.Highlight)
            pen = QPen(focusColour)
            pen.setWidth(3)
            
            painter.setPen(pen)
            painter.setBrush(QBrush(Qt.NoBrush))
            painter.drawRect(clipRect)
            
        
        
    def calcGridlines(self):
        """ Calculate positions of grid lines
        return a list of the positions in one dimension
        """
        
        xGrid_IC = self.coordinateManager.get_xGridMajor_IC(self)
        yGrid_IC = self.coordinateManager.get_yGridMajor_IC(self)
        
        
        self.xGridMajorPositions = xGrid_IC
        self.yGridMajorPositions = yGrid_IC
        
    #-------------------------------------------------------------------------    
    # Handle events
    #-------------------------------------------------------------------------
    def wheelEvent(self,event):
        """ Mouse wheel turned over widget
        
        zoom the scales of both axes in the graph
        
        """
        
        # Get how much the wheel has turned
        numDegrees = event.delta()/8
        numSteps = numDegrees/15
        direction = -np.sign(numSteps)
        
        self.coordinateManager.zoom_all(direction)
        
        
        
    def mousePressEvent(self,event):
        """
        Handle the mouse being pressed for panning the graph
        
        """
        
        
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.SizeAllCursor)
            
            self.pan = True
            if DEBUG:
                print("\nPlotBox:mousePressEvent")
                print("Mouse : Left button down")
                
        else:
            event.ignore()
            
           
           
           
    def mouseMoveEvent(self,event):
        """
        Mouse move or drag event. This is used for panning around the plotbox
        
        """
        
        
        
        # Get how much Mouse has moved in PlotBox
        # ----------------------------------------------
        # Log mouse positions
        buttonDownPos_IC = event.lastPos()
        mouseCurrentPos_IC = event.pos()
        
        
        
        x_IC = np.array([buttonDownPos_IC.x(),mouseCurrentPos_IC.x()])
        y_IC = np.array([buttonDownPos_IC.y(),mouseCurrentPos_IC.y()])
              
        # Decide if the mouse has moved enough to pan the graph 
        # --------------------------------------------------------
        x_DC,y_DC = self.coordinateManager.item2data(self,x_IC,y_IC)
        dx_DC = np.diff(x_DC)[0]
        dy_DC = np.diff(y_DC)[0]
        
        # Pan the axis
        self.coordinateManager.pan(dx_DC,dy_DC)
        
        
                
                
    def mouseReleaseEvent(self,event):
        """
        Mouse released - handle panning
        
        """
        
        # Restore cursor
        self.setCursor(Qt.CrossCursor)
        
        if DEBUG:
            print("New x axis range = [%.3f - %.3f]" % (self.coordinateManager.x_min_DC,self.coordinateManager.x_max_DC))
            print("New y axis range = [%.3f - %.3f]" % (self.coordinateManager.y_min_DC,self.coordinateManager.y_max_DC))
        
      
      
    def keyPressEvent(self,event):
        """
        Handle key presses
        TODO : plotBox doesn't recognise keyboard events yet???
        
        """

        shortcuts = self.coordinateManager.preferences.keyboard['plot']
        
        action = shortcuts.getActionFromEvent(event)        
        
        logger.debug("PlotBox: Keyboard Action: %s" % action)
        
        if not action or action not in self.keyPressActions:
            event.ignore()
            return
            
        # Action is one of ours, execute and accept the event
        event.accept()
        
        self.keyPressActions[action]()
            
            
        
        
        
            
    def contextMenuEvent(self,event):
        """
        Context menu (right click) for PlotBox
        
        """
        
        menu = QMenu(self.parentWidget())
        
        menu.addAction("Autoscale",self.autoscale)
        menu.addAction("Autoscale X axis",self.autoscaleX)
        menu.addAction("Autoscale Y axis",self.autoscaleY)
        menu.addSeparator()
        menu.addAction("Add Horizontal Marker",self.addHorizMarkerSignal)
        menu.addAction("Add Vertical Marker",self.addVertMarkerSignal)
        menu.addSeparator()
        menu.addAction("Copy plot to clipboard",self.copyPlotSignal)
        menu.addSeparator()
        menu.addAction("Show Legend",self.showLegend)
        menu.addAction("Hide Legend",self.hideLegend)
        
        
        menu.exec_(event.screenPos())
        
        
    
    def addHorizMarkerSignal(self):
        """
        Add marker to the plot via the coordinate manager
        
        """
        logger.debug("Sending add Horiz marker signal")
        self.coordinateManager.viewport.addHorizMarker()
        
    
    
    def addVertMarkerSignal(self):
        """
        Add marker to the plot via the coordinate manager
        
        """
        logger.debug("Sending add Vert marker signal")
        self.coordinateManager.viewport.addVertMarker()
        
        
    def autoscale(self):
        
        logger.debug("Autoscale selected")
        
        self.coordinateManager.autoscale()
        
        
    def autoscaleX(self):
        
        logger.debug("Autoscale X selected")
        
        self.coordinateManager.autoscale('x')
        
        
    def autoscaleY(self):
        
        logger.debug("Autoscale Y selected")
        
        self.coordinateManager.autoscale('y')
        
    def copyPlotSignal(self):
        
        logger.debug("Copy to clipboard")
        
        self.coordinateManager.viewport.plot2clipboard()
        
        
    def showLegend(self):
        
        logger.debug("Add legend")
        
        self.coordinateManager.viewport.showLegend()
        
        
    def hideLegend(self):
        
        logger.debug("Hide legend")
        
        self.coordinateManager.viewport.hideLegend()
    
        
        


#=============================================================================
#%% Graph series class definition
#=============================================================================


class GraphSeries(QGraphicsItem):
    """Item representing on curve on the graph
    
    """
    
    def __init__(self,x_data_DC,y_data_DC,name,coordinateManager,**kwargs):
        
        super(GraphSeries, self).__init__()
        
        # Data
        # ---------------
        self.x_DC = x_data_DC # numpy arrays
        self.y_DC = y_data_DC
        
        self.name = name
        self.setToolTip(name)
        
        # Flag to set whether a recalculation of the coordinates is
        # required. This is to speed up painting by only recalculating
        # coordinates when absolutely necessary
        self.recalculate = True
        
        # Appearance
        # -----------------
        
        # Colours & styles
        self.lineColour = kwargs.get('lineColour',Qt.blue)
        self.lineDashStyle = kwargs.get('lineStyle',Qt.SolidLine)
        self.lineWidth = kwargs.get('lineWidth',2)
        self.lineTransparency = kwargs.get('lineTransparency',255)
        
        self.markerColour = kwargs.get('markerColour',Qt.blue)
        self.markerFillColour = kwargs.get('markerFillColour',Qt.green)
        self.markerTransparency = kwargs.get('markerTransparency',200)
        self.markerSize = kwargs.get('markerSize',10)
        self.markerShape = kwargs.get('markerShape',col_shapes.make_markers('^'))
        
        self.drawMarkers = kwargs.get('drawMarkers',True)
        
        # TODO : Need some way to change the marker colours
        
        
        # coordinateManager
        # ------------------------
        self.coordinateManager = coordinateManager
        
        # Points to plot
        # ---------------
        # List of QPoints that holds the local coordinates of every point in
        # the series
        self.xy_points = []
        
        # Marker list
        # ----------------
        # Used to hold all marker items
        self.markerList = []
        
        # Create list TODO : remove when markers are working
#        if self.drawMarkers:
#            self.create_markers()
        
        # Pre-calculate data in item coordinates
        self.create_lines()
        self.create_markers()
        
        # Clip rectangle for data (plotBox boundary)
        self.clipRect = self.coordinateManager.itemClipRect(self)
        
        
        
    def boundingRect(self):
        """
        Return bounding rectangle of the graph series.
        
        Output
        ---------
        bounding_rect : QRect
            rectangle coordinates in item coordinate system
            
        Programming note
        ----------------
        The bounding rectangle returned is the boundary of the plotBox. It could
        have been calculated from the data but zooming and panning can cause
        the data to go off screen. If the bounding rect returned is off screen
        then QT4 will not update the graphics item. By keeping the bounding rect
        to the same dimensions as the plotBox it ensures that the graph series
        is always updated.
        
        """
        
        return self.clipRect
    
    
    def shape(self):
        # Return painter path of curve
        
        return self.lines
    
   
   
    def paint(self, painter, option, widget=None):
        
        if self.x_DC==[] or self.y_DC==[]:
            return
            
        
        # Convert data coordinates to item coordinates
        # ---------------------------------------------
        #x_IC,y_IC = self.coordinateManager.data2item(self,self.x_DC,self.y_DC)
        
        if self.recalculate:
            self.create_lines()
            self.create_markers()
            
        
        
        # Get clip rectangle
        # -----------------------
        self.clipRect = self.coordinateManager.itemClipRect(self)
        painter.setClipRect(self.clipRect)
        painter.setClipping(True)
        
        
        # Draw clip rectangle TODO : remove sometime
        #painter.setPen(QPen(Qt.red))
        #painter.drawRect(self.clipRect)
        
    
        
        # Draw lines
        # -------------------------------
        
        if self.lineColour is not None:
            lineColour = QColor()
            lineColour.setNamedColor(self.lineColour)
            lineColour.setAlpha(self.lineTransparency)
            pen = QPen(lineColour)
            pen.setStyle(self.lineDashStyle)
            pen.setWidthF(self.lineWidth)
            
            painter.setPen(pen)
            
            painter.drawPath(self.lines)
            
        
        # Exit if we don't have to draw markers
        if not self.drawMarkers:
            return
            
        
        

        # Draw markers
        # -------------------------------
    
        pen = QColor()
        pen.setNamedColor(self.markerColour)
        pen.setAlpha(self.markerTransparency)
        
        brush = QColor()
        brush.setNamedColor(self.markerFillColour)
        brush.setAlpha(self.markerTransparency)
        
        painter.setPen(pen)
        painter.setBrush(brush)
        
        
        for marker in self.markerList:
            painter.save()
            painter.drawPath(marker)
            painter.restore()
        

            
            
            

    def create_lines(self):
        """
        Convert data to item coordinates and create the graph lines
        
        """
        
        # This function is to centralise the data conversion so that it is
        # only done once during a paint function and the results are shared
        # by shape and boundingRect
        # It also converts the data array to a polygon which is a 
        # time consuming task and is required by both paint and shape.
        # Again it is done once during paint and the results are shared by
        # shape
        
        #self.x_IC,self.y_IC = self.coordinateManager.data2item(self,self.x_DC,self.y_DC)
        
        self.xy_points = self.coordinateManager.data2itemQPoints(self,self.x_DC,self.y_DC)
        
        # Create a path for the lines
        self.lines = QPainterPath()
        #self.lines.addPolygon(array2polygon(self.x_IC,self.y_IC))
        self.lines.addPolygon(QPolygonF(self.xy_points))
        
        # Set recalculate to False
        # Must be set by external event, such as axis range changing
        self.recalculate = False
        
        #self.prepareGeometryChange()
        
        
    def forceUpdate(self):
        """
        Reimplemented update function.
        
        Recalculates the bounding box before calling the standard update
        
        """
        
        self.create_lines()
        self.create_markers()
      
        self.prepareGeometryChange()
        
        #self.updateMarkers()
        
        self.update(self.boundingRect())
        
        
    # ------------------------------------------------------------------------
    # Marker functions
    # ------------------------------------------------------------------------
    
    def create_markers(self):
        """Create all markers required from GraphMarker items
        """
        
        if not self.drawMarkers:
            return
        
        # Initialise list
        self.markerList = []
        
        for Point in self.xy_points:            
            tr = QTransform()
            tr.translate(Point.x(),Point.y())
            # TODO : aspect ratio conversion needed here
            tr.scale(self.markerSize,self.markerSize)
            
            finalPath = tr.map(self.markerShape)
            
            self.markerList.append(finalPath)
            
            
        

        
            
        
        
    def updateMarkers(self):
        """
        Update the colours on all the markers
        
        """
        
        # Go through all markers and update
        
        for marker in self.markerList:
            # Get ready for change
            marker.prepareGeometryChange()
            
            # Make the changes
            marker.markerColour = self.markerColour
            marker.markerFillColour = self.markerFillColour
            marker.markerSize = self.markerSize
            marker.markerShape = marker.getMarkerShape(self.markerShape)
            marker.transparency = self.markerTransparency
            
            
    
        
        
        
        
        
#=============================================================================
#%% Channel Graph series class definition
#=============================================================================


class ChannelGraphSeries(GraphSeries):
    """
    GraphSeries specifically for ScopePy channels. It handles the chunks
    and supplies the underlying GraphSeries with updated x_DC & y_DC arrays
    
    """
    
    def __init__(self,channel,coordinateManager,**kwargs):
        
        
        # Get initial data from channel
        # TODO : This may need some initialisation
        
        self.channel = channel
        
        self.chunkSelection = [0]
        
        self.chunkMode = kwargs.get('chunkMode',ch.CHUNK_MODE_ALL)
        
        self.getData()
        
        # Initialise base class
        super(ChannelGraphSeries, self).__init__(self.x_DC,self.y_DC,
                                                self.channel.name,
                                                coordinateManager,
                                                lineColour = channel.plot_lineStyle.lineColour,
                                                lineDashStyle = channel.plot_lineStyle.lineDashStyle,
                                                markerColour = channel.plot_lineStyle.markerColour,
                                                markerFillColour = channel.plot_lineStyle.markerFillColour,
                                                markerSize = channel.plot_lineStyle.markerSize,
                                                markerShape = col_shapes.make_markers(channel.plot_lineStyle.marker))
        
        # Linestyles are taken from the channel

        
        
        
        
    # ------------------------------------------------------------------------
    # Chunk handling
    # ------------------------------------------------------------------------
        
    
    def setChunkMode(self,mode):
        """
        Set the chunk mode for the plots.
        
        This defines which data is used.
        
        Inputs
        -----------
        mode : string
            Chunk mode : 'all','latest','first','selection'
            
        """
        
        assert mode in ch.CHUNK_MODES,"Unknown chunk mode : %s" % mode
        
        self.chunkMode = mode
        
        # Update the data
        self.getData()
        
        # logging
        logger.debug("Chunk mode [%s] set to [%s]" % (self.name,self.chunkMode))
        logger.debug("Data length [%d]" % len(self.x_DC))
        
        
        
    def setChunkSelection(self,chunkIndexList):
        """
        Set the chunks to be plotted when the chunk mode is 'selection'
        
        Inputs
        ----------
        chunkIndexList : list of numbers (indexes)
            list of numeric indices of the chunks to be plotted
            
        """
        
        # Get chunks that are in the correct range
        indexList = [x for x in chunkIndexList if x < self.channel.chunks]
        
        # TODO : Do some sort of checking on this
        
        if indexList:
            self.chunkSelection = indexList
            
        
     
        
    def getData(self):
        """
        Get data from channel according to chunk mode
        
        """
        
        # Handle empty channels
        if self.channel.isEmpty:
            self.x_DC = []
            self.y_DC = []
            logger.debug('ChannelSeries getData: returning empty data')
            return
            
            
        data = self.channel.data(chunkMode=self.chunkMode,chunkList=self.chunkSelection)
        
        self.x_DC = data[self.channel.x_axis]
        self.y_DC = data[self.channel.y_axis]
        
        # Update limits for coordinate manager
        # TODO : This is a bit kludgy needs some rethinking
        if hasattr(self,'coordinateManager'):
            self.coordinateManager.updateDataMinMax(self.x_DC.min(),
                                                    self.x_DC.max(),
                                                    self.y_DC.min(),
                                                    self.y_DC.max())
                                                    
        
        
    
    def updateChunkData(self):
        """
        General update when the chunk mode changes
        
        This is a slot for other functions to signal to.
        
        """
        
        
        # Get new data
        self.getData()
        
        # TODO : Maybe more stuff needed here
        
        
        
    def updateFromChannel(self):
        """
        Update linestyles from channel. 
        
        Need to do this as the channel settings are not directly connected
        to the line styles.
        
        """
        
        # Update linestyles
        self.lineColour = self.channel.plot_lineStyle.lineColour
        self.lineDashStyle = self.channel.plot_lineStyle.lineDashStyle
        self.markerColour = self.channel.plot_lineStyle.markerColour
        self.markerFillColour = self.channel.plot_lineStyle.markerFillColour
        self.markerShape = col_shapes.make_markers(self.channel.plot_lineStyle.marker)
        
        # Update chunks
        self.updateChunkData()
        
        
        
        
        
        
        
     

#=============================================================================
#%% Graph marker class
#=============================================================================


class GraphMarker(QGraphicsItem):
    """Graph marker, 
    - not used by plot series anymore, but keep anyway for displaying graph
    markers in other places e.g. legend.
    
    """
    
    def __init__(self,name,x_DC,y_DC,parent=None,markerColour=Qt.blue,markerFillColour=Qt.blue,
                 markerSize=1, marker_shape='o',transparency=200):
        
        super(GraphMarker, self).__init__(parent)
        
        self.setAcceptHoverEvents(True)
        
        # Data
        # --------------
        # Data point that this marker represents
        # in actual data coordinates
        self.x_DC = x_DC
        self.y_DC = y_DC
        
        # Name label - given by parent
        self.name = name
        
        self.setMarkerTip()
        
        # Appearance
        # -----------------
        
        # Colours & styles
        self.markerColour = markerColour
        self.markerFillColour = markerFillColour
        self.transparency = transparency
        
        # Size
        self.markerSize = markerSize
        
        # Shape
        self.markerShape = self.getMarkerShape(marker_shape)
        
        # Visibility
        self.visible = True
        
        
        
        
    def boundingRect(self):
        # Scale rectangle same as marker size
        x1,y1,x2,y2 = self.markerShape.boundingRect().getCoords()
        
        # Get centre of rectangle
        ox = (x1+x2)/2
        oy = (y1+y2)/2
        
        # Scale width and height according to marker size setting
        width = abs(x2-x1)*self.markerSize*1.5
        height = abs(y2-y1)*self.markerSize*1.5
        
        # Return scaled rectangle
        return QRectF(ox-width/2,oy-height/2,width,height)
    
    def shape(self):
        return self.markerShape
        
    
    def paint(self, painter, option, widget=None):
        """
        Draw the marker
        
        """
 
        
        if not self.visible:
            alpha = 0
        else:
            alpha = self.transparency
        
        if DEBUG:
            # Draw bounding rect
            painter.save()
            painter.setPen(QColor(Qt.red))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.boundingRect())
            painter.restore
            
        
        
        pen = QColor()
        pen.setNamedColor(self.markerColour)
        pen.setAlpha(alpha)
        
        brush = QColor()
        brush.setNamedColor(self.markerFillColour)
        brush.setAlpha(alpha)
        
        painter.setPen(pen)
        painter.setBrush(brush)
        
        painter.save()
        
        painter.scale(self.markerSize,self.markerSize)
        painter.drawPath(self.markerShape)
        
        painter.restore()
        
        
        
        
    
    def getMarkerShape(self,marker_shape):
        """Validate the marker_shape
        """
        
        if isinstance(marker_shape,QPainterPath):
            return marker_shape
            
        elif isinstance(marker_shape,str):
            return col_shapes.make_markers(marker_shape)
            
        else:
            # Return default
            return col_shapes.make_markers('o')
            
            
            
    def setMarkerTip(self,xformat = '%.3f',yformat='%.3f'):
        """ Set the tool tip for the marker
        
        """
        
        tooltipFormat = '%s (' + xformat +',' + yformat +')'
        
        tooltip = tooltipFormat %(self.name,self.x_DC,self.y_DC)
        
        self.setToolTip(tooltip)
        
        
    def hoverEnterEvent(self,event):
        
        print("Hover enter")
        super().hoverEnterEvent(event)
        
        
            
    
#=============================================================================
#%% GraphLegend class
#=============================================================================
    
LEGEND_UPPER_RIGHT = 'upper right'
LEGEND_UPPER_LEFT = 'upper left'
LEGEND_LOWER_RIGHT = 'lower right'
LEGEND_LOWER_LEFT = 'lower left'
LEGEND_UPPER_MIDDLE = 'upper middle'
LEGEND_LOWER_MIDDLE = 'lower middle'

LEGEND_VERTICAL = 'vertical'
LEGEND_HORIZONTAL = 'horizontal'

LEGEND_POSITIONS = {LEGEND_UPPER_RIGHT:(0.7,0.9),
                    LEGEND_UPPER_LEFT: (0.15,0.9),
                    LEGEND_LOWER_RIGHT: (0.7,0.2),
                    LEGEND_LOWER_LEFT: (0.15,0.2),
                    LEGEND_UPPER_MIDDLE: (0.4,0.9),
                    LEGEND_LOWER_MIDDLE: (0.4,0.2),
                    }

class GraphLegend(QGraphicsItem):
    """
    Legend for graphs
    
    """
    
    VERTICAL = 'vertical'
    HORIZONTAL = 'horizontal'
    
    
    
    def __init__(self,coordinateManager,channel_dict,position=LEGEND_UPPER_RIGHT,parent=None):
        """
        Inputs
        -------
        
        coordinateManager : class
            link to coordinate manager for the GraphWidget
            
        channel_dict : dict
            Link to channels in the plot
            
        """
            
        super(GraphLegend, self).__init__(parent)
        
        
        # Internal variables
        # --------------------------
        self.coordinateManager = coordinateManager
        self.channel_dict = channel_dict
        
        # Flag for forcing the legend to update itself, e.g. when orientation
        # is changed.
        self.forceUpdate = False
        
        # Graphics settings
        # -------------------------
        self.setFlag(QGraphicsItem.ItemIsMovable,True)   
        self.setFlag(QGraphicsItem.ItemIsSelectable,True)
        self.setFlag(QGraphicsItem.ItemIsFocusable,True)
        self.setToolTip('Legend - right click for options')
        
        # Type of mouse cursor to use
        self.setCursor(Qt.SizeAllCursor)
        
        # Text settings
        # ----------------
        self.font = QFont()
        self.font.setPixelSize(8)
        self.fmt = QFontMetrics(self.font)
        
        self.maxTextLength_chars = 32
        
        # Overall legend Dimensions
        # ----------------------------
        #self.max_width_NC = 0.75
        #self.max_height_NC = 0.75
      
        
        
        # Legend cell dimensions
        # --------------------------
        self.cell_width_IC = 30
        self.cell_height_IC = 10
        self.cell_lineLength_IC = 20
        self.cell_VBuffer_IC = 3
        self.cell_HBuffer_IC = 5
        self.cell_gapLength_IC = 8
        self.cell_textWidth_chars = self.maxTextLength_chars
        
        
        # Legend orientation
        # -----------------------
        # horizontal or vertical
        self._orientation = self.VERTICAL
        
        # Max number of rows/columns depending on orientation
        self.max_entries = 8
        
        # Internal table of legend entries
        # --------------------------------------
        # This is a list of lists table that is basically a representation
        # of how the legend is arranged. It is used to draw the legend. It is 
        # not accessed directly, but through the plotTable property
        self._plot_table= []
        self._num_plots = len(self.channel_dict)
        self.rows = None
        self.columns = None
        
        
        # Legend colours and styles
        # -----------------------------------
        self.outlineColour = QColor(Qt.darkGray)
        self.outlineWidth = 2
        self.outlineDashStyle = Qt.SolidLine
        self.outlineTransparency = 255
        self.outlineMargin = 4
        
        self.cellBorderColour = QColor(Qt.black)
        self.cellWidth = 0
        self.cellDashStyle = Qt.NoPen
        self.cellTransparency = 0
        self.cellBackgroundColour = QColor(Qt.black)
        
        self.backgroundColour = QColor(Qt.black)
        self.textColour = QColor(Qt.lightGray)
        
        
        
        
    @property
    def orientation(self):
        return self._orientation
        
    @orientation.setter
    def orientation(self,value):
        """
        Set orientation
        
        Input
        ---------
        value: str
            'horizontal' or 'vertical' or 'rows and columns'
            
        Example usage
        ----------------
        >>> legend.orientation = legend.VERTICAL
        >>> legend.orientation = legend.HORIZONTAL
        >>> legend.orientation = legend.ROWS_AND_COLUMNS
        
        """
        if value.lower() not in [self.VERTICAL,self.HORIZONTAL]:
            return
            
        
        
        # Force an update if the value is different to the current setting
        if self._orientation != value:
            self._orientation = value
            self.forceUpdate = True
            
            self.updateLegend()
            self.update()
            
        
        
    
    
    @property
    def position_NC(self):
        """
        Return position of Legend top left hand corner in normalised coordinates.
        
        Output
        ---------
        position_NC : (float,float)
            (x,y) position of legend in normalised coordinates
        
        """
        
        # Get position in scene coordinaes
        pos_SC = self.scenePos()
        
        # Convert to normalised
        x_NC,y_NC = self.coordinateManager.scene2norm([pos_SC.x()],[pos_SC.y()])
  
        return (x_NC[0],y_NC[0])
        
        
    @position_NC.setter
    def position_NC(self,pos):
        """
        Set position of legend in normalised coordinates
        
        Inputs
        --------
        (x_NC,y_NC) : tuple of two floats
            New position of legend in normalised coordinates
            
        """
        
        # Unpack x,y coordinates
        x_NC,y_NC = pos
        
        # Convert to normalised
        x_SC,y_SC = self.coordinateManager.norm2scene([x_NC],[y_NC])
        logger.debug('[Legend] x_SC = %.1f, y_SC = %.1f' % (x_SC[0],y_SC[0]))
        
        self.setPos(QPointF(x_SC[0],y_SC[0]))
        
        
        
    def boundingRect(self):
        """
        Convert  to scene coordinates
        
        """
        
        # Note: boundingRect does not require the actual x,y position in
        # scene coordinates to be correct. The rect is specified relative
        # to 0,0 which makes it relative to the current scenePos()
        
        return self.rect
    
    
    
    def shape(self):
        path = QPainterPath()
        path.addRect(self.boundingRect())
        
        return path
        
        
    @property
    def fontsize(self):
        return self.font.pixelSize()
        
    @fontsize.setter
    def fontsize(self,value):
        if isinstance(value,int):
            self.font.setPixelSize(value)
        
    
    
    def paint(self, painter, option, widget=None):
        """
        Draw the legend
        
        """
        
        
        # Draw legend box
        # -----------------------
        outlineColour = self.outlineColour
        outlineColour.setAlpha(self.outlineTransparency)
        pen = QPen(outlineColour)
        pen.setStyle(self.outlineDashStyle)
        pen.setWidthF(self.outlineWidth)
        painter.setPen(pen)
        
        backgroundColour = self.backgroundColour
        painter.setBrush(QBrush(backgroundColour))
        painter.drawRect(self.rect)
              
        self.drawCells(painter,self.outlineMargin,self.outlineMargin)
        
        
        if DEBUG:
            # TODO: the x,y positions of the bounding rect are wrong
            #
            painter.save()
            painter.setPen(QColor(Qt.red))
            painter.drawRect(self.mapRectFromScene(self.boundingRect()))
            painter.restore()
            
            
        # Make legend top item
        number_of_items = len(self.coordinateManager.scene.items())
        self.setZValue(number_of_items+1)
        
        
        
    def updateLegend(self):
        """
        General update
        
        """
        
        # See if we have any entries
        table = self.plotTable
        
        # If no entries then exit and do nothing
        if not table:
            return
            
            
        self.calculateCellDimensions()
        
        
        
    
    @property
    def rect(self):
        """
        Return rect for the legend box        
            
        Output
        ------
        rect_IC : QRect()
            legend rectangle coordinates
            
        """
        
        # Debug stuff remove when everything is working [TODO]
#        print('\n')
#        print('*'*70)
#        print('GraphLegend:rect')
#        print('rows =',self.rows)
#        print('columns =',self.columns)
#        print('cell_width =',self.cell_width_IC)
#        print('cell_height =',self.cell_height_IC)
#        print('*'*70)
#        print('\n')
#        
        
        # Convert normalised width and height to item coordinates
        
        if self.rows is None or self.columns is None:
            width_IC = height_IC = 0
        else:
            width_IC  = self.columns*self.cell_width_IC + 2*self.outlineMargin
            height_IC = self.rows*self.cell_height_IC + 2*self.outlineMargin
        
        
        
        return QRectF(0,0,width_IC,height_IC)
        
        
    @property
    def rect_NC(self):
        """
        Return rect for legend box in normalised coordinates
        
        Output
        ------
        rect_NC : QRect()
            legend rectangle with x,y = 0,0 and width and height in 
            normalised coordinates
            
        """
        
        rect_SC =self.mapRectToScene(self.rect)
        x_NC,y_NC = self.coordinateManager.scene2norm([0,rect_SC.width()],[0,rect_SC.height()])

        w_NC = abs(x_NC[1]-x_NC[0])        
        h_NC = abs(y_NC[1]-y_NC[0])

        
        return QRectF(0,0,w_NC,h_NC)
        
        
        
    def calculateCellDimensions(self):
        """
        Calculate how big each cell in the legend is going to be
        
        """
        
        # Get maximum name lengths
        # --------------------------------
        max_name_length = max([len(name) for name in self.channel_dict])
        self.cell_textWidth_chars = min([max_name_length,self.maxTextLength_chars])
        
        # Text sizes
        # ----------------------
        charWidth_px = self.fmt.averageCharWidth()
        charHeight_px = self.fmt.height()
        
        textLength_IC = self.cell_textWidth_chars*charWidth_px
        
        # Calculate overall width and height of cell
        # ---------------------------------------------
        self.cell_width_IC = (self.cell_HBuffer_IC + 
                                self.cell_lineLength_IC +
                                self.cell_gapLength_IC +
                                textLength_IC +
                                self.cell_HBuffer_IC)
                                
        self.cell_height_IC = (self.cell_VBuffer_IC + charHeight_px + self.cell_VBuffer_IC)
        
        
        
        
    def drawCells(self,painter,x_IC,y_IC):
        """
        Draw legend cells on the screen
        
        Inputs
        -------
        painter : QPainter
            supplied by the main paint() functions
            
        x_IC,y_IC : int or floats
            coordinates of top left hand corner of the legend cell
            
            
        """
        
        # If no plots then don't draw anything
        if not self.plotTable:
            return
            
        
        # Draw the cells
        # =============================
        
        for col in range(self.columns):
            
            for row in range(self.rows):
                
                # Get plot name and styles
                # ===========================
                plot_name = self.plotTable[row][col]
                
                # Skip on if there is no name
                if plot_name is None:
                    continue
                
                # Get the plot series object
                plot_series = self.channel_dict[plot_name]
                
                
                # Setup colours and styles
                # ================================
                backgroundColour = self.cellBackgroundColour
                painter.setBrush(QBrush(backgroundColour))
                
                outlineColour = self.cellBorderColour
                outlineColour.setAlpha(self.cellTransparency)
                pen = QPen(outlineColour)
                pen.setStyle(self.cellDashStyle)
                pen.setWidthF(self.cellWidth)
                painter.setPen(pen)
                
                
                # Define top left hand corner of cell
                # ======================================
                ox = x_IC+col*self.cell_width_IC
                oy = y_IC+row*self.cell_height_IC
                
                
                # Draw cell outline
                # ============================
                rect = QRectF(ox,
                              oy,
                              self.cell_width_IC,
                              self.cell_height_IC)
                
                
                painter.drawRect(rect)
                
                
                # Draw legend line 
                # ================================
                
                # Get line styles from channel
                
                lineColour = QColor()
                lineColour.setNamedColor(plot_series.lineColour)
                lineColour.setAlpha(plot_series.lineTransparency)
                pen = QPen(lineColour)
                pen.setStyle(plot_series.lineDashStyle)
                pen.setWidthF(plot_series.lineWidth)
                
                painter.setPen(pen)
                
                # Draw line
                x1 = ox + self.cell_HBuffer_IC
                x2 = x1 + self.cell_lineLength_IC
                y1 = y2 = oy + int(self.cell_height_IC/2)
                painter.drawLine(x1,y1,x2,y2)
                
                # Draw markers
                # ================
                
                # Get styles
                pen = QColor()
                pen.setNamedColor(plot_series.markerColour)
                pen.setAlpha(plot_series.markerTransparency)
                
                brush = QColor()
                brush.setNamedColor(plot_series.markerFillColour)
                brush.setAlpha(plot_series.markerTransparency)
                
                painter.setPen(pen)
                painter.setBrush(brush)
                
                if plot_series.drawMarkers:
                    
                    mx_IC = [x1,x2]
                    my_IC = [y1,y2]
                    
                    for iPoint in range(2):
            
                        # Move to the data point (translate)
                        # Scale to marker size (scale)
                        # draw marker shape
                        # 
                        # this is done inside a save/restore to avoid
                        # changing the other points.
                        
                        painter.save()
                        
                        tr = QTransform()
                        tr.translate(mx_IC[iPoint],my_IC[iPoint])
                        # TODO : aspect ratio conversion needed here
                        tr.scale(plot_series.markerSize,plot_series.markerSize)
                        
                        finalPath = tr.map(plot_series.markerShape)
                        painter.drawPath(finalPath)
            
                        painter.restore()
                
                
                
                # Draw text
                # =================
                textColour = self.textColour
                painter.setPen(textColour)                
                painter.setFont(self.font)
                
                
                txt_x_IC = ox + (self.cell_HBuffer_IC 
                                + self.cell_lineLength_IC
                                + self.cell_gapLength_IC)
                                
                txt_y_IC = oy + (self.cell_height_IC - self.cell_VBuffer_IC)
                                
                
                painter.drawText(txt_x_IC,txt_y_IC,truncateText(plot_name,self.maxTextLength_chars))
                
        
     
    @property
    def plotTable(self):
        """
        Return channels in a list of lists that is basically a table
        representation of the final legend.
        
        Always return a 2D table, even if there are only one row or one column.
        Drawing always assumes a 2D table.
        
        Output
        ------
        table : list of lists
            table of strings representing the names of each curve to shown in
            the legend. Where there are not enough plots to fill the table then
            the entry will be None.
        
        """
        
        # Check for no entries
        # ============================
        nPlots = len(self.channel_dict)
        
        if nPlots==0:
            return
            
            
        # Check for no change case
        # ================================
        if self._plot_table != [] and self._num_plots==nPlots and not self.forceUpdate:
            return self._plot_table
        
            
        
        
        # Create the plot table fro scratch
        # ====================================
        
        # Convert plot dict to list
        plot_names = [k for k in self.channel_dict]
        
        # Update number of plots in legend
        self._num_plots = len(plot_names)
        
        # Make the table
        # Note plot_names gets destroyed in the process
        self._plot_table = makeLegendTable(plot_names,self.max_entries,
                                           orientation=self.orientation)
                                           
                                           
        # record rows and columns
        self.rows = len(self._plot_table)
        self.columns = len(self._plot_table[0])
               
        return self._plot_table
        
        
    # ---------------------------------------------------------------------
    # Positioning
    # ---------------------------------------------------------------------
    # Dedicated functions to set positions
        
    def upper_left(self):
        self.position_NC = LEGEND_POSITIONS[LEGEND_UPPER_LEFT]
        
    
    def upper_right(self):
        self.position_NC = LEGEND_POSITIONS[LEGEND_UPPER_RIGHT]
        
    
    def lower_left(self):
        self.position_NC = LEGEND_POSITIONS[LEGEND_LOWER_LEFT]
        
    def lower_right(self):
        self.position_NC = LEGEND_POSITIONS[LEGEND_LOWER_RIGHT]
        
        
    def upper_middle(self):
        self.position_NC = LEGEND_POSITIONS[LEGEND_UPPER_MIDDLE]
        
    def lower_middle(self):
        self.position_NC = LEGEND_POSITIONS[LEGEND_LOWER_MIDDLE]
    
    
    # ---------------------------------------------------------------------
    # Orientation
    # ---------------------------------------------------------------------    
    
    def horizontal(self):
        self.orientation = self.HORIZONTAL
        
        
    def vertical(self):
        self.orientation = self.VERTICAL
        
        
        
        
    # ---------------------------------------------------------------------
    # Menu/mouse control
    # ---------------------------------------------------------------------
        
    def mouseMoveEvent(self,event):
        """
        Mouse move or drag event. 
        
        Moves the legend
        
        """
        
        self.setFocus()

        
        # Constants
        # ----------------------
        BUTTON_DOWN = 0
        CURRENT = 1
        
        # Get mouse positions in scene coordinates
        # ------------------------------------------
        button = event.button()
        # TODO : Check the button
        
        buttonDown_SC = event.lastScenePos()
        currentPos_SC = event.scenePos()
        
        # Note on getting mouse positions:
        # There is a function called buttonDownScenePos() which is supposed to
        # give the position where the button went down. It doesn't seem to 
        # work, just gives an empty QPointF(). The lastScenePos() function
        # does work, so using that instead.
        

        
        # Convert to normalised
        # ---------------------------
        x_NC,y_NC = self.coordinateManager.scene2norm([buttonDown_SC.x(),currentPos_SC.x()],
                                                      [buttonDown_SC.y(),currentPos_SC.y()])
                                                      
        
        # Calculate offset from top left corner of legend
        # -------------------------------------------------
        dx_NC = x_NC[BUTTON_DOWN] - self.position_NC[0]
        dy_NC = y_NC[BUTTON_DOWN] - self.position_NC[1]
        
        # Calculate new position of top left corner of legend
        # ----------------------------------------------------
        new_pos_x_NC = x_NC[CURRENT] - dx_NC
        new_pos_y_NC = y_NC[CURRENT] - dy_NC
        
        # Setup a rectangle in normalised coordinates
        w_NC = self.rect_NC.width()
        h_NC = self.rect_NC.height()
        
        #print('Legend width,height = %.3f,%.3f' % (w_NC,h_NC))
        
        # Check legend rectangle is inside viewport using normalised coordinates
        # Note minus sign on bottom RH corner
        check_conditions = [ new_pos_x_NC>=0,new_pos_y_NC - h_NC>=0,
                            new_pos_x_NC + w_NC<=1.0,new_pos_y_NC<=1.0,]
                            
        #print('Legend conditions',check_conditions)
        #print('legend pos',[new_pos_x_NC,new_pos_y_NC,new_pos_x_NC + w_NC,new_pos_y_NC - h_NC])
                            
        # Move legend if the whole box is inside the normalised screen
        #if viewport_rect_NC.contains(legend_rect_NC):
        if all(check_conditions):
            self.position_NC = (new_pos_x_NC,new_pos_y_NC)
            
            self.prepareGeometryChange()
            self.update()
        
        
       
            
            
            
    def contextMenuEvent(self,event):
        """
        Context menu (right click) for Horiz marker
        
        """
        
        
        # Functions for menu actions
        # ...........................
        
        def showPos():
            print('Legend at :',self.position_NC,' [NC]')
        
        
        
        # Construct menu
        # .....................
        menu = QMenu(self.parentWidget())
        
        menu.addAction('Horizontal',self.horizontal)
        menu.addAction('Vertical',self.vertical)
        menu.addSeparator()
        menu.addAction('Upper Left',self.upper_left)
        menu.addAction('Upper Right',self.upper_right)
        menu.addAction('Lower Left',self.lower_left)
        menu.addAction('Lower Right',self.lower_right)
        menu.addAction('Upper middle',self.upper_middle)
        menu.addAction('Lower middle',self.lower_middle)
        menu.addSeparator()
        menu.addAction("Print Positions",showPos)
        
        
        
        # Show menu
        menu.exec_(event.screenPos())
        
        
    def focusInEvent(self,event):
        #logger.debug("Marker got focus")
        self.selected = True
        
        
    def focusOutEvent(self,event):
        self.selected = False
        
        

#%% Support functions for GraphLegend
# --------------------------------------

def makeLegendTable(label_list,max_entries,orientation=LEGEND_VERTICAL):
    """
    Create a table (list of lists) of labels according to the max row and 
    column restraints given.
    
    Inputs
    --------
    label_list : list of str
        List of legend entries
        
    max_entries: int
        max number of entries in a row or column depending on the orientation
        
    orientation: str
        'vertical' - max_entries = max number of rows is one column
        'horizontal' - max_entries = max number of columns in one row
        
    Output
    ----------
    table : list of list of str
        Table of entries, filled with the values from label_list. If the number
        of entries does not correspond to a full table then the remaining 
        entries will be None
        
        
    Example usage
    ------------------
    
    Horizontal single row table
    
    >>> labels = [str(n) for n in range(5)]
    >>> makeLegendTable(labels,8,orientation='horizontal')
    [['0', '1', '2', '3', '4']]
    
    Horizontal multi row table
    
    >>> labels = [str(n) for n in range(15)]
    >>> makeLegendTable(labels,8,orientation='horizontal')
    [['0', '1', '2', '3', '4', '5', '6', '7'],
 ['8', '9', '10', '11', '12', '13', '14', None]]
    
    Vertical single column table
    
    >>> labels = [str(n) for n in range(5)]
    >>> makeLegendTable(labels,8,orientation='vertical')
    [['0'], ['1'], ['2'], ['3'], ['4']]
    
    
    Vertical multi column table
    
    >>> labels = [str(n) for n in range(15)]
    >>> makeLegendTable(labels,8,orientation='vertical')
    [['0', '8'],
     ['1', '9'],
     ['2', '10'],
     ['3', '11'],
     ['4', '12'],
     ['5', '13'],
     ['6', '14'],
     ['7', None]]
        
    """
    
    # Implementation note:
    # The table will be populated as if the orientation is horizontal first,
    # because this is natural for Python lists. If a vertical orientation is
    # required then the table will be transposed at the end
    
    # Get number of entries
    # --------------------------
    nEntry = len(label_list)
    
    # Less than max case
    # ---------------------
    # Number of labels is less than the max number of entries for one row or
    # column.
    if nEntry <= max_entries:
        if orientation == LEGEND_HORIZONTAL:
            # single row table
            return [label_list]
        else:
            # single column table
            return [[entry] for entry in label_list]
            
            
    # General 2D case
    # --------------------
    # Where there are more than the max number of entries per column or row
        
    
    # Make the output list
    table = []

    # For now assume this is a horizontal table, so we will populate by rows
    # Calculate how many rows will be required
    nRows = int(np.ceil(nEntry/max_entries))
    
    # Calculate how many empty table entries are left with this many rows
    nEmptyEntries = nRows*max_entries - nEntry
    
    # Pad label_list so that it is an integer multiple of the number of max entries
    label_list += [None]*nEmptyEntries
    
    print('Length of list = %i' % nEntry)
    print('Max entries = %i' % max_entries)
    print('Number of rows in table = %i' % nRows)
    print('Padded list length = %i' % len(label_list))
    
    
    for row in range(nRows):
        # 'Cool' list comprehension way to pop multiple entries from the list
        # pop max_entries number of elements for each row
        table.append([label_list.pop(0) for n in range(max_entries)])
    
    # Return horizontal here
    if orientation == LEGEND_HORIZONTAL:
        return table
        
        
    # Vertical format: transpose list of lists
    # ---------------------------------------------
    # Make an empty table
    transpose_table = [[None for k in range(nRows)] for n in range(max_entries)]
    
    # Now flip the rows and columns
    for row in range(nRows):
        for col in range(max_entries):
            transpose_table[col][row] = table[row][col]
            
    return transpose_table
    

def truncateText(text_string,max_char=32):
    """
    Return a truncated string

    Inputs
    --------
    text_string : str
        full text to truncate
        
    max_char : int
        maximum number of characters to return
        
    Output
    ------
    truncated_text : str
        text truncated to max_char or less
        
    """
    
    if len(text_string)<= max_char:
        return text_string
        
    else:
        return text_string[0:max_char]

#=============================================================================
#%% GraphTextBoxItem class
#=============================================================================


class GraphTextBoxItem(QGraphicsItem):
    """
    Text box for use as axis labels or graph title.
    Can have a variety of different styles
    
    """
    
    def __init__(self,coordinateManager):
        """
        Inputs
        -------
        
        coordinateManager : class
            link to coordinate manager for the GraphWidget
            
        """
            
        
        super(GraphTextBoxItem, self).__init__(parent)
        
        self.coordinateManager = coordinateManager
        
        
        # Position coordinates
        # --------------
        # In Normalised Coordinates
        self.x_NC = 0
        self.y_NC = 0
        
        # Text to display
        # ----------------
        self._text = 'No text'
        
        # Text item
        # -----------
        self._editor = QLineEdit()
        self.lineEdit = QGraphicsProxyWidget()
        self.lineEdit.setWidget(self._editor)
        
        
        # Font
        # --------
        self.font = QFont()
        self.font.setPixelSize(8)
        self.fmt = QFontMetrics(self.font)
        
        
        # Appearance
        # -------------
        self.boxStyle = 'plain'
        self.backgroundColour = '#aa00ff' # TODO replace this
        self.borderColour = '#aa00ff'
        self.textColour = '#aa00ff'
        
        self.visible = True
        self.transparency = 255
        
        # TODO : select this based on style
        self.boxFunction = self.plainBox
        
        
        # Position in Scene coordinates
        # ----------------------------
        self.x_SC = 0
        self.y_SC = 0
        self.rect = None
        self._shape = None
        self.poly = None
        self.text_x_SC = 0
        self.text_y_SC = 0
        
        # Calculate the shape
        self.boxFunction()
        
        
        
    def boundingRect(self):
        """
        Return rectangle in scene coordinate
        
        """
        
        # TODO convert to scene coordinates
        
        
        # Return scaled rectangle
        return self.rect
        
        
    
    def shape(self):
        
        return self._shape
        
        
        
    
    def paint(self, painter, option, widget=None):
        """
        Draw the Text box
        
        """
 
        
        if not self.visible:
            alpha = 0
        else:
            alpha = self.transparency
        
        if DEBUG:
            # Draw bounding rect
            painter.save()
            painter.setPen(QColor(Qt.red))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.boundingRect())
            painter.restore
            
            
            
        
        # Draw the box
        # ---------------------
        pen = QColor()
        pen.setNamedColor(self.borderColour)
        pen.setAlpha(alpha)
        
        brush = QColor()
        brush.setNamedColor(self.backgroundColour)
        brush.setAlpha(alpha)
        
        painter.setPen(pen)
        painter.setBrush(brush)
        
        painter.drawPoly(self.poly)
        
        
        # Draw the text
        # ---------------
        painter.drawText(QPointF(self.text_x_SC,self.text_y_SC),self._text)
        
        
    def setText(self,new_text):
        """
        Set text 
        
        Inputs
        --------
        new_text : str
        
        """
        
        # Set the text
        self._text = new_text
        
        # Recalculate box
        self.boxFunction()
        
        
    def text(self):
        return self._text
        
        
        
        
        
    # --------------------------------------------------------------------
    # Box coordinates calculations
    # --------------------------------------------------------------------  
    # Define a function to calculate the coordinates of boxes with different
    # styles.
        
    def plainBox(self):
        """
        Plain box style

          +------------------------------------+
          |                                    |
          |   +----------------------------+   |
          |   |                            |   |
          |   |<Text goes here>            |   |
          |   +----------------------------+   |
          |                                    |
          +------------------------------------+
          
        """
        
        # Settings
        # -----------
        
        # Padding in units of characters
        # Front padding
        padF_x = 2
        padF_y = 0.2
        
        # Rear padding
        padR_x = 3
        padR_y = 0.3
        
      
        # Get  text rectangle
        # -------------------
        textRect = self.fmt.boundingRect(self._text)
        txtWidth = textRect.width()
        textHeight = textRect.height()
        nChars = len(self._text)
        
        
        # Character size
        # ---------------
        charRect = self.fmt.boundingRect(self._text)
        charWidth = charRect.width()
        charHeight = charRect.height()
        
        
        # Box coordinates normalised to character size
        # --------------------------------------------
        boxCoords = np.array( [[0,0],
                               [(padF_x+nChars+padR_x),0],
                               [(padF_x+nChars+padR_x),(padF_y+1+padR)],
                               [0,(padF_y+1+padR)]],
                                dtype=[('x',float),('y',float)])
                                
                                
        # Convert normalised units to scene units
        # ----------------------------------------
        x_SC,y_SC = self.coordinateManager.norm2scene(self.x_NC,self.y_NC)  

        # Convert box coordinates to scene coordinates
        # ---------------------------------------------
        # Multiply by character size and add to x_SC,y_SC
        boxCoords['x'] = x_SC + charWidth*boxCoords['x']
        boxCoords['y'] = y_SC + charHeight*boxCoords['y'] 
        
        
        # Make a polygon
        # ----------------
        self.poly = array2polygon(boxCoords['x'],boxCoords['y'])
        
        # Calculate text position
        # -------------------------
        self.text_x_SC = x_SC + padF_x*charWidth
        self.text_y_SC = y_SC + padF_y*charHeight
        
        # Calculate shape and bounding rect
        # -----------------------------------
        self._shape = poly
        self.rect = poly.boundingRect()
        
        
        
        
        

#=============================================================================
#%% Coordinate manager class
#=============================================================================


class CoordinateManager():
    """ 
    Class for managing different coordinate systems that are used
    to plot graphs.
    
    The coordinate systems are:
    
    * Data Coordinates [DC] defined by the data to be plotted
    
    * Scene coordinates [SC] the size of the QGraphics scene that holds all
      the graphics items
      
    * View coordinates [PX] the viewport coordinates in pixels
    
    * Normalised coordinates [NC] normalised to bottom left hand corner of 
      viewport and ranging from 0-1 in both directions
      
    * Item coordinates [IC] coordinates inside individual items
    
    Data coordinates are specific to the graph plotting. They are an additional
    set that allows scaling and plotting the y axis in the "growing upward" sense.
    
    Class properties have the units abbreviation appended to be explicit
    about which coordinate system is being used (e.g. x_min_DC)
    
    """
    
    def __init__(self,scene,viewport):
        """ 
        Initialise the class with references to scene and viewport. So that
        the class can access their coordinate mapping functions.
        
        """
        
        # Data coordinates
        # -----------------
        
        self.x_min_DC = -10
        self.x_max_DC = 10
        
        self.y_min_DC = -10
        self.y_max_DC = 10
        
        # Min and Max data values for all data series
        # --------------------------------------------
        # Set initial values to +/- infinity so that any real numbers will
        # override them.
        self.x_data_min_DC = np.inf
        self.x_data_max_DC = -np.inf
        
        self.y_data_min_DC = np.inf
        self.y_data_max_DC = -np.inf
        
        
        # Scene reference
        # ------------------
        self.scene = scene
        
        # View port reference
        # -----------------------
        self.viewport = viewport
        
        
        
        # PlotBox position in normalised coordinates
        # --------------------------------------------
        self.plot_box_x_NC = 0.1
        self.plot_box_y_NC = 0.125
        self.plot_box_width_NC = 0.8
        self.plot_box_height_NC = 0.8 #0.75
        
        # Axis limit editor positions in normalised coordinates
        # --------------------------------------------------------
        self.xMinEditorPos = (0.09,0.11)
        self.xMaxEditorPos = (0.9,0.11)
        
        self.yMinEditorPos = (0.08,0.125)
        self.yMaxEditorPos = (0.08,0.925)
                
        
        # Grid spacing
        # ------------------------
        self.x_grid_major_tick_spacing_DC = 2
        self.x_grid_major_DC = np.arange(-10,11,2)
        
        self.y_grid_major_tick_spacing_DC = 2
        self.y_grid_major_DC = np.arange(-10,11,2)
        
        self.x_grid_minor_tick_spacing_DC = 0.2
        self.x_grid_minor_DC = np.arange(-10,10,0.2)
        
        self.y_grid_minor_tick_spacing_DC = 0.2
        self.y_grid_minor_DC = np.arange(-10,10,0.2)
        
        # labelling
        # ---------------------------
        self.x_label_format = '%.1f'
        self.y_label_format = '%.1f'
        
        # Zoom
        # -----------------------------
        # Zoom factor dictionary
        # the keys are :
        #   +1 : Expand axis
        #   -1 : Contract axis
        self.zoom_factor = {1:1.2,-1:0.6} 
        
        # TODO : These may be redundant
        self.zoom_out_factor = 1.2
        self.zoom_in_factor = 0.8
        
        
    # ------------------------------------------------------------------------    
    # Axis scaling and zooming
    # ------------------------------------------------------------------------
    def general_update(self):
        self.viewport.recalculate_graphs()
        self.scene.update()
    
    
    def updateDataMinMax(self,xmin,xmax,ymin,ymax):
        """
        Update the data min and max values
        
        Inputs
        -------
        xmin,xmax,ymin,ymax: float
            new min max values from data, usually a new channel or chunk.
            
        
        """
        
        # Check if the min/max limits need updating
        if xmin < self.x_data_min_DC:
            self.x_data_min_DC = xmin
            
        if xmax < self.x_data_max_DC:
            self.x_data_max_DC = xmax
            
            
        if ymin < self.y_data_min_DC:
            self.y_data_min_DC = ymin
            
        if ymax < self.y_data_max_DC:
            self.y_data_max_DC = ymax
            
        
        
        
    def autoscale(self,axis=None):
        """
        Autoscale the individual or both axes
        
        * Get the min and max values from all channels
        
        * Update either one or both axes
        
        Inputs
        ----------
        axis: str or None
            None - autoscales both axes
            'x' or 'y' autoscales individual axis
            
        """
        
        # Check for min/max values being the same
        # ===========================================
        if self.x_data_min_DC == self.x_data_max_DC:
            tmp = self.x_data_max_DC
            self.x_data_min_DC = 0.9*tmp
            self.x_data_max_DC = 1.1*tmp
            

        if self.y_data_min_DC == self.y_data_max_DC:
            tmp = self.y_data_max_DC
            self.y_data_min_DC = 0.9*tmp
            self.y_data_max_DC = 1.1*tmp
        
            
        
        # Set new scales
        # =================================
        # Get min and max values logged from all series
        # and set new scales
        
        if axis in ['x','X']:
            self.update_x_axis(self.x_data_min_DC,self.x_data_max_DC)
        elif axis in ['y','Y']:
            self.update_y_axis(self.y_data_min_DC,self.y_data_max_DC)
        else:
            self.update_x_axis(self.x_data_min_DC,self.x_data_max_DC)
            self.update_y_axis(self.y_data_min_DC,self.y_data_max_DC)
            
        self.viewport.recalculate_graphs()
        self.scene.update()
            
        
        
    
    def zoom_all(self,direction):
        """Expand/contract both x and y scales
        
        Applies the zoom factor to both axes once. This is intended to be
        called by wheel events from PlotBox or Axis classes
        
        Inputs
        -------
        direction = +1 to expand axis range, -1 to contract axis range
        
        """
        
        self.zoom_x_axis(direction,update=False)
        self.zoom_y_axis(direction,update=False)
        self.viewport.recalculate_graphs()
        self.scene.update()
        
        
        
    
    def zoom_x_axis(self,direction,update=True):
        """ Expand/contract x axis scale
        
        Inputs
        -------
        direction = +1 to expand axis range, -1 to contract axis range
        
        """
        
        # Calculate intermediate axis range
        axis_range_DC = (self.x_max_DC-self.x_min_DC)*self.zoom_factor[direction]
        axis_centre_DC = (self.x_max_DC+self.x_min_DC)/2
        
        new_min_DC = axis_centre_DC - axis_range_DC/2
        new_max_DC = axis_centre_DC + axis_range_DC/2
        
        # update scale
        self.update_x_axis(new_min_DC,new_max_DC)
        
#        # TODO : Minor ticks
#        if DEBUG:
#            print("direction = ",direction)
#            print("New x axis range [%.1f - %.1f]" % (self.x_min_DC,self.x_max_DC))
#            print("minor tick spacing = ",newScale.minorTickSpacing)
        
        if update:
            self.viewport.recalculate_graphs()
            self.scene.update()
            
        
        
    def zoom_y_axis(self,direction,update=True):
        """ Expand/contract y axis scale
        
        Inputs
        -------
        direction = +1 to expand axis range, -1 to contract axis range
        
        """
        
        # Calculate intermediate axis range
        axis_range_DC = (self.y_max_DC-self.y_min_DC)*self.zoom_factor[direction]
        axis_centre_DC = (self.y_max_DC+self.y_min_DC)/2
        
        new_min_DC = axis_centre_DC - axis_range_DC/2
        new_max_DC = axis_centre_DC + axis_range_DC/2
        
        # update scale
        self.update_y_axis(new_min_DC,new_max_DC)
        
        
#        # TODO : Minor ticks
#        if DEBUG:
#            print("direction = ",direction)
#            print("New y axis range [%.1f - %.1f]" % (self.y_min_DC,self.y_max_DC))
#            print("minor tick spacing = ",newScale.minorTickSpacing)
#        
        if update:
            self.viewport.recalculate_graphs()
            self.scene.update()
            
            
            
    def pan(self,dx_DC,dy_DC):
        """
        Calculate axis adjustments for panning.
        
        Take changes in x and y and calculate how much to change the axis
        limits by.
        
        Inputs
        --------------
        dx_DC, dy_DC : floats
            differences in x and y coordinates. These are taken from how much
            the mouse was dragged. Typically they come from PlotBox mouse events.
            
        """
        
        # Check how large the differences are
        # if they are larger than a fraction of minor grid spacing then adjust the
        # axis limits by one minor grid space
        
        # x axis
        if abs(dx_DC) > 0.1*self.x_grid_minor_tick_spacing_DC:
            self.pan_x_axis(np.sign(dx_DC))
            
        # y axis
        if abs(dy_DC) > 0.1*self.y_grid_minor_tick_spacing_DC:
            self.pan_y_axis(np.sign(dy_DC))
        
        
    def pan_x_axis(self,direction,update=True):
        """
        Pan the x-axis by changing the axis limits by one minor grid spacing
        
        Inputs:
        --------------
        direction: signed int
            +1 (to right) or -1 (to left)
            
        """
        
        # Calculate shift
        axis_shift_DC = - direction*self.x_grid_minor_tick_spacing_DC
        #print("\n [pan_x_axis] axis_shift_DC = ",axis_shift_DC)
      
        # Shift the axis
        self.x_min_DC += axis_shift_DC
        self.x_max_DC += axis_shift_DC
        
        self.update_x_axis(self.x_min_DC,self.x_max_DC)
        
        
        if update:
            self.viewport.recalculate_graphs()
            self.scene.update()
            
            
            
            
            
    def pan_y_axis(self,direction,update=True):
        """
        Pan the y-axis by changing the axis limits by one grid spacing
        
        Inputs:
        --------------
        direction: signed int
            +1 (to right) or -1 (to left)
            
        """
        
        # Calculate shift
        axis_shift_DC = - direction*self.y_grid_minor_tick_spacing_DC
      
        # Shift the axis
        self.y_min_DC += axis_shift_DC
        self.y_max_DC += axis_shift_DC
        
        self.update_y_axis(self.y_min_DC,self.y_max_DC)
        
        
        if update:
            self.viewport.recalculate_graphs()
            self.scene.update()
            
        
        
        
        
    def update_x_axis(self,new_min_DC,new_max_DC):
        """
        Update x axis scale and grid lines for new min and max.
        
        Uses the NiceScale class to give readable axis ticks
        
        Inputs:
        -------------
        new_x_min_DC,new_x_max_DC: float
            new axis limits
            
        """
  
        
        # Find "nice" range
        newScale = NiceScale(new_min_DC,new_max_DC)
        
        
        # Set new min and max to requested values
        self.x_min_DC = new_min_DC
        self.x_max_DC = new_max_DC
        
        # Use nice scale to define ticks
        self.x_grid_major_tick_spacing_DC = newScale.tickSpacing
        self.x_grid_major_DC = np.arange(newScale.niceMin,newScale.niceMax,newScale.tickSpacing)
        
        self.x_grid_minor_tick_spacing_DC = newScale.minorTickSpacing
        self.x_grid_minor_DC = np.arange(newScale.niceMin,newScale.niceMax,newScale.minorTickSpacing)
        
        self.update_label_format("x")
            

    def update_y_axis(self,new_min_DC,new_max_DC):
        """
        Update y axis scale and grid lines for new min and max.
        
        Uses the NiceScale class to give readable axis ticks
        
        Inputs:
        -------------
        new_y_min_DC,new_y_max_DC: float
            new axis limits
            
        """
        
        # Find "nice" range
        newScale = NiceScale(new_min_DC,new_max_DC)
        
        self.y_min_DC = new_min_DC
        self.y_max_DC = new_max_DC
        
        self.y_grid_major_tick_spacing_DC = newScale.tickSpacing
        self.y_grid_major_DC = np.arange(newScale.niceMin,newScale.niceMax,newScale.tickSpacing)
        
        self.y_grid_minor_tick_spacing_DC = newScale.minorTickSpacing
        self.y_grid_minor_DC = np.arange(newScale.niceMin,newScale.niceMax,newScale.minorTickSpacing)
        
        self.update_label_format("y")


    # Convenience functions for updating the axis limits
    # -----------------------------------------------------
    # These functions all take into account if a min is set higher than a max
    # or vice versa and make a simple offset to keep max above min


    def set_x_min_DC(self,new_value):        
        
        if new_value > self.x_max_DC:
            return
            
        self.update_x_axis(new_value,self.x_max_DC)
        
        
            
    def set_x_max_DC(self,new_value):        
        
        if new_value < self.x_min_DC:
            return
            
        self.update_x_axis(self.x_min_DC,new_value)
        
        
        
    def set_y_min_DC(self,new_value):        
        
        if new_value > self.y_max_DC:
            return
        
        self.update_y_axis(new_value,self.y_max_DC)
        
        
            
    def set_y_max_DC(self,new_value):        
        
        if new_value < self.y_min_DC:
            return
            
        self.update_y_axis(self.y_min_DC,new_value)
        
        
    def reset_data_min_max(self):
        """
        Reset the min and max values used for autoscaling
        
        """
        self.x_data_min_DC = np.inf
        self.x_data_max_DC = -np.inf
        
        self.y_data_min_DC = np.inf
        self.y_data_max_DC = -np.inf
    
    # ------------------------------------------------------------------------    
    # Coordinate conversions
    # ------------------------------------------------------------------------
        
    def data2scene(self,x_data_DC,y_data_DC):
        """ 
        Convert from data to scene coordinates
        The data values are assumed to be contained in the PlotBox rectangle
        
        Inputs
        --------
        x_data_DC, y_data_DC = x,y coordinates to be converted. Both are arrays
                                or lists
                                
        Outputs
        --------
        x_data_SC, y_data_SC = x,y converted to scene coordinates
        
        """
        # Input data validation
        # --------------------------------
        if isinstance(x_data_DC,list):
            x_data_DC = np.array(x_data_DC)
            
        if isinstance(y_data_DC,list):
            y_data_DC = np.array(y_data_DC)
            
    
        
        
        # Get Plot box dimensions in scene coordinates
        # ---------------------------------------------
        plot_box_rect_SC = self.plotBox2scene()
        # plot_box_rect.x, plot_box_rect.y, plot_box_rect.width, plot_box_rect.height
        
        
        # Calculate x values
        # ----------------------
        x_scale = plot_box_rect_SC.width()/(self.x_max_DC - self.x_min_DC)
        x_data_SC = plot_box_rect_SC.x() + (x_data_DC - self.x_min_DC)*x_scale
        
        
        # Calculate y values
        # ----------------------
        # This accounts for the scene coordinates having y values increase
        # in the downwards direction, but data coordinates grow upwards.
        # The points are calculated by a difference from y_max_DC instead
        # of the min value as in the x coordinate above
        y_scale = plot_box_rect_SC.height()/(self.y_max_DC - self.y_min_DC)
        y_data_SC = plot_box_rect_SC.y() + (self.y_max_DC - y_data_DC )*y_scale
        
        
        return x_data_SC,y_data_SC
        
        
        
    def scene2data(self,x_data_SC,y_data_SC):
        """
        Convert from scene to data coordinates
        
        
        """
        
        # Input data validation
        # --------------------------------
        
        # Convert to arrays for speed
        if isinstance(x_data_SC,list):
            x_data_SC = np.array(x_data_SC)
            
        if isinstance(y_data_SC,list):
            y_data_SC = np.array(y_data_SC)
            
            
        # Get Plot box dimensions in scene coordinates
        # ---------------------------------------------
        plot_box_rect_SC = self.plotBox2scene()
        # plot_box_rect.x, plot_box_rect.y, plot_box_rect.width, plot_box_rect.height
        
        
        # Calculate x values
        # ----------------------
        x_scale = plot_box_rect_SC.width()/(self.x_max_DC - self.x_min_DC)
        x_data_DC = self.x_min_DC + (x_data_SC-plot_box_rect_SC.x())/x_scale
        
        # Calculate y values
        # ----------------------
        # Get distance from plotBox top LH corner and subtract scaled
        # version from data max 
        # Different to x because y grows downward in QT coordinate systems
        y_scale = plot_box_rect_SC.height()/(self.y_max_DC - self.y_min_DC)
        y_data_DC = self.y_max_DC - (y_data_SC-plot_box_rect_SC.y())/y_scale
          
          
        return x_data_DC,y_data_DC
        
        
        
        
    def data2item(self,graphics_item,x_data_DC,y_data_DC):
        """
        Map data coordinates into QGraphicsItem local coordinate
        system [IC]
        
        Inputs
        ------------
        graphics_item = instance of QGraphicsItem
        x_data_DC, y_data_DC = x,y coordinates to be converted. Both are arrays
                                or lists
                                
        Outputs
        --------
        x_data_IC, y_data_IC = x,y converted to item coordinates
        
        """
        
        # Convert to scene coordinates
        x_data_SC,y_data_SC = self.data2scene(x_data_DC,y_data_DC)
        
        # Use QGraphicsItem.mapFromScene() to convert to item's
        # local coordinate system
        nData = len(x_data_SC)
        x_data_IC = np.zeros(nData)
        y_data_IC = np.zeros(nData)
        
        for iP in range(nData):
            pt_IC = graphics_item.mapFromScene(QPointF(x_data_SC[iP],y_data_SC[iP]))
            
            x_data_IC[iP] = pt_IC.x()
            y_data_IC[iP] = pt_IC.y()
            
            
        # Return arrays
        return x_data_IC,y_data_IC
        
        
    def data2itemQPoints(self,graphics_item,x_data_DC,y_data_DC):
        """
        Map data coordinates into QPoints in QGraphicsItem local coordinate
        system [IC].
        
        GraphSeries objects need their final coordinates as a list of QPoints.
        This function goes direct from data coordinates to QPoints in local item
        coordinates.
        
        Inputs
        ------------
        graphics_item = instance of QGraphicsItem
        x_data_DC, y_data_DC = x,y coordinates to be converted. Both are arrays
                                or lists
                                
        Outputs
        --------
        QPoint_list = x,y converted to item QPoints
        
        """
        
        # Convert to scene coordinates
        x_data_SC,y_data_SC = self.data2scene(x_data_DC,y_data_DC)
        
        # Use QGraphicsItem.mapFromScene() to convert to item's
        # local coordinate system
        nData = len(x_data_SC)
        
        QPoint_list = []
        for iP in range(nData):
            QPoint_list.append(graphics_item.mapFromScene(QPointF(x_data_SC[iP],y_data_SC[iP])) )
            
            
            
        # Return list of QPoints
        return QPoint_list
        
        
        
    def item2data(self,graphics_item,x_data_IC,y_data_IC):
        """
        Map item coordinates to data coordinates
        
        Inputs
        ------------
        graphics_item : QGraphicsItem
            The graphics item whose coordinate system is being used
            
        x_data_IC, y_data_IC: list or numpy array
            x,y item coordinates to be converted
            
        Outputs
        -----------
        x_data_DC, y_data_DC : numpy array
            Data coordinates corresponding to inputs
        """
        
        # TODO:
        
        # Validate input data
        # ------------------------------
        nData = len(x_data_IC)
        assert nData == len(y_data_IC),"CoordinateManager:item2data:x and y data are not the same length"
        
        
        # Convert from item to scene coordinates
        # ---------------------------------------
        # Intermediate arrays to get scene coordinates
        x_data_SC = np.zeros(nData)
        y_data_SC = np.zeros(nData)
        
        for iP in range(nData):
            # Use QT to map to scene coordinates
            pt_SC = graphics_item.mapToScene(QPointF(x_data_IC[iP],y_data_IC[iP]))
            
            # Store data
            x_data_SC[iP] = pt_SC.x()
            y_data_SC[iP] = pt_SC.y()
            
            
        # Convert scene coordinates to data coordinates
        # ----------------------------------------------
        x_data_DC,y_data_DC = self.scene2data(x_data_SC,y_data_SC)
        
        return x_data_DC,y_data_DC
                                
        
        
    def itemClipRect(self,graphics_item):
        """
        Return plotBox clipping rectangle in item coordinates
        
        Translates x,y axis ranges into a rectangle
        
        Input:
        -------------
        graphics_item: QGraphicsItem
            item in the scene
            
        Output
        ----------
        clipRect_IC : QRectF
            clip rectangle in item coordinates
        
        """
        
        # Convert axis ranges to item coordinates
        # --------------------------------------------
        x_DC = [self.x_min_DC,self.x_max_DC]
        y_DC = [self.y_min_DC,self.y_max_DC]
        
        x_IC,y_IC = self.data2item(graphics_item,x_DC,y_DC)
        
        # Make rectangle
        # -------------------
        
        # Top LH corner
        rect_x_IC = min(x_IC)
        rect_y_IC = min(y_IC)
        
        # Width and height
        rect_w_IC = abs(x_IC[1]-x_IC[0])
        rect_h_IC = abs(y_IC[1]-y_IC[0])
        
        return QRectF(rect_x_IC,rect_y_IC,rect_w_IC,rect_h_IC)
        
        
        
    def plotBox2scene(self):
        """
        Convert plot box normalised coordinates to scene coordinates
        
        Assume that the viewport always displays the whole scene. So the 
        plot box coordinates are calculated as fractions of the whole 
        scene size.
        
        Output
        ------
        plot_box_rect = QRectF() with plot box coordinates
        
        """
        
        # Get viewport dimensions
        # ---------------------------
        sceneRect_SC = self.viewport2sceneRect();
        
        
        # Calculate plot box dimensions
        # --------------------------------
        
        # x coordinate
        # straight forward distance from left side
        pb_x_SC = sceneRect_SC.x() + self.plot_box_x_NC*sceneRect_SC.width()
        
        # Plot box y coordinate is specified in normalised units relative to
        # bottom left hand corner of scene. In scene coordinates this needs 
        # to be converted to be relative the the top left hand corner
        y_from_top_NC = 1 - (self.plot_box_y_NC + self.plot_box_height_NC)
        pb_y_SC = sceneRect_SC.y() + y_from_top_NC*sceneRect_SC.height()
        
        # Width and height
        # straightforward fractions of scene width and height
        pb_width_SC = self.plot_box_width_NC*sceneRect_SC.width()
        pb_height_SC = self.plot_box_height_NC*sceneRect_SC.height()
        
        return QRectF(pb_x_SC,pb_y_SC,pb_width_SC,pb_height_SC)
    
    def viewport2sceneRect(self):
        """ Return the viewport rectangle in scene coordinates
        
        Output
        -----------
        viewport_rect_SC = QRectF() in scene coordinates
        """
        
        # Get scene dimensions
        # ---------------------------
        # Translate viewport dimensions into scene units
        # This gives a QPolygon with four points. Then create a rect
        # using top left and bottom right points in this polygon
        viewportCoords_SC = self.viewport.mapToScene(self.viewport.rect())
        sceneRect_SC = QRectF(viewportCoords_SC.value(0),viewportCoords_SC.value(2))
        
        return sceneRect_SC   
        
        
    def viewport2scene(self,x_PX,y_PX):
        """ Convert viewport coordinates in pixels to scene coordinates
        
        Inputs
        ------------
        x_PX,y_PX = arrays of coordinates in pixels
        
        Output
        -----------
        x_SC,y_SC = coordinates in scene coordinates
        """
        
        nData = len(x_PX)
        x_SC = np.zeros(nData)
        y_SC = np.zeros(nData)
        
        for iP in range(nData):
            Point_SC = self.viewport.mapToScene(x_PX[iP],y_PX[iP])
            x_SC[iP] = Point_SC.x()
            y_SC[iP] = Point_SC.y()
        
        return x_SC,y_SC
        
        
    def viewport2item(self,graphics_item,x_data_PX,y_data_PX):
        """ Convert from viewport to item coordinates
        
        
        Inputs
        --------
        graphics_item = instance of QGraphicsItem
        x_data_PX, y_data_PX = x,y coordinates to be converted. Both are arrays
                                or lists
                                
        Outputs
        --------
        x_data_IC, y_data_IC = x,y converted to item local coordinates
        
        """
        
        # Convert from viewport to scene coordinates
        x_data_SC,y_data_SC = self.viewport2scene(x_data_PX,y_data_PX)
        
        # Convert to item coordinates with item's mapFromScene() function
        nData = len(x_data_SC)
        x_data_IC = np.zeros(nData)
        y_data_IC = np.zeros(nData)
        
        for iP in range(nData):
            pt_IC = graphics_item.mapFromScene(QPointF(x_data_SC[iP],y_data_SC[iP]))
            
            x_data_IC[iP] = pt_IC.x()
            y_data_IC[iP] = pt_IC.y()
            
            
        # Return arrays
        return x_data_IC,y_data_IC
        
        
    def viewportWidth2item(self,graphics_item,width_PX):
        """Convert a width in viewport coordinates to a width in
        local item coordinates
        
        Inputs
        --------
        graphics_item = instance of QGraphicsItem
        width_PX = width value in viewport coordinates
        
        Output
        ---------
        width_IC = width in item coordinates
        
        """
        
        x_IC,dummy = self.viewport2item(graphics_item,[0,width_PX],[0,0])
        
        return float(abs(x_IC[1]-x_IC[0]))
        
        
        
    def viewportHeight2item(self,graphics_item,height_PX):
        """Convert at height in viewport coordinates to a height in
        local item coordinates
        
        Inputs
        --------
        graphics_item = instance of QGraphicsItem
        height_PX = height value in normalised coordinates
        
        Output
        ---------
        height_IC = height in item coordinates
        
        """
        
        dummy,y_IC = self.viewport2item(graphics_item,[0,0],[0,height_PX])
        
        return float(abs(y_IC[1]-y_IC[0]))
        
        
    def norm2scene(self,x_data_NC,y_data_NC):
        """ 
        Convert from normalised to scene coordinates
        
        
        
        Inputs
        --------
        x_data_NC, y_data_NC = x,y coordinates to be converted. Both are arrays
                                or lists
                                
        Outputs
        --------
        x_data_SC, y_data_SC = x,y converted to scene coordinates
        
        """
        # Input data validation
        # --------------------------------
        if not isinstance(x_data_NC,np.ndarray):
            x_data_NC = np.array(x_data_NC)
            
        if not isinstance(y_data_NC,np.ndarray):
            y_data_NC = np.array(y_data_NC) 
            
        
        # Get viewport dimensions
        # ---------------------------
        sceneRect_SC = self.viewport2sceneRect()
        
        
        # Convert to scene coordinates
        # --------------------------------
        
        # x coordinate
        # straight forward distance from left side
        x_SC = sceneRect_SC.x() + x_data_NC*sceneRect_SC.width()
        
        # Plot box y coordinate is specified in normalised units relative to
        # bottom left hand corner of scene. In scene coordinates this needs 
        # to be converted to be relative the the top left hand corner
        y_from_top_NC = 1 - (y_data_NC)
        y_SC = sceneRect_SC.y() + y_from_top_NC*sceneRect_SC.height()
        
        return x_SC,y_SC
        
        
    def scene2norm(self,x_SC,y_SC):
        """ 
        Convert from scene to normalised coordinates        
        
        Inputs
        --------
        x_SC, y_SC = x,y coordinates to be converted. Both are arrays
                                or lists
                                
        Outputs
        --------
        x_data_NC, y_data_NC = x,y converted to scene coordinates
        
        """
        # Input data validation
        # --------------------------------
        if not isinstance(x_SC,np.ndarray):
            x_SC = np.array(x_SC)
            
        if not isinstance(y_SC,np.ndarray):
            y_SC = np.array(y_SC) 
            
        
        # Get viewport dimensions
        # ---------------------------
        sceneRect_SC = self.viewport2sceneRect()
        
        
        # Convert to scene coordinates
        # --------------------------------
        
        # x coordinate
        # straight forward distance from left side
        #x_SC = sceneRect_SC.x() + x_data_NC*sceneRect_SC.width()
        x_NC = (x_SC - sceneRect_SC.x())/sceneRect_SC.width()
        
        # Plot box y coordinate is specified in normalised units relative to
        # bottom left hand corner of scene. In scene coordinates this needs 
        # to be converted to be relative the the top left hand corner
        #y_from_top_NC = 1 - (y_data_NC)
        #y_SC = sceneRect_SC.y() + y_from_top_NC*sceneRect_SC.height()
        
        y_NC = 1 - (y_SC-sceneRect_SC.y())/sceneRect_SC.height()
        
        return x_NC,y_NC
        
        
        
    def normWidth2scene(self,width_NC):
        """Convert a width in normalised coordinates to a width in
        scene coordinates
        
        Inputs
        --------
        graphics_item = instance of QGraphicsItem
        width_NC = width value in normalised coordinates
        
        Output
        ---------
        width_SC = width in scene coordinates
        
        """
        
        x_SC,dummy = self.norm2scene([0,width_NC],[0,0])
        
        return float(abs(x_SC[1]-x_SC[0]))
        
        
        
    def normHeight2scene(self,height_NC):
        """
        Convert at height in normalised coordinates to a width in
        scene coordinates
        
        Inputs
        --------
        graphics_item = instance of QGraphicsItem
        height_NC = height value in normalised coordinates
        
        Output
        ---------
        height_SC = height in scene coordinates
        
        """
        
        dummy,y_SC = self.norm2scene([0,0],[0,height_NC])
        
        return float(abs(y_SC[1]-y_SC[0]))
        
        
        
    def norm2item(self,graphics_item,x_data_NC,y_data_NC):
        """ Convert from normalised to item coordinates
        The data values are assumed to be contained in the PlotBox rectangle
        
        Inputs
        --------
        graphics_item = instance of QGraphicsItem
        x_data_NC, y_data_NC = x,y coordinates to be converted. Both are arrays
                                or lists
                                
        Outputs
        --------
        x_data_IC, y_data_IC = x,y converted to item local coordinates
        
        """
        
        # Convert from normalised to scene coordinates
        x_data_SC,y_data_SC = self.norm2scene(x_data_NC,y_data_NC)
        
        # Convert to item coordinates with item's mapFromScene() function
        nData = len(x_data_SC)
        x_data_IC = np.zeros(nData)
        y_data_IC = np.zeros(nData)
        
        for iP in range(nData):
            pt_IC = graphics_item.mapFromScene(QPointF(x_data_SC[iP],y_data_SC[iP]))
            
            x_data_IC[iP] = pt_IC.x()
            y_data_IC[iP] = pt_IC.y()
            
            
        # Return arrays
        return x_data_IC,y_data_IC
        
        
        
    def normWidth2item(self,graphics_item,width_NC):
        """Convert a width in normalised coordinates to a width in
        local item coordinates
        
        Inputs
        --------
        graphics_item = instance of QGraphicsItem
        width_NC = width value in normalised coordinates
        
        Output
        ---------
        width_IC = width in item coordinates
        
        """
        
        x_IC,dummy = self.norm2item(graphics_item,[0,width_NC],[0,0])
        
        return float(abs(x_IC[1]-x_IC[0]))
        
        
        
    def normHeight2item(self,graphics_item,height_NC):
        """Convert at height in normalised coordinates to a width in
        local item coordinates
        
        Inputs
        --------
        graphics_item = instance of QGraphicsItem
        height_NC = height value in normalised coordinates
        
        Output
        ---------
        height_IC = height in item coordinates
        
        """
        
        dummy,y_IC = self.norm2item(graphics_item,[0,0],[0,height_NC])
        
        return float(abs(y_IC[1]-y_IC[0]))
        
        
        
    # ------------------------------------------------------------------------    
    # Grid line conversions
    # ------------------------------------------------------------------------
        
       
    def get_xGridMajor_IC(self,graphics_item):
        """ Return list of grid line positions in the x axis in item coordinates
        
        Output
        ---------
        x_grid_positions_SC = position for vertical grid lines in x direction
        
        """
        
        x_IC,y_IC = self.data2item(graphics_item,self.x_grid_major_DC,np.zeros(len(self.x_grid_major_DC)))
        
        #x_SC = [-1,0,1]
                
        return x_IC
        
    
        
        
    def get_yGridMajor_IC(self,graphics_item):
        """ Return list of grid line positions in the y axis in item coordinates
        
        Output
        ---------
        y_grid_positions_SC = position for vertical grid lines in y direction
        """
        
        x_IC,y_IC = self.data2item(graphics_item,np.zeros(len(self.y_grid_major_DC)),self.y_grid_major_DC)
        
        
        return y_IC
        
        
        
       
    def get_xGridMinor_IC(self,graphics_item):
        """ Return list of grid line positions in the x axis in item coordinates
        
        Output
        ---------
        x_grid_positions_SC = position for vertical grid lines in x direction
        
        """
        
        x_IC,y_IC = self.data2item(graphics_item,self.x_grid_minor_DC,np.zeros(len(self.x_grid_minor_DC)))
        
        return x_IC
        
        
    def get_yGridMinor_IC(self,graphics_item):
        """ Return list of grid line positions in the y axis in item coordinates
        
        Output
        ---------
        y_grid_positions_SC = position for vertical grid lines in y direction
        """
        
        x_IC,y_IC = self.data2item(graphics_item,np.zeros(len(self.y_grid_minor_DC)),self.y_grid_minor_DC)
        
        return y_IC
        
        
    # ------------------------------------------------------------------------    
    # Label formatting
    # ------------------------------------------------------------------------
    def x_grid_major_labels(self):
        """Convert x major grid values to a list of strings
        This is used to label the x axis
        """
        
        labels = []
       
        for value in self.x_grid_major_DC:
            labels.append(self.x_label_format % value)
            
        return labels
     
     
    def y_grid_major_labels(self):
        """Convert y major grid values to a list of strings
        This is used to label the y axis
        """
        
        labels = []
       
        for value in self.y_grid_major_DC:
            labels.append(self.y_label_format % value)
            
        return labels
        
        
        
    def update_label_format(self,axis="all"):
        """
        Adapt label format to magnitude of data
        
        
        """
        
        if axis == "x":
            self.x_label_format = util.getNumberFormat(self.x_max_DC-self.x_min_DC)
        elif axis == "y":
            self.y_label_format = util.getNumberFormat(self.y_max_DC-self.y_min_DC)
        else:
            self.x_label_format = util.getNumberFormat(self.x_max_DC-self.x_min_DC)
            self.y_label_format = util.getNumberFormat(self.y_max_DC-self.y_min_DC)
        
    
    def in_plotBox(self,x_DC,y_DC):
        """
        Return if a pair of x,y data coordinates lie inside the plotbox
        
        Used to determine if a point is drawn or not
        """
        
        in_x = self.x_min_DC <= x_DC <= self.x_max_DC
        in_y = self.y_min_DC <= y_DC <= self.y_max_DC
        
        return in_x and in_y
        
        
    def item_in_plotBox(self,item,x_IC,y_IC):
        """
        Determine if a pair of item coordinate are inside the plotBox
        
        Input
        ------
        item : QGraphicsItem
        x_IC, y_IC : single numbers
            Coordinates to test if they are in the plotBox
        
        Output
        ---------
        in_box : boolean
            True if item is inside plotBox
        
        """
        
                
        # Convert to data coordinate
        x_DC,y_DC = self.item2data(item,[x_IC],[y_IC])
        
        # Check against limits
        in_x = self.x_min_DC <= x_DC[0] <= self.x_max_DC
        in_y = self.y_min_DC <= y_DC[0] <= self.y_max_DC
        
        return in_x and in_y
        
        

    # Convenience functions that access the viewport
    @property
    def preferences(self):
        
        return self.viewport.preferences
    
        
        
    
        
        
        
#=============================================================================
#%% Marker lines
#=============================================================================

MARKER_ABSOLUTE = "ABSOLUTE"
MARKER_DELTA = "DELTA"


class HorizMarkerLine(QGraphicsObject):
    """
    Horizontal marker line that the user can move up or down with the mouse
    or keyboard.
    
    """
    
    def __init__(self,coordinateManager,name="H1",markerDict={}):
        
        super(HorizMarkerLine, self).__init__()
        
        # Marker name
        # --------------
        self.name = name
        
        # Selected flag
        # ----------------
        self.selected = False
        
        # Setup flags
        # ---------------
        #self.setFlags(QGraphicsItem.ItemIsFocusable|QGraphicsItem.ItemIsMovable|QGraphicsItem.ItemIsSelectable|QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIsMovable,True)
        self.setFlag(QGraphicsItem.ItemIsSelectable,True)
        
        # Type of mouse cursor to use
        self.setCursor(Qt.SizeVerCursor)
        
        # Link to coordinate manager
        self.coordinateManager = coordinateManager
        
        # Position
        # ----------------
        # Actual position on graph
        self.position_DC = np.mean([self.coordinateManager.y_max_DC,self.coordinateManager.y_min_DC])
        
        # The value that will be reported on the marker
        # can be absolute or a delta
        self.reported_position_DC = self.position_DC
        
        # Mode
        # ------------
        # TODO: This doesn't work for some reason, value doesn't get changed
        self.mode = MARKER_ABSOLUTE
        
        # Link to another marker for calculating the delta position
        self.deltaMarker = None
        
        # Link to dict of other markers held in parent
        self.markerDict = markerDict
        
        
        # bounding rect dimensions
        # --------------------------
        # Calculated in paint function
        self.total_width_IC = 0.0
        self.total_length_IC = 0.0
        self.boundingRect_SC = QRectF()
        
        # Label offset
        # ------------------
        # distance from end of line to label
        self.labelOffset_NC = 0.1
        
        
        # Colours and styles
        # ----------------------
        self.lineColour = '#81F781' # green
        self.lineColour_selected = '#99F799' # green
        
        self.lineTransparency = 255
        
        self.lineDashStyle = Qt.SolidLine
        
        # Text settings
        # ----------------
        self.font = QFont()
        self.font.setPixelSize(8)
        self.fmt = QFontMetrics(self.font)
        
        # Signal/slot connections
        # -----------------------
        self.connect(self,SIGNAL("setDeltaMode"),self.setDeltaMarkerMode)
        
        
        
        
    def boundingRect(self):
        """
        Return length of line plus or minus self.width
        
        """
       
        return self.boundingRect_SC
        
    
    def shape(self):
        """
        Return bounding rect converted to a path
        """
        
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path
        
        
    @property   
    def length_DC(self):
        """
        Get the length of the line.
        
        Dynamically link to coordinate manager
        """
      
        return np.array([self.coordinateManager.x_min_DC,self.coordinateManager.x_max_DC])
        
        
        
    def paint(self, painter, option, widget=None):
        
        painter.setClipping(False)
        
        # Convert data coordinates to item coordinates
        # ---------------------------------------------
        
        x_IC,y_IC = self.coordinateManager.data2item(self,
                                                     self.length_DC,
                                                     [self.position_DC,self.position_DC])
        
    
        
        # Draw lines
        # -------------------------------
        
        lineColour = QColor()
        if self.selected:
            lineColour.setNamedColor(self.lineColour_selected)
        else:
            lineColour.setNamedColor(self.lineColour)
        lineColour.setAlpha(self.lineTransparency)
        pen = QPen(lineColour)
        pen.setStyle(self.lineDashStyle)
        
        painter.setPen(pen)
        
        painter.drawLine(QPointF(x_IC[0],y_IC[0]), QPointF(x_IC[1],y_IC[1]) )
        
        # Draw marker text
        # ---------------------
        painter.setFont(self.font)
        
        # Convert label offset to item coordinates
        label_offset_IC = self.coordinateManager.normWidth2item(self,self.labelOffset_NC)
        
        # Make label
        label_text = self.labelText()
        
        # Adjust positions for the size of the labels
        labelRect = self.fmt.boundingRect(label_text)
        
        
        # Set y position 
        ypos_IC = y_IC[0] - 1.0*labelRect.height()
        
        
        # Draw labels either end of the line
        painter.drawText(QPointF(x_IC[0]+label_offset_IC-labelRect.width(),ypos_IC),label_text)
        painter.drawText(QPointF(x_IC[1]-label_offset_IC,ypos_IC),label_text)
        
        
        # Calculate bounding rect        
        self.boundingRect_SC = self.mapRectToScene( 
                                    QRectF( 
                                    QPointF(x_IC[0]-label_offset_IC-labelRect.width(),y_IC[0] - 2*labelRect.height()),
                                    QPointF(x_IC[1]+label_offset_IC+labelRect.width(),y_IC[0] + 2*labelRect.height())))
        
        
        # Draw bounding rect
        # -----------------------
        if DEBUG:
            # Draw bounding rect
            painter.save()
            painter.setPen(QColor(Qt.red))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.boundingRect())
            painter.restore
        
        
    
    def labelText(self):
        """
        Return text for the marker line:
            Name : Position
        
        """
        
        #  convert position to printable format
        position_text = util.formatNumber(self.reported_position_DC)
        
        if not self.deltaMarker:
            label_text = "%s: %s" % (self.name,position_text)
        else:
            label_text = "%s: \u0394 %s" % (self.name,position_text)
        
        return label_text
        
        
    def increment(self,step_size_DC=None):
        """
        Increment marker position by one unit
        
        Inputs
        ---------
        step_size_DC: float
            value for one step
        
        """
        
        # Set default step size
        if not step_size_DC:
            step_size_DC = self.coordinateManager.y_grid_minor_tick_spacing_DC
            
        # Move marker
        self.position_DC += step_size_DC
        self.update()
        
        
    
    def decrement(self,step_size_DC=None):
        """
        Decrement marker position by one unit
        
        Inputs
        ---------
        step_size_DC: float
            value for one step
        
        """
        
        # Set default step size
        if not step_size_DC:
            step_size_DC = self.coordinateManager.y_grid_minor_tick_spacing_DC
            
        # Move marker
        self.position_DC -= step_size_DC
        self.update()
    
    
    def keyPressEvent(self,event):
        """
        Enable the marker line to be moved with the up/down arrow keys
        
        """
        
        dbg(self,"Key press event entered",["brief","HorizMarkerLine"])
        
        
        
        changed = False
        increment_DC = self.coordinateManager.y_grid_minor_tick_spacing_DC
        
        modifier = event.modifier()
        
        if event.key() == Qt.Key_Up and modifier == Qt.AltModifier:
            self.position_DC += increment_DC
            changed = True
            
        elif event.key() == Qt.Key_Down and modifier == Qt.AltModifier:
            self.position_DC -= increment_DC
            changed = True
            
            
        if changed:
            self.update()
            
        else:
            QGraphicsItem.keyPressEvent(self,event)
          
          
            
    def mousePressEvent(self,event):
        """
        Handle the mouse being pressed for panning the graph
        
        """
        
        # Doesn't do much but is kept for debugging
        
        if event.button() == Qt.LeftButton:
            # self.setCursor(Qt.SizeVerCursor)
            #self.setCursor(Qt.SizeAllCursor)
            
            
            #logger.debug("Mouse Left button down")
            pass
            
            
        else:
            
            event.ignore()
            
      
    # TODO : These never get called because PlotBox always has the focus      
    def focusInEvent(self,event):
        #logger.debug("Marker got focus")
        self.selected = True
        
        
    def focusOutEvent(self,event):
        self.selected = False
            
           
           
           
    def mouseMoveEvent(self,event):
        """
        Mouse move or drag event. 
        
        Moves the line up or down
        
        """
        
        self.setFocus()
        
        
        # Get how much Mouse has moved in PlotBox
        # ----------------------------------------------
        # Log mouse positions
        buttonDownPos_IC = event.lastPos()
        mouseCurrentPos_IC = event.pos()
        
        
        # Get Position of mouse
        # -------------------------
        x_IC = np.array([buttonDownPos_IC.x(),mouseCurrentPos_IC.x()])
        y_IC = np.array([buttonDownPos_IC.y(),mouseCurrentPos_IC.y()])
        
              
        # Change marker position if still in the plotbox
        # --------------------------------------------------------
        x_DC,y_DC = self.coordinateManager.item2data(self,x_IC,y_IC)
        
        if self.coordinateManager.in_plotBox(x_DC[0],y_DC[0]):
        
            self.position_DC = y_DC[0]
            
            if self.deltaMarker: #self.mode == MARKER_DELTA:
                self.reported_position_DC = self.position_DC - self.deltaMarker.position_DC
                #logger.debug("%s:Delta Calc : rep. pos = %.3f" % (self.name,self.reported_position_DC))
            else:
                self.reported_position_DC = self.position_DC
                #logger.debug("%s:Absolute Calc : rep. pos = %.3f" % (self.name,self.reported_position_DC))
            
            self.prepareGeometryChange()
            self.update()
            
            
            
    def contextMenuEvent(self,event):
        """
        Context menu (right click) for Horiz marker
        
        """
        
        # Functions for menu actions
        # ...........................
        
        def deleteMe():
            # Function for deleting this marker
            self.coordinateManager.viewport.deleteHorizMarker(self.name)
            
            
        def setDeltaMarker(markerName):
            """
            Closure function to return a signalling function for each
            marker
            """
            
            def sendSignal():
                self.emit(SIGNAL("setDeltaMode"),markerName)
                
            return sendSignal
        
        
        # Get other markers if any
        # .........................
        otherMarkers = list(self.markerDict.keys())
        
        # remove this marker
        otherMarkers.pop(otherMarkers.index(self.name))
        
        # Make a list of functions to add to the menu actions
        markerFunctions = {}
        
        for marker in otherMarkers:
            markerFunctions[marker] = setDeltaMarker(marker)
        
        
        # Construct menu
        # .....................
        menu = QMenu(self.parentWidget())
        
        menu.addAction("Remove Marker",deleteMe)
        #menu.addAction("Add Vertical Marker",self.addVertMarkerSignal)
        
        menu.addSeparator()
        
        menu.addAction("Set to absolute mode",self.setAbsoluteMarkerMode)
        
        menu.addSeparator()
        
        # Add other markers
        if otherMarkers != []:
            for item in otherMarkers:
                menu.addAction("Delta : %s" % item,markerFunctions[item])
        
        menu.exec_(event.screenPos())
        
       
       
    def setAbsoluteMarkerMode(self):
        """
        Set marker line to absolute readout
        
        """
        
        self.deltaMarker = None
        self.mode == MARKER_ABSOLUTE
        #logger.debug("Marker: %s is set to absolute mode" % self.name)
        self.update()
        
        
        
    def setDeltaMarkerMode(self,markerName):
        """
        Set marker readout to be relative to given marker
        
        Input
        --------
        markerName : str
            name of marker to be relative to
            
        """
        
        self.deltaMarker = self.markerDict[markerName]
        self.mode == MARKER_DELTA
        #logger.debug("Marker: %s is delta to %s" % (self.name,markerName))
        self.update()
        
    
        
class VertMarkerLine(QGraphicsObject):
    """
    Vertical marker line that the user can move up or down with the mouse
    or keyboard.
    
    """
    
    def __init__(self,coordinateManager,name="V1",markerDict={}):
        
        super(VertMarkerLine, self).__init__()
        
        # Marker name
        # --------------
        self.name = name
        
        # Setup flags
        # ---------------
        #self.setFlags(QGraphicsItem.ItemIsFocusable|QGraphicsItem.ItemIsMovable|QGraphicsItem.ItemIsSelectable|QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIsMovable,True)
        self.setFlag(QGraphicsItem.ItemIsSelectable,True)
        
        # Type of mouse cursor to use
        self.setCursor(Qt.SizeHorCursor)
        
        # Link to coordinate manager
        self.coordinateManager = coordinateManager
        
        # Position
        # ----------------
        self.position_DC = np.mean([self.coordinateManager.x_max_DC,self.coordinateManager.x_min_DC])
        
        # The value that will be reported on the marker
        # can be absolute or a delta
        self.reported_position_DC = self.position_DC
        
        # Mode
        # ------------
        # TODO: This doesn't work for some reason, value doesn't get changed
        self.mode = MARKER_ABSOLUTE
        
        # Link to another marker for calculating the delta position
        self.deltaMarker = None
        
        # Link to dict of other markers held in parent
        self.markerDict = markerDict
        
        # bounding rect dimensions
        # --------------------------
        # Calculated in paint function
        self.total_width_IC = 0.0
        self.total_length_IC = 0.0
        self.boundingRect_SC = QRectF()
        
        # Label offset
        # ------------------
        # distance from end of line to label
        self.labelOffset_NC = 0.01
        
        
        # Colours and styles
        # ----------------------
        self.lineColour = '#FFFF00' # Yellow
        
        self.lineTransparency = 255
        
        self.lineDashStyle = Qt.SolidLine
        
        # Text settings
        # ----------------
        self.font = QFont()
        self.font.setPixelSize(8)
        self.fmt = QFontMetrics(self.font)
        
        # Debug flag
        # --------------
        self.DEBUG = False
        
        # Signal/slot connections
        # -----------------------
        self.connect(self,SIGNAL("setDeltaMode"),self.setDeltaMarkerMode)
        
        
        
        
    def boundingRect(self):
        """
        Return length of line plus or minus self.width
        
        """
       
        return self.boundingRect_SC
        
    
    def shape(self):
        """
        Return bounding rect converted to a path
        """
        
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path
        
        
    @property   
    def length_DC(self):
        """
        Get the length of the line.
        
        Dynamically link to coordinate manager
        """
      
        return np.array([self.coordinateManager.y_max_DC,self.coordinateManager.y_min_DC])
        
        
        
    def paint(self, painter, option, widget=None):
        
        painter.setClipping(False)
        
        # Convert data coordinates to item coordinates
        # ---------------------------------------------
        
        x_IC,y_IC = self.coordinateManager.data2item(self,
                                             [self.position_DC,self.position_DC],
                                             self.length_DC)
        
    
        
        # Draw lines
        # -------------------------------
        
        lineColour = QColor()
        lineColour.setNamedColor(self.lineColour)
        lineColour.setAlpha(self.lineTransparency)
        pen = QPen(lineColour)
        pen.setStyle(self.lineDashStyle)
        
        painter.setPen(pen)
        
        painter.drawLine(QPointF(x_IC[0],y_IC[0]), QPointF(x_IC[1],y_IC[1]) )
        
        # Draw marker text
        # ---------------------
        painter.setFont(self.font)
        
        # Convert label offset to item coordinates
        label_offset_IC = self.coordinateManager.normHeight2item(self,self.labelOffset_NC)
        
        # Make label
        label_text = self.labelText()
        
        # Adjust positions for the size of the labels
        # TODO : use QFontMetrics
        labelRect = self.fmt.boundingRect(label_text)
        
        
        # Set y position 
        xpos_IC = x_IC[0] - 0.5*labelRect.width()
        
        
        # Draw labels either end of the line
        painter.drawText(QPointF(xpos_IC,y_IC[0]-label_offset_IC),label_text)
        painter.drawText(QPointF(xpos_IC,y_IC[1]+label_offset_IC+0.75*labelRect.height()),label_text)
        
        
        # Calculate bounding rect        
        self.boundingRect_SC = self.mapRectToScene( 
                                    QRectF( 
                                    QPointF(x_IC[0] - 2*labelRect.width()/2,y_IC[0]-label_offset_IC-labelRect.height()),
                                    QPointF(x_IC[0] + 2*labelRect.width()/2,y_IC[1]+label_offset_IC+labelRect.height())
                                    ))
                                    
        
        
        # Draw bounding rect
        # -----------------------
        if self.DEBUG:
            # Draw bounding rect
            painter.save()
            painter.setPen(QColor(Qt.red))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(self.mapRectToItem(self,self.boundingRect()))
            painter.restore
            
            
        
        
    
    def labelText(self):
        """
        Return text for the marker line:
            Name : Position
        
        """
        
        #  convert position to printable format
        position_text = util.formatNumber(self.reported_position_DC)
        
        if not self.deltaMarker:
            label_text = "%s: %s" % (self.name,position_text)
        else:
            label_text = "%s: \u0394 %s" % (self.name,position_text)
        
        return label_text
        
    
    
    def increment(self,step_size_DC=None):
        """
        Increment marker position by one unit
        
        Inputs
        ---------
        step_size_DC: float
            value for one step
        
        """
        
        # Set default step size
        if not step_size_DC:
            step_size_DC = self.coordinateManager.x_grid_minor_tick_spacing_DC
            
        # Move marker
        self.position_DC += step_size_DC
        self.update()
        
        
    
    def decrement(self,step_size_DC=None):
        """
        Decrement marker position by one unit
        
        Inputs
        ---------
        step_size_DC: float
            value for one step
        
        """
        
        # Set default step size
        if not step_size_DC:
            step_size_DC = self.coordinateManager.x_grid_minor_tick_spacing_DC
            
        # Move marker
        self.position_DC -= step_size_DC
        self.update()
    
    
    
    
    def keyPressEvent(self,event):
        """
        Enable the marker line to be moved with the up/down arrow keys
        
        """
        
        dbg(self,"Key press event entered",["brief","HorizMarkerLine"])
        
        
        
        changed = False
        increment_DC = self.coordinateManager.y_grid_minor_tick_spacing_DC
        
        if event.key() == Qt.Key_Right:
            self.position_DC += increment_DC
            changed = True
            
        elif event.key() == Qt.Key_Left:
            self.position_DC -= increment_DC
            changed = True
            
            
        if changed:
            self.update()
            
        else:
            QGraphicsItem.keyPressEvent(self,event)
          
          
            
    def mousePressEvent(self,event):
        """
        Handle the mouse being pressed for panning the graph
        
        """
        
        # Doesn't do much but is kept for debugging
        
        if event.button() == Qt.LeftButton:
            # self.setCursor(Qt.SizeVerCursor)
            #self.setCursor(Qt.SizeAllCursor)
            
            
            dbg(self,"Mouse Left button down",["brief","HorizMarkerLine"],disable=True)
                
        else:
            event.ignore()
            
           
           
           
    def mouseMoveEvent(self,event):
        """
        Mouse move or drag event. 
        
        Moves the line up or down
        
        """
        
        
        
        # Get how much Mouse has moved in PlotBox
        # ----------------------------------------------
        # Log mouse positions
        buttonDownPos_IC = event.lastPos()
        mouseCurrentPos_IC = event.pos()
        
        
        # Get Position of mouse
        # -------------------------
        x_IC = np.array([buttonDownPos_IC.x(),mouseCurrentPos_IC.x()])
        y_IC = np.array([buttonDownPos_IC.y(),mouseCurrentPos_IC.y()])
        
              
        # Change marker position if still in the plotbox
        # --------------------------------------------------------
        x_DC,y_DC = self.coordinateManager.item2data(self,x_IC,y_IC)
        
        if self.coordinateManager.in_plotBox(x_DC[0],y_DC[0]):
        
            self.position_DC = x_DC[0]
            
            if self.deltaMarker: #self.mode == MARKER_DELTA:
                self.reported_position_DC = self.position_DC - self.deltaMarker.position_DC
                #logger.debug("%s:Delta Calc : rep. pos = %.3f" % (self.name,self.reported_position_DC))
            else:
                self.reported_position_DC = self.position_DC
                #logger.debug("%s:Absolute Calc : rep. pos = %.3f" % (self.name,self.reported_position_DC))
            
            
            self.prepareGeometryChange()
            self.update()               
                
    
    
    def contextMenuEvent(self,event):
        """
        Context menu (right click) for Horiz marker
        
        """
        
        # Functions for menu actions
        # ...........................
        
        def deleteMe():
            # Function for deleting this marker
            self.coordinateManager.viewport.deleteHorizMarker(self.name)
            
            
        def setDeltaMarker(markerName):
            """
            Closure function to return a signalling function for each
            marker
            """
            
            def sendSignal():
                self.emit(SIGNAL("setDeltaMode"),markerName)
                
            return sendSignal
        
        
        # Get other markers if any
        # .........................
        otherMarkers = list(self.markerDict.keys())
        
        # remove this marker
        otherMarkers.pop(otherMarkers.index(self.name))
        
        # Make a list of functions to add to the menu actions
        markerFunctions = {}
        
        for marker in otherMarkers:
            markerFunctions[marker] = setDeltaMarker(marker)
        
        
        # Construct menu
        # .....................
        menu = QMenu(self.parentWidget())
        
        menu.addAction("Remove Marker",deleteMe)
        #menu.addAction("Add Vertical Marker",self.addVertMarkerSignal)
        
        menu.addSeparator()
        
        menu.addAction("Set to absolute mode",self.setAbsoluteMarkerMode)
        
        menu.addSeparator()
        
        # Add other markers
        if otherMarkers != []:
            for item in otherMarkers:
                menu.addAction("Delta : %s" % item,markerFunctions[item])
        
        menu.exec_(event.screenPos())
        
       
       
    def setAbsoluteMarkerMode(self):
        """
        Set marker line to absolute readout
        
        """
        
        self.deltaMarker = None
        self.mode == MARKER_ABSOLUTE
        logger.debug("Marker: %s is set to absolute mode" % self.name)
        self.update()
        
        
        
    def setDeltaMarkerMode(self,markerName):
        """
        Set marker readout to be relative to given marker
        
        Input
        --------
        markerName : str
            name of marker to be relative to
            
        """
        
        self.deltaMarker = self.markerDict[markerName]
        self.mode == MARKER_DELTA
        logger.debug("Marker: %s is delta to %s" % (self.name,markerName))
        self.update()
            
            



#=============================================================================
#%% Plotting utilities
#=============================================================================

class AxisManager:
    """
    Base class for handling an axis. The AxisManager class is responsible for:
        * Tick mark locations
        * Tick mark labels
        * min and max values
        * Providing a data transform function for the actual data (e.g. log scale)
        * Rescaling
        * Transformation to screen plotting coordinates from data coordinates
        
        
    """
    
    def __init__(self):
        """
        Constructor - defines the internal variables
        """
        
        # Name to be used in any selection menu
        self.name = 'linear 1:1'
        
        
        # Axis min and max
        # -------------------------------------------------
        # The axis has several different versions of the min and max limits:
        # 1. The actual data values
        # 2. The transformed data values
        # 3. The screen coordinate limits
        
        
        # Axis limits in data coordinates
        self.data_min_DC = -2.0
        self.data_max_DC = 2.0
        
        # Plot min and max
        # - The displayed limits of the axis, this gets changed when the plot
        #   is panned or zoomed
        self.plot_min_DC = -1.0
        self.plot_max_DC = 1.0
        
        # Transformed data min and max
        self.transform_min = -1.0
        self.transform_max = 1.0
        
        
        # Screen coordinate min and max
        self.screen_min_SC = 0
        self.screen_max_SC = 100
        

        # Ticks 
        # -----------------------------------------------
        # These define the positions and labels of the ticks        
        
        # Major tick spacing in data coordinates
        self.major_ticks_DC = [-1,-0.5,0,0.5,1]
        
        # Major tick spacing in screen coordinates        
        self.major_ticks_SC = [-1,-0.5,0,0.5,1]
        
        # Major tick labels
        # - List of strings
        self.major_tick_labels =[]
        
        
        
        # Minor tick spacing in data coordinates
        self.minor_ticks_DC = [-0.75,-0.25,0.25,0.75]
        
        # Minor tick spacing in screen coordinates
        self.minor_ticks_SC = [-0.75,-0.25,0.25,0.75]
        
        # Minor tick labels
        # - List of strings
        self.minor_tick_labels =[]
        
        self.tick_label_format = '%g'
        
        
        
        # Coordinate transform
        # -------------------------------
        # These get set by the update() function when axis limits are changed
        self._offset = 0
        self._slope = 0
        
        
        
    def __str__(self):
        """
        Printout the axis properties for debugging
        """
        
        array2str = lambda x: ','.join([str(n) for n in x])
        
        printout = [
            'Axis Properties',
            '====================',
            ' ',
            'Min/Max scales',
            '----------------------',
            'Data min %g' % self.data_min_DC,
            'Data max %g' % self.data_max_DC,
            'Screen min %i' % self.screen_min_SC,
            'Screen max %i' % self.screen_max_SC,
            ' ',
            'Tick spacing in data coordinates:',
            '------------------------------------',
            'Major tick spacing %g' % self.major_tick_spacing_DC,
            'Minor tick spacing %g' % self.minor_tick_spacing_DC,
            ' ',
            'Tick values in data coordinates:',
            '------------------------------------',
            'Major ticks  \n\t[%s]' % array2str(self.major_ticks_DC),
            'Minor ticks  \n\t[%s]' % array2str(self.minor_ticks_DC),
            ' ',
            'Tick values in screen coordinates:',
            '------------------------------------',
            'Major ticks  \n\t[%s]' % array2str(self.major_ticks_SC),
            'Minor ticks  \n\t[%s]' % array2str(self.minor_ticks_SC),
            ' ',
            'Tick labels',
            '---------------------',
            'Major tick labels \n\t[%s]' % ','.join(self.major_tick_labels),
            'Minor tick labels \n\t[%s]' % ','.join(self.minor_tick_labels)]
        

        return '\n'.join(printout)
        
        
    def __repr__(self):
        return self.__str__()
        
        
        
    def to_screen(self,data_DC):
        """
        Convert data values to final screen coordinates, performing any special
        transforms in the process.
        
        
        Inputs
        ------
        data_DC : numpy array or similar
            raw data values
            
        Outputs
        --------
        screen_SC : numpy array
            screen coordinates
            
        """
        
        # Transform data
        # -------------------
        
        
        
        # Convert to screen coordinates
        # --------------------------------
        return self.transform2screen(self.transform(data_DC))
    
    
    
    def transform(self,data_DC):
        """
        Perform the transform specific to this Axis manager
        
        Inputs
        ------
        data_DC : numpy array or similar
            raw data values
            
        Outputs
        --------
        data_TC : numpy array
            transformed data
            
        """
        
        # In this case the transform is a straight 1:1
        # - for more exotic transforms put the code here
        return data_DC
        
        
        
        
    def transform2screen(self,data_TC):
        """
        Convert transformed coordinates to final screen coordinates
        
        Conversion is done according to the following diagram. Above the 
        horizontal line are input data coordinates (transformed). Below the
        line are the final screen coordinate scale. Pd is a single data point
        and Ps is its equivalent value in screen coordinates
        

        Data Coordinates


        Dmin                                            Dmax
                                Pd
        ^                                               ^
        |         dPd           +                       |
        |+--------------------->|                       |
        |                       |                       |
        |+----------------------|-----------------------|
        |                       |                       |
        |                       v                       |
        |                                               |
        +                       Ps                      +
                                                       Smax
        Smin


       Screen Coordinates
       
       dPd is the offset from the data minimum to the point at Pd
       dPd = Pd - Dmin
       
       We want to calculate the equivalent distance in screen coordinates from
       Smin:
       
                          (Smin-Smax)
       Ps = Smin + dPd x  -----------
                          (Dmin-Dmax)
                          
       
                        (Smin-Smax)          (Smin-Smax)
       Ps = Smin - Dmin ------------   + Pd ------------
                        (Dmin-Dmax)         (Dmin-Dmax)


        This can be reduced to:
            Ps = offset + Pd x slope

        Only the term in Pd needs to be calculated on the fly, all the other
        terms are calculated in the update() method when the limits change.               
       
        
        Inputs
        ----------
        data_TC : numpy array
            transformed data
            
        Output
        ----------
        data_SC : numpy array
            final screen coordinates
            
        """
        
        # Use pre-calculated constants
        data_SC = self._offset + data_TC*self._slope
        
        return data_SC
        
        
        
    def update_scaling(self):
        """
        Update internal scaling constants when screen or data limits have changed
        
        Inputs
        --------
        TODO Pass them in or rely on the class variables being updated?
        
        Outputs
        -------
        None
        
        Class variables updated
        ----------------------------
        self._offset, self._slope
        
        All the tick mark variables
        
        """
        
        
        # Update slope and offset for coordinate transformations
        # ---------------------------------------------------------
        # Transform data coordinate min and max according to transform()
        # Calculate slope and offset from transformed coordinates
        
        
        Dmin = self.transform(self.data_min_DC)
        Dmax = self.transform(self.data_max_DC)

        # Slope
        # - see transform2screen for formula        
        self._slope = (self.screen_min_SC-self.screen_max_SC)/(Dmin-Dmax)
        
        # Offset         
        self._offset = self.screen_min_SC - Dmin*self._slope
        
        
        
    def update_axis(self,new_min_DC=None,new_max_DC=None):
        """
        Update x axis scale and grid lines for new min and max.
        
        Uses the NiceScale class to give readable axis ticks
        
        Inputs:
        -------------
        new_x_min_DC,new_x_max_DC: float
            new axis limits, if None then the limits in self.plot_min_DC and
            self.plot_max_DC are used
            
        """
        
        # Check for inputs
        if not new_min_DC:
            new_min_DC = self.plot_min_DC
            
        if not new_max_DC:
            new_max_DC = self.plot_max_DC
  

        # Update ticks in data coordinates
        # =====================================================        
        
        # Find "nice" range
        newScale = NiceScale(new_min_DC,new_max_DC)
        
        
        # Set new min and max to requested values
        self.plot_min_DC = new_min_DC
        self.plot_max_DC = new_max_DC
        
        # Use nice scale to define ticks
        self.major_tick_spacing_DC = newScale.tickSpacing
        self.major_ticks_DC = np.arange(newScale.niceMin,newScale.niceMax,newScale.tickSpacing)
        
        self.minor_tick_spacing_DC = newScale.minorTickSpacing
        self.minor_ticks_DC = np.arange(newScale.niceMin,newScale.niceMax,newScale.minorTickSpacing)
        
        
        # Update tick labels
        # =====================================================
        
        self.update_label_format()
        
        # Make tick labels
        self.major_tick_labels = [self.tick_label_format % tick for tick in self.major_ticks_DC]
        self.minor_tick_labels = [self.tick_label_format % tick for tick in self.minor_ticks_DC]
        
        
        # Update ticks in screen coordinates
        # =====================================================
        self.major_ticks_SC = self.to_screen(self.major_ticks_DC)
        self.minor_ticks_SC = self.to_screen(self.minor_ticks_DC)
        
        
        
        
    def update_label_format(self):
        """
        Adapt label format to magnitude of data
        
        Sets the tick_label_format to a format string appropriate to the data
        
        """
        
        self.tick_label_format = util.getNumberFormat(self.plot_max_DC-self.plot_min_DC)
        
        
        
        
    def update(self):
        """
        Central update function. Calls all the other updates
        
        * Updates the scaling of the axis
        * Updates the tick spacing and labels
        
        """
        
        self.update_scaling()
        
        self.update_axis()
        
        self.update_label_format()

        
        
        
        
        
        
        



class NiceScale:
    """ Taken from StackOverflow and converted to use numpy
    Calculates a nice scale given min and max data values
    also gives the tick spacing
    
    Ref:
    http://stackoverflow.com/questions/8506881/nice-label-algorithm-for-charts-with-minimum-ticks/16363437#16363437
    """
    
    def __init__(self, minv,maxv):
        self.maxTicks = 10
        self.tickSpacing = 0
        self.minorTickSpacing = 0
        self.lst = 10
        self.niceMin = 0
        self.niceMax = 0
        self.minPoint = minv
        self.maxPoint = maxv
        self.calculate()
        
        
    
    def calculate(self):
        
        # Calculate nice range
        # TODO : setting round to True may give tighter results???
        niceRange = self.niceNum(self.maxPoint - self.minPoint, False)
        
        # Calculate number of ticks in nice range
        self.tickSpacing = self.niceNum(niceRange / (self.maxTicks - 1), True)
        
        # Calculate min and max
        # floor the min/ceiling the max
        self.niceMin = np.floor(self.minPoint / self.tickSpacing) * self.tickSpacing
        self.niceMax = np.ceil(self.maxPoint / self.tickSpacing) * self.tickSpacing
        
        # Calculate minor tick spacing
        # = tick spacing divided into a 'nice' number of sections
        self.minorTickSpacing = self.niceNum(self.tickSpacing/ (self.maxTicks - 1), False)
    
    
    
    def niceNum(self, x, rround):
        """
        Find a "nice" number that is approximately equal to lst.
        
        Either round up or down
        
        Inputs
        ----------
        x : float
            the raw number that we want to return a "nice" equivalent of
            
        rround: bool
            True - round the number
            False - ceiling the number
        
        
        
        """
        
        
        
        exponent = 0 # exponent of range */
        fraction = 0 # fractional part of range */
        niceFraction = 0 # nice, rounded fraction */
    
        exponent = np.floor(np.log10(np.abs(x)))
        fraction = x / np.power(10, exponent) # Between 1-10
    
        if rround: 
            if (fraction < 1.5):
                niceFraction = 1
            elif (fraction < 3):
                niceFraction = 2
            elif (fraction < 7):
                niceFraction = 5;
            else:
                niceFraction = 10;
        else :
            if (fraction <= 1):
                niceFraction = 1
            elif (fraction <= 2):
                niceFraction = 2
            elif (fraction <= 5):
                niceFraction = 5
            else:
                niceFraction = 10
    
        return niceFraction * np.power(10, exponent)
        
    
    def setMinMaxPoints(self, minPoint, maxPoint):
          self.minPoint = minPoint
          self.maxPoint = maxPoint
          self.calculate()
          
    
    def setMaxTicks(self, maxTicks):
        self.maxTicks = maxTicks;
        self.calculate()   
        
    def __str__(self):
        
        disp = ["min = %f" % self.minPoint,
                "max = %f" % self.maxPoint,
                "nice min = %f" % self.niceMin,
                "nice max = %f" % self.niceMax,
                "tick spacing = %f" % self.tickSpacing,
                "minor tick spacing = %f" % self.minorTickSpacing]
                
        return "\n".join(disp)
        
        
    def __repr__(self):
        
        return self.__str__()

#%%

def array2polygon(x,y):
    """
    Convert an array or list of coordinates to a QPolygonF
    
    Inputs
    ---------
    x,y = coordinates
    
    Outputs
    -----------
    poly = QPolygonF
    """
    #nPoints = len(x)
    #assert nPoints==len(y),"array2polygon : x and y are different lengths"
    
    #point_list = [QPointF(x[iP],y[iP]) for iP in range(nPoints)]
    
    point_list = [QPointF(xv,yv) for xv,yv in zip(x.tolist(),y.tolist())]
        
    return QPolygonF(point_list)
    
#%% Colours

    
    


#=============================================================================
# Main window
#=============================================================================


class MainForm(QDialog):
    """ Class for testing graph widgets
    """

    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)


        
        self.view = GraphWidget([])
        

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        
        self.setLayout(layout)

        #self.draw()
        self.setWindowTitle("Graphics scene demo")
        
        # Add graphs to GraphWidget
        # --------------------------------------------
        
        # Draw a curve
#        x_DC = np.arange(-8,9,1)
#        y_DC = np.arange(-8,9,1)
#        
#        series1 = GraphSeries(x_DC,y_DC,"test series",self.coordinateManager,
#                              markerSize=10,markerShape='^',
#                              markerTransparency = 255,
#                              lineTransparency = 0)
#        self.view.addSeries(series1)
#        
#        x2_DC = np.linspace(-100,100,10000)
#        y2_DC = np.sin(x2_DC)
#        
#        series2 = GraphSeries(x2_DC,y2_DC,"test series 2",self.coordinateManager,
#                              markerSize=10,markerShape='+',
#                              markerTransparency = 255,
#                              lineTransparency = 255,
#                              drawMarkers=False)
#        self.view.addSeries(series2)
        
        
        # Channel series test
        # ----------------------------
        dtype = [("time",float),("amplitude",float)]
        npoints = 1000
        
        # Channel 1
        recarray = np.zeros(npoints,dtype)
        recarray["time"] = np.linspace(-100,100,npoints)
        recarray["amplitude"] = np.cos(recarray["time"])+3
        
        linestyle1 = ch.plotLineStyle(lineColour='#6C71C4',marker='^',markerColour='#d33682')
        channel1 = ch.ScopePyChannel("channel test",linestyle1)
        channel1.addData2Channel(recarray)
        
        # Chunk 2
        recarray = np.zeros(npoints,dtype)
        recarray["time"] = np.linspace(-100,100,npoints)
        recarray["amplitude"] = 0.8*np.cos(recarray["time"])-3
        
        linestyle2 = ch.plotLineStyle(lineColour='#0071C4',marker='+',markerColour='#d33600')
        channel2 = ch.ScopePyChannel("channel2 test",linestyle2)
        channel2.addData2Channel(recarray)
        
        
        
        self.view.addChannel(channel1)
        self.view.addChannel(channel2)
        
        # Set axis limits
        self.view.xmin = 0
        self.view.xmax = 10
        self.view.ymin = -5
        self.view.ymax = 5
        
        # Add a horizontal marker line
        self.view.addHorizMarker()
        
        
        

#=============================================================================
#%% Colour defaults
#=============================================================================      
        
COLOURS = col_shapes.default_palette() #[Qt.blue,Qt.red,Qt.green,Qt.cyan,Qt.magenta,Qt.yellow,Qt.white,Qt.gray]
MARKERS = list(col_shapes.make_markers().keys())       
        

#=============================================================================
#%% Code runner
#=============================================================================


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = MainForm()
    rect = QApplication.desktop().availableGeometry()
    print("Screen rect",rect)
    form.resize(int(rect.width() * 0.5), int(rect.height() * 0.6))
    #form.resize(800, 600)
    form.show()
    app.exec_()
