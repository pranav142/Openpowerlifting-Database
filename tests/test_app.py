import pytest
import requests
from requests import Response

server_url = "http://127.0.0.1:5000"


def create_api_url(endpoint: str, server_url: str = server_url) -> str:
    return server_url + endpoint


def get_api_response(api_url: str) -> Response:
    return requests.get(api_url)


def get_response_from_endpoint(endpoint: str, server_url: str = server_url) -> Response:
    api_url = create_api_url(endpoint, server_url)
    return get_api_response(api_url)


# /api/rankings
def test_get_range_records() -> None:
    endpoint = "/api/rankings"
    response = get_response_from_endpoint(endpoint, server_url)
    print(response.content.decode())


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
