## half_marathons_scraper bakground

Recently I read a New York Times article on land subsidence in the tidewater region of Virginia and the related over pumping of the Potomac Aquifer. As a Virginia resident this got me thinking about how groundwater sources are monitored in the state I call home.

## The Data

   The USGS happens to have current condition data on 193 groundwater stations in Virginia monitoring the depth to water level in feet. The records are not instantaneous but rather give a latest updated depth from a few minutes to an hour from when you are accessing the dashboard. [usgs current conditions for groundwater](https://waterdata.usgs.gov/va/nwis/current/?type=gw).


## Work 
This project scrapes groundwater data from the USGS website for Virginia counties. It utilizes the requests library to fetch the HTML content, which is then parsed using BeautifulSoup. Key data extracted includes jurisdiction names, station numbers, dates, site names, and water table depths. The cleaned data is stored in a pandas DataFrame and exported to a CSV file. This data was then merged with a virginia fips/county dataset to make a choropleth to vizualize water table depths and station counts by counties.

## Results
[Jupyter notebook results](https://lukeschneider7.github.io/va_groundwater/va_groundwater_scraper.html)

## Future Work
5. **Automate retrieval of USGS water Data** 
   - I want to use a crontab to get the virginia groundwater monitoring depth data daily so that I can start to analzye changes over time and compare by county
