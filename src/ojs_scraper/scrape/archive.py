import logging
import re
from typing import cast

from ojs_scraper.utils.soup import soupify
from ojs_scraper.utils.types import Link

logger = logging.getLogger(__name__)


class ArchiveScraper:
    def __init__(
        self,
        base_url: str,
    ):
        self.base_url = base_url
        self.issue_view_pattern = re.compile(r"/issue/view/[A-Za-z0-9-_.]+/?$")

    def scrape_links_for_issues(self) -> list[Link]:
        """An iterable over the issue links."""
        counter = 1
        issue_pages = set()

        while counter < 500:
            current_url = f"{self.base_url}/{counter}"
            current_page_soup = soupify(current_url)

            curent_issue_a_tags = current_page_soup.find_all(
                "a", href=self.issue_view_pattern
            )
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
