#!/bin/bash
nohup mongod --dbpath="/root/work/mongodb" &
export FLASK_APP=newsheadlinesfetcher.py
export FLASK_DEBUG=1
source dev/bin/activate ; nohup python -m flask run &