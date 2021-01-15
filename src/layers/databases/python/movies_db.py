import os
import uuid

import boto3
from boto3.dynamodb.conditions import Key

import logger

DATABASE_NAME = os.getenv("MOVIES_DATABASE_NAME")
MOVIE_UUID_NAMESPACE = uuid.UUID("9c5bbb4a-5fef-4d16-917b-537421aabfa6")

table = None
client = None

log = logger.get_logger(__name__)


class Error(Exception):
    pass


class NotFoundError(Error):
    pass


def _get_table():
    global table
    if table is None:
        table = boto3.resource("dynamodb").Table(DATABASE_NAME)
    return table


def _get_client():
    global client
    if client is None:
        client = boto3.client("dynamodb")
    return client


def new_movie(api_name, api_id):
    movie_id = create_movie_uuid(api_name, str(api_id))
    update_movie(movie_id, {f"{api_name}_id": api_id})

    return movie_id


def create_movie_uuid(api_name, api_id):
    api_uuid = uuid.uuid5(MOVIE_UUID_NAMESPACE, api_name)
    item_uuid = str(uuid.uuid5(api_uuid, api_id))
    return item_uuid


def update_movie(movie_id, data):
    items = ','.join(f'#{k}=:{k}' for k in data)
    update_expression = f"SET {items}"
    expression_attribute_names = {f'#{k}': k for k in data}
    expression_attribute_values = {f':{k}': v for k, v in data.items()}

    log.debug("Running update_item")
    log.debug(f"Update expression: {update_expression}")
    log.debug(f"Expression attribute names: {expression_attribute_names}")
    log.debug(f"Expression attribute values: {expression_attribute_values}")

    _get_table().update_item(
        Key={"id": movie_id},
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values
    )


def get_movie_by_id(movie_id):
    res = _get_table().get_item(Key={"id": movie_id})

    if "Item" not in res:
        raise NotFoundError(f"Movie with id: {movie_id} not found")

    return res["Item"]


def get_movie_by_api_id(api_name, api_id):
    key_name = f"{api_name}_id"
    res = _get_table().query(
        IndexName=key_name,
        KeyConditionExpression=Key(key_name).eq(api_id)
    )
    log.debug(f"get_movie_by_id res: {res}")

    if not res["Items"]:
        raise NotFoundError(f"Movie with {key_name}: {api_id} not found")

    return res["Items"][0]
