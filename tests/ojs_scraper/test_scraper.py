from unittest.mock import MagicMock, patch
from unittest.mock import patch, mock_open

from ojs_scraper.scraper import Scraper


def make_scraper() -> Scraper:
    config = MagicMock()
    config.archive_url = "test.url"
    scraper = Scraper(archive_config=config, registry=MagicMock())
    return scraper


def test_compute_delay_from_robots_returns_delay() -> None:
    ROBOTS_TXT = """
        User-agent: *
        Crawl-delay: 10
        """
    with patch("urllib.request.urlopen", mock_open(read_data=ROBOTS_TXT.encode())):
        scraper = make_scraper()
    assert scraper.delay == 10


def test_compute_delay_from_robots_defaults_to_5() -> None:
    ROBOTS_TXT = """
        User-agent: *
        """
    with patch("urllib.request.urlopen", mock_open(read_data=ROBOTS_TXT.encode())):
        scraper = make_scraper()
    assert scraper.delay == 5
