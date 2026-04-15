from datetime import datetime
from typing import cast

from bs4 import Tag

from ojs_scraper.models.article import BaseArticle
from ojs_scraper.utils.soup import soupify
from ojs_scraper.utils.constants import PREFERENCE_ORDER
from ojs_scraper.models.article import ArticleFormat


class ArticleScraper:
    def __init__(
        self, article_url: str, article_galley_class: str | None = None
    ) -> None:
        self.article_url = article_url
        self.article_soup = soupify(article_url)

        self.article_galley_class = article_galley_class or "obj_galley_link"

    def extract_metadata(self) -> dict[str, str]:
        """
        Extracts metadata from a BeautifulSoup object.

        Returns a tuple of the article ID and its metadata.
        """

        meta = self.article_soup.find_all("meta", attrs={"name": True})

        metadata = {}
        for item in meta:
            metadata[item["name"]] = item["content"]  # type: ignore

        return metadata

    def _find_tag_with_best_format(
        self, link_tags: list[Tag]
    ) -> tuple[Tag, ArticleFormat]:
        article_tag = None
        article_format = None
        for format_ in PREFERENCE_ORDER:
            candidate_tags = [
                tag for tag in link_tags if format_ in tag.get_text(strip=True).lower()
            ]

            if len(candidate_tags) > 0:
                # We found a link with the desired format.
                # We can return the article object.
                article_tag = candidate_tags[0]
                article_format = format_
                break
        else:
            raise ValueError(
                f"None of the preferred formats {PREFERENCE_ORDER} found in article links. {[tag.get_text(strip=True) for tag in link_tags]}"
            )

        if "href" not in article_tag.attrs:
            article_tag = article_tag.find("a")

        return cast(Tag, article_tag), ArticleFormat(article_format.lower())

    def scrape_article(self) -> BaseArticle:
        raw_metadata = self.extract_metadata()

        link_tags = cast(
            list[Tag],
            self.article_soup.find_all(attrs={"class": f"{self.article_galley_class}"}),
        )

        article_tag, article_format = self._find_tag_with_best_format(link_tags)

        link_to_raw_file = article_tag["href"]

        article = BaseArticle(
            created_at=datetime.now(),
            journal=raw_metadata.get("DC.Source", None)
            or raw_metadata.get("citation_journal_title", ""),
            url=self.article_url,
            parsed=False,
            raw_metadata=raw_metadata,
            format=article_format,
            url_to_raw_file=cast(str, link_to_raw_file),
        )

        return article
