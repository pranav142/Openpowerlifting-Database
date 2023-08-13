import pandas as pd
import mysql.connector
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor
from dotenv import load_dotenv
import os
from server.db_utils import (
    MySqlInstance,
    MySQL,
    DatabaseError,
    connect_to_MySQL_instance,
)
from data.utils import timeit
from server.tables import Tables
import argparse
import itertools


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


def create_table(
    sql_connection: MySQLConnection, database_name: str, table_name: str, columns: list
) -> None:
    try:
        cursor = sql_connection.cursor()
        cursor.execute(f"USE {database_name}")
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        cursor.execute(f"CREATE TABLE {table_name} ({', '.join(columns)})")

        print("Successfully Added Tables")
    except mysql.connector.Error as err:
        raise DatabaseError(f"Error creating tables: {err}")
    finally:
        cursor.close()


def connect_to_database(
    sql_connection: MySQLConnection, database_name: str
) -> MySQLCursor:
    cursor = sql_connection.cursor()
    cursor.execute(f"USE {database_name}")
    return cursor


def execute_truncate_query(cursor: MySQLCursor, table_name: str) -> None:
    truncate_query = f"TRUNCATE TABLE {table_name}"
    cursor.execute(truncate_query)


def generate_insert_sql(table_name: str, columns: list[str]) -> str:
    cols = ", ".join(columns)
    placeholders = ", ".join(["%s" for _ in columns])
    return f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"


def insert_batch(
    cursor: MySQLCursor, sql_connection: MySQLConnection, sql: str, batch: int
) -> None:
    cursor.executemany(sql, batch)
    sql_connection.commit()


def print_progress(current_row: int, total_rows: int, spinner: itertools.cycle) -> None:
    loading_indicator = next(spinner)
    progress = current_row / total_rows * 100
    print(
        f"Inserted {current_row}/{total_rows} rows {loading_indicator} - {progress:.2f} % \r",
        end="",
    )


def populate_table(
    df: pd.DataFrame,
    table_name: str,
    columns: list[str],
    sql_connection: MySQLConnection,
    database_name: str,
    batch_size: int = 1000,
) -> None:
    cursor = connect_to_database(sql_connection, database_name)
    execute_truncate_query(cursor, table_name)

    sql = generate_insert_sql(table_name, columns)
    batch = []
    spinner = itertools.cycle(["-", "/", "|", "\\"])
    current_row = 0
    total_rows = len(df)

    for _, row in df.iterrows():
        values = []
        for col in columns:
            value = row[col]
            if pd.isna(value):
                value = None
            values.append(value)

        batch.append(tuple(values))

        if len(batch) >= batch_size:
            insert_batch(cursor, sql_connection, sql, batch)
            current_row += len(batch)
            print_progress(current_row, total_rows, spinner)
            batch = []

    if batch:
        insert_batch(cursor, sql_connection, sql, batch)
        current_row += len(batch)
        print_progress(current_row, total_rows, spinner)

    print(f"Finished Populating {table_name} in {database_name} database")
    cursor.close()


@timeit
def create_db_with_data(
    database_name: str,
    sql_instance: MySqlInstance,
    csv_file: str,
) -> None:
    df = pd.read_csv(csv_file)

    with MySQL(sql_instance) as sql_connection:
        create_database(sql_connection, database_name)
        for table in Tables:
            create_table(
                sql_connection,
                database_name=database_name,
                table_name=table.name,
                columns=table.columns_collection.get_all_sql_columns(),
            )

            populate_table(
                df,
                table.name,
                table.columns_collection.get_all_column_names(),
                sql_connection,
                database_name,
            )


def parse_arguments() -> argparse.Namespace:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Create a database with data.")
    parser.add_argument(
        "--name",
        default=os.getenv("MY_SQL_DATABASE"),
        help="Name of the database to create (default: MY_SQL_DATABASE from .env)",
    )

    args = parser.parse_args()
    return args


def main() -> None:
    args = parse_arguments()
    database_name = args.name

    csv_file = "../../data/processed/processed_lifting_data.csv"

    sql_instance = MySqlInstance(
        host=os.getenv("MY_SQL_HOST"),
        port=os.getenv("MY_SQL_PORT"),
        user=os.getenv("MY_SQL_USER"),
        password=os.getenv("MY_SQL_PASSWORD"),
    )

    create_db_with_data(
        database_name,
        sql_instance,
        csv_file,
    )


if __name__ == "__main__":
    main()
