from typing import Protocol

from bs4 import BeautifulSoup


class ClientProtocol(Protocol):
    def get(self, url: str) -> BeautifulSoup: ...
