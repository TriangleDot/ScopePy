===========
ScopePy
===========

What is ScopePy
================

ScopePy is basically a Python graph plotting program with an interface inspired by digital oscilloscopes. It also provides a modular GUI framework that can be customised.

What can ScopePy do?
=====================


- Plot 2D graphs on a multiple tabs
- Takes data from multiple formats e.g. HDF5, CSV, Excel, Open Office, SQL(?)
- Accepts data from a TCIP connection
- Built-in Python console and text editor
- Stores sessions that can include links to data sources, plots, open tabs and more
- Modular architecture allows customisation using simplified GUI interface


How to run ScopePy
===================

Download the contents here into a directory and execute the following

::
    python ScopePy_GUI.py
    

Dependencies
===============

ScopePy is written in Python 3 only using the QT graphics library. It is dependent on the following third party libraries:

- numpy
- pyqt (Version 4)
- qt (Version 4)
- h5py (Optional)
- pandas (Optional)
- openpyxl (Optional)

Note: Currently only QT4 is supported


For Anaconda users
-------------------

For those using the Anaconda python distribution the file "anaconda_environment.yml" gives an example environment which can be used to run ScopePy.


Help
=======

ScopePy has its own internal help system which can be accessed from the "Help" menu when the program is run


State of development
======================

ScopePy should be considered a work in progress. It is designed as an extendable program that allows extra features to be added by means of "Panels".



ScopePy concepts
==================


Channels: 
----------

Like a digital oscilloscope ScopePy has the concept of channels. A channel is a set of (x,y) data. A channel can be plotted in any standard 2D graph. Multiple channels can be added to any graph. Channels are defined globally so that any changes in the style will be reflected in all graphs where the channel appears. Channels can also be added to. This is known as 'chunks'. A channel can have multiple chunks and if the standard plot is used to display the channel then the chunks can be individually view.



Data sources :
---------------

Data sources are exactly what they say. They provide the data which can be used to create channels so that they can be plotted. Data sources can be files, e.g. HDF5, CSV, Excel etc files, or internally generated data (from the internal Python console).



Panels :
---------

ScopePy has a modular architecture. All the functionality is built into different panels. The panels can either appear in the sidebar on the left side as different tabs or in the main area as windows. The main area features a tabbed interface so that panels can be grouped onto different pages or tabs. There are a number of panels that ship with ScopePy. Panels can also be created by users who want to customised their use of ScopePy. See ScopePy development guide (link??). The built-in panels are listed below:


Built-in Sidebar panels:
-------------------------

- Channel selector : This panel allows channels to be added to plot panels. It also has a 'channel crafter' for making new channels
- Data Source Selector : All data sources that are currently being accessed appear in this panel. From here their contents can be viewed and data can be selected and made into channels for plotting.
- Docs Browser : ScopePy's help system. Panels can display help in this panel.
- Log : ScopePy keeps detailed logs of its actions, mainly for debugging. This panel displays a list of the logs.


Built-in Main area panels
----------------------------


- Standard Plot : The basic 2D plot in ScopePy. Any plot that is currently active can have channels added to it using the 'Channel selector'. The standard plot features autoscaling, editable axis limits, panning with mouse or the arrow keys, copying to the clipboard.
- Python console : ScopePy has a built-in Python console and text editor. This allows scripts to be written to generate data such as Numpy arrays or Pandas DataFrames which can also be plotted as channels.
- Table editor : This panel can display 2D data as rows and columns. It allows channels to be created by selecting columns from the data. 








