from flask import jsonify

from base_api import BaseApi
from utils.log import Log

log = Log().get_logger(__name__)


class TmdbApi(BaseApi):
    def __init__(self):
        super(TmdbApi, self).__init__()
        self.headers = {"Authorization": self.config["user_token"]}
        self.config["configuration"] = self.configuration()
        log.debug("TMDB image base_url: {}".format(
            self.config["configuration"]["images"]["base_url"]))

    def configuration(self):
        return self._get("/configuration")

    def search(self, movie_name):
        return jsonify(self._get("/search/movie", {"query": movie_name}))

    def get_movies(self):
        result = []
        movies1 = self._get("/discover/movie?sort_by=popularity.desc",
                            {"page": 1})
        movies2 = self._get("/discover/movie?sort_by=popularity.desc",
                            {"page": 2})
        movies3 = self._get("/discover/movie?sort_by=popularity.desc",
                            {"page": 3})

        result.extend(movies1['results']).extend(
            movies2['results'].extend(movies3['results']))

        return jsonify(movies=result)
