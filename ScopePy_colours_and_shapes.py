# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 16:43:18 2015

@author: john


ScopePy colours and shapes library
=========================================
Separate library for colours and shapes and other graphical settings


Version
==============================================================================
$Revision:: 116                           $
$Date:: 2015-11-16 07:36:25 -0500 (Mon, 1#$
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


#======================================================================
#%% Imports
#======================================================================

# Standard library

# Third party libraries
from qt_imports import *



#==============================================================================
#%% Constants
#==============================================================================



#==============================================================================
#%% Markers
#==============================================================================

def make_markers(shape_code=None):
    """Create dictionary of markers

    """

    markers = {}

    # dot
    # ------------------------------------------------------
    dot = QPolygonF([QPointF(0.0,0.0),
                         QPointF(0.0,0.0)])

    path = QPainterPath()
    #path.addRect(-0.5,0.5,1,1)
    path.addPolygon(dot)
    path.closeSubpath()
    #path.moveTo(0,0)


    markers['.'] = path

    # Square
    # ------------------------------------------------------
    rectangle = QPolygonF([QPointF(0.5,0.5),
                         QPointF(0.5,-0.5),
                         QPointF(-0.5,-0.5),
                         QPointF(-0.5,0.5)])

    path = QPainterPath()
    #path.addRect(-0.5,0.5,1,1)
    path.addPolygon(rectangle)
    path.closeSubpath()
    path.moveTo(0,0)


    markers['s'] = path

    # Circle  TODO : Doesn't plot in correct position
    # ------------------------------------------------------
    path = QPainterPath()
    path.addEllipse(-0.5,-0.5,1,1)
    #path.moveTo(-0.5,0.5)

    markers['o'] = path

    # Triangle pointing up
    # ------------------------------------------------------
    triangle = QPolygonF([QPointF(0.5,0.5),
                         QPointF(0.0,-0.5),
                         QPointF(-0.5,0.5)])
    path = QPainterPath()
    path.addPolygon(triangle)
    path.closeSubpath()
    path.moveTo(0,0)

    markers['^'] = path

    # Cross
    # ------------------------------------------------------
    horiz = QPolygonF([QPointF(-0.5,0.0),QPointF(0.5,0.0)])
    vert = QPolygonF([QPointF(0,-0.5),QPointF(0,0.5)])

    path = QPainterPath()
    path.addPolygon(horiz)
    path.addPolygon(vert)

    markers['+'] = path


    # ------------------------------------------------------
    # Return dictionary of markers
    # or individual marker if requested

    if not shape_code:
        return markers

    elif shape_code in markers:
        return markers[shape_code]

    else:
        # Default marker
        return markers["o"]



#==============================================================================
#%% Colours
#==============================================================================
def default_palette():
    """
    Return the default colour palette as a list of RGB numbers

    Output
    -----------
    colour_list : list
        Each item is an HTML style RGB string eg '#aa00ff'

    """

    # Use Hue/Saturation/Value (HSV) model to generate the colours
    # and then convert to RGB

    Hues = [0,120,240]
    Saturation = 255
    Value = 255

    # Make a cyclical palette that is essentially red/green/blue repeated
    # but offsetting the hue by a constant amount each time


    colour_list = []

    for offset in range(0,120,20):
        for hue in Hues:
            colour_list.append( QColor.fromHsv(hue+offset,Saturation,Value).name() )


    return colour_list


def rgb_str2num(rgb_str):
    """
    Convert RGB string to RGB number using QT functions

    Input
    ------
    rgb_str : str
        RGB string e.g. '#55ff00'

    Output
    -------
    rgb_int : int
        integer version of RGB string e.g.

    Example
    ---------
    >>> rgb_str2num('#55ff00')
    4283825920

    """

    # Make a QColor object and use it to do the conversion
    c = QColor()
    c.setNamedColor(rgb_str)

    return c.rgb()




#==============================================================================
#%% Defaults
#==============================================================================
COLOURS = default_palette()
