#import dependencies
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



#database setup

engine=create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine,reflect=True)

Measurement=Base.classes.measurement
Station=Base.classes.station

#setting global variables for date list
session=Session(engine)
results_1=session.query(Measurement.date).distinct().\
        order_by(Measurement.date).all()
session.close()
dates_list=list(np.ravel(results_1))


#define flask app
app=Flask(__name__)

#set 'Home' route
@app.route("/")
#create function that displays instructions for the pathways
def welcome():
    print("Server has recieved request for 'Welcome' page...")
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/START<br/>"
        f"/api/v1.0/START/END"
    )

#set precipitation route
@app.route("/api/v1.0/precipitation")
# create function that returns precipitation results for query
def precipitation():
    session=Session(engine)
    
    
    #filter query by station with most measurments
    results=session.query(Measurement.date,Measurement.prcp).\
        filter(Measurement.station=='USC00519281').all()
     #close session for efficiency   
    session.close()
    
    
    #create dictionary that uses date as key and precipitation as value
    precipitation_dict={}
    for date, precipitation in results:
        
        precipitation_dict[date] = precipitation
        
        #return jsonified dictionary
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)
    results=session.query(Station.station,Station.name).all()
    session.close()

    station_dict={}
    for station_id, station_name in results:
        station_dict[station_id]=station_name
        
    return jsonify(station_dict)
# set route for tobs
@app.route("/api/v1.0/tobs")
#same repeated process as the precipatition route
def temperature():
    session=Session(engine)
    results = session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >='2016-08-23').\
        filter(Measurement.date <='2017-08-23').all()
    session.close()
    popular_dict={}
    
    for date, measurement_tobs in results:
        popular_dict[date]=measurement_tobs
    return jsonify(popular_dict)

#set route for start date only
@app.route("/api/v1.0/<start>")
def one_date(start):
    #created variable to store the string of start
    canonicalization=f'{start}'
    
    #check to see if date entered in url is valid
    if start in dates_list:
        #create session
        session=Session(engine)
        
        #create query saved to results
        results=session.query(func.min(Measurement.tobs),func.round(func.avg(Measurement.tobs),2),func.max(Measurement.tobs)).\
            filter(Measurement.date >= canonicalization).\
            order_by(Measurement.date).all()
        session.close()
        
        #create list of dictionaries that will display query
        #testing a few aestetics for data display
        #create blank list
        all_temp=[]
        #loop through results query and save elements to dictionary
        for temp_min,temp_avg,temp_max in results:
            temp_dict={}
            temp_dict["Min Temp"]=temp_min
            temp_dict["Average Temp"]=temp_avg
            temp_dict["Max Temp"]=temp_max
            #append dictionaries to all_temp
            all_temp.append(temp_dict)
        
        #return jsonify of all_temp
        return jsonify(all_temp)
    #if date not found return else
    else:
        return f"error! date: {start} not found",404



#repeat procoss of start date to date range
@app.route("/api/v1.0/<start>/<end>")
def date_range(start=None,end=None):
    
    if start in dates_list and end in dates_list and end > start:
        session=Session(engine)
        results_2=session.query(func.min(Measurement.tobs),
                            func.round(func.avg(Measurement.tobs),2),
                            func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).\
                            filter(Measurement.date<= end).all()
    
        session.close()
        all_temp_2=[]
        for temp_min_2,temp_avg_2,temp_max_2 in results_2:
            temp_dict_2={}
            temp_dict_2["Min Temp"]=temp_min_2
            temp_dict_2["Average Temp"]=temp_avg_2
            temp_dict_2["Max Temp"]=temp_max_2
            all_temp_2.append(temp_dict_2)
        
        return jsonify(all_temp_2)
    else:
        return f"error! date range: {start} : {end} not found",404


#close out flask
if __name__=='__main__':
    app.run(debug=True)