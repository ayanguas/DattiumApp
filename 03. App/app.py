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
from numpy.random import randint
from datetime import timedelta, datetime, date

#%%###########################################################################
#                            01. CONFIGURACIÓN                               #
##############################################################################

# Configurar ip para acceder a los datos de postgreSQL
postgre_ip = '127.0.0.1'

dark = True
    
# Script con las configuraciones CSS de Bootstrap
if dark:
    external_stylesheets =  [dbc.themes.DARKLY] #SLATE / DARKLY /SUPERHERO / BOOTSTRAP
    navbar_image = "logo-dattium-navbar-dark.png"
else:
    external_stylesheets =  [dbc.themes.BOOTSTRAP] #SLATE / DARKLY /SUPERHERO / BOOTSTRAP
    navbar_image = "logo-dattium-navbar.png"
    
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

if dark:
    graph_bg = '#303030'#272B30'
    text_color = '#AAAA9F'
    pp_bg_green = '#356437'
    pp_bg_red = '#653434'
    pp_mk_green = '#59C159'
    pp_mk_red = '#EC5550'
else:
    graph_bg = ''
    text_color = ''
    pp_bg_green = '#F7FAF0'
    pp_bg_red = '#F9E9E0'
    pp_mk_green = '#76B7B2'
    pp_mk_red = '#E15759'

colors = {
    'navbar': 'secondary',
    'title-bg': '#444444',
    'graph-bg': graph_bg,
    'text': text_color,
    'text-dropdown': '#3A3A3A',
    'plantplot-bg-green': pp_bg_green, # Plantplot Background Green
    'plantplot-bg-red': pp_bg_red, # Plantplot Background Red
    'plantplot-l-red': '#B31919', # Plantplot Line Red #E46B6B
    'plantplot-mk-green': pp_mk_green, # Plantplot Marker Green
    'plantplot-mk-red': pp_mk_red, # Plantplot Merker Red
    'histogram-act': '#FFA64D', # Histogram Actual
    'histogram-act-br': '#FF8C1A', # Histogram Actual Border
    'histogram-hist': '#4DA6FF', # Histogram Historical
    'histogram-hist-br': '#1A8CFF', # Histogram Historical Border
    'grid': '#636363', 
    'signal-line': '#FEC036',# Linea del gráfico de la señal
    'signal-marker': '#B31919',
}

# Parametros de configuración del texto de los gráficos
family_font = 'Arial, sans-serif' # Graph Text Font
size_font = 22 # Graph Text Size
size_font_cards = 18 # Graph Text Size
pp_size = '500px' # Plant plot graph size
summary_graph_size = '400px' # Summary graphs size

#%%###########################################################################
#                             02. FUNCIONES                                  #
##############################################################################

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
            children.append(dbc.ListGroupItem(column, className='text-center', \
                                              style={"color": colors['text'], "font-size": size_font_cards, \
                                                     "font-family": family_font,}, \
                                                  id='list-item-{}'.format(i)))
            i+=1
        return children
    else:
        if desviaciones:
            return dbc.ListGroupItem("No hay ningúna señal desviada", className='text-center',\
                                     color='success', style={"font-size": size_font_cards,\
                                                             "font-family": family_font,},\
                                         id='list-item-1')
        else:
            return dbc.ListGroupItem("No hay ningúna señal con fallos de registro/sensor",\
                                     className='text-center', style={"font-size": size_font_cards,\
                                                                     "font-family": family_font,}, color='success',\
                                         id='list-item-1')

# Función que devuelve el texto que ira dentro del recuadro de información de la barra seleccionada page-2
def get_card_info_layout(id_data, column):
    df = pd.read_sql('SELECT * FROM signals WHERE id={}'.format(id_data), server_conn)
    if len(df)==1:
        text = dcc.Markdown('''**ID**: {}  
                            **Date**: {}   
                            **{}**: {:.2f}  '''.format(df['id'].iloc[0], df['date'].iloc[0],\
                            column, df[column].iloc[0]), style={"color": colors['text'], \
                                                                          "font-size": size_font_cards, "font-family": family_font,})
    else:
        text = dcc.Markdown('''**ID**: -  
                            **Date**: -   
                            **-**: -  ''', style={"color": colors['text'], "font-size": size_font_cards, "font-family": family_font,})              
    return text

# Función que devuelve el trace y layout de plant-plot
def get_plant_plot(df):
    
    column = 'label'
    datemin1 = df['date'].min() - timedelta(hours=2)
    datemax1 = df['date'].max() + timedelta(hours=2)
    
    # Scatter plot con del label de comportamiento de la planta
    trace = dict(
        type="scatter",
        ids=df['id'],
        x=df['date'],
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
        marker=dict(
            color=[colors['plantplot-mk-green'] if x > 3 else colors['plantplot-mk-red'] for x in df['label']],
            size=10,
        ),
    )
        
    # Opciones de estilo del gráfico
    layout = dict(
        plot_bgcolor=colors["graph-bg"],
        paper_bgcolor=colors["graph-bg"],
        font={"color": colors['text'], "size": size_font, "family": family_font,},
        height=500,
        xaxis={
            "range": [datemin1, datemax1],
            "showline": False,
            "zeroline": False,
            "fixedrange": True,
            # "tickvals": [0, 25, 50, 75, 100],
            # "ticktext": ["100", "75", "50", "25", "0"],
            "title": "Time Elapsed (hours)",
            "ylabel": column,
            "automargin": True,
        },
        yaxis={
            "range": [
                0,# df[column].min() - 0.1*(df[column].max() - df[column].min()), #min(200, min(df[column])),
                6.5# df[column].max() + 0.1*(df[column].max() - df[column].min()), #max(700, max(df[column])),
            ],
            "tickvals": [1,2,3,4,5,6],
            "showgrid": False,
            "showline": False,
            "fixedrange": True,
            "zeroline": False,
            "gridcolor": colors["grid"],
            "nticks": 7, #max(50, round(df[column].iloc[-1] / 10)),
            "automargin": True,
        },
        shapes=[
            # Rectangulo de color verde para estilizar el scatter
            dict(
                type='rect', 
                x0=datemin1, 
                x1=datemax1, 
                y0=4, 
                y1=6.5, 
                fillcolor=colors['plantplot-bg-green'], 
                layer='below',
                linewidth=0,
            ),
            # Rectangulo de color rojo para estilizar el scatter
            dict(
                type='rect', 
                x0=datemin1, 
                x1=datemax1, 
                y0=0, 
                y1=4, 
                fillcolor=colors['plantplot-bg-red'], 
                layer='below',
                linewidth=0,
            ),
            # Linea de color rojo para estilizar el scatter
            dict(
                type="line",
                x0=datemin1,
                y0=4,
                x1=datemax1,
                y1=4,
                line=dict(
                    color=colors['plantplot-l-red'],
                    width=4,
            
                ),
                layer='below'
            )
        ],
    )
    return trace, layout

# Función que devuelve el trace y layout del gráfico de la señal
def get_signal_plot(df, column, id_data):
    # Signal Plot S1
    trace = dict(
        type="scatter",
        y=df[column],
        x=df['date'],
        line={"color": colors['signal-line']},
        mode="lines",
        name='Señal',
    )
    
    trace2 = dict(
        type="scatter",
        y=df[df['id']==id_data][column],
        x=df[df['id']==id_data]['date'],
        line={"color": colors['signal-marker']},
        mode="markers",
        marker=dict(symbol='cross', size=12),
        name='Seleccionado',
    )
    
    # Signal Layout S1
    layout = dict(
        plot_bgcolor=colors["graph-bg"],
        paper_bgcolor=colors["graph-bg"],
        font={"color": colors['text'], "size": size_font, "family": family_font,},
        height=700,
        xaxis={
            "showline": True,
            "zeroline": False,
            "fixedrange": False,
            "title": "Fecha",
            "ylabel": column,
        },
        yaxis={
            "range": [
                df[column].min() - 0.1*(df[column].max() - df[column].min()), 
                df[column].max() + 0.1*(df[column].max() - df[column].min()),
            ],
            "showgrid": True,
            "showline": True,
            # "fixedrange": True,
            "zeroline": False,
            "gridcolor": colors["grid"],
            "nticks": 10
        },
    )
    return trace, trace2, layout

# Función que devuelve los traces y layout del histograma
def get_histogram(df, column, id_data):
    # Datos historicos del histograma S1
    trace = dict(
        type="histogram",
        name='Historico',
        x=df_raw[column],
        nbins=10,
        bingroup=1,
        histnorm='percent',
        label='historical',
        marker={
            'line':{
                'width': 1,
                'color': colors['histogram-hist-br'],
            },
            'color': colors['histogram-hist'],
        },
    )
    
    # Datos seleccionados con la id para el histograma S1
    trace2 = dict(
        type="histogram",
        name='Actual',
        x=df[column],
        bingroup=1,
        nbins=10,
        histnorm='percent',
        opacity=0.75,
        label='current',
        marker={
            'line':{
                'width': 1,
                'color': colors['histogram-act-br'],
            },
            'color': colors['histogram-act'],
        },
    )
    
    # Layout del histograma S1
    layout=dict(
        barmode='overlay',
        height=700,
        plot_bgcolor=colors["graph-bg"],
        paper_bgcolor=colors["graph-bg"],
        font={"color": colors['text'], "size": size_font, "family": family_font,},
        shapes=[
            {
                'type':"line",
                # 'xref':df[df['id']==id_data['id']][column].iloc[0],
                'yref':'paper',
                'x0':df[df['id']==id_data][column].iloc[0],
                'y0':0,
                'x1':df[df['id']==id_data][column].iloc[0], 
                'y1':0.95,
                'line':dict(
                    color=colors['plantplot-l-red'],
                    width=4,
            
                ),
                # 'layer':'below'
            }
        ],
    )
    return trace, trace2, layout

# Devuelve una tabla en HTML a partir de un DF
def make_table(df):
    """ Return a dash definition of an HTML table for a Pandas dataframe """
    table = []
    for index, row in df.iterrows():
        html_row = []
        for i in range(len(row)):
            html_row.append(html.Td([row[i]]))
        if index%2 == 0:
            table.append(html.Tr(html_row))
        else:
            table.append(html.Tr(html_row, className='secondary'))
    return table

# Devuelve la tabla resumen por producto
def product_summary_table(df):
    # df = pd.read_sql(('SELECT * FROM signals'), server_conn)
    max_p = df.groupby('product').count()['id'].idxmax() # Producto más fabricado
    max_q = df.groupby('quality').count()['id'].idxmax() # Calidad más fabricada
    max_pq = df.groupby(['product', 'quality']).count()['id'].idxmax() # Producto-Calidad más fabricado
    fail_p = df[df['label']<4].groupby('product').count()['id'].idxmax() # Producto con más fallos
    fail_q = df[df['label']<4].groupby('quality').count()['id'].idxmax() # Calidad con más fallos
    fail_pq = df[df['label']<4].groupby(['product', 'quality']).count()['id'].idxmax() # Producto con más fallos
    df_table = pd.DataFrame(data=[['Producto + fabricado', 'Producto ' + str(max_p)],\
                                  ['Calidad + fabricada', 'Calidad ' + str(max_q)],\
                                  ['Producto/Calidad + fabricada', 'Producto ' + str(max_pq[0])+'/'+\
                                   'Calidad ' + str(max_pq[1])],
                                  ['Producto con + fallos', 'Producto ' + str(fail_p)],\
                                  ['Calidad con + fallos', 'Calidad ' + str(fail_q)],\
                                  ['Producto/Calidad con + fallos', 'Producto ' + str(fail_pq[0])+'/'+\
                                   'Calidad ' + str(fail_pq[1])]])
    product_table = make_table(df_table)
    return product_table

# Devuelve la tabla resumen por producto
def seccion_summary_table(df):
    seccions = ['S1', 'S2', 'S3']
    fail_s = 'S-'
    aux_fail_s = -1
    for seccion in seccions:
        if aux_fail_s < len(df[df[f'label_{seccion}']<1]):
            fail_s = seccion
    df_table = pd.DataFrame(data=[['Seccion con + fallos', fail_s]])
    seccion_table = make_table(df_table)
    return seccion_table
# Devuelve el layout de los tabs de reports
def summary_tab_layout(tab):
    if tab == 'products':
        table = product_summary_table(df_raw)
        data_bar = bar_graph_product_summary(df_raw, 'product')
        titulo_line_plot = 'Buenas por producto/calidad/mes'
        data_line = liner_graph_product_summary(df_raw, df_raw['product'].unique(), df_raw['quality'].unique())    
        buttons=[]
    else:
        table = seccion_summary_table(df_raw)
        data_bar = bar_graph_seccions_summary(df_raw)
        titulo_line_plot = 'Buenas por seccion/mes'
        data_line = liner_graph_seccions_summary(df_raw, 'S1')
        buttons=list([
            dict(
                args=[dict(y=[liner_graph_seccions_summary(df_raw, 'S1')[0]['y']])],
                label='S1',
                method='restyle',
            ),
            dict(
                args=[dict(y=[liner_graph_seccions_summary(df_raw, 'S2')[0]['y']])],
                label='S2',
                method='restyle'
            ),
            dict(
                args=[dict(y=[liner_graph_seccions_summary(df_raw, 'S3')[0]['y']])],
                label='S3',
                method='restyle',
            ),
        ])
                    
    return html.Div([ html.Br(),
            html.Div([
                # html.Div(className='col-1'),
                html.Div([
                    # html.Div(className='col-1'),
                    html.H2(f'Resumen de {tab}'),
                    dbc.Table(table, 
                               striped=True, 
                                # bordered=True, 
                               responsive=True,
                               hover=True,
                               dark=True,
                              className='table mt-5', #table-secondary
                              id=f'summary-table-{tab}')
                ], className='col-3 ml-4'),
                html.Div(className='col-1'),
                html.Div([
                    html.H4('Buenas vs. Malas', className='text-center'),
                    dcc.Graph(
                        id=f'bar-plot-{tab}',
                        figure=dict(
                            layout=dict(
                                plot_bgcolor=colors["graph-bg"],
                                paper_bgcolor=colors["graph-bg"],
                                font=dict(
                                    color = colors['text'],
                                    family = family_font,
                                ),
                            ),
                            data = data_bar,
                        ),
                    ),
                ], className='col-3'),
                html.Div(className='col-1'),
                html.Div([
                    html.H4(titulo_line_plot, className='text-center'),
                    dcc.Graph(
                        id=f'time-plot-{tab}',
                        figure=dict(
                            layout=dict(
                                plot_bgcolor=colors["graph-bg"],
                                paper_bgcolor=colors["graph-bg"],
                                font=dict(
                                    color = colors['text'],
                                    family = family_font,
                                ),
                                updatemenus = [
                                    dict(
                                        type = 'buttons',
                                        # direction = "left",
                                        buttons=buttons,
                                        # showactive=True,
                                        # xanchor="left",
                                        # yanchor="top"
                                        direction="right",
                                        pad={"r": 10, "t": 10},
                                        showactive=True,
                                        x=0.1,
                                        xanchor="left",
                                        y=1.1,
                                        yanchor="top"
                                    )
                                ],
                            ),
                            data = data_line
                        ),
                    ),
                ], className='col-3'),
            ], className='row'),])

# Devuelve el gráfico de barras de barras buenas/malas en funcion de una o varias columnas
def bar_graph_product_summary(df, column):
    todas = df.groupby('product').count()['id']
    buenas = df[df['label']>=4].groupby('product').count()['id']
    malas = df[df['label']<4].groupby('product').count()['id']
    trace = dict(
        type='bar',
        name='Buenas',
        x = ['Product ' + str(idx) for idx in todas.index],
        y = ((buenas/todas)*100).values,
        marker = dict(
            color = colors['plantplot-mk-green'], 
        ),
    )
    trace2 = dict(
        type='bar',
        name='Malas',
        x = ['Product ' + str(idx) for idx in todas.index],
        y = ((malas/todas)*100).values,
        marker = dict(
            color = colors['plantplot-mk-red'], 
        ),
    )
    
    return [trace, trace2]

def liner_graph_product_summary(df, product, quality):
    df['month'] = df['date'].apply(lambda x: datetime(x.year, x.month, 1))
    todas = df[(df['product'].isin(product)) & (df['quality'].isin(quality))].groupby('month').count()['id']
    buenas = df[(df['label']>=4) & (df['product'].isin(product)) & (df['quality'].isin(quality))].groupby('month').count()['id']
    trace = dict(
        type='line',
        x = todas.index,
        y = ((buenas/todas)*100).values,
    )
    return [trace]

# Devuelve el gráfico de barras de barras buenas/malas por seccion
def bar_graph_seccions_summary(df):
    secciones = ['S1', 'S2', 'S3']
    todas = []
    buenas = []
    malas = []
    for seccion in secciones:
        todas = np.append(todas, len(df))
        buenas = np.append(buenas, len(df[df[f'label_{seccion}']>=1]))
        malas = np.append(malas, len(df[df[f'label_{seccion}']<1]))

    trace = dict(
        type='bar',
        name='Buenas',
        x = secciones,
        y = ((buenas/todas)*100),
        marker = dict(
            color = colors['plantplot-mk-green'], 
        ),
    )
    trace2 = dict(
        type='bar',
        name='Malas',
        x = secciones,
        y = ((malas/todas)*100),
        marker = dict(
            color = colors['plantplot-mk-red'], 
        ),
    )
    
    return [trace, trace2]

def liner_graph_seccions_summary(df, seccion):
    df['month'] = df['date'].apply(lambda x: datetime(x.year, x.month, 1))
    todas = df.groupby('month').count()['id']
    buenas = df[(df[f'label_{seccion}']>0)].groupby('month').count()['id']
    trace = dict(
        type='line',
        x = todas.index,
        y = ((buenas/todas)*100).values,
    )
    return [trace]

#%%###########################################################################
#                              03. LAYOUT                                    #
##############################################################################

# Barra de navegacion de la aplicacion
navbar = dbc.Navbar([
            html.A(
                # Imagen con el logo de Dattium que nos llevara a la página principal de la App
                # Use row and col to control vertical alignment of logo / brand
                html.Img(src=app.get_asset_url(navbar_image),\
                                         height="45px"),
                href="/",
                className='float-right col-2'
            ),
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.NavItem(dbc.NavLink("Reports", href="/reports")),
    ], className='lg', color=colors['navbar'])
    
# Layout de la app
app.layout = html.Div([
    # Store, sirve para guardar datos y poder acceder a ellos entre paginas
    dcc.Store(id='store-p2-layout'),
    dcc.Store(id='store-id-clicked'),
    # Sirve para poder crear distintas paginas www.dattiumapp.com/seccions o www.dattiumapp.com/reports
    dcc.Location(id='url', refresh=False),
    navbar,
    # Contenido de las paginas
    html.Div(id='page-content')
])

# Update the index
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/seccions':
        return seccions_page_layout
    elif pathname == '/reports':
         return reports_page_layout
    else:
        return home_page_layout
    # You could also return a 404 "URL not found" page here


#%%###########################################################################
#                             04_1. HOME-PAGE                                #
##############################################################################
    
# Pagina 1, imagen de la planta y un gráfico general con el comportamiento de esta
home_page_layout = html.Div([
    # Barra de navegación de la aplicación
    # navbar,
    dbc.Tabs([
        dbc.Tab([
            # Content
            html.Div([
                # PLot of general view of plant
                html.Div([
                    # Titulo del gráfico
                    html.H1(
                        id='header-plant-plot-real',
                        children='Tiempo Real',
                        style={
                            'textAlign': 'center',
                            'color': colors['text'],
                            'margin-top': '30px'
                            },
                    ),
                    html.Br(),
                    html.Div([
                        html.Div(className='col-10'),
                        dbc.Button("Pause", className='ml-auto', id="pause-button"),
                        html.Div(className='col-1'),
                    ], className='row'),
                    html.Br(),
                    # Gráfico y filtros
                    html.Div([
                        html.Div(className='col-1', style=dict(height=pp_size)),
                        # Gráfico general del comportamiento de la planta
                        dcc.Graph(
                            id="plant-plot-real",
                            figure=dict(
                                layout=dict(
                                    plot_bgcolor=colors["graph-bg"],
                                    paper_bgcolor=colors["graph-bg"],
                                )
                            ),
                            className = 'col-10',
                            style=dict(background=colors['graph-bg'])
                        ),
                    ], className='row'),
                    # Interval, sirve para ir actualizando el gráfico cada GRAPH_INTERVAL ms
                    dcc.Interval(
                        id="signal-update",
                        interval=int(GRAPH_INTERVAL),
                        n_intervals=0,
                    ), 
                ]), 
            ]),
            html.Br(),
            # Imagen de la planta
            html.Div([
                html.Img(src=app.get_asset_url("plant-diagram.png"), className='mx-auto d-block')
            ], className = 'row'),
        ], label='Tiempo Real'),
        dbc.Tab([
            # Content
            html.Div([
                # PLot of general view of plant
                html.Div([
                    # Titulo del gráfico
                    html.H1(
                        id='header-plant-plot-hist',
                        children='Historico',
                        style={
                            'textAlign': 'center',
                            'color': colors['text'],
                            'margin-top': '30px'
                            },
                    ),
                    html.Br(),
                    # Filters
                    html.Div([
                        html.Div(className='col-1'),
                        # html.H4('Filtros'),
                        # html.Br(),
                        html.Div([
                            html.H5('Fecha de inicio'),
                            html.Div([
                                dcc.DatePickerSingle(date=date(2017, 3, 1), display_format='DD-MM-YYYY', \
                                                     className='col-4', id='date-min'),
                                dcc.Input(type='number', min=0, max=23, value=0, className='col-2', id='hour-min'),
                                html.Div([
                                    html.P(':'),
                                ], className='col-1', style={'fontSize': 22}),
                                dcc.Input(type='number', min=0, max=59, value=0, className='col-2', id='min-min'),
                            ], className='row'),
                        ], className='col-3'),
                        # html.Br(),
                        # html.Div(className='col-1'),º
                        html.Div([
                            html.H5('Fecha final'),
                            html.Div([
                                dcc.DatePickerSingle(date=date(2017, 3, 20), display_format='DD-MM-YYYY', \
                                                     className='col-4', id='date-max'),
                                dcc.Input(type='number', min=0, max=23, value=0, className='col-2', id='hour-max'),
                                html.Div([
                                    html.P(':'),
                                ], className='col-1', style={'fontSize': 22}),
                                dcc.Input(type='number', min=0, max=59, value=0, className='col-2', id='min-max'),
                            ], className='row'),
                        ], className='col-3'),
                    ], className="row"),
                    # Gráfico y filtros
                    html.Div([
                        html.Div(className='col-1', style=dict(height=pp_size)),
                        # Gráfico general del comportamiento de la planta
                        dcc.Graph(
                            id="plant-plot-hist",
                            figure=dict(
                                layout=dict(
                                    plot_bgcolor=colors["graph-bg"],
                                    paper_bgcolor=colors["graph-bg"],
                                ),
                            ),
                            className = 'col-10',
                        ), 
                    ], className='row'),
                ]), 
            ]),
            html.Br(),
            # Imagen de la planta
            html.Div([
                html.Img(src=app.get_asset_url("plant-diagram.png"), className='mx-auto d-block')
            ], className = 'row'),
        ], label='Historico'),
    ], className = ''),   
])

#%%###########################################################################
#                         04_2. HOME-PAGE CALLBACKS                          #
##############################################################################

# Callback que pausa la actualización automática del gráfico
@app.callback(
    [Output("signal-update", "disabled"), Output("pause-button", "children")], 
    [Input("pause-button", "n_clicks")],
    [State("signal-update", "disabled")]
)
def enable_update(n, disabled):
    children = "Play"
    if n is not None:
        if disabled:
            children="Pause"
        return (not disabled), children

# Callback que actualiza el gráfica cada X segundos o rango de fechas
@app.callback(
    [Output("plant-plot-real", "figure")], 
    [Input("signal-update", "n_intervals")]
)
def gen_signal_real(interval):
    """
    Generate the signal graph.
    :params interval: update the graph based on an interval
    """ 

    # Consulta a postgreSQL que devuelve las 100 primeras filas con un offset que incrementa cada GRAPH_INTERVALS ms
    df = pd.read_sql(('SELECT * FROM signals LIMIT 100 OFFSET %s' % (interval)), server_conn)
    
    trace, layout = get_plant_plot(df)

    return [dict(data=[trace], layout=layout)]

# Callback que actualiza el gráfica cada X segundos o rango de fechas
@app.callback(
    [Output("plant-plot-hist", "figure")], 
    [Input("date-min", "date"), Input("date-max", "date"), Input('hour-min', 'value'),\
     Input('hour-max', 'value'), Input('min-min', 'value'), Input('min-max', 'value')]
)
def gen_signal_hist(datemin, datemax, hourmin, hourmax, minmin, minmax):
    """
    Generate the signal graph.
    :params datemin: update the graph based on a date interval
    :params datemax: update the graph based on a date interval
    """  
    datemin = "'" + datemin + " " + str(hourmin).zfill(2) + ":"+ str(minmin).zfill(2) +"'"
    datemax = "'" + datemax + " " + str(hourmax).zfill(2) + ":"+ str(minmin).zfill(2) +"'"
    # Consulta a postgreSQL que devuelve
    df = pd.read_sql(("SELECT * FROM signals WHERE date >= %s AND date < %s" % (datemin, datemax)), server_conn)                 

    trace, layout = get_plant_plot(df)

    return [dict(data=[trace], layout=layout)]

# Callback al clicar en un punto del gráfico, guarda en los Store el id del punto y el layout de las señales
# que se van a mostrar como desviaciones/fallos
@app.callback([Output('store-p2-layout', 'data'), Output('url', 'pathname'), Output('store-id-clicked', 'data')],
              [Input('plant-plot-real', 'clickData'), Input('plant-plot-hist', 'clickData')])
def change_page(click_data, click_data_hist):
    des_s1 =  dbc.ListGroupItem("No hay ningúna señal desviada", id="desviacion-s1-item", className='text-center')
    des_s2 =  dbc.ListGroupItem("No hay ningúna señal desviada", id="desviacion-s2-item", className='text-center')
    fal_s1 =  dbc.ListGroupItem("No hay ningúna señal con fallos de registro/sensor", id="fallos-s1-item", className='text-center')
    fal_s2 =  dbc.ListGroupItem("No hay ningúna señal con fallos de registro/sensor", id="fallos-s2-item", className='text-center')
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
    if (click_data is None) and (click_data_hist is not None):
        if 'points' in click_data_hist.keys():
            if 'id' in click_data_hist['points'][0].keys():
                point_id = click_data_hist['points'][0]['id']
                selected_data = pd.read_sql(('SELECT * FROM signals WHERE id=%s' % (point_id)), server_conn)
                [col_fal_s1, col_des_s1] = get_columns(selected_data, 's1')
                [col_fal_s2, col_des_s2] = get_columns(selected_data, 's2')
                des_s1 = get_cards_layout(col_des_s1, True)
                fal_s1 = get_cards_layout(col_fal_s1, False)
                des_s2 = get_cards_layout(col_des_s2, True)
                fal_s2 = get_cards_layout(col_fal_s2, False)
    return [{'des_s1': (des_s1), 'fal_s1': (fal_s1), 'des_s2': (des_s2), 'fal_s2': (fal_s2)}, '/seccions', {'id': point_id}]


#%%###########################################################################
#                           05_1. SECCIONS-PAGE                              #
##############################################################################

# Página 2, dividida en dos tabs S1 y S2, en cada una de ellas tenemos la imagen de la seccion, la lista de 
# señales desviadas, la lista de las señales con fallos en el sensor/registro, la señal sobre el tiempo,
# y un histograma (con datos antiguos y un periodo de datos nuevos) junto a un dropdown para seleccionar las
# señales
seccions_page_layout = html.Div([
    # Barra de navegación de la App
    # navbar,
    # Dividimos la página en dos mediante tabs, para la S1 y S2
    dbc.Tabs([
        # Tab S1
        dbc.Tab(label='S1', children = [
            html.Br(),
            html.Div([
                # Listas de desviacion y fallos de resgistros/sensores
                html.Div([
                    # Titulo seccion
                    html.H1('Seccion 1', id='header-s1', className='text-center'),
                    html.Br(),
                    # Listas de desviacion y fallos de registro/sensor S1
                    html.Div([
                         # Lista de desviacion S1
                        html.Div(className='col-1'),
                        html.Div([
                            dbc.Card([
                                dbc.CardHeader([
                                    html.H3('Desviaciones', className='text-center'),
                                ]),
                                dbc.CardBody([
                                    dbc.ListGroup(id='list-des-s1'), 
                                ]),
                            ], color='warning', outline=True),#col-4
                        ], className='col-5'),
                        html.Div(className='col-1'),
                        # Lista de fallos de registro/sensor S1
                        html.Div([
                            dbc.Card([
                                dbc.CardHeader([
                                    html.H3('Fallos de registro/sensor', className='text-center'),
                                ]),
                                dbc.CardBody([
                                    dbc.ListGroup(id='list-fal-s1'), 
                                ]),
                            ], color='danger', outline=True),#col-4
                        ], className='col-5'),
                        html.Div(className='col-1'),#col-1
                    ], className='row'),#row
                ], className='col-5'),                
                html.Div(className='col-2'),
                # Imagen
                html.Img(src=app.get_asset_url("plant-s1.png"), className='mx-auto d-block col-4'),
                
                # html.Div(className='col-1'),
            ], className='row'),
            html.Br(),
            # Plot señal + histograma S1 
            html.Div([                
                # Plot señal S1
                html.Div([
                        # Título del gráfico 
                        html.Br(),
                        html.H3(
                            id='header-signal-plot-s1',
                            children='Signal plot',
                            style={
                                'textAlign': 'center',
                                'color': colors['text'],
                            }
                        ),
                        # Gráfico S1
                        dcc.Graph(
                            id="signal-s1",
                            figure=dict(
                                layout=dict(
                                    plot_bgcolor=colors["graph-bg"],
                                    paper_bgcolor=colors["graph-bg"],
                                )
                            ),
                        ),
                        
                    ],className='signal-plot col-5', style={'background': colors['graph-bg']}),
                
                #Dropdown S1
                html.Div([
                    html.H3('Selector de señal'),
                    dcc.Dropdown(
                        id="signal-dropdown-s1",
                        options=[{'label': x, 'value': x} for x in columns_s1],
                        value='Amina Flow',
                        style={
                            'color': colors['text-dropdown'],
                            # 'background': colors['graph-bg']
                        },
                    ),
                    html.Br(),
                    # Carta informativa de la ID seleccionada S1
                    html.Div([
                        dbc.Card([
                            dbc.CardHeader([
                                html.H3('Información de la barra', className='text-center'),
                            ]),
                            dbc.CardBody([
                                html.P("ID: ********", className='card-text text-left', id='card_info_id_s1'),
                            ]),
                        ], outline=True)
                    ],className='rounded d-flex justify-content-center align-items-center'),#col-2
                ], className='col-2 text-center'),
                
                # Plot histograma S1
                html.Div([
                    # Título del histograma de S1
                    html.Br(),
                    html.H3(
                        id='header-histogram-s1',
                        children='Histogram',
                        style={
                            'textAlign': 'center',
                            'color': colors['text']
                        }
                    ),
                    # Histograma de S1
                    dcc.Graph(
                        id="histogram-s1",
                        figure=dict(
                            layout=dict(
                                barmode='overlay',
                                plot_bgcolor=colors["graph-bg"],
                                paper_bgcolor=colors["graph-bg"],
                            )
                        ),
                    ),
                ],className='histogram-plot col-5', style={'background': colors['graph-bg']}),
            ], id='graficos-s1', className='row'),
        ]),
        # Tab S2
        dbc.Tab(label='S2', children = [
            html.Br(),
            html.Div([
                # Listas de desviacion y fallos de resgistros/sensores
                html.Div([
                    # Titulo seccion
                    html.H1('Seccion 1', id='header-s2', className='text-center'),
                    html.Br(),
                    # Listas de desviacion y fallos de registro/sensor S2
                    html.Div([
                         # Lista de desviacion S2
                        html.Div(className='col-1'),
                        html.Div([
                            dbc.Card([
                                dbc.CardHeader([
                                    html.H3('Desviaciones', className='text-center'),
                                ]),
                                dbc.CardBody([
                                    dbc.ListGroup(id='list-des-s2'), 
                                ]),
                            ], color='warning', outline=True),#col-4
                        ], className='col-5'),
                        html.Div(className='col-1'),
                        # Lista de fallos de registro/sensor S2
                        html.Div([
                            dbc.Card([
                                dbc.CardHeader([
                                    html.H3('Fallos de registro/sensor', className='text-center'),
                                ]),
                                dbc.CardBody([
                                    dbc.ListGroup(id='list-fal-s2'), 
                                ]),
                            ], color='danger', outline=True),#col-4
                        ], className='col-5'),
                        html.Div(className='col-1'),#col-1
                    ], className='row'),#row
                ], className='col-5'),                
                html.Div(className='col-2'),
                # Imagen
                html.Img(src=app.get_asset_url("plant-s2.png"), className='mx-auto d-block col-4'),
                
                # html.Div(className='col-1'),
            ], className='row'),
            html.Br(),
            # Plot señal + histograma S2 
            html.Div([                
                # Plot señal S2
                html.Div([
                        # Título del gráfico 
                        html.Br(),
                        html.H3(
                            id='header-signal-plot-s2',
                            children='Signal plot',
                            style={
                                'textAlign': 'center',
                                'color': colors['text'],
                            }
                        ),
                        # Gráfico S2
                        dcc.Graph(
                            id="signal-s2",
                            figure=dict(
                                layout=dict(
                                    plot_bgcolor=colors["graph-bg"],
                                    paper_bgcolor=colors["graph-bg"],
                                )
                            ),
                        ),
                        
                    ],className='signal-plot col-5', style={'background': colors['graph-bg']}),
                
                #Dropdown S2
                html.Div([
                    html.H3('Selector de señal'),
                    dcc.Dropdown(
                        id="signal-dropdown-s2",
                        options=[{'label': x, 'value': x} for x in columns_s2],
                        value='Flotation Column 02 Level',
                        style={
                            'color': colors['text-dropdown'],
                            # 'background': colors['graph-bg']
                        },
                    ),
                    html.Br(),
                    # Carta informativa de la ID seleccionada S2
                    html.Div([
                        dbc.Card([
                            dbc.CardHeader([
                                html.H3('Información de la barra', className='text-center'),
                            ]),
                            dbc.CardBody([
                                html.P("ID: ********", className='card-text text-left', id='card_info_id_s2'),
                            ]),
                        ], outline=True)
                    ],className='rounded d-flex justify-content-center align-items-center'),#col-2
                ], className='col-2 text-center'),
                
                # Plot histograma S2
                html.Div([
                    # Título del histograma de S2
                    html.Br(),
                    html.H3(
                        id='header-histogram-s2',
                        children='Histogram',
                        style={
                            'textAlign': 'center',
                            'color': colors['text']
                        }
                    ),
                    # Histograma de S2
                    dcc.Graph(
                        id="histogram-s2",
                        figure=dict(
                            layout=dict(
                                barmode='overlay',
                                plot_bgcolor=colors["graph-bg"],
                                paper_bgcolor=colors["graph-bg"],
                            )
                        ),
                    ),
                ],className='histogram-plot col-5', style={'background': colors['graph-bg']}),
            ], id='graficos-s2', className='row'),
        ]),
    ], id='tab-seccions'),
    html.Br(),
    dcc.Link('Go back to home', href='/')
])

#%%###########################################################################
#                        05_2. SECCIONS-PAGE CALLBACKS                       #
##############################################################################

# Callback que actualiza la targeta de información de ID S1
@app.callback(Output('card_info_id_s1', 'children'),
              [Input('store-id-clicked', 'modified_timestamp'), Input("signal-dropdown-s1", "value")],
              [State('store-id-clicked', 'data')])
def modify_info_card_s1(timestamp, column, id_data):  
    return_data = dcc.Markdown('''**ID**: -  
                                **Date**: -   
                                **-**: -  ''')  
    if id_data is not None:
        if 'id' in id_data.keys():
            return_data = get_card_info_layout(id_data['id'], column)
    return return_data

# Callback que actualiza la targeta de información de ID S2
@app.callback(Output('card_info_id_s2', 'children'),
              [Input('store-id-clicked', 'modified_timestamp'), Input("signal-dropdown-s2", "value")],
              [State('store-id-clicked', 'data')])
def modify_info_card_s2(timestamp, column, id_data):
    return_data = dcc.Markdown('''**ID**: -  
                                **Date**: -   
                                **-**: -  ''')  
    if id_data is not None:
        if 'id' in id_data.keys():
            return_data = get_card_info_layout(id_data['id'], column)
    return return_data
    
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
            df = pd.read_sql(('SELECT * FROM signals WHERE id>{} AND id<={}'.format(id_data['id']-500, id_data['id']+500)), server_conn)
    
    trace, trace2, layout = get_signal_plot(df, column, id_data['id'])
    
    trace3, trace4, layout2 = get_histogram(df, column, id_data['id'])
    return [dict(data=[trace, trace2], layout=layout), dict(data=[trace3, trace4], layout=layout2)]

# Callback que actualiza el plot y el histograma de la señal al cambiar de señal con el dropdown de S2
@app.callback(
    [Output("signal-s2", "figure"),  Output("histogram-s2", "figure")], 
    [Input("signal-dropdown-s2", "value")],
    [State('store-id-clicked', 'data')]
)
def gen_signal_s2(column, id_data):
    # Query por si no se ha seleccionado ningun punto devuelve los 1000 primeros puntos
    df = pd.read_sql('SELECT * FROM signals LIMIT 10000 OFFSET 0', server_conn)
    
    # Si se ha seleccionado punto:
    if id_data is not None:
        if 'id' in id_data.keys():
            # Query que devuelve a partir de una id las 1000 muestras anteriores
            df = pd.read_sql(('SELECT * FROM signals WHERE id>{} AND id<={}'.format(id_data['id']-500, id_data['id']+500)), server_conn)
    
    trace, trace2, layout = get_signal_plot(df, column, id_data['id'])
    
    trace3, trace4, layout2 = get_histogram(df, column, id_data['id'])
    
    return [dict(data=[trace, trace2], layout=layout), dict(data=[trace3, trace4], layout=layout2)]

#%%###########################################################################
#                           06_1. REPORTS-PAGE                               #
##############################################################################

# Página con los informes por seccion y producto
reports_page_layout = html.Div([
    dbc.Tabs([
        dbc.Tab(label='Resumen por producto', tab_id='products'), 
        dbc.Tab(label='Resumen por seccion', tab_id='seccions'),
        dbc.Tab(label='Resumen', tab_id='all'),
    ], id='summary-tabs', active_tab='products'),
    html.Div(id='summary-tab-content')
])

#%%###########################################################################
#                      06_2. REPORTS-PAGE CALLBACKS                          #
##############################################################################

# Callback que modifica el contenido de la página en función del Tab activo.
@app.callback(
    Output("summary-tab-content", "children"),
    [Input("summary-tabs", "active_tab")],
)
def render_tab_content(active_tab):
    if active_tab == "products":
        return summary_tab_layout('products')
    elif active_tab == "seccions":
        return summary_tab_layout('seccions')
    else: 
        return [summary_tab_layout('products'),
                summary_tab_layout('seccions')]
    

#%%###########################################################################
#                              07. MAIN                                      #
##############################################################################
if __name__ == '__main__':
    app.run_server(debug=False)