#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 10:24:24 2020

@author: albertoyanguasrovira
"""

import pandas as pd
from sqlalchemy import create_engine
import numpy as np

##############################################################################
#                              01_EXTRACT                                    #
##############################################################################

# Conexion creation to local database, DattiumApp; user=test; pswd=test123
local_conn = create_engine('postgresql://test:test123@127.0.0.1:5432/DattiumApp')
# Extract all rows from signals
df = pd.read_sql('SELECT * FROM signals', local_conn, parse_dates='date')

##############################################################################
#                             02_TRANSFORM                                   #
##############################################################################

df = df.groupby('date').mean()

##############################################################################
#                               03_LOAD                                      #
##############################################################################
# Conexion creation to server (192.168.1.33) database, DattiumApp; user=test; pswd=test123
server_conn = create_engine('postgresql://test:test123@192.168.1.33:5432/DattiumApp')
# Load transformed DataFrame to server
df.to_sql(name='signals', con=server_conn, if_exists='replace')