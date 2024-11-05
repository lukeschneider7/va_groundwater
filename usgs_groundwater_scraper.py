import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json # json is a package that allows us to work with json data
import groundwater_by_state



# Url to get HTML from 
url = f"https://waterdata.usgs.gov/{abv}/nwis/current/?type=gw"
r = requests.get(url, headers=headers)
# Parsing HTML code 
mysoup = BeautifulSoup(r.text, 'html.parser')

fips = pd.read_csv('minoritymajority.csv')
fips['FIPS'] = fips['FIPS'].astype(str).str.zfill(5)
fips_filtered = fips[fips['STNAME'] == state]

# make empty list of counties
counties=[]
# populate county list with one instance for each site number under that county
for td in mysoup.find_all('td'):
    if 'colspan' in td.attrs:
        county_name = td.strong.text
        current_county = county_name
    elif td.find('a') and td.find('a').get('href', '').startswith(f'/{abv}/nwis/uv'):
        counties.append(current_county[1:])


station_number = [x.string for x in mysoup.find_all(lambda tag: tag.has_attr('href') and tag['href'].startswith(f'/{abv}/nwis/uv'))]

date_and_site = [x.string for x in mysoup.find_all('td', attrs = {'nowrap':'nowrap'})]
site_name = [item[1:-1] for i, item in enumerate(date_and_site) if i%2==0]
dates = [item[1:-1] for i, item in enumerate(date_and_site) if i%2==1]

water_depth_strings = [x.find_all('td')[3].string for x in mysoup.find_all('tr', attrs = {'align':'right'})]
water_depths = [item[:-1] if item != None and item != '--' else np.nan for item in water_depth_strings]

counties =  [x.replace('Of', 'of') for x in counties] # uncapitalize 'Of' in places
counties = [x.replace('And', 'and') for x in counties] # uncapitalize 'And' for places
counties = [x[:-4] + 'city' if x.endswith('City') else x for x in counties] # uncapitalize 'City' in places


# Create a DataFrame of scraped information
groundwater_data = pd.DataFrame({
    'Jurisdiction': counties,
    'station number': station_number, 
    'dates': dates,
    'site_name': site_name,
    'water table depth': water_depths})
groundwater_data['water table depth'] = groundwater_data['water table depth'].replace({',': '',
                                                                                    '--': None}, regex=True).astype(float)

# Group by county and calculate statistics
grouped = groundwater_data.groupby('Jurisdiction').agg(
    mean_county_depth=('water table depth', 'mean'),
    median_county_depth = ('water table depth', 'median'),
    num_county_stations = ('water table depth', 'size'),
    min_county_depth = ('water table depth', 'min'),
    max_county_depth = ('water table depth', 'max'),
    q25_county_depth = ('water table depth', lambda x: np.percentile(x, 75)),
    q75_county_depth = ('water table depth', lambda x: np.percentile(x, 75)),
    ).reset_index()
merged_with_stats = pd.merge(groundwater_data, grouped, on='Jurisdiction', how='left')