from contextlib import contextmanager
from unittest.mock import patch

from bs4 import BeautifulSoup


@contextmanager
def mock_soupify_with_html(html: str):
    with patch("ojs_scraper.scrape.issue.soupify") as mock_soupify:
        mock_soupify.return_value = BeautifulSoup(html, features="lxml")
        yield mock_soupify
