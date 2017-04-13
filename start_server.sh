#!/bin/bash
current_time=$(date -u +"%Y-%m-%dT%H-%M-%SZ")
ln -sf mongod.log.$current_time logs/mongod.log
ln -sf flask.log.$current_time logs/flask.log
nohup mongod --config ./mongod.conf --logpath logs/mongod.log.$current_time </dev/null >/dev/null 2>&1 &
export FLASK_APP=newsheadlinesfetcher
#export FLASK_DEBUG=1
source dev/bin/activate ; pip install -e . ; nohup flask run >logs/flask.log.$current_time 2>&1 &
