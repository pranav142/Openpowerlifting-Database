import sys
from bs4 import BeautifulSoup
import pytest
from pytest import MonkeyPatch
import json
from data.payload import Payload


# Test case for successful content generation
def test_payload_content_generation() -> None:
    raw_response = json.dumps({"key": "value"})
    payload = Payload(status=200, raw_response=raw_response, start=1, end=10)

    assert payload.content == {"key": "value"}


# Test case for failed content generation due to invalid Data
def test_payload_content_invalid() -> None:
    raw_response = "Hello_World"
    payload = Payload(status=200, raw_response=raw_response, start=1, end=10)

    assert payload.content is None

    raw_response = "<html><body><p>Invalid JSON</p></body></html>"
    payload = Payload(status=200, raw_response=raw_response, start=1, end=10)

    assert payload.content == None


# Test case for verifying status attribute
def test_payload_status() -> None:
    raw_response = "<html><body><p>{'key': 'value'}</p></body></html>"
    payload = Payload(status=200, raw_response=raw_response, start=1, end=10)

    assert payload.status == 200


# Test case for verifying start and end attributes
def test_payload_start_end_valid() -> None:
    raw_response = "<html><body><p>{'key': 'value'}</p></body></html>"
    payload = Payload(status=200, raw_response=raw_response, start=1, end=10)

    assert payload.start == 1
    assert payload.end == 10


# test case when end is greater than start
def test_payload_start_end_invalid() -> None:
    raw_response = "<html><body><p>{'key': 'value'}</p></body></html>"

    with pytest.raises(AssertionError):
        Payload(status=200, raw_response=raw_response, start=20, end=10)

    with pytest.raises(AssertionError):
        Payload(status=200, raw_response=raw_response, start=-10, end=10)

    with pytest.raises(AssertionError):
        Payload(status=200, raw_response=raw_response, start=-10, end=-10)

    with pytest.raises(AssertionError):
        Payload(status=200, raw_response=raw_response, start=10, end=-10)
