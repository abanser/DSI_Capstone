# <center> <img src="images/Logo_Strava.png" width="330" height="185" /> meets <img src="images/Logo_Zillow.png" width="450" height="110" /> </center>


#### Summary
 My Capstone project researches the correlation between workout habits of a population as modeled by Strava segment data and real estate prices as aggregated by Zillow.

 Strava is a fitness app used by people to keep track of their running and biking activitiy. A Strava user can create segments, which are sections in the user's path used to track improvement overtime and challenge other users. I will use segment concentration to quantify workout activity. Zillow is a real estate website. I will get information about median home prices by zipcode from Zillow.

#### Motivation

Predicting house prices is hard. It's a problem many are trying to solve in the multibillion dollar real estate industry. Recently Zillow setup a [Kaggle competition](https://www.kaggle.com/c/zillow-prize-1) which awarded $1,000,000 to the top person or team who could help improve it's zestimate home price metric. I hope to add to the conversation about potential predictors that can be used to improve accuracy of existing models.

My intuition going into this project is that there is a positive correlation between house prices and workout habits of a population.


#### Workflow
 ![workflow](images/workflow.png)



#### Strava API challenges
Strava's API returns the top 10 segments within a boundary. In order to get as many segments as possible, I split the city's bounding box into sub sections. I used the code from Ryan Baumann's atletedataviz project, varying split sizes during each run.

#### Segment concentration by type - Austin
Find below biking and running segment concentrations in Austin


<p style="float: left; font-size: 12pt; text-align: center; width: 45%; margin-right: 1%; margin-bottom: 0.5em;">
Biking Segments<img src="images/Strava_Biking_Segments.png" style="width: 100%">
Running Segments<img src="images/Strava_Running_Segments.png" style="width: 100%">
</p>
