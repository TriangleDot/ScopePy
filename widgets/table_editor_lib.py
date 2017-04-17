# -*- coding: utf-8 -*-
"""
Created on Sat Sep 19 14:19:25 2015

@author: john

Version
==============================================================================
$Revision:: 75                            $
$Date:: 2015-09-13 12:13:04 -0400 (Sun, 1#$
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



#==============================================================================
#%% Imports
#==============================================================================

# Standard library
import os,sys
import imp
import logging

# Third party libraries
import numpy as np
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# My libraries


#==============================================================================
#%% Constants
#==============================================================================



           
            
            

#==============================================================================
#%% Table Model
#==============================================================================

class TableEditorModel(QAbstractTableModel):
    """
    Model for table editor.
    This is responsible for extracting and inserting data into the table editor
    
    Formats supported:
        * HDF5
        * numpy array
        
    TODO: formats e.g pandas dataframe, CSV, Excel
    
    """
    
    def __init__(self,table_data):
        """
        
        Inputs
        ---------
        table_data : data source wrapper class
            class object that provides a standard set of methods for accessing
            the underlying data
            
        """
        
        super(TableEditorModel,self).__init__()
        
        # Check the data source has a formatter
        assert hasattr(table_data,'formatter'),"Data source does not have a formatter class"
        self.data_source = table_data
        
        self.column_formats = '%.4f'
        
        # Link to formatting function
        self.format = table_data.formatter.format
        
        
        
    # -----------------------------------------------------------------------    
    # Required methods
    # -----------------------------------------------------------------------
    def data(self,index, role=Qt.DisplayRole):
        """
        Return numeric data from the data source, formatted according to
        each column's format requirements.
        
        TODO : format for each column
        """
        
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return
            
        col = index.column()
        row = index.row()
        
        if role == Qt.DisplayRole:
            # Get value of cell and return with appropriate format
            value = self.data_source.cell(row,col)
            
            # Use data source formatter
            return self.format(value)
            
#            if isinstance(value,str):
#                return value
#            elif value is not None:
#                return self.data_source.columnFormat(col) % value
#            else:
#                return "##"
            
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignLeft|Qt.AlignVCenter)
        
        
    
    def rowCount(self,index=QModelIndex()):
        return self.data_source.rowCount()

        
    def columnCount(self,index=QModelIndex()):
        return self.data_source.columnCount()

    
    def headerData(self,section,orientation,role=Qt.DisplayRole):
        
        # Alignment role
        # ---------------------
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignCenter|Qt.AlignVCenter)

        if role != Qt.DisplayRole:
            return None            
            
        # Horizontal
        # --------------
        if orientation == Qt.Horizontal:
            return self.data_source.columnHeaders()[section]
            
        # Vertical
        # --------------------
        # Return a number
        return int(section+1)

    
    def flags(self, index):
        """
        Direct copy from Mark Summerfield
        - Makes everything editable
        """
        
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(
                QAbstractTableModel.flags(self, index)|
                Qt.ItemIsEditable)


    
    def setData(self,index,value, role=Qt.EditRole):
        """
        Convert value as string into a float and put back into data source
        
        """
        
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return
            
        if role == Qt.EditRole:
            col = index.column()
            row = index.row()
            
            try:
                self.data_source.setCell(row,col,np.float(value))
                self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                      index, index)
                return True
                
            except:
                pass
            
        return False
            
                    
            

    
    def insertRows(self, position, rows=1, index=QModelIndex()):
        
        # Begin insert (standard call)
        # -------------------------------------
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        
        # Do the insertion        
        # -----------------------
        self.data_source.insertRows(position,rows)
                              
        # End the insert (standard call)
        # -------------------------------------
        self.endInsertRows()
        self.dirty = True
        return True


    
    def removeRows(self, position, rows=1, index=QModelIndex()):
        
        # Begin removal (standard call)
        # --------------------------------------------
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
        
        # Do the removal
        # ---------------------------
        self.data_source.removeRows(position,rows)
                      

        # End the removal (standard call)
        # ---------------------------------------
        self.endRemoveRows()
        self.dirty = True
        return True

    
    # -----------------------------------------------------------------------    
    # User methods
    # -----------------------------------------------------------------------
    def columnName(self,column_index):
        """ 
        Return the column name for the specified index
        
        Input
        --------
        column_index : int
            
        Output
        --------
        column_name : str
            Name of column at the column given by column_index
            
        """
        return self.data_source.columnHeaders()[column_index]
        
    def columnHeaders(self):
        """
        Return a list of the column headers
        
        Output
        -------
        headers : list of str
            column headers in order
            
        """
        return self.data_source.columnHeaders()
        
        
    
    def rawData(self,row,col):
        """
        Extract raw data from table
        
        Inputs
        --------
        row,col : int
            cell coordinates in table
            
        Output
        -------
        value : float
            cell value
        """
        
        value = self.data_source.cell(row,col)
        
        if value:
            return value
        else:
            return
            
            
            
            
    def getColumnByIndex(self,column_index):
        """
        Retreive a whole column in one shot.
        
        This calls the data_source function getColumn() so that it can use
        any fast methods of extracting whole columns that it may have.
        
        Input
        -----
        column_index : int
        
        Output
        -------
        array : single column numpy array
        
        """
        
        array = self.data_source.getColumn(column_index)

        return array
        
        
    def tableChanged(self,visibleRows,visibleColumns):
        """
        Slot called by TableEditorWidget, to tell the model that the size of
        the table displayed on screen has changed.
        
        If the underlying data is buffered then this can be used to signal to
        refresh the buffer.
        
        Inputs
        ---------
        visibleRows : list of 2 ints
            [top_row_index,bottom_row_index]
            
        visibleColumns  : list of 2 ints
            [left_column_index, right_column_index]
            
        """
        
        nRows = visibleRows[1]-visibleRows[0]
        nCols = visibleColumns[1]-visibleColumns[0]
        #print("Model:Table changed:\n\t%i rows x %i cols" % (nRows,nCols))
        
        if hasattr(self.data_source,'tableChanged'):
            self.data_source.tableChanged(visibleRows,visibleColumns)
        
        
        
    


#==============================================================================
#%% Table delegate
#==============================================================================
class TableEditorDelegate(QItemDelegate):
    """
    Table editor delegate
    
    """
    
    def __init__(self,parent=None):
        super(TableEditorDelegate,self).__init__(parent)
        
        
    def createEditor(self,parent,option,index):
        """
        Return a QLineEdit for all columns that only accepts numeric input
        
        """
        float_regex = QRegExp(r"[\.0-9\-\+e\*\/]+")
        float_validator = QRegExpValidator(float_regex)
        
        editor = QLineEdit(parent)
        editor.setValidator(float_validator)
        self.connect(editor,SIGNAL('returnPressed()'),self.commitAndCloseEditor)
        
        return editor
        
        
    
    def setEditorData(self,editor,index):
        """
        Get numeric data from model as text and put into editor
        """
        
        number_as_text = index.model().data(index,Qt.DisplayRole)
        editor.setText(number_as_text)
        
    
    def setModelData(self,editor,model,index):
        """
        Pass back string to model and let it do the conversions
        """
        model.setData(index,editor.text())
        
    
    def commitAndCloseEditor(self):
        editor = self.sender()
        if isinstance(editor, (QTextEdit, QLineEdit)):
            self.emit(SIGNAL("commitData(QWidget*)"), editor)
            self.emit(SIGNAL("closeEditor(QWidget*)"), editor)

    
    def sizeHint(self,option,index):
        """
        Return a size based on an assumed number length
        TODO : This could be done more intelligently
        
        """
        
        fm = option.fontMetrics
        
        standard_number = '999999.9999'
        
        return Qsize(fm.width(standard_number),fm.height())
    
    

#==============================================================================
#%% TableEditor widget
#==============================================================================

class TableEditorWidget(QTableView):
    """
    Table editor
    
    This is a QTableView with extra methods for extracting selections
    
    """
    
    def __init__(self,parent=None):
        super(TableEditorWidget, self).__init__(parent)
        
        
        whatsThis = """
        Keyboard short cuts:
        ALT + Up arrow : Insert row above
        ALT + Down arrow : Insert row below
        """
        self.setWhatsThis(whatsThis)
        
        
    def keyPressEvent(self,event):
        """
        Handle key presses
        
        
        """

        alt_pressed = event.modifiers() & Qt.AltModifier
        ctrl_pressed = event.modifiers() & Qt.ControlModifier
        
        if event.key() == Qt.Key_Down:
            if alt_pressed:
                self.insertRowBelow()
            
        elif event.key()==Qt.Key_Up:
            if alt_pressed:
                self.insertRowAbove()
            
            
            
        # Not this widgets actions, call parent keyPressEvent
        super().keyPressEvent(event)
            
        
        
    def currentRow(self):
        """
        Return current row
        
        Output
        ----------
        row : int
        
        """
        
        return self.currentIndex().row()
        

    def currentColumn(self):
        """
        Return current column
        
        Output
        ----------
        column : int
        
        """
        
        return self.currentIndex().column()
        
        
    
    def getStrSelection(self):
        """
        Like getSelection, but returns a list and CAN HANDLE STRINGS!!
            
        """
        
        # Get selected cells
        # -----------------------------
        sel_indexes  = self.selectedIndexes()
        
        # Quit if no selection
        if sel_indexes == []:
            return
            
        # Get row and column indexes
        # -------------------------------
        rows = [ind.row() for ind in sel_indexes]
        cols = [ind.column() for ind in sel_indexes]
        
        nRows = len(set(rows))
        minRow = min(rows)
        

        
        # Get column headers for selected columns
        # ------------------------------------------
        model = self.model()
        
        # List of headers in selection
        column_headers = [model.headerData(col,Qt.Horizontal) for col in set(cols)]
        
        # Dictionary to convert column indexes to a header label
        colLabel = {col:model.headerData(col,Qt.Horizontal) for col in set(cols)}
        
        # Copy data into a numpy recarray
        # ----------------------------------
        
        # Make the array, initialised to NaNs
        dtype = [(name,str) for name in column_headers]
        array = np.zeros(nRows,dtype)
        
        # Make everything NaN
        # array[:] = np.nan (this doesn't work when a single row is selected)
        for name in array.dtype.names:
            array[name] = np.nan
        
        
        
        # Extract data from selection
        for row,col in zip(rows,cols):
            value = model.rawData(row,col)
            
            if value:
                array[colLabel[col]][row-minRow] = value
                
                
        return array.toList()
        
    def getSelection(self):
        """
        Return cells selected in the table as an array
        
        This is a raw selection. Use getSelectionAsList or getSelectionAsDict
        for other formats.
        
        Output
        -------
        array : numpy recarray
            return array with headers embedded in
            
        """
        
        # Get selected cells
        # -----------------------------
        sel_indexes  = self.selectedIndexes()
        
        # Quit if no selection
        if sel_indexes == []:
            return
            
        # Get row and column indexes
        # -------------------------------
        rows = [ind.row() for ind in sel_indexes]
        cols = [ind.column() for ind in sel_indexes]
        
        nRows = len(set(rows))
        minRow = min(rows)
        

        
        # Get column headers for selected columns
        # ------------------------------------------
        model = self.model()
        
        # List of headers in selection
        column_headers = [model.headerData(col,Qt.Horizontal) for col in set(cols)]
        
        # Dictionary to convert column indexes to a header label
        colLabel = {col:model.headerData(col,Qt.Horizontal) for col in set(cols)}
        
        # Copy data into a numpy recarray
        # ----------------------------------
        
        # Make the array, initialised to NaNs
        dtype = [(name,float) for name in column_headers]
        array = np.zeros(nRows,dtype)
        
        # Make everything NaN
        # array[:] = np.nan (this doesn't work when a single row is selected)
        for name in array.dtype.names:
            array[name] = np.nan
        
        
        
        # Extract data from selection
        for row,col in zip(rows,cols):
            value = model.rawData(row,col)
            
            if value:
                array[colLabel[col]][row-minRow] = value
                
                
        return array
        
        
    def getSelectionAsList(self):
        """
        Return multiple column selection as a list of tuples
        
        Each tuple has the same number of elements as columns in the selection.
        
        Output
        ---------
        selection : list of tuples
            Example if the selection is
            1   2
            3   4
            5   6
            
            Then the returned list will be
            [(1,2),(3,4),(5,6)]
            
            So access element in row 1, column 1 (remember zero indexing)
                element = selection[1][1]
        
        """
        
        array = self.getSelection()
        
        if array is not None:
            return array.tolist()
            
            
    def getSelectionAsDict(self):
        """
        Return selection as a dictionary, where the key is the column header
        and the values are a list of numbers.
        
        Output
        -------
        selection : dict of lists
            Example if the selection is
            x   y            (column headers in table view)
            1   2
            3   4
            5   6
            
            The returned dictionary will be:
            selected = {'x':[1,3,5],'y':[2,4,6]}
        """
        
        array = self.getSelection()
        
        if array is None:
            return
            
        selected = {}
        for name in array.dtype.names:
            selected[name] = array[name].tolist()
            
        return selected
        
        
    def getSelectedColumn(self):
        """
        If a single column has been selected this function will extract
        everything in that column using the root data source methods
        e.g. array slicing from a numpy array.
        
        If more than one column is selected then nothing is returned
        
        Output
        -------
        array : numpy array
            Single column array
            
        """
        
        # Get selected cells
        # -----------------------------
        sel_indexes  = self.selectedIndexes()
        
        # Quit if no selection
        if sel_indexes == []:
            return
            
        # Get column index
        # -------------------------------
        cols = list(set([ind.column() for ind in sel_indexes]))
        nCols = len(cols)
        
        # Exit if more than one column is selected
        if nCols > 1:
            return
            
        # Use model to extract a whole column
        return self.model().getColumnByIndex(cols[0])
        
        
        
    def getSelectedColumnAsList(self):
        
        array = self.getSelectedColumn()
        
        if array is not None:
            return array.tolist()
            
            
            
            
    def getSelectedColumnName(self):
        """
        If a single column has been selected this function will extract
        the name of the column
        
        If more than one column is selected then nothing is returned
        
        Output
        -------
        column_name : str
            
        """
        
        # Get selected cells
        # -----------------------------
        sel_indexes  = self.selectedIndexes()
        
        # Quit if no selection
        if sel_indexes == []:
            return
            
        # Get column index
        # -------------------------------
        cols = list(set([ind.column() for ind in sel_indexes]))
        nCols = len(cols)
        
        # Exit if more than one column is selected
        if nCols > 1:
            return
            
        # Use model to extract column name
        return self.model().columnName(cols[0])
        
        
        
        
    def getSelectedColumnIndex(self):
        """
        If a single column has been selected this function will extract
        the index of the column
        
        If more than one column is selected then nothing is returned
        
        Output
        -------
        column_index : int
            
            
        """
        
        # Get selected cells
        # -----------------------------
        sel_indexes  = self.selectedIndexes()
        
        # Quit if no selection
        if sel_indexes == []:
            return
            
        # Get column index
        # -------------------------------
        cols = list(set([ind.column() for ind in sel_indexes]))
        nCols = len(cols)
        
        # Exit if more than one column is selected
        if nCols > 1:
            return
            
        # Use model to extract column name
        return self.model().columnName(cols[0])
        
        
        
        
    def getColumnByIndex(self,column_index):
        """
        Return whole column by index
        
        Inputs
        ----------
        column_index : int
        
        Output
        -------
        column_array : numpy array
            data from specified column
            
        """
        
        # Use model to extract a whole column
        return self.model().getColumnByIndex(column_index)
        
        
    
    def getColumnByName(self,column_name):
        """
        Return whole column by header name
        
        Inputs
        ----------
        column_name : str
        
        Output
        -------
        column_array : numpy array
            data from specified column
            
            or None if column does not exist
            
        """
        
        column_headers = self.model().columnHeaders()
        
        if column_name not in column_headers:
            return
            
        column_index = column_headers.index(column_name)
        
        
        # Use model to extract a whole column
        return self.model().getColumnByIndex(column_index)
        
        
    def isColumnInTable(self,column_name):
        """
        Check if a column name is in the table
        
        Inputs
        ----------
        column_name : str
        
        Output
        -------
        col_exists : bool
            True if column_name is in the table
            
        """
        
        column_headers = self.model().columnHeaders()
        
        return column_name in column_headers
            
            
        
    def getColumnIndexFromName(self,column_name):
        """
        Return whole column index from header name, or return none
        
        Inputs
        ----------
        column_name : str
        
        Output
        -------
        column_array : numpy array
            data from specified column
            
            or None if column does not exist
            
        """
        
        column_headers = self.model().columnHeaders()
        
        if column_name not in column_headers:
            return
            
        column_index = column_headers.index(column_name)
        
        return column_index
    
    
    def visibleRows(self):
        """
        Return the row indexes of the visible rows in the table
        
        Output
        -------
        rows : list
            [top_row_index,bottom_row_index]
            
        """
        
        # The incredibly convoluted method of getting rows and columns from
        # screen coordinates!
        rows = [self.rowAt(self.rect().topLeft().y()),
                self.rowAt(self.rect().bottomLeft().y())]
                
        return rows
        
        
    
    def visibleColumns(self):
        """
        Return the column indexes of the visible columns in the table
        
        Output
        -------
        cols : list
            [left_col_index,right_col_index]
            
        """
        
        # The incredibly convoluted method of getting rows and columns from
        # screen coordinates!
        cols = [self.columnAt(self.rect().topLeft().x()),
                self.columnAt(self.rect().topRight().x())]
                
        return cols
        
        
        
    def tableChanged(self):
        rows = self.visibleRows()
        cols = self.visibleColumns()
        nRows = rows[1]-rows[0]
        nCols = cols[1]-cols[0]
        #print("Widget:Table changed:\n\t%i rows x %i cols\n ---**---" % (nRows,nCols))
        
        if self.model() is not None:
            self.model().tableChanged(rows,cols)
        
        
        
    def resizeEvent(self,event):
        """
        Intercept resize event in order to catch the new size of the table.
        This is useful for buffered sources that need to be told which part of
        the table is being displayed so they can decide whether to refresh 
        the buffer.
        
        """
        
        self.tableChanged()
        
        super().resizeEvent(event)
        
        
    @property
    def readOnly(self):
        """
        Return whether the data is read-only or not
        
        Output:
        ---------
        readOnly : bool
        
        """
        
        if hasattr(self.model().data_source,'readOnly'):
            return self.model().data_source.readOnly
        else:
            return False
            
            
    def insertRows(self,pos,rows=1):
        """
        Insert rows into table
        
        Inputs
        ---------
        pos : int
            starting row
            
        rows : int
            Number of rows to insert
            
        """
        
        self.model().insertRows(pos,rows)
        
        
    def insertRowBelow(self):
        """
        Insert a blank row in the table
        Keyboard shortcut ALT+Down Arrow
        
        """
        print("Table editor insert row below")
        
        # Don't insert anything for read-only data
        if self.readOnly:
            return
        
        # Get current row
        row = self.currentRow()
        
        # Insert new row underneath current row
        self.insertRows(row+1)
        
        
    def insertRowAbove(self):
        """
        Insert a blank row in the table
        Keyboard shortcut ALT+Up Arrow
        
        """
        print("Table editor insert row above")
        
        # Don't insert anything for read-only data
        if self.readOnly:
            return
        
        # Get current row
        row = self.currentRow()
        
        # Insert new row above current row
        if row > 0:
            self.insertRows(row-1)
        else:
            self.insertRows(0)
        
        
        
        
        
        
        

#==============================================================================
#%% MainForm for testing
#==============================================================================
class MainForm(QDialog):
    """ Class for testing graph widgets
    """

    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)

        data = self.make_data()

        self.model = TableEditorModel(NumpyTableWrapper(data))

        self.table = TableEditorWidget()
        self.table.setModel(self.model)
        self.table.setItemDelegate(TableEditorDelegate(self))
        
        dumpSelectionButton = QPushButton("Dump selection")
        dumpColumnSelectionButton = QPushButton("Dump Column selection")
        
        dumpPositionButton = QPushButton("Dump position")        
        
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(dumpPositionButton)
        layout.addWidget(dumpSelectionButton)
        layout.addWidget(dumpColumnSelectionButton)
        
        self.connect(dumpPositionButton,SIGNAL("clicked()"),self.dumpPosition)
        self.connect(dumpSelectionButton,SIGNAL("clicked()"),self.dumpSelection)
        self.connect(dumpColumnSelectionButton,SIGNAL("clicked()"),self.dumpColumn)
        
        self.setLayout(layout)
        
        
        
        
    def make_data(self):
        """
        Make a set of data for testing table editor
        """
        npoints = 30

        # Create array
        dtype = [('H%i' % n,float) for n in range(5) ]
        data = np.zeros(npoints,dtype)

        for col,name in enumerate(data.dtype.names):
            data[name] = 100*col + np.random.rand(npoints)
            
        return data
        
        
    def dumpSelection(self):
        """
        Print selected column
        """
        
        
        selected_array = self.table.getSelection()
        
        if selected_array is None:
            return
            
        print('\nSelected array:')
        print('-'*60)
        print(selected_array)
        
        selected_list = self.table.getSelectionAsList()
        print('\nSelected list:')
        print('-'*60)
        print(selected_list)
        
        selected_dict = self.table.getSelectionAsDict()
        print('\nSelected dict:')
        print('-'*60)
        print(selected_dict)
        
        
    def dumpColumn(self):
        
        selected_array = self.table.getSelectedColumn()
        
        if selected_array is None:
            return
           
        print('\nSelected Column array:')
        print('-'*60)
        print(selected_array)
        
            
        selected_list = self.table.getSelectedColumnAsList()
        print('\nSelected Column list:')
        print('-'*60)
        print(selected_list)
        
        
    def dumpPosition(self):
        
        print("Current Row: ",self.table.currentRow())
        print("Current Column: ",self.table.currentColumn())
        print("Current index:",self.table.currentIndex())
        
        


#=============================================================================
#%% Code runner
#=============================================================================


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = MainForm()
    rect = QApplication.desktop().availableGeometry()
    print("Screen rect",rect)
    form.resize(int(rect.width() * 0.4), int(rect.height() * 0.5))
    #form.resize(800, 600)
    form.show()
    app.exec_()
