import logging
import re
from typing import cast

from ojs_scraper.utils.soup import soupify
from ojs_scraper.utils.types import Link

logger = logging.getLogger(__name__)


def scrape_archive(
    base_url: str,
    issue_view_pattern: re.Pattern = re.compile(r"/issue/view/[A-Za-z0-9-_.]+/?$"),
    *,
    max_counter: int = 500,
) -> list[Link]:
    """A list over the issue links."""
    counter = 1
    issue_pages = set()

    while counter < max_counter:
        current_url = f"{base_url}/{counter}"
        current_page_soup = soupify(current_url)

        curent_issue_a_tags = current_page_soup.find_all("a", href=issue_view_pattern)
        current_issue_links = {
            cast("Link", link.get("href"))
            for link in curent_issue_a_tags
            if link.get("href")
        }

        if issue_pages.union(current_issue_links) > issue_pages:
            issue_pages = issue_pages.union(current_issue_links)
            logger.info(
                "Visited and added %d links from %s",
                len(current_issue_links),
                current_url,
            )
            counter += 1
        else:
            break

    return list(issue_pages)
