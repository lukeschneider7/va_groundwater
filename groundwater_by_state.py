import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json # json is a package that allows us to work with json data
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

r = requests.get('https://httpbin.org/user-agent')
useragent = json.loads(r.text)['user-agent']
headers = {'User-Agent': 'data science passion project (vrd9sd@virginia.edu) (Language=Python 3.8.2; platform=Mac OSX 13.0.1'}

st.title('Analyzing USGS Groundwater Data by State')
st.markdown('### See groundwater data for your state')
st.text_input("Your State (ex. va)", key="state")
state = st.session_state.state

# Url to get HTML from 
url = f"https://waterdata.usgs.gov/{state}/nwis/current/?type=gw"
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
    elif td.find('a') and td.find('a').get('href', '').startswith(f'/{state}/nwis/uv'):
        counties.append(current_county[1:])


station_number = [x.string for x in mysoup.find_all(lambda tag: tag.has_attr('href') and tag['href'].startswith(f'/{state}/nwis/uv'))]

date_and_site = [x.string for x in mysoup.find_all('td', attrs = {'nowrap':'nowrap'})]
dates = [item[1:-1] for i, item in enumerate(date_and_site) if i%2==1]
site_name = [item[1:-1] for i, item in enumerate(date_and_site) if i%2==0]

water_depth_strings = [x.find_all('td')[3].string for x in mysoup.find_all('tr', attrs = {'align':'right'})]
water_depths = [item[:-1] if item != None else np.nan for item in water_depth_strings]

groundwater_data = pd.DataFrame({
    'Jurisdiction': counties,
    'station number': station_number, 
    'dates': dates,
    'site_name': site_name,
    'water table depth': water_depths})
groundwater_data['water table depth'] = groundwater_data['water table depth'].astype('float')

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

fig = px.scatter(
    grouped,
    x='median_county_depth',
    y='num_county_stations',
    color='Jurisdiction',
    hover_name='Jurisdiction',  # Shows county name on hover
    labels={
        'median_county_depth': 'Median Water Table Depth (ft)',
        'num_county_stations': 'Number of Stations'
    },
    title='Median Water Table Depth vs. Number of Stations by County'
)
fig.update_xaxes(autorange="reversed")
# Display Plotly figure in Streamlit
st.plotly_chart(fig)

fig, ax = plt.subplots()
sns.histplot(merged_with_stats['water table depth'], bins=9, ax=ax)
ax.set_xlabel('Water Table Depth (ft)')
ax.set_ylabel('Frequency')
ax.set_title('VA Water Table Depths at USGS Monitoring Locations')
# Display plot in Streamlit
st.pyplot(fig)

st.write(f"Mean groundwater Depths by county for {state}")
depths = grouped.sort_values(by='mean_county_depth', ascending=False)
depths

st.write(f"Number of USGS groundwater monitoring stations by county for {state}")
num_station = grouped.sort_values(by='num_county_stations', ascending=False)
num_station

st.write(f"All USGS groundwater monitoring sites for {state}")
groundwater_data