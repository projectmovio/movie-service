from base_api import BaseApi
from utils.log import Log

log = Log().get_logger(__name__)


class TmdbApi(BaseApi):

    def __init__(self):
        super(TmdbApi, self).__init__()
        self.config = self.config["tmdb"]
        self.headers = {"Authorization": self.config["user_token"]}
        self.config["configuration"] = self.configuration()
        log.debug("TMDB image base_url: {}".format(
            self.config["configuration"]["images"]["base_url"]))

    def configuration(self):
        return self._send_request("GET", "/configuration", 200, get_data=True)


