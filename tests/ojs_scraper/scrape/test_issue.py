from unittest.mock import patch

from bs4 import BeautifulSoup
from hypothesis import given
from hypothesis import strategies as st

from ojs_scraper.scrape.issue import IssueScraper


def get_mock_scraper(
    mock_html: str, issue_a_tag_for_article__parent: str | None = None
) -> IssueScraper:
    with patch("ojs_scraper.scrape.issue.soupify") as mock_soupify:
        mock_soupify.return_value = BeautifulSoup(mock_html, features="lxml")

        return IssueScraper(
            issue_url="test.url",
            issue_a_tag_for_article__parent=issue_a_tag_for_article__parent,
        )


def get_mock_html(
    article_id_one: str,
    article_id_two: str,
    issue_a_tag_for_article__parent: str = "obj_article_summary",
) -> str:
    return f"""
    <div class="{issue_a_tag_for_article__parent}">
        <a href="test.com/{article_id_one}">Article Title 1</a>
    </div>
    <div class="{issue_a_tag_for_article__parent}">
        <a href="test.com/{article_id_two}">Article Title 2</a>
    </div>
    <div class="invalid_parent_class">
        <a href="test.com/{article_id_one}">Ignore this article</a>
    </div>
    <div class="{issue_a_tag_for_article__parent}">
        <a href="test.com/invalid_url/">Ignore this article</a>
    </div>
    <div class="{issue_a_tag_for_article__parent}">
        <a href="" id="link-without-href">Ignore this article</a>
    </div>
    <div class="{issue_a_tag_for_article__parent}">
        <span id="not-an-a-tag">Ignore this article</a>
    </div>
    """


regex_strategy = st.from_regex("article/view/[A-Za-z0-9-_.]+/?", fullmatch=True)


@given(regex_strategy, regex_strategy)
def test_scrape_links_for_articles_default_tag(
    article_id_one: str, article_id_two: str
) -> None:
    mock_html = get_mock_html(article_id_one, article_id_two)

    scraper = get_mock_scraper(mock_html)
    resulting_links = list(scraper.scrape_links_for_articles())

    assert resulting_links == [
        f"test.com/{article_id_one}",
        f"test.com/{article_id_two}",
    ]


@given(regex_strategy, regex_strategy)
def test_scrape_links_for_articles_custom_tag(
    article_id_one: str, article_id_two: str
) -> None:
    custom_class = "custom_class"
    mock_html = get_mock_html(
        article_id_one, article_id_two, issue_a_tag_for_article__parent=custom_class
    )

    scraper = get_mock_scraper(mock_html, custom_class)
    resulting_links = list(scraper.scrape_links_for_articles())

    assert resulting_links == [
        f"test.com/{article_id_one}",
        f"test.com/{article_id_two}",
    ]


def test_scrape_links_no_articles():
    scraper = get_mock_scraper("<div class='obj_article_summary'></div>")
    assert list(scraper.scrape_links_for_articles()) == []
