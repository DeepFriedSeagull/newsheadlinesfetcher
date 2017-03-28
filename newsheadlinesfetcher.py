import time
import atexit
import datetime
import os

from urllib.parse import urlparse
from flask import Flask, render_template, flash, redirect
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

app = Flask(__name__)
app.config["MONGO_DBNAME"]="livefetch"
mongo = PyMongo(app)


@app.route('/newspaper/<newspaper>')
def newspaper(newspaper):
	images = mongo.db.articlesCollection.find({"origin":newspaper}, 
		{"top_image":1, "_id":0, "url":1, "title":1 } ).sort("_id", -1)
	return render_template('main.html', images=images)

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


@app.route('/')
def main():
	# flash('Testing FLASH FLASK')	
	images = mongo.db.articlesCollection.find({}, {"top_image":1, "_id":1, "local_top_image":1, "url":1} ).sort("_id", -1)

	return render_template('main.html', images=images)


def fetch_start():
	print(time.strftime("Starting Fetching: %A, %d. %B %Y %I:%M:%S %p"))
	livefetch.main_exec()
	print(time.strftime("Finishing Fetching: %A, %d. %B %Y %I:%M:%S %p"))
	

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


