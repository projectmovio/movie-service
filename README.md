# Requirements

* python3.7
* pip install -r requirements.txt

# Start server

* Set `MOVIE_SERVICE_API_KEY` env variable
* python run_flask.py
* API base URL: `http://localhost:8082/`

# Formatting

* pip install yapf
* yapf -r -i -vv service/ run_flask.py

# Running in docker

* Set `MOVIE_SERVICE_API_KEY` env variable
* docker build -t movie-service:1.0 .
* docker run -e MOVIE_SERVICE_API_KEY -p 8082:8082 -d -t movie-service:1.0

