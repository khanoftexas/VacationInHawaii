import numpy as np
import pandas as pd

from flask import Flask, jsonify


#dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

import datetime as dt
from dateutil.relativedelta import relativedelta

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)

@app.route("/")
def home():
	print("Server received request for 'Home' page.")
	return "Welcome to the Surfs Up Weather API!"

@app.route("/welcome")
#List all available routes
def welcome ():
	return (
		f"Welcome to the Surf Up API<br>"
		f"Available Routes:<br>"
		f"/api/v1.0/precipitation<br>"
		f"/api/v1.0/stations<br>"
		f"/api/v1.0/tobs<br>"
		f"/api/v1.0/start<br>"
		f"/api/v1.0/start/end<br>"
	)
	
@app.route("/api/v1.0/precipitation")
def precipitation():
	#Query for the dates and temperature observations from the last year.
	last_date = session.query(Measurement.date).order_by(desc(Measurement.date)).first()
	last_date = last_date.date
	last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
	last_year_date =  last_date - dt.timedelta(days=365)
	results = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= last_year_date).all()

	year_prcp = list(np.ravel(results))
	#results.___dict___
	#Create a dictionary using 'date' as the key and 'prcp' as the value.
	year_prcp = []
	for result in results:
		row = {}
		row[Measurement.date] = row[Measurement.prcp]
		year_prcp.append(row)

	return jsonify(year_prcp)

@app.route("/api/v1.0/stations")
def stations():
	#return a json list of stations from the dataset.
	results = session.query(Station.station).all()

	all_stations = list(np.ravel(results))

	return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def temperature():
	#Return a json list of Temperature Observations (tobs) for the previous year
	last_date = session.query(Measurement.date).order_by(desc(Measurement.date)).first()
	last_date = last_date.date
	last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
	last_year_date =  last_date - dt.timedelta(days=365)
	year_tobs = []
	results = session.query(Measurement.tobs).filter(Measurement.date >= last_year_date).all()

	year_tobs = list(np.ravel(results))

	return jsonify(year_tobs)

@app.route("/api/v1.0/<start>")
def start_trip_temp(start_date):
	start_trip = []
	sel = [func.min(Measurement.tobs), 
       func.max(Measurement.tobs), 
       func.avg(Measurement.tobs)]

	results = session.query(*sel).filter(Measurement.date == start_date).all()
	start_trip = list(np.ravel(results))

	return jsonify(start_trip)

def greater_start_date(start_date):

	start_trip_date_temps = []
	sel = [func.min(Measurement.tobs), 
       func.max(Measurement.tobs), 
       func.avg(Measurement.tobs)]
	
	results = session.query(*sel).filter(Measurement.date >= start_date).all()
	start_trip_date_temps = list(np.ravel(results))

	return jsonify(start_trip_date_temps)

@app.route("/api/v1.0/<start>/<end>")

def start_end_trip(start_date, end_date):

	round_trip_temps = []
	sel = [func.min(Measurement.tobs), 
       func.max(Measurement.tobs), 
       func.avg(Measurement.tobs)]
	
	results = session.query(*sel).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
	round_trip_temps = list(np.ravel(results))

	return jsonify(round_trip_temps)


if __name__ == '__main__':
    app.run(debug=True)