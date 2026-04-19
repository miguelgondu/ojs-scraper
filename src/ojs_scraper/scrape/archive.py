from typing import cast
from collections.abc import Iterable
import logging

from ojs_scraper.utils.soup import soupify
from ojs_scraper.utils.types import Archive, Link

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

    def _fetch_all_archive_pages(self) -> Iterable[Link]:
        counter = 1
        previous_page_text = None
        current_page_is_empty = False
        next_page_equals_current_page = False
        current_url = f"{self.base_url}/{counter}"

        """
        There are two criteria for stopping:
        1. We find no issues in the current page.
        2. The next page is equal to the current page.
        """
        while not current_page_is_empty and not next_page_equals_current_page:
            current_url = f"{self.base_url}/{counter}"
            current_page_soup = soupify(current_url)
            current_page_text = current_page_soup.get_text()

            current_page_is_empty = (
                current_page_soup.find(class_=self.a_tag_for_issue__parent) is None
            )
            if current_page_is_empty:
                break
            if current_page_text == previous_page_text:
                break

            yield current_url
            previous_page_text = current_page_text
            counter += 1

    def _extract_issues_from_archive_page(self, archive_soup: Archive) -> Iterable[str]:
        issue_summaries = archive_soup.find_all(
            "div", class_=self.a_tag_for_issue__parent
        )

        for div in issue_summaries:
            if self.a_tag_for_issue__child is None:
                # TODO: polish
                link = div.find("a").get("href")  # type: ignore
                if link is None:
                    raise RuntimeError("a tag didn't have an href")
                yield cast(str, link)
            else:
                link = div.find("a", class_=self.a_tag_for_issue__child).get("href")  # type: ignore
                if link is None:
                    raise RuntimeError("a tag didn't have an href")
                yield cast(str, link)

    def scrape_links_for_issues(self) -> Iterable[Link]:
        """An iterable over the issue links."""
        # Logic to scrape the archive page
        archive_pages = self._fetch_all_archive_pages()
        for page in archive_pages:
            # Convert the archive page to a soup
            archive_soup = soupify(page)

            # Extract issue links from the soup
            yield from self._extract_issues_from_archive_page(archive_soup)
