from flask import Flask, request, jsonify

from api.tmdb import TmdbApi

app = Flask(__name__)
tmdb_api = TmdbApi()


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/movies", methods=["get"])
def movies():
    search = request.args.get("search")
    return jsonify(tmdb_api.search(search))
