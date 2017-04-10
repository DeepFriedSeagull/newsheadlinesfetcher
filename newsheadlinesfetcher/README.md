# News Headlines Fetcher

## Installation on Ubuntu / Linux

### Install MongoDB
* Follow the step [here](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu)

### Install Python3 / virtualenv / pip
pip is already installed if you're using Python 2 >=2.7.9 or Python 3 >=3.4 
* `python3 --version` *to check the version of python3 your have
* `pip install -U pip` *to update pip [link](https://pip.pypa.io/en/stable/installing/#upgrading-pip)*
*  pip install virtualenv *to install virtualenv[link](https://virtualenv.pypa.io/en/stable/installation/)* 

### Setup Virtual Environment called "dev"
* `virtualenv -p python3 dev` *this will create our dev environement*
* `source dev/bin/activate` *this will activate it*
* `pip install -r requirements.txt` *this will install required python libraries*
* `python download_corpora.py` *this is for NLP*
* `mkdir static/images_db` *this is were we will store our images*

### Start Server
* `./start_server.sh`


# Installation on Windows
* `virtualenv dev`
* `dev\Scripts\activate.bat`
* `pip install -r requirements.txt` *this will install required python libraries*
* `python download_corpora.py` *this is for NLP*
* `mkdir static/images_db` *this is were we will store our images*
