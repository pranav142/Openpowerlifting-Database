from dataclasses import dataclass
from mysql.connector.connection import MySQLConnection
import mysql.connector


@dataclass
class MySqlInstance:
    host: str
    port: int
    user: str
    password: str


class MySQL:
    def __init__(self, sql_instance: MySqlInstance):
        self.sql_instance = sql_instance
        self.sql_connection = None

    def __enter__(self):
        self.sql_connection = connect_to_MySQL_instance(self.sql_instance)
        return self.sql_connection

    def __exit__(self, exc_type, exc_value, traceback):
        if self.sql_connection is not None:
            self.sql_connection.close()


class DatabaseError(Exception):
    pass


def connect_to_MySQL_instance(sql_instance: MySqlInstance) -> MySQLConnection:
    return mysql.connector.connect(
        host=sql_instance.host,
        port=sql_instance.port,
        user=sql_instance.user,
        password=sql_instance.password,
    )
