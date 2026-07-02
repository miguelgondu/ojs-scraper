from hypothesis import given
from hypothesis import strategies as st

from ojs_scraper.scrape.issue import scrape_issue
from tests.helpers.mocks import MockWithHTMLClient


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

    resulting_links = scrape_issue("test.com", client=MockWithHTMLClient(mock_html))

    assert resulting_links == list(
        {
            f"test.com/{article_id_one}",
            f"test.com/{article_id_two}",
        }
    )


def test_scrape_links_no_articles():
    mock_html = "<div class='obj_article_summary'></div>"
    resulting_links = scrape_issue("test.com", client=MockWithHTMLClient(mock_html))

    assert resulting_links == []
