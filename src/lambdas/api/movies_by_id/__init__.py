import json

import movies_db
import decimal_encoder
import logger

log = logger.get_logger("movies_by_id")


class HttpError(object):
    pass


def handle(event, context):
    log.debug(f"Received event: {event}")

    movie_id = event["pathParameters"].get("id")

    try:
        res = movies_db.get_movie_by_id(movie_id)
    except movies_db.NotFoundError:
        return {"statusCode": 404}

    return {
        "statusCode": 200,
        "body": json.dumps(res, cls=decimal_encoder.DecimalEncoder)
    }
