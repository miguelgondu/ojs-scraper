import pytest
from unittest.mock import patch

from bs4 import BeautifulSoup
from ojs_scraper.scrape.article import ArticleScraper
from ojs_scraper.models.article import BaseArticle, ArticleFormat


def get_mock_scraper(
    minimal_html: str, article_galley_class: str | None = None
) -> ArticleScraper:

    with patch("ojs_scraper.scrape.article.soupify") as mock_soupify:
        mock_soupify.return_value = BeautifulSoup(minimal_html, features="lxml")

        scraper = ArticleScraper(
            article_url="test.url", article_galley_class=article_galley_class
        )

        return scraper


def test_scraper_with_default_article_galley_class() -> None:
    minimal_html = """
        <a class='obj_galley_link'>Correct Tag</a>
        <a class='test_galley_class'>Invalid Tag</a>
    """
    scraper = get_mock_scraper(minimal_html, article_galley_class=None)
    test_tag = scraper.article_soup.find(
        attrs={"class": f"{scraper.article_galley_class}"}
    )

    assert test_tag.text == "Correct Tag"


def test_scraper_with_custom_article_galley_class() -> None:
    minimal_html = """
        <a class='obj_galley_link'>PDF</a>
        <a class='test_galley_class'>Test Tag</a>
    """
    scraper = get_mock_scraper(minimal_html, article_galley_class="test_galley_class")
    test_tag = scraper.article_soup.find(
        attrs={"class": f"{scraper.article_galley_class}"}
    )

    assert test_tag.text == "Test Tag"


def test_extract_metadata() -> None:
    minimal_html = """
        <meta name="DC.Source" content="Test Journal"/>
        <meta name="citation_journal_title" content="Test Journal - Fallback Meta Tag"/>
        <meta name="DC.Title" content="Test Article Title"/>
        <meta content="Meta Tag with no name"/>
    """
    scraper = get_mock_scraper(minimal_html)
    metadata = scraper.extract_metadata()

    assert metadata == {
        "DC.Source": "Test Journal",
        "citation_journal_title": "Test Journal - Fallback Meta Tag",
        "DC.Title": "Test Article Title",
    }


@pytest.mark.parametrize(
    ("minimal_html", "expected_format"),
    [
        (
            """
        <a class="obj_galley_link pdf" href="Test Link">PDF</a>
        <a class="obj_galley_link html" href="Test Link">HTML</a>
        <a class="obj_galley_link xml" href="Test Link">XML</a>
        """,
            ArticleFormat.XML,
        ),
        (
            """
        <a class="obj_galley_link pdf" href="Test Link">PDF</a>
        <a class="obj_galley_link html" href="Test Link">HTML</a>
        """,
            ArticleFormat.HTML,
        ),
        (
            """
        <a class="obj_galley_link pdf" href="Test Link">PDF</a>
        """,
            ArticleFormat.PDF,
        ),
    ],
)
def test__find_tag_with_best_format_pick_expected_value(
    minimal_html: str, expected_format: ArticleFormat
) -> None:
    scraper = get_mock_scraper(minimal_html)
    link_tags = scraper.article_soup.find_all(
        attrs={"class": f"{scraper.article_galley_class}"}
    )

    best_tag = scraper._find_tag_with_best_format(link_tags)

    assert best_tag[1] == expected_format


def test__find_tag_with_best_format_if_a_tag_is_contained_in_div() -> None:
    minimal_html = """
    '<div class="obj_galley_link">
        <a href="TARGET A TAG">PDF</a>
    </div>
    """
    scraper = get_mock_scraper(minimal_html)
    link_tags = scraper.article_soup.find_all(
        attrs={"class": f"{scraper.article_galley_class}"}
    )

    selected_tag, _ = scraper._find_tag_with_best_format(link_tags)

    assert selected_tag.get("href") == "TARGET A TAG"


def test__find_tag_with_best_format_raise_error_for_not_found() -> None:
    minimal_html = '<a class="obj_galley_link" href="Test Link">Invalid Format</a>'
    scraper = get_mock_scraper(minimal_html)
    link_tags = scraper.article_soup.find_all(
        attrs={"class": f"{scraper.article_galley_class}"}
    )

    with pytest.raises(ValueError):
        scraper._find_tag_with_best_format(link_tags)


def test_scrape_article_with_dc_source_metadata():
    minimal_html = """
    <html>
        <head>
            <meta name="DC.Source" content="Test Journal"/>
            <meta name="citation_journal_title" content="Test Journal - Fallback Meta Tag"/>
            <meta name="DC.Title" content="Test Article Title"/>
            <meta content="Meta Tag with no name"/>
            </head>
        <body>
            <a class="obj_galley_link pdf" href="Test Link">PDF</a>
        </body>
    </html>
    """
    scraper = get_mock_scraper(minimal_html)
    article = scraper.scrape_article()
    assert isinstance(article, BaseArticle)
    assert article.journal == "Test Journal"
    assert article.url == "test.url"
    assert article.format == ArticleFormat.PDF
    assert article.url_to_raw_file == "Test Link"


def test_scrape_article_with_citation_journal_metadata():
    minimal_html = """
    <html>
        <head>
            <meta name="citation_journal_title" content="Test Journal - Fallback Meta Tag"/>
            <meta name="DC.Title" content="Test Article Title"/>
            <meta content="Meta Tag with no name"/>
            </head>
        <body>
            <a class="obj_galley_link pdf" href="Test Link">PDF</a>
        </body>
    </html>
    """
    scraper = get_mock_scraper(minimal_html)
    article = scraper.scrape_article()
    assert isinstance(article, BaseArticle)
    assert article.journal == "Test Journal - Fallback Meta Tag"
    assert article.url == "test.url"
    assert article.format == ArticleFormat.PDF
    assert article.url_to_raw_file == "Test Link"
