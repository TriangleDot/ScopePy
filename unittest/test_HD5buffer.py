# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 11:51:07 2015

@author: john

Unit test for HDF5 buffer
=================================



"""


#==============================================================================
#%% Imports
#==============================================================================

# Standard library
import os,sys
import string
import unittest
import inspect


CURRENTPATH, dummy = os.path.split(os.path.abspath(__file__))
BASEPATH = os.path.dirname(CURRENTPATH)
sys.path.append(BASEPATH)
sys.path.append(os.path.join(BASEPATH,'data_sources'))


# Third party libraries
import numpy as np
import h5py

# My libraries
from source_hdf5 import Hdf5Buffer,DatasetTableWrapper


#==============================================================================
#%% Constants
#==============================================================================
TEST_FILENAME = "HDF5_test.h5"
HDF5_FILE = None

# HDF5 field names
ARRAY_2D = "array_2D"
ARRAY_1D = "array_1D"
RECARRAY = "recarray" 
COMPLEX_ARRAY = "complex array"

# Array sizes
NROWS = 500
NCOLS = 100
NCOLS_RECARRAY = 26

#==============================================================================
#%% Class definitions
#==============================================================================


#==============================================================================
#%% Functions
#==============================================================================


def whoami():
    return inspect.stack()[1][3]
    
def print_test_name(function_name):
    print('\n')
    print("-"*40)
    print("Method: %s" % function_name)
    print("-"*40)
    

def makeTestFile(filename=TEST_FILENAME):

    # Make recarray example
    # ===============================    
    upperCaseLetters = list(string.ascii_uppercase)
    dtype = [(letter,float) for letter in upperCaseLetters]
    
    recarray = np.zeros(NROWS,dtype)
    
    
    for iCol,name in enumerate(upperCaseLetters):
        recarray[name] = np.arange(NROWS) + (iCol/100)
        
    
    # Make normal 2D array example
    #===============================    
    array2d = np.zeros((NROWS,NCOLS),np.float)
    
    for iCol in range(NCOLS):
        array2d[:,iCol] = np.arange(NROWS) + (iCol/100)
        
    # Make 1D array example
    # ================================
    array1d = np.arange(NROWS)
    
    
    # Make complex array example
    # =================================
    arrayComplex = np.zeros((NROWS,NCOLS),np.complex)
    
    for iCol in range(NCOLS):
        arrayComplex[:,iCol] = np.arange(NROWS) + 1j*(iCol/100)
    
    
    # Make HDF5 file
    # =======================
    with h5py.File(os.path.join(CURRENTPATH,filename), "w") as f:
        f.create_dataset(RECARRAY, data=recarray)
        f.create_dataset(ARRAY_2D, data=array2d)
        f.create_dataset(ARRAY_1D, data=array1d)
        f.create_dataset(COMPLEX_ARRAY, data=arrayComplex)
        
    
        

def getTestFile(filename=TEST_FILENAME):
    
    pathAndFilename = os.path.join(CURRENTPATH,filename)
    assert os.path.exists(pathAndFilename),"Unable to open test file [%s]" % filename
    
    return h5py.File(pathAndFilename,'r')
    


#==============================================================================
#%% Tests
#==============================================================================

class Test_HDF5_buffer(unittest.TestCase):
    """
    Tests for the Hdf5Buffer and DatasetTableWrapper classes
    
    """
    
    
    #%% Setup teardown
    # ------------------------------------------------------------------------
    
    def setUp(self):
        """
        Setup HDF5 files for testing
        
        """
        
        makeTestFile()
        self.source_file = getTestFile()
        
    def tearDown(self):
        self.source_file.close()
        
        
        
    #%% Hd5Buffer tests
    # ------------------------------------------------------------------------
        
    def test_read_rec_array(self):
        """
        Basic read of recarray
        
        """
        
        print_test_name(whoami())

        
        buf_rec = Hdf5Buffer(self.source_file[RECARRAY],100,5,250,15)
        buf_rec.read()
          
        self.assertTrue(buf_rec.sourceColumnCount==NCOLS_RECARRAY,"recarray columns not correct")
        self.assertTrue(buf_rec.sourceRowCount==NROWS,"recarray rows not correct")
        self.assertTrue(buf_rec._rows==250,"recarray internal rows not correct")
        self.assertTrue(buf_rec._columns==15,"recarray internal columns not correct")
        self.assertTrue(buf_rec.start_row==100,"recarray start row is not correct")
        self.assertTrue(buf_rec.start_column==5,"recarray start column is not correct")
        
        
    def test_read_rec_array_fitted(self):
        """
        Read recarray and resize buffer to fit
        
        """
        print_test_name(whoami())
        
        buf_rec = Hdf5Buffer(self.source_file[RECARRAY],100,5,NROWS,NCOLS)
        buf_rec.read()
          
        self.assertTrue(buf_rec.sourceColumnCount==NCOLS_RECARRAY,"recarray columns not correct")
        self.assertTrue(buf_rec.sourceRowCount==NROWS,"recarray rows not correct")
        self.assertTrue(buf_rec._rows==NROWS,"recarray internal rows not correct")
        self.assertTrue(buf_rec._columns==NCOLS_RECARRAY,"recarray internal columns not correct")
        self.assertTrue(buf_rec.start_row==0,"recarray start row is not correct")
        self.assertTrue(buf_rec.start_column==0,"recarray start column is not correct")
        
    


    def test_read_2d_array(self):
        """
        Basic read of 2D
        
        """
        print_test_name(whoami())
        
        buf_2d = Hdf5Buffer(self.source_file[ARRAY_2D],100,20,250,60)
        buf_2d.read()
          
        self.assertTrue(buf_2d.sourceColumnCount==NCOLS,"2D array columns not correct")
        self.assertTrue(buf_2d.sourceRowCount==NROWS,"2D array rows not correct")
        self.assertTrue(buf_2d._rows==250,"2D array internal rows not correct")
        self.assertTrue(buf_2d._columns==60,"2D array internal columns not correct")
        self.assertTrue(buf_2d.start_row==100,"2D array start row is not correct")
        self.assertTrue(buf_2d.start_column==20,"2D array start column is not correct")
        
        
    def test_read_2d_array_fitted(self):
        """
        Read 2D array and resize
        
        """
        print_test_name(whoami())
        
        buf_2d = Hdf5Buffer(self.source_file[ARRAY_2D],100,20,NROWS,NCOLS)
        buf_2d.read()
          
        self.assertTrue(buf_2d.sourceColumnCount==NCOLS,"2D array columns not correct")
        self.assertTrue(buf_2d.sourceRowCount==NROWS,"2D array rows not correct")
        self.assertTrue(buf_2d._rows==NROWS,"2D array internal rows not correct")
        self.assertTrue(buf_2d._columns==NCOLS,"2D array internal columns not correct")
        self.assertTrue(buf_2d.start_row==0,"2D array start row is not correct")
        self.assertTrue(buf_2d.start_column==0,"2D array start column is not correct")
        
        
        
    def test_reload_definite_recarray(self):
        """
        Test reloading recarray
        
        """
        print_test_name(whoami())

        # Load rec array        
        buf_rec = Hdf5Buffer(self.source_file[RECARRAY],100,5,250,15)
        buf_rec.read()

        # Definite reload    
        # ----------------------------------------    
        buf_rec.reload([0,100],[0,14])
        
        self.assertTrue(buf_rec.start_row==0,"recarray start row is not correct")
        self.assertTrue(buf_rec.start_column==0,"recarray start column is not correct")
        self.assertTrue(buf_rec.end_row==249,"recarray end row is not correct")
        self.assertTrue(buf_rec.end_column==14,"recarray end row is not correct")
        
        
        
        
        
    def test_reload_no_reload_recarray(self):
        """
        Test reload() recarray
         - No reload should occur here
        
        """
        print_test_name(whoami())

        # Load rec array        
        buf_rec = Hdf5Buffer(self.source_file[RECARRAY],100,5,250,15)
        buf_rec.columnThreshold = 2
        buf_rec.read()
        
        print("Start Buffer:\n",buf_rec)

        # No reload    
        # ----------------------------------------    
        print("\nNew buffer:\n")
        buf_rec.reload([130,150],[8,15])
        
        print("End Buffer:\n",buf_rec)
        
        self.assertTrue(buf_rec.start_row==100,"recarray start row is not correct")
        self.assertTrue(buf_rec.start_column==5,"recarray start column is not correct")
        self.assertTrue(buf_rec.end_row==349,"recarray end row is not correct")
        self.assertTrue(buf_rec.end_column==19,"recarray end row is not correct")
        
        
    #%% DataTableWrapper tests
    # ------------------------------------------------------------------------
        
    def test_make_wrapper_rec_array(self):
        """
        Test creating a wrapper from a recarray
        
        """
        print_test_name(whoami())
        
        wrapper = DatasetTableWrapper(self.source_file[RECARRAY])
        
        print("Wrapper shape = %i x %i" % (wrapper.rowCount(),wrapper.columnCount()))
        
        self.assertTrue(wrapper.columnCount()==NCOLS_RECARRAY,"column count is wrong" )
        self.assertTrue(wrapper.rowCount()==NROWS,"row count is wrong" )
        
        
    def test_wrapper_index_rec_array(self):
        """
        Test creating a wrapper from a recarray
        
        """
        print_test_name(whoami())
        
        wrapper = DatasetTableWrapper(self.source_file[RECARRAY])
        
        self.assertTrue(wrapper.cell(0,0)==0.0,"cell(0,0) is wrong")
        
        answer = NROWS-1 + (NCOLS_RECARRAY-1)/100
        self.assertTrue(wrapper.cell(NROWS-1,NCOLS_RECARRAY-1)==answer,
                        "cell(%i,%i) is wrong" % (NROWS-1,NCOLS_RECARRAY-1) )
                        
                        

    def test_wrapper_column_rec_array(self):
        """
        Test creating a wrapper from a recarray
        
        """
        print_test_name(whoami())
        
        wrapper = DatasetTableWrapper(self.source_file[RECARRAY])
        
        col_values = wrapper.getColumn(3)
        end_row = NROWS-1
        
        self.assertTrue(col_values.min()==0.03,"column min is wrong")
        self.assertTrue(col_values.max()==end_row+0.03,"column max is wrong")
        
        
    
#==============================================================================
#%% Runner
#==============================================================================

#if __name__ == "__main__":
#    
#    if 'src' in dir():
#        src.close()
#        
#        
#    makeTestFile()
#    src = getTestFile()
#
#    buf_rec = Hdf5Buffer(src[RECARRAY],100,5,250,15)
#    buf_rec.columnThreshold = 3
#    buf_rec.read()
#    
#    buf_2d = Hdf5Buffer(src[ARRAY_2D],100,20,250,60)
#    buf_2d.read()
#
#    # Rec array test
#    # =========================    
#    print("RecArray")
#    print("="*60)
#    print(buf_rec)
#    
#    # Try resizing recarray
#    # --------------------------
#    print('\n1. Definite reload:')
#    buf_rec.reload([0,100],[0,14])
#    
#    
#    print('\n2. No reload:')
#    buf_rec.reload([0,50],[0,12])
#    
#    print("\n")
#    print('*'*65)
#    
#    # 2D array test
#    # =========================    
#    print("2D Array")
#    print("="*60)
#    print(buf_2d)
#    
#    print('\nDefinite reload:')
#    buf_2d.reload([0,100],[0,14])
#    
#    print('\n2. No reload:')
#    buf_2d.reload([0,50],[0,12])
#    
#    print("\n")
#    print('*'*65)
#    
#    
#    # Rec array test fitted
#    # =========================    
#    print("\n\nRecArray - fitted")
#    print("="*60)
#    buf_rec_fit = Hdf5Buffer(src[RECARRAY],100,5,NROWS,NCOLS)
#    buf_rec_fit.read()
#    print(buf_rec_fit)
#    
#    
#    
#    # 2D array test fitted
#    # =========================    
#    print("\n\n2D Array - fitted")
#    print("="*60)
#    buf_2d_fit = Hdf5Buffer(src[ARRAY_2D],100,5,NROWS,NCOLS)
#    buf_2d_fit.read()
#    print(buf_2d_fit)
    
if __name__ == "__main__":
    unittest.main()    
    
#    test = Test_HDF5_buffer()
#    test.setUp()
#    test.run()
#    test.tearDown()
    
    
    
    
    