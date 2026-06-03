import re
from collections.abc import Iterable
from typing import cast

from ojs_scraper.utils.soup import soupify
from ojs_scraper.utils.types import Issue, Link


class IssueScraper:
    def __init__(
        self, issue_url: str, issue_a_tag_for_article__parent: str | None = None
    ) -> None:
        self.issue_url = issue_url
        self.issue: Issue = soupify(issue_url)

        self.issue_a_tag_for_article__parent = (
            issue_a_tag_for_article__parent or "obj_article_summary"
        )

    def scrape_links_for_articles(self) -> Iterable[Link]:
        article_tags = self.issue.select(f".{self.issue_a_tag_for_article__parent}")

        article_view_pattern = r"/article/view/[A-Za-z0-9-_.]+/?$"

        # Extraer los links.
        for article_summary in article_tags:
            link_tags = article_summary.find_all("a")

            for link_tag in link_tags:
                link = cast("str", link_tag.get("href", ""))  # type: ignore

                if link != "" and re.search(article_view_pattern, link):
                    yield link
