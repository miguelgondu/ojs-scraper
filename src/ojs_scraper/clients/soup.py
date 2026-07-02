import logging
from time import sleep
from urllib.error import URLError
from urllib.parse import urlparse, urlunparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class SoupClient:
    def __init__(self, headers: dict[str, str] | None = None, delay: int | None = None):
        self.headers = headers
        self.delay = delay

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

    def get(self, url: str) -> BeautifulSoup:
        """Returns a BeautifulSoup object from a url."""
        if self.delay is None:
            self.delay = self._compute_delay_from_robots(url)

        response = requests.get(url, verify=False, headers=self.headers)
        logger.info(f"Request to {url}. Sleeping for {self.delay}")
        sleep(self.delay)
        response.raise_for_status()
        return BeautifulSoup(response.content, features="lxml")
