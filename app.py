# Libraries
from dash import dcc, html, Dash
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import feffery_markdown_components as fmc

from utils.app_setup import (
    YEAR_PLACE_OPTIONS,
    PLACE_YEAR_OPTIONS,
    ALL_YEARS,
    footer_string,
    geodata_map, geodata_plot
)


# -- -- --
# Colors
# -- -- --
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




# -- --
# App
# -- --
app = Dash(__name__,
           external_stylesheets = [dbc.themes.SIMPLEX, "assets/style.css"],
           meta_tags = [{"name": "viewport", "content": "width=device-width, initial-scale=1"}])
server = app.server
app.title = 'Rent Burden in Los Angeles County'



app.layout = dbc.Container([
    # Title
    html.Div([html.B("Rent Burden in Los Angeles County")],
             style = {'display': 'block',
                'color': MaroonRed_color,
                'margin': '0.2em 0',
                'padding': '0px 1.25% 0px 1.25%', # Numbers represent spacing for the top, right, bottom, and left (in that order)
                'font-family': 'Trebuchet MS, sans-serif',
                'font-size': '220.0%'
               }
            ),
    # Subtitle
    html.Div([html.P(f"Rent Burden and Severe Rent Burden for Census Tracts across Cities and Census-Designated Places in Los Angeles County, {min(ALL_YEARS)} to {max(ALL_YEARS)}")],
             style = {'display': 'block',
                'color': ObsidianBlack_color,
                'margin': '-0.5em 0',
                'padding': '0px 1.25% 0px 1.25%',
                'font-family': 'Trebuchet MS, sans-serif',
                'font-size': '105.0%'
               }
            ),
    # Horizontal line rule
    html.Div([html.Hr()],
             style = {'display': 'block',
                'height': '1px',
                'border': 0,
                'margin': '-0.9em 0',
                'padding': '0px 1.25% 0px 1.25%',
                'justify-content': 'spacing-around'
               }),

    # Dropdowns
    html.Div([
        dbc.Row([
        dbc.Col([
            dcc.Dropdown(id          = 'place-dropdown',
                         placeholder = 'Select a place',
                         options     = YEAR_PLACE_OPTIONS[2023],
                         value       = 'LongBeach',
                         clearable   = False
                        )],
            width = 12, sm = 12, xl = 4,
            style = {'margin': '0 0', 'padding': '30px 1.25% 0px 1.25%'}),
        dbc.Col([
            dcc.Dropdown(id          = 'year-dropdown',
                         placeholder = 'Select a year',
                         options     = PLACE_YEAR_OPTIONS['LongBeach'],
                         value       = max(ALL_YEARS),
                         clearable   = False,
                         searchable  = False
                        )],
            width = 12, sm = 12, xl = 2,
            style = {'margin': '0 0', 'padding': '30px 1.25% 0px 1.25%'}),
        dbc.Col([
            dcc.Dropdown(id          = 'census-tract-dropdown',
                         placeholder = 'Click on a census tract in the map',
                         clearable   = True
                        )],
            width = 12, sm = 12, xl = 3,
            style = {'margin': '0 0', 'padding': '30px 1.25% 0px 1.25%'}),
        dbc.Col([
            dcc.Dropdown(id         = 'measure-dropdown',
                         options    = [{'label': 'Rent Burden', 'value': 'Rent Burden'},
                                       {'label': 'Severe Rent Burden', 'value': 'Severe Rent Burden'},
                                       {'label': 'Rent Burden by Age', 'value': 'Rent Burden by Age'}],
                         value      = 'Rent Burden',
                         clearable  = False,
                         searchable = False
                         )],
            width = 12, sm = 12, xl = 3,
            style = {'margin': '0 0', 'padding': '30px 1.25% 0px 1.25%'})
        ]),
    ], style = {"padding": "0px 2.00% 10px 2.00%"}),
    
    # Map and plot
    html.Div([
            dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(children = [html.B(id="map-title1"), " in ", html.B(id="map-title2"), " by Census Tract, ", html.B(id="map-title3")],
                                   style = {'background-color': MaroonRed_color, 'color': '#FFFFFF'}),
                    dbc.CardBody([
                        dcc.Loading(color   = '#29B0F0',
                                    display = 'show',
                                    style   = {'position': 'relative', 'margin-top': '75%'}),
                        geodata_map],
                        style = {'background-color': AlabasterWhite_color})
                ])
            ], width = 12, xl = 6),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(children = html.B(id = "plot-title"),
                                   style = {'background-color': Teal_color, 'color': '#FFFFFF'}),
                    dbc.CardBody([geodata_plot],
                                 style = {'background-color': AlabasterWhite_color})
                ])
            ], width = 12, xl = 6)
        ], align = 'center', justify = 'center')
    ], style = {'padding': '10px 1.05% 20px 1.05%'}),

    # Footer
    html.Div([
        fmc.FefferyMarkdown(markdownStr    = footer_string,
                            renderHtml     = True,
                            style          = {'background': LightBrown_color, 'margin-top': '1em', 'padding': '0px 2.00% 0px 2.00%'})
    ]),

    # Data
    dcc.Store( id = 'MASTERFILE' ),
    dcc.Store( id = 'LAT-LON' ),
    dcc.Store( id = 'YEAR_PLACE_OPTIONS', data = YEAR_PLACE_OPTIONS ),
    dcc.Store( id = 'PLACE_YEAR_OPTIONS', data = PLACE_YEAR_OPTIONS ),

], style = {'background-color': LightBrown_color, "padding": "0px 0px 20px 0px"})



# ------------ CALLBACKS ------------ #
#
# Data:
#  place value -> masterfile data
#  year value -> lat/lon center point data
#
# Dropdowns:
#  year value -> place options
#  place value -> year options
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
# ----------------------------------- #

# -- -- -- --
# Data
# -- -- -- --

# Masterfile
app.clientside_callback(
    """
    async function(selected_place) {
        const url = `https://raw.githubusercontent.com/ramindersinghdubb/Rent-Burden-in-LA-County/refs/heads/main/data/masterfiles/${selected_place}_masterfile.json`;
        const response = await fetch(url);
        const data = await response.json();
        return data;
    }
    """,
    Output('MASTERFILE', 'data'),
    Input('place-dropdown', 'value')
)

# Latitudinal/longitudinal center points
app.clientside_callback(
    """
    async function(selected_year) {
        const url = `https://raw.githubusercontent.com/ramindersinghdubb/Rent-Burden-in-LA-County/refs/heads/main/data/lat_lon_center_points/${selected_year}_latlon_center_points.json`;
        const response = await fetch(url);
        const data = await response.json();
        return data;
    }
    """,
    Output('LAT-LON', 'data'),
    Input('year-dropdown', 'value')
)


# -- -- -- --
# Dropdowns
# -- -- -- --

# Place dropdown options
app.clientside_callback(
    """
    function(selected_year, YEAR_PLACE_OPTIONS) {
        return YEAR_PLACE_OPTIONS[selected_year]
    }
    """,
    Output('place-dropdown', 'options'),
    [Input('year-dropdown', 'value'),
     Input('YEAR_PLACE_OPTIONS', 'data')
    ]
)

# Year dropdown options
app.clientside_callback(
    """
    function(selected_place, PLACE_YEAR_OPTIONS) {
        return PLACE_YEAR_OPTIONS[selected_place]
    }
    """,
    Output('year-dropdown', 'options'),
    [Input('place-dropdown', 'value'),
     Input('PLACE_YEAR_OPTIONS', 'data')
    ]
)

# Census tract options
app.clientside_callback(
    """
    function(selected_place, selected_year, MASTERFILE) {
        var options = MASTERFILE.filter(x => x['YEAR'] === selected_year);
        var tract_options = options.map(item => { return item.TRACT });
        return tract_options
    }
    """,
    Output('census-tract-dropdown', 'options'),
    [Input('place-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('MASTERFILE', 'data')
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




# -- -- -- --
# Titles
# -- -- -- --


# Map title
app.clientside_callback(
    """
    function(selected_metric, selected_place, selected_year, MASTERFILE) {
        var my_array = MASTERFILE.filter(item => item['YEAR'] === selected_year);
        var city_array = my_array.map(({CITY}) => CITY);
        var selected_city = city_array[0];

        if ( ['Rent Burden', 'Rent Burden by Age'].includes(selected_metric) ) {
            var title = 'Percentage of Rent Burdened Individuals';
        } else {
            var title = 'Percentage of Severely Rent Burdened Individuals';
        }
        
        return [title, selected_city, selected_year];
    }
    """,
    [Output('map-title1', 'children'),
     Output('map-title2', 'children'),
     Output('map-title3', 'children')
    ],
    [Input('measure-dropdown', 'value'),
     Input('place-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('MASTERFILE', 'data')
    ]
)

# Plot title
app.clientside_callback(
    """
    function(selected_tract, MASTERFILE) {
        if (selected_tract == undefined){
            return "Please click on a tract.";
        } else {
            var selected_city = MASTERFILE[0]['CITY'];
            return `${selected_city}, ${selected_tract}`;
        }
    }
    """,
    Output('plot-title', 'children'),
    [Input('census-tract-dropdown', 'value'),
     Input('MASTERFILE', 'data')
    ]
)


# -- -- --
# Graphs
# -- -- --

# Choropleth map
app.clientside_callback(
    """
    function(selected_metric, selected_place, selected_year, selected_tract, MASTERFILE, LAT_LON){
        var my_array = MASTERFILE.filter(item => item['YEAR'] === selected_year);
        
        var url_path = `https://raw.githubusercontent.com/ramindersinghdubb/Rent-Burden-in-LA-County/refs/heads/main/data/mastergeometries/${selected_year}_mastergeometry.geojson`;
        
        var locations_array  = my_array.map( ({GEO_ID}) => GEO_ID );
        var customdata_array = my_array.map( ({TRACT}) => TRACT );
        
        var lat_lon_array = LAT_LON.filter(item => item['ABBREV_NAME'] === selected_place);
        const lon_center  = lat_lon_array[0]['LON_CENTER'];
        const lat_center  = lat_lon_array[0]['LAT_CENTER'];

        if ( ['Rent Burden', 'Rent Burden by Age'].includes(selected_metric) ) {
            var z_array = my_array.map( ({TotalRentBurden}) => TotalRentBurden );
            var strings = my_array.map(function(item) {
                return "<b style='font-size:16px;'>" + item['TRACT'] + "</b><br>" + item['CITY'] + ", Los Angeles County<br><br>"
                + "Of the estimated " + item['B25070_001E'] + " renters, approx. <b style='font-size:16px; color:#800000;'>" + item['TotalRentBurden'] + "%</b><br>"
                + "were considered <b style='font-size:16px; color:#800000;'>rent-burdened</b> during <b style='font-size:14px'>" + item['YEAR'] + "</b>.<extra></extra>";
                });
            var colorscale = 'YlOrRd';
            var colorbar_title = 'Percentage of<br>Rent-Burdened<br>Individuals (%)';
        } else {
            var z_array = my_array.map( ({TotalSevereRentBurden}) => TotalSevereRentBurden );
            var strings = my_array.map(function(item) {
                return "<b style='font-size:16px;'>" + item['TRACT'] + "</b><br>" + item['CITY'] + ", Los Angeles County<br><br>"
                + "Of the estimated " + item['B25070_001E'] + " renters, approx. <b style='font-size:16px; color:#610000;'>" + item['TotalSevereRentBurden'] + "%</b><br>"
                + "were considered <b style='font-size:16px; color:#610000;'>severely rent-burdened</b><br>during <b style='font-size:14px'>" + item['YEAR'] + "</b>.<extra></extra>";
                });
            var colorscale = 'Hot';
            var colorbar_title = 'Percentage of<br>Severely<br>Rent-Burdened<br>Individuals (%)';
        }
        
        var data = [{
            'type': 'choroplethmap',
            'customdata': customdata_array,
            'geojson': url_path,
            'locations': locations_array,
            'featureidkey': 'properties.GEO_ID',
            'colorscale': colorscale,
            'reversescale': true,
            'z': z_array,
            'marker': {'line': {'color': '#020403', 'width': 1.75}, 'opacity': 0.7},
            'text': strings,
            'colorbar': {'outlinewidth': 2,
                         'ticklabelposition': 'outside bottom',
                         'ticksuffix': '%',
                         'title': {'font': {'color': '#020403', 'weight': 500}, 'text': colorbar_title}},
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
        
        if (selected_tract != undefined){
            var aux_array           = my_array.filter(item => item['TRACT'] === selected_tract);
            var aux_locations_array = aux_array.map( ({GEO_ID}) => GEO_ID );
            var aux_z_array         = aux_array.map( ({dummy}) => dummy );
        
            var aux_data = {
                'type': 'choroplethmap',
                'geojson': url_path,
                'locations': aux_locations_array,
                'featureidkey': 'properties.GEO_ID',
                'colorscale': [[0, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,0)']],
                'showscale': false,
                'z': aux_z_array,
                'zmin': 0, 'zmax': 1,
                'marker': {'line': {'color': '#04D9FF', 'width': 4}},
                'hoverinfo': 'skip',
            }
            
            data.push(aux_data);
        }
        
        return {'data': data, 'layout': layout};
    }
    """,
    Output('chloropleth_map', 'figure'),
    [Input('measure-dropdown', 'value'),
     Input('place-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('census-tract-dropdown', 'value'),
     Input('MASTERFILE', 'data'),
     Input('LAT-LON', 'data')
    ]
)



# Plot
app.clientside_callback(
    """
    function(selected_metric, selected_place, selected_tract, selected_year, MASTERFILE){        
        if (selected_tract != undefined) {
            var my_array = MASTERFILE.filter(item => item['TRACT'] === selected_tract);
            var my_array = my_array.sort((a, b) => a.YEAR - b.YEAR);
            
            var x_array = my_array.map( ({YEAR}) => YEAR) ;

            if ( selected_metric == 'Rent Burden' ) {
                var y_array = my_array.map( ({TotalRentBurden}) => TotalRentBurden );

                var strings = my_array.map(function(item) {
                    function str_parse(col) {
                        return isNaN( parseFloat(item[col]) ) ? 'Not Available' : parseFloat(item[col]).toString() + '%';
                    }

                    const RB_15to24 = str_parse('RentBurden_15to24');
                    const RB_25to34 = str_parse('RentBurden_25to34');
                    const RB_35to64 = str_parse('RentBurden_35to64');
                    const RB_65 = str_parse('RentBurden_65+');

                    return "<b style='font-size:16px;'>" + item['YEAR'] + "</b><br>" + item['TRACT'] + ", " + item['CITY'] + " <br><br>"
                    + "Of the estimated " + item['B25070_001E'] + " renters, approx.<br><b style='font-size:16px; color:#800000;'>" + item['TotalRentBurden'] + "%</b> "
                    + "were considered <b style='font-size:16px; color:#800000;'>rent-burdened</b>.<extra></extra>";
                });
                var plot_title = `<b>Percentage of Rent Burdened Individuals</b>, ${Math.min(...x_array)} to ${Math.max(...x_array)}`;
                var line_color = '#C0451C';
            }
            if ( selected_metric == 'Severe Rent Burden' ) {
                var y_array = my_array.map( ({TotalSevereRentBurden}) => TotalSevereRentBurden );
                var strings = my_array.map(function(item) {
                    return "<b style='font-size:16px;'>" + item['YEAR'] + "</b><br>" + item['TRACT'] + ", " + item['CITY'] + " <br><br>"
                    + "Of the estimated " + item['B25070_001E'] + " renters, approx. <b style='font-size:16px; color:#610000;'>" + item['TotalSevereRentBurden'] + "%</b><br>"
                    + "were considered <b style='font-size:16px; color:#610000;'>severely rent-burdened</b> <br>during <b style='font-size:14px'>" + item['YEAR'] + "</b>.<extra></extra>";
                });
                var plot_title = `<b>Percentage of Severely Rent Burdened Individuals</b>, ${Math.min(...x_array)} to ${Math.max(...x_array)}`;
                var line_color = '#800000';
            }

            var data = [{
                'type': 'scatter',
                'x': x_array,
                'y': y_array,
                'mode': 'lines+markers',
                'line': {'color': line_color},
                'marker': {'size': 10, 'line': {'width': 2, 'color': '#F5FBFF'}},
                'text': strings,
                'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
                'hovertemplate': '%{text}'
            }];

            var layout = {
                'font': {'color': '#020403'},
                'hoverlabel': {'align': 'left'},
                'margin': {'b': 40, 't': 40, 'r': 20},
                'autosize': true,
                'uirevision': true,
                'paper_bgcolor': '#FEF9F3',
                'plot_bgcolor': '#FEF9F3',
                'title': {'text': plot_title, 'x': 0.05},
                'xaxis': {'title': {'text': '<b>Year</b>', 'ticklabelstandoff': 10, 'font': {'size': 14}}, 'showgrid': false, 'tick0': Math.min(...x_array), 'dtick': 2, 'ticks': '', 'tickfont': {'color': '#666666'}},
                'yaxis': {'title': {'text': '<b>Percentage (%)</b>', 'standoff': 15, 'font': {'size': 14}}, 'ticksuffix': '%', 'gridcolor': '#E0E0E0', 'ticklabelstandoff': 5, 'ticks': '', 'tickfont': {'color': '#666666'}},
            };

            if (selected_metric == 'Rent Burden by Age') {
                var my_array = my_array.filter(item => item['YEAR'] == selected_year);

                const age_groups = ['RentBurden_15to24', 'RentBurden_25to34', 'RentBurden_35to64', 'RentBurden_65+'];
                var y_array = age_groups.map(key => my_array[0][key]);

                function str_parse(col) {
                    return isNaN( parseFloat(my_array[0][col]) ) ? 'Not Available' : parseFloat(my_array[0][col]).toString() + '%';
                }

                const RB_15to24 = str_parse('RentBurden_15to24');
                const RB_25to34 = str_parse('RentBurden_25to34');
                const RB_35to64 = str_parse('RentBurden_35to64');
                const RB_65 = str_parse('RentBurden_65+');

                var strings = [
                    "Of renters <b style='color:#B22222;'>15 to 24 year old</b>, approx.<br><b style='color:#B22222; font-size:14px;'>" + RB_15to24 + "</b> were rent-burdened.<extra></extra>",
                    "Of renters <b style='color:#B22222;'>25 to 34 year old</b>, approx.<br><b style='color:#B22222; font-size:14px;'>" + RB_25to34 + "</b> were rent-burdened.<extra></extra>",
                    "Of renters <b style='color:#B22222;'>35 to 64 year old</b>, approx.<br><b style='color:#B22222; font-size:14px;'>" + RB_35to64 + "</b> were rent-burdened.<extra></extra>",
                    "Of renters <b style='color:#B22222;'>65 and older</b>, approx.<br><b style='color:#B22222; font-size:14px;'>" + RB_65 + "</b> were rent-burdened.<extra></extra>"
                ]

                var strings = strings.map((item) => "<b style='font-size:16px;'>" + my_array[0]['YEAR'] + "</b><br>" + my_array[0]['TRACT'] + ", " + my_array[0]['CITY'] + " <br><br>" + item );

                var data = [{
                    'type': 'bar',
                    'x': ['15 to 24', '25 to 34', '35 to 64', '65+'],
                    'y': y_array,
                    'marker': {'color': '#800000', 'line': {'color': '#666666', 'width': 2}, 'opacity': 0.8},
                    'text': strings,
                    'textposition': 'none',
                    'hoverlabel': {'bgcolor': '#FAFAFA', 'bordercolor': '#BEBEBE', 'font': {'color': '#020403'}},
                    'hovertemplate': '%{text}'
                }];
                var layout = {
                    'font': {'color': '#020403'},
                    'hoverlabel': {'align': 'left'},
                    'margin': {'b': 40, 't': 40, 'r': 20},
                    'autosize': true,
                    'uirevision': true,
                    'paper_bgcolor': '#FEF9F3',
                    'plot_bgcolor': '#FEF9F3',
                    'title': {'text': `<b>Percentage of Rent Burdened Individuals by Age</b>, ${selected_year}`, 'x': 0.05},
                    'xaxis': {'title': {'text': '<b>Age Group</b>', 'ticklabelstandoff': 10, 'font': {'size': 14}}, 'showgrid': false, 'ticks': '', 'tickfont': {'color': '#666666', 'size': 13}},
                    'yaxis': {'title': {'text': '<b>Percentage (%)</b>', 'standoff': 15, 'font': {'size': 14}}, 'ticksuffix': '%', 'gridcolor': '#E0E0E0', 'ticklabelstandoff': 5, 'ticks': '', 'tickfont': {'color': '#666666'}},
                };
            }
            
            return {'data': data, 'layout': layout};
        }
    }
    """,
    Output('rent_plot', 'figure'),
    [Input('measure-dropdown', 'value'),
     Input('place-dropdown', 'value'),
     Input('census-tract-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('MASTERFILE', 'data')
    ]
)




# Execute the app
if __name__ == '__main__':
    app.run(debug = False)
