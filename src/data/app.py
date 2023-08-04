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


class Units(Enum):
    pounds = ("(lbs)", POUNDS_TO_POUNDS_COEF)
    kilos = ("(kgs)", POUNDS_TO_KILOS_COEF)


class Tables(Enum):
    competitiors = ("competitors",)
    competitions = ("competitions",)

    # TODO: Create a function that will generate all of the columns for each of the tables
    @classmethod
    def get_table_columns(cls):
        columns = execute_sql_query(f"SHOW COLUMNS FROM competitors")
        return columns

    @classmethod
    def get_all_tables(cls):
        return [table.value[0] for table in cls]

    def __len__(self):
        return len(self.get_all_tables())


def convert_pounds(pounds: int, desired_units: Units, precision: int = 3) -> float:
    if pounds is None:
        return None
    return round(pounds * desired_units.value[1], precision)


def format_data(data: tuple, units: Units) -> dict:
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


def format_competitions_data(competiton_data: tuple, units: Units) -> dict:
    UNIT_NAME = 0
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
                f"Weight{units.value[UNIT_NAME]}": convert_pounds(
                    competition[6], units
                ),
                "Class": competition[7],
                f"Squat{units.value[UNIT_NAME]}": convert_pounds(competition[8], units),
                f"Bench{units.value[UNIT_NAME]}": convert_pounds(competition[9], units),
                f"Deadlift{units.value[UNIT_NAME]}": convert_pounds(
                    competition[10], units
                ),
                f"Total{units.value[UNIT_NAME]}": convert_pounds(
                    competition[11], units
                ),
                "Dots": competition[12],
            }
        )
    return formated_data


def execute_sql_query(query: str, additional_params: tuple = None) -> tuple:
    cur = mysql.connection.cursor()
    if additional_params is None:
        cur.execute(query)
    else:
        cur.execue(query, additional_params)
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


def select_range_data_single_table(
    table: str, start_index: int, end_index: int
) -> tuple:
    return execute_sql_query(
        f"SELECT {table}.* FROM {table} WHERE {table}.id BETWEEN {start_index} AND {end_index}"
    )


def select_record_id_single_table(table: str, id: int) -> tuple:
    return execute_sql_query(f"SELECT {table}.* FROM {table} WHERE {table}.id = {id}")


# TODO: Test that This works then remove once General function has been Created
def add_competitor_record(table: str, data) -> tuple:
    insert_query = f"""
        INSERT INTO {table} (Name, Instagram_Handle, Weight, Country)
        VALUES (%s, %s, %s, %s)
    """

    name = data.get("Name")
    age = data.get("Instagram_Handle")
    weight = data.get("Origin")
    country = data.get("Gender")

    return execute_sql_query(insert_query, (name, age, weight, country))


# TODO: Test that this works then Remove Once general Function has been created
def add_competition_record(table: str, data) -> tuple:
    insert_query = f"""
        INSERT INTO {table}  (Competition_Date, Competition_Country, Competition_City, Equipment, Age, Weight, Class, Squat, Bench, Deadlift, Total, Dots) VALUES (%s, %s, %s)
    """

    Competition_Date = data.get("Competition_Date")
    Competition_Country = data.get("Competition_Country")
    Competition_City = data.get("Competition_City")
    Equipment = data.get("Equipment")
    Age = data.get("Age")
    Weight = data.get("Weight")
    Class = data.get("Class")
    Squat = data.get("Squat")
    Bench = data.get("Bench")
    Deadlift = data.get("Deadlift")
    Total = data.get("Total")
    Dots = data.get("Dots")

    return execute_sql_query(
        insert_query,
        (
            Competition_Date,
            Competition_Country,
            Competition_City,
            Equipment,
            Age,
            Weight,
            Class,
            Squat,
            Bench,
            Deadlift,
            Total,
            Dots,
        ),
    )


# TODO: Fix This, ensure data and table have same columns
def add_competition_record(table: str, data) -> tuple:
    columns = ", ".join(data.keys())
    values_placeholder = ", ".join(["%s"] * len(data))
    insert_query = f"INSERT INTO {table} ({columns}) VALUES ({values_placeholder})"

    return execute_sql_query(insert_query, tuple(data.values()))


def update_record(table: str, id: int, column: str, value: any) -> tuple:
    sql_query = f"UPDATE {table} SET {column} = {value} WHERE ID = {id}"
    return execute_sql_query(sql_query)


def delete_record(table: str, id: int) -> tuple:
    sql_query = f"DELETE FROM {table }WHERE id = {id};"
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
    units = get_units()
    data = select_record_id(id)
    formated_data = format_data(data, units)
    return jsonify(formated_data)


@app.route("/api/competitor/<int:id>")
def get_competitor_from_id(id: int) -> Response:
    data = select_record_id_single_table(Tables.competitiors.value[0], id)
    formated_data = format_competitor_data(data)
    return jsonify(formated_data)


@app.route("/api/competitor")
def get_range_competitors() -> Response:
    start_index, end_index = get_start_and_end_index()
    data = select_range_data_single_table(
        Tables.competitiors.value[0], start_index, end_index
    )
    formated_data = format_competitor_data(data)
    return jsonify(formated_data)


@app.route("/api/competition/<int:id>")
def get_competition_from_id(id: int) -> Response:
    data = select_record_id_single_table(Tables.competitions.value[0], id)
    units = get_units()
    formated_data = format_competitions_data(data, units)
    return jsonify(formated_data)


@app.route("/api/competition")
def get_range_competitions() -> Response:
    start_index, end_index = get_start_and_end_index()
    units = get_units()
    data = select_range_data_single_table(
        Tables.competitions.value[0], start_index, end_index
    )
    formated_data = format_competitions_data(data, units)
    return jsonify(formated_data)


@app.route("/api/add-competitor", methods=["POST"])
def post_competitor_record() -> Response:
    units = get_units()
    data = add_competitor_record(Tables.competitiors.value[0], request.json)
    formated_data = format_competitor_data(data, units)
    response_data = {"message": "POST request successful!", "data": formated_data}
    return jsonify(response_data)


@app.route("/api/add-competition", methods=["POST"])
def post_competition_record() -> Response:
    units = get_units()
    data = add_competition_record(Tables.competitions.value[0], request.json)
    formated_data = format_competitions_data(data, units)
    response_data = {"message": "POST request successful!", "data": formated_data}
    return jsonify(response_data)


# TODO: Combine delete competitor and delete competition so user cannot just delete one and make database unusable
@app.route("/api/<int:id>/delete-competitor", methods=["DELETE"])
def delete_competitor_record(id) -> Response:
    data = request.json
    delete_record(Tables.competitiors.value[0], id)
    response_data = {"message": "POST request successful!", "data": data}
    return jsonify(response_data)


@app.route("/api/<int:id>/delete-competition", methods=["DELETE"])
def delete_competition_record(id) -> Response:
    data = request.json
    delete_record(Tables.competitions.value[0], id)
    response_data = {"message": "POST request successful!", "data": data}
    return jsonify(response_data)


@app.route("/api/<int:id>/update-competitor", methods=["PUT"])
def update_competitor_record(id) -> Response:
    data = request.json
    column_name, value = get_update_values()
    update_record(Tables.competitiors.value[0], id, column_name, value)
    response_data = {"message": "POST request successful!", "data": data}
    return jsonify(response_data)


@app.route("/api/<int:id>/update-competition", methods=["PUt"])
def update_competition_record(id) -> Response:
    data = request.json
    column_name, value = get_update_values()
    update_record(Tables.competitiors.value[0], id, column_name, value)
    response_data = {"message": "POST request successful!", "data": data}
    return jsonify(response_data)


if __name__ == "__main__":
    app.run(debug=True)
