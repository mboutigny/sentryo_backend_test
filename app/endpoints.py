from flask import request

from app import app
from app.utils import database_connect, database_disconnect, create_json_response
from app.character_manager import CharacterManager


@app.route("/")
def ping():
    return "It's alive !"


@app.route("/characters", methods=["GET"])
@app.route("/characters/<int:character_id>", methods=["GET"])
def get_characters(character_id=None):
    """
    Get character(s) endpoint
    """
    connector, cursor = database_connect()
    character_manager = CharacterManager(connector, cursor)
    data = character_manager.get(character_id)
    database_disconnect(connector, cursor)
    return create_json_response(data)


@app.route("/characters", methods=["POST"])
def add_characters():
    """
    Add character endpoint
    """
    connector, cursor = database_connect()
    character_manager = CharacterManager(connector, cursor)
    data = character_manager.add(request.json)
    database_disconnect(connector, cursor)
    return create_json_response(data)


@app.route("/characters/<int:character_id>", methods=["PUT"])
def update_characters(character_id=None):
    """
    Update character endpoint
    """
    connector, cursor = database_connect()
    character_manager = CharacterManager(connector, cursor)
    data = character_manager.update(character_id, request.json)
    database_disconnect(connector, cursor)
    return create_json_response(data)


@app.route("/characters/<int:character_id>", methods=["DELETE"])
def delete_characters(character_id=None):
    """
    Delete character endpoint
    """
    connector, cursor = database_connect()
    character_manager = CharacterManager(connector, cursor)
    data = character_manager.delete(character_id)
    database_disconnect(connector, cursor)
    return create_json_response(data)
