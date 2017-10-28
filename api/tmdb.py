import requests

from utils.config import Config
from utils.log import Log

log = Log().get_logger(__name__)


class TmdbApi:
    def __init__(self):
        self.config = Config().cfg["api"]["tmdb"]
        self.headers = {"Authorization": self.config["user_token"]}
        self.config["configuration"] = self.configuration()
        log.debug("TMDB configuration: {}".format(self.config["configuration"]))

    def configuration(self):
        return self._send_request("GET", "/configuration", 200, get_data=True)

    # TODO: Move to common api class?
    def _send_request(self, method, route, status_code, get_data=False):
        url = "{}{}?api_key={}".format(self.config["base_url"], route,
                                       self.config["key"])

        log.debug("Sending {} request to URL: {}".format(method, url))
        response = requests.request(method, url)
        if response.status_code != status_code:
            raise RuntimeError("Wrong return code: {} (expected: {})".format(
                response.status_code, status_code))

        if get_data:
            if response and response.json():
                return response.json()
        return response
