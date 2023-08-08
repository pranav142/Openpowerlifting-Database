from flask import Flask, jsonify, request, abort
from flask.wrappers import Response
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os
from enum import Enum
from tables import Tables, columnsCollection

app = Flask(__name__)

load_dotenv()

app.config["MYSQL_USER"] = os.getenv("MY_SQL_USER")
app.config["MYSQL_PASSWORD"] = os.getenv("MY_SQL_PASSWORD")
app.config["MYSQL_DB"] = "test_refactor"
app.config["MYSQL_HOST"] = os.getenv("MY_SQL_HOST")

mysql = MySQL(app)

POUNDS_TO_KILOS_COEF = 0.45
POUNDS_TO_POUNDS_COEF = 1


class Units(Enum):
    pounds = ("(lbs)", POUNDS_TO_POUNDS_COEF)
    kilos = ("(kgs)", POUNDS_TO_KILOS_COEF)


def convert_pounds(pounds: int, desired_units: Units, precision: int = 3) -> float:
    if pounds is None:
        return None
    return round(pounds * desired_units.value[1], precision)


def format_data(row: list, columns_collection: columnsCollection, units: Units) -> dict:
    data = {}
    for i, column in enumerate(columns_collection.columns):
        if column.is_weight:
            data[f"{column.column_name} {units.value[0]}"] = convert_pounds(
                row[i], units
            )
        else:
            data[column.column_name] = row[i]
    return data


def format_response(
    data: tuple, units: Units, columns_collection: columnsCollection
) -> dict:
    formated_data = []
    for row in data:
        formated_data.append(format_data(row, columns_collection, units))
    return formated_data


def execute_sql_query(
    query: str, additional_params: tuple = None, connection: MySQL = mysql
) -> tuple:
    cur = connection.connection.cursor()
    if additional_params is None:
        cur.execute(query)
    else:
        cur.execute(query, additional_params)
    data = cur.fetchall()
    connection.connection.commit()
    cur.close()
    return data


def generate_select_range_query(
    start_index: int,
    end_index: int,
    table_name: str,
) -> str:
    sql_query = f"SELECT * FROM {table_name} WHERE {table_name}.id BETWEEN {start_index} AND {end_index}"
    return sql_query


def select_range_data(
    start_index: int,
    end_index: int,
    table_name: str,
    max: int = 100,
) -> list:
    if end_index - start_index > max:
        end_index = start_index + max
    if start_index > end_index:
        end_index = start_index
    sql_query = generate_select_range_query(start_index, end_index, table_name)
    result = execute_sql_query(sql_query)
    return result


def select_record_id(id: int, table_name: str) -> tuple:
    sql_query = f"SELECT * FROM {table_name} WHERE {table_name}.ID = %s"
    return execute_sql_query(sql_query, (id,))


def select_range_data_single_table(
    table: str, start_index: int, end_index: int
) -> tuple:
    return execute_sql_query(
        f"SELECT {table}.* FROM {table} WHERE {table}.id BETWEEN {start_index} AND {end_index}"
    )


def select_record_id_single_table(table: str, id: int) -> tuple:
    return execute_sql_query(f"SELECT {table}.* FROM {table} WHERE {table}.id = {id}")


# TODO: FIx this So User can Add Multiple Competitons But Can't add multiple Competitors With Same ID
def add_record(data, table: str, columns: list) -> tuple:
    insert_query = f"""INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['%s']*len(columns))})"""

    values = []
    for column in columns:
        values.append(data.get(column))

    return execute_sql_query(insert_query, tuple(values))


def update_record(table: str, id: int, column: str, value: any) -> tuple:
    sql_query = f"UPDATE {table} SET {column} = {value} WHERE ID = {id}"
    return execute_sql_query(sql_query)


def delete_record(table: str, id: int) -> tuple:
    sql_query = f"DELETE FROM {table} WHERE id = {id};"
    return execute_sql_query(sql_query)


def get_update_values() -> tuple[str, any]:
    column = request.args.get("column")
    value = request.args.get("value")
    return column, value


def get_units() -> Units:
    unit_param = request.args.get("units", "pounds")
    return Units[unit_param.lower()]


def get_start_and_end_index() -> tuple[int, int]:
    start_index = int(request.args.get("start", 0))
    end_index = int(request.args.get("end", 10))
    return start_index, end_index


def get_column_to_order_by() -> str:
    return request.args.get("orderby", "id")


@app.route("/api/rankings")
def get_range_records() -> Response:
    start_index, end_index = get_start_and_end_index()
    units = get_units()
    formated_data = []
    for table in Tables:
        data = select_range_data(
            start_index,
            end_index,
            table.value[0],
        )
        formated_data.append(format_response(data, units, table.value[1]))
    return jsonify(formated_data)


@app.route("/api/<int:id>")
def get_record_from_id(id: int) -> Response:
    units = get_units()
    formated_data = []
    for table in Tables:
        data = select_record_id(id, table.value[0])
        formated_data.append(format_response(data, units, table.value[1]))
    return jsonify(formated_data)


@app.route("/api/add-record", methods=["POST"])
def post_competitor_record() -> Response:
    for table in Tables:
        add_record(
            request.json,
            table=table.value[0],
            columns=table.value[1].get_all_column_names(),
        )
    response_data = {"message": "POST request successful!"}
    return jsonify(response_data)


@app.route("/api/<int:id>/delete-record", methods=["DELETE"])
def delete_competitor_record(id) -> Response:
    for table in Tables:
        delete_record(table.value[0], id)
    response_data = {"message": "DELETE request successful!", "id": id}
    return jsonify(response_data)


@app.route("/api/<int:id>/update-record", methods=["PUT"])
def update_competitor_record(id) -> Response:
    column_name, value = get_update_values()
    update_record(Tables.competitors.value[0], id, column_name, value)
    response_data = {"message": "UPDATE request successful!", "id": id}
    return jsonify(response_data)


if __name__ == "__main__":
    app.run(debug=True)
