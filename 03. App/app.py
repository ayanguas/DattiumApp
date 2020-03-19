#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 11:40:57 2020

@author: albertoyanguasrovira
"""

import os
import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_auth
from sqlalchemy import create_engine
import json
from textwrap import dedent as d
from numpy.random import randint

postgre_ip = '127.0.0.1'

external_stylesheets =  [dbc.themes.BOOTSTRAP] #['https://codepen.io/chriddyp/pen/bWLwgP.css'] #["https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"]

colors = {
    'background': '#EFEFEF',
    'text': '#111144'
}

app_color = {"graph_bg": "#HFHFHF", "graph_line": "#007ACE"}


def get_columns(df, seccion):
    columns_fallo=columns[randint(len(columns), size=(randint(5)), dtype='int')]
    columns_desviacion=columns[randint(len(columns), size=(randint(5)), dtype='int')]
    return [columns_fallo, columns_desviacion]

def get_cards_layout(columns):
    children = []
    if len(columns)>0:
        i = 1
        for column in columns:
            children.append(dbc.ListGroupItem(column, className='text-center', id='list-item-{}'.format(i)))
            i+=1
        return children
    else:
        return dbc.ListGroupItem("No hay ningúna señal desviada", className='text-center', color='success', id='list-item-1')

server_conn = create_engine('postgresql://test:test123@{}:5432/DattiumApp'.format(postgre_ip))
df_raw = pd.read_sql(('SELECT * FROM signals'), server_conn)
columns = np.array(list(df_raw.columns)[1:len(df_raw.columns)])

# Evento para el refresco del grafico principal
GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 3000)

USERNAME_PASSWORD_PAIRS = [
    ['test', 'test123'],['jamesbond', '007']
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True
auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS)
server = app.server

app.layout = html.Div([
    dcc.Store(id='store-p2-layout'),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

navbar = dbc.Navbar([
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            html.Img(src=app.get_asset_url("logo-dattium-navbar.png"),\
                                     height="30px"),
            href="/",
            className='float-right'
        ),
    ])

page_1_layout = html.Div([
    # Barra de navegación de la aplicación
    navbar,
    
    # Content
    dbc.Container([
        # PLot of general view of plant
        html.Div([
            html.H1(
                id='header-plant-plot',
                children='Plant stability',
                style={
                    'textAlign': 'center',
                    'color': colors['text'],
                    'margin-top': '30px'
                    },
            ),
            dcc.Graph(
                id="plant-plot",
                figure=dict(
                    layout=dict(
                        plot_bgcolor=app_color["graph_bg"],
                        paper_bgcolor=app_color["graph_bg"],
                    )
                ),
            ),
            dcc.Interval(
                id="signal-update",
                interval=int(GRAPH_INTERVAL),
                n_intervals=0,
            ), 
        ]), 
        
        html.Div([
            html.Img(src=app.get_asset_url("plant-diagram.png"), className='mx-auto d-block')
        ], className = 'row'), 
    ], className = 'container'),   
    html.Br(),
    dcc.Link('Go to page 1', href='/page-1'),
])

@app.callback(
    [Output("plant-plot", "figure")], 
    [Input("signal-update", "n_intervals")]
)
def gen_signal(interval):
    """
    Generate the signal graph.
    :params interval: update the graph based on an interval
    """
    column = 'label'
    
    # total_time = get_current_time()
    
    df = pd.read_sql(('SELECT * FROM signals LIMIT 100 OFFSET %s' % (interval)), server_conn)
    trace = dict(
        type="scatter",
        ids=df.index,
        y=df[column],
        line={"color": "dimgray"},
        hoverinfo='text',
        hovertext = ['<b>Id</b>: {}<br><b>All</b>: {}<br><b>S1</b>: {}<br><b>S2</b>: {}<br><b>S3</b>: {}'.format(row['id'],row['label'], row['label_S1'], row['label_S2'], row['label_S3']) \
                     for index, row in df.iterrows()],
        # error_y={
        #     "type": "data",
        #     "array": df["SpeedError"],
        #     "thickness": 1.5,
        #     "width": 2,
        #     "color": "#B4E8FC",
        # },
        mode="markers",
        name='Label',
    )
    
    trace2 = dict(
        type='rect', 
        x0=0, 
        x1=100, 
        y0=4, 
        y1=6, 
        fillcolor='green', 
        layer='below',
    )
    
    trace3 = dict(
        type='rect', 
        x0=0, 
        x1=100, 
        y0=0, 
        y1=4, 
        fillcolor='red', 
        layer='below',
    )

    layout = dict(
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        font={"color": colors['text']},
        height=700,
        xaxis={
            "range": [0, 100],
            "showline": False,
            "zeroline": False,
            "fixedrange": True,
            "tickvals": [0, 25, 50, 75, 100],
            "ticktext": ["100", "75", "50", "25", "0"],
            "title": "Time Elapsed (hours)",
            "ylabel": column,
        },
        yaxis={
            "range": [
                0,# df[column].min() - 0.1*(df[column].max() - df[column].min()), #min(200, min(df[column])),
                6.5# df[column].max() + 0.1*(df[column].max() - df[column].min()), #max(700, max(df[column])),
            ],
            "showgrid": False,
            "showline": False,
            "fixedrange": True,
            "zeroline": False,
            "gridcolor": app_color["graph_line"],
            "nticks": 7 #max(50, round(df[column].iloc[-1] / 10)),
        },
        shapes=[
            dict(
                type='rect', 
                x0=0, 
                x1=100, 
                y0=4, 
                y1=6.5, 
                fillcolor='lightgreen', 
                layer='below',
                linewidth=0,
            ),
            dict(
                type='rect', 
                x0=0, 
                x1=100, 
                y0=0, 
                y1=4, 
                fillcolor='LightSalmon', 
                layer='below',
                linewidth=0,
            ),
            dict(
                type="line",
                x0=0,
                y0=4,
                x1=100,
                y1=4,
                line=dict(
                    color="Salmon",
                    width=4,
            
                ),
                layer='below'
            )
        ],
    )

    return [dict(data=[trace, trace2, trace3], layout=layout)]

@app.callback([Output('store-p2-layout', 'data'), Output('url', 'pathname')],
              [Input('plant-plot', 'clickData')])
def change_page(click_data):
    des_s1 =  dbc.ListGroupItem("No hay ningúna señal desviada", id="desviacion-s1-item", className='text-center')
    if click_data is not None:
        if 'points' in click_data.keys():
            if 'id' in click_data['points'][0].keys():
                point_id = click_data['points'][0]['id']
                selected_data = pd.read_sql(('SELECT * FROM signals WHERE id=%s' % (point_id)), server_conn)
                [col_fal_s1, col_des_s1] = get_columns(selected_data, 's1')
                [col_fal_s2, col_des_s2] = get_columns(selected_data, 's2')
                des_s1 = get_cards_layout(col_des_s1)
                fal_s1 = get_cards_layout(col_fal_s1)
                des_s2 = get_cards_layout(col_des_s2)
                fal_s2 = get_cards_layout(col_fal_s2)
                print(des_s1)
                print(click_data['points'][0]['id'])
    return [{'des_s1': (des_s1), 'fal_s1': (fal_s1)}, '/page-1']

page_2_layout = html.Div([
    navbar,
    dbc.Tabs([
        dbc.Tab(label='S1', children = [
            html.Img(src=app.get_asset_url("plant-s1.png"), className='mx-auto d-block'),
            html.H1('Seccion 1', id='header-s1', className='text-center'),
            html.Div([
                html.Div(className='col-1'),
                dbc.Card([
                    html.Br(),
                    html.H2('Desviaciones', className='text-center'),
                    html.Br(),
                    dbc.ListGroup(id='list-des-s1'),
                    # dbc.ListGroup(id='list-desviaciones-s1'),  
                    html.Br()
                ], className='col-4', color='warning', outline=True),                
                html.Div(className='col-2 rounded'),
                dbc.Card([
                    html.Br(),
                    html.H2('Fallos de registro/sensor', className='text-center'),
                    html.Br(),
                    dbc.ListGroup(id='list-fal-s1'), 
                    html.Br()
                ], className='col-4', color='danger', outline=True),
                html.Div(className='col-1'),
            ], className='row'),
        ]),
        dbc.Tab(label='S2', children = [
            html.Img(src=app.get_asset_url("plant-s2.png"), className='mx-auto d-block'),
            html.H1('Seccion 2', id='header-s2', className='text-center'),
            html.Div([
                html.Div([
                    html.H2('Desviaciones', className='text-center'),
                    dbc.ListGroup(children=[
                        dbc.ListGroupItem(
                            "Button", id="desviacion-s2-item", n_clicks=0, action=True, className='text-center',
                        ),
                    ], id='list-desviaciones-s2'),     
                ], className='col-6'),
                html.Div([
                    html.H2('Fallos de registro/sensor', className='text-center'),
                    dbc.ListGroup(children=[
                        dbc.ListGroupItem(
                            "Button", id="fallo-s2-item", n_clicks=0, action=True, className='text-center',
                        ),
                    ], id='list-fallos-s2'),     
                ], className='col-6'),
                
            ], className='row'),
        ]),
    ], id='tab-seccions'),
    html.Br(),
    dcc.Link('Go back to home', href='/')
])
@app.callback(Output('list-des-s1', 'children'),
              [Input('store-p2-layout', 'modified_timestamp')],
              [State('store-p2-layout', 'data')])
def modify_lists_p2(timestamp, data):
    print('hey')
    no_data = dbc.ListGroupItem("No hay ningúna señal desviada", id="desviacion-s1-item", color='success', className='text-center')
    return_data_0 = no_data
    return_data_1 = no_data
    if 'des_s1' in data.keys():
        return_data_0 = data['des_s1']
    if 'fal_s1' in data.keys():
        return_data_1 = data['fal_s1']
    return return_data_0
    
    
# Update the index
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-1':
        return page_2_layout
    else:
        return page_1_layout
    # You could also return a 404 "URL not found" page here

if __name__ == '__main__':
    app.run_server(debug=False)