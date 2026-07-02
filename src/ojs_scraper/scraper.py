import logging
from collections.abc import Iterator

from ojs_scraper.clients import ClientProtocol, SoupClient
from ojs_scraper.models.article import BaseArticle
from ojs_scraper.scrape.archive import scrape_archive
from ojs_scraper.scrape.article import scrape_article
from ojs_scraper.scrape.issue import scrape_issue

logger = logging.getLogger(__name__)


def scrape(
    archive_url: str,
    *,
    delay: int | None = None,
    headers: dict[str, str] | None = None,
    client: ClientProtocol | None = None,
) -> Iterator[BaseArticle]:
    logger.info("Scraping from: %s", archive_url)

    client = client or SoupClient(headers=headers, delay=delay)

    issue_links = scrape_archive(archive_url, client=client)
    for issue_link in issue_links:
        logger.info("Finding all article links in %s", issue_link)
        article_links = scrape_issue(issue_link, client=client)

        for article_link in article_links:
            logger.info("Scraping article from %s", issue_link)
            yield scrape_article(article_link, client=client)
