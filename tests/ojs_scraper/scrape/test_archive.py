from unittest.mock import patch

from bs4 import BeautifulSoup

from ojs_scraper.scrape.archive import ArchiveScraper


def make_soup_for_all_pages(pages: list[str]) -> list[BeautifulSoup]:
    return [BeautifulSoup(page, features="lxml") for page in pages]


def make_scraper(
    a_tag_for_issue__child: str | None = "issue_tag_child",
) -> ArchiveScraper:
    return ArchiveScraper("test.url", "issue_tag_parent", a_tag_for_issue__child)


def test__fetch_all_archive_pages_one_valid_page() -> None:
    pages = ["<div class='issue_tag_parent'>...Valid page...</div>", ""]
    scraper = make_scraper()
    soups = make_soup_for_all_pages(pages)
    with patch("ojs_scraper.scrape.archive.soupify", side_effect=soups):
        results = list(scraper._fetch_all_archive_pages())
        assert results == ["test.url/1"]


def test__fetch_all_archive_pages_multiple_valid_pages() -> None:
    pages = [
        "<div class='issue_tag_parent'>...Valid page 1...</div>",
        "<div class='issue_tag_parent'>...Valid page 2...</div>",
        "<div class='issue_tag_parent'>...Valid page 3...</div>",
        "",
    ]
    scraper = make_scraper()
    soups = make_soup_for_all_pages(pages)
    with patch("ojs_scraper.scrape.archive.soupify", side_effect=soups):
        results = list(scraper._fetch_all_archive_pages())
        assert results == ["test.url/1", "test.url/2", "test.url/3"]


def test__fetch_all_archive_pages_stop_when_two_equal() -> None:
    pages = [
        "<div class='issue_tag_parent'>...Valid page 1...</div>",
        "<div class='issue_tag_parent'>...Valid page 2...</div>",
        "<div class='issue_tag_parent'>...Valid page 2...</div>",
    ]
    scraper = make_scraper()
    soups = make_soup_for_all_pages(pages)
    with patch("ojs_scraper.scrape.archive.soupify", side_effect=soups):
        results = list(scraper._fetch_all_archive_pages())
        assert results == ["test.url/1", "test.url/2"]


def test__fetch_all_archive_pages_no_valid_pages() -> None:
    pages = [""]
    scraper = make_scraper()
    soups = make_soup_for_all_pages(pages)
    with patch("ojs_scraper.scrape.archive.soupify", side_effect=soups):
        results = list(scraper._fetch_all_archive_pages())
        assert results == []


def test__extract_issues_from_archive_page_with_child_tag() -> None:
    html = """
        <div class="issue_tag_parent">
            <a class="issue_tag_child" href="link-to-issue-1">Issue Title 1</a>
        </div>
        <div class="issue_tag_parent">
            <a class="issue_tag_child" href="link-to-issue-2">Issue Title 2</a>
        </div>
        <div class="invalid_tag">
            <a class="issue_tag_child" href="link-to-issue-3">Ignore this issue</a>
        </div>
        """
    scraper = make_scraper()
    soup = BeautifulSoup(html, features="lxml")
    results = list(scraper._extract_issues_from_archive_page(soup))

    assert results == ["link-to-issue-1", "link-to-issue-2"]


def test__extract_issues_from_archive_page_without_child_tag() -> None:
    html = """
        <div class="issue_tag_parent">
            <a href="link-to-issue-1">Issue Title 1</a>
        </div>
        <div class="issue_tag_parent">
            <a href="link-to-issue-2">Issue Title 2</a>
        </div>
        <div class="invalid_tag">
            <a href="link-to-issue-3">Ignore this issue</a>
        </div>
        """
    soup = BeautifulSoup(html, features="lxml")
    scraper = make_scraper(a_tag_for_issue__child=None)
    results = list(scraper._extract_issues_from_archive_page(soup))

    assert results == ["link-to-issue-1", "link-to-issue-2"]


# Note: There is no test_scrape_links_for_issues because it just
# combines the other private methods in the class we already
# tested.
