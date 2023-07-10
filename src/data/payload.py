from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import json
from bs4 import BeautifulSoup


class ServerConnectionStatus(Enum):
    SUCCESSFUL = 200
    NOT_FOUND = 404
    UNAUTHORIZED = 401
    INTERNAL_ERROR = 500


@dataclass
class Payload:
    status: int
    raw_response: str = field(repr=False)
    start: int
    end: int
    content: Optional[dict[str, any]] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        self.content = self._generate_content()

    def _html_parser(self, html: str) -> str:
        return html.body.p.text

    def _convert_html_to_json(self, html: str) -> Optional[dict[str, any]]:
        try:
            raw_data = self._html_parser(html)
            json_data = json.loads(raw_data)
        except Exception as e:
            print(f"Error: {e} for rows {self.start, self.end}")
            json_data = None

        return json_data

    def _generate_content(self) -> Optional[dict[str, any]]:
        html = BeautifulSoup(self.raw_response.text, "lxml")
        return self._convert_html_to_json(html)
