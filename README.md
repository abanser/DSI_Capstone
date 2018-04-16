# <center> Final Proposal for Capstone </center>

## <center> Strava meets Zillow </center>



 - What are you trying to do? My Capstone project seeks to research a correlation between workout habits of the population of Austin, TX as modeled by Strava segment data and real estate prices as aggregated by Zillow.

- How has this problem been solved before? While modeling real estate trends and workout habits have been solved separately before, I've not found an open source project which merges the two datasets. I am hoping to find something interesting after overlaying these sets of data

- Who cares? If you're successful, what will the impact be? The results of this project can be useful for
  - Strava: By leveraging the data they generate in a creative way outside their current business model, Strava can gain more business value.
  - Zillow: By including variables of workout habits in their datasets, Zillow can potentially augment existing models
  - City of Austin: The City of Austin can get insights into where to build new parks for the city


- How will you present your work?
  - Presentation slides and J3 or Bokeh visualization given the time


- What are your data sources? What is the size of your dataset, and what is your storage format?
  - My data sources are Zillow, Strava API, Google geocoding API and US census bureau. After my first pass run, I have several thousand segment data points. I will store my data in a PostGres SQL database.


- What are potential problems with your capstone, and what have you done to mitigate these problems?
  - Potential problems are not getting enough data to draw a conclusion on my initial hypothesis. If I don't get enough data from Austin, I will consider running the analysis on a larger city.


- What is the next thing you need to work on?
  - I have already downloaded segment data from Strava and house price data from Zillow. I have created a few initial plots. See below - The plot indicates Strava running segments in Austin, TX. My next step is to merge these data and start analyzing them.



![alt text](https://github.com/abanser/DSI_Capstone/tree/master/images/Strava_Running_Segments.png)
