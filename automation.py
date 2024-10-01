import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import sys
import os
os.system("chmod +x /Users/luke/Downloads/data_pipelines/automation.py")

# Problem 1 - Get user agent and make headers dictionary
r = requests.get('https://httpbin.org/user-agent')
useragent = json.loads(r.text)['user-agent']
headers = {'User-Agent': 'data science passion project (vrd9sd@virginia.edu) (Language=Python 3.8.2; platform=Mac OSX 13.0.1'}

# Url to get HTML from 
url = 'https://waterdata.usgs.gov/va/nwis/current/?type=gw'
r = requests.get(url, headers=headers)

# Parsing HTML code 
mysoup = BeautifulSoup(r.text, 'html.parser')

# make empty list of counties
counties=[]

# populate county list with one instance for each site number under that county
for td in mysoup.find_all('td'):
    if 'colspan' in td.attrs:
        county_name = td.strong.text
        current_county = county_name
    elif td.find('a') and td.find('a').get('href', '').startswith('/va/nwis/uv'):
        counties.append(current_county[1:])


station_number = [x.string for x in mysoup.find_all(lambda tag: tag.has_attr('href') and tag['href'].startswith('/va/nwis/uv'))]


date_and_site = [x.string for x in mysoup.find_all('td', attrs = {'nowrap':'nowrap'})]
dates = [item[1:-1] for i, item in enumerate(date_and_site) if i%2==1]
site_name = [item[1:-1] for i, item in enumerate(date_and_site) if i%2==0]


water_depth_strings = [x.find_all('td')[3].string for x in mysoup.find_all('tr', attrs = {'align':'right'})]
water_depths = [item[:-1] if item != None else np.nan for item in water_depth_strings]

#Making County names consistent with Fips database
counties =  [x.replace('Of', 'of') for x in counties] # uncapitalize 'Of' in places
counties = [x.replace('And', 'and') for x in counties] # uncapitalize 'And' for places
counties = [x[:-4] + 'city' if x.endswith('City') else x for x in counties] # uncapitalize 'City' in places

groundwater_data = pd.DataFrame({
    'Jurisdiction': counties,
    'station number': station_number, 
    'dates': dates,
    'site_name': site_name,
    'water table depth': water_depths})

csv_file_path = 'water_table_depths.csv'
if not os.path.exists(file_path):
    os.chdir(sys.path[0])  #get cwd
    groundwater_data.to_csv(file_path, index=False)
else:
    new_data.to_csv(csv_file_path, mode='a', header=False, index=False)