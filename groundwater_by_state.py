import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

st.title('Analyzing USGS Groundwater Data by State')
st.markdown('### See groundwater data for your state')
state = st.text_input("Your State (ex. va)", key="state")

# Headers for the request
headers = {'User-Agent': 'data science passion project (vrd9sd@virginia.edu) (Language=Python 3.8.2; platform=Mac OSX 13.0.1'}

# Cache the scraping and data processing function
@st.cache_data
def get_groundwater_data(state):
    url = f"https://waterdata.usgs.gov/{state}/nwis/current/?type=gw"
    r = requests.get(url, headers=headers)
    mysoup = BeautifulSoup(r.text, 'html.parser')

    counties, station_number, date_and_site, water_depth_strings = [], [], [], []
    
    for td in mysoup.find_all('td'):
        if 'colspan' in td.attrs:
            county_name = td.strong.text
            current_county = county_name
        elif td.find('a') and td.find('a').get('href', '').startswith(f'/{state}/nwis/uv'):
            counties.append(current_county[1:])
    
    station_number = [x.string for x in mysoup.find_all(lambda tag: tag.has_attr('href') and tag['href'].startswith(f'/{state}/nwis/uv'))]
    date_and_site = [x.string for x in mysoup.find_all('td', attrs={'nowrap': 'nowrap'})]
    site_name = [item[1:-1] for i, item in enumerate(date_and_site) if i % 2 == 0]
    dates = [item[1:-1] for i, item in enumerate(date_and_site) if i % 2 == 1]
    
    water_depth_strings = [x.find_all('td')[3].string for x in mysoup.find_all('tr', attrs={'align': 'right'})]
    water_depths = [item[:-1] if item and item != '--' else np.nan for item in water_depth_strings]

    # Create a DataFrame
    groundwater_data = pd.DataFrame({
        'Jurisdiction': counties,
        'station number': station_number,
        'dates': dates,
        'site_name': site_name,
        'water table depth': water_depths
    })
    groundwater_data['water table depth'] = groundwater_data['water table depth'].replace({',': '', '--': None}, regex=True).astype(float)
    
    # Aggregate statistics
    grouped = groundwater_data.groupby('Jurisdiction').agg(
        mean_county_depth=('water table depth', 'mean'),
        median_county_depth=('water table depth', 'median'),
        num_county_stations=('water table depth', 'size'),
        min_county_depth=('water table depth', 'min'),
        max_county_depth=('water table depth', 'max'),
        q25_county_depth=('water table depth', lambda x: np.percentile(x.dropna(), 25)),
        q75_county_depth=('water table depth', lambda x: np.percentile(x.dropna(), 75)),
    ).reset_index()
    
    return groundwater_data, grouped

if state:
    groundwater_data, grouped = get_groundwater_data(state)

    # User Options for Output
    tab = st.sidebar.selectbox("Choose Output", ["Plots", "Tables"])

    if tab == "Plots":
        fig = px.scatter(
            grouped,
            x='median_county_depth',
            y='num_county_stations',
            color='Jurisdiction',
            hover_name='Jurisdiction',
            labels={
                'median_county_depth': 'Median Water Table Depth (ft)',
                'num_county_stations': 'Number of Stations'
            },
            title='Median Water Table Depth vs. Number of Stations by County'
        )
        fig.update_xaxes(autorange="reversed")
        st.plotly_chart(fig)

        fig, ax = plt.subplots()
        sns.histplot(merged_with_stats['water table depth'], bins=9, ax=ax)
        ax.set_xlabel('Water Table Depth (ft)')
        ax.set_ylabel('Number of Monitoring Stations')
        ax.set_title(f'Water Table Depths in {state.upper()}')
        st.pyplot(fig)
    
    elif tab == "Tables":
        st.write(f"Number of USGS groundwater monitoring stations by county for {state.upper()}")
        st.write(grouped.sort_values(by='num_county_stations', ascending=False))

        st.write(f"All USGS groundwater monitoring sites for {state.upper()}")
        st.write(groundwater_data)