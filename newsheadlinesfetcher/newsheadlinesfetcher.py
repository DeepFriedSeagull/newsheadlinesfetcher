from newsheadlinesfetcher import app

import time
import atexit
import os

from datetime import datetime
from urllib.parse import urlparse
from flask import Flask, render_template, flash, redirect, request, send_from_directory

# from flask.ext.pymongo import PyMongo
# from flask_pymongo import Pymongo
from pymongo import MongoClient

import newsheadlinesfetcher.livefetch
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

import newsheadlinesfetcher.generate_cloud_image


# mongo = PyMongo(app)
mongo_client = MongoClient()
db = mongo_client.livefetch

@app.route('/log/<name>')
def log(name):
	return send_from_directory( app.config["LOG_FOLDER"], name, mimetype='text/txt' )


@app.route('/newspaper/<newspaper>')
def newspaper(newspaper):
	images = db.articlesCollection.find({"origin":newspaper}, 
		{"local_thumbnail":1, "_id":0, "url":1, "title":1 } ).sort("_id", -1)
	return render_template('newspaper.html', images=images, newspaper_name=newspaper)

# http://127.0.0.1:5000/2017/03/22
@app.route('/<int:year>/')
@app.route('/<int:year>/<int:month>')
@app.route('/<int:year>/<int:month>/<int:day>')
def per_date(year,month=-1,day=-1):
	if month == -1:
		selected_date = datetime(year, 1, 1)
		the_day_after = selected_date + datetime.timedelta(years=1)
	elif day == -1:
		selected_date = datetime(year, month, 1)
		the_day_after = selected_date + datetime.timedelta(months=1)
	else:
		selected_date = datetime(year, month, day)
		the_day_after = selected_date + datetime.timedelta(days=1)

	images = db.articlesCollection.find(
		{"time_of_insert_iso":
			# {"$gte": "2017-03-21T15:35:49.299462"}},
			{"$gte": selected_date.isoformat(), "$lt":the_day_after.isoformat()}},
		{"top_image":1, "_id":0, "url":1, "title":1 } ).sort("_id", -1)
	return render_template('main.html', images=images)
	

@app.route('/run')
def run():
	livefetch.main_exec()
	return redirect('/',302,None)

# http://localhost:5000/run/fetch_image?param=https://www.mediapart.fr/journal/international/290317/brexit-les-grands-travaux-ne-font-que-commencer
@app.route('/run/<command>')
def run2(command):
	param=request.args.get('param')
	print( param )
	if param is not None:
		result = getattr(livefetch,command)(param)
	else:
		result = getattr(livefetch,command)()

	return redirect('/',302,None)

@app.route('/articles')
def articles():
	count = request.args.get('Count')

	start_date = request.args.get('StartDate')
	if count is None:
		count = 80
	else:
		count = int(count)

	if start_date is None:
		raise Exception("Invalid StartDate")
	images = list ( db.articlesCollection.find(
			{"time_of_insert_iso": {"$lt":start_date} },
			{"title":1, "_id":1, "local_thumbnail":1, "url":1, "time_of_insert_iso":1} ).sort("_id", -1).limit(count) )
	
	# print (  images[-1]["time_of_insert_iso"] )

	next_start_date = ""
	if (len(images) > 0 ):
		next_start_date = images[-1]["time_of_insert_iso"]

	newspapers = db.newspapersCollection.find({}, {"name":1, "_id":0, "url":1} ) 
	
	return render_template('gallery_images.html', images=images, newspapers=newspapers, start_date=start_date , next_start_date=next_start_date  )

@app.route('/')
def main():
	flash('Testing FLASH FLASK')	


	images = db.articlesCollection.find({}, {"title":1, "_id":1, "local_thumbnail":1, "url":1} ).sort("_id", -1)
	newspapers = db.newspapersCollection.find({}, {"name":1, "_id":0, "url":1} ) 
	next_start_date = datetime.now().isoformat()
	acticles_number = db.articlesCollection.count();
	

	political_articles = len( newsheadlinesfetcher.generate_cloud_image.fetch_filtered_titles_from_db() )
	
	return render_template('main.html', images=images, newspapers=newspapers, 
		next_start_date=next_start_date, acticles_number=acticles_number, political_articles=political_articles )

def fetch_start():
	print(time.strftime("Starting Fetching: %A, %d. %B %Y %I:%M:%S %p"))
	newsheadlinesfetcher.livefetch.main_exec()
	print(time.strftime("Finishing Fetching: %A, %d. %B %Y %I:%M:%S %p"))
	# flash( time.strftime("Last Update: %I:%M:%S"))
	

scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
	func=fetch_start,
	trigger=IntervalTrigger(minutes=10),
	id='livefetch_job',
	name='Fetching latest headlines',
	replace_existing=True)

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


