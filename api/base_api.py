import requests

from utils.config import Config
from utils.log import Log

log = Log().get_logger(__name__)


class BaseApi(object):

    def __init__(self):
        self.config = Config().cfg["api"]
        self.headers = {}

    def _send_request(self, method, route, status_code, get_data=False):

        url = "{}{}?api_key={}".format(self.config["base_url"], route,
                                       self.config["key"])

        log.debug(
            "Sending {} request to URL: {}. headers: {}".format(method, url,
                                                                self.headers))
        response = requests.request(method, url, headers=self.headers)
        if response.status_code != status_code:
            raise RuntimeError("Wrong return code: {} (expected: {})".format(
                response.status_code, status_code))

        if get_data:
            if response and response.json():
                return response.json()
        return response