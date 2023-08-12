import pytest
import sys
import requests
import os
from requests import Response
from dotenv import load_dotenv
import json
from server import MySQL, MySqlInstance, create_db_with_data
from server.db_utils import connect_to_MySQL_instance
from server.app_utils import execute_sql_query
from mysql.connector.cursor import MySQLCursor

load_dotenv("../src/server/.env")

server_url = "http://127.0.0.1:8080"
database_name = os.getenv("MY_SQL_DATABASE")
csv_file = "../data/processed/processed_lifting_data.csv"
sql_instance = MySqlInstance(
    host=os.getenv("MY_SQL_HOST"),
    port=os.getenv("MY_SQL_PORT"),
    user=os.getenv("MY_SQL_USER"),
    password=os.getenv("MY_SQL_PASSWORD"),
)
# create_db_with_data(database_name, sql_instance, csv_file)
sql_connection = connect_to_MySQL_instance(sql_instance)
cursor = sql_connection.cursor()
sql_connection.autocommit = True


def create_api_url(endpoint: str, server_url: str = server_url) -> str:
    return server_url + endpoint


def get_api_response(api_url: str, **kwargs) -> Response:
    return requests.get(api_url, params=kwargs)


def post_api(api_url: str, data: dict) -> Response:
    return requests.post(api_url, json=data)


def put_api(api_url: str, data: dict) -> Response:
    return requests.put(api_url, json=data)


def delete_api(api_url: str, **kwargs) -> Response:
    return requests.delete(api_url, params=kwargs)


def get_response_from_endpoint(
    endpoint: str, server_url: str = server_url, **kwargs
) -> Response:
    api_url = create_api_url(endpoint, server_url)
    return get_api_response(api_url, **kwargs)


def post_data_from_endpoint(
    endpoint: str,
    data: dict,
    server_url: str = server_url,
) -> Response:
    api_url = create_api_url(endpoint, server_url)
    return post_api(api_url, data)


def put_data_from_endpoint(
    endpoint: str, data: dict, server_url: str = server_url
) -> Response:
    api_url = create_api_url(endpoint, server_url)
    return put_api(api_url, data)


def delete_data_from_endpoint(endpoint: str, server_url: str, **kwargs) -> Response:
    api_url = create_api_url(endpoint, server_url)
    return delete_api(api_url, **kwargs)


def get_last_record(cursor: MySQLCursor, database_name: str, table_name: str) -> tuple:
    last_record_query = (
        f"SELECT * FROM {database_name}.{table_name} ORDER BY id DESC LIMIT 1"
    )
    cursor.execute(last_record_query)
    return cursor.fetchone()


def get_record_by_id(
    cursor: MySQLCursor, database_name: str, table_name: str, id: int
) -> tuple:
    record_query = f"SELECT * FROM {database_name}.{table_name} WHERE id = {id}"
    cursor.execute(record_query)
    return cursor.fetchall()


# /api/rankings
def test_get_range_records() -> None:
    endpoint = "/api/rankings"

    # Regular Test Case
    START = 1
    END = 3
    response = get_response_from_endpoint(endpoint, server_url, start=START, end=END)
    response_data = response.json()
    assert response.status_code == 200
    assert isinstance(response_data, list)
    assert len(response_data[0]) == END - START + 1
    for i, record in enumerate(response_data[0]):
        assert record.get("ID") == START + i

    # Test Case when Start is Greater Than End
    START = 50
    END = 3
    response = get_response_from_endpoint(endpoint, server_url, start=START, end=END)
    response_data = response.json()
    assert response.status_code == 200
    assert isinstance(response_data, list)
    assert len(response_data[0]) == 1
    assert response_data[0][0].get("ID") == START

    # Test Case Where Start and End are Equal
    START = 5
    END = 5
    response = get_response_from_endpoint(endpoint, server_url, start=START, end=END)
    response_data = response.json()
    assert response.status_code == 200
    assert isinstance(response_data, list)
    assert len(response_data[0]) == 1
    assert response_data[0][0].get("ID") == START

    # Test Case Where End is Bigger than Max Number of Records
    START = 5
    END = 5000000
    response = get_response_from_endpoint(endpoint, server_url, start=START, end=END)
    response_data = response.json()
    assert response.status_code == 200
    assert isinstance(response_data, list)
    assert len(response_data[0]) == 101


def test_get_record_from_id() -> None:
    # Test Case For Valid IDs
    valid_ids = [1, 34489, 240, 4333, 12315, 27381, 1297]
    for id in valid_ids:
        endpoint = f"/api/{id}"
        response = get_response_from_endpoint(endpoint, server_url)
        response_data = response.json()
        assert response.status_code == 200
        assert isinstance(response_data, list)
        assert len(response_data[0]) == 1
        assert response_data[0][0].get("ID") == id

    # Test Case For Invalid IDs
    invalid_ids = [0, 5000000000]
    for id in invalid_ids:
        endpoint = f"/api/{id}"
        response = get_response_from_endpoint(endpoint, server_url)
        response_data = response.json()
        assert response.status_code == 200
        assert isinstance(response_data, list)
        assert len(response_data[0]) == 0


def test_add_record() -> None:
    endpoint = "/api/add-record"

    data = {
        "Name": "John Doe",
        "Instagram_Handle": "John_Doe",
    }
    response = post_data_from_endpoint(endpoint, data, server_url)
    assert response.status_code == 200

    last_record_data = get_last_record(cursor, database_name, "records")
    assert last_record_data is not None
    assert last_record_data[1] == data["Name"]
    assert last_record_data[2] == data["Instagram_Handle"]


def test_update_record() -> None:
    valid_ids = [1, 452, 764]

    data = {"Name": "Testing"}
    for id in valid_ids:
        endpoint = f"/api/{id}/update-record"
        response = put_data_from_endpoint(endpoint, data)
        assert response.status_code == 200
        assert (
            get_record_by_id(cursor, database_name, "records", id)[0][1] == data["Name"]
        )


def test_delete_record() -> None:
    ids = [200, 300, 400]

    for id in ids:
        endpoint = f"/api/{id}/delete-record"
        response = delete_data_from_endpoint(endpoint, server_url)
        assert response.status_code == 200
        assert len(get_record_by_id(cursor, database_name, "records", id)) == 0
