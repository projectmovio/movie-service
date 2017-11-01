from urllib import urlencode

import requests

from utils.config import Config
from utils.log import Log

log = Log().get_logger(__name__)


class BaseApi(object):
    def __init__(self):
        self.api_key = Config().cfg["api"]["key"]
        self.base_url = Config().cfg["base_url"]
        self.headers = {}

    def _post(self, route, url_params={}):
        url = "{}{}?{}".format(self.base_url, route, urlencode(url_params))

        log.debug("Sending post request to URL: {}. headers: {}"
                  .format(url, self.headers))

        requests.post(url, headers=self.headers)

    def _get(self, route, url_params={}):
        url = "{}{}?{}".format(self.base_url, route, urlencode(url_params))

        log.debug("Sending post request to URL: {}. headers: {}"
                  .format(url, self.headers))

        return requests.get(url, headers=self.headers).json()
