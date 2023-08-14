from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import json
from bs4 import BeautifulSoup


class ServerConnectionStatus(Enum):
    """An enumeration of server connection status codes."""

    SUCCESSFUL = 200
    NOT_FOUND = 404
    UNAUTHORIZED = 401
    INTERNAL_ERROR = 500


@dataclass
class Payload:
    """A class representing a payload from a server response.

    This class holds information about the server response, including its status,
    raw response content, start and end indices, and parsed content if applicable.

    Attributes:
        status (int): The status code of the server response.
        raw_response (str): The raw response content.
        start (int): The start index of the payload.
        end (int): The end index of the payload.
        content (Optional[dict[str, any]]): Parsed content of the response.
    """

    status: int
    raw_response: str = field(repr=False)
    start: int
    end: int
    content: Optional[dict[str, any]] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        """Perform post-initialization validation and content generation."""
        assert (
            self.start >= 0 and self.end >= 0
        ), "ensure start and end are greater than 0"
        assert self.start <= self.end, "ensure start is less than end"
        self.content = self._generate_content()

    def _html_parser(self, html: str) -> str:
        """Parse HTML content and return the text of the first <p> tag.

        Args:
            html (str): HTML content.

        Returns:
            str: Text content of the first <p> tag.
        """
        return html.body.p.text

    def _convert_html_to_json(self, html: str) -> Optional[dict[str, any]]:
        """Convert HTML content to a JSON-like dictionary.

        Args:
            html (str): HTML content.

        Returns:
            Optional[dict[str, any]]: JSON-like dictionary converted from HTML.
        """
        try:
            raw_data = self._html_parser(html)
            json_data = json.loads(raw_data)
        except Exception as e:
            print(f"Error: {e} for rows {self.start, self.end}")
            json_data = None

        return json_data

    def _generate_content(self) -> Optional[dict[str, any]]:
        """Generate parsed content from the raw_response.

        Returns:
            Optional[dict[str, any]]: Parsed content of the response.
        """
        html = BeautifulSoup(self.raw_response, "lxml")
        return self._convert_html_to_json(html)
