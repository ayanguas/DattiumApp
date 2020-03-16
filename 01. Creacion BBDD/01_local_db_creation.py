#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 16:29:58 2020

@author: albertoyanguasrovira
"""

import pandas as pd
from sqlalchemy import create_engine
import numpy as np
from datetime import datetime

# Load csv to a DataFrame (converters is used to change string date to datetime)
df = pd.read_csv('../data/MiningProcess_Flotation_Plant_Database.csv', \
                 converters={'date': lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S')},\
                     decimal =',')

# Delete of character '%' from DataFrame columns names
array_columns = []
for column in df.columns:
    array_columns = np.append(array_columns, column.replace('%', 'Percentage'))
df.columns = array_columns

# Creation conexion to local database, DattiumApp; user=test; pswd=test123
conn = create_engine('postgresql://test:test123@127.0.0.1:5432/DattiumApp')

# Create a table with df 
df.to_sql(name='raw', con=conn, if_exists = 'replace', index=False)