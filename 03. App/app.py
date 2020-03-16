#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 11:40:57 2020

@author: albertoyanguasrovira
"""

import os
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_auth
from sqlalchemy import create_engine
import json
from textwrap import dedent as d

ip = '127.0.0.1'

external_stylesheets =  [dbc.themes.BOOTSTRAP] #['https://codepen.io/chriddyp/pen/bWLwgP.css'] #["https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"]

server_conn = create_engine('postgresql://test:test123@{}:5432/DattiumApp'.format(ip))
df_raw = pd.read_sql(('SELECT * FROM signals'), server_conn)
columns = list(df_raw.columns)[1:len(df_raw.columns)]

USERNAME_PASSWORD_PAIRS = [
    ['test', 'test123'],['jamesbond', '007']
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS)
server = app.server

app.layout = dbc.Container([
    # Barra de navegación de la aplicación
    dbc.Navbar([
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=app.get_asset_url("Logotipo-Dattium_13x46.png"), height="30px")),
                    #dbc.Col(dbc.NavbarBrand("Navbar", className="ml-2")),
                ],
                align="center",
                no_gutters=True,
            ),
            href="https://www.dattium.com",
        ),  
    ], color='light', dark=True),
    
])



if __name__ == '__main__':
    app.run_server(debug=False)