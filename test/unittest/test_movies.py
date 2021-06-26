import json
import pytest

from api.movies import handle, UnsupportedMethod


def test_post_movies(mocked_movies_db):
    mocked_movies_db.table.query.side_effect = mocked_movies_db.NotFoundError
    event = {
        "requestContext": {
            "http": {
                "method": "POST"
            }
        },
        "body": '{"api_id": "123", "api_name": "tmdb"}'
    }

    res = handle(event, None)

    exp = {
        "body": json.dumps({"id": "e6d4fa11-1ad7-5137-a962-9554c8766356"}),
        "statusCode": 200
    }
    assert res == exp


def test_post_movies_already_exist(mocked_movies_db):
    mocked_movies_db.table.query.return_value = {
        "Items": [
            {
                "tmdb_id": "123"
            }
        ]
    }
    event = {
        "requestContext": {
            "http": {
                "method": "POST"
            }
        },
        "body": '{"api_id": "123", "api_name": "tmdb"}'
    }

    res = handle(event, None)

    exp = {
        "body": json.dumps({"id": "e6d4fa11-1ad7-5137-a962-9554c8766356"}),
        "statusCode": 200
    }
    assert res == exp


def test_post_movies_no_body(mocked_movies_db):
    mocked_movies_db.table.query.return_value = {
        "Items": [
            {
                "tmdb_id": "123"
            }
        ]
    }
    event = {
        "requestContext": {
            "http": {
                "method": "POST"
            }
        },
    }

    res = handle(event, None)

    exp = {
        "statusCode": 400,
        "body": "Invalid post body"
    }
    assert res == exp


def test_post_movies_invalid_body(mocked_movies_db):
    mocked_movies_db.table.query.return_value = {
        "Items": [
            {
                "mal_id": 123
            }
        ]
    }
    event = {
        "requestContext": {
            "http": {
                "method": "POST"
            }
        },
        "body": '{"aa": "bb"}'
    }

    res = handle(event, None)

    exp = {
        'body': '{"message": "Invalid post schema", '
                '"error": "Additional properties are not allowed (\'aa\' was unexpected)"}',
        'statusCode': 400
    }
    assert res == exp


def test_unsupported_method():
    event = {
        "requestContext": {
            "http": {
                "method": "AA"
            }
        },
        "queryStringParameters": {
            "mal_id": "123"
        }
    }

    with pytest.raises(UnsupportedMethod):
        handle(event, None)


def test_get_by_api_id(mocked_movies_db):
    exp_res = {
        "id": "123"
    }
    mocked_movies_db.table.query.return_value = {
        "Items": [
            exp_res
        ]
    }
    event = {
        "requestContext": {
            "http": {
                "method": "GET"
            }
        },
        "queryStringParameters": {
            "api_id": "123",
            "api_name": "tmdb",
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 200,
        "body": json.dumps(exp_res)
    }
    assert res == exp


def test_get_by_api_id_not_found(mocked_movies_db):
    mocked_movies_db.table.query.side_effect = mocked_movies_db.NotFoundError
    event = {
        "requestContext": {
            "http": {
                "method": "GET"
            }
        },
        "queryStringParameters": {
            "api_id": "123",
            "api_name": "tmdb"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 404,
    }
    assert res == exp


def test_get_no_query_params():
    event = {
        "requestContext": {
            "http": {
                "method": "GET"
            }
        },
        "queryStringParameters": {
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 400,
        "body": json.dumps({"error": "Please specify query parameters"})
    }
    assert res == exp


def test_get_invalid_query_params():
    event = {
        "requestContext": {
            "http": {
                "method": "GET"
            }
        },
        "queryStringParameters": {
            "abc": "123"
        }
    }

    res = handle(event, None)

    exp = {
        "statusCode": 400,
        "body": json.dumps({"error": "Missing api_id query parameter"})
    }
    assert res == exp
