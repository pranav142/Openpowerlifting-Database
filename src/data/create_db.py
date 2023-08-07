import pandas as pd
import mysql.connector
from mysql.connector.connection import MySQLConnection
from dotenv import load_dotenv
import os
from data.db_utils import MySqlInstance, MySQL, DatabaseError, connect_to_MySQL_instance
from data.utils import timeit


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


# TODO: Add Query To Ensure Key can Auto Increment
def table_post_processing(database_name: str, sql_connection: MySQLConnection) -> None:
    cursor = sql_connection.cursor()
    cursor.execute(f"USE {database_name}")
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]

    for table_name in tables:
        alter_query = f"""ALTER TABLE {database_name}.{table_name}
                        CHANGE COLUMN `ID` `ID` INT NOT NULL AUTO_INCREMENT ;"""
        cursor.execute(alter_query)
    sql_connection.commit()
    cursor.close()


@timeit
def create_db_with_data(
    database_name: str, sql_instance: MySqlInstance, csv_file: str
) -> None:
    df = pd.read_csv(csv_file)

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

        table_post_processing(database_name, sql_connection)


def main() -> None:
    csv_file = "../../data/processed/processed_lifting_data.csv"

    load_dotenv()

    sql_instance = MySqlInstance(
        host=os.getenv("MY_SQL_HOST"),
        port=os.getenv("MY_SQL_PORT"),
        user=os.getenv("MY_SQL_USER"),
        password=os.getenv("MY_SQL_PASSWORD"),
    )

    database_name = "test"

    create_db_with_data(database_name, sql_instance, csv_file)


if __name__ == "__main__":
    main()
