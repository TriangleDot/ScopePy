# -*- coding: utf-8 -*-
"""
Created on Sat Jul  4 07:12:29 2015

@author: john

ScopePy Default Channel Math function library
===============================================

Definitions for default Channel Math functions


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
#%% Simple Math function definitions
#==============================================================================

# ---------------------------------------------------------------------------
# Example functions
# ---------------------------------------------------------------------------
ex = MathFunction()
ex.name = 'exampleFunc'
ex.description = 'y =  2*y'
ex.function = lambda chan : (chan.x,2*chan.y)

mathFunctions.append(ex)


# ---------------------------------------------------------------------------
# dB conversion functions
# ---------------------------------------------------------------------------
dB10 = MathFunction()
dB10.name = 'dB10'
dB10.description = 'y =  10*log10(y)'
dB10.function = lambda chan : (chan.x,10*np.log10(chan.y))

mathFunctions.append(dB10)

# ++++++++++++++++++++++++++++++++++++++++++++++++++++

dB20 = MathFunction()
dB20.name = 'dB20'
dB20.description = 'y =  20*log10(y)'
dB20.function = lambda chan : (chan.x,20*np.log10(chan.y))

mathFunctions.append(dB20)

# ++++++++++++++++++++++++++++++++++++++++++++++++++++

flip = MathFunction()
flip.name = 'flip x & y'
flip.description = 'y = x x = y'
flip.function = lambda chan : (chan.y,chan.x)

mathFunctions.append(flip)
# ++++++++++++++++++++++++++++++++++++++++++++++++++++
# Example of a function with two input channels
diff = MathFunction()
diff.name = 'diff'
diff.description = 'y =  channel2 - channel1'
diff.function = lambda channel1,channel2 : (channel1.x,channel2.y-channel1.y)

mathFunctions.append(diff)







#==============================================================================
#%% More complicated functions
#==============================================================================

# TODO: This causes a "can't set attribute error"

#class runningAverage(MathFunction):
#    """
#    Running average with editable averaging window
#    
#    """
#    
#    def __init__(self):
#        
#        # Initialise base class
#        super(runningAverage,self).__init__()
#        
#        # Make a parameter : averaging window
#        self.parameter['Averaging window'] = 5
#        
#        # Make the running average function
#        
#            
#    
#    @property
#    def function(self):
#        
#        return self._function()
#        
#        
#        
#    def _function(self):
#        
#        # (lifted from StackOverflow)
#        def running_mean(x, N):
#            cumsum = np.cumsum(np.insert(x, 0, 0)) 
#            return (cumsum[N:] - cumsum[:-N]) / N 
#            
#        Navg = self.parameter['Averaging window']
#        
#        return lambda x,y : (x,running_mean(y,Navg))
#
#
#mathFunctions.append(runningAverage())