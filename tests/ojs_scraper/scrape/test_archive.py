from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup

from ojs_scraper.scrape.archive import ArchiveScraper


@pytest.mark.parametrize(
    ("archive_pages", "expected_links"),
    [
        (
            [
                """
                <a href='test.url/issue/view/123'>...Valid tag...</a>
                <a href='test.url/issue/invalid-url'>...Invalid a tag with /issue/...</a>
                <a href='test.url/invalid-url'>...Invalid a tag without /issue/...</a>
                <a href=''>...Invalid a tag without href...</a>
                """,
                "",
            ],
            ["test.url/issue/view/123"],
        ),
        (
            [
                "<a href='test.url/issue/view/123'>...Valid tag...</a>",
                "<a href='test.url/issue/view/123'>...Valid tag...</a><a href='test.url/issue/view/456'>...Valid tag...</a>",
                "<a href='test.url/issue/view/456'>...Valid tag...</a>",
            ],
            ["test.url/issue/view/123", "test.url/issue/view/456"],
        ),
        (
            [
                "<a href='test.url/issue/view/123'>...Issue 1...</a>",
                "",
            ],
            ["test.url/issue/view/123"],
        ),
        (
            [
                "<a href='test.url/issue/view/123'>...Valid archive page 1...</a>",
                "<a href='test.url/issue/view/456'>...Valid archive page 2...</a>",
                "<a href='test.url/issue/view/789'>...Valid archive page 3...</a>",
                "",
            ],
            [
                "test.url/issue/view/123",
                "test.url/issue/view/456",
                "test.url/issue/view/789",
            ],
        ),
        (
            [
                "<a href='test.url/issue/view/123'>...Valid page 1...</a>",
                "<a href='test.url/issue/view/456'>...Equal Page...</a>",
                "<a href='test.url/issue/view/456'>...Equal Page...</a>",
            ],
            [
                "test.url/issue/view/123",
                "test.url/issue/view/456",
            ],
        ),
        (
            [""],
            [],
        ),
    ],
)
def test_scrape_archive_pages(
    archive_pages: list[str], expected_links: list[str]
) -> None:
    scraper = ArchiveScraper("test.url")
    soups = [BeautifulSoup(page, features="lxml") for page in archive_pages]
    with patch("ojs_scraper.scrape.archive.soupify", side_effect=soups):
        results = scraper.scrape_links_for_issues()
        assert results.sort() == expected_links.sort()
