import json
import os
from json import JSONDecodeError

import decimal_encoder
import logger
import schema
import movies_db

sqs_queue = None

log = logger.get_logger("movies")

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
POST_SCHEMA_PATH = os.path.join(CURRENT_DIR, "post.json")


class Error(Exception):
    pass


class UnsupportedMethod(Error):
    pass


def handle(event, context):
    log.debug(f"Received event: {event}")

    method = event["requestContext"]["http"]["method"]

    if method == "POST":
        body = event.get("body")
        return _post_movie(body)
    elif method == "GET":
        query_params = event.get("queryStringParameters")
        return _get_movie_by_api_id(query_params)
    else:
        raise UnsupportedMethod()


def _post_movie(body):
    try:
        body = json.loads(body)
    except (TypeError, JSONDecodeError):
        log.debug(f"Invalid body: {body}")
        return {
            "statusCode": 400,
            "body": "Invalid post body"
        }

    try:
        schema.validate_schema(POST_SCHEMA_PATH, body)
    except schema.ValidationException as e:
        return {"statusCode": 400, "body": json.dumps({"message": "Invalid post schema", "error": str(e)})}

    if body["api_name"] == "tmdb":
        return _post_tmdb(body["api_id"])


def _post_tmdb(tmdb_id):
    try:
        movies_db.get_movie_by_api_id("tmdb", int(tmdb_id))
    except movies_db.NotFoundError:
        pass
    else:
        return {
            "statusCode": 200,
            "body": json.dumps({"id": movies_db.create_movie_uuid("tmdb", tmdb_id)})
        }

    movies_db.new_movie("tmdb", int(tmdb_id))

    return {
        "statusCode": 200,
        "body": json.dumps({"id": movies_db.create_movie_uuid("tmdb", tmdb_id)})
    }


def _get_movie_by_api_id(query_params):
    if not query_params:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Please specify query parameters"})
        }

    if "tmdb_id" in query_params:
        try:
            res = movies_db.get_movie_by_api_id("tmdb", int(query_params["tmdb_id"]))
            return {"statusCode": 200, "body": json.dumps(res, cls=decimal_encoder.DecimalEncoder)}
        except movies_db.NotFoundError:
            return {"statusCode": 404}
    else:
        return {"statusCode": 400, "body": json.dumps({"error": "Unsupported query param"})}
