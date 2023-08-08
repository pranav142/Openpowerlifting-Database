import pandas as pd
import mysql.connector
from mysql.connector.connection import MySQLConnection
from dotenv import load_dotenv
import os
from data.db_utils import MySqlInstance, MySQL, DatabaseError, connect_to_MySQL_instance
from data.utils import timeit
from tables import Tables


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
        cursor.execute(f"CREATE TABLE {table_name} ({', '.join(columns)})")

        print("Successfully Added Tables")
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_TABLE_EXISTS_ERROR:
            print("Tables already exist.")
        else:
            raise DatabaseError(f"Error creating tables: {err}")
    finally:
        cursor.close()


def populate_table(
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
                table_name=table.value[0],
                columns=table.value[1].get_all_sql_columns(),
            )

            populate_table(
                df,
                table.value[0],
                table.value[1].get_all_column_names(),
                sql_connection,
                database_name,
            )


def main() -> None:
    csv_file = "../../data/processed/processed_lifting_data.csv"

    load_dotenv()

    sql_instance = MySqlInstance(
        host=os.getenv("MY_SQL_HOST"),
        port=os.getenv("MY_SQL_PORT"),
        user=os.getenv("MY_SQL_USER"),
        password=os.getenv("MY_SQL_PASSWORD"),
    )

    database_name = "test_refactor"

    create_db_with_data(
        database_name,
        sql_instance,
        csv_file,
        tables=Tables,
    )


if __name__ == "__main__":
    main()
