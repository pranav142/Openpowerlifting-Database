import pytest
import sys
import requests
import os
from requests import Response
from dotenv import load_dotenv

from data import MySQL, MySqlInstance, create_db_with_data
from data.db_utils import connect_to_MySQL_instance

load_dotenv("../src/server/.env")

server_url = "http://127.0.0.1:5000"
database_name = "test"
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


def create_api_url(endpoint: str, server_url: str = server_url) -> str:
    return server_url + endpoint


def get_api_response(api_url: str, **kwargs) -> Response:
    return requests.get(api_url, params=kwargs)


def get_response_from_endpoint(
    endpoint: str, server_url: str = server_url, **kwargs
) -> Response:
    api_url = create_api_url(endpoint, server_url)
    return get_api_response(api_url, **kwargs)


# /api/rankings
def test_get_range_records() -> None:
    endpoint = "/api/rankings"

    START = 0
    END = 3
    response = get_response_from_endpoint(endpoint, server_url, start=START, end=END)
    assert response.status_code == 200

    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == END - START + 1


# /api/<int:id>
def test_get_record_from_id() -> None:
    pass


# /api/competitor/<int:id>
def test_get_competitor_from_id() -> None:
    pass


# /api/competitor
def test_get_range_competitors() -> None:
    pass


# /api/competition/<int:id>
def test_get_competition_from_id() -> None:
    pass


# /api/competition
def test_get_range_competitions() -> None:
    pass


# /api/add-competitor
def test_post_competitor_record() -> None:
    pass


# /api/add-competition
def test_post_competition_record() -> None:
    pass


# /api/<int:id>/delete-record
def test_delete_competitor_record() -> None:
    pass


# /api/<int:id>/update-competitor
def test_update_competitor_record() -> None:
    pass


# /api/<int:id>/update-competition
def test_update_competition_record():
    pass


if __name__ == "__main__":
    test_get_range_records()
