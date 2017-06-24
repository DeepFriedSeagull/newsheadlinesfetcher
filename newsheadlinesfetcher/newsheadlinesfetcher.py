from newsheadlinesfetcher import app

import time
import atexit
import os

from datetime import datetime
from urllib.parse import urlparse
from flask import Flask, render_template, flash, redirect, request, send_from_directory

from pymongo import MongoClient

import newsheadlinesfetcher.newsheadlines_livefetcher
import newsheadlinesfetcher.generate_cloud_image

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger


# 1- Setting up routes 
# 2- Setting up Tools routes
# 3- Setting up main scheduller

mongo_client = MongoClient()
db = mongo_client.livefetch


@app.route('/')
def main():
	# images = db.articlesCollection.find({}, {"title":1, "_id":1, "local_thumbnail":1, "url":1} ).sort("_id", -1)
	# newspapers = db.newspapersCollection.find({}, {"name":1, "_id":0, "url":1} ) 
	# acticles_number = db.articlesCollection.count();
	# political_articles = len( newsheadlinesfetcher.generate_cloud_image.fetch_filtered_titles_from_db() )
	# acticles_number=acticles_number, political_articles=political_articles  

	newspapers = db.newspapersCollection.find({}, {"name":1, "_id":0, "url":1} ) 
	next_start_date = datetime.now().isoformat()	
	return render_template('main.html', next_start_date=next_start_date, newspapers=newspapers )


@app.route('/newspaper/<newspaper>')
def newspaper(newspaper):
	# images = db.articlesCollection.find({"origin":newspaper}, 
	# 	{"local_thumbnail":1, "_id":0, "url":1, "title":1 } ).sort("_id", -1)

	next_start_date = datetime.now().isoformat()
	newspapers = db.newspapersCollection.find({}, {"name":1, "_id":0, "url":1} ) 
	
	return render_template('newspaper.html', newspaper_name=newspaper, newspapers=newspapers,
		next_start_date=next_start_date, newspaper_filter=newspaper )


# TODO Update with pagging 
# # http://127.0.0.1:5000/2017/03/22
# @app.route('/<int:year>/')
# @app.route('/<int:year>/<int:month>')
# @app.route('/<int:year>/<int:month>/<int:day>')
# def per_date(year,month=-1,day=-1):
# 	if month == -1:
# 		selected_date = datetime(year, 1, 1)
# 		the_day_after = selected_date + datetime.timedelta(years=1)
# 	elif day == -1:
# 		selected_date = datetime(year, month, 1)
# 		the_day_after = selected_date + datetime.timedelta(months=1)
# 	else:
# 		selected_date = datetime(year, month, day)
# 		the_day_after = selected_date + datetime.timedelta(days=1)

# 	images = db.articlesCollection.find(
# 		{"time_of_insert_iso":
# 			{"$gte": selected_date.isoformat(), "$lt":the_day_after.isoformat()}},
# 		{"top_image":1, "_id":0, "url":1, "title":1 } ).sort("_id", -1)
# 	return render_template('main.html', images=images)
	

"""Principal Route
Db request is done here
Agrs:
# Count: Number of ruturned images
# StartDate: Date that the article should be prior or egal to
# newspaper_filter: Name of the newspaper we are interrested in
"""
@app.route('/articles')
def articles():
	count = request.args.get('Count')
	start_date = request.args.get('StartDate')
	newspaper_filter = request.args.get('newspaper_filter')

	if count is None:
		count = 80
	else:
		count = int(count)

	if start_date is None:
		raise Exception("Invalid StartDate")

	qd_request = {"time_of_insert_iso": {"$lt":start_date} }

	if (newspaper_filter):
		qd_request.update({"origin":newspaper_filter})

	images = list ( db.articlesCollection.find(
			qd_request,
			{"title":1, "_id":1, "local_thumbnail":1, "url":1, "time_of_insert_iso":1} ).sort("_id", -1).limit(count) )
	
	# next_start_date is based on last retrieve image, as it is sorted by date
	next_start_date = ""
	if (len(images) > 0 ):
		next_start_date = images[-1]["time_of_insert_iso"]
	
	return render_template('gallery_images.html', images=images,
		start_date=start_date , next_start_date=next_start_date)


# Tools routes 
@app.route('/run')
def run():
	newsheadlines_livefetcher.Website_Fecther.main_exec()
	return redirect('/',302,None)

# http://localhost:5000/run/fetch_image?param=http://next.liberation.fr/culture-next/2017/04/06/et-si-les-ados-osaient-la-politique_1556995
# http://localhost:5000/run/fetch_image?param=https://www.mediapart.fr/journal/international/290317/brexit-les-grands-travaux-ne-font-que-commencer
@app.route('/run/<command>')
def run2(command):
	param=request.args.get('param')
	print( param )
	if param is not None:
		result = getattr(newsheadlinesfetcher.newsheadlines_livefetcher,command)(param)
	else:
		result = getattr(newsheadlinesfetcher.newsheadlines_livefetcher,command)()
	return redirect('/',302,None)

# http://localhost:5000/log/flask.log
@app.route('/log/<name>')
def log(name):
	return send_from_directory( app.config["LOG_FOLDER"], name, mimetype='text/txt' )


def fetch_start():
	print(time.strftime("Starting Fetching: %A, %d. %B %Y %I:%M:%S %p"))
	newsheadlinesfetcher.newsheadlines_livefetcher.Website_Fecther.main_exec()
	print(time.strftime("Finishing Fetching: %A, %d. %B %Y %I:%M:%S %p"))


# # Setting our scheduler
# scheduler = BackgroundScheduler()
# scheduler.start()
# scheduler.add_job(
# 	func=fetch_start,
# 	trigger=IntervalTrigger(minutes=10),
# 	id='livefetch_job',
# 	name='Fetching latest headlines',
# 	replace_existing=True)

# # Shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())