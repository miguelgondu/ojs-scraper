"""Unit tests for article."""

# ruff: noqa: E501
from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup

from ojs_scraper.models.article import Article, ArticleFormat
from ojs_scraper.scrape.article import scrape_article
from tests.helpers.mocks import MockWithHTMLClient

DEFAULT_TEST_ARTICLE_URL = "test.url/journal/article/view/article123"


def scrape_article_with_mock_soupify(minimal_html: str):
    with patch("ojs_scraper.scrape.article.soupify") as mock_soupify:
        mock_soupify.return_value = BeautifulSoup(minimal_html, features="lxml")
        return scrape_article(DEFAULT_TEST_ARTICLE_URL)


def test_scrape_article_select_only_tags_with_valid_href() -> None:
    minimal_html = """
        <a href="/article/view/123/article123/">PDF</a>
        <a href="" incorrect>PDF</a>
        <a href="/wrong/pattern/" incorrect>PDF</a>
    """
    result_article = scrape_article(
        DEFAULT_TEST_ARTICLE_URL, client=MockWithHTMLClient(minimal_html)
    )
    assert result_article.format == ArticleFormat.PDF


def test_scrape_article_correct_metadata() -> None:
    minimal_html = f"""
        <head>
        <meta name="DC.Source" content="Test Journal"/>
        <meta name="citation_journal_title" content="Test Journal - Fallback Meta Tag"/>
        <meta name="DC.Title" content="Test Article Title"/>
        <meta content="Meta Tag with no name"/>
        </head>
        <body>
            <a href="{DEFAULT_TEST_ARTICLE_URL}/file123">PDF</a>
        </body>
    """
    result_article = scrape_article(
        DEFAULT_TEST_ARTICLE_URL, client=MockWithHTMLClient(minimal_html)
    )

    assert result_article.raw_metadata == {
        "DC.Source": "Test Journal",
        "citation_journal_title": "Test Journal - Fallback Meta Tag",
        "DC.Title": "Test Article Title",
    }


@pytest.mark.parametrize(
    ("minimal_html", "expected_format"),
    [
        (
            """
        <a href="/article/view/123/article123/">PDF</a>
        <a href="/article/view/123/article456/">HTML</a>
        <a href="/article/view/123/article789/">XML</a>
        """,
            ArticleFormat.XML,
        ),
        (
            """
        <a href="/article/view/123/article123/">PDF</a>
        <a href="/article/view/123/article456/">HTML</a>
        """,
            ArticleFormat.HTML,
        ),
        (
            """
        <a href="/article/view/123/article123/">PDF</a>
        """,
            ArticleFormat.PDF,
        ),
    ],
)
def test_scrape_article_with_best_format(
    minimal_html: str, expected_format: ArticleFormat
) -> None:
    result_article = scrape_article(
        DEFAULT_TEST_ARTICLE_URL, client=MockWithHTMLClient(minimal_html)
    )
    assert result_article.format == expected_format


def test_scrape_article_raise_error_if_no_format_found() -> None:
    minimal_html = '<a href="/article/view/123/article123/">Invalid Format</a>'
    with pytest.raises(ValueError):
        scrape_article(
            DEFAULT_TEST_ARTICLE_URL, client=MockWithHTMLClient(minimal_html)
        )


def test_scrape_article_with_dc_source_metadata():
    raw_file_url = f"{DEFAULT_TEST_ARTICLE_URL}/file123/"
    minimal_html = f"""
    <html>
        <head>
            <meta name="DC.Source" content="Test Journal"/>
            <meta name="citation_journal_title" content="Test Journal - Fallback Meta Tag"/>
            <meta name="DC.Title" content="Test Article Title"/>
            <meta content="Meta Tag with no name"/>
            </head>
        <body>
            <a href="{raw_file_url}">PDF</a>
        </body>
    </html>
    """
    result_article = scrape_article(
        DEFAULT_TEST_ARTICLE_URL, client=MockWithHTMLClient(minimal_html)
    )
    assert isinstance(result_article, Article)
    assert result_article.journal == "Test Journal"
    assert result_article.url == DEFAULT_TEST_ARTICLE_URL
    assert result_article.format == ArticleFormat.PDF
    assert result_article.url_to_raw_file == raw_file_url


def test_scrape_article_with_citation_journal_metadata():
    raw_file_url = f"{DEFAULT_TEST_ARTICLE_URL}/file123/"
    minimal_html = f"""
    <html>
        <head>
            <meta name="citation_journal_title" content="Test Journal - Fallback Meta Tag"/>
            <meta name="DC.Title" content="Test Article Title"/>
            <meta content="Meta Tag with no name"/>
            </head>
        <body>
            <a href="{raw_file_url}">PDF</a>
        </body>
    </html>
    """
    result_article = scrape_article(
        DEFAULT_TEST_ARTICLE_URL, client=MockWithHTMLClient(minimal_html)
    )

    assert isinstance(result_article, Article)
    assert result_article.journal == "Test Journal - Fallback Meta Tag"
    assert result_article.url == DEFAULT_TEST_ARTICLE_URL
    assert result_article.format == ArticleFormat.PDF
    assert result_article.url_to_raw_file == raw_file_url
