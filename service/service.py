from api.tmdb import TmdbApi
from utils.log import Log

log = Log().get_logger(__name__)


class Service(object):

    def __init__(self):
        self.tmdb_api = TmdbApi()


