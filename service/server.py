import logging

from api.tmdb import TmdbApi
from flask import Flask, request

log = logging.getLogger("service")
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.getLogger("urllib3").setLevel("WARNING")

app = Flask(__name__)

tmdb_api = TmdbApi()


@app.route("/movies", methods=["get"])
def movies():
    log.debug("Headers: %s", request.headers)
    if "search" in request.args:
        search = request.args.get("search")
        return tmdb_api.search(search)
    else:
        return tmdb_api.get_movies()
