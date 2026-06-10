import logging
import re
from collections.abc import Iterable

from ojs_scraper.utils.soup import soupify
from ojs_scraper.utils.types import Link

logger = logging.getLogger(__name__)


class ArchiveScraper:
    def __init__(
        self,
        base_url: str,
        a_tag_for_issue__parent: str,
        a_tag_for_issue__child: str | None,
    ):
        self.base_url = base_url

        self.a_tag_for_issue__parent = a_tag_for_issue__parent
        self.a_tag_for_issue__child = a_tag_for_issue__child
        self.issue_view_pattern = r"/issue/view/[A-Za-z0-9-_.]+/?$"

    def scrape_links_for_issues(self) -> Iterable[Link]:
        """An iterable over the issue links."""
        # Logic to scrape the archive page
        counter = 1
        issue_pages = set()

        while counter < 500:
            current_url = f"{self.base_url}/{counter}"
            current_page_soup = soupify(current_url)

            current_issue_links = [
                link_tag.get("href", "")
                for link_tag in current_page_soup.find_all("a")
                if re.search(self.issue_view_pattern, link_tag.get("href", ""))
            ]

            yield from current_issue_links

            if issue_pages.union(set(current_issue_links)) <= issue_pages:
                return

            counter += 1
            issue_pages = issue_pages.union(set(current_issue_links))
