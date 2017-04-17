# Pandas dataframe with long names
import pandas as pd

filename='/home/john/Documents/Python/datafiles/PwrDetFails.csv'
df = pd.read_csv(filename)
API.addDataSource('Dataframe','Long name dataframe',df)
