import os
from unittest.mock import MagicMock
import pytest

os.environ["LOG_LEVEL"] = "DEBUG"


@pytest.fixture(scope='function')
def mocked_movies_db():
    import movies_db

    movies_db.table = MagicMock()
    movies_db.client = MagicMock()

    return movies_db
