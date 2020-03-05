#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 16:29:58 2020

@author: albertoyanguasrovira
"""

import pandas as pd
from sqlalchemy import create_engine
import numpy as np

# Load csv to a DataFrame
df = pd.read_csv('../data/MiningProcess_Flotation_Plant_Database.csv', nrows=10000)

array_columns = []
for column in df.columns:
    array_columns = np.append(array_columns, column.replace('%', 'Percentage'))

df.columns = array_columns

# Creation conexion to local database, DattiumApp; user=test; pswd=test123
conn = create_engine('postgresql://test:test123@127.0.0.1:5432/DattiumApp')

# Create a table with df 
df.to_sql(name='test', con=conn, if_exists = 'replace')