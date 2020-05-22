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
import calendar
from params import colors, dark, postgre_ip, user, pswrd, params
from comparativas import selector_de_fechas, histograma_layout, get_histogram2

#%%###########################################################################
#                            01. CONFIGURACIÓN                               #
##############################################################################

# font_awesome1 = "//netdna.bootstrapcdn.com/twitter-bootstrap/2.3.2/css/bootstrap-combined.no-icons.min.css"
font_awesome2 = "//netdna.bootstrapcdn.com/font-awesome/3.2.1/css/font-awesome.css"

external_scripts = [{
        'src': 'https://kit.fontawesome.com/c67d65477e.js',
        'crossorigin': 'anonymous'
    }
]

# Script con las configuraciones CSS de Bootstrap
if dark:
    external_stylesheets =  [dbc.themes.DARKLY, font_awesome2] #SLATE / DARKLY /SUPERHERO / BOOTSTRAP
    navbar_image = "logo-dattium-navbar-dark2.png"
else:
    external_stylesheets =  [dbc.themes.BOOTSTRAP, font_awesome2] #SLATE / DARKLY /SUPERHERO / BOOTSTRAP
    navbar_image = "logo-dattium-navbar.png"
    
# Conexion a la BBDD postgreSQL con el usuario test, contraseña test123 y en la BBDD DattiumApp        
server_conn = create_engine('postgresql://{}:{}@{}:5432/DattiumApp'.format(user, pswrd, postgre_ip))
# Extraemos en un DF todos los datos de la BBDD
df_raw = pd.read_sql(('SELECT * FROM signals'), server_conn)
# Array con el nombre de las señales que vamos a utilizar
columns = np.array(list(df_raw.columns)[1:len(df_raw.columns)])
columns_s1 = columns[0:11]
columns_s2 = columns[11:23]

columns1 = columns[0:7]
columns2 = columns[7:14]
columns3 = columns[14:23]

# Evento para el refresco del grafico principal
GRAPH_INTERVAL = os.environ.get("GRAPH_INTERVAL", 3000)

# User/Password para acceder a la app
USERNAME_PASSWORD_PAIRS = [
    ['test', 'test123'],['jamesbond', '007']
]

# Configuración de DASH
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts)
app.config.suppress_callback_exceptions = True
auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS)
server = app.server

if dark:
    graph_bg = '#303030'#272B30'
    text_color = '#AAAA9F'
    text_highlight = '#CCCCC0'
    pp_bg_green = '#356437'
    pp_bg_red = '#653434'
    pp_mk_green = '#59C159'
    pp_mk_red = '#EC5550'
    pp_ma_grey = '#AAAAAA'
    chm_good = '#DDDDDD'
    chm_dev = '#e8b68b'
    chm_fail = '#e04f38'
else:
    graph_bg = ''
    text_color = '262626'
    text_highlight = '0d0d0d'
    pp_bg_green = '#F7FAF0'
    pp_bg_red = '#F9E9E0'
    pp_mk_green = '#76B7B2'
    pp_mk_red = '#E15759'
    pp_ma_grey = '#DDDDDD'
    chm_green = '#EEEEEE'
    chm_dev = '#E8C2A0'
    chm_fail = '#E06E5D'

colors = {
    'navbar': 'secondary',
    'title-bg': '#444444',
    'graph-bg': graph_bg,
    'text': text_color,
    'text-highlight': text_highlight,
    'text-dropdown': '#3A3A3A',
    'plantplot-bg-green': pp_bg_green, # Plantplot Background Green
    'plantplot-bg-red': pp_bg_red, # Plantplot Background Red
    'plantplot-l-red': '#B31919', # Plantplot Line Red #E46B6B
    'plantplot-mk-green': pp_mk_green, # Plantplot Marker Green
    'plantplot-mk-red': pp_mk_red, # Plantplot Merker Red
    'plantplot-ma-grey': pp_ma_grey, # Plantplot Moving Average line grey
    'chm-good': chm_good, # Calendar HeatMap Green
    'chm-dev': chm_dev, # Calendar HeatMap Yellow
    'chm-fail': chm_fail, # Calendar HeatMap Red
    'histogram-act': '#FFA64D', # Histogram Actual
    'histogram-act-br': '#FF8C1A', # Histogram Actual Border
    'histogram-hist': '#4DA6FF', # Histogram Historical
    'histogram-hist-br': '#1A8CFF', # Histogram Historical Border
    'grid': '#636363', 
    'signal-line': '#FEC036', # Linea amarilla del gráfico de la señal
    'signal-marker': '#B31919',
    'stacked-bar-yellow': '#FEC036',
}

# Parametros de configuración del texto de los gráficos
family_font = 'Arial, sans-serif' # Graph Text Font
size_font = 16 # Graph Text Size
size_font_summary = 16 # Summary Graph Text Size
size_font_cards = 16 # Font Text Size
pp_size = '10%' # Plant plot graph size
navbar_logo_size = "90%" # Navbar logo size

perfiles = {
    0: '5.5',
    1: '7.5',
    2: '10'
}

calidad = {
    0: '',
    1: '',
    2: '',
}

#%%###########################################################################
#                       02_01. FUNCIONES (HOME PAGE)                         #
##############################################################################

date_min = datetime(2017, 4, 1, 1, 0, 0) #df_raw['date'].min()
date_max = datetime(2017, 4, 2, 1, 0, 0) # df_raw['date'].max()

# Selector  de fechas
selector_fecha = html.Div([
        html.Div([
            html.Div([
                html.H6('Fecha desde', className='col-4'),
                html.Div(className='col-1'),
                html.I(id="hour-min-up", n_clicks=0, n_clicks_timestamp = -1,
                       className="fas fa-caret-up fa-2x text-center col-2",
                       style={"cursor": "pointer"}),
                html.Div(className='col-1'),
                html.I(id="min-min-up", n_clicks=0, n_clicks_timestamp = -1,
                       className="fas fa-caret-up fa-2x text-center col-2 pointer",
                       style={"cursor": "pointer"}),
            ], className='row'),
            html.Div([
                dcc.DatePickerSingle(date=datetime.date(date_min), display_format='DD-MM-YYYY',
                                     className='col-4 rounded-lg h-100 w-100 DateInput_1', persistence=True,
                                     id='date-min'),
                html.Div(className='col-1'),
                dbc.Input(type='text', value="00", className='col-2 px-1 text-center', 
                          style={"height":"inherit"},
                           persistence=True,
                          id='hour-min'),
                html.Div([
                    html.P(':'),
                ], className='col-1', style={'fontSize': 22}),
                dbc.Input(type='text', value="00", className='col-2 px-1 text-center', 
                           persistence=True,
                          style={"height":"inherit",
                                 "cursor": "pointer"}, 
                          id='min-min'),
            ], className='row'),
            html.Div([
                html.H6('Fecha desde', className='col-4 invisible'),
                html.Div(className='col-1'),
                html.I(id="hour-min-down", n_clicks=0, n_clicks_timestamp = -1,
                       className="fas fa-caret-down fa-2x text-center col-2",
                       style={"cursor": "pointer"}),
                html.Div(className='col-1'),
                html.I(id="min-min-down", n_clicks=0, n_clicks_timestamp = -1,
                       className="fas fa-caret-down fa-2x text-center col-2",
                       style={"cursor": "pointer"}),
            ], className='row'),
        ], className='col-3'),
        # html.Br(),
        # html.Div(className='col-1'),º
        html.Div([
            html.Div([
                html.H6('Fecha hasta', className='col-4'),
                html.Div(className='col-1'),
                html.I(id="hour-max-up", n_clicks=0, n_clicks_timestamp = -1,
                       className="fas fa-caret-up fa-2x text-center col-2",
                       style={"cursor": "pointer"}),
                html.Div(className='col-1'),
                html.I(id="min-max-up", n_clicks=0, n_clicks_timestamp = -1,
                       className="fas fa-caret-up fa-2x text-center col-2 pointer",
                       style={"cursor": "pointer"}),
            ], className='row'),
            html.Div([
                dcc.DatePickerSingle(date=datetime.date(date_max), display_format='DD-MM-YYYY',
                                     className='col-4 rounded-lg h-100 w-100', persistence=True,
                                     id='date-max'),
                html.Div(className='col-1'),
                dbc.Input(type='text', value="00", className='col-2 px-1 text-center', 
                          style={"height":"inherit"},
                           persistence=True,
                          id='hour-max'),
                html.Div([
                    html.P(':'),
                ], className='col-1', style={'fontSize': 22}),
                dbc.Input(type='text', value="00", className='col-2 px-1 text-center', 
                           persistence=True,
                          style={"height":"inherit",
                                 "cursor": "pointer"}, 
                          id='min-max'),
            ], className='row'),
            html.Div([
                html.H6('Fecha desde', className='col-4 invisible'),
                html.Div(className='col-1'),
                html.I(id="hour-max-down", n_clicks=0, n_clicks_timestamp = -1,
                       className="fas fa-caret-down fa-2x text-center col-2",
                       style={"cursor": "pointer"}),
                html.Div(className='col-1'),
                html.I(id="min-max-down", n_clicks=0, n_clicks_timestamp = -1,
                       className="fas fa-caret-down fa-2x text-center col-2",
                       style={"cursor": "pointer"}),
            ], className='row'),
        ], className='col-3'),
        html.Div([
            html.I(className="fas fa-caret-up fa-2x text-center col-2 invisible"),
            html.Div([
                dbc.Button([
                    html.Div([
                        html.P([
                            html.I(className='fas fa-search h-100'),
                            html.A('  BUSCAR', className='h-100'),
                        ], className='h-100', style={"margin-bottom": 0,}),
                    ], className='h-100 w-100 pt-2')
                ], className='col-6 px-1 py-1 btn-block h-100', id='search-button', n_clicks=0),
                dcc.DatePickerSingle(date=datetime.date(date_max), display_format='DD-MM-YYYY',
                                     className='invisible h-100 col-1', persistence=True),
            ], className='row h-50 pb-2'),
            html.I(className="fas fa-caret-up fa-2x text-center col-2 invisible"),
        ], className='col-2')
    ], className="row w-100 pl-4 pt-2")

# Card content
def chm_card_content(card):
    data={
        1: {
            "first" : '% de efciencia en los últimos 30 días',
            "second" : '97%',
            "third" : '30 Mayo 2017 - 30 Junio 2017'
        },
        2: {
            "first" : 'Racha actual de eficiencia',
            "second" : '3 días',
            "third" : '27 Junio 2017 - 30 Junio 2017'
        },
        3: {
            "first" : 'Mayor racha de eficiencia',
            "second" : '27 días',
            "third" : '3 Mayo 2017 - 30 Mayo 2017'
        },
    }
    return html.Div([
        html.Div(data[card]['first'], style={"font-size": "1rem", "color": colors['text']}),
        html.Div(data[card]['second'], style={"font-size": "3rem"}),
        html.Div(data[card]['third'], style={"font-size": "1rem", "color": colors['text']}),
    ], className='my-auto')

# Calendar HeatMap  Figure Layout and Traces
def calendar_heatmap(df, seccion):
    if seccion == 'S1':
        label = '_S1'
        label_max = 2
    elif seccion == 'S2':
        label = '_S2'
        label_max = 2
    else:
        label = ''
        label_max = 6
        
    df['day'] = [datetime.date(fecha) for fecha in df['date']]
    
    d1 = datetime.date(df['date'].min())
    d2 = datetime.date(df['date'].max())
    delta = d2 - d1
    num_months = (d2.year - d1.year) * 12 + (d2.month - d1.month)
    
    dates_in_year = [d1 + timedelta(i) for i in range(delta.days+1)] #gives me a list with datetimes for each day a year
    weekdays_in_year = [i.weekday() for i in dates_in_year] #gives [0,1,2,3,4,5,6,0,1,2,3,4,5,6,…] (ticktext in xaxis dict translates this to weekdays
    weeknumber_of_dates = [i.strftime("%Gww%V") for i in dates_in_year] #gives [1,1,1,1,1,1,1,2,2,2,2,2,2,2,…] name is self-explanatory
    z = np.array([0 if x<label_max*0.8 else 1 if x<label_max*0.85 else 2 
                  for x in df.groupby('day').mean()[f'label{label}'].values]) #df.groupby('day').mean()[f'label{label}'] 
    text = [str(i) for i in dates_in_year] #gives something like list of strings like '2018-01-25' for each date. Used in data trace to _ta good hovertext.
    
    xtickvals = [d1.strftime("%Gww%V")]
    xticktext = [d1.strftime("%b")]
    month = d1.month + 1
    year = d1.year
    for i in range(1, num_months):
        if month > 12:
            month=1
            year+=1
        fecha = datetime(year, month, 1)
        xtickvals = np.append(xtickvals, fecha.strftime("%Gww%V"))
        xticktext = np.append(xticktext, fecha.strftime("%b"))
        month += 1
    
    trace = dict(
        type='heatmap',
        x = weeknumber_of_dates,
        y = weekdays_in_year,
        z = z,
        text=text,
        hoverinfo="text+z",
        xgap=3, # this
        ygap=3, # and this is used to make the grid-like apperance
        zmin=0,
        zmax=2,
        showscale=True,
        colorscale=[(0, colors['chm-fail']),   (0.33, colors['chm-fail']),
                    (0.33, colors['chm-dev']), (0.66, colors['chm-dev']),
                    (0.66, colors['chm-good']),  (1.00, colors['chm-good'])],
        colorbar=dict(
            title="Anomalías",
            # titleside="top",
            tickmode="array",
            tickvals=[0.33, 1, 1.66],
            ticktext=["Muchas", "Algunas", "Pocas"],
            ticks="outside"
        ),
    )
    layout = dict(
        yaxis=dict(
            showline = False, showgrid = False, zeroline = False,
            tickmode="array",
            ticktext=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], 
            tickvals=[0,1,2,3,4,5,6],
            ticks = '',
        ),
        xaxis=dict(
            showline = False, showgrid = False, zeroline = False,
            ticktext= xticktext,
            tickvals = xtickvals,
        ),
        font={"color": colors['text'], "size": size_font, "family": family_font,},
        plot_bgcolor=colors["graph-bg"],
        paper_bgcolor=colors["graph-bg"],
        margin = dict(t=40, b=40, r=40, l=40),
    )
    return dict(data=[trace], layout=layout)

# Calendar HeatMap Layout
calendar_heatmap_layout = html.Div([
    dbc.Card([
        dbc.CardHeader([html.H5('Resumen por día', className='text-style')], className='px-2 pt-1 p-0'),
        dbc.CardBody([
            dcc.Graph(
                id='calendar-heatmap',
                figure = calendar_heatmap(df_raw, 'general'),
                    # layout=dict(
                    #     plot_bgcolor=colors["graph-bg"],
                    #     paper_bgcolor=colors["graph-bg"],
                    # )
                
                # figure=calendar_heatmap(df, seccion),
                className = 'col-12',
                style=dict(
                    background=colors['graph-bg'],
                    height='100%'
                )
            ),
        ], className='h-100 w-100 py-1')
    ], className='h-100 w-100')
], className='row w-100 py-2 h-100 mx-0')

# Calendar HeatMap Info Layout
chm_info_layout = html.Div([
    dbc.Card([
        dbc.CardHeader([html.H5('Información general', className='text-style')], className='px-2 pt-1 p-0'),
        dbc.CardBody([
            html.Div([
                dbc.Card([
                    chm_card_content(1)
                ], id='chm_info_card1', className='ml-4 col-3 bg-secondary text-center'),
                html.Div(className='col-1'),
                dbc.Card([
                    chm_card_content(2)
                ], id='chm_info_card2', className='h-100 col-3 bg-secondary text-center'),
                html.Div(className='col-1'),
                dbc.Card([
                    chm_card_content(3)
                ], id='chm_info_card3', className='h-100 col-3 bg-secondary text-center'),
            ], className='row h-100 py-4 mx-auto')
        ], className='h-100 w-100 py-1')
    ], className='h-100 w-100')
], className='row w-100 py-2 h-100 mx-0')

# Bottom seccion real tab layout
bottom_seccion_real_layout = html.Div([
        dbc.Tabs([
            dbc.Tab(label='General', tab_id='general'), 
            dbc.Tab(label='Horno', tab_id='S1'),
            dbc.Tab(label='Casetas', tab_id='S2'),
        ], id='chm-tabs', active_tab='general'),
        html.Div([
            html.Div([calendar_heatmap_layout],id='chm-tab-content', className='col-6 pl-3 pr-1 h-100'),
            html.Div([chm_info_layout], id='info-tab-content', className='col-6 pr-3 pl-1 h-100'),
        ], className='row w-100 pt-1 mx-0', style=dict(height='calc(100% - 40px)'))
    ], className='h-100 w-100 py-3') 

# Filters
filters = html.Div([
    html.Div([
        html.Div(className='col-11'),
        dbc.Button("Pause", className='ml-auto', id="pause-button"),
        # html.Div(className='col-1'),
        html.Div(selector_fecha, style={"height":0, "visibility": "hidden"})
    ], className='row w-100 px-5 pb-1 h-100'), 
], className='h-100')

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
    max_p = df.groupby('product').count()['id'].idxmax() # Producto más fabricado
    max_q = df.groupby('quality').count()['id'].idxmax() # Calidad más fabricada
    max_pq = df.groupby(['product', 'quality']).count()['id'].idxmax() # Producto-Calidad más fabricado
    fail_p = df[df['label']<4].groupby('product').count()['id'].idxmax() # Producto con más fallos
    fail_q = df[df['label']<4].groupby('quality').count()['id'].idxmax() # Calidad con más fallos
    fail_pq = df[df['label']<4].groupby(['product', 'quality']).count()['id'].idxmax() # Producto con más fallos
    df_table = pd.DataFrame(data=[['Producto + fabricado', 'Perfil ' + perfiles[max_p]],
                                  ['Calidad + fabricada', 'Calidad ' + str(max_q)],
                                  ['Producto/Calidad + fabricada', 'Perfil ' +
                                   perfiles[max_pq[0]] + ' / Calidad ' + str(max_pq[1])],
                                  ['Producto con + fallos', 'Perfil ' + perfiles[fail_p]],
                                  ['Calidad con + fallos', 'Calidad ' + str(fail_q)],
                                  ['Producto/Calidad con + fallos', 'Perfil ' + 
                                   perfiles[fail_pq[0]]+' / Calidad ' + str(fail_pq[1])]])
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


# Devuelve el gráfico de barras de barras buenas/malas en funcion de una o varias columnas
def bar_graph_product_summary(df):
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
    layout = dict(
        plot_bgcolor=colors["graph-bg"],
        paper_bgcolor=colors["graph-bg"],
        font={"color": colors['text'], "size": size_font_summary, "family": family_font,},
        margin={"t":30, "r":15, "l": 35},
        xaxis={
            "tickangle": 30,
        },
    )
    
    return [trace, trace2], layout

def liner_graph_product_summary(df, product, quality, xaxis):
    if product == -1:
        fproduct = df['product'].isin(df['product'].unique())
    else:
        fproduct = df['product'] == product
    if quality == -1:
        fquality = df['quality'].isin(df['quality'].unique())
    else:
        fquality = df['quality'] == quality
        
    if xaxis == 'month':
        df['date_groupby'] = df['date'].apply(lambda x: datetime(x.year, x.month, calendar.monthrange(x.year, x.month)[1]))
    else:
        df['date_groupby'] = df['date'].apply(lambda x: x.date())
        
    todas = df[(fproduct) & (fquality)].groupby('date_groupby').count()['id']
    buenas = df[(df['label']>=4) & (fproduct) & (fquality)].groupby('date_groupby').count()['id']  
    trace = dict(
        type='line',
        x = todas.index,
        y = ((buenas/todas)*100).values,
    )
    layout = dict(
        plot_bgcolor=colors["graph-bg"],
        paper_bgcolor=colors["graph-bg"],
        font={"color": colors['text'], "size": size_font_summary, "family": family_font,},
        margin={"t":30, "r":15, "l": 35},
        xaxis={
            "tickangle": 30,
        },
        yaxis={
            "range": [50,100]    
        },
    )
    return trace, layout

# Devuelve el gráfico de barras de barras buenas/malas por seccion
def bar_graph_seccions_summary(df):
    secciones = [1 ,2, 3]
    name_secciones = ['Horno', 'Casetas', 'Tren']
    todas = []
    buenas = []
    malas = []
    desviadas = []
    for seccion in secciones:
        todas = np.append(todas, len(df))
        buenas = np.append(buenas, len(df[df[f'label_S{seccion}']==2]))
        desviadas = np.append(desviadas, len(df[df[f'label_S{seccion}']==1]))
        malas = np.append(malas, len(df[df[f'label_S{seccion}']==0]))

    trace = dict(
        type='bar',
        name='Buenas',
        x = [f'{seccion}' for seccion in name_secciones],
        y = ((buenas/todas)*100),
        marker = dict(
            color = colors['plantplot-mk-green'], 
        ),
    )
    trace2 = dict(
        type='bar',
        name='Anomalías',
        x = [f'{seccion}' for seccion in name_secciones],
        y = ((malas/todas)*100),
        marker = dict(
            color = colors['plantplot-mk-red'], 
        ),
    )
    trace3 = dict(
        type='bar',
        name='Desviaciones',
        x = [f'{seccion}' for seccion in name_secciones],
        y = ((desviadas/todas)*100),
        marker = dict(
            color = colors['stacked-bar-yellow'], 
        ),
    )
    layout = dict(
        plot_bgcolor=colors["graph-bg"],
        paper_bgcolor=colors["graph-bg"],
        font={"color": colors['text'], "size": size_font_summary, "family": family_font,},
        margin={"t":30, "r":15, "l": 35},
        xaxis={
            "tickangle": 30,
        },
        barmode='stack',
    )
    
    return [trace, trace3, trace2], layout

def liner_graph_seccions_summary(df, seccion, xaxis):
    if xaxis == 'month':
        df['date_groupby'] = df['date'].apply(lambda x: datetime(x.year, x.month, calendar.monthrange(x.year, x.month)[1]))
    else:
        df['date_groupby'] = df['date'].apply(lambda x: x.date())
        
    todas = df.groupby('date_groupby').count()['id']
    buenas = df[(df[f'label_S{seccion}']>0)].groupby('date_groupby').count()['id']
    
    trace = dict(
        type='line',
        x = todas.index,
        y = ((buenas/todas)*100).values,
    )
    layout = dict(
        plot_bgcolor=colors["graph-bg"],
        paper_bgcolor=colors["graph-bg"],
        font={"color": colors['text'], "size": size_font_summary, "family": family_font,},
        margin={"t":30, "r":15, "l": 35},
        xaxis={
            "tickangle": 30,
        },
        yaxis={
            "range": [50,100]    
        },
    )
    return trace, layout

# Devuelve el layout de los tabs de reports
def summary_tab_layout(tab, df, single):
    
    product_options = [{"label": f"Perfil {perfiles[product]}", "value": product}
                             for product in np.sort(df['product'].unique())]
    product_options.append({"label": "Todos", "value": -1})
    
    quality_options = [{"label": f"Calidad {quality}", "value": quality} 
                       for quality in np.sort(df['quality'].unique())]
    quality_options.append({"label": "Todos", "value": -1})
    
    if single:
        hcontainer = '100%'
    else:
        hcontainer = '50%'
        
    if tab == 'products':
        table = product_summary_table(df)
        data_bar, layout_bar = bar_graph_product_summary(df)
        titulo_bar_plot = 'Evaluación Anomalias por producto'
        titulo_line_plot = 'Estabilidad temporal del proceso por producto'
        data_line, layout_line = liner_graph_product_summary(df, df['product'].unique()[0],\
                                                df['quality'].unique()[0], 'day')    
        pq_selector = [
            dbc.FormGroup([
                dcc.Dropdown(
                    options=product_options,                
                    value=-1,#df['product'].unique()[0],
                    id="checklist-product",
                    style={'color': colors['text-dropdown'],},
                ),
            ]),
            dbc.FormGroup([
                dcc.Dropdown(
                    options= quality_options,       
                    value=-1,
                    id="checklist-quality",
                    style={'color': colors['text-dropdown'],},
                ),
            ]),
            dbc.FormGroup([
                dbc.RadioItems(
                    options=[{"label": "Day", "value": "day"},
                        {"label": "Month", "value": "month"},],                
                    value="day",
                    id=f"checklist-xaxis-product",
                ),
            ]),
        ]
    else:
        table = seccion_summary_table(df)
        data_bar, layout_bar = bar_graph_seccions_summary(df)
        titulo_bar_plot = 'Evaluación Anomalias por seccion'
        titulo_line_plot = 'Estabilidad temporal del proceso por seccion'
        data_line, layout_line = liner_graph_seccions_summary(df, '1', 'day')
        pq_selector = [
            dbc.FormGroup([
                # dbc.Label("Selector de seccion"),
                dcc.Dropdown(
                    options=[{"label": f"Seccion {seccion}", "value": seccion}\
                             for seccion in [1,2,3]],                
                    value=1,
                    id="checklist-seccion",
                    style={'color': colors['text-dropdown'],},
                ),
            ]),
            dbc.FormGroup([
                dbc.RadioItems(
                    options=[{"label": "Day", "value": "day"},
                        {"label": "Month", "value": "month"},],                
                    value="day",
                    id=f"checklist-xaxis-seccion",
                ),
            ]),
        ]         
    return html.Div([
        html.Div([
            html.Div([
                dbc.Card([
                    dbc.CardHeader([html.H5('Resumen de {}'.format(tab), className='text-style')], className='px-2 pt-1 p-0'),
                    dbc.CardBody([
                        dbc.Table(table, 
                                  striped=True, 
                                    # bordered=True, 
                                  responsive=True,
                                  hover=True,
                                  dark=True,
                                  className='table text-style-table m-0',
                                  style={"height": '100%'},
                                  id=f'summary-table-{tab}')
                    ], className='h-100 px-1 py-0'),
                ], className='h-100'),
            ], className='col-3 px-2 h-100'),
            html.Div([
                dbc.Card([
                    dbc.CardHeader([html.H5(titulo_bar_plot, className='text-style')], className='px-2 pt-1 p-0'),
                    dbc.CardBody([
                        dcc.Graph(
                            id=f'bar-plot-{tab}',
                            figure=dict(
                                data = data_bar,
                                layout=layout_bar,
                            ),
                            style={"height": '100%'},
                        ),
                    ], className='py-1 px-2'),
                ], className='h-100 w-100'),
            ], className='col-4 px-1 h-100'),
            html.Div([
                dbc.Card([
                    dbc.CardHeader([html.H5(titulo_line_plot, className='text-style')], className='px-2 pt-1 p-0'),
                    dbc.CardBody([
                        html.Div([
                            dcc.Graph(
                                id=f'time-plot-{tab}',
                                figure=dict(
                                    data = [data_line],
                                    layout = layout_line,
                                ),
                                style={"height": '100%'},
                                className='col-9'
                            ),
                            html.Div(pq_selector,className='col-3 pt-4 h-100'),
                        ], className='row h-100 w-100')
                    ], className='h-100 py-1 px-1')
                ], className='h-100')
            ], className='col-5 pl-1 pr-1 h-100'),
            
        ], className='row py-1 px-2 m-0 w-100', style={"height": '100%'})], className='pt-1', style={"height": hcontainer})

# Report Page Layout
reports_page_layout2 = html.Div([
    dbc.Tabs([
        dbc.Tab(label='Resumen por producto', tab_id='products'), 
        dbc.Tab(label='Resumen por seccion', tab_id='seccions'),
    ], id='summary-tabs', active_tab='products', className='Tabs1'),
    html.Div([summary_tab_layout('products', df_raw, True)], id='summary-tab-content', style=dict(height='calc(100% - 40px)'))
], className='h-100') 

home_layout = html.Div([
    # PLot of general view of plant
    html.Div([
        dbc.Card([
            dbc.CardHeader([html.H5('Resumen del processo', className='py-0 text-style')], className='px-2 pt-1 p-0'),
            dbc.CardBody([
                html.Div([
                    html.Div([
                        html.Div(selector_fecha, id='selector-fechas-container', className='invisible'),#style={"height":0, "visibility": "hidden"}),
                        html.Div([
                            html.Div(className='col-11'),
                            dbc.Button("Pause", className='ml-auto', id="pause-button"),
                        ], className='row w-100 pr-3 pb-1 h-100', id='button-container'),
                    ], id='filters-container', style={"height": '12%'}),
                    html.Div([
                        dcc.Graph(
                            id=f'plant-plot',
                            figure=dict(
                                layout=dict(
                                    plot_bgcolor=colors["graph-bg"],
                                    paper_bgcolor=colors["graph-bg"],
                                )
                            ),
                            className='h-100',
                        ),
                    ], className='px-2 pt-1', id='plant-plot-container', style=dict( height= '88%'))
                ], className='h-100')
            ], className='py-2', style={"height": "85%"}),
        ], className='h-100 w-100'),
        # html.Div([dcc.Graph(id=f'plant-plot-{altertab}')],className='invisible', style={'height': 0}),
    ], className='pb-3 px-4 pt-2 h-50'), 
    html.Div([
        html.Div([bottom_seccion_real_layout], id='bottom_seccion_real', className='h-100'),#style={'height': '100%'}),
        html.Div(reports_page_layout2, id='bottom_seccion_hist', className='invisible')#style={'height': 0, "visibility": "hidden"}),
    ], id='hp-bottom-div', className='pt-3 w-100 h-50'),
], className='h-100 w-100') 

# Función que devuelve el trace y layout de plant-plot
def get_plant_plot(df):
        
    column = 'label'
    datemin1 = df['date'].min() - timedelta(hours=2)
    datemax1 = df['date'].max() + timedelta(hours=2)
    
    # moving_average = df[column].rolling(3).mean()
    
    df.loc[df['label_S1']==2, 'label_S1'] = -1
    df.loc[df['label_S1']==0, 'label_S1'] = 2
    df.loc[df['label_S1']==-1, 'label_S1'] = 0
    
    df.loc[df['label_S2']==2, 'label_S2'] = -1
    df.loc[df['label_S2']==0, 'label_S2'] = 2
    df.loc[df['label_S2']==-1, 'label_S2'] = 0

    df.loc[df['label_S3']==2, 'label_S3'] = -1
    df.loc[df['label_S3']==0, 'label_S3'] = 2
    df.loc[df['label_S3']==-1, 'label_S3'] = 0
    
    # Scatter plot con del label de comportamiento de la planta
    trace = dict(
        type="bar",
        ids=df['id'],
        x=df['date'],
        y=df['label_S1'],
        # marker={"color": "#FF6B35"},
        hoverinfo='x+text',
        # Texto que se muestra al pasar el cursor por encima de un punto
        hovertext = ['<b>Horno</b>: {}'.format(row['label_S1']) \
                     for index, row in df.iterrows()],
        # mode="markers",
        name='Horno',
    )
        
    trace2 = dict(
        type="bar",
        ids=df['id'],
        x=df['date'],
        y=df['label_S2'],
        # marker={"color": "#F7C59F"},
        hoverinfo='x+text',
        # Texto que se muestra al pasar el cursor por encima de un punto
        hovertext = ['<b>Casetas</b>: {}'.format(row['label_S2']) \
                     for index, row in df.iterrows()],
        # mode="markers",
        name='Casetas',
    )
        
    trace3 = dict(
        type="bar",
        ids=df['id'],
        x=df['date'],
        y=df['label_S3'],
        # marker={"color": "#EFEFD0"},
        hoverinfo='x+text',
        # Texto que se muestra al pasar el cursor por encima de un punto
        hovertext = ['<b>Id</b>: {}<br><b>All</b>: {}<br><b>Placa Enfriadora</b>: {}'.format(row['id'],row['label'], row['label_S3']) \
                     for index, row in df.iterrows()],
        name='Placa Enfriadora',
    )
        
    # trace2 = dict(
    #     type="bar",
    #     x=df['date'],
    #     y=moving_average,
    #     line={"color": colors['plantplot-ma-grey']},
    #     mode="line",
    #     name='Moving average 5',
    # )
        
    # Opciones de estilo del gráfico
    layout = dict(
        plot_bgcolor=colors["graph-bg"],
        paper_bgcolor=colors["graph-bg"],
        font={"color": colors['text'], "size": size_font, "family": family_font,},
        margin={"t":30, "b": 50, "r": 15, "l":15},
        barmode='stack',
        # height=500,
        xaxis={
            "range": [datemin1, datemax1],
            "showline": False,
            "zeroline": False,
            "fixedrange": True,
            "ylabel": column,
        },
        yaxis={
            "range": [
                0,
                6.5
            ],
            "tickvals": [2,4,6],
            "showgrid": False,
            "showline": False,
            "fixedrange": True,
            "zeroline": False,
            "gridcolor": colors["grid"],
            "nticks": 7,
            "automargin": True,
        },
        # shapes=[
        #     # Rectangulo de color verde para estilizar el scatter
        #     dict(
        #         type='rect', 
        #         x0=datemin1, 
        #         x1=datemax1, 
        #         y0=4, 
        #         y1=6.5, 
        #         fillcolor=colors['plantplot-bg-green'], 
        #         layer='below',
        #         linewidth=0,
        #     ),
        #     # Rectangulo de color rojo para estilizar el scatter
        #     dict(
        #         type='rect', 
        #         x0=datemin1, 
        #         x1=datemax1, 
        #         y0=0, 
        #         y1=4, 
        #         fillcolor=colors['plantplot-bg-red'], 
        #         layer='below',
        #         linewidth=0,
        #     ),
        #     # Linea de color rojo para estilizar el scatter
        #     dict(
        #         type="line",
        #         x0=datemin1,
        #         y0=4,
        #         x1=datemax1,
        #         y1=4,
        #         line=dict(
        #             color=colors['plantplot-l-red'],
        #             width=4,
            
        #         ),
        #         layer='below'
        #     )
        # ],
    )
    return trace, trace2, trace3, layout

def return_weeknumber(fecha):
    return fecha.strftime("%Gww%V")




#%%###########################################################################
#                     02_02. FUNCIONES  PAGE)                        #
##############################################################################

# Layout con las listas de desviacion y fallos de registro/sensor S1
list_columns_layout = html.Div([
        # Lista de desviacion S1
        html.Div([
            dbc.Card([
                dbc.CardHeader([
                    html.H4('Desviaciones', 
                            className='text-center text-style'),
                ]),
                dbc.CardBody([
                    dbc.ListGroup(id='list-des'), 
                ], className='h-100 overflow-auto'),
            ], color='warning', outline=True, className='h-100'),
        ], className='col-6 px-2 h-100'),
        # Lista de fallos de registro/sensor S1
        html.Div([
            dbc.Card([
                dbc.CardHeader([
                    html.H4('Fallos de registro/sensor', 
                            className='text-center text-style'),
                ]),
                dbc.CardBody([
                    dbc.ListGroup(id='list-fal'), 
                ], className='h-100 overflow-auto'),
            ], color='danger', outline=True, className='h-100'),
        ], className='col-6 px-2 h-100'),
    ], className='row h-100 m-0')#row

# Devuelve el layout del gráfico de lina
def line_plot_layout(tab):
    # Título del gráfico 
    return [
        dbc.Card([
            dbc.CardHeader([html.H4('Análisis Temporal', className='text-style')], 
                           className='px-2 pt-1 p-0'),
            # Gráfico S1
            dbc.CardBody([
                dcc.Graph(
                    id="signal-plot",
                    figure=dict(
                        layout=dict(
                            plot_bgcolor=colors["graph-bg"],
                            paper_bgcolor=colors["graph-bg"],
                        )
                    ),
                    style={"height": "100%"},
                )
            ]),
        ], className='h-100')
    ]

# Devuelve el layout del histograma
def histo_layout(tab):
    return [
    # Título del histograma de S1
    dbc.Card([
        dbc.CardHeader([html.H4('Comparativa de operación', className='text-style')], 
                       className='px-2 pt-1 p-0'),
        dbc.CardBody([
            # Histograma de S1
            dcc.Graph(
                id="histogram",
                figure=dict(
                    layout=dict(
                        barmode='overlay',
                        plot_bgcolor=colors["graph-bg"],
                        paper_bgcolor=colors["graph-bg"],
                    )
                ),
                style={"height": "100%"},
            )]),
        ], className='h-100'),
    ]

# Layout del dropdown y la carta de información de la barra
def dropdown_cardinfo_layout(tab):
    if tab == 's1':
        columns = columns_s1
        default = 'Amina Flow'
    else:
        columns = columns_s2
        default = 'Flotation Column 02 Level'

    # Dropdown selector de señal
    layout = html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H4('Selector de señal', className='text-style m-0'),
            ], className='px-2 py-1'),
            dbc.CardBody([
                dcc.Dropdown(
                    id="signal-dropdown",
                    options=[{'label': x, 'value': x} for x in columns],
                    value=default,
                    style={
                        'color': colors['text-dropdown'],
                    },
                ),
                html.P("-: -", className='card-text text-left pt-3', id='signal_info'),
            ], className='h-100'),
        ], className='h-100'),
    ], className='h-100'),
    return layout
                
# Funcion que devuelve (aleatoriamente) las columnas que se desvian o tienen algun fallo
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
def get_cards_layout(columns, desviaciones, df):
    children = []
    if len(columns)>0:
        i = 1
        for column in columns:
            value = df[column][0]
            children.append(dbc.ListGroupItem([column, html.B(f' ({value:.2f})', 
                                                              style={"color": colors['text-highlight']})], 
                                              className='text-center', 
                                              style={"color": colors['text'], 
                                                     "font-size": size_font_cards, 
                                                     "font-family": family_font,}, 
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
    spaces = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
    if len(df)==1:
        text = dcc.Markdown('''**ID**: {} {} **Producto**: {} {} **Calidad**:
                               {} {} **Fecha**: {}'''.format(df['id'].iloc[0], spaces, df['product'].iloc[0],
                            spaces, df['quality'].iloc[0], spaces, df['date'].iloc[0]), 
                            style={"color": colors['text'], 
                                    "font-size": size_font_cards, 
                                    "font-family": family_font,})
    else:
        text = dcc.Markdown('''**ID**: - {} **Producto**: - {} **Calidad**:
                               - {} **Fecha**: - {}'''.format(spaces, spaces, 
                               spaces, spaces), 
                            style={"color": colors['text'], "font-size": size_font_cards, "font-family": family_font,})          
    return text

# Función que devuelve el texto que ira dentro del recuadro de información de la señal seleccionada page-2
def get_signal_info(id_data, column):
    df = pd.read_sql('SELECT * FROM signals WHERE id={}'.format(id_data), server_conn)
    df_all = pd.read_sql(('SELECT * FROM signals WHERE id>{} AND id<={}'.format(id_data-500, id_data+500)), server_conn)
    mean = df_all[column].mean()
    std = 2*df_all[column].std()
    if len(df)==1:
        text = dcc.Markdown('''**{}**: {:.2f}  
                            **Valor Medio**: {:.2f}  
                            **Limite superior**: {:.2f}  
                            **Limite inferior**: {:.2f}'''.format(column, df[column].iloc[0], 
                            mean, mean + std, mean - std),
                            style={"color": colors['text'], 
                                    "font-size": size_font_cards, 
                                    "font-family": family_font,})
    else:
        text = dcc.Markdown('''**-**: -  
                            **Valor Medio**: -  
                            **Limite superior**: -  
                            **Limite inferior**: -''', 
                            style={"color": colors['text'], "font-size": size_font_cards, "font-family": family_font,})        
    return text

# Función que devuelve el trace y layout del gráfico de la señal
def get_signal_plot(df, column, id_data):
    mean = df[column].mean()
    std = 2*df[column].std()
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
        margin={'t':25, 'b': 45, 'l': 30, 'r': 15},
        legend={
            "orientation": "h",
            "xanchor":"center",
            "yanchor":"top",
            "y":1.3, # play with it
            "x":0.2 # play with it
        },
        xaxis={
            "showline": True,
            "zeroline": False,
            "fixedrange": False,
            "ylabel": column,
        },
        yaxis={
            "range": [
                df[column].min() - 0.1*(df[column].max() - df[column].min()), 
                df[column].max() + 0.1*(df[column].max() - df[column].min()),
            ],
            "showgrid": True,
            "showline": True,
            "zeroline": False,
            "gridcolor": colors["grid"],
            "nticks": 10
        },
        shapes=[
            {
                'type':"line",
                # 'xref':df[df['id']==id_data['id']][column].iloc[0],
                'xref':'paper',
                'x0':0,
                'y0':mean - std,
                'x1':1,
                'y1':mean - std, 
                'line':dict(
                    color=colors['plantplot-l-red'],
                    width=4,
                    dash="dashdot",
            
                ),
            },
            {
                'type':"line",
                # 'xref':df[df['id']==id_data['id']][column].iloc[0],
                'xref':'paper',
                'x0':0,
                'y0':mean + std,
                'x1':1,
                'y1':mean + std, 
                'line':dict(
                    color=colors['plantplot-l-red'],
                    width=4,
                    dash="dashdot",
            
                ),
            },
        ],
    )
    return trace, trace2, layout

# Función que devuelve los traces y layout del histograma
def get_histogram(df, column, id_data):
    # Datos historicos del histograma S1
    df_hist = pd.DataFrame(df_raw).drop(df.index)
    mean = df[column].mean()
    std = 2*df[column].std()
    trace = dict(
        type="histogram",
        name='Último año',
        x=df_hist[column],
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
        name='Último mes',
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
        plot_bgcolor=colors["graph-bg"],
        paper_bgcolor=colors["graph-bg"],
        font={"color": colors['text'], "size": size_font, "family": family_font,},
        margin={'t':25, 'b': 45, 'l': 30, 'r': 15},
        legend={
            "orientation": "h",
            "xanchor":"center",
            "yanchor":"top",
            "y":1.3, # play with it
            "x":0.2 # play with it
        },
        yaxis={
            "gridcolor": colors["grid"],
        },
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
            },
            {
                'type':"line",
                # 'xref':df[df['id']==id_data['id']][column].iloc[0],
                'yref':'paper',
                'x0':mean - std,
                'y0':0,
                'x1':mean - std, 
                'y1':0.95,
                'line':dict(
                    color=colors['plantplot-l-red'],
                    width=4,
                    dash="dashdot",
            
                ),
            },
            {
                'type':"line",
                # 'xref':df[df['id']==id_data['id']][column].iloc[0],
                'yref':'paper',
                'x0':mean + std,
                'y0':0,
                'x1':mean + std,
                'y1':0.95,
                'line':dict(
                    color=colors['plantplot-l-red'],
                    width=4,
                    dash="dashdot",
            
                ),
            }
        ],
    )
    return trace, trace2, layout

#%%###########################################################################
#                              03. LAYOUT                                    #
##############################################################################

# Barra de navegacion de la aplicacion
navbar = dbc.Navbar([
            html.A(
                # Imagen con el logo de Dattium que nos llevara a la página principal de la App
                # Use row and col to control vertical alignment of logo / brand
                html.Img(src=app.get_asset_url(navbar_image),\
                                          height=navbar_logo_size),
                href="/home",
                className='float-right col-2 h-100'
            ),
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Home", href="/home", style={"color":colors['text']})),
                dbc.NavItem(dbc.NavLink("Reports", href="/reports", style={"color":colors['text']}, id='report_page_nav')),
                dbc.NavItem(dbc.NavLink("Comparativas", href="/comparativas", style={"color":colors['text']}, id='comparativas_page_nav')),
            ], className=''),
    ], className='lg py-1 px-1', color=colors['navbar'], style={"height": '5vh'})
    
# Layout de la app
app.layout = html.Div([
    # Store, sirve para guardar datos y poder acceder a ellos entre paginas
    dcc.Store(id='store-p2-layout'),
    dcc.Store(id='store-id-clicked'),
    dcc.Store(id='store-update-signal'),
    dcc.Store(id='n_clicks_update'),
    dcc.Store(id='store-heatmap'),
    # Sirve para poder crear distintas paginas www.dattiumapp.com/seccions o www.dattiumapp.com/reports
    dcc.Location(id='url', refresh=False),
    navbar,
    # Contenido de las paginas
    html.Div(id='page-content', className='w-100', style={"height": '92vh'}),
    html.Footer([
        html.Div([
            '© 2020 Copyright: Dattium Technology'
        ], className='text-center')
    ], className='py-1', style={"height": '3vh'}),
], className='min-vh-100 vh-100 w-100')

# Update the index
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/home':
        return home_page_layout
    elif pathname == '/seccions':
        return seccions_page_layout
    elif pathname == '/reports':
         return reports_page_layout
    elif pathname == '/comparativas':
        return comparativas_page_layout
    else:
        return home_page_layout
    # You could also return a 404 "URL not found" page here


#%%###########################################################################
#                             04_1. HOME-PAGE                                #
##############################################################################
    
# Pagina 1, imagen de la planta y un gráfico general con el comportamiento de esta

home_page_layout = html.Div([
    dbc.Tabs([
        dbc.Tab(label='Tiempo Real', tab_id='real'),
        dbc.Tab(label='Historico', tab_id='hist'),
    ], id='home-page-tabs', active_tab='real'), 
    html.Div(home_layout, id='home-page-content', style={"height": "calc(100% - 40px)"}),
    dcc.Interval(
        id="signal-update",
        interval=int(GRAPH_INTERVAL),
        n_intervals=0,
    ),
], className='h-100')

#%%###########################################################################
#                         04_2. HOME-PAGE CALLBACKS                          #
##############################################################################

@app.callback(
    [Output("date-min", "date"), Output("hour-min", "value"), Output("min-min", "value"),
     Output("date-max", "date"), Output("hour-max", "value"), Output("min-max", "value")],
    [Input("hour-min-up", "n_clicks_timestamp"),Input("min-min-up", "n_clicks_timestamp"),
     Input("hour-min-down", "n_clicks_timestamp"), Input("min-min-down", "n_clicks_timestamp"),
     Input("hour-max-up", "n_clicks_timestamp"),Input("min-max-up", "n_clicks_timestamp"),
     Input("hour-max-down", "n_clicks_timestamp"), Input("min-max-down", "n_clicks_timestamp"),
     Input('calendar-heatmap', 'clickData')],
    [State("date-min", "date"), State("hour-min", "value"), State("min-min", "value"),
     State("date-max", "date"), State("hour-max", "value"), State("min-max", "value"),]
)
def update_date_min(hour_up_min, min_up_min, hour_down_min, min_down_min,
                    hour_up_max, min_up_max, hour_down_max, min_down_max,
                    click_data, fecha_min, hour_min, minute_min,
                    fecha_max, hour_max, minute_max):
    
    ctx = dash.callback_context
    clicked = ctx.triggered[0]['prop_id'].split('.')[0]
    if clicked == 'calendar-heatmap':
        if click_data is not None:
            if 'points' in click_data.keys():
                if 'text' in click_data['points'][0].keys():
                    fecha = click_data['points'][0]['text']
                    date_out_min = datetime.strptime(fecha + " 00:00",'%Y-%m-%d %H:%M')
                    date_out_max = datetime.strptime(fecha + " 23:59",'%Y-%m-%d %H:%M')
    else:
        values_min = {"hour-min-up":[1,0], 
                      "min-min-up":[0,1], 
                      "hour-min-down":[-1,0], 
                      "min-min-down":[0,-1],
                      "hour-max-up":[0,0], 
                      "min-max-up":[0,0], 
                      "hour-max-down":[0,0], 
                      "min-max-down":[0,0],
                      "calendar-heatmap":[0,0],
                     }
        values_max = {"hour-min-up":[0,0], 
                      "min-min-up":[0,0], 
                      "hour-min-down":[0,0], 
                      "min-min-down":[0,0],
                      "hour-max-up":[1,0], 
                      "min-max-up":[0,1], 
                      "hour-max-down":[-1,0], 
                      "min-max-down":[0,-1],
                      "calendar-heatmap":[0,0],
                     }
        date_out_min = datetime.strptime(fecha_min + " " + str(hour_min).zfill(2) + ":"+ str(minute_min).zfill(2),
                                     '%Y-%m-%d %H:%M')
        date_out_min = date_out_min + timedelta(hours=values_min[clicked][0], minutes=values_min[clicked][1])
        
        date_out_max = datetime.strptime(fecha_max + " " + str(hour_max).zfill(2) + ":"+ str(minute_max).zfill(2),
                                     '%Y-%m-%d %H:%M')
        date_out_max = date_out_max + timedelta(hours=values_max[clicked][0], minutes=values_max[clicked][1])
    return [date_out_min.date(), str(date_out_min.hour).zfill(2), str(date_out_min.minute).zfill(2),
            date_out_max.date(), str(date_out_max.hour).zfill(2), str(date_out_max.minute).zfill(2)]

# Callback que modifica el contenido de la página en función del Tab activo.
@app.callback(
    [Output('selector-fechas-container', 'className'), Output('button-container', 'className'), 
     Output('bottom_seccion_hist', 'className'), Output('bottom_seccion_real', 'className'),
     Output('plant-plot-container', 'style'), Output('filters-container', 'style')],
    [Input("home-page-tabs", "active_tab"), Input('calendar-heatmap', 'clickData')],
)
def render_tab_content(tab, clicked):
    ctx = dash.callback_context
    clicked = ctx.triggered[0]['prop_id'].split('.')[0]
    if (tab == 'hist') or (clicked == 'calendar-heatmap'):
        fechas = 'h-100' #dict(height='100%', visibility='visible')
        button = 'invisible' #dict(height='0%', visibility='hidden')
        bottom_seccion_real = 'invisible' #dict(height='0%', visibility='hidden')
        bottom_seccion_hist =  'h-100' #dict(height='100%', visibility='visible')
        plant_plot_graph_h = dict(height='66%')
        plant_plot_filter_h = dict(height='34%')
    else:
        button = 'row w-100 pr-3 pb-1 h-100' #dict(height='100%', visibility='visible')
        fechas = 'invisible' #dict(height='0%', visibility='hidden')
        bottom_seccion_real = 'h-100'#dict(height='100%', visibility='visible')
        bottom_seccion_hist =  'invisible'#dict(height='0%', visibility='hidden')
        plant_plot_graph_h = dict(height='88%')
        plant_plot_filter_h = dict(height='12%')
    return fechas, button, bottom_seccion_hist, bottom_seccion_real, plant_plot_graph_h, plant_plot_filter_h

# Callback que actualiza el gráfica cada X segundos o rango de fechas
@app.callback(
    [Output("plant-plot", "figure")], 
    [Input("search-button", "n_clicks"), Input("signal-update", "n_intervals"), Input("home-page-tabs", "active_tab")],
    [State("date-min", "date"), State("date-max", "date"), State('hour-min', 'value'),
     State('hour-max', 'value'), State('min-min', 'value'), State('min-max', 'value')]
)
def gen_signal_hist(n_clicks, interval, tab, datemin, datemax, hourmin, hourmax, minmin, minmax):
    """
    Generate the signal graph.
    :params datemin: update the graph based on a date interval
    :params datemax: update the graph based on a date interval
    """  
    
    if tab == "hist":
        datemin = "'" + datemin + " " + str(hourmin).zfill(2) + ":"+ str(minmin).zfill(2) +"'"
        datemax = "'" + datemax + " " + str(hourmax).zfill(2) + ":"+ str(minmin).zfill(2) +"'"
        # Consulta a postgreSQL que devuelve
        df = pd.read_sql(("SELECT * FROM signals WHERE date >= %s AND date < %s" % (datemin, datemax)), server_conn)
        trace, trace2, trace3, layout = get_plant_plot(df)
        
    else:
        # Consulta a postgreSQL que devuelve las 100 primeras filas con un offset que incrementa cada GRAPH_INTERVALS ms
        df = pd.read_sql(('SELECT * FROM signals LIMIT 100 OFFSET %s' % (interval)), server_conn)
        trace, trace2, trace3, layout = get_plant_plot(df)

    return [dict(data=[trace, trace2, trace3], layout=layout)]

# Callback que pausa la actualización automática del gráfico
@app.callback(
    [Output("signal-update", "disabled"), Output("pause-button", "children"), Output('store-update-signal', 'data'), Output('n_clicks_update', 'data')], 
    [Input("pause-button", "n_clicks"), Input("home-page-tabs", "active_tab")],
    [State("signal-update", "disabled"), State('store-update-signal', 'data'), State('n_clicks_update', 'data')]
)
def enable_update(n, tab, disabled, store, n_clicks):
    if n is None:
        n = 0
    # actual_disabled=True
    # children = 'Play'
    if disabled is None:
        disabled = True
    if store is None:
        store = disabled
    if n_clicks is None:
        n_clicks = -1
    if tab == 'hist':
        actual_disabled = True
        children = "Play"
    else:
        if n_clicks == n:
            if store:
                children="Play"
                actual_disabled = True
                disabled = actual_disabled
            else:
                children="Pause"
                actual_disabled = False
                disabled = actual_disabled
        else:
            if disabled:
                children="Pause"
                actual_disabled = False
                disabled = actual_disabled
            else: 
                children="Play"
                actual_disabled = True
                disabled = actual_disabled
    return actual_disabled, children, disabled, n

# Callback al clicar en un punto del gráfico, guarda en los Store el id del punto y el layout de las señales
# que se van a mostrar como desviaciones/fallos
@app.callback([Output('store-p2-layout', 'data'), Output('url', 'pathname'), Output('store-id-clicked', 'data')],
              [Input('plant-plot', 'clickData')])
def change_page(click_data):
    if click_data is not None:
        des_s1 =  dbc.ListGroupItem("No hay ningúna señal desviada", id="desviacion-s1-item", className='text-center')
        des_s2 =  dbc.ListGroupItem("No hay ningúna señal desviada", id="desviacion-s2-item", className='text-center')
        fal_s1 =  dbc.ListGroupItem("No hay ningúna señal con fallos de registro/sensor", id="fallos-s1-item", className='text-center')
        fal_s2 =  dbc.ListGroupItem("No hay ningúna señal con fallos de registro/sensor", id="fallos-s2-item", className='text-center')
        point_id = -1
        if 'points' in click_data.keys():
            if 'id' in click_data['points'][1].keys():
                point_id = click_data['points'][1]['id']
                selected_data = pd.read_sql(('SELECT * FROM signals WHERE id=%s' % (point_id)), server_conn)
                [col_fal_s1, col_des_s1] = get_columns(selected_data, 's1')
                [col_fal_s2, col_des_s2] = get_columns(selected_data, 's2')
                des_s1 = get_cards_layout(col_des_s1, True, selected_data)
                fal_s1 = get_cards_layout(col_fal_s1, False, selected_data)
                des_s2 = get_cards_layout(col_des_s2, True, selected_data)
                fal_s2 = get_cards_layout(col_fal_s2, False, selected_data)
        return [{'des_s1': (des_s1), 'fal_s1': (fal_s1), 'des_s2': (des_s2), 'fal_s2': (fal_s2)}, '/seccions', {'id': point_id}]

@app.callback(
    [Output("calendar-heatmap", "figure"), Output("chm_info_card1", "children"),
     Output("chm_info_card2", "children"), Output("chm_info_card3", "children")],
    [Input("chm-tabs", "active_tab")],
)
def render_chm_tab_content(active_tab):    
        return [calendar_heatmap(df_raw, active_tab), chm_card_content(1),
                chm_card_content(2), chm_card_content(3)]

@app.callback(
    Output("home-page-tabs", "active_tab"),
    [Input('calendar-heatmap', 'clickData')],
)
def change_tab(clicked):
    if clicked is not None:
        return 'hist'

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
        # # Tab S1
        dbc.Tab(label='Horno', tab_id='s1'),
        # Tab S2
        dbc.Tab(label='Caseta', tab_id='s2'),
    ], id='seccion-tabs', active_tab='s1'),
    html.Div([
        html.Div([
            # Listas de desviacion y fallos de resgistros/sensores
            html.Div([
                # Carta informativa de la ID seleccionada S1
                html.Div([
                    dbc.Card([
                        dbc.CardHeader([
                            html.H4('Información de la barra', className='text-style m-0'),
                        ], className='px-2 py-1'),
                        dbc.CardBody([
                            # get_card_info_layout(id, default)
                            html.P("ID: ********", className='card-text text-left', id='card_info_id'),
                        ], className='h-100'),
                    ], className='h-100'),
                ], className='h-25 pb-2'),
                # Lista de señales con desviaciones/fallos
                dbc.Card([
                    dbc.CardHeader([html.H5('Señales con desviación o errores', className='py-0 text-style')], className='px-2 pt-1 p-0'),
                    dbc.CardBody([
                        list_columns_layout
                    ], className='h-100')
                ], className='h-75')
            ], className='col-7 px-1 h-100', id='list_columns'),
            # Imagen
            html.Div([
                dbc.Card([
                    dbc.CardHeader([html.H5('Diagram', className='py-0 text-style')], className='px-2 pt-1 p-0'),
                    dbc.CardBody([
                        html.Img(src=app.get_asset_url(f"plant-s1.png"), id='seccion-img',\
                                 className='mx-auto d-block h-100 w-100'),
                        html.I(className="fas fa-exclamation-triangle warning-icon", style={"top": "35%", "left": "76%"}),
                        html.I(className="fas fa-exclamation-triangle warning-yellow-icon", style={"top": "56%", "left": "80.5%"}),
                        html.I(className="fas fa-exclamation-triangle warning-icon", style={"top": "49%", "left": "63.5%"}),
                        # html.I(className="fas fa-check-circle check-icon", style={"top": "12%", "left": "40%"}),
                        # html.Div(className='red-dot'),
                        # html.Div(className='green-dot'),
                    ], className='h-100')
                ], className='h-100')
            ], className='h-100 col-5 px-1')
            
            # html.Div(className='col-1'),
        ], className='row w-100 h-50 pb-1'),
        # Plot señal + histograma
        html.Div([    
            #Dropdown + info card
            html.Div(
                dropdown_cardinfo_layout('s1')
            , className='col-2 h-100 px-1', id='dropdown_card_info'),      
            
            # Plot señal S1
            html.Div(
                line_plot_layout('s1')               
            ,className='signal-plot col-5 h-100 px-1'),
            
            # Plot histograma S1
            html.Div(
                histo_layout('s1')
            ,className='histogram-plot col-5 h-100 px-1'),
        ], id='graficos', className='row w-100 h-50 py-1')
    ], id='seccion-content', className='py-1 pl-4', style=dict(height='calc(100% - 40px)'))
], className = 'h-100 w-100')

#%%###########################################################################
#                        05_2. SECCIONS-PAGE CALLBACKS                       #
##############################################################################


@app.callback(
    [Output("signal-dropdown", "options"), Output("signal-dropdown", "value"), \
     Output("seccion-img", "src")],
    [Input("seccion-tabs", "active_tab")],
)
def render_seccion_tab_content(active_tab):
    if active_tab == 's1':
        columns = [{'label': x, 'value': x} for x in columns_s1]
        default = 'Amina Flow'
        img = 'plant-s1.png'
    else:
        columns = [{'label': x, 'value': x} for x in columns_s2]
        default = 'Flotation Column 02 Level' 
        img = 'plant-s2.png'
    return [columns, default, app.get_asset_url(img)]

# Callback que actualiza la targeta de información de ID S1
@app.callback([Output('card_info_id', 'children'), Output('signal_info', 'children')],
              [Input('store-id-clicked', 'modified_timestamp'), Input("signal-dropdown", "value"),\
               Input("seccion-tabs", "active_tab")],
              [State('store-id-clicked', 'data')])
def modify_info_card_s1(timestamp, column, active_tab, id_data):  
    spaces = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
    return_data = dcc.Markdown('''**ID**: - {} **Producto**: - {} **Calidad**:
                               - {} **Fecha**: - {}'''.format(spaces, spaces, 
                               spaces, spaces), 
                            style={"color": colors['text'], "font-size": size_font_cards, "font-family": family_font,})   
    return_data_signal = dcc.Markdown('''**-**: -  
                            **Valor Medio**: -  
                            **Limite superior**: -  
                            **Limite inferior**: -''', 
                            style={"color": colors['text'], "font-size": size_font_cards, "font-family": family_font,})
    if id_data is not None:
        if 'id' in id_data.keys():
            return_data = get_card_info_layout(id_data['id'], column)
            return_data_signal = get_signal_info(id_data['id'], column)
    return return_data, return_data_signal
    
# Callback que actualiza la lista de desviaciones de S1
@app.callback(Output('list-des', 'children'),
              [Input('store-p2-layout', 'modified_timestamp'), Input("seccion-tabs", "active_tab")],
              [State('store-p2-layout', 'data')])
def modify_lists_des(timestamp, active_tab, data):
    no_data = dbc.ListGroupItem("No hay ningúna señal desviada", color='success', className='text-center')
    if data is not None:
        return_data = no_data
        if 'des_' + active_tab in data.keys():
            return_data = data['des_' + active_tab]
        return return_data
    else: 
        return no_data

# Callback que actualiza la lista de fallos de S1
@app.callback(Output('list-fal', 'children'),
              [Input('store-p2-layout', 'modified_timestamp'), Input("seccion-tabs", "active_tab")],
              [State('store-p2-layout', 'data')])
def modify_lists_fal(timestamp, active_tab, data):
    no_data = dbc.ListGroupItem("No hay ningúna señal con fallos de registro/sensor",\
                                color='success', className='text-center')
    if data is not None:
        return_data = no_data
        if 'fal_' + active_tab in data.keys():
            return_data = data['fal_' + active_tab]
        return return_data
    else: 
        return no_data


# Callback que actualiza el plot y el histograma de la señal al cambiar de señal con el dropdown de S1
@app.callback(
    [Output("signal-plot", "figure"), Output("histogram", "figure")], 
    [Input("signal-dropdown", "value"), Input("seccion-tabs", "active_tab")],
    [State('store-id-clicked', 'data')]
)
def gen_signal_s1(column, active_tab, id_data):
    
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


#%%###########################################################################
#                           06_1. REPORTS-PAGE                               #
##############################################################################

# Página con los informes por seccion y producto
reports_page_layout = html.Div([
    html.Div([
        dbc.Tabs([
            dbc.Tab(label='Resumen', tab_id='all'),
        ], id='summary-tabs', active_tab='all', className='Tabs1 invisible', style=dict(height='0')),
        html.Div([
            dbc.Card([
                dbc.CardHeader([html.H5('Selector de fechas', className='py-0 text-style')], className='px-2 pt-1 p-0'),
                dbc.CardBody([
                    html.Div([selector_fecha], className='h-100 col-11 m-0'),
                    html.Div([
                        html.I(className="fas fa-caret-up fa-2x text-center col-2 invisible"),
                        html.Div([
                            html.I(id="hour-min-up", n_clicks=0, n_clicks_timestamp = -1,
                                className="far fa-save fa-3x text-center col-1 align-middle",
                                style={"cursor": "pointer"}),
                            dcc.DatePickerSingle(date=datetime.date(date_max), display_format='DD-MM-YYYY',
                                                 className='invisible h-100 col-2', persistence=True),
                        ], className='row h-50 pb-2 m-0'),
                    ], className='h-100 col-1  m-0 pl-5')
                ], className='h-100 pb-2 row m-0'),
            ], className='h-100')
        ], className='px-3 pt-2', style={"height": "22%"}),
        html.Div(id='summary-tab-content', style=dict(height='78%'))
    ], className='h-100'),
    
    # INVISIBLE
    dcc.Graph(
        id='calendar-heatmap',
        className='invisible'
    ),
    dbc.Tabs([
        dbc.Tab(label='Tiempo Real', tab_id='real'),
        dbc.Tab(label='Historico', tab_id='hist'),
    ], className='invisible', id='home-page-tabs', active_tab='real'), 
], className='h-100') 

#%%###########################################################################
#                      06_2. REPORTS-PAGE CALLBACKS                          #
##############################################################################

# Callback que modifica el contenido de la página en función del Tab activo.
@app.callback(
    Output("summary-tab-content", "children"),
    [Input("summary-tabs", "active_tab"), Input('report_page_nav', 'n_clicks')],
    [State("date-min", "date"), State("date-max", "date"), State('hour-min', 'value'),
     State('hour-max', 'value'), State('min-min', 'value'), State('min-max', 'value')],
)
def render_summary_tab_content(active_tab, n_clicks, datemin, datemax, hourmin, hourmax, minmin, minmax):  

    datemin = "'" + datemin + " " + str(hourmin).zfill(2) + ":"+ str(minmin).zfill(2) +"'"
    datemax = "'" + datemax + " " + str(hourmax).zfill(2) + ":"+ str(minmin).zfill(2) +"'"
    # Consulta a postgreSQL que devuelve
    df = pd.read_sql(("SELECT * FROM signals WHERE date >= %s AND date < %s" % (datemin, datemax)), server_conn)

    if active_tab == "products":
        return summary_tab_layout('products', df, True)
    elif active_tab == "seccions":
        return summary_tab_layout('seccions', df, True)
    else: 
        return [summary_tab_layout('products', df, False),
                summary_tab_layout('seccions', df, False)]
    
@app.callback(
    Output("time-plot-products", "figure"),
    [Input("checklist-product", "value"), Input("checklist-quality", "value"), 
     Input("search-button", "n_clicks"), Input("checklist-xaxis-product", "value"),
     Input("home-page-tabs", "active_tab")],
    [State("date-min", "date"), State("date-max", "date"), State('hour-min', 'value'),
     State('hour-max', 'value'), State('min-min', 'value'), State('min-max', 'value')],
)
def checklist_product_trace(ckd_product, ckd_quality, n_clicks, xaxis, active_tab_hp, datemin, datemax, hourmin, hourmax, minmin, minmax):
    
    datemin = "'" + datemin + " " + str(hourmin).zfill(2) + ":"+ str(minmin).zfill(2) +"'"
    datemax = "'" + datemax + " " + str(hourmax).zfill(2) + ":"+ str(minmin).zfill(2) +"'"
    # Consulta a postgreSQL que devuelve
    df = pd.read_sql(("SELECT * FROM signals WHERE date >= %s AND date < %s" % (datemin, datemax)), server_conn)  
    
    trace, layout = liner_graph_product_summary(df, ckd_product, ckd_quality, xaxis)
    return dict(data=[trace], layout=layout)

@app.callback(
    Output("time-plot-seccions", "figure"),
    [Input("checklist-seccion", "value"), Input("search-button", "n_clicks"),
     Input("checklist-xaxis-seccion", "value"), Input("home-page-tabs", "active_tab")],
    [State("date-min", "date"), State("date-max", "date"), State('hour-min', 'value'),
     State('hour-max', 'value'), State('min-min', 'value'), State('min-max', 'value')],
)
def checklist_seccion_trace(ckd_seccion, n_clicks, xaxis, active_tab_hp, datemin, datemax, hourmin, hourmax, minmin, minmax):
    datemin = "'" + datemin + " " + str(hourmin).zfill(2) + ":"+ str(minmin).zfill(2) +"'"
    datemax = "'" + datemax + " " + str(hourmax).zfill(2) + ":"+ str(minmin).zfill(2) +"'"
    # Consulta a postgreSQL que devuelve
    df = pd.read_sql(("SELECT * FROM signals WHERE date >= %s AND date < %s" % (datemin, datemax)), server_conn)  
    
    trace, layout = liner_graph_seccions_summary(df, ckd_seccion, xaxis)
    return dict(data=[trace], layout=layout)

@app.callback(
    Output("bar-plot-products", "figure"),
    [Input("search-button", "n_clicks"), Input("home-page-tabs", "active_tab")],
    [State("date-min", "date"), State("date-max", "date"), State('hour-min', 'value'),
     State('hour-max', 'value'), State('min-min', 'value'), State('min-max', 'value')],
)
def bar_graph_product(n_clicks, active_tab_hp, datemin, datemax, hourmin, hourmax, minmin, minmax):
    
    datemin = "'" + datemin + " " + str(hourmin).zfill(2) + ":"+ str(minmin).zfill(2) +"'"
    datemax = "'" + datemax + " " + str(hourmax).zfill(2) + ":"+ str(minmin).zfill(2) +"'"
    # Consulta a postgreSQL que devuelve
    df = pd.read_sql(("SELECT * FROM signals WHERE date >= %s AND date < %s" % (datemin, datemax)), server_conn)  
    
    trace, layout = bar_graph_product_summary(df)
    return dict(data=trace, layout=layout)

@app.callback(
    Output("bar-plot-seccions", "figure"),
    [Input("search-button", "n_clicks"), Input("home-page-tabs", "active_tab")],
    [State("date-min", "date"), State("date-max", "date"), State('hour-min', 'value'),
     State('hour-max', 'value'), State('min-min', 'value'), State('min-max', 'value')],
)
def bar_graph_seccion(n_clicks, active_tab_hp, datemin, datemax, hourmin, hourmax, minmin, minmax):
    
    datemin = "'" + datemin + " " + str(hourmin).zfill(2) + ":"+ str(minmin).zfill(2) +"'"
    datemax = "'" + datemax + " " + str(hourmax).zfill(2) + ":"+ str(minmin).zfill(2) +"'"
    # Consulta a postgreSQL que devuelve
    df = pd.read_sql(("SELECT * FROM signals WHERE date >= %s AND date < %s" % (datemin, datemax)), server_conn)  
    
    trace, layout = bar_graph_seccions_summary(df)
    return dict(data=trace, layout=layout)

#%%###########################################################################
#                         07. COMPARATIVA-PAGE                             #
##############################################################################

# Página con los informes por seccion y producto
comparativas_page_layout = html.Div([
    html.Div([
        html.Div([
            dbc.Card([
                dbc.CardHeader([html.H5('Selector de fechas 1', className='py-0 text-style', id="selector-header1")], className='px-2 pt-1 p-0'),
                dbc.CardBody([
                    html.Div([selector_de_fechas('-1', datetime(2017, 4, 1, 1, 0, 0), datetime(2017, 5, 1, 1, 0, 0), True)], className='h-100 m-0'),
                ], className='h-100 pb-2 m-0 px-2'),
            ], className='h-100'),
        ], className='h-100 col-6 pl-2 pr-1'),
        html.Div([
            dbc.Card([
                dbc.CardHeader([html.H5('Selector de fechas 2', className='py-0 text-style', id="selector-header2")], className='px-2 pt-1 p-0'),
                dbc.CardBody([
                    html.Div([selector_de_fechas('-2', datetime(2017, 5, 1, 1, 0, 0), datetime(2017, 6, 1, 1, 0, 0), True)], className='h-100 m-0'),
                ], className='h-100 pb-2 m-0'),
            ], className='h-100'),
        ], className='h-100 col-6 pl-1 pr-2'),
    ], className='px-3 pt-2 row m-0 pb-2', style={"height": "28%"}),
    dbc.Tabs([
        dbc.Tab(label='Horno', tab_id='s1'),
        dbc.Tab(label='Casetas', tab_id='s2'),
        dbc.Tab(label='Placa de enfriamiento', tab_id='s3'),
    ], id='seccion-tabs', active_tab='s1', className='pt-2'),
    html.Div([
        html.Div([
            html.Div([
                histograma_layout(1),
            ], className='col-4 h-100 pl-2 pr-1 pt-2'),
            html.Div([
                histograma_layout(2),
            ], className='col-4 h-100 pl-1 pr-1 pt-2'),
            html.Div([
                histograma_layout(3),
            ], className='col-4 h-100 pl-1 pr-2 pt-2'),
        ], className='row m-0 h-50'),
        html.Div([
            html.Div([
                histograma_layout(4),
            ], className='col-4 h-100 pl-2 pr-1 pt-2'),
            html.Div([
                histograma_layout(5),
            ], className='col-4 h-100 pl-1 pr-1 pt-2'),
            html.Div([
                histograma_layout(6),
            ], className='col-4 h-100 pl-1 pr-2 pt-2'),
        ], className='row m-0 h-50')
    ], style={"height": "calc(72% - 40px)"})
], className='h-100 pb-2')



@app.callback(
    [Output("date-min-1", "date"), Output("hour-min-1", "value"), Output("min-min-1", "value"),
      Output("date-max-1", "date"), Output("hour-max-1", "value"), Output("min-max-1", "value")],
    [Input("hour-min-up-1", "n_clicks_timestamp"),Input("min-min-up-1", "n_clicks_timestamp"),
      Input("hour-min-down-1", "n_clicks_timestamp"), Input("min-min-down-1", "n_clicks_timestamp"),
      Input("hour-max-up-1", "n_clicks_timestamp"),Input("min-max-up-1", "n_clicks_timestamp"),
      Input("hour-max-down-1", "n_clicks_timestamp"), Input("min-max-down-1", "n_clicks_timestamp")],
    [State("date-min-1", "date"), State("hour-min-1", "value"), State("min-min-1", "value"),
      State("date-max-1", "date"), State("hour-max-1", "value"), State("min-max-1", "value"),]
)
def update_date_1(hour_up_min, min_up_min, hour_down_min, min_down_min,
                    hour_up_max, min_up_max, hour_down_max, min_down_max,
                    fecha_min, hour_min, minute_min,
                    fecha_max, hour_max, minute_max):
    
    ctx = dash.callback_context
    clicked = ctx.triggered[0]['prop_id'].split('.')[0]
    values_min = {"hour-min-up-1":[1,0], 
                  "min-min-up-1":[0,1], 
                  "hour-min-down-1":[-1,0], 
                  "min-min-down-1":[0,-1],
                  "hour-max-up-1":[0,0], 
                  "min-max-up-1":[0,0], 
                  "hour-max-down-1":[0,0], 
                  "min-max-down-1":[0,0],
                  "calendar-heatmap-1":[0,0],
                  }
    values_max = {"hour-min-up-1":[0,0], 
                  "min-min-up-1":[0,0], 
                  "hour-min-down-1":[0,0], 
                  "min-min-down-1":[0,0],
                  "hour-max-up-1":[1,0], 
                  "min-max-up-1":[0,1], 
                  "hour-max-down-1":[-1,0], 
                  "min-max-down-1":[0,-1],
                  "calendar-heatmap-1":[0,0],
                  }
    date_out_min = datetime.strptime(fecha_min + " " + str(hour_min).zfill(2) + ":"+ str(minute_min).zfill(2),
                                  '%Y-%m-%d %H:%M')
    date_out_min = date_out_min + timedelta(hours=values_min[clicked][0], minutes=values_min[clicked][1])
    
    date_out_max = datetime.strptime(fecha_max + " " + str(hour_max).zfill(2) + ":"+ str(minute_max).zfill(2),
                                  '%Y-%m-%d %H:%M')
    date_out_max = date_out_max + timedelta(hours=values_max[clicked][0], minutes=values_max[clicked][1])
    return [date_out_min.date(), str(date_out_min.hour).zfill(2), str(date_out_min.minute).zfill(2), 
            date_out_max.date(), str(date_out_max.hour).zfill(2), str(date_out_max.minute).zfill(2)]

@app.callback(
    [Output("date-min-2", "date"), Output("hour-min-2", "value"), Output("min-min-2", "value"),
      Output("date-max-2", "date"), Output("hour-max-2", "value"), Output("min-max-2", "value")],
    [Input("hour-min-up-2", "n_clicks_timestamp"),Input("min-min-up-2", "n_clicks_timestamp"),
      Input("hour-min-down-2", "n_clicks_timestamp"), Input("min-min-down-2", "n_clicks_timestamp"),
      Input("hour-max-up-2", "n_clicks_timestamp"),Input("min-max-up-2", "n_clicks_timestamp"),
      Input("hour-max-down-2", "n_clicks_timestamp"), Input("min-max-down-2", "n_clicks_timestamp")],
    [State("date-min-2", "date"), State("hour-min-2", "value"), State("min-min-2", "value"),
      State("date-max-2", "date"), State("hour-max-2", "value"), State("min-max-2", "value")]
)
def update_date_2(hour_up_min, min_up_min, hour_down_min, min_down_min,
                    hour_up_max, min_up_max, hour_down_max, min_down_max,
                    fecha_min, hour_min, minute_min,
                    fecha_max, hour_max, minute_max):
    
    ctx = dash.callback_context
    clicked = ctx.triggered[0]['prop_id'].split('.')[0]
    values_min = {"hour-min-up-2":[1,0], 
                  "min-min-up-2":[0,1], 
                  "hour-min-down-2":[-2,0], 
                  "min-min-down-2":[0,-2],
                  "hour-max-up-2":[0,0], 
                  "min-max-up-2":[0,0], 
                  "hour-max-down-2":[0,0], 
                  "min-max-down-2":[0,0],
                  "calendar-heatmap-2":[0,0],
                  }
    values_max = {"hour-min-up-2":[0,0], 
                  "min-min-up-2":[0,0], 
                  "hour-min-down-2":[0,0], 
                  "min-min-down-2":[0,0],
                  "hour-max-up-2":[1,0], 
                  "min-max-up-2":[0,1], 
                  "hour-max-down-2":[-2,0], 
                  "min-max-down-2":[0,-2],
                  "calendar-heatmap-2":[0,0],
                  }
    date_out_min = datetime.strptime(fecha_min + " " + str(hour_min).zfill(2) + ":"+ str(minute_min).zfill(2),
                                  '%Y-%m-%d %H:%M')
    date_out_min = date_out_min + timedelta(hours=values_min[clicked][0], minutes=values_min[clicked][1])
    
    date_out_max = datetime.strptime(fecha_max + " " + str(hour_max).zfill(2) + ":"+ str(minute_max).zfill(2),
                                  '%Y-%m-%d %H:%M')
    date_out_max = date_out_max + timedelta(hours=values_max[clicked][0], minutes=values_max[clicked][1])
    return [date_out_min.date(), str(date_out_min.hour).zfill(2), str(date_out_min.minute).zfill(2),
            date_out_max.date(), str(date_out_max.hour).zfill(2), str(date_out_max.minute).zfill(2)]

# Callback que modifica el contenido de la página en función del Tab activo.
@app.callback(
    [Output("histogram-1", "figure"), Output("histogram-2", "figure"), Output("histogram-3", "figure"),
     Output("histogram-4", "figure"), Output("histogram-5", "figure"), Output("histogram-6", "figure"),
     Output("hist-header-1", "children"), Output("hist-header-2", "children"), Output("hist-header-3", "children"),
     Output("hist-header-4", "children"), Output("hist-header-5", "children"), Output("hist-header-6", "children")],
    # Output("hist-header-2", "children"),
    [Input("search-button-1", "n_clicks"), Input('search-button-2', 'n_clicks'),
      Input("seccion-tabs", "active_tab")],
    [State("date-min-1", "date"), State("date-max-1", "date"), State('hour-min-1', 'value'),
      State('hour-max-1', 'value'), State('min-min-1', 'value'), State('min-max-1', 'value'),
      State("date-min-2", "date"), State("date-max-2", "date"), State('hour-min-2', 'value'),
      State('hour-max-2', 'value'), State('min-min-2', 'value'), State('min-max-2', 'value')]
)
def histogram_traces(n_clicks1, n_clicks2, active_tab, datemin_1, datemax_1, 
                                hourmin_1, hourmax_1, minmin_1, minmax_1, datemin_2, 
                                datemax_2, hourmin_2, hourmax_2, minmin_2, minmax_2):  
    if active_tab == 's2':
        columns = columns2
    elif active_tab == 's3':
        columns = columns3
    else:
        columns = columns1
    datemin_1 = "'" + datemin_1 + " " + str(hourmin_1).zfill(2) + ":"+ str(minmin_1).zfill(2) +"'"
    datemax_1 = "'" + datemax_1 + " " + str(hourmax_1).zfill(2) + ":"+ str(minmin_1).zfill(2) +"'"
    datemin_2 = "'" + datemin_2 + " " + str(hourmin_2).zfill(2) + ":"+ str(minmin_2).zfill(2) +"'"
    datemax_2 = "'" + datemax_2 + " " + str(hourmax_2).zfill(2) + ":"+ str(minmin_2).zfill(2) +"'"
    # Consulta a postgreSQL que devuelve
    df1 = pd.read_sql(("SELECT * FROM signals WHERE date >= %s AND date < %s" % (datemin_1, datemax_1)), server_conn)
    df2 = pd.read_sql(("SELECT * FROM signals WHERE date >= %s AND date < %s" % (datemin_2, datemax_2)), server_conn)

    return [get_histogram2(df1,df2, columns[0]), get_histogram2(df1,df2, columns[1]), get_histogram2(df1,df2, columns[2]),
            get_histogram2(df1,df2, columns[3]), get_histogram2(df1,df2, columns[4]), get_histogram2(df1,df2, columns[5]),
            columns[0], columns[1], columns[2], columns[3], columns[4], columns[5]]

#%%###########################################################################
#                              07. MAIN                                      #
##############################################################################
if __name__ == '__main__':
    app.run_server(debug=False)