import time
import atexit
import datetime
import os

from urllib.parse import urlparse
from flask import Flask, render_template, flash, redirect, request, send_from_directory
from flask.ext.pymongo import PyMongo
import livefetch
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# from apscheduler.scheduler import Scheduler



# def test_scheduler():
# 	print (TEST)
# 	print (time.time())


# sched = Scheduler()
# sched.add_interval_job(test_scheduler, seconds=5)
# sched.start()


# from flask_pymongo import Pymongo

app = Flask(__name__,static_folder='static',static_path='')
app.config["MONGO_DBNAME"]="livefetch"
app.secret_key = 'dZjBgu6vwAH5z16q1DygCSsvPbsPzqL89GNY7Oyj7e3vyg4ORrhoxiq6AJhtjKJ9'
mongo = PyMongo(app)


@app.route('/log/<name>')
def log(name):
	return send_from_directory( '', name, mimetype='text/txt' )


@app.route('/newspaper/<newspaper>')
def newspaper(newspaper):
	images = mongo.db.articlesCollection.find({"origin":newspaper}, 
		{"local_thumbnail":1, "_id":0, "url":1, "title":1 } ).sort("_id", -1)
	return render_template('newspaper.html', images=images, newspaper_name=newspaper)

# http://127.0.0.1:5000/2017/03/22
@app.route('/<int:year>/')
@app.route('/<int:year>/<int:month>')
@app.route('/<int:year>/<int:month>/<int:day>')
def per_date(year,month=-1,day=-1):

	if month == -1:
		selected_date = datetime.datetime(year, 1, 1)
		the_day_after = selected_date + datetime.timedelta(years=1)
	elif day == -1:
		selected_date = datetime.datetime(year, month, 1)
		the_day_after = selected_date + datetime.timedelta(months=1)
	else:
		selected_date = datetime.datetime(year, month, day)
		the_day_after = selected_date + datetime.timedelta(days=1)

	images = mongo.db.articlesCollection.find(
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


@app.route('/')
def main():
	# flash('Testing FLASH FLASK')	
	images = mongo.db.articlesCollection.find({}, {"title":1, "_id":1, "local_thumbnail":1, "url":1} ).sort("_id", -1)
	newspapers = mongo.db.newspapersCollection.find({}, {"name":1, "_id":0, "url":1} ) 
	return render_template('main.html', images=images, newspapers=newspapers)


def fetch_start():
	print(time.strftime("Starting Fetching: %A, %d. %B %Y %I:%M:%S %p"))
	livefetch.main_exec()
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


