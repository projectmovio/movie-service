import logging
import os

log = logging.getLogger(__name__)


class Config(object):
    def __init__(self):
        self.base_url = "https://api.themoviedb.org/3"
        self.api_key = ""
        self._read_config()

    def _read_config(self):
        api_key_env = os.getenv("MOVIE_SERVICE_API_KEY")
        if api_key_env is None:
            raise RuntimeError("Please set MOVIE_SERVICE_API_KEY environment variable")
        self.api_key = api_key_env

