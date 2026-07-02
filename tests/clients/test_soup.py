from unittest.mock import MagicMock, mock_open, patch

from ojs_scraper.clients.soup import SoupClient


def make_client() -> SoupClient:
    config = MagicMock()
    config.archive_url = "test.url"
    return SoupClient()


def test_delay_is_none_at_init() -> None:
    client = SoupClient()
    assert client.delay is None


def test_compute_delay_from_robots_returns_delay() -> None:
    ROBOTS_TXT = """
        User-agent: *
        Crawl-delay: 10
        """
    client = SoupClient()
    with patch("urllib.request.urlopen", mock_open(read_data=ROBOTS_TXT.encode())):
        delay = client._compute_delay_from_robots("...")

    assert delay == 10


def test_compute_delay_from_robots_defaults_to_5() -> None:
    ROBOTS_TXT = """
        User-agent: *
        """
    client = SoupClient()
    with patch("urllib.request.urlopen", mock_open(read_data=ROBOTS_TXT.encode())):
        delay = client._compute_delay_from_robots("...")

    assert delay == 5
