from flask import Flask, jsonify, request, abort
from flask.wrappers import Response
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os
from enum import Enum

app = Flask(__name__)

load_dotenv()

app.config["MYSQL_USER"] = os.getenv("MY_SQL_USER")
app.config["MYSQL_PASSWORD"] = os.getenv("MY_SQL_PASSWORD")
app.config["MYSQL_DB"] = "openpowerlifting"
app.config["MYSQL_HOST"] = os.getenv("MY_SQL_HOST")

mysql = MySQL(app)

POUNDS_TO_KILOS_COEF = 0.45
POUNDS_TO_POUNDS_COEF = 1

ALL_TABLES = ["competitors", "competitions"]


class units(Enum):
    pounds = ("(lbs)", POUNDS_TO_POUNDS_COEF)
    kilos = ("(kgs)", POUNDS_TO_KILOS_COEF)


def convert_pounds(pounds: int, desired_units: units, precision: int = 3) -> float:
    if pounds is None:
        return None
    return round(pounds * desired_units.value[1], precision)


def format_data(data: tuple, units: units) -> dict:
    UNIT_NAME = 0
    formated_data = []
    for row in data:
        formated_data.append(
            {
                "ID": row[0],
                "Name": row[1],
                "Instagram_Handle": row[2],
                "Origin": row[3],
                "Gender": row[4],
                "ID": row[5],
                "Competition_Date": row[6],
                "Competition_Country": row[7],
                "Competition_City/State": row[8],
                "Equipment": row[9],
                "Age": row[10],
                f"Weight{units.value[UNIT_NAME]}": convert_pounds(row[11], units),
                "Class": row[12],
                f"Squat{units.value[UNIT_NAME]}": convert_pounds(row[13], units),
                f"Bench{units.value[UNIT_NAME]}": convert_pounds(row[14], units),
                f"Deadlift{units.value[UNIT_NAME]}": convert_pounds(row[15], units),
                f"Total{units.value[UNIT_NAME]}": convert_pounds(row[16], units),
                "Dots": row[17],
            }
        )
    return formated_data


def execute_sql_query(query: str) -> tuple:
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data


def generate_select_range_query(
    start_index: int,
    end_index: int,
    column: str = f"{ALL_TABLES[0]}.id",
    tables: list = ALL_TABLES,
) -> str:
    table_names = ", ".join(tables)
    table_id_conditions = " AND ".join(
        f"{table}.id = {tables[0]}.id" for table in tables[1:]
    )
    sql_query = f"SELECT * FROM {table_names} WHERE {table_id_conditions} AND {tables[0]}.id BETWEEN {start_index} AND {end_index} ORDER BY {column} DESC"
    return sql_query


def select_range_data(
    start_index: int,
    end_index: int,
    max: int = 100,
    column: str = f"{ALL_TABLES[0]}.id",
    tables: list = ALL_TABLES,
) -> list:
    if end_index - start_index > max:
        end_index = start_index + max
    if start_index > end_index:
        end_index = start_index
    sql_query = generate_select_range_query(start_index, end_index, column, tables)
    result = execute_sql_query(sql_query)
    return result


def select_record_id(id: int, tables: list = ALL_TABLES) -> tuple:
    table_names = ", ".join(tables)
    join_conditions = " AND ".join(f"{table}.id = {id}" for table in tables)
    sql_query = f"SELECT * FROM {table_names} WHERE {join_conditions}"
    result = execute_sql_query(sql_query)
    return result


def get_units() -> units:
    unit_param = request.args.get("units", "pounds")
    return units[unit_param.lower()]


def get_start_and_end_index() -> tuple[int, int]:
    start_index = int(request.args.get("start", 0))
    end_index = int(request.args.get("end", 10))
    return start_index, end_index


def get_column_to_order_by() -> str:
    return request.args.get("orderby", f"{ALL_TABLES[0]}.id")


@app.route("/api/rankings")
def get_range_records() -> Response:
    start_index, end_index = get_start_and_end_index()
    units = get_units()
    order_column = get_column_to_order_by()
    data = select_range_data(start_index, end_index, column=order_column)
    formated_data = format_data(data, units)
    return jsonify(formated_data)


@app.route("/api/<int:id>")
def get_record_from_id(id: int) -> Response:
    units = get_units
    data = select_record_id(id)
    formated_data = format_data(data, units)
    return jsonify(formated_data)


if __name__ == "__main__":
    app.run(debug=True)
