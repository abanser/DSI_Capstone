#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
from stravalib.client import Client
import pandas as pd
from ratelimit import rate_limited
from sqlalchemy import create_engine
from geocodio import GeocodioClient


ONE_MINUTE = 60
chunksize = 10


#Initialize api keys and database connections to use in code

STRAVA_API_KEY = os.environ.get('STRAVA_API_KEY')
GEOCODIO_API_KEY = os.environ.get('GEOCODIO_API_KEY')

client = Client(access_token=STRAVA_API_KEY)
geocodio_client = GeocodioClient(GEOCODIO_API_KEY)

engine = create_engine('postgresql://tom:jerry@mydbs.cahzu59qwcbo.us-east-2.rds.amazonaws.com:5432/strava_zillow')



#bisect_rectange function from:

#Author: <Ryan Baumann>
#Title: <athletedataviz>
#Availability: <https://www.ryanbaumann.com/blog/2016/4/10/on-caching-how-advs-segments-works>

def bisect_rectange(numSplits, minlat, minlong, maxlat, maxlong):
    """Split a lat long bounded rectangle into (numSplits+1)^2 sub-rectangles.
       Returns a list of arrays containing lat long bounds for sub-rectangles
    """
    #initialize function variables
    longpoints = []
    latpoints = []
    extents = []

    #Get a list of the split lat/long locations in the rectangle
    for i in range(numSplits+1):
        latpoints.append( (minlat + ((maxlat-minlat)/numSplits)*i) )
        longpoints.append( (minlong + ((maxlong-minlong)/numSplits)*i) )

    #Loop through the line locations and create a list of sub-rectangles
    for latindex, latmin in enumerate(latpoints):
        for longindex, longmin in enumerate(longpoints):
            if latindex<(len(latpoints)-1) and longindex<(len(longpoints)-1):
                newextent = [latmin, longmin, latpoints[latindex+1], longpoints[longindex+1]]
                extents.append(newextent)
    return extents


def getsegs (bounds, split):
    """Takes lat long bounds for area
        Splits the bounds
        Uses sub bounds to get information on segments from Strava API
        Uses segment information to get zipcode information from geocodio API
        Saves data to PostGres database
    """
    segmentslist=bisect_rectange(split, bounds[0], bounds[1], bounds[2], bounds[3])
    count=1
    segpass=0
    
    #Get list of segment ids currently in database
    query="""select seg_id from segment;"""
    df = pd.read_sql_query(query,con=engine)
    segids=set(df.seg_id)
        
    while count < len(segmentslist):
        try:
            for i in segmentslist:
                segments=getsegmentinfo(i)
                
                
                for seg in segments:
                    #If running function several times for different splits, this ignores existing segments and prints a message
                    if seg.id in segids: 
                        segpass+=1
                        if (segpass % 10 == 0): 
                            print ("{} segments already exist".format(segpass))
                    #Else this is a new segment, so get details from the strava and geocodio apis and save them to a dataframe and eventually to the database
                    else:
                        location = geocodio_client.reverse((seg.start_latlng[0], seg.start_latlng[1]))
                        zipcode=location['results'][0]['address_components']['zip']
                        
                        newrow = {'seg_id' : seg.id,
                            'resource_state': seg.resource_state,
                            'climb_category':seg.climb_category,
                            'climb_category_desc':seg.climb_category_desc,
                            'average_grade':seg.avg_grade,
                            'elev_difference': str(seg.elev_difference).split()[0],
                            'distance': str(seg.distance).split()[0],
                            'name' : seg.name,
                            'start_lat' : seg.start_latlng[0],
                            'start_long' : seg.start_latlng[1],
                            'end_lat' : seg.end_latlng[0],
                            'end_long' : seg.end_latlng[1],
                            'points' : seg.points,
                            'starred':seg.starred,
                            'zipcode':zipcode
                            }
                        df=pd.DataFrame(newrow, index=[0])
                    
                        try:
                            #Save dataframe to database
                            df.to_sql('segment', engine,index=False,if_exists='append')
                        except:
                            pass

                #Prints message which keeps track of number of sub bounds completed     
                if (count % 10) == 0:
                    print ("Getting segments in bound {} of {}".format(count, len(segmentslist)))
                count+=1
        except Exception as inst:
            print (inst) 
    return None



def getsegdetails():
    """ Check for segment ids in segment database that are not in the segment details database
        Gets segment details for these ids
        Save details to PostGres database
    """
    
    
    connection = engine.connect()
    #Query to get segment ids in segment database that are not in segment details database
    unique_segments = connection.execute("""SELECT segment.seg_id
                                         FROM segment
                                         LEFT JOIN segment_details
                                         ON segment.seg_id = segment_details.seg_id
                                         WHERE segment_details.seg_id IS NULL;""")
    connection.close()
    count=1
    
    while count < unique_segments.rowcount:
        try:
            #Get details for segment ids and save in segment_details database
            for segmentid in unique_segments:
                segment=segmentid['seg_id']
                segdetails=getdetails(segment)
                
                
                newrow = {'seg_id' : segment,
                'maximum_grade':segdetails.maximum_grade,
                'activity_type' : segdetails.activity_type,
                'elevation_low' : str(segdetails.elevation_low).split()[0],
                'elevation_high' : str(segdetails.elevation_high).split()[0],
                'date_created' : segdetails.created_at.replace(tzinfo=None),
                'date_updated': segdetails.updated_at.replace(tzinfo=None),
                'total_elevation_gain':str(segdetails.total_elevation_gain).split()[0],
                'effort_count' : segdetails.effort_count,
                'athlete_count' : segdetails.athlete_count,
                'star_count':segdetails.star_count,
                'city':segdetails.city,
                'state':segdetails.state,
                'country':segdetails.country,
                'private':segdetails.private,
                'hazardous':segdetails.hazardous
                     }
                
                df=pd.DataFrame(newrow, index=[0])
                
                try:
                    #Save dataframe to database
                    df.to_sql('segment_details', engine,index=False,if_exists='append')
                except:
                    pass
                
                #Prints message which keeps track of number of segment ids completed
        
                if (count % 10) == 0:
                    print ("Getting segments {} of {}".format(count, unique_segments.rowcount))
                count+=1
        
        except Exception as inst:
            print (inst)
    return None
    
    
@rate_limited(35, ONE_MINUTE) #Use wrapper function to avoid getting kicked out by Strava API
def getsegmentinfo(boundsarray):
    segments = client.explore_segments(boundsarray, activity_type='running')
    return segments

@rate_limited(35, ONE_MINUTE) #Use wrapper function to avoid getting kicked out by Strava API
def getdetails(segid):
    segdetails=client.get_segment(segid)
    return segdetails

 
def main():
    
    #Hard coded bounds for several city limits
    #See City_Bounds.txt file for more bounds
    TXbounds=[29.7996,-98.188,30.6759,-97.2989]
    
    #Vary splits and bounds to get more segments

    print ('Updating segment table')
    getsegs(TXbounds, 65)
   
    print ('Updating segment details table')
    getsegdetails()

if __name__== "__main__":
    main()