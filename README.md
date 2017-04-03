# News Headlines Fetcher

## Installation on Ubuntu / Linux

### Install MongoDB
* Follow the step [here](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu)

### Install Python3 / virtualenv
* `python3 --version`

### Setup Virtual Environment called "dev"
* `virtualenv -p python3 dev` *this will create our dev environement*
* `source dev/bin/activate` *this will activate it*
* `pip install -r requirements.txt` *this will install required python libraries*
* `python download_corpora.py` *this is for NLP*
* `mkdir static/images_db` *this is were we will store our images*

### Start Server
* `./start_server.sh`