from flask import Flask, jsonify, request, abort
from flask.wrappers import Response
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os
from enum import Enum
from server.tables import Tables, columnsCollection
from server.app_utils import (
    get_start_and_end_index,
    get_units,
    select_range_data,
    select_record_id,
    format_response,
    add_record,
    delete_record,
    update_record,
)
import argparse

app = Flask(__name__)

load_dotenv()

parser = argparse.ArgumentParser(description="Flask MySQL App")
parser.add_argument("--user", default=os.getenv("MY_SQL_USER"), help="MySQL user")
parser.add_argument(
    "--password", default=os.getenv("MY_SQL_PASSWORD"), help="MySQL password"
)
parser.add_argument(
    "--database", default=os.getenv("MY_SQL_DATABASE"), help="MySQL database name"
)
parser.add_argument("--host", default=os.getenv("MY_SQL_HOST"), help="MySQL host")
args = parser.parse_args()

app.config["MYSQL_USER"] = args.user
app.config["MYSQL_PASSWORD"] = args.password
app.config["MYSQL_DB"] = args.database
app.config["MYSQL_HOST"] = args.host

mysql = MySQL(app)


@app.route("/api/rankings")
def get_range_records() -> Response:
    start_index, end_index = get_start_and_end_index()
    units = get_units()
    formated_data = []
    for table in Tables:
        data = select_range_data(
            start_index, end_index, table.name, sql_connection=mysql
        )
        formated_data.append(format_response(data, units, table.columns_collection))
    return jsonify(formated_data)


@app.route("/api/<int:id>")
def get_record_from_id(id: int) -> Response:
    units = get_units()
    formated_data = []
    for table in Tables:
        data = select_record_id(id, table.name, sql_connection=mysql)
        formated_data.append(format_response(data, units, table.columns_collection))
    return jsonify(formated_data)


@app.route("/api/add-record", methods=["POST"])
def post_competitor_record() -> Response:
    add_record(
        request.json,
        table=Tables.records.name,
        columns=Tables.records.columns_collection.get_all_column_names(),
        sql_connection=mysql,
    )
    response_data = {"message": "POST request successful!"}
    return jsonify(response_data)


@app.route("/api/<int:id>/delete-record", methods=["DELETE"])
def delete_competitor_record(id) -> Response:
    delete_record(Tables.records.name, id, sql_connection=mysql)
    response_data = {"message": "DELETE request successful!", "id": id}
    return jsonify(response_data)


@app.route("/api/<int:id>/update-record", methods=["PUT"])
def update_competitor_record(id) -> Response:
    update_record(Tables.records.name, id, request.json, sql_connection=mysql)
    response_data = {"message": "UPDATE request successful!", "id": id}
    return jsonify(response_data)


def main() -> None:
    app.run(debug=True, host="0.0.0.0", port=os.getenv("SERVER_PORT", 8080))


if __name__ == "__main__":
    main()
