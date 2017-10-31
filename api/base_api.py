from urllib import urlencode

import requests

from utils.config import Config
from utils.log import Log

log = Log().get_logger(__name__)


class BaseApi(object):
    def __init__(self):
        self.config = Config().cfg["api"]
        self.headers = {}

    def _send_request(self, method, route, url_params={}, get_data=False):
        url_params["api_key"] = self.config["key"]
        url = "{}{}?{}".format(self.config["base_url"], route,
                               urlencode(url_params))

        log.debug(
            "Sending {} request to URL: {}. headers: {}".format(method, url,
                                                                self.headers))
        response = requests.request(method, url, headers=self.headers)

        if get_data:
            if response and response.json():
                return response.json()
        return response
