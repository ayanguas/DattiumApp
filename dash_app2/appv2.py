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

ip = '127.0.0.1' #192.168.1.37

external_stylesheets =  [dbc.themes.BOOTSTRAP] #['https://codepen.io/chriddyp/pen/bWLwgP.css'] #["https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"]

server_conn = create_engine('postgresql://test:test123@{}:5432/DattiumApp'.format(ip))
df_raw = pd.read_sql(('SELECT * FROM signals'), server_conn)
columns = list(df_raw.columns)[1:len(df_raw.columns)]

colors = {
    'background': '#EFEFEF',
    'text': '#111144'
}

app_color = {"graph_bg": "#HFHFHF", "graph_line": "#007ACE"}

GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 1000)

USERNAME_PASSWORD_PAIRS = [
    ['test', 'test123'],['jamesbond', '007']
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS)
server = app.server

app.layout = dbc.Container([html.Div(style={'backgroundColor': app_color['graph_bg']}, children=[
    # header
    html.Div([
        html.Div([
            html.H1(
                children='Dattium App',
                style={
                    'textAlign': 'center',
                    'color': colors['text']
                }
            ),
            html.P(
                children='Visualizador de señales Dattium',
                style={
                    'textAlign': 'center',
                    'color': colors['text']
                }
            ),
        ], className='app_header_desc col-9'),
        html.Div([
            html.Img(
                src=app.get_asset_url("Logotipo-Dattium_fondo.png"),
                style={'width':'100%'},
                className="app_menu_img center",
            ),
        ], className='app_header_logo col-3'),      
    ], className='app_header row'),
    

    # html.Div(children='Dash: A web application framework for Python.', style={
    #     'textAlign': 'center',
    #     'color': colors['text']
    # }),
    
    # Graficos
    html.Div([
        dbc.Tabs([
            dbc.Tab(label='Graph1',children = [
                html.Div([
                    html.H3(
                        id='header-selector',
                        children='Signal selector',
                        style={
                            'textAlign': 'center',
                            'color': colors['text']
                            }
                    ),
                    dcc.Dropdown(
                        id="signal-dropdown",
                        options=[{'label': x, 'value': x} for x in columns],
                        value='Amina Flow',
                        style={
                            'color': colors['text']
                        },
                    ),
                ],className='selector col center'),
                html.Div([
                    # Signal plot
                    html.Div([
                        html.H3(
                            id='header-signal-plot',
                            children='Signal plot',
                            style={
                                'textAlign': 'center',
                                'color': colors['text']
                                }
                        ),
                        dcc.Graph(
                            id="signal",
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
                    ],className='signal-plot col-7'),
                    # Histograma
                    html.Div([
                        html.H3(
                            id='header-histogram',
                            children='Histogram',
                            style={
                                'textAlign': 'center',
                                'color': colors['text']
                            }
                        ),
                        dcc.Graph(
                            id="histogram",
                            figure=dict(
                                layout=dict(
                                    barmode='overlay',
                                    plot_bgcolor=app_color["graph_bg"],
                                    paper_bgcolor=app_color["graph_bg"],
                                )
                            ),
                        ),
                    ],className='histogram-plot col-5'),
                ], className='row')
            ],className='app-content'),
            
        dbc.Tab(label='Graph2', children = [
            html.Div([
                html.Div([
                        html.H3(
                            id='header-signal-plot2',
                            children='Signal plot',
                            style={
                                'textAlign': 'center',
                                'color': colors['text']
                                }
                        ),
                        dcc.Graph(
                            id="signal2",
                            figure=dict(
                                layout=dict(
                                    plot_bgcolor=app_color["graph_bg"],
                                    paper_bgcolor=app_color["graph_bg"],
                                )
                            ),
                        ),
                        dcc.Interval(
                            id="signal-update2",
                            interval=int(GRAPH_INTERVAL),
                            n_intervals=0,
                        ), 
                    ],className='signal-plot col-7'),
                html.Div([
                    html.H3(
                            id='header-histogram2',
                            children='Histogram',
                            style={
                                'textAlign': 'center',
                                'color': colors['text']
                            }
                        ),
                        dcc.Graph(
                            id="histogram2",
                            figure=dict(
                                layout=dict(
                                    barmode='overlay',
                                    plot_bgcolor=app_color["graph_bg"],
                                    paper_bgcolor=app_color["graph_bg"],
                                )
                            ),
                        ),
                    ],className='histogram-plot col-5'),
                ], className='row'),
            ]),
        ],style={'color': colors['text']}),
    ]),
],className='app-container')])

@app.callback(
    [Output("signal", "figure"), Output("histogram", "figure")], 
    [Input("signal-update", "n_intervals"), Input("signal-dropdown", "value")]
)
def gen_signal(interval, column):
    """
    Generate the signal graph.
    :params interval: update the graph based on an interval
    """
    # total_time = get_current_time()
    
    df = pd.read_sql(('SELECT * FROM signals LIMIT 100 OFFSET %s' % (interval)), server_conn)
    trace = dict(
        type="scatter",
        y=df[column],
        line={"color": "#42C4F7"},
        hoverinfo="skip",
        # error_y={
        #     "type": "data",
        #     "array": df["SpeedError"],
        #     "thickness": 1.5,
        #     "width": 2,
        #     "color": "#B4E8FC",
        # },
        mode="lines",
    )

    layout = dict(
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        font={"color": colors['text']},
        height=700,
        xaxis={
            "range": [0, 100],
            "showline": True,
            "zeroline": False,
            "fixedrange": True,
            "tickvals": [0, 25, 50, 75, 100],
            "ticktext": ["100", "75", "50", "25", "0"],
            "title": "Time Elapsed (hours)",
            "ylabel": column,
        },
        yaxis={
            "range": [
                df[column].min() - 0.1*(df[column].max() - df[column].min()), #min(200, min(df[column])),
                df[column].max() + 0.1*(df[column].max() - df[column].min()), #max(700, max(df[column])),
            ],
            "showgrid": True,
            "showline": True,
            "fixedrange": True,
            "zeroline": False,
            "gridcolor": app_color["graph_line"],
            "nticks": 20#max(50, round(df[column].iloc[-1] / 10)),
        },
    )
    
    trace2 = dict(
        type="histogram",
        name='Historical',
        x=df_raw[column],
        xbins=10,
        bingroup=1,
        histnorm='probability',
        label='historical',
    )
    trace3 = dict(
        type="histogram",
        name='Actual',
        x=df[column],
        bingroup=1,
        xbins=10,
        histnorm='probability',
        opacity=0.75,
        label='current',
    )
    layout2=dict(
        barmode='overlay',
        height=700,
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        font={"color": colors['text']},
    )

    return [dict(data=[trace], layout=layout), dict(data=[trace2, trace3], layout=layout2)]

@app.callback(
    [Output("signal2", "figure")], 
    [Input("signal-dropdown", "value")]
)
def gen_signal2(column):
    trace = dict(
        type="scatter",
        y=df_raw[column],
        line={"color": "#42C4F7"},
        # hoverinfo="skip",
        # error_y={
        #     "type": "data",
        #     "array": df_raw["SpeedError"],
        #     "thickness": 1.5,
        #     "width": 2,
        #     "color": "#B4E8FC",
        # },
        mode="lines",
    )

    layout = dict(
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        font={"color": colors['text']},
        height=700,
        xaxis={
            "showline": True,
            "zeroline": False,
            "fixedrange": False,
            "title": "Time Elapsed (hours)",
            "ylabel": column,
        },
        yaxis={
            "range": [
                df_raw[column].min() - 0.1*(df_raw[column].max() - df_raw[column].min()), #min(200, min(df_raw[column])),
                df_raw[column].max() + 0.1*(df_raw[column].max() - df_raw[column].min()), #max(700, max(df_raw[column])),
            ],
            "showgrid": True,
            "showline": True,
            # "fixedrange": True,
            "zeroline": False,
            "gridcolor": app_color["graph_line"],
            "nticks": 20#max(50, round(df_raw[column].iloc[-1] / 10)),
        },
    )

    return [dict(data=[trace], layout=layout)]


@app.callback(
    [Output("histogram2", "figure")], 
    [Input("signal-dropdown", "value"), Input("signal2","relayoutData")]
)
def gen_histo2(column, relayout):
    df_hist=pd.DataFrame(df_raw)
    minimum = df_hist[column].min()
    maximum = df_hist[column].max()
    rang = maximum-minimum
    
    if relayout is not None:
        if 'xaxis.range[0]' in relayout.keys():
            first = round(relayout['xaxis.range[0]'])
            last = round(relayout['xaxis.range[1]'])
            df_hist = df_hist.iloc[first:last, :]
            print(df_hist[column].max())
            print(relayout['xaxis.range[1]'])
            print(relayout['xaxis.range[0]'])
            print(df_hist[column].min())
    
    trace = dict(
        type="histogram",
        x=df_hist[column],
        xbins=dict(
                start=minimum,
                end=maximum,
                size=rang/10,
            ),
        # autobinx=False,
        # bingroup=1,
        histnorm='probability',
        label='Selected',
    )
    
    trace2 = dict(
        type="histogram",
        x=df_raw[column],
        opacity=0.001,
        visible=True,
        histnorm='probability',
    )
    
    layout=dict(
        barmode='overlay',
        height=700,
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        font={"color": colors['text']},
    )
    return [dict(data=[trace, trace2], layout=layout)]


if __name__ == '__main__':
    app.run_server(debug=False)