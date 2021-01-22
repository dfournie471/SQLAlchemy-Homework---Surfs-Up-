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

app=Flask(__name__)

@app.route("/")
def welcome():
    print("Server has recieved request for 'Welcome' page...")
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tob<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session=Session(engine)
    
    
    results=session.query(Measurement.date,func.round(func.sum(Measurement.prcp),2)).\
        group_by(Measurement.date).all()
    session.close()
    
    
    all_dates=[]
    for date, precipitation in results:
        precipitation_dict={}
        precipitation_dict["date"] = date
        precipitation_dict["precipitation"] = precipitation
        all_dates.append(precipitation_dict)
    
    return jsonify(all_dates)

@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)
    results=session.query(Station.station,Station.name).all()
    session.close()

    all_stations=[]
    for station_id, station_name in results:
        station_dict={}
        station_dict["station_id"]=station_id
        station_dict["station_name"]=station_name
        all_stations.append(station_dict)
    return jsonify(all_stations)







if __name__=='__main__':
    app.run(debug=True)