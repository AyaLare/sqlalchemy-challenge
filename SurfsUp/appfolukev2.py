# Import the required modules - SqlAlchemy, Flask
import numpy as np

# Pandas and Date modeules
import pandas as pd
import datetime as dt
from datetime import datetime
from datetime import timedelta

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
#from sqlalchemy.ext.automap import automap_basepip
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Import Flask and JSON
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
# Setup the database
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Create our session (link) from Python to the DB
session = Session(engine)

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)
Base.classes.keys()
# reflect the tables
conn = engine.connect()




# 2. Create an app, being sure to pass __name__
#################################################
# Flask Setup
#################################################
app = Flask(__name__)



# 1. Define what to do when a user hits the index route
# @app.route("/")
# def home():
#     print("Server received request for 'Home' page...")
#     return "Welcome to my 'Start' page!"
#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome Foluke's Precipitation and Station API!<br/>"
        f"Available Routes:<br/>"
        f"1. /<br/>"
        f"2. /api/v1.0/precipitation<br/>"
        f"3. /api/v1.0/precipitation_json<br/>"
        f"4. /api/v1.0/station_json<br/>"
        f"5. /api/v1.0/tobs<br/>"
        f"6. /api/v2.0/<start_date><br/>"
        f"7. /about<br/>"
    )

# Define what to do when a user hits the /about route
@app.route("/about")
def about():
    print("Server received request for 'About' page...")
    return "Welcome to my 'About' page!"


# 2. Define what to do when a user hits the /api/v1.0/precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request to display the precipitation dictionary")
    """Create our session link"""
    session = Session(engine)
    measurement = Base.classes.measurement
    station = Base.classes.station
    """Get the date of the most recent data"""
    most_recent = session.query(measurement.date).order_by(measurement.date.desc()).first()
    most_recent_date = most_recent[0]
    date_format = "%Y-%m-%d"  # Format of the date string (YYYY-MM-DD)
    most_recent_date_d = dt.datetime.strptime(most_recent_date, date_format)
    """Calculate the date one year from the last date in data set."""
    twelve_months_ago_date = most_recent_date_d - dt.timedelta(days=365)
    """Run query to get all precipication data"""
    results = session.query(measurement.id, measurement.date, measurement.prcp).\
        filter(measurement.date >= twelve_months_ago_date).\
        order_by(measurement.date).all()
    
    """for row in session.query(Demographics.id, Demographics.occupation).limit(5).all():"""
    """print(row)"""
      # Convert list of tuples into normal list
    precipitation_results = list(np.ravel(results))
    session.close()
    return(precipitation_results)
    """return(most_recent_date)"""


# 3. Define what to do when a user hits the /api/v1.0/precipitation_json
@app.route("/api/v1.0/precipitation_json")
def precipitation_json():
    print("Server received request to display the jsonified precipitation dictionary")
    """Create our session link"""
    session = Session(engine)
    measurement = Base.classes.measurement
    station = Base.classes.station
    """Get the date of the most recent data"""
    most_recent = session.query(measurement.date).order_by(measurement.date.desc()).first()
    most_recent_date = most_recent[0]
    date_format = "%Y-%m-%d"  # Format of the date string (YYYY-MM-DD)
    most_recent_date_d = dt.datetime.strptime(most_recent_date, date_format)
    """Calculate the date one year from the last date in data set."""
    twelve_months_ago_date = most_recent_date_d - dt.timedelta(days=365)
    """Run query to get all precipication data"""
    results = session.query(measurement.id, measurement.date, measurement.prcp).\
        filter(measurement.date >= twelve_months_ago_date).\
        order_by(measurement.date).all()
    # Convert list of tuples into normal list
    precipitation_results = list(np.ravel(results))
    """precipitation_results = np.ravel(results)"""
    session.close()
    return jsonify(precipitation_results)


# 4. Define what to do when a user hits the /api/v1.0/station
@app.route("/api/v1.0/station_json")
def station():
    print("Server received requiest to display the station dictionary")
    """Create our session link"""
    session = Session(engine)
    station = Base.classes.station
    """Get the date of the most recent data"""
    results = session.query(station.station, station.name).distinct(station.station).all()
    results_station = list(np.ravel(results))
    session.close()
    print(results_station)
    return jsonify(results_station)


# 5. Define what to do when a user hits the /api/v1.0/tobs
@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most-active station for the previous year of data"""
    print("Server received request to display the temperature observations of the most active station for the previous year of data")
    """Create our session link"""
    session = Session(engine)
    measurement = Base.classes.measurement
    station = Base.classes.station
              
    # Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
    results_station_most_active = session.query(measurement.station, func.count(measurement.station).label("station_count")
        ).group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).first()
    #print(results_station_most_active)
    most_active_id = results_station_most_active[0]
    #print(most_active_id)
    summary_active_results = session.query(measurement.id, measurement.station, measurement.tobs).\
        filter(measurement.station == most_active_id).\
        order_by(measurement.date).all()
    session.close()
    #print(summary_active_results)
    summary_df = pd.DataFrame(summary_active_results)
    summary_df.describe()
    print(summary_df)
    """summary_result_display = list(np.ravel(summary_df))"""
    """return jsonify(summary_result_display)"""
    all_result = []
    for id, station, tobs in summary_active_results:
        result_dict = {}
        result_dict["id"] = id
        result_dict["station"] = station
        result_dict["temperature"] = tobs
        all_result.append(result_dict)
    return jsonify(all_result) 
    """jsonify(summary_result_display)"""



# 6. Define what to do when a user hits the 5.	/api/v2.0/<start> and /api/v2.0/<start>/<end>
@app.route("/api/v2.0/<start_date>") 
def datafordates(start_date):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range."""
    print("Server received request to extract data based on dates")
    """Create our session link"""
    session = Session(engine)
    measurement = Base.classes.measurement
    station = Base.classes.station
    """ Get the date """
    #most_recent = session.query(measurement.date).order_by(measurement.date.desc()).first()
    #most_recent_date = most_recent[0]  
    date_format = "%Y-%m-%d"
    # most_recent_date_d = dt.datetime.strptime(most_recent_date, date_format)
    start_date_check = dt.datetime.strptime(start_date, date_format)
    #twelve_months_ago_date = most_recent_date_d - dt.timedelta(days=365)
    """filter(measurement.date >= twelve_months_ago_date).\""""
    temperature_period = session.query(measurement.id, measurement.station, measurement.date, measurement.tobs).\
            filter(measurement.date >= start_date_check).\
            order_by(measurement.date.desc()).all()
    summary_df = pd.DataFrame(temperature_period)

    temperature_min = summary_df["tobs"].min()
    temperature_max = summary_df["tobs"].max()
    temperature_average = summary_df["tobs"].mean()
    print("Lowest Temperature =  ", str(temperature_min), "\n")
    print("Hihghest Temperature =  ", str(temperature_max), "\n")
    print("AVerage Temperature =  ", str(round(temperature_average,2)) )
    result = []
    result0 = "<br/>"+ "Start Date supplied: " + start_date
    #result1 = "<br/>"+ "Start Date: " + str(twelve_months_ago_date)
    #result2 = "<br/>"+ " End Date:  " + str(most_recent_date)
    result3 = "<br/>"+ "Minimum temperature is :" + str(temperature_min)
    result4 = "<br/>"+ "Max temperature is :" + str(temperature_max)
    result5 = "<br/>"+ "Average temperature is :" + str(round(temperature_average,2))
    return jsonify(result0 + "\n"  + result3 + "\n" + result4 + "\n" + result5)




if __name__ == "__main__":
    app.run(debug=True)