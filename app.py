import numpy as np
import pandas as pd

from flask import Flask, jsonify,render_template
from flask_table import Table, Col

import datetime

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

# @app.route("/")
# def home():
# 	print("Server received request for 'Home' page.")
# 	return "Welcome to the Surfs Up Weather API!"
@app.route("/")
@app.route("/welcome")
#List all available routes
def welcome ():
	return (
		f"Welcome to the Surf Up API<br><br>"
		f"Available Routes:<br><br>"
		f"<a href=api/precipitation>/api/precipitation</a><br><br>"
		f"<a href=api/stations>/api/stations</a><br><br>"
		f"<a href=api/temperature>/api/temperature</a><br><br>"
		f"<a href=api/start>api/startdate</a><br>"
		f"Please enter Start Date in YYYY-MM-DD format.<br><br>"
		f"<a href=api/start/end>api/startdate/enddate</a><br>"
		f"Please enter Start Date and End Date in YYYY-MM-DD format.<br>"
	)
	
@app.route("/api/precipitation")
def precipitation():
	#Query for the dates and temperature observations from the last year.
	last_date = session.query(Measurement.date).order_by(desc(Measurement.date)).first()
	last_date = last_date.date
	last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
	last_year_date =  last_date - dt.timedelta(days=365)
	results = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= last_year_date,Measurement.prcp !=None).all()

	# year_prcp = list(np.ravel(results))
	# year_prcp_dict=dict(zip(*[iter(year_prcp)]*2)) 
	# return jsonify(year_prcp_dict)

	# Populate the table
	tableRain = RainTable(results)
	# Print the html
	return (
		f"<a href=/welcome> Back to Main Page</a><br><br>"
		f"Rain in Hawaii for Last Year<br><br>"
		f"{tableRain.__html__()}")

@app.route("/api/stations")
def stations():
	results = session.query(Station.station,Station.name).all()

	# Populate the table
	tableStations = StationTable(results)

	# Print the html
	return (
		f"<a href=/welcome> Back to Main Page</a><br><br>"
		f"Station List in Hawaii<br><br>"
		f"{tableStations.__html__()}")

@app.route("/api/temperature")
def temperature():
	#Return a json list of Temperature Observations (tobs) for the previous year
	last_date = session.query(Measurement.date).order_by(desc(Measurement.date)).first()
	last_date = last_date.date
	last_date = dt.datetime.strptime(last_date, "%Y-%m-%d")
	last_year_date =  last_date - dt.timedelta(days=365)
	#year_tobs = []
	results = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= last_year_date,Measurement.prcp !=None).all()

	# year_tobs = list(np.ravel(results))
	# return jsonify(year_tobs)

	# Populate the table
	tableTemperature = TemperatureTable(results)

	# Print the html
	return (
		f"<a href=/welcome> Back to Main Page</a><br><br>"
		f"Temperature in Hawaii for Last Year<br><br>"
		f"{tableTemperature.__html__()}")

@app.route("/api/<start>")
def starttrip(start):
	#start_trip = []
	try:
		datetime.datetime.strptime(start, '%Y-%m-%d')
		sel = [func.min(Measurement.tobs), 
       		   func.max(Measurement.tobs), 
       		   func.avg(Measurement.tobs)]

		results = session.query(*sel).filter(Measurement.date == start,Measurement.prcp !=None).all()

		#start_trip = list(np.ravel(results))
		#return jsonify(start_trip)

		# Print the html
		return (
			f"<a href=/welcome> Back to Main Page</a><br><br>"
			f"On <b>{start}</b>:<br><br><br>"
			f"Minimum Temperature was {results[0][0]}<br>"
			f"Maximum Temperature was {results[0][1]}<br>"
			f"Average Temperature was {results[0][2]}<br>"
			)
	except ValueError:
		return (
			f"<a href=/welcome> Back to Main Page</a><br><br>"
			f"Please enter Start Date in YYYY-MM-DD format.<br>")

# def greater_start_date(start_date):

# 	start_trip_date_temps = []
# 	sel = [func.min(Measurement.tobs), 
#        func.max(Measurement.tobs), 
#        func.avg(Measurement.tobs)]
	
# 	results = session.query(*sel).filter(Measurement.date >= start_date,Measurement.prcp !=None).all()
# 	start_trip_date_temps = list(np.ravel(results))

# 	return jsonify(start_trip_date_temps)

@app.route("/api/<start>/<end>")
def startendtrip(start, end):
	try:
		datetime.datetime.strptime(start, '%Y-%m-%d')
		datetime.datetime.strptime(end, '%Y-%m-%d')
		#round_trip_temps = []
		sel = 	[func.min(Measurement.tobs), 
       			func.max(Measurement.tobs), 
       			func.avg(Measurement.tobs)]
	
		results = session.query(*sel).filter(Measurement.date >= start, Measurement.date <= end,Measurement.prcp !=None).all()
		#round_trip_temps = list(np.ravel(results))
		#return jsonify(round_trip_temps)
		# Print the html
		return (
			f"<a href=/welcome> Back to Main Page</a><br><br>"
			f"Between <b>{start}</b> and <b>{end}</b>:<br><br><br>"
			f"Minimum Temperature was {results[0][0]}<br>"
			f"Maximum Temperature was {results[0][1]}<br>"
			f"Average Temperature was {results[0][2]}<br>"
			)
	except ValueError:
		return (
			f"<a href=/welcome> Back to Main Page</a><br><br>"
			f"Please enter Start Date and End Date in YYYY-MM-DD format.<br>")


class StationTable(Table):
	station = Col('Station')
	name = Col('Name')

class TemperatureTable(Table):
	date = Col('Date')
	tobs = Col('Temperature')

class RainTable(Table):
	date = Col('Date')
	prcp = Col('Precipitation')

if __name__ == '__main__':
    app.run(debug=True)