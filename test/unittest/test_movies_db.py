import pytest


def test_get_movie_by_tmdb_id_not_found(mocked_movies_db):
    mocked_movies_db.table.query.return_value = {
        "Items": []
    }

    with pytest.raises(mocked_movies_db.NotFoundError):
        mocked_movies_db.get_movie_by_api_id("tmdb", "123")


def test_get_movie_by_id_not_found(mocked_movies_db):
    mocked_movies_db.table.get_item.return_value = {
        "Items": []
    }

    with pytest.raises(mocked_movies_db.NotFoundError):
        mocked_movies_db.get_movie_by_id("123")