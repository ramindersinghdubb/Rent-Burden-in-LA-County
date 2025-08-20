# ------------ LIBRARIES ------------ #
import dash
from dash import dcc, html, clientside_callback, ClientsideFunction
from dash.dependencies import Output, Input, State
from dash_extensions import Purify
import dash_bootstrap_components as dbc
import feffery_markdown_components as fmc


import pandas as pd
import numpy as np
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import json
from copy import deepcopy
import os



# ------------ DATA COLLECTION ------------ #
assets_path = "assets/"

data_path = "masterfiles/"

# -- Masterfiles -- #
masterfile = pd.DataFrame()
alert_masterfile = pd.DataFrame()
years = range(2010, 2024)

columns = ['PLACE', 'YEAR',
           'B25070_007E', 'B25070_008E', 'B25070_009E', 'B25070_010E', 'B25070_001E', # overall rent burden percentage
           'B25072_006E', 'B25072_007E', 'B25072_002E', # 15 to 24 rent burden percentage
           'B25072_013E', 'B25072_014E', 'B25072_009E', # 25 to 34 rent burden percentage
           'B25072_020E', 'B25072_021E', 'B25072_016E', # 35 to 64 rent burden percentage
           'B25072_027E', 'B25072_028E', 'B25072_023E', # 65 and older rent burden percentage
           #'B25070_010E', 'B25070_001E' # overall severe rent burden percentage
          ]

for year in years:
    file_path = f'{data_path}rent_burden_masterfile_{year}.csv'
    df = pd.read_csv(file_path)
    map_path = f'{assets_path}rent_burden_mastergeometry_{year}.json'
    gdf = gpd.read_file(map_path)
    df = pd.merge(df, gdf[['PLACE', 'NAME', 'GEO_ID','INTPTLAT','INTPTLON']], on=['PLACE', 'NAME', 'GEO_ID'], how='left')

    # For the alert text
    alert_df = df[columns]
    alert_df = alert_df.groupby(['PLACE', 'YEAR'], as_index=False).sum()
    alert_df['TotalPop'] = alert_df['B25070_001E']
    alert_df['OverallRB'] = round( ( ( alert_df['B25070_007E'] + alert_df['B25070_008E'] + alert_df['B25070_009E'] + alert_df['B25070_010E']) / alert_df['TotalPop']) * 100, 2 )
    alert_df['15to24Pop'] = alert_df['B25072_002E']
    alert_df['15to24RB'] = round( ( ( alert_df['B25072_006E'] + alert_df['B25072_007E']) / alert_df['15to24Pop']) * 100, 2 )
    alert_df['25to34Pop'] = alert_df['B25072_009E']
    alert_df['25to34RB'] = round( ( ( alert_df['B25072_013E'] + alert_df['B25072_014E']) / alert_df['25to34Pop']) * 100, 2 )
    alert_df['35to64Pop'] = alert_df['B25072_016E']
    alert_df['35to64RB'] = round( ( ( alert_df['B25072_020E'] + alert_df['B25072_021E']) / alert_df['35to64Pop']) * 100, 2 )
    alert_df['65olderPop'] = alert_df['B25072_023E']
    alert_df['65olderRB'] = round( ( ( alert_df['B25072_027E'] + alert_df['B25072_028E']) / alert_df['65olderPop']) * 100, 2 )
    alert_df['OverallSRB'] = round( ( alert_df['B25070_010E'] / alert_df['TotalPop']) * 100, 2)
    alert_df = alert_df[['PLACE', 'YEAR', 'TotalPop', 'OverallRB', '15to24Pop', '15to24RB', '25to34Pop', '25to34RB', '35to64Pop', '35to64RB', '65olderPop', '65olderRB', 'OverallSRB']]
    alert_masterfile = pd.concat([alert_masterfile, alert_df], ignore_index = True)

    # For the trace
    df['dummy'] = 1

    # Formatting for the hovertemplate
    df['TotalRentBurden']   = round( ( (df['B25070_007E'] + df['B25070_008E'] + df['B25070_009E'] + df['B25070_010E']) / df['B25070_001E']) * 100, 2)
    df['RentBurden_15to24'] = round( ( (df['B25072_006E'] + df['B25072_007E']) / df['B25072_002E']) * 100, 2)
    df['RentBurden_25to34'] = round( ( (df['B25072_013E'] + df['B25072_014E']) / df['B25072_009E']) * 100, 2)
    df['RentBurden_35to64'] = round( ( (df['B25072_020E'] + df['B25072_021E']) / df['B25072_016E']) * 100, 2)
    df['RentBurden_65+']    = round( ( (df['B25072_027E'] + df['B25072_028E']) / df['B25072_023E']) * 100, 2)

    df['RentBurden_15to24_str'] = df['RentBurden_15to24'].astype(str) + '%'
    df.loc[df['RentBurden_15to24_str'] == 'nan%', 'RentBurden_15to24_str'] = 'Not Available'
    df['RentBurden_25to34_str'] = df['RentBurden_25to34'].astype(str) + '%'
    df.loc[df['RentBurden_25to34_str'] == 'nan%', 'RentBurden_25to34_str'] = 'Not Available'
    df['RentBurden_35to64_str'] = df['RentBurden_35to64'].astype(str) + '%'
    df.loc[df['RentBurden_35to64_str'] == 'nan%', 'RentBurden_35to64_str'] = 'Not Available'
    df['RentBurden_65+_str'] = df['RentBurden_65+'].astype(str) + '%'
    df.loc[df['RentBurden_65+_str'] == 'nan%', 'RentBurden_65+_str'] = 'Not Available'

    df['TotalSevereRentBurden']  = round( ( (df['B25070_010E']) / df['B25070_001E']) * 100, 2)
    df = df[['YEAR', 'PLACE', 'GEO_ID', 'NAME', 'B25070_001E', 'INTPTLAT', 'INTPTLON', 'dummy',
             'TotalRentBurden', 'RentBurden_15to24_str', 'RentBurden_25to34_str', 'RentBurden_35to64_str',
             'RentBurden_65+_str', 'TotalSevereRentBurden']]

    masterfile = pd.concat([masterfile, df], ignore_index = True)


  
# ------------ UTILITY FUNCTIONS ------------ #
# Function for creating a dictionary where the places (keys) hold lists of dictionaries for our year dropdown
def place_year_dictionary():
    place_year_dict = dict()

    places = masterfile['PLACE'].unique().tolist()
    masterfile['NAME'].unique
    for place in places:
        df = masterfile[masterfile['PLACE'] == place]
        list_of_years = df['YEAR'].unique().tolist()
        dummy_dict = [{'label': year, 'value': year} for year in list_of_years]
        place_year_dict[place] = dummy_dict

    return place_year_dict



# ------------ CONTAINERS AND STRINGS------------ #

# Container for geospatial choropleth map
geodata_map = html.Div([
    dcc.Graph(
        id = "chloropleth_map",
        config={'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d', 'resetview'],
                'displaylogo': False
               },
    )
])

# Container for rent plot
geodata_plot = html.Div([
    dcc.Graph(
        id = "rent_plot",
        config={'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d', 'resetview'],
                'displaylogo': False
               },
    )
])



# Footer string
footer_string = """
### <b style='color:#800000;'>Information</b>

This website allows you to view the percentage of rent-burdened individuals and/or severely rent-burdened individuals for census tracts across various cities in Los Angeles county. <br>

For the purposes of this website . . . <ul>
<li><b style='color:#B22222;'>Rent-burdened individuals</b> are individuals for whom <u style='color:#B22222;'><b style='color:#B22222;'>over 30% of their income</b></u> goes to paying rent </li>
<li> <b style='color:#800000;'>Severely rent-burdened individuals</b> are individuals for whom <u style='color:#800000;'><b style='color:#800000;'>over 50% of their income</b></u> goes to paying rent </li>
</ul>

Use the dropdowns to choose a city of interest and a year of interest. You can also choose whether you wish to see the percentage of rent-burdened renters
or the percentage of severely rent-burdened renters by clicking on the options. <br>

Hover over the map to view a detailed breakdown of rent-burdened individuals by age. <br>

Click on a census tract to visualize how the percentage of either rent-burdened or severely rent-burdened individuals has evolved over time in the plot.
You can also hover over points in the plot to view additional information on the age demographics of rent-burdened individuals.

<hr style="height:2px; border-width:0; color:#212122; background-color:#212122">

### <b style='color:#800000;'>Notes</b>
1. Rent burden was quantified on the basis of gross rent being at least 30% of an individual's household income in the past 12 months while severe rent burden
was quantified on the basis of gross rent being at least 50% of an individual's household income in the past 12 months. Gross rents, per the <u style='color:#800000;'><a href="https://www2.census.gov/programs-surveys/acs/methodology/design_and_methodology/2024/acs_design_methodology_report_2024.pdf" style='color:#800000;'>December 2024 American Community Survey and Puerto Rico Community Survey Design and Methodology</a></u>, is defined as <br>

   <blockquote> <q> ...[the monthly rent agreed to or contracted for, regardless of any furnishings, utilities, fees, meals, or services that may be included] plus the estimated average monthly cost of utilities and fuels, if these are paid by the renter.</q> (Chapter 6) </blockquote>

2. Data for rent burden were taken from the United States Census Bureau <u style='color:#800000;'><a href="https://www.census.gov/programs-surveys/acs.html" style='color:#800000;'>American Community Survey</a></u> (ACS codes B25070, and B25072).
3. Redistricting over the years affects the availability of some census tracts in certain cities. Unavailability of data for certain census tracts during select years may affect whether or not census tracts are displayed on the map. For these reasons, some census tracts and their data may only be available for a partial range of years.

### <b style='color:#800000;'>Disclaimer</b>

This tool is developed for illustrative purposes. This tool is constructed with the assistance of the United States Census Bureau’s American Community Survey data.
Survey data is based on individuals’ voluntary participation in questionnaires. The creator is not liable for any missing, inaccurate, or incorrect data. This tool
is not affiliated with, nor endorsed by, the government of the United States.

### <b style='color:#800000;'>Appreciation</b>
Thank you to <u style='color:#800000;'><a href="https://www.wearelbre.org/" style='color:#800000;'>Long Beach Residents Empowered (LiBRE)</a></u> for providing the opportunity to work on this project.

### <b style='color:#800000;'>Author Information</b>
Raminder Singh Dubb <br>
<u style='color:#800000;'><a href="https://github.com/ramindersinghdubb/Rent-Burden-in-LA-County" style='color:#800000;'>GitHub</a></u>

© 2025 Raminder Singh Dubb
"""

# ------------ Initialization ------------ #
place_year_dict = place_year_dictionary()

# ------------ Colors ------------ #
Cream_color = '#FAE8E0'
SnowWhite_color = '#F5FEFD'
AlabasterWhite_color = '#FEF9F3'
LightBrown_color = '#F7F2EE'
Rose_color = '#FF7F7F'
MaroonRed_color = '#800000'
SinopiaRed_color = '#C0451C'
Teal_color = '#2A9D8F'
ObsidianBlack_color = '#020403'
CherryRed_color = '#E3242B'




# ------------ APP ------------ #
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.SIMPLEX,
                                      "assets/style.css"
                                     ]
               )
server=app.server



app.layout = dbc.Container([
    # ------------ Title ------------ #
    html.Div([
        html.B("Rent Burden in Los Angeles County")
    ], style = {'display': 'block',
                'color': MaroonRed_color,
                'margin': '0.2em 0',
                'padding': '0px 0px 0px 0px', # Numbers represent spacing for the top, right, bottom, and left (in that order)
                'font-family': 'Trebuchet MS, sans-serif',
                'font-size': '220.0%'
               }
            ),
    # ------------ Subtitle ------------ #
    html.Div([
        html.P("Rent Burden and Severe Rent Burden for Census Tracts across Cities and Census-Designated Places in Los Angeles County, 2010 to 2023")
    ], style = {'display': 'block',
                'color': ObsidianBlack_color,
                'margin': '-0.5em 0',
                'padding': '0px 0px 0px 0px',
                'font-family': 'Trebuchet MS, sans-serif',
                'font-size': '105.0%'
               }
            ),
    # ------------ Horizontal line rule ------------ #
    html.Div([
        html.Hr()
    ], style = {'display': 'block',
                'height': '1px',
                'border': 0,
                'margin': '-0.9em 0',
                'padding': 0
               }
            ),
    # ------------ Labels for dropdowns (discarded) ------------ #
    
    # ------------ Dropdowns ------------ #
    html.Div([
        html.Div([
            dcc.Dropdown(id='place-dropdown',
                         placeholder='Select a place',
                         options=[{'label': p, 'value': p} for p in list(place_year_dict.keys())],
                         value='Long Beach',
                         clearable=False
                        )
        ], style = {'display': 'inline-block',
                    'margin': '0 0',
                    'padding': '30px 15px 0px 0px',
                    'width': '22.5%'
                   }
                ),
        html.Div([
            dcc.Dropdown(id='year-dropdown',
                         placeholder='Select a year',
                         clearable=False
                        )
        ], style = {'display': 'inline-block',
                    'margin': '0 0',
                    'padding': '30px 15px 0px 0px',
                    'width': '12.5%',
                   }
                ),
        html.Div([
            dcc.Dropdown(id='census-tract-dropdown',
                         placeholder = 'Click on a census tract in the map',
                         clearable=True
                        )
        ], style = {'display': 'inline-block',
                    'padding': '30px 30px 0px 0px',
                    'margin': '0 0',
                    'width': '30.0%'
                   }
                ),
    # ------------ Option Buttons ------------ #
        html.Div([
            dbc.RadioItems(id='radio-options',
                           options = [{'label': 'Rent Burden', 'value': 'Rent Burden'},
                                      {'label': 'Severe Rent Burden', 'value': 'Severe Rent Burden'}
                                     ],
                           value = 'Rent Burden',
                           inline = True,
                           labelCheckedClassName = "text-primary",
                           inputCheckedClassName = "border border-primary bg-primary"
                        )
        ], style = {'display': 'inline-block',
                    'padding': '35px 30px 0px 10px',
                    'margin': '0 0',
                    'width': '30.0%',
                    #'textAlign': 'center'
                   }
                )
    ], style={"padding": "0px 0px 10px 15px"}, className = 'row'
            ),
    # ------------ Spatial map with plot ------------ #
    html.Div([
            dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(children = [html.B(id="map-title1"), " in ", html.B(id="map-title2"), " by Census Tract, ", html.B(id="map-title3")],
                                   style = {'background-color': MaroonRed_color,
                                            'color': '#FFFFFF'}
                                  ),
                    dbc.CardBody([geodata_map],
                                 style = {'background-color': AlabasterWhite_color}
                                )
                ])
            ]),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(children = html.B(id = "plot-title"),
                                   style = {'background-color': Teal_color,
                                            'color': '#FFFFFF'}
                                  ),
                    dbc.CardBody([geodata_plot],
                                 style = {'background-color': AlabasterWhite_color}
                                )
                ])
            ])
        ], align='center', justify='center'
               )
    ], style = {
                'padding': '10px 0px 20px 0px',
               }
            ),
    # ------------ Alerts ------------ #
    html.Div([
        dbc.Row([
           dbc.Col([
               dbc.Alert(children=['Of the estimated ', html.B(id='dv1'), ' renters residing in ', html.B(id='dv2'), ' during ',
                                    html.B(id='dv3'), ', approximately ', html.B(id='dv4'), ' of all renters were considered ',
                                    html.B('rent-burdened'), '.', html.Br(), html.Br(), 'Of the estimated ', html.B(id='dv5'),
                                    ' renters who were ', html.B('15 to 24 years old'), ', approximately ', html.B(id='dv6'),
                                    ' were considered ', html.B('rent-burdened'), '.', html.Br(), html.Br(), 'Of the estimated ',
                                    html.B(id='dv7'), ' renters who were ', html.B('25 to 34 years old'), ', approximately ', html.B(id='dv8'),
                                    ' were considered ', html.B('rent-burdened'), '.', html.Br(), html.Br(), 'Of the estimated ',
                                    html.B(id='dv9'), ' renters who were ', html.B('35 to 64 years old'), ', approximately ', html.B(id='dv10'),
                                    ' were considered ', html.B('rent-burdened'), '.', html.Br(), html.Br(), 'Of the estimated ',
                                    html.B(id='dv11'), ' renters who were ', html.B('65 years and older'), ', approximately ', html.B(id='dv12'),
                                    ' were considered ', html.B('rent-burdened'), '.',
                                   ],
                          color = 'primary')
           ])   
        ]
                ),
        dbc.Row([
           dbc.Col([
               dbc.Alert(children=['Of the estimated ', html.B(id='ndv1'), ' renters residing in ', html.B(id='ndv2'), ' during ',
                                    html.B(id='ndv3'), ', approximately ', html.B(id='ndv4'), ' of all renters were considered ',
                                    html.B('severely rent-burdened'), '.'],
                          color = 'danger')
           ])   
        ]
                )
    ], style = {
                'padding': '20px 0px 0px 0px',
               }
            ),
    # ------------ Footer ------------ #
    html.Div([
        fmc.FefferyMarkdown(markdownStr    = footer_string,
                            renderHtml     = True,
                            style          = {'background': LightBrown_color,
                                              'margin-top': '1em'
                                             }
                           )
    ]
            ),
    # ------------ Data ------------ #
    dcc.Store(id='masterfile_data',
              data=masterfile.to_dict("records")
             ),
    dcc.Store(id='alert_masterfile_data',
              data=alert_masterfile.to_dict("records")
             ),
    dcc.Store(id='place_year_dict',
              data=place_year_dict
             )
], style = {'background-color': LightBrown_color, "padding": "0px 0px 20px 0px",})



# ------------ CALLBACKS ------------ #
#
# Summary (inputs -> outputs)
#
#
# Dropdowns:
#  place value -> year options
#  year options -> default year value
#  place options, year options, map ClickData -> census tract options
#  click data -> census tract value
#
# Titles:
#  place value, year value, radio options -> map title
#  place value, census tract value -> plot title
#
# Graphs:
#  place value, year value, census tract value, radio options -> map
#  place value, census tract value, radio options -> plot
#
# Alert:
#  place value, year value -> alert
#
# ----------------------------------- #


# ------------ Dropdowns ------------ #

# Year tract options
app.clientside_callback(
    """
    function(selected_place, place_year_dict) {
        return place_year_dict[selected_place]
    }
    """,
    Output('year-dropdown', 'options'),
    [Input('place-dropdown', 'value'),
     Input('place_year_dict', 'data')
    ]
)


# Year tract value
app.clientside_callback(
    """
    function(options) {
        var opt = options.find(x => x['label'] === 2023);
        return opt['label']
    }
    """,
    Output('year-dropdown', 'value'),
    Input('year-dropdown', 'options')
)


# Census tract options
app.clientside_callback(
    """
    function(selected_place, selected_year, masterfile_data) {
        var selected_place = `${selected_place}`;
        var options = masterfile_data.filter(x => x['YEAR'] === selected_year && x['PLACE'] === selected_place);
        var tract_options = options.map(item => { return item.NAME });
        return tract_options
    }
    """,
    Output('census-tract-dropdown', 'options'),
    [Input('place-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('masterfile_data', 'data')
    ]
)




# Census tract value based on click data
app.clientside_callback(
    """
    function(clickData) {
        return clickData['points']['0']['customdata']
    }
    """,
    Output('census-tract-dropdown', 'value'),
    Input('chloropleth_map', 'clickData')
)




# ------------ Titles ------------ #


# Map title
app.clientside_callback(
    """
    function(selected_metric, selected_place, selected_year) {
        var selected_metric = `${selected_metric}`;
        var selected_place = `${selected_place}`;
        var selected_year = `${selected_year}`;

        if (selected_metric == 'Rent Burden') {
            return ['Percentage of Rent Burdened Individuals', selected_place, selected_year];
        }
        
        else {
            return ['Percentage of Severely Rent Burdened Individuals', selected_place, selected_year];
        }
    }
    """,
    [Output('map-title1', 'children'),
     Output('map-title2', 'children'),
     Output('map-title3', 'children')
    ],
    [Input('radio-options', 'value'),
     Input('place-dropdown', 'value'),
     Input('year-dropdown', 'value'),
    ]
)

# Plot title
app.clientside_callback(
    """
    function(selected_place, selected_tract) {
        if (selected_tract == undefined){
            return "Please click on a tract.";
        } else {
            return `${selected_place}, ${selected_tract}`;
        }
    }
    """,
    Output('plot-title', 'children'),
    [Input('place-dropdown', 'value'),
     Input('census-tract-dropdown', 'value')
    ]
)


# ------------ Graphs ------------ #

# Choropleth map
app.clientside_callback(
    """
    function(selected_metric, selected_place, selected_year, selected_tract, masterfile_data){
        var selected_metric = `${selected_metric}`;
        var selected_place = `${selected_place}`;
        var selected_year = Number(selected_year);
        var my_array = masterfile_data.filter(item => item['PLACE'] === selected_place && item['YEAR'] === selected_year);
        
        var place_string = selected_place.replaceAll(' ','');
        var url_path = "https://raw.githubusercontent.com/ramindersinghdubb/Rent-Burden-in-LA-County/refs/heads/main/as" + "sets/" + selected_year + "/rent_burden_mastergeometry_" + selected_year + "_" + place_string + ".json";
        
        var locations_array = my_array.map(({GEO_ID}) => GEO_ID);
        var customdata_array = my_array.map(({NAME}) => NAME);
        
        var long_array = my_array.map(({INTPTLON})=>INTPTLON);
        var long_center = long_array.reduce((a, b) => a + b) / long_array.length;
        const lon_center = parseFloat(long_center.toFixed(5));
        
        var lat_array = my_array.map(({INTPTLAT})=>INTPTLAT);
        var lati_center = lat_array.reduce((a, b) => a + b) / lat_array.length;
        const lat_center = parseFloat(lati_center.toFixed(5));

        var rent_burden_z_array = my_array.map(({TotalRentBurden})=>TotalRentBurden);
        var rent_burden_strings = my_array.map(function(item) {
            return "<b style='font-size:16px;'>" + item['NAME'] + "</b><br>" + item['PLACE'] + ", Los Angeles County<br><br>"
            + "Of the estimated " + item['B25070_001E'] + " renters, approx. <b style='font-size:16px; color:#800000;'>" + item['TotalRentBurden'] + "%</b><br>"
            + "were considered <b style='font-size:16px; color:#800000;'>rent-burdened</b> during <b style='font-size:14px'>" + item['YEAR'] + "</b>. <br><br>"
            + "Of renters <b style='color:#B22222;'>15 to 24 year old</b>, approx.<br><b style='color:#B22222; font-size:14px;'>" + item['RentBurden_15to24_str'] + "</b> were rent-burdened.<br><br>"
            + "Of renters <b style='color:#B22222;'>25 to 34 year old</b>, approx.<br><b style='color:#B22222; font-size:14px;'>" + item['RentBurden_25to34_str'] + "</b> were rent-burdened.<br><br>"
            + "Of renters <b style='color:#B22222;'>35 to 64 year old</b>, approx.<br><b style='color:#B22222; font-size:14px;'>" + item['RentBurden_35to64_str'] + "</b> were rent-burdened.<br><br>"
            + "Of renters <b style='color:#B22222;'>65 and older</b>, approx.<br><b style='color:#B22222; font-size:14px;'>" + item['RentBurden_65+_str'] + "</b> were rent-burdened.<extra></extra>";
            });
        
        var rent_burden_main_data = [{
            'type': 'choroplethmap',
            'customdata': customdata_array,
            'geojson': url_path,
            'locations': locations_array,
            'featureidkey': 'properties.GEO_ID',
            'colorscale': 'Hot',
            'reversescale': true,
            'z': rent_burden_z_array,
            'zmin': 0, 'zmax': 100,
            'marker': {'line': {'color': '#020403', 'width': 1.75}, 'opacity': 0.4},
            'text': rent_burden_strings,
            'colorbar': {'outlinewidth': 2,
                         'ticklabelposition': 'outside bottom',
                         'ticksuffix': '%',
                         'title': {'font': {'color': '#020403', 'weight': 500}, 'text': 'Percentage of<br>Rent-Burdened<br>Individuals (%)'}},
            'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
            'hovertemplate': '%{text}'
        }];

        var severe_rent_burden_z_array = my_array.map(({TotalSevereRentBurden})=>TotalSevereRentBurden);
        var severe_rent_burden_strings = my_array.map(function(item) {
            return "<b style='font-size:16px;'>" + item['NAME'] + "</b><br>" + item['PLACE'] + ", Los Angeles County<br><br>"
            + "Of the estimated " + item['B25070_001E'] + " renters, approx. <b style='font-size:16px; color:#610000;'>" + item['TotalSevereRentBurden'] + "%</b><br>"
            + "were considered <b style='font-size:16px; color:#610000;'>severely rent-burdened</b><br>during <b style='font-size:14px'>" + item['YEAR'] + "</b>.<extra></extra>";
            });
                
        var severe_rent_burden_main_data = [{
            'type': 'choroplethmap',
            'customdata': customdata_array,
            'geojson': url_path,
            'locations': locations_array,
            'featureidkey': 'properties.GEO_ID',
            'colorscale': 'Viridis',
            'reversescale': true,
            'z': severe_rent_burden_z_array,
            'zmin': 0, 'zmax': 100,
            'marker': {'line': {'color': '#020403', 'width': 1.75}, 'opacity': 0.4},
            'text': severe_rent_burden_strings,
            'colorbar': {'outlinewidth': 2,
                         'ticklabelposition': 'outside bottom',
                         'ticksuffix': '%',
                         'title': {'font': {'color': '#020403', 'weight': 500}, 'text': 'Percentage of<br>Severely<br>Rent-Burdened<br>Individuals (%)'}},
            'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
            'hovertemplate': '%{text}'
        }];
        
        var layout = {
            'autosize': true,
            'hoverlabel': {'align': 'left'},
            'map': {'center': {'lat': lat_center, 'lon': lon_center}, 'style': 'streets', 'zoom': 10},
            'margin': {'b': 0, 'l': 0, 'r': 0, 't': 0},
            'paper_bgcolor': '#FEF9F3',
            'plot_bgcolor': '#FEF9F3',
        };
        
        if (selected_metric == 'Rent Burden') {
            if (selected_tract != undefined){
                    var aux_rb_array = my_array.filter(item => item['NAME'] === selected_tract);
                    var aux_rb_locations_array = aux_rb_array.map(({GEO_ID}) => GEO_ID);
                    var aux_rb_z_array = aux_rb_array.map(({dummy})=>dummy);
                
                    var rent_burden_data_aux = {
                        'type': 'choroplethmap',
                        'geojson': url_path,
                        'locations': aux_rb_locations_array,
                        'featureidkey': 'properties.GEO_ID',
                        'colorscale': 'Reds',
                        'showscale': false,
                        'z': aux_rb_z_array,
                        'zmin': 0, 'zmax': 1,
                        'marker': {'line': {'color': '#04D9FF', 'width': 4}},
                        'selected': {'marker': {'opacity': 0.4}},
                        'hoverinfo': 'skip',
                    }
                rent_burden_main_data.push(rent_burden_data_aux);
            }
            return {'data': rent_burden_main_data, 'layout': layout};
        }
        else {
            if (selected_tract != undefined){
                    var aux_srb_array = my_array.filter(item => item['NAME'] === selected_tract);
                    var aux_srb_locations_array = aux_srb_array.map(({GEO_ID}) => GEO_ID);
                    var aux_srb_z_array = aux_srb_array.map(({dummy})=>dummy);
                
                    var severe_rent_burden_data_aux = {
                        'type': 'choroplethmap',
                        'geojson': url_path,
                        'locations': aux_srb_locations_array,
                        'featureidkey': 'properties.GEO_ID',
                        'colorscale': `[[0, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,0)']]`,
                        'showscale': false,
                        'z': aux_srb_z_array,
                        'zmin': 0, 'zmax': 1,
                        'marker': {'line': {'color': '#04D9FF', 'width': 4}},
                        'selected': {'marker': {'opacity': 0.4}},
                        'hoverinfo': 'skip',
                    }
                    severe_rent_burden_main_data.push(severe_rent_burden_data_aux);
                }
            return {'data': severe_rent_burden_main_data, 'layout': layout};
        }
    }
    """,
    Output('chloropleth_map', 'figure'),
    [Input('radio-options', 'value'),
     Input('place-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('census-tract-dropdown', 'value'),
     Input('masterfile_data', 'data')
    ]
)



# Plot
app.clientside_callback(
    """
    function(selected_metric, selected_place, selected_tract, masterfile_data){        
        if (selected_tract != undefined) {
            var selected_metric = `${selected_metric}`;
            var selected_place = `${selected_place}`;
            var selected_tract = `${selected_tract}`;
            var my_array = masterfile_data.filter(item => item['PLACE'] === selected_place && item['NAME'] === selected_tract);

            var customdata_array = my_array.map(({NAME}) => NAME);
            
            var x_array = my_array.map(({YEAR})=>YEAR);
            var rb_y_array = my_array.map(({TotalRentBurden})=>TotalRentBurden);
            var srb_y_array = my_array.map(({TotalSevereRentBurden})=>TotalSevereRentBurden);

            var rb_strings = my_array.map(function(item) {
                return "<b style='font-size:16px;'>" + item['YEAR'] + "</b><br>" + item['NAME'] + ", " + item['PLACE'] + " <br><br>"
                + "Of the estimated " + item['B25070_001E'] + " renters, approx.<br><b style='font-size:16px; color:#800000;'>" + item['TotalRentBurden'] + "%</b> "
                + "were considered <b style='font-size:16px; color:#800000;'>rent-burdened</b>. <br><br>"
                + "<b style='font-size:14px;'>Proportion of Rent-Burdened <br>Individuals by Age</b><br>"
                + "Of renters <b style='color:#B22222;'>15 to 24 year old</b>, approx.<br><b style='color:#B22222; font-size:14px;'>" + item['RentBurden_15to24_str'] + "</b> were rent-burdened.<br><br>"
                + "Of renters <b style='color:#B22222;'>25 to 34 year old</b>, approx.<br><b style='color:#B22222; font-size:14px;'>" + item['RentBurden_25to34_str'] + "</b> were rent-burdened.<br><br>"
                + "Of renters <b style='color:#B22222;'>35 to 64 year old</b>, approx.<br><b style='color:#B22222; font-size:14px;'>" + item['RentBurden_35to64_str'] + "</b> were rent-burdened.<br><br>"
                + "Of renters <b style='color:#B22222;'>65 and older</b>, approx.<br><b style='color:#B22222; font-size:14px;'>" + item['RentBurden_65+_str'] + "</b> were rent-burdened.<extra></extra>";
            });

            var rb_data = [{
                'type': 'scatter',
                'x': x_array,
                'y': rb_y_array,
                'mode': 'lines+markers',
                'line': {'color': '#800000'},
                'marker': {'size': 10, 'line': {'width': 2, 'color': '#F5FBFF'}},
                'text': rb_strings,
                'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
                'hovertemplate': '%{text}'
            }];
        
            var rb_layout = {
                'font': {'color': '#020403'},
                'hoverlabel': {'align': 'left'},
                'margin': {'b': 40, 't': 40, 'r': 20},
                'autosize': true,
                'uirevision': true,
                'paper_bgcolor': '#FEF9F3',
                'plot_bgcolor': '#FEF9F3',
                'title': {'text': `Percentage of Rent Burdened Individuals, ${Math.min(...x_array)} to ${Math.max(...x_array)}`, 'x': 0.05},
                'xaxis': {'title': {'text': 'Year', 'ticklabelstandoff': 10}, 'showgrid': false, 'tickvals': x_array},
                'yaxis': {'title': {'text': 'Percentage of Rent-Burdened Individuals (%)', 'standoff': 15}, 'ticksuffic': '%', 'gridcolor': '#E0E0E0', 'ticklabelstandoff': 5},
            };

            var srb_strings = my_array.map(function(item) {
                return "<b style='font-size:16px;'>" + item['YEAR'] + "</b><br>" + item['NAME'] + ", " + item['PLACE'] + " <br><br>"
                + "Of the estimated " + item['B25070_001E'] + " renters, approx. <b style='font-size:16px; color:#610000;'>" + item['TotalSevereRentBurden'] + "%</b><br>"
                + "were considered <b style='font-size:16px; color:#610000;'>severely rent-burdened</b> <br>during <b style='font-size:14px'>" + item['YEAR'] + "</b>.<extra></extra>";
            });

            var srb_data = [{
                'type': 'scatter',
                'x': x_array,
                'y': srb_y_array,
                'mode': 'lines+markers',
                'line': {'color': '#A865B5'},
                'marker': {'size': 10, 'line': {'width': 2, 'color': '#F5FBFF'}},
                'text': srb_strings,
                'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
                'hovertemplate': '%{text}'
            }];
        
            var srb_layout = {
                'font': {'color': '#020403'},
                'hoverlabel': {'align': 'left'},
                'margin': {'b': 40, 't': 40, 'r': 20},
                'autosize': true,
                'uirevision': true,
                'paper_bgcolor': '#FEF9F3',
                'plot_bgcolor': '#FEF9F3',
                'title': {'text': `Percentage of Severely Rent Burdened Individuals, ${Math.min(...x_array)} to ${Math.max(...x_array)}`, 'x': 0.05},
                'xaxis': {'title': {'text': 'Year', 'ticklabelstandoff': 10}, 'showgrid': false, 'tickvals': x_array},
                'yaxis': {'title': {'text': 'Percentage of Severely Rent-Burdened Individuals (%)', 'standoff': 15}, 'ticksuffic': '%', 'gridcolor': '#E0E0E0', 'ticklabelstandoff': 5},
            };
            
            if (selected_metric == 'Rent Burden') {
                return {'data': rb_data, 'layout': rb_layout};
            }
            else {
                return {'data': srb_data, 'layout': srb_layout};
            }
        }
    }
    """,
    Output('rent_plot', 'figure'),
    [Input('radio-options', 'value'),
     Input('place-dropdown', 'value'),
     Input('census-tract-dropdown', 'value'),
     Input('masterfile_data', 'data')
    ]
)



# ------------ Alerts ------------ #

# Rent-burdened alert
app.clientside_callback(
    """
    function(selected_place, selected_year, alert_masterfile) {
        var selected_place = `${selected_place}`;
        var selected_year = Number(selected_year);
        var my_array = alert_masterfile.filter(item => item['PLACE'] === selected_place && item['YEAR'] === selected_year);

        var dv1 = `${my_array['0']['TotalPop']}`;
        var dv2 = selected_place;
        var dv3 = selected_year;
        var dv4 = `${my_array['0']['OverallRB']}` + '%';
        var dv5 = `${my_array['0']['15to24Pop']}`;
        var dv6 = `${my_array['0']['15to24RB']}` + '%';
        var dv7 = `${my_array['0']['25to34Pop']}`;
        var dv8 = `${my_array['0']['25to34RB']}` + '%';
        var dv9 = `${my_array['0']['35to64Pop']}`;
        var dv10 = `${my_array['0']['35to64RB']}` + '%';
        var dv11 = `${my_array['0']['65olderPop']}`;
        var dv12 = `${my_array['0']['65olderRB']}` + '%';
        

        return [dv1, dv2, dv3, dv4, dv5, dv6, dv7, dv8, dv9, dv10, dv11, dv12]
    }
    """,
    [Output('dv1', 'children'), Output('dv2', 'children'), Output('dv3', 'children'),
     Output('dv4', 'children'), Output('dv5', 'children'), Output('dv6', 'children'),
     Output('dv7', 'children'), Output('dv8', 'children'), Output('dv9', 'children'),
     Output('dv10', 'children'), Output('dv11', 'children'), Output('dv12', 'children')
    ],
    [Input('place-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('alert_masterfile_data', 'data')
    ]
)

# Severely rent-burdened alert
app.clientside_callback(
    """
    function(selected_place, selected_year, alert_masterfile) {
        var selected_place = `${selected_place}`;
        var selected_year = Number(selected_year);
        var my_array = alert_masterfile.filter(item => item['PLACE'] === selected_place && item['YEAR'] === selected_year);

        var ndv1 = `${my_array['0']['TotalPop']}`;
        var ndv2 = selected_place;
        var ndv3 = selected_year;
        var ndv4 = `${my_array['0']['OverallSRB']}` + '%';
        

        return [ndv1, ndv2, ndv3, ndv4]
    }
    """,
    [Output('ndv1', 'children'), Output('ndv2', 'children'), Output('ndv3', 'children'),
     Output('ndv4', 'children')
    ],
    [Input('place-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('alert_masterfile_data', 'data')
    ]
)




# ------------ EXECUTE THE APP ------------ #
if __name__ == '__main__':
    app.run(debug=False)
