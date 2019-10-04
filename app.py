# Import dependencies
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt
import numpy as np

# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask setup
app = Flask(__name__)

@app.route("/")
# Create the home page with all available routes
def welcome():
    
    # Return a home page and all available routes
    return (
        f"Welcome to the Climate App<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start_date><br/>"
        f"/api/v1.0/<start_date>/<end_date><br/>"
    )

# Create the precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the dates and precipitation
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary with date as the key and prcp as the value
    precip_list = []
    for date, prcp in results:
        precip_dict = {date: prcp}
        precip_list.append(precip_dict)

    return jsonify(precip_list)

# Create the station route
@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the name of the stations
    results = session.query(Station.name).all()

    session.close()

    # Convert tuples into a normal list
    station_names = list(np.ravel(results))

    return jsonify(station_names)

# Create the tobs route
@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the dates and temperature observations from a year from the last data point
    sel = [Measurement.date, Measurement.tobs]
    results = session.query(*sel).filter(Measurement.date.between(dt.date(2016, 8, 23), dt.date(2017, 8, 23))).all()

    session.close()

    # Create a dictionary with date as the key and prcp as the value
    temp_list = []
    for date, tobs in results:
        temp_dict = {date: tobs}
        temp_list.append(temp_dict)

    return jsonify(temp_list)

# Create the start date search route
@app.route("/api/v1.0/<start_date>")
@app.route("/api/v1.0/<start_date>/<end_date>")
def start(start_date=None,end_date=None):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    min_temp = func.min(Measurement.tobs)
    avg_temp = func.avg(Measurement.tobs)
    max_temp = func.max(Measurement.tobs)
    sel = [min_temp, avg_temp, max_temp]

    if not end_date:
        results = session.query(*sel).filter(Measurement.date >= start_date).all()

        # Create a dictinary that will be returned
        for min_temp, avg_temp, max_temp in results:
            temp_dict = {}
            temp_dict['Minimum Temperature'] = min_temp
            temp_dict['Average Temperature'] = avg_temp
            temp_dict['Max Temperature'] = max_temp

        return jsonify(temp_dict)

    # Query the minimum, average, and max temperature
    results = session.query(*sel).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

    # Create a dictinary that will be returned
    for min_temp, avg_temp, max_temp in results:
        temp_dict = {}
        temp_dict['Minimum Temperature'] = min_temp
        temp_dict['Average Temperature'] = avg_temp
        temp_dict['Max Temperature'] = max_temp

    session.close()

    return jsonify(temp_dict)

if __name__ == "__main__":
    app.run(debug=True)