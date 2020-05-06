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
local = False

if not local:
    ip = 'dattiumappdb.cxlqgh9vjio0.us-east-2.rds.amazonaws.com'
    user = 'postgres'
    pswrd = 'D4ttium1'
else:
    ip = '127.0.0.1'
    user = 'test'
    pswrd = 'test123'

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
df['id'] = list(range(len(df)))
df['label_S1'] = np.random.choice(3, len(df), p=[0.05, 0.15, 0.8])
df['label_S2'] = np.random.choice(3, len(df), p=[0.05, 0.15, 0.8])
df['label_S3'] = np.random.choice(3, len(df), p=[0.05, 0.15, 0.8])
df['label'] = df['label_S1'] + df['label_S2'] + df['label_S3']
df['product'] = np.random.choice(3, len(df), p=[0.3334, 0.3333, 0.3333])
df['quality'] = np.random.choice(3, len(df), p=[0.3333, 0.3333, 0.3334])

##############################################################################
#                               03_LOAD                                      #
##############################################################################
# Conexion creation to server (192.168.1.33) database, DattiumApp; user=test; pswd=test123
server_conn = create_engine('postgresql://{}:{}@{}:5432/DattiumApp'.format(user, pswrd, ip))
# Load transformed DataFrame to server
df.to_sql(name='signals', con=server_conn, if_exists='replace')