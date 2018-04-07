# -*- coding: utf-8 -*-
"""
Created on Sat Dec 20 07:39:41 2014

@author: john

ScopePy testing

"""

#==============================================================================
#%% Setup paths
#==============================================================================

 # Adding to the system path
import sys
sys.path.append('/home/john/Documents/Python/scopePy')
sys.path.append('/home/john/Documents/Python/scopePy/unittest')

#==============================================================================
#%% Imports
#==============================================================================

# Standard library
import os
import imp

# Third party libraries
import numpy as np

from qt_imports import *

# My libraries
import ScopePy_channel as ch
import ScopePy_graphs as graphs
import ScopePy_widgets as wid


#==============================================================================
#%% Constants
#==============================================================================




#=============================================================================
# Main window
#=============================================================================


class MainForm(QDialog):
    """ Class for testing graph widgets
    """

    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)


        self.dock = wid.FlexiDock(fillDirection = 'fill across')

        # Add graphs to the dock
        self.view1 = graphs.GraphWidget()
        self.dock.addDock(self.view1)

        self.view2 = graphs.GraphWidget()
        self.dock.addDock(self.view2)

        self.view3 = graphs.GraphWidget()
        self.dock.addDock(self.view3)

        layout = QVBoxLayout()
        layout.addWidget(self.dock)

        self.setLayout(layout)

        #self.draw()
        self.setWindowTitle("Graphics scene in dock demo")

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
        npoints = 100

        # Chunk 1
        recarray = np.zeros(npoints,dtype)
        recarray["time"] = np.linspace(-100,100,npoints)
        recarray["amplitude"] = np.cos(recarray["time"])+3

        linestyle = ch.plotLineStyle(marker='.')
        channel = ch.ScopePyChannel("channel test",linestyle)
        channel.addData2Channel(recarray)

        # Chunk 2
        recarray = np.zeros(npoints,dtype)
        recarray["time"] = np.linspace(-100,100,npoints)
        recarray["amplitude"] = np.cos(recarray["time"])-3
        channel.addData2Channel(recarray)



        self.view1.addChannel(channel)
        self.view2.addChannel(channel)
        self.view3.addChannel(channel)








#=============================================================================
#%% Code runner
#=============================================================================


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = MainForm()
    rect = QApplication.desktop().availableGeometry()
    print("Screen rect",rect)
    #form.resize(int(rect.width() * 0.25), int(rect.height() * 0.4))
    #form.resize(800, 600)
    form.show()
    app.exec_()
