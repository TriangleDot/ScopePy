"""
Numpy Array source creator example
=====================================

"""

# Imports
# ==========================
import string,time
import numpy as np


# Test code
# ========================================


# Numpy array
# ------------------
NROWS = 10
cols = ['a','b','c']
dtype = [(letter,float) for letter in cols]
recarray = np.zeros(NROWS,dtype)
for iCol,name in enumerate(cols):
    recarray[name] = np.arange(NROWS) + (iCol/100)

API.addDataSource('NumpyArray','test_array_with_numbers',recarray)
    


