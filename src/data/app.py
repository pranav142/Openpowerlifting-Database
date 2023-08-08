from flask import Flask, jsonify, request, abort
from flask.wrappers import Response
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os
from enum import Enum
from tables import Tables, columnsCollection
from app_utils import (
    get_start_and_end_index,
    get_units,
    select_range_data,
    select_record_id,
    format_response,
    add_record,
    delete_record,
    update_record,
)

app = Flask(__name__)

load_dotenv()

app.config["MYSQL_USER"] = os.getenv("MY_SQL_USER")
app.config["MYSQL_PASSWORD"] = os.getenv("MY_SQL_PASSWORD")
app.config["MYSQL_DB"] = "test_refactor"
app.config["MYSQL_HOST"] = os.getenv("MY_SQL_HOST")

mysql = MySQL(app)


@app.route("/api/rankings")
def get_range_records() -> Response:
    start_index, end_index = get_start_and_end_index()
    units = get_units()
    formated_data = []
    for table in Tables:
        data = select_range_data(
            start_index, end_index, table.value[0], sql_connection=mysql
        )
        formated_data.append(format_response(data, units, table.value[1]))
    return jsonify(formated_data)


@app.route("/api/<int:id>")
def get_record_from_id(id: int) -> Response:
    units = get_units()
    formated_data = []
    for table in Tables:
        data = select_record_id(id, table.value[0], sql_connection=mysql)
        formated_data.append(format_response(data, units, table.value[1]))
    return jsonify(formated_data)


@app.route("/api/add-record", methods=["POST"])
def post_competitor_record() -> Response:
    add_record(
        request.json,
        table=Tables.records.value[0],
        columns=Tables.records.value[1].get_all_column_names(),
        sql_connection=mysql,
    )
    response_data = {"message": "POST request successful!"}
    return jsonify(response_data)


@app.route("/api/<int:id>/delete-record", methods=["DELETE"])
def delete_competitor_record(id) -> Response:
    delete_record(Tables.records.value[0], id, sql_connection=mysql)
    response_data = {"message": "DELETE request successful!", "id": id}
    return jsonify(response_data)


@app.route("/api/<int:id>/update-record", methods=["PUT"])
def update_competitor_record(id) -> Response:
    update_record(Tables.records.value[0], id, request.json, sql_connection=mysql)
    response_data = {"message": "UPDATE request successful!", "id": id}
    return jsonify(response_data)


def main() -> None:
    app.run(debug=True)


if __name__ == "__main__":
    main()
