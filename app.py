# Ignore warnings
import warnings
warnings.filterwarnings('ignore')

# Import dependencies
import numpy as np
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, and_
from flask import Flask, jsonify

# Database Setup

# Establish connection
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB, the transaction control
session = Session(engine)

# Flask setup
app = Flask(__name__)

# Flask route
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Welcome to the Hawaiian Weather API!<br/><br/>"
        f"These are the available routes:<br/><br/>"
        f"To see the precipitation from last year: /api/v1.0/precipitation<br/>"
        f"To see the temperatures from last year: /api/v1.0/tobs<br/>"
        f"To see information about the weather stations: /api/v1.0/stations<br/><br/>"
        f"To see information about a specific date, add a date: /api/v1.0/<start><br/>"
        f"Example: /api/v1.0/2011-08-11<br/><br/>"
        f"To see information about a specific date range, add a start and end date: /api/v1.0/<start>/<end><br/>"
        f"Example: /api/v1.0/2011-08-11/2011-08-12<br/><br/>"
        f"Note: the earliest date available is 2010-01-01, and the latest date available is 2017-08-23"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return JSON representation of last years's precipitation"""
    # Query for the dates and precipitation from the last year.

    # Calculate the date 1 year ago from '2017-08-20'
    year_today = dt.date(2017,8,20)
    year_ago = year_today - dt.timedelta(days=365)

    # Query for dates and temp from 2016-08-20 to 2017-08-19
    yearly_data = session.query(Measurement.date,Measurement.prcp, \
                                Measurement.station).\
        filter(and_(Measurement.date >= year_ago, Measurement.date < year_today)).\
        order_by(Measurement.date).all()

    # Convert the query results to a Dictionary using `date` as the key and `tobs` as the value.
    prcp_result = []
    for each in yearly_data:
        yearly_data_dict = {}
        yearly_data_dict['Date'] = each.date
        yearly_data_dict['Precipitation'] = each.prcp
        yearly_data_dict['Station Name'] = each.station
        prcp_result.append(yearly_data_dict)
    return jsonify(prcp_result)

@app.route("/api/v1.0/stations")
def stations():

    # Query to grab all stations
    stations = session.query(Station.__table__).all()

    # Convert query results to dictionary
    stations_result = []
    for each in stations:
        stations_dict = {}
        stations_dict['ID'] = each.id
        stations_dict['Station #'] = each.station
        stations_dict['Name'] = each.name
        stations_dict['Latitude'] = each.latitude
        stations_dict['Longitude'] = each.longitude
        stations_dict['Elevation'] = each.elevation
        stations_result.append(stations_dict)
    return jsonify(stations_result)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return JSON representation of last years's temperature"""
    # Query for the dates and temperature observations from the last year.

    # Calculate the date 1 year ago from '2017-08-20'
    year_today = dt.date(2017,8,20)
    year_ago = year_today - dt.timedelta(days=365)

    # Query for dates and temp from 2016-08-20 to 2017-08-19
    yearly_data = session.query(Measurement.date,Measurement.tobs, \
                                Measurement.station).\
        filter(and_(Measurement.date >= year_ago, Measurement.date < year_today)).\
        order_by(Measurement.date).all()

    # Convert the query results to a Dictionary using `date` as the key and `tobs` as the value.
    temp_result = []
    for each in yearly_data:
        yearly_data_dict = {}
        yearly_data_dict['Date'] = each.date
        yearly_data_dict['Temperature'] = each.tobs
        yearly_data_dict['Station Name'] = each.station
        temp_result.append(yearly_data_dict)
    return jsonify(temp_result)

@app.route("/api/v1.0/<start_date>")
def calc_temps(start_date):
    """TMIN, TAVG, and TMAX for a list of dates.

    Args:
        start_date (string): A date string in the format %Y-%m-%d

    Returns:
        TMIN, TAVE, and TMAX
    """

    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date == start_date).all()

    func_temps = []
    for each in result:
        func_dict = {}
        func_dict['Minimum Temperature'] = each[0]
        func_dict['Average Temperature'] = each[1]
        func_dict['Maximum Temperature'] = each[2]
        func_temps.append(func_dict)
    return jsonify(func_temps)

@app.route("/api/v1.0/<start_date>/<end_date>")
def calc_temps_range(start_date,end_date):
    """TMIN, TAVG, and TMAX for a list of dates.

    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string: A date string in the format %Y-%m-%d

    Returns:
        TMIN, TAVE, and TMAX
    """

    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    func_temps = []
    for each in result:
        func_dict = {}
        func_dict['Minimum Temperature'] = each[0]
        func_dict['Average Temperature'] = each[1]
        func_dict['Maximum Temperature'] = each[2]
        func_temps.append(func_dict)
    return jsonify(func_temps)

if __name__ == '__main__':
    app.run(debug=True)
