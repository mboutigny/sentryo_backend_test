from datetime import datetime

from app.utils import ConveyanceType, database_commit
from app.character_vehicles_and_starships_manager import (
    CharacterVehiclesAndStarshipsManager,
)

CHARACTER_KEYS = (
    "people.birth_year",
    "people.eye_color",
    "people.gender",
    "people.hair_color",
    "people.height",
    "people.homeworld",
    "people.mass",
    "people.name",
    "people.skin_color",
)

ADD_CHARACTER_KEYS = (
    "people.id",
    "people.url",
    "people.created",
)

UPDATE_CHARACTER_KEYS = ("people.edited",)


class CharacterManager:
    def __init__(self, connector, cursor):
        self.connector = connector
        self.cursor = cursor

    def get(self, character_id=None):
        """
        Get all the characters or a single one from it's id

        Args:
            character_id (str): the character's id (default is None)

        Returns:
            (list): a list of characters
        """
        where_clause = "WHERE people.id=?"
        sql = (
            "SELECT {1}, vehicles.id vehicles_id, vehicles.name vehicles_name, NULL starships_id, NULL starships_name "
            "FROM people "
            "LEFT JOIN people_vehicles ON (people.id=people_vehicles.people) "
            "LEFT JOIN vehicles ON vehicles.id = people_vehicles.vehicles "
            "{0} "
            "UNION "
            "SELECT {1}, NULL vehicles_id, NULL vehicles_names, starships.id starships_id, starships.name starships_name "
            "FROM people "
            "LEFT JOIN people_starships ON (people.id=people_starships.people) "
            "LEFT JOIN starships ON starships.id = people_starships.starships "
            "{0} ".format(
                where_clause if character_id else "",
                ", ".join(CHARACTER_KEYS + ADD_CHARACTER_KEYS + UPDATE_CHARACTER_KEYS),
            )
        )

        try:
            if character_id:
                query_result = self.cursor.execute(sql, [str(character_id), str(character_id)])
            else:
                query_result = self.cursor.execute(sql)
        except Exception as e:
            raise Exception(
                "An error occurred while querying the database. query: %s - message: %s"
                % (sql, e)
            )

        rows = query_result.fetchall()
        characters_dict = self._prettify_sqlite_response(rows)

        # Transform the dict of characters into a list of characters
        characters = []
        for (_, value) in characters_dict.items():
            characters.append(value)

        # Raise an error if there are no results.
        if not characters:
            raise Exception(
                "An error occurred. No character were found: ID: %s" % character_id
            )

        return characters

    def add(self, character_data):
        """
        Add a character

        Args:
            character_data (dict): the character's data to add

        Returns:
            (dict): the new character
        """
        # Generate auto-generated fields
        character_id = self._generate_new_user_id()
        url = character_id
        created = datetime.now().isoformat()

        # Only add the existing fields
        values = tuple(
            (character_data[key] if key in character_data.keys() else "NULL")
            for key in CHARACTER_KEYS
        )

        params_number = len((CHARACTER_KEYS + ADD_CHARACTER_KEYS))
        columns_name = ", ".join((CHARACTER_KEYS + ADD_CHARACTER_KEYS)).replace("people.", "")
        params = ", ".join(["?" for i in range(params_number)])
        sql = "INSERT INTO people ({}) VALUES ({})".format(columns_name, params)
        try:
            self.cursor.execute(sql, values + (character_id, url, str(created)))
        except Exception as e:
            raise Exception(
                "An error occurred while adding a character in the database. query: %s - message: %s"
                % (sql, e)
            )
        database_commit(self.connector)

        # Add the character vehicles ownership
        vehicles = character_data.get("vehicles_id")
        if vehicles:
            character_vehicles_manager = CharacterVehiclesAndStarshipsManager(
                self.connector, self.cursor, conveyance_type=ConveyanceType.VEHICLES
            )
            character_vehicles_manager.add(character_id, vehicles)

        # Add the character starships ownership
        starships = character_data.get("starships_id")
        if starships:
            character_starships_manager = CharacterVehiclesAndStarshipsManager(
                self.connector, self.cursor, conveyance_type=ConveyanceType.STARSHIPS
            )
            character_starships_manager.add(character_id, starships)

        return self.get(character_id)

    def update(self, character_id, character_data):
        """
        Update a character

        Args:
            character_id (str): the character's ID
            character_data (dict): the charater's data to update

        Returns:
            (dict): the updated character
        """
        # Get the character in order to check that he exist
        old_character = self.get(character_id)[0]

        # Generate auto-generated fields
        edited = datetime.now().isoformat()

        # Only update the specified and existing fields
        keys = tuple(set(character_data.keys()) & set(key.replace(".people", "") for key in CHARACTER_KEYS))
        if keys:
            params_and_columns_name = ", ".join([key + "=?" for key in keys]) + ", edited=?"
            sql = "UPDATE people SET {} WHERE id=?".format((params_and_columns_name))

            params_values = [character_data[key] for key in keys] + [
                edited,
                str(character_id),
            ]
            try:
                self.cursor.execute(sql, params_values)
            except Exception as e:
                raise Exception(
                    "An error occurred while updating a character in the database. query: %s - message: %s"
                    % (sql, e)
                )
            database_commit(self.connector)

        # Update the character vehicles ownership
        vehicles = character_data.get("vehicles_id")

        character_vehicles_manager = CharacterVehiclesAndStarshipsManager(
            self.connector, self.cursor, conveyance_type=ConveyanceType.VEHICLES
        )
        character_vehicles_manager.update(
            character_id, old_character["vehicles_id"], vehicles
        )

        # Update the character starships ownership
        starships = character_data.get("starships_id")
        character_starships_manager = CharacterVehiclesAndStarshipsManager(
            self.connector, self.cursor, conveyance_type=ConveyanceType.STARSHIPS
        )
        character_starships_manager.update(
            character_id, old_character["starships_id"], starships
        )

        return self.get(character_id)

    def delete(self, character_id):
        """
        Delete a character

        Args:
            character_id (str): the character's ID

        Returns:
            (str): the deleted character's id
        """
        # Get the character in order to check that he exist
        character = self.get(character_id)[0]

        sql = "DELETE FROM people " "WHERE id=?"
        try:
            self.cursor.execute(sql, (str(character_id),))
        except Exception as e:
            raise Exception(
                "An error occurred while deleting a character in the database. query: %s - message: %s"
                % (sql, e)
            )
        database_commit(self.connector)

        # Delete the character vehicles ownership
        vehicles = character.get("vehicles_id")
        if vehicles:
            character_vehicles_manager = CharacterVehiclesAndStarshipsManager(
                self.connector, self.cursor, conveyance_type=ConveyanceType.VEHICLES
            )
            character_vehicles_manager.delete(character_id)

        # Delete the character starships ownership
        starships = character.get("starships_id")
        if starships:
            character_starships_manager = CharacterVehiclesAndStarshipsManager(
                self.connector, self.cursor, conveyance_type=ConveyanceType.STARSHIPS
            )
            character_starships_manager.delete(character_id)

        return character_id

    def _prettify_sqlite_response(self, rows):
        """
        Get a dict of characters from a sqlite response

        Args:
            rows (list(Row)): all the rows from a sqlite response

        Returns:
            (dict): a dict of one or more characters
        """
        characters = {}
        for row in rows:
            character = self._prettify_sqlite_row(row)

            # Merge entries with the same ID in order to have only one entry per character
            character_id = character["id"]
            if character_id in characters:
                for element in [
                    "vehicles_id",
                    "vehicles_name",
                    "starships_id",
                    "starships_name",
                ]:
                    element_set = set(characters[character_id][element])
                    characters[character_id][element] = list(
                        element_set.union(character[element])
                    )
            else:
                characters[character_id] = character

        return characters

    def _prettify_sqlite_row(self, row):
        """
        Get a character from a sqlite row

        Args:
            row (Row): a single row from a sqlite response

        Returns:
            (dict): a dict representing a character row
        """
        character = dict(row)

        # Transform the vehicles and starships entries in lists
        character["vehicles_id"] = (
            [character["vehicles_id"]] if character["vehicles_id"] else []
        )
        character["vehicles_name"] = (
            [character["vehicles_name"]] if character["vehicles_name"] else []
        )

        character["starships_id"] = (
            [character["starships_id"]] if character["starships_id"] else []
        )
        character["starships_name"] = (
            [character["starships_name"]] if character["starships_name"] else []
        )

        return character

    def _generate_new_user_id(self):
        """
        Generate a new user ID

        Returns:
            (str): a new ID has a string
        """
        sql = "SELECT id FROM people ORDER BY cast(id AS INTEGER) DESC LIMIT 1"
        try:
            query_result = self.cursor.execute(sql)
            rows = query_result.fetchall()
            last_id = rows[0]["id"]
        except Exception as e:
            raise Exception(
                "An error occurred while retrieving the last character ID in the database. query: %s - message: %s"
                % (sql, e)
            )

        return str(int(last_id) + 1)
