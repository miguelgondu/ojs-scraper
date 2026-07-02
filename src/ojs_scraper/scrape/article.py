import re
from datetime import datetime
from typing import cast

from bs4 import BeautifulSoup, Tag

from ojs_scraper.clients import ClientProtocol, SoupClient
from ojs_scraper.models.article import ArticleFormat, BaseArticle

PREFERENCE_ORDER = ["xml", "html", "pdf"]


def _extract_metadata(article_soup: BeautifulSoup) -> dict[str, str]:
    meta = article_soup.find_all("meta", attrs={"name": True})

    metadata = {}
    for item in meta:
        metadata[item["name"]] = item["content"]  # type: ignore

    return metadata


def _find_tag_with_best_format(link_tags: list[Tag]) -> tuple[Tag, ArticleFormat]:
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
            f"None of the preferred formats {PREFERENCE_ORDER} found in article "
            f"links. {[tag.get_text(strip=True) for tag in link_tags]}"
        )

    if "href" not in article_tag.attrs:
        article_tag = article_tag.find("a")

    return cast("Tag", article_tag), ArticleFormat(article_format.lower())


def scrape_article(
    article_url: str,
    *,
    article_content_pattern: re.Pattern = re.compile(
        r"/article/view/[A-Za-z0-9-_.]+/[A-Za-z0-9-_.]+/?$"
    ),
    client: ClientProtocol = SoupClient(),
) -> BaseArticle:
    article_soup = client.get(article_url)
    raw_metadata = _extract_metadata(article_soup)

    link_tags = cast(
        "list[Tag]",
        article_soup.find_all("a", href=article_content_pattern),  # type: ignore
    )

    article_tag, article_format = _find_tag_with_best_format(link_tags)

    link_to_raw_file = article_tag["href"]

    return BaseArticle(
        created_at=datetime.now(),
        journal=raw_metadata.get("DC.Source", None)
        or raw_metadata.get("citation_journal_title", ""),
        url=article_url,
        parsed=False,
        raw_metadata=raw_metadata,
        format=article_format,
        url_to_raw_file=cast("str", link_to_raw_file),
    )
