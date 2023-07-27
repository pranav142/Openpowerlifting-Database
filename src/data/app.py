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


class units(Enum):
    pounds = ("(lbs)", POUNDS_TO_POUNDS_COEF)
    kilos = ("(kgs)", POUNDS_TO_KILOS_COEF)


def format_competitor_data(competitor_data: tuple) -> dict:
    formated_data = []
    for competitor in competitor_data:
        formated_data.append(
            {
                "ID": competitor[0],
                "Name": competitor[1],
                "Instagram_Handle": competitor[2],
                "Origin": competitor[3],
                "Gender": competitor[4],
            }
        )
    return formated_data


def format_competitions_data(
    competiton_data: tuple, units: units = units.pounds
) -> dict:
    UNIT_NAME = 0
    UNIT_CONVERSION_COEFFECIENT = 1
    formated_data = []
    for competition in competiton_data:
        formated_data.append(
            {
                "ID": competition[0],
                "Competition_Date": competition[1],
                "Competition_Country": competition[2],
                "Competition_City": competition[3],
                "Equipment": competition[4],
                "Age": competition[5],
                f"Weight{units.value[UNIT_NAME]}": competition[6]
                * units.value[UNIT_CONVERSION_COEFFECIENT],
                "Class": competition[7],
                f"Squat{units.value[UNIT_NAME]}": competition[8]
                * units.value[UNIT_CONVERSION_COEFFECIENT],
                f"Bench{units.value[UNIT_NAME]}": competition[9]
                * units.value[UNIT_CONVERSION_COEFFECIENT],
                f"Deadlift{units.value[UNIT_NAME]}": competition[10]
                * units.value[UNIT_CONVERSION_COEFFECIENT],
                f"Total{units.value[UNIT_NAME]}": competition[11]
                * units.value[UNIT_CONVERSION_COEFFECIENT],
                "Dots": competition[12],
            }
        )
    return formated_data


def execute_sql_query(query: str) -> tuple:
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data


def select_range_data(
    table: str, start_index: int, end_index: int, max: int = 100
) -> tuple:
    if end_index - start_index > max:
        end_index = start_index + max
    if start_index > end_index:
        end_index = start_index
    return execute_sql_query(
        f"SELECT {table}.* FROM {table} WHERE {table}.id BETWEEN {start_index} AND {end_index}"
    )


def select_record_id(table: str, id: int) -> tuple:
    return execute_sql_query(f"SELECT {table}.* FROM {table} WHERE {table}.id = {id}")


def get_units() -> units:
    unit_param = request.args.get("units", "pounds")
    return units[unit_param.lower()]


def get_start_and_end_index() -> tuple[int, int]:
    start_index = int(request.args.get("start", 0))
    end_index = int(request.args.get("end", 10))
    return start_index, end_index


@app.route("/api/rankings")
def get_range_records() -> Response:
    start_index, end_index = get_start_and_end_index()
    units = get_units()
    data = select_range_data("competitions", start_index, end_index)
    formated_data = format_competitions_data(data, units)
    return jsonify(formated_data)


@app.route("/api/<int:id>")
def get_record_from_id(id: int) -> Response:
    data = select_record_id("competitors", id)
    if not data:
        abort(404, description="Record not found. Please enter a valid id")
    formated_data = format_competitor_data(data)
    return jsonify(formated_data)


if __name__ == "__main__":
    app.run(debug=True)
