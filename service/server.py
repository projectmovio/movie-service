import requests
from flasgger import swag_from, Swagger
from flask import Flask, request, jsonify
from api.tmdb import TmdbApi

app = Flask(__name__)
Swagger(app, template_file='swagger/template.yml')

tmdb_api = TmdbApi()


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/movies", methods=["get"])
@swag_from("swagger/movies.yml")
def movies():
    if "search" in requests.args:
        search = request.args.get("search")
        return tmdb_api.search(search)
    else:
        return tmdb_api.get_movies()
