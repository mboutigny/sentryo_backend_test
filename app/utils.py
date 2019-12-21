import json
from app import app
import sqlite3
from enum import Enum


class ConveyanceType(Enum):
    VEHICLES = "vehicles"
    STARSHIPS = "starships"


def database_connect():
    """
    Open the database connection

    Returns:
        (tuple):
            (Connector): the database connector
            (Cursor): the database cursor
    """
    try:
        connector = sqlite3.connect("data/swapi.dat")
        connector.row_factory = sqlite3.Row
        cursor = connector.cursor()
    except Exception as e:
        raise Exception("An error occurred while opening the database : %s" % e)

    return connector, cursor


def database_commit(connector):
    """
    Commit the modifications into the database

    Args:
        (Connector): the database connector
    """
    try:
        connector.commit()
    except Exception as e:
        raise Exception(
            "An error occurred while committing the modifications in the database: %s"
            % e
        )


def database_disconnect(connector, cursor):
    """
    Close the database connection

    Args:
        (Connector): the database connector
        (Cursor): the database cursor
    """
    try:
        cursor.close()
        connector.close()
    except Exception as e:
        raise Exception("An error occurred while closing the database : %s" % e)


def create_json_response(data):
    response = app.response_class(
        response=json.dumps(data, ensure_ascii=False),
        status=200,
        mimetype="application/json",
    )

    return response
