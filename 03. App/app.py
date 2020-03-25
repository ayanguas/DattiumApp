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

# Configurar ip para acceder a los datos de postgreSQL
postgre_ip = '127.0.0.1'

# Script con las configuraciones CSS de Bootstrap
external_stylesheets =  [dbc.themes.BOOTSTRAP] #['https://codepen.io/chriddyp/pen/bWLwgP.css'] #["https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css"]

colors = {
    'background': '#EFEFEF',
    'text': '#111144'
}

app_color = {"graph_bg": "#HFHFHF", "graph_line": "#007ACE"}

# Funcion que nos devuelve (aleatoriamente) las columnas que se desvian o tienen algun fallo
def get_columns(df, seccion):
    if seccion == 's1':
        columns = columns_s1
    elif seccion == 's2':
        columns = columns_s2
    else:
        columns= columns
    columns_fallo=columns[randint(len(columns), size=(randint(5)), dtype='int')]
    columns_desviacion=columns[randint(len(columns), size=(randint(5)), dtype='int')]
    return [columns_fallo, columns_desviacion]

# A partir de las columnas seleccionadas nos devuelve el layout para mostrar en la app
def get_cards_layout(columns, desviaciones):
    children = []
    if len(columns)>0:
        i = 1
        for column in columns:
            children.append(dbc.ListGroupItem(column, className='text-center', id='list-item-{}'.format(i)))
            i+=1
        return children
    else:
        if desviaciones:
            return dbc.ListGroupItem("No hay ningúna señal desviada", className='text-center',\
                                     color='success', id='list-item-1')
        else:
            return dbc.ListGroupItem("No hay ningúna señal con fallos de registro/sensor",\
                                     className='text-center', color='success', id='list-item-1')

# Conexion a la BBDD postgreSQL con el usuario test, contraseña test123 y en la BBDD DattiumApp        
server_conn = create_engine('postgresql://test:test123@{}:5432/DattiumApp'.format(postgre_ip))
# Extraemos en un DF todos los datos de la BBDD
df_raw = pd.read_sql(('SELECT * FROM signals'), server_conn)
# Array con el nombre de las señales que vamos a utilizar
columns = np.array(list(df_raw.columns)[1:len(df_raw.columns)])
columns_s1 = columns[0:11]
columns_s2 = columns[11:23]

# Evento para el refresco del grafico principal
GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 3000)

# User/Password para acceder a la app
USERNAME_PASSWORD_PAIRS = [
    ['test', 'test123'],['jamesbond', '007']
]

# Configuración de DASH
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True
auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS)
server = app.server

# Layout de la app
app.layout = html.Div([
    # Store, sirve para guardar datos y poder acceder a ellos entre paginas
    dcc.Store(id='store-p2-layout'),
    dcc.Store(id='store-id-clicked'),
    # Sirve para poder crear distintas paginas www.dattiumapp.com/page-1 o www.dattiumapp.com/page-2
    dcc.Location(id='url', refresh=False),
    # Contenido de las paginas
    html.Div(id='page-content')
])

# Barra de navegacion de la aplicacion
navbar = dbc.Navbar([
        html.A(
            # Imagen con el logo de Dattium que nos llevara a la página principal de la App
            # Use row and col to control vertical alignment of logo / brand
            html.Img(src=app.get_asset_url("logo-dattium-navbar.png"),\
                                     height="30px"),
            href="/",
            className='float-right'
        ),
    ])

# Pagina 1, imagen de la planta y un gráfico general con el comportamiento de esta
page_1_layout = html.Div([
    # Barra de navegación de la aplicación
    navbar,
    
    # Content
    dbc.Container([
        # PLot of general view of plant
        html.Div([
            # Titulo del gráfico
            html.H1(
                id='header-plant-plot',
                children='Plant stability',
                style={
                    'textAlign': 'center',
                    'color': colors['text'],
                    'margin-top': '30px'
                    },
            ),
            # Boton de pausa para pausar el gráfico
            dbc.Button("Stop", id="example-button", className="mr-2"),
            html.Br(),
            # Gráfico general del comportamiento de la planta
            dcc.Graph(
                id="plant-plot",
                figure=dict(
                    layout=dict(
                        plot_bgcolor=app_color["graph_bg"],
                        paper_bgcolor=app_color["graph_bg"],
                    )
                ),
            ),
            # Interval, sirve para ir actualizando el gráfico cada GRAPH_INTERVAL ms
            dcc.Interval(
                id="signal-update",
                interval=int(GRAPH_INTERVAL),
                n_intervals=0,
            ), 
        ]), 
        # Imagen de la planta
        html.Div([
            html.Img(src=app.get_asset_url("plant-diagram.png"), className='mx-auto d-block')
        ], className = 'row'), 
    ], className = 'container'),   
])

# Callback que pausa la actualización automática del gráfico
@app.callback(
    [Output("signal-update", "disabled"), Output("example-button", "children")], 
    [Input("example-button", "n_clicks")],
    [State("signal-update", "disabled")]
)
def enable_update(n, disabled):
    children = "Play"
    if n is not None:
        if disabled:
            children="Stop"
        return (not disabled), children

# Callback que actualiza el gráfica cada X segundos
@app.callback(
    [Output("plant-plot", "figure")], 
    [Input("signal-update", "n_intervals")]
)
def gen_signal(interval):
    """
    Generate the signal graph.
    :params interval: update the graph based on an interval
    """
    # Columna del df que se va a visualizar en el gráfico
    column = 'label'
    
    # total_time = get_current_time()
    # Hacemos una consulta a postgreSQL que nos devuelve las 100 primeras filas con un offset que incrementa cada GRAPH_INTERVALS ms
    df = pd.read_sql(('SELECT * FROM signals LIMIT 100 OFFSET %s' % (interval)), server_conn)
    # Scatter plot con del label de comportamiento de la planta
    trace = dict(
        type="scatter",
        ids=df.index,
        y=df[column],
        line={"color": "dimgray"},
        hoverinfo='text',
        # Texto que se muestra al pasar el cursor por encima de un punto
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
        
    # Opciones de estilo del gráfico
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
            # Rectangulo de color verde para estilizar el scatter
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
            # Rectangulo de color rojo para estilizar el scatter
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
            # Linea de color rojo para estilizar el scatter
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

    return [dict(data=[trace], layout=layout)]

# Callback al clicar en un punto del gráfico, guarda en los Store el id del punto y el layout de las señales
# que se van a mostrar como desviaciones/fallos
@app.callback([Output('store-p2-layout', 'data'), Output('url', 'pathname'), Output('store-id-clicked', 'data')],
              [Input('plant-plot', 'clickData')])
def change_page(click_data):
    des_s1 =  dbc.ListGroupItem("No hay ningúna señal desviada", id="desviacion-s1-item", className='text-center')
    point_id = -1
    if click_data is not None:
        if 'points' in click_data.keys():
            if 'id' in click_data['points'][0].keys():
                point_id = click_data['points'][0]['id']
                selected_data = pd.read_sql(('SELECT * FROM signals WHERE id=%s' % (point_id)), server_conn)
                [col_fal_s1, col_des_s1] = get_columns(selected_data, 's1')
                [col_fal_s2, col_des_s2] = get_columns(selected_data, 's2')
                des_s1 = get_cards_layout(col_des_s1, True)
                fal_s1 = get_cards_layout(col_fal_s1, False)
                des_s2 = get_cards_layout(col_des_s2, True)
                fal_s2 = get_cards_layout(col_fal_s2, False)
    return [{'des_s1': (des_s1), 'fal_s1': (fal_s1), 'des_s2': (des_s2), 'fal_s2': (fal_s2)}, '/page-1', {'id': point_id}]

# Página 2, dividida en dos tabs S1 y S2, en cada una de ellas tenemos la imagen de la seccion, la lista de 
# señales desviadas, la lista de las señales con fallos en el sensor/registro, la señal sobre el tiempo,
# y un histograma (con datos antiguos y un periodo de datos nuevos) junto a un dropdown para seleccionar las
# señales
page_2_layout = html.Div([
    # Barra de navegación de la App
    navbar,
    # Dividimos la página en dos mediante tabs, para la S1 y S2
    dbc.Tabs([
        # Tab S1
        dbc.Tab(label='S1', children = [
            # Imagen
            html.Img(src=app.get_asset_url("plant-s1.png"), className='mx-auto d-block'),
            # Titulo seccion
            html.H1('Seccion 1', id='header-s1', className='text-center'),
            # Listas de desviacion y fallos de registro/sensor S1
            html.Div([
                 # Lista de desviacion S1
                html.Div(className='col-1'),
                dbc.Card([
                    html.Br(),
                    html.H2('Desviaciones', className='text-center'),
                    html.Br(),
                    dbc.ListGroup(id='list-des-s1'),
                    html.Br()
                ], className='col-4', color='warning', outline=True),  
                 # Lista de fallos de registro/sensor S1
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
            html.Br(),
            # Plot señal + histograma S1 
            dcc.Dropdown(
                id="signal-dropdown-s1",
                options=[{'label': x, 'value': x} for x in columns_s1],
                value='Amina Flow',
                style={
                    'color': colors['text']
                },
            ),
            html.Div([
                # Plot señal S1
                html.Div([
                        html.H3(
                            id='header-signal-plot-s1',
                            children='Signal plot',
                            style={
                                'textAlign': 'center',
                                'color': colors['text']
                                }
                        ),
                        dcc.Graph(
                            id="signal-s1",
                            figure=dict(
                                layout=dict(
                                    plot_bgcolor=app_color["graph_bg"],
                                    paper_bgcolor=app_color["graph_bg"],
                                )
                            ),
                        ),
                    ],className='signal-plot col-7'),
                # Plot histograma S1
                html.Div([
                    html.H3(
                            id='header-histogram-s1',
                            children='Histogram',
                            style={
                                'textAlign': 'center',
                                'color': colors['text']
                            }
                        ),
                        dcc.Graph(
                            id="histogram-s1",
                            figure=dict(
                                layout=dict(
                                    barmode='overlay',
                                    plot_bgcolor=app_color["graph_bg"],
                                    paper_bgcolor=app_color["graph_bg"],
                                )
                            ),
                        ),
                    ],className='histogram-plot col-5'),
            ], id='graficos-s1', className='row'),
        ]),
        # Tab S2
        dbc.Tab(label='S2', children = [
            # Imagen de la seccion
            html.Img(src=app.get_asset_url("plant-s2.png"), className='mx-auto d-block'),
            # Titulo de la seccion
            html.H1('Seccion 2', id='header-s2', className='text-center'),
            # Listas de desviacion y fallos de registro/sensor S1
            html.Div([
                # Lista de desviacion
                html.Div(className='col-1'),
                dbc.Card([
                    html.Br(),
                    # Titulo de la lista
                    html.H2('Desviaciones', className='text-center'),
                    html.Br(),
                    # Lista
                    dbc.ListGroup(id='list-des-s2'),
                    # dbc.ListGroup(id='list-desviaciones-s1'),  
                    html.Br()
                ], className='col-4', color='warning', outline=True), 
                # Lista de fallos de registro/sensor S1
                html.Div(className='col-2 rounded'),
                dbc.Card([
                    html.Br(),
                    # Titulo de la lista
                    html.H2('Fallos de registro/sensor', className='text-center'),
                    html.Br(),
                    # Lista
                    dbc.ListGroup(id='list-fal-s2'), 
                    html.Br()
                ], className='col-4', color='danger', outline=True),
                html.Div(className='col-1'),
            ], className='row'),
            html.Br(),
            # Plot señal + histograma S2 
            dcc.Dropdown(
                id="signal-dropdown-s2",
                options=[{'label': x, 'value': x} for x in columns_s2],
                value='Amina Flow',
                style={
                    'color': colors['text']
                },
            ),
            html.Div([
                # Plot señal S1
                html.Div([
                    # Titulo de la señal
                    html.H3(
                        id='header-signal-plot-s2',
                        children='Signal plot',
                        style={
                            'textAlign': 'center',
                            'color': colors['text']
                            }
                    ),
                    # Grafico de la señal
                    dcc.Graph(
                        id="signal-s2",
                        figure=dict(
                            layout=dict(
                                plot_bgcolor=app_color["graph_bg"],
                                paper_bgcolor=app_color["graph_bg"],
                            )
                        ),
                    ),
                ],className='signal-plot col-7'),
                # Plot histograma S1
                html.Div([
                    html.H3(
                            id='header-histogram-s2',
                            children='Histogram',
                            style={
                                'textAlign': 'center',
                                'color': colors['text']
                            }
                        ),
                        dcc.Graph(
                            id="histogram-s2",
                            figure=dict(
                                layout=dict(
                                    barmode='overlay',
                                    plot_bgcolor=app_color["graph_bg"],
                                    paper_bgcolor=app_color["graph_bg"],
                                )
                            ),
                        ),
                    ],className='histogram-plot col-5'),
            ], id='graficos-s2', className='row'),
        ]),
    ], id='tab-seccions'),
    html.Br(),
    dcc.Link('Go back to home', href='/')
])

# Callback que actualiza la lista de desviaciones de S1
@app.callback(Output('list-des-s1', 'children'),
              [Input('store-p2-layout', 'modified_timestamp')],
              [State('store-p2-layout', 'data')])
def modify_lists_des_s1(timestamp, data):
    no_data = dbc.ListGroupItem("No hay ningúna señal desviada", color='success', className='text-center')
    if data is not None:
        return_data = no_data
        if 'des_s1' in data.keys():
            return_data = data['des_s1']
        return return_data
    else: 
        return no_data

# Callback que actualiza la lista de fallos de S1
@app.callback(Output('list-fal-s1', 'children'),
              [Input('store-p2-layout', 'modified_timestamp')],
              [State('store-p2-layout', 'data')])
def modify_lists_fal_s1(timestamp, data):
    no_data = dbc.ListGroupItem("No hay ningúna señal con fallos de registro/sensor",\
                                color='success', className='text-center')
    if data is not None:
        return_data = no_data
        if 'fal_s1' in data.keys():
            return_data = data['fal_s1']
        return return_data
    else: 
        return no_data

# Callback que actualiza la lista de desviaciones de S2
@app.callback(Output('list-des-s2', 'children'),
              [Input('store-p2-layout', 'modified_timestamp')],
              [State('store-p2-layout', 'data')])
def modify_lists_des_s2(timestamp, data):
    no_data = dbc.ListGroupItem("No hay ningúna señal desviada", color='success', className='text-center')
    if data is not None:
        return_data = no_data
        if 'des_s2' in data.keys():
            return_data = data['des_s2']
        return return_data
    else: 
        return no_data

# Callback que actualiza la lista de fallos de S2
@app.callback(Output('list-fal-s2', 'children'),
              [Input('store-p2-layout', 'modified_timestamp')],
              [State('store-p2-layout', 'data')])
def modify_lists_fal_s2(timestamp, data):
    no_data = dbc.ListGroupItem("No hay ningúna señal con fallos de registro/sensor",\
                                color='success', className='text-center')
    if data is not None:
        return_data = no_data
        if 'fal_s2' in data.keys():
            return_data = data['fal_s2']
        return return_data
    else: 
        return no_data

# Callback que actualiza el plot y el histograma de la señal al cambiar de señal con el dropdown de S1
@app.callback(
    [Output("signal-s1", "figure"), Output("histogram-s1", "figure")], 
    [Input("signal-dropdown-s1", "value")],
    [State('store-id-clicked', 'data')]
)
def gen_signal_s1(column, id_data):
    
    # Query por si no se ha seleccionado ningun punto devuelve los 1000 primeros puntos
    df = pd.read_sql('SELECT * FROM signals LIMIT 1000 OFFSET 0', server_conn)
    
    # Si se ha seleccionado punto:
    if id_data is not None:
        if 'id' in id_data.keys():
            # Query que devuelve a partir de una id las 1000 muestras anteriores
            df = pd.read_sql(('SELECT * FROM signals WHERE id>{} AND id<={}'.format(id_data['id']-1000, id_data['id'])), server_conn)
    
    # Scatter plot S1
    trace = dict(
        type="scatter",
        y=df_raw[column],
        line={"color": "#42C4F7"},
        mode="lines",
    )
    
    # Scatter Layout S1
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
                df_raw[column].min() - 0.1*(df_raw[column].max() - df_raw[column].min()), 
                df_raw[column].max() + 0.1*(df_raw[column].max() - df_raw[column].min()),
            ],
            "showgrid": True,
            "showline": True,
            # "fixedrange": True,
            "zeroline": False,
            "gridcolor": app_color["graph_line"],
            "nticks": 20
        },
    )
    
    # Datos historicos del histograma S1
    trace2 = dict(
        type="histogram",
        name='Historical',
        x=df_raw[column],
        xbins=10,
        bingroup=1,
        histnorm='probability',
        label='historical',
    )
    
    # Datos seleccionados con la id para el histograma S1
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
    
    # Layout del histograma S1
    layout2=dict(
        barmode='overlay',
        height=700,
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        font={"color": colors['text']},
    )

    return [dict(data=[trace], layout=layout), dict(data=[trace2, trace3], layout=layout2)]

# Callback que actualiza el plot y el histograma de la señal al cambiar de señal con el dropdown de S2
@app.callback(
    [Output("signal-s2", "figure"), Output("histogram-s2", "figure")], 
    [Input("signal-dropdown-s2", "value")],
    [State('store-id-clicked', 'data')]
)
def gen_signal_s1(column, id_data):
    # Query por si no se ha seleccionado ningun punto devuelve los 1000 primeros puntos
    df = pd.read_sql('SELECT * FROM signals LIMIT 10000 OFFSET 0', server_conn)
    
    # Si se ha seleccionado punto:
    if id_data is not None:
        if 'id' in id_data.keys():
            # Query que devuelve a partir de una id las 1000 muestras anteriores
            df = pd.read_sql(('SELECT * FROM signals WHERE id>{} AND id<={}'.format(id_data['id']-1000, id_data['id'])), server_conn)
    
    # Scatter plot S2
    trace = dict(
        type="scatter",
        y=df_raw[column],
        line={"color": "#42C4F7"},
        mode="lines",
    )

    # Scatter Layout S2
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
                df_raw[column].min() - 0.1*(df_raw[column].max() - df_raw[column].min()), 
                df_raw[column].max() + 0.1*(df_raw[column].max() - df_raw[column].min()),
            ],
            "showgrid": True,
            "showline": True,
            # "fixedrange": True,
            "zeroline": False,
            "gridcolor": app_color["graph_line"],
            "nticks": 20
        },
    )
    
    # Datos historicos del histograma S2
    trace2 = dict(
        type="histogram",
        name='Historical',
        x=df_raw[column],
        xbins=10,
        bingroup=1,
        histnorm='probability',
        label='historical',
    )
    
    # Datos seleccionados con la id para el histograma S2
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
    
    # Layout del histograma S1
    layout2=dict(
        barmode='overlay',
        height=700,
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        font={"color": colors['text']},
    )

    return [dict(data=[trace], layout=layout), dict(data=[trace2, trace3], layout=layout2)]

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