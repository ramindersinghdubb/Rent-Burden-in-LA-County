import os
import pandas as pd
from util_func import (
    masterfile_creation,
    mastergeometry_creation,
    lat_lon_center_points
)

# Masterfile creation
masterfile_creation(['B25070', 'B25072'], API_key = os.environ['SECRET_KEY'], batch_size = 400)

# Formatting
ABBREV_NAMES = [file.split('_')[0] for file in os.listdir('data/masterfiles/') if 'masterfile.csv' in file]

df_list = []
for ABBREV_NAME in ABBREV_NAMES:
    CSV_file_path = f'data/masterfiles/{ABBREV_NAME}_masterfile.csv'
    df = pd.read_csv(CSV_file_path)

    if not df.columns.isin(['TotalSevereRentBurden']).any():
        df['TotalRentBurden']   = round( ( (df['B25070_007E'] + df['B25070_008E'] + df['B25070_009E'] + df['B25070_010E']) / df['B25070_001E']) * 100, 2)
        df['RentBurden_15to24'] = round( ( (df['B25072_006E'] + df['B25072_007E']) / df['B25072_002E']) * 100, 2)
        df['RentBurden_25to34'] = round( ( (df['B25072_013E'] + df['B25072_014E']) / df['B25072_009E']) * 100, 2)
        df['RentBurden_35to64'] = round( ( (df['B25072_020E'] + df['B25072_021E']) / df['B25072_016E']) * 100, 2)
        df['RentBurden_65+']    = round( ( (df['B25072_027E'] + df['B25072_028E']) / df['B25072_023E']) * 100, 2)
        df['TotalSevereRentBurden']  = round( ( (df['B25070_010E']) / df['B25070_001E']) * 100, 2)

        df['RentBurden_15to24_str'] = df['RentBurden_15to24'].astype(str) + '%'
        df.loc[df['RentBurden_15to24_str'] == 'nan%', 'RentBurden_15to24_str'] = 'Not Available'
        
        df['RentBurden_25to34_str'] = df['RentBurden_25to34'].astype(str) + '%'
        df.loc[df['RentBurden_25to34_str'] == 'nan%', 'RentBurden_25to34_str'] = 'Not Available'
        
        df['RentBurden_35to64_str'] = df['RentBurden_35to64'].astype(str) + '%'
        df.loc[df['RentBurden_35to64_str'] == 'nan%', 'RentBurden_35to64_str'] = 'Not Available'
        
        df['RentBurden_65+_str'] = df['RentBurden_65+'].astype(str) + '%'
        df.loc[df['RentBurden_65+_str'] == 'nan%', 'RentBurden_65+_str'] = 'Not Available'
    
    # For the trace
    df['dummy'] = 1

    df.to_csv(CSV_file_path, index = False)

    JSON_file_path = f'data/masterfiles/{ABBREV_NAME}_masterfile.json'
    df.to_json(JSON_file_path, orient='records')

# Mastergeometry creation
mastergeometry_creation()

# Accompanying latitudinal and longitudinal center points
lat_lon_center_points()