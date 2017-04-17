"""
Numpy Array source creator example
=====================================

"""

# Imports
# ==========================
import string,time
import numpy as np
import pandas as pd

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

API.addDataSource('NumpyArray','array_with_numbers',recarray)
    
# Pandas dataframe
# ------------------

# Create basic numeric data
df = pd.DataFrame(recarray)

# Add text data
upperCaseLetters = list(string.ascii_uppercase)
df['txt']=pd.Series(upperCaseLetters[0:NROWS])

# Add timestamps
tl = []
for n in range(10):
    time.sleep(1)
    tl.append(time.asctime())
    
df['timestamp'] = pd.to_datetime(pd.Series(tl))

API.addDataSource('Dataframe','test_frame',df)

