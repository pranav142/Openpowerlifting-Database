from flask import request
from flask_mysqldb import MySQL
from enum import Enum
from tables import columnsCollection

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
    query: str, sql_connection: MySQL, additional_params: tuple = None
) -> tuple:
    cur = sql_connection.connection.cursor()
    if additional_params is None:
        cur.execute(query)
    else:
        cur.execute(query, additional_params)
    data = cur.fetchall()
    sql_connection.connection.commit()
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
    sql_connection: MySQL,
    max: int = 100,
) -> list:
    if end_index - start_index > max:
        end_index = start_index + max
    if start_index > end_index:
        end_index = start_index
    sql_query = generate_select_range_query(start_index, end_index, table_name)
    return execute_sql_query(query=sql_query, sql_connection=sql_connection)


def select_record_id(id: int, table_name: str, sql_connection: MySQL) -> tuple:
    sql_query = f"SELECT * FROM {table_name} WHERE {table_name}.ID = %s"
    return execute_sql_query(
        query=sql_query, additional_params=(id,), sql_connection=sql_connection
    )


def add_record(data, table: str, columns: list, sql_connection: MySQL) -> tuple:
    if "ID" in columns:
        columns.remove("ID")
    insert_query = f"""INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['%s']*len(columns))})"""

    values = []
    for column in columns:
        values.append(data.get(column))

    return execute_sql_query(
        query=insert_query,
        additional_params=tuple(values),
        sql_connection=sql_connection,
    )


def update_record(table: str, id: int, data, sql_connection: MySQL) -> tuple:
    update_values = ", ".join([f"{column} = %s" for column in data.keys()])
    sql_query = f"UPDATE {table} SET {update_values} WHERE ID = %s"

    values = list(data.values())
    values.append(id)

    return execute_sql_query(
        query=sql_query,
        additional_params=tuple(values),
        sql_connection=sql_connection,
    )


def delete_record(table: str, id: int, sql_connection: MySQL) -> tuple:
    sql_query = f"DELETE FROM {table} WHERE id = {id};"
    return execute_sql_query(query=sql_query, sql_connection=sql_connection)


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
