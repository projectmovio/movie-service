import logging
from urllib.parse import urlencode
import requests
from flask import jsonify

from service.utils.config import Config

log = logging.getLogger(__name__)


class TmdbApi:
    def __init__(self):
        self.config = Config()

        self.configuration = self.configuration()
        print(self.configuration)
        log.debug("TMDB image base_url: {}".format(self.configuration["images"]["base_url"]))

    def configuration(self):
        return self._get("/configuration")

    def search(self, movie_name):
        return jsonify(self._get("/search/movie", {"query": movie_name}))

    def get_movies(self):
        result = []
        movies1 = self._get("/discover/movie", {"sort_by": "popularity.desc", "page": 1})
        movies2 = self._get("/discover/movie", {"sort_by": "popularity.desc", "page": 2})
        movies3 = self._get("/discover/movie", {"sort_by": "popularity.desc", "page": 3})

        result.extend(movies1["results"])
        result.extend(movies2["results"])
        result.extend(movies3["results"])

        return jsonify(movies=result)

    def _post(self, route, url_params={}):
        url_params["api_key"] = self.config.api_key
        url = "{}{}?{}".format(self.config.base_url, route, urlencode(url_params))

        log.debug("Sending post request to URL: {}".format(url))

        requests.post(url)

    def _get(self, route, url_params={}):
        url_params["api_key"] = self.config.api_key
        url = "{}{}?{}".format(self.config.base_url, route, urlencode(url_params))

        log.debug("Sending post request to URL: {}".format(url))

        return requests.get(url).json()
