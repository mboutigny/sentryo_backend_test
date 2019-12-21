from app.utils import ConveyanceType, database_commit


class CharacterVehiclesAndStarshipsManager:
    def __init__(self, connector, cursor, conveyance_type):
        self.connector = connector
        self.cursor = cursor

        if not isinstance(conveyance_type, ConveyanceType):
            raise Exception("'conveyance_type' must be ENUM ConveyanceType.")
        self.conveyance_type = conveyance_type.value

    def get_by_character(self, character_id):
        """
        Get all the vehicles or starships ID owned by a character

        Args:
            character_id (str) the character's ID

        Return:
            (list): a list of vehicles or starships ID
        """
        sql = "SELECT {0} FROM people_{0} WHERE people=?".format(self.conveyance_type)
        try:
            query_result = self.cursor.execute(sql, (str(character_id),))
        except Exception as e:
            raise Exception(
                "An error occurred while getting a character %s in the database: query: %s - message: %s"
                % (self.conveyance_type, sql, e)
            )

        rows = query_result.fetchall()
        starships = [s_id for _, s_id in rows]

        return starships

    def add(self, character_id, conveyances):
        """
        Add the character vehicles or starships ownership in the database

        Args:
            character_id (str): the character's ID
            conveyances (list): a list of vehicles or starships IDs
        """
        sql = "INSERT INTO people_{0} ('people', '{0}') VALUES (?, ?)".format(
            self.conveyance_type
        )

        for conveyance in set(conveyances):
            try:
                if not self._is_conveyance_id_valid(conveyance):
                    raise Exception(
                        "The specified %s does not exist: ID: %s"
                        % (self.conveyance_type, conveyance)
                    )
                self.cursor.execute(sql, (str(character_id), conveyance))
            except Exception as e:
                raise Exception(
                    "An error occurred while adding a character %s in the database: query: %s - message: %s"
                    % (self.conveyance_type, sql, e)
                )

        database_commit(self.connector)

    def update(self, character_id, old_conveyances, new_conveyances):
        """
        Update the character vehicles or starships ownership in the database

        Args:
            character_id (str): the character's ID
            old_conveyances (list): the old list of vehicles or starships IDs
            new_conveyances (list): the new list of vehicles or starships IDs
        """
        # Make sure all ID in the lists are strings
        new_conveyances = [str(nc) for nc in new_conveyances]

        conveyances_to_add = list(set(new_conveyances) - set(old_conveyances))
        conveyances_to_delete = list(set(old_conveyances) - set(new_conveyances))

        if conveyances_to_add:
            self.add(character_id, conveyances_to_add)

        if conveyances_to_delete:
            self.delete(character_id, conveyances_to_delete)

    def delete(self, character_id, conveyances=None):
        """
        Delete the character vehicles or starships ownership in the database

        Args:
            character_id (str): the character's ID
            conveyances (list): a list of vehicles or starships IDs default is None
        """
        try:
            if conveyances:
                in_clause = (
                    str(tuple(conveyances))
                    if len(conveyances) > 1
                    else "(" + conveyances[0] + ")"
                )
                optional_sql = " AND {} IN ({})".format(
                    self.conveyance_type, ", ".join("?" * len(conveyances))
                )

                sql = (
                    "DELETE FROM people_{} "
                    "WHERE people=?".format(self.conveyance_type) + optional_sql
                )
                self.cursor.execute(sql, [character_id] + conveyances)
            else:
                sql = "DELETE FROM people_{} " "WHERE people=?".format(
                    self.conveyance_type
                )
                self.cursor.execute(sql, [character_id])
        except Exception as e:
            raise Exception(
                "An error occurred while deleting a character %s in the database: query: %s - message: %s"
                % (self.conveyance_type, sql, e)
            )

        database_commit(self.connector)

    def _is_conveyance_id_valid(self, conveyance_id):
        """
        Check that the given ID of the vehicle or the starship is valid

        Args:
            conveyance_id (str): a vehicle or starship ID

        Returns:
            (bool): Whether the given ID is valid or not
        """
        sql = "SELECT id FROM {} WHERE id=?".format(self.conveyance_type)

        try:
            query_result = self.cursor.execute(sql, (str(conveyance_id),))
            if query_result.fetchall():
                return True
            return False
        except Exception as e:
            raise Exception(
                "An error occurred while fetching a %s in the database: query: %s - message: %s"
                % (self.conveyance_type, sql, e)
            )
