#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 10:24:24 2020

@author: albertoyanguasrovira
"""

import pandas as pd
from sqlalchemy import create_engine
import numpy as np

# Cambiar a False para conectarse a un servidor remoto y modificar 
# la ip con la dirección del servidor
local = True

if not local:
    ip = '192.168.1.33'
else:
    ip = '127.0.0.1'

##############################################################################
#                              01_EXTRACT                                    #
##############################################################################

# Conexion creation to local database, DattiumApp; user=test; pswd=test123
local_conn = create_engine('postgresql://test:test123@127.0.0.1:5432/DattiumApp')
# Extract all rows from signals
df = pd.read_sql('SELECT * FROM raw', local_conn, parse_dates='date')

##############################################################################
#                             02_TRANSFORM                                   #
##############################################################################

# Media por horas de las señales
df = df.groupby('date').mean()
df['label_S1'] = np.random.choice(3, len(df), p=[0.05, 0.15, 0.8])
df['label_S2'] = np.random.choice(3, len(df), p=[0.05, 0.15, 0.8])
df['label_S3'] = np.random.choice(3, len(df), p=[0.05, 0.15, 0.8])
df['label'] = df['label_S1'] + df['label_S2'] + df['label_S3']

##############################################################################
#                               03_LOAD                                      #
##############################################################################
# Conexion creation to server (192.168.1.33) database, DattiumApp; user=test; pswd=test123
server_conn = create_engine('postgresql://test:test123@{}:5432/DattiumApp'.format(ip))
# Load transformed DataFrame to server
df.to_sql(name='signals', con=server_conn, if_exists='replace')