#!/bin/bash
mongod --dbpath="/root/work/mongodb" &
export FLASK_APP=newsheadlinesfetcher.py
export FLASK_DEBUG=1
source dev/bin/activate | python -m flask run 