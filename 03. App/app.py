#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 11:40:57 2020

@author: albertoyanguasrovira
"""

# -*- coding: utf-8 -*-
import os
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_auth
from sqlalchemy import create_engine

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#EFEFEF'
}

app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}

GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 1000)

USERNAME_PASSWORD_PAIRS = [
    ['test', 'test123'],['jamesbond', '007']
]

auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS)

app.layout = html.Div(style={'backgroundColor': app_color['graph_bg']}, children=[
    # header
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
            )
    ], className='header'),
    

    # html.Div(children='Dash: A web application framework for Python.', style={
    #     'textAlign': 'center',
    #     'color': colors['text']
    # }),
    
    # Signal plot
    html.Div([
        html.H3(
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
    ]),
])

@app.callback(
    Output("signal", "figure"), [Input("signal-update", "n_intervals")]
)
def gen_signal(interval):
    """
    Generate the signal graph.
    :params interval: update the graph based on an interval
    """
    
    # total_time = get_current_time()
    server_conn = create_engine('postgresql://test:test123@192.168.1.33:5432/DattiumApp')
    df = pd.read_sql(('SELECT * FROM signals LIMIT 100 OFFSET %s' % (interval)), server_conn)
    trace = dict(
        type="scatter",
        y=df["Amina Flow"],
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
        font={"color": "#fff"},
        height=700,
        xaxis={
            "range": [0, 100],
            "showline": True,
            "zeroline": False,
            "fixedrange": True,
            "tickvals": [0, 25, 50, 75, 100],
            "ticktext": ["100", "75", "50", "25", "0"],
            "title": "Time Elapsed (hours)",
        },
        yaxis={
            "range": [
                min(0, min(df["Amina Flow"])),
                max(45, max(df["Amina Flow"])),
            ],
            "showgrid": True,
            "showline": True,
            "fixedrange": True,
            "zeroline": False,
            "gridcolor": app_color["graph_line"],
            "nticks": max(6, round(df["Amina Flow"].iloc[-1] / 10)),
        },
    )

    return dict(data=[trace], layout=layout)

if __name__ == '__main__':
    app.run_server(debug=True)