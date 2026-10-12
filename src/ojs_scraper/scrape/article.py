import re
from datetime import datetime
from typing import cast

from bs4 import BeautifulSoup, Tag

from ojs_scraper.clients import ClientProtocol, SoupClient
from ojs_scraper.exceptions import ScrapingException
from ojs_scraper.models.article import Article, ArticleFormat
from ojs_scraper.models.metadata import ArticleRawMetadata, Metadata

PREFERENCE_ORDER = ["xml", "html", "pdf"]


def _extract_metadata(article_soup: BeautifulSoup) -> ArticleRawMetadata:
    meta = article_soup.find_all("meta", attrs={"name": True, "content": True})

    return [(item["name"], item["content"]) for item in meta]  # type: ignore


def _find_tag_and_formats(link_tags: list[Tag]) -> dict[ArticleFormat, Tag]:
    format_to_tag = {}
    for format_ in ArticleFormat:
        candidate_tags = [
            tag for tag in link_tags if format_ in tag.get_text(strip=True).lower()
        ]
        if len(candidate_tags) > 0:
            format_to_tag[format_] = candidate_tags[0]

    return format_to_tag


def _find_download_links_for_pdf(soup: BeautifulSoup) -> list[str]:
    a_download_links = [
        cast("str", a.get("href"))
        for a in soup.find_all("a", href=re.compile(r"/article/download/.+"))
    ]
    iframe_download_links = [
        cast("str", iframe.get("src")).strip()
        for iframe in soup.find_all("iframe", src=re.compile(r"/article/download/.+"))
    ]

    return a_download_links if len(a_download_links) > 0 else iframe_download_links


def _compute_download_link_for_html_and_xml(link: str) -> str:
    return link.replace("/view/", "/download/")


def scrape_article(
    article_url: str,
    *,
    article_content_pattern: re.Pattern = re.compile(
        r"/article/view/[A-Za-z0-9-_.]+/[A-Za-z0-9-_.]+/?$"
    ),
    client: ClientProtocol = SoupClient(),
) -> Article:
    article_soup = client.get(article_url)
    if article_soup is None:
        raise ScrapingException(f"Could not visit {article_url}.")

    raw_metadata = _extract_metadata(article_soup)

    link_tags = cast(
        "list[Tag]",
        article_soup.find_all("a", href=article_content_pattern),  # type: ignore
    )

    url_to_raw_files = {}
    for format, article_tag in _find_tag_and_formats(link_tags).items():
        link_to_file = cast("str", article_tag["href"])

        if format in {ArticleFormat.HTML, ArticleFormat.XML}:
            download_links = [_compute_download_link_for_html_and_xml(link_to_file)]
        else:
            soup = client.get(link_to_file)
            if soup is None:
                raise ScrapingException(
                    f"Could not visit download link for pdf: {link_to_file}."
                )

            download_links = _find_download_links_for_pdf(soup)

        if len(download_links) < 1:
            raise ValueError(
                f"Could not find a download link for {format.value} in {link_to_file}"
            )

        url_to_raw_files[format] = download_links[0]

    if len(url_to_raw_files) < 1:
        raise ValueError(
            "Could not find a link to any of the formats "
            f"({', '.join(ArticleFormat._member_names_)}), article url: "
            f"{article_url}"
        )

    metadata = Metadata(raw_metadata)

    journal_from_metadata = metadata.to_dict().get(
        "DC.Source", None
    ) or metadata.to_dict().get("citation_journal_title", [""])

    return Article(
        created_at=datetime.now(),
        journal=journal_from_metadata[0],
        url=article_url,
        metadata=metadata,
        formats=set(url_to_raw_files.keys()),
        url_to_raw_files=url_to_raw_files,
    )
