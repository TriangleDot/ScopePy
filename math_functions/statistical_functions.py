# -*- coding: utf-8 -*-
"""
Created on Sat Jul  4 07:12:29 2015

@author: john

ScopePy Statistics Math function library
===============================================

Requires scipy


Version
==============================================================================
$Revision:: 46                            $
$Date:: 2015-06-08 08:02:00 -0400 (Mon, 0#$
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


#======================================================================
#%% Imports
#======================================================================

# Standard library


# Third party
import numpy as np
from scipy.stats import probplot



# ScopePy
from ScopePy_channel import MathFunction





#======================================================================
#%% Constants
#======================================================================


#======================================================================
#%% Initialise list of functions
#======================================================================
# This list will be exported from this module

mathFunctions = []

#==============================================================================
#%% Statistical Math function definitions
#==============================================================================

# ---------------------------------------------------------------------------
# Example functions
# ---------------------------------------------------------------------------
ex = MathFunction()
ex.name = 'exampleFuncInStats'
ex.description = 'y =  2*y'
ex.function = lambda chan : (chan.x,2*chan.y)

mathFunctions.append(ex)


# ---------------------------------------------------------------------------
# LogNormal function
# ---------------------------------------------------------------------------
def lognormal(values):
    (osm,osr),dummy = probplot(values,plot=None)
    
    return (osm,osr)


ex = MathFunction()
ex.name = 'lognormal'
ex.description = 'x =  std deviations, y = values'
ex.function = lambda chan : lognormal(chan.y)

mathFunctions.append(ex)




