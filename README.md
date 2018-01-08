# Requirements

* python2.7
* pip install -r requirements.txt

# Start server

* python run_flask.py
* API base URL: `http://localhost:5000/`

For more info check the `run_flask.py -h` section

# API docs

For api docs go to http://localhost:5000/apidocs

# Formatting

* pip install yapf
* yapf -r -i -vv service/ run_flask.py

# Running in docker

* docker build -t movie-service:1.0 .
* docker run -p 5000:5000 -d -t movie-service:1.0

