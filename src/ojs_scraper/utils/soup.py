import logging
from time import sleep
from warnings import filterwarnings

import requests
from bs4 import BeautifulSoup

# Headers for requests
DEFAULT_HEADERS = {
    "User-Agent": "LatinAmericanPhilosophyMiningBot/1.0 (jloaiza@uahurtado.cl, "
    "miguelgondu@gmail.com, nicolas.duque@ucaldas.edu.co)",
}

logger = logging.getLogger(__name__)

# Ignore SSL warnings
filterwarnings("ignore", message="Unverified HTTPS request is being made to host")


def soupify(url: str, retries: int = 5, sleep_time_seconds: int = 2) -> BeautifulSoup:
    """Returns a BeautifulSoup object from a url."""
    for _ in range(retries):
        try:
            response = requests.get(url, verify=False, headers=DEFAULT_HEADERS)
            response.raise_for_status()
            return BeautifulSoup(response.content, features="lxml")
        except requests.RequestException as e:
            logger.warning(f"Request to {url} failed: {e}. Retrying...")
            sleep(sleep_time_seconds)

    return BeautifulSoup(response.content, features="lxml")
