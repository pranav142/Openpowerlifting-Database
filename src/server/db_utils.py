from dataclasses import dataclass
from mysql.connector.connection import MySQLConnection
import mysql.connector


@dataclass
class MySqlInstance:
    """Data class representing MySQL instance configuration.

    Args:
        host (str): Hostname or IP address of the MySQL server.
        port (int): Port number for the MySQL server.
        user (str): Username for authenticating to the MySQL server.
        password (str): Password for authenticating to the MySQL server.
    """

    host: str
    port: int
    user: str
    password: str


class MySQL:
    """Context manager for managing MySQL database connections.

    Args:
        sql_instance (MySqlInstance): Configuration for the MySQL instance.

    Example:
        with MySQL(sql_instance) as sql_connection:
            cursor = sql_connection.cursor()
            cursor.execute("SELECT * FROM my_table")
            result = cursor.fetchall()
            cursor.close()
    """

    def __init__(self, sql_instance: MySqlInstance):
        """Initialize the MySQL context manager.

        Args:
            sql_instance (MySqlInstance): Configuration for the MySQL instance.
        """
        self.sql_instance = sql_instance
        self.sql_connection = None

    def __enter__(self):
        """Enter the context and establish a MySQL connection.

        Returns:
            MySQLConnection: MySQL connection object.
        """
        self.sql_connection = connect_to_MySQL_instance(self.sql_instance)
        return self.sql_connection

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the context and close the MySQL connection.

        Args:
            exc_type: Type of the exception raised (if any).
            exc_value: Value of the exception raised (if any).
            traceback: Exception traceback (if any).
        """
        if self.sql_connection is not None:
            self.sql_connection.close()


class DatabaseError(Exception):
    """Custom exception class for database-related errors."""

    pass


def connect_to_MySQL_instance(sql_instance: MySqlInstance) -> MySQLConnection:
    """Connect to a MySQL database instance.

    Args:
        sql_instance (MySqlInstance): Configuration for the MySQL instance.

    Returns:
        MySQLConnection: A connection to the MySQL database.
    """
    return mysql.connector.connect(
        host=sql_instance.host,
        port=sql_instance.port,
        user=sql_instance.user,
        password=sql_instance.password,
    )
