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


def execute_sql_query(query: str) -> tuple:
    cur = mysql.connection.cursor()
    cur.execute(query)
    data = cur.fetchall()
    cur.close()
    return data


def select_all_data(table: str) -> tuple:
    return execute_sql_query(f"SELECT * FROM {table}")


def select_record_id(table: str, id: int):
    return execute_sql_query(f"SELECT {table}.* FROM {table} WHERE {table}.id = {id}")


@app.route("/api/")
def get_all_records() -> Response:
    data = select_all_data("competitors")
    return jsonify(data)


@app.route("/api/<int:id>")
def get_record_from_id(id: int) -> Response:
    data = select_record_id("competitors", id)
    if not data:
        abort(404, description="Record not found. Please enter a valid id")
    formated_data = format_competitor_data(data)
    return jsonify(formated_data)


if __name__ == "__main__":
    app.run(debug=True)
