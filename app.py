#!/usr/bin/env python
# coding: utf-8

import osmnx as ox
from shapely.geometry import Polygon, MultiPolygon
import chart_studio.plotly as py
import plotly.graph_objs as go
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import ast


# In[2]:


colors = ['#0045ff', '#3080f8', '#58b2f3', '#7fe2ed', '#ffffe0', '#ffcfc7', '#ff9aad', '#ff5a8c', '#ee0000']
color1 = '#ff005e'
color2 = '#9ff0f9'
color3 = '#fffec9'
color4 = '#333231'
color_text = 'silver'
font_text = 'Muli, sans-serif'
color_bg = '#303030'
plot_bg = '#191a1a'


# In[3]:


# Utilities

def get_layers_from_boundary(place, which_result=2, project=False, 
                             linewidth=1.5, linecolor='rgb( 100, 100, 100)'):
    
    # function that extracts a mapbox layer from the Polygon(s) defined in a 
    # geodataframe returned by  osmnx for a place
    
    geodf = ox.geocode_to_gdf(place, which_result=which_result)
    if project:
        geodf =  ox.project_gdf(geodf) #perform UTM projection
    b_lons = []
    b_lats = []
    coords=[]
    
    for geometry  in geodf['geometry']:
        if isinstance(geometry, (Polygon, MultiPolygon)):
            if isinstance(geometry, Polygon):
                geometry = MultiPolygon([geometry])
            for  polygon in geometry:
                x, y = polygon.exterior.xy
                b_lons.extend(list(x))
                b_lats.extend(list(y))

    for lon, lat in zip(b_lons, b_lats):
        coords.append([lon, lat])  
    
    layer=dict(sourcetype = 'geojson',
                 source={ "type": "Feature",
                     "geometry": {"type": "LineString",
                                  "coordinates": coords
                                  }
                    },
                 color= linecolor,
                 type = 'line',   
                 line=dict(width=linewidth)
            )  
    return layer


# In[4]:


def select_polylines(coord_lim, max_num):
    lon_coord = []
    lat_coord = []
    lon_start_coord = []
    lat_start_coord = []
    counter = 0
#     §
    for i in range(len(df['POLYLINE'])):
        if counter < max_num:
            polyline = json.loads(df['POLYLINE'][i])
            dist = 0
            
            for j in range(len(polyline)-1):
                lon1, lat1 = polyline[j][0], polyline[j][1]
                lon2, lat2 = polyline[j+1][0], polyline[j+1][1]
                dist = max(dist, haversine_np(lon1, lat1, lon2, lat2))
            
            if len(polyline)>1 and dist < 1:
                if polyline[-1][0] > coord_lim[0] and polyline[-1][0] < coord_lim[1] and polyline[-1][1] > coord_lim[2] and polyline[-1][1] < coord_lim[3]:
                    
                    layer_trajectory = {'color': color1,
                    'line': {'width': 0.5},
                    'source': {'geometry': {'coordinates': polyline,
                                              'type': 'LineString'},
                                'type': 'Feature'},
                    'sourcetype': 'geojson',
                    'type': 'line'
                    }
                    
                    counter += 1
                    for x, y in polyline:
                        lon_coord.append(x)
                        lat_coord.append(y)
                    lon_coord.append(None)
                    lat_coord.append(None)
                    
                    lon_start_coord.append(polyline[0][0])
                    lat_start_coord.append(polyline[0][1])
                
        else:
            break
    
    return counter, lon_coord, lat_coord, lon_start_coord, lat_start_coord


# In[5]:


def haversine_np(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees) in km.

    All args must be of equal length.    

    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2

    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c
    return km


# In[6]:


def string_df_to_float_dict(old_dict):
    new_dict = {}
    for k in ['stadium', 'airport', 'hosp_SA', 'hosp_SJ', 'clinica', 'shopping','cathedral', 'music', 'train_PC']:
        new_dict[k] = ast.literal_eval(old_dict[k].values[0])
    return new_dict


# In[7]:


def less_trajectories(lim, old_dict):
    new_dict = {}
    for k in old_dict.keys():
        new_list = []
        count = 0
        i = 0
        old_list = old_dict[k]
        while count < lim:
            try:
                new_list.append(old_list[i])
                if old_list[i] is None:
                    count += 1
                i += 1
            except:
                break
            new_dict[k] = new_list
    return new_dict


# In[8]:


def less_starting(lim, old_dict):
    new_dict = {}
    for k in old_dict.keys():
        new_dict[k] = old_dict[k][:lim]
    return new_dict


# In[9]:


# Data processing

mapbox_access_token = 'pk.eyJ1IjoidmFsZWJsIiwiYSI6ImNrd3oxcDRkYTBzdmcydXVyYXg5aHdkdWEifQ.gL9tgJVjrWPcewxR3kxgaA'
# py.sign_in('valebl', 'vA2OGTqs7XYdJJKbfbb8')


# In[10]:


layer_porto_city =  get_layers_from_boundary('Porto, Portugal', which_result=1, linecolor=color3, linewidth=2)


# In[11]:


layers = []
layers.append(layer_porto_city)


# In[21]:


destinations_coord = {'airport' : [-8.6793293, 41.2420257], 'hosp_SA': [-8.6198591, 41.1475573],
                      'hosp_SJ': [-8.6011901, 41.181421], 'clinica': [-8.605679,41.127106],
                      'shopping': [-8.6262568, 41.1556637], 'cathedral': [-8.6111713, 41.1427354],
                      'music': [-8.6308436, 41.1589279], 'train_PC': [-8.5855852,41.1488489],
                     'stadium':[-8.5836671,41.1618028]}


# In[22]:


df = pd.read_csv('lat_start_coord.csv')
lat_start_coord = string_df_to_float_dict(df)

df = pd.read_csv('lon_start_coord.csv')
lon_start_coord = string_df_to_float_dict(df)

df = pd.read_csv('lon_coord.csv')
lon_coord = string_df_to_float_dict(df)

df = pd.read_csv('lat_coord.csv')
lat_coord = string_df_to_float_dict(df)


# In[23]:


lim = 1000
lon_coord_new = less_trajectories(lim,lon_coord)
lat_coord_new = less_trajectories(lim,lat_coord)
lat_start_coord_new = less_starting(lim,lat_start_coord)
lon_start_coord_new = less_starting(lim,lon_start_coord)


# In[24]:


# Dash app

def make_figure_mod(destination_value, lat_coord, lon_coord, lat_start_coord, lon_start_coord):
    
    lat_display = lat_coord[destination_value]
    lon_display = lon_coord[destination_value]
    lat_start_display = lat_start_coord[destination_value]
    lon_start_display = lon_start_coord[destination_value]
    
    lon_min = -8.747379988711117
    lon_max = -8.510830611269995
    lat_min = 41.119288590205514
    lat_max = 41.19657622644641
    
    fig = go.Figure(data = [go.Scattermapbox(
                                lat = lat_start_display,
                                lon = lon_start_display,
                                mode = "markers",
                                marker = {'color' : colors[-2], 'size': 7},
                                name = 'Starting Points',
                                subplot = 'mapbox',
                                ),
                            go.Scattermapbox(
                                lat = lat_display,
                                lon = lon_display,
                                mode = "lines",
                                line = {'color' : color2, 'width':0.5},
                                name = 'Trajectories',
                                subplot = 'mapbox'),
                            go.Scattermapbox(
                                lat = [destinations_coord[destination_value][1]],
                                lon = [destinations_coord[destination_value][0]],
                                mode = "markers",
                                marker = go.scattermapbox.Marker(color = colors[1], size = 20, symbolsrc = 'location.svg'),
                                # {'color' : colors[1], 'size': 20, 'symbol' : 'circle'},
                                name = 'Destination',
                                subplot = 'mapbox',
                                showlegend = True,
                                ),                            
                            go.Violin(alignmentgroup = True,
                                  hoverinfo = 'skip',                                      
                                  legendgroup = '',
                                  side = 'positive',
                                  marker = {'color': colors[-2], 'symbol': 'circle'},
                                  offsetgroup = '',
                                  scalegroup = 'y',
                                  showlegend = False,
                                  x = lon_start_display,
                                  xaxis = 'x3',
                                  yaxis = 'y3',
                                  points = False),
                              go.Violin(alignmentgroup = True,
                                  hoverinfo = 'skip',
                                  legendgroup = '',
                                  side = 'positive',
                                  marker = {'color': colors[-2], 'symbol': 'circle'},
                                  offsetgroup = '',
                                  scalegroup = 'y',
                                  showlegend = False,
                                  xaxis = 'x2',
                                  y = lat_start_display,
                                  yaxis = 'y2',
                                  points = False)],
                            layout = {'font' : {'family' : font_text},
                                        'plot_bgcolor' : plot_bg,
                                        'autosize' : False,
                                        'hovermode' : 'closest',
                                        'mapbox' : {'accesstoken' : mapbox_access_token,
                                                    'style' : 'dark',
                                                    'layers' : layers,
                                                    'bearing' : 0,
                                                    'center' : {
                                                        'lat' : 41.1579438, 
                                                        'lon': -8.6291053},
                                                    'pitch' : 0,
                                                    'zoom': 12,
                                                    'domain':{'x': [0.0, 0.84], 'y': [0.17, 1.0]}},
                                        'width' : 1800, 
                                        'height' : 900,
                                        'legend': {'tracegroupgap': 0},
                                        'xaxis': {'anchor': 'y', 'domain': [0.0, 0.85]},
                                        'xaxis2': {'anchor': 'y2',
                                                  'domain': [0.85, 0.925],
                                                  'matches': 'x2',
                                                  'showgrid': False,
                                                  'showline': False,
                                                  'showticklabels': False,
                                                  'ticks': ''},
                                       'xaxis3': {'anchor': 'y3',
                                                  'domain': [0.0, 0.84],
                                                  'matches': 'x',
                                                  'showgrid': False,
                                                  'showticklabels': False},
                                       'xaxis4': {'anchor': 'y4',
                                                  'domain': [0.85, 1.0],
                                                  'matches': 'x2',
                                                  'showgrid': False,
                                                  'showline': False,
                                                  'showticklabels': False,
                                                  'ticks': ''},
                                       'yaxis': {'anchor': 'x', 'domain': [0.0, 0.85]},
                                       'yaxis2': {'anchor': 'x2',
                                                  'domain': [0.17, 1.0],
                                                  'matches': 'y',
                                                  'showgrid': False,
                                                  'showticklabels': False},
                                       'yaxis3': {'anchor': 'x3',
                                                  'domain': [0.0, 0.15],
                                                  'matches': 'y3',
                                                  'showgrid': False,
                                                  'showline': False,
                                                  'showticklabels': False,
                                                  'ticks': '',
                                                  'autorange':'reversed'},
                                       'yaxis4': {'anchor': 'x4',
                                                  'domain': [0.85, 1.0],
                                                  'matches': 'y3',
                                                  'showgrid': True,
                                                  'showline': False,
                                                  'showticklabels': False,
                                                  'ticks': ''}}
                        )
    
    fig.update_layout(
        title = dict (text= "Taxi <b>trajectories</b> show concentration in the <b>city center</b><br>",
            xref="paper",
            x=0,
            font=dict(family=font_text,size=44, color=color_text)),
        annotations = [{
            'text': "Interactive map of Porto showing trajectories and starting points for a given destination",
              'font': {
              'family' : 'Muli, sans-serif',
              'size': 21,
              'color': color_text,
            },
            'showarrow': False,
            'align': 'left',
            'x': 0,
            'y': 1.05,
            'xref': 'paper',
            'yref': 'paper',
          },
        ],
        paper_bgcolor = color_bg,
        legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="right",
        x=0.835))
    
    fig.update_layout(legend = dict(font=dict(family=font_text,size=14, color=color_text)))
    fig.update_layout(xaxis3 = dict(range = [lon_min, lon_max])) # box 
    fig.update_layout(yaxis2 = dict(range = [lat_min, lat_max])) # violin

    return fig


# In[27]:


app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        dcc.Graph(
            id = "mapbox-plot",
            figure = make_figure_mod('train_PC', lat_coord_new, lon_coord_new, lat_start_coord_new, lon_start_coord_new))
    ],style={'backgroundColor':color_bg, 'position':'absolute', 'top':'40px'}),
    html.Div([
        dcc.Dropdown(
            id = 'drop-opt',
            options = [{'label': 'Porto Campanha Train Station', 'value': 'train_PC'},
                       {'label': 'Aeroporto Francisco Sá Carneiro', 'value': 'airport'},
                       {'label': 'Estádio do Dragão', 'value':'stadium'},
                       {'label': 'Hospital Santo António', 'value': 'hosp_SA'},
                       {'label': 'São João Universitary Hospital', 'value': 'hosp_SJ'},
                       {'label': 'Clínica Lusíadas Gaia', 'value': 'clinica'},
                       {'label': 'Shopping Center Itália', 'value': 'shopping'},
                       {'label': 'Cathédrale de Porto', 'value': 'cathedral'},
                       {'label': 'Casa Da Musica', 'value': 'music'}],
                        value = 'train_PC',
            style = {"width": "350px",'font-family':font_text,'color':color_bg, 'background-color':'silver',
                    'position':'absolute','top':'80px','left':'50px'})
    ]),
    html.H1('For a correct visualization of the starting points distribution plots set the laptop layout zoom option to 100%',
            style = {'position':'absolute', 'bottom':'45px','left':'90px',
                     'font-family':'Muli, sans-serif','fontSize':16,'color':'silver'}),
    html.H1('The interactive map is a 2D visualization (works with zoom and translation only)',
            style = {'position':'absolute', 'bottom':'20px','left':'90px',
                     'font-family':'Muli, sans-serif','fontSize':16,'color':'silver'}),
    html.H1('Data source: https://www.kaggle.com/crailtap/taxi-trajectory',
            style = {'position':'absolute', 'bottom':'45px','right':'475px',
                     'font-family':'Muli, sans-serif','fontSize':16,'color':'silver'}),
    html.H1('1000 trajectories are plotted per destination',
            style = {'position':'absolute', 'bottom':'20px','right':'475px',
                     'font-family':'Muli, sans-serif','fontSize':16,'color':'silver'}),
    html.H1('Starting',
            style = {'position':'absolute', 'bottom':'155px','left':'1475px',
                     'font-family':'Muli, sans-serif','fontSize':16,'color':colors[-2]}),
    html.H1('points',
            style = {'position':'absolute', 'bottom':'130px','left':'1475px',
                     'font-family':'Muli, sans-serif','fontSize':16,'color':colors[-2]}),
    html.H1('distributions',
            style = {'position':'absolute', 'bottom':'105px','left':'1475px',
                     'font-family':'Muli, sans-serif','fontSize':16,'color':colors[-2]}),],
    style = {'background-color':color_bg, 'position':'absolute', 'top':'0px','left':'0px','right':'0px','bottom':'0px'})
    
@app.callback(Output(component_id='mapbox-plot',component_property='figure'),
              Input(component_id='drop-opt', component_property='value'),
              Input(component_id='mapbox-plot', component_property='relayoutData'))
def update_zoom(destination_value, relayoutData):
 
    try: # to consider the case in which destination_value is None
        figure_mod = make_figure_mod(destination_value, lat_coord_new, lon_coord_new, lat_start_coord_new, lon_start_coord_new)
    except:
        figure_mod = make_figure_mod('train_PC', lat_coord_new, lon_coord_new, lat_start_coord_new, lon_start_coord_new)

    try: # to consider the case in which relayoutData is None      
        coords = relayoutData['mapbox._derived']['coordinates']
        lon_min = coords[0][0]
        lon_max = coords[1][0]
        lat_min = coords[2][1]
        lat_max = coords[1][1]        
        center = relayoutData['mapbox.center']
        zoom = relayoutData['mapbox.zoom']
        figure_mod.layout.mapbox.zoom = zoom 
        figure_mod.layout.mapbox.center = center
        figure_mod.layout.xaxis3.autorange = False # box
        figure_mod.layout.yaxis2.autorange = False # violin
        figure_mod.update_layout(xaxis3 = dict(range = [lon_min, lon_max])) # bottom dist plot
        figure_mod.update_layout(yaxis2 = dict(range = [lat_min, lat_max])) # right dist plot
    except:
        print('')

    
    return figure_mod

app.run_server(debug=True, port=5085)

