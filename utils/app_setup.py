import os
import pandas as pd
from dash import dcc, html
from datetime import datetime


ref_df = pd.read_csv('data/reference.txt', sep='|')

# --
# Dropdown options
# --

ALL_ABBREV_NAMES = list(ref_df['ABBREV_NAME'])
ALL_PLACES_OPTIONS = [{'label': html.Span([i], style = {'color': '#151E3D'}), 'value': j} for i, j in zip(ref_df['CITY'], ALL_ABBREV_NAMES)]

ALL_YEARS = list(range(min(ref_df['INITIAL_YEAR']), max(ref_df['RECENT_YEAR']) + 1))
ALL_YEARS_OPTIONS = [{'label': html.Span([i], style = {'color': '#151E3D'}), 'value': i} for i in ALL_YEARS]

# Generate available year options for the selected place
PLACE_YEAR_OPTIONS = {}
for ABBREV_NAME in ALL_ABBREV_NAMES:
    int_year = ref_df.loc[ref_df['ABBREV_NAME'] == ABBREV_NAME, 'INITIAL_YEAR'].iloc[0]
    rec_year = ref_df.loc[ref_df['ABBREV_NAME'] == ABBREV_NAME, 'RECENT_YEAR'].iloc[0]

    avail_years = list(range(int_year, rec_year + 1))
    unavail_years = [i for i in ALL_YEARS if i not in avail_years]

    year_options = [dict(item, **{'disabled': True}) if item['value'] in unavail_years else dict(item) for item in ALL_YEARS_OPTIONS]

    PLACE_YEAR_OPTIONS[ABBREV_NAME] = year_options

# Generate available place options for the selected year
files = [f'data/masterfiles/{file}' for file in os.listdir('data/masterfiles/') if file.endswith('masterfile.csv')]
df_list = []
for file in files:
    df_list.append( pd.read_csv(file) )
df = pd.concat(df_list, ignore_index = True)

YEAR_PLACE_OPTIONS = {}
for YEAR in ALL_YEARS:
    dummy_df = df[df['YEAR'] == YEAR]

    avail_places = list(dummy_df['ABBREV_NAME'].unique())
    unavail_places = [i for i in ALL_ABBREV_NAMES if i not in avail_places]

    place_options = [dict(item, **{'disabled': True}) if item['value'] in unavail_places else dict(item) for item in ALL_PLACES_OPTIONS]

    YEAR_PLACE_OPTIONS[YEAR] = place_options

# -- -- -- -- --
# Footer string
# -- -- -- -- --
footer_string = f"""
### <b style='color:#800000;'>Information</b>

This website allows you to view the percentage of rent-burdened individuals and/or severely rent-burdened individuals for census tracts across various cities in Los Angeles county. <br>

For the purposes of this website . . . <ul>
<li><b style='color:#B22222;'>Rent-burdened individuals</b> are individuals for whom <u style='color:#B22222;'><b style='color:#B22222;'>over 30% of their income</b></u> goes to paying rent </li>
<li> <b style='color:#800000;'>Severely rent-burdened individuals</b> are individuals for whom <u style='color:#800000;'><b style='color:#800000;'>over 50% of their income</b></u> goes to paying rent </li>
</ul>

Use the dropdowns to choose a city of interest and a year of interest.

Click on a census tract to visualize how the percentage of either rent-burdened or severely rent-burdened individuals has evolved over time in the plot.
You can also view information on the age demographics of rent-burdened individuals for the chosen census tract.

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

© {datetime.now().year} Raminder Singh Dubb
"""

# -- -- -- --
# Containers
# -- -- -- --

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