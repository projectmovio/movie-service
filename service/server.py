from api.tmdb import TmdbApi
from flasgger import swag_from, Swagger
from flask import Flask, request

app = Flask(__name__)
Swagger(app, template_file='swagger/template.yml')

tmdb_api = TmdbApi()


@app.route("/movies", methods=["get"])
@swag_from("swagger/movies.yml")
def movies():
    if "search" in request.args:
        search = request.args.get("search")
        return tmdb_api.search(search)
    else:
        return tmdb_api.get_movies()
