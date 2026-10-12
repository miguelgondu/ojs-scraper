import logging
from time import sleep
from urllib.error import URLError
from urllib.parse import urlparse, urlunparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class SoupClient:
    def __init__(
        self,
        headers: dict[str, str] | None = None,
        delay: int | None = None,
        retries: int = 3,
    ):
        self.headers = headers
        self.delay = delay
        self.retries = retries

    def _compute_delay_from_robots(self, url: str) -> int:
        parsed_url = urlparse(url)
        robots_url = urlunparse(
            (
                "https",
                parsed_url.netloc,
                "robots.txt",
                "",
                "",
                "",
            )
        )

        try:
            robot_parser = RobotFileParser(robots_url)
            robot_parser.read()
        except URLError:
            robot_parser = RobotFileParser(robots_url.replace("https", "http"))
            robot_parser.read()

        # Default to 5 seconds if not specified
        crawl_delay = int(robot_parser.crawl_delay("*") or 5)
        logger.info("Scraping with a delay of %s", crawl_delay)

        return crawl_delay

    def _get(self, url: str) -> requests.Response:
        """Returns a BeautifulSoup object from a url."""
        if self.delay is None:
            self.delay = self._compute_delay_from_robots(url)

        logger.info(f"Request to {url}. Sleeping for {self.delay}")
        sleep(self.delay)
        return requests.get(url, verify=False, headers=self.headers)

    def get(self, url: str) -> BeautifulSoup | None:
        for _ in range(self.retries):
            response = self._get(url)

            if 200 <= response.status_code < 300:
                return BeautifulSoup(response.content, features="lxml")

            if 400 <= response.status_code < 500:
                logger.warning(
                    "Client error: Visiting page %s rendered status code %s",
                    url,
                    response.status_code,
                )
                break

            if 500 <= response.status_code < 600:
                logger.warning(
                    "Server error: Visiting page %s rendered status code %s",
                    url,
                    response.status_code,
                )
                continue

        return None
