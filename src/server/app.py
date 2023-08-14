from flask import Flask, jsonify, request, abort, send_from_directory, render_template
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


def parse_args() -> argparse.Namespace:
    """Parse command line arguments and return the parsed namespace.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
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
    return parser.parse_args()


def configure_app(args: argparse.Namespace, app: Flask) -> MySQL:
    """Configure the Flask app with MySQL connection settings.

    Args:
        args (argparse.Namespace): Parsed command line arguments.

    Returns:
        MySQL: MySQL connection object.
    """
    app.config["MYSQL_USER"] = args.user
    app.config["MYSQL_PASSWORD"] = args.password
    app.config["MYSQL_DB"] = args.database
    app.config["MYSQL_HOST"] = args.host

    return MySQL(app)


@app.route("/docs/")
@app.route("/docs/<path:path>")
def serve_docs(path="index.html"):
    """
    Serve the Sphinx-generated documentation files.

    This route serves the Sphinx-generated documentation files from the specified path.

    Args:
        path (str, optional): The path to the documentation file. Defaults to "index.html".

    Returns:
        Response: The requested documentation file.
    """
    return send_from_directory("../docs/_build/html", path)


@app.route("/api/rankings")
def get_range_records() -> Response:
    """Get data records within a specified range and return the formatted response.

    Returns:
        Response: Formatted JSON response containing data records.
    """
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
    """Get data records for a specified ID and return the formatted response.

    Args:
        id (int): ID of the record to retrieve.

    Returns:
        Response: Formatted JSON response containing data records.
    """
    units = get_units()
    formated_data = []
    for table in Tables:
        data = select_record_id(id, table.name, sql_connection=mysql)
        formated_data.append(format_response(data, units, table.columns_collection))
    return jsonify(formated_data)


@app.route("/api/add-record", methods=["POST"])
def post_competitor_record() -> Response:
    """Add a new data record and return a response message.

    Returns:
        Response: JSON response indicating the success of the POST request.
    """
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
    """Delete a data record by ID and return a response message.

    Args:
        id (int): ID of the record to delete.

    Returns:
        Response: JSON response indicating the success of the DELETE request.
    """
    delete_record(Tables.records.name, id, sql_connection=mysql)
    response_data = {"message": "DELETE request successful!", "id": id}
    return jsonify(response_data)


@app.route("/api/<int:id>/update-record", methods=["PUT"])
def update_competitor_record(id) -> Response:
    """Delete a data record by ID and return a response message.

    Args:
        id (int): ID of the record to delete.

    Returns:
        Response: JSON response indicating the success of the DELETE request.
    """
    update_record(Tables.records.name, id, request.json, sql_connection=mysql)
    response_data = {"message": "UPDATE request successful!", "id": id}
    return jsonify(response_data)


def main() -> None:
    """Run the Flask app.

    Starts the Flask app to serve HTTP requests.
    """
    global mysql
    args = parse_args()
    mysql = configure_app(args, app)
    app.run(debug=True, host="0.0.0.0", port=os.getenv("SERVER_PORT", 8080))


if __name__ == "__main__":
    main()
