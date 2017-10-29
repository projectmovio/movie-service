from flasgger import swag_from, Swagger
from flask import Flask, request, jsonify
from api.tmdb import TmdbApi

app = Flask(__name__)
swagger_template = {
  "swagger": "2.0",
  "info": {
    "title": "Movio movie service api",
    "description": "API to get and update movie information",
    "contact": {
      "responsibleOrganization": "Michal Sadowski",
      "responsibleDeveloper": "Michal Sadowski",
      "email": "michcio90po@gmail.com",
      "url": "test",
    },
    "termsOfService": "test",
    "version": "0.0.0"
  },
  "host": "localhost:5000",  # overrides localhost:5000
  "basePath": "/api",  # base bash for blueprint registration
  "schemes": [
    "http",
    "https"
  ]
}
Swagger(app, template=swagger_template)

tmdb_api = TmdbApi()


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/movies", methods=["get"])
@swag_from("swagger/movies.yml")
def movies():
    search = request.args.get("search")
    return jsonify(tmdb_api.search(search))
