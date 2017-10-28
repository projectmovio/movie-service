from flask import Flask

from api.tmdb import TmdbApi

app = Flask(__name__)
tmdb_api = TmdbApi()

@app.route("/")
def hello():
    return "Hello World!"
