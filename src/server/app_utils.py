from flask import request
from flask_mysqldb import MySQL
from enum import Enum
from server.tables import columnsCollection

POUNDS_TO_KILOS_COEF = 0.45
POUNDS_TO_POUNDS_COEF = 1


class Units(Enum):
    """Enumeration of units for weight conversion."""

    pounds = ("(lbs)", POUNDS_TO_POUNDS_COEF)
    kilos = ("(kgs)", POUNDS_TO_KILOS_COEF)


def convert_pounds(pounds: int, desired_units: Units, precision: int = 3) -> float:
    """Convert weight in pounds to desired units with specified precision.

    Args:
        pounds (int): Weight in pounds.
        desired_units (Units): Desired units for conversion.
        precision (int, optional): Precision of the result. Defaults to 3.

    Returns:
        float: Weight converted to the desired units.
    """
    if pounds is None:
        return None
    return round(pounds * desired_units.value[1], precision)


def format_data(row: list, columns_collection: columnsCollection, units: Units) -> dict:
    """Format row data with appropriate units and labels.

    Args:
        row (list): Row data from a response.
        columns_collection (columnsCollection): Collection of columns' metadata.
        units (Units): Units for weight conversion.

    Returns:
        dict: Formatted data with units and labels.
    """
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
    """Format a response data tuple with appropriate units and labels.

    Args:
        data (tuple): Response data tuple.
        units (Units): Units for weight conversion.
        columns_collection (columnsCollection): Collection of columns' metadata.

    Returns:
        dict: Formatted response data with units and labels.
    """
    formated_data = []
    for row in data:
        formated_data.append(format_data(row, columns_collection, units))
    return formated_data


def execute_sql_query(
    query: str, sql_connection: MySQL, additional_params: tuple = None
) -> tuple:
    """Execute an SQL query and return the fetched data.

    Args:
        query (str): SQL query to execute.
        sql_connection (MySQL): MySQL connection object.
        additional_params (tuple, optional): Additional parameters for the query. Defaults to None.

    Returns:
        tuple: Fetched data from the query.
    """
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
    """Generate an SQL query for selecting a range of records.

    Args:
        start_index (int): Starting index of the range.
        end_index (int): Ending index of the range.
        table_name (str): Name of the table to query.

    Returns:
        str: SQL query to select records within the specified range.
    """
    sql_query = f"SELECT * FROM {table_name} WHERE {table_name}.id BETWEEN {start_index} AND {end_index}"
    return sql_query


def select_range_data(
    start_index: int,
    end_index: int,
    table_name: str,
    sql_connection: MySQL,
    max: int = 100,
) -> list:
    """Select a range of data records from a table.

    Args:
        start_index (int): Starting index of the range.
        end_index (int): Ending index of the range.
        table_name (str): Name of the table to query.
        sql_connection (MySQL): MySQL connection object.
        max (int, optional): Maximum number of records to retrieve. Defaults to 100.

    Returns:
        list: List of data records within the specified range.
    """
    if end_index - start_index > max:
        end_index = start_index + max
    if start_index > end_index:
        end_index = start_index
    sql_query = generate_select_range_query(start_index, end_index, table_name)
    return execute_sql_query(query=sql_query, sql_connection=sql_connection)


def select_record_id(id: int, table_name: str, sql_connection: MySQL) -> tuple:
    """Select a record by its ID from a table.

    Args:
        id (int): ID of the record to select.
        table_name (str): Name of the table to query.
        sql_connection (MySQL): MySQL connection object.

    Returns:
        tuple: Tuple containing the selected record data.
    """
    sql_query = f"SELECT * FROM {table_name} WHERE {table_name}.ID = %s"
    return execute_sql_query(
        query=sql_query, additional_params=(id,), sql_connection=sql_connection
    )


def add_record(data: dict, table: str, columns: list, sql_connection: MySQL) -> tuple:
    """Add a new record to a table.

    Args:
        data (dict): Data for the new record.
        table (str): Name of the table to add the record to.
        columns (list): List of column names for the record.
        sql_connection (MySQL): MySQL connection object.

    Returns:
        tuple: Tuple containing the result of the record addition operation.
    """
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
    """Update a record in the specified table.

    Args:
        table (str): Name of the table to update the record in.
        id (int): ID of the record to update.
        data (dict): Updated data for the record.
        sql_connection (MySQL): MySQL connection object.

    Returns:
        tuple: Tuple containing the result of the record update operation.
    """
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
    """Delete a record from the specified table.

    Args:
        table (str): Name of the table to delete the record from.
        id (int): ID of the record to delete.
        sql_connection (MySQL): MySQL connection object.

    Returns:
        tuple: Tuple containing the result of the record deletion operation.
    """
    sql_query = f"DELETE FROM {table} WHERE id = {id};"
    return execute_sql_query(query=sql_query, sql_connection=sql_connection)


def get_update_values() -> tuple[str, any]:
    """Get column and value parameters for record updates.

    Returns:
        tuple[str, any]: Tuple containing the column name and the new value.
    """
    column = request.args.get("column")
    value = request.args.get("value")
    return column, value


def get_units() -> Units:
    """Get the desired units for weight conversion.

    Returns:
        Units: The desired units for weight conversion.
    """
    unit_param = request.args.get("units", "pounds")
    return Units[unit_param.lower()]


def get_start_and_end_index() -> tuple[int, int]:
    """Get start and end indices for data selection.

    Returns:
        tuple[int, int]: Tuple containing the start and end indices.
    """
    start_index = int(request.args.get("start", 0))
    end_index = int(request.args.get("end", 10))
    return start_index, end_index


def get_column_to_order_by() -> str:
    """Get the column name for ordering data.

    Returns:
        str: The column name to use for data ordering.
    """
    return request.args.get("orderby", "id")
