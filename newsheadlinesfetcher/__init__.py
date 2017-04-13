from flask import Flask


app = Flask(__name__,static_folder='static',static_path='')
app.config["MONGO_DBNAME"]="livefetch"
app.config["LOG_FOLDER"]='../logs'
app.secret_key = 'dZjBgu6vwAH5z16q1DygCSsvPbsPzqL89GNY7Oyj7e3vyg4ORrhoxiq6AJhtjKJ9'


import newsheadlinesfetcher.newsheadlinesfetcher
