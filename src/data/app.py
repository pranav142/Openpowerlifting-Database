from flask import Flask, jsonify, request, abort
from flask.wrappers import Response
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()

app.config["MYSQL_USER"] = os.getenv("MY_SQL_USER")
app.config["MYSQL_PASSWORD"] = os.getenv("MY_SQL_PASSWORD")
app.config["MYSQL_DB"] = "openpowerlifting"
app.config["MYSQL_HOST"] = os.getenv("MY_SQL_HOST")

mysql = MySQL(app)


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


def format_competitions_data(competiton_data: tuple) -> dict:
    formated_data = []
    for competition in competiton_data:
        formated_data.append()


def execute_sql_query(query: str) -> tuple:
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data


def select_range_data(table: str, start_index: int, end_index: int) -> tuple:
    return execute_sql_query(
        f"SELECT {table}.* FROM {table} WHERE {table}.id BETWEEN {start_index} AND {end_index}"
    )


def select_record_id(table: str, id: int):
    return execute_sql_query(f"SELECT {table}.* FROM {table} WHERE {table}.id = {id}")


@app.route("/api/rankings")
def get_range_records() -> Response:
    start_index = int(request.args.get("start", 0))
    end_index = int(request.args.get("end", 10))
    data = select_range_data("competitors", start_index, end_index)
    formated_data = format_competitor_data(data)
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
