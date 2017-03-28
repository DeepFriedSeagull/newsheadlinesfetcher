#!/bin/bash
mongod --dbpath="/root/work/mongodb" &
export FLASK_APP=newsheadlinesfetcher.py
export FLASK_DEBUG=1
source dev/bin/activate.bat | python -m flask run 