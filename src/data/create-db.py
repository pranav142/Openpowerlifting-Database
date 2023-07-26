import pandas as pd
import mysql.connector
from mysql.connector import Error
from dataclasses import dataclass
from typing import Optional
from mysql.connector.connection import MySQLConnection
import pyodbc
from dotenv import load_dotenv, dotenv_values
import os


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


def create_database(sql_connection: MySQLConnection, database_name: str):
    try:
        cursor = sql_connection.cursor()
        cursor.execute(f"CREATE DATABASE {database_name}")
        print(f"Database '{database_name}' created successfully.")
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_DB_CREATE_EXISTS:
            print(f"Database '{database_name}' already exists.")
        else:
            raise DatabaseError(f"Error creating database: {err}")
    finally:
        cursor.close()


def create_tables(sql_connection: MySQLConnection, database_name: str) -> None:
    try:
        cursor = sql_connection.cursor()
        cursor.execute(f"USE {database_name}")
        cursor.execute(
            "CREATE TABLE competitors (ID INT PRIMARY KEY, Name VARCHAR(255), Instagram_Handle VARCHAR(255), Origin VARCHAR(255), Gender VARCHAR(10))"
        )

        cursor.execute(
            "CREATE TABLE competitions (ID INT PRIMARY KEY, Competition_Date DATE, Competition_Country VARCHAR(255), Competition_City VARCHAR(255), Equipment VARCHAR(255), Age INT, Weight FLOAT, Class FLOAT, Squat FLOAT, Bench FLOAT, Deadlift FLOAT, Total FLOAT, Dots FLOAT)"
        )

        print("Successfully Added Tables")
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_TABLE_EXISTS_ERROR:
            print("Tables already exist.")
        else:
            raise DatabaseError(f"Error creating tables: {err}")
    finally:
        cursor.close()


def populate_tables(
    df: pd.DataFrame,
    table_name: str,
    columns: list[str],
    sql_connection: MySQLConnection,
    database_name: str,
):
    cursor = sql_connection.cursor()
    cursor.execute(f"USE {database_name}")

    truncate_query = f"TRUNCATE TABLE {table_name}"
    cursor.execute(truncate_query)

    cols = ", ".join(columns)
    placeholders = ", ".join(["%s" for _ in columns])
    sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"

    for index, row in df.iterrows():
        values = []
        for col in columns:
            value = row[col]
            if pd.isna(value):
                value = None
            values.append(value)

        cursor.execute(sql, tuple(values))

    sql_connection.commit()
    print(f"Finished Populating {table_name} in {database_name} database")
    cursor.close()


def main():
    csv_file = "../../data/processed/processed_lifting_data.csv"
    df = pd.read_csv(csv_file)

    load_dotenv()

    sql_instance = MySqlInstance(
        host="localhost",
        port=3306,
        user="root",
        password=os.getenv("MY_SQL_PASSWORD"),
    )

    database_name = "openpowerlifting"

    with MySQL(sql_instance) as sql_connection:
        create_database(sql_connection, database_name)
        create_tables(sql_connection, database_name)

        columns_to_insert_into_competitors = [
            "ID",
            "Name",
            "Instagram_Handle",
            "Origin",
            "Gender",
        ]

        populate_tables(
            df,
            "competitors",
            columns_to_insert_into_competitors,
            sql_connection,
            database_name,
        )

        columns_to_insert_into_competitions = [
            "ID",
            "Competition_Date",
            "Competition_Country",
            "Competition_City",
            "Equipment",
            "Age",
            "Weight",
            "Class",
            "Squat",
            "Bench",
            "Deadlift",
            "Total",
            "Dots",
        ]

        populate_tables(
            df,
            "competitions",
            columns_to_insert_into_competitions,
            sql_connection,
            database_name,
        )


if __name__ == "__main__":
    main()
