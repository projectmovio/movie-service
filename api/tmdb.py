from urllib import urlencode

import requests
from flask import jsonify
from utils.log import Log
from utils.config import Config

log = Log().get_logger(__name__)


class TmdbApi:
    def __init__(self):
        self.config = Config().cfg["api"]["tmdb"]
        self.api_key = self.config["key"]
        self.base_url = self.config["base_url"]
        self.headers = {"Authorization": self.config["user_token"]}

        self.config["configuration"] = self.configuration()
        log.debug("TMDB image base_url: {}".format(self.config["configuration"]["images"]["base_url"]))

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
        url_params["api_key"] = self.api_key
        url = "{}{}?{}".format(self.base_url, route, urlencode(url_params))

        log.debug("Sending post request to URL: {}. headers: {}".format(url, self.headers))

        requests.post(url, headers=self.headers)

    def _get(self, route, url_params={}):
        url_params["api_key"] = self.api_key
        url = "{}{}?{}".format(self.base_url, route, urlencode(url_params))

        log.debug("Sending post request to URL: {}. headers: {}".format(url, self.headers))

        return requests.get(url, headers=self.headers).json()
