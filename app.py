import numpy as np
import pandas as pd

from flask import Flask, jsonify,render_template
from flask_table import Table, Col



#dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
from sqlalchemy.pool import StaticPool

import datetime as dt
from dateutil.relativedelta import relativedelta
# from itertools import *

engine = create_engine("sqlite:///Resources/hawaii.sqlite",\
                    connect_args={'check_same_thread':False},\
                    poolclass=StaticPool)
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
		f"Welcome to the Surf Up API<br><br>"
		f"Available Routes:<br><br>"
		f"<a href=api/precipitation>/api/precipitation</a><br><br>"
		f"<a href=api/stations>/api/stations</a><br><br>"
		f"<a href=api/temperature>/api/temperature</a><br><br>"
		f"<a href=api/<start>/api/<start></a><br><br>"
		f"<a href=api/<start>/<end>/api/<start>/<end></a><br>"
	)
	
@app.route("/api/precipitation")
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
	# year_prcp = []
	# for result in results:
	# 	row = {}
	# 	row[Measurement.date] = row[Measurement.prcp]
	# 	year_prcp.append(row)
	year_prcp_dict=dict(zip(*[iter(year_prcp)]*2)) #dict(itertools.zip_longest(*[iter(year_prcp)] * 2, fillvalue=""))

	return jsonify(year_prcp_dict)

@app.route("/api/stations")
def stations():
	#return a json list of stations from the dataset.
	#results = session.query(Station.name,Station.station).all()

	#all_stations = list(np.ravel(results))

	# return jsonify(all_stations)
	items = session.query(Station.station,Station.name).all()

	# Populate the table
	tableStations = ItemTable(items)

	# Print the html
	return (f"Station List in Hawaii<br><br>"
			f"{tableStations.__html__()}")

@app.route("/api/temperature")
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

@app.route("/api/<start>")
def starttrip(start_date):
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

@app.route("/api/<start>/<end>")
def startendtrip(start_date, end_date):
	round_trip_temps = []
	sel = [func.min(Measurement.tobs), 
       func.max(Measurement.tobs), 
       func.avg(Measurement.tobs)]
	
	results = session.query(*sel).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
	round_trip_temps = list(np.ravel(results))

	return jsonify(round_trip_temps)

class ItemTable(Table):
	station = Col('Station')
	name = Col('Name')

if __name__ == '__main__':
    app.run(debug=True)