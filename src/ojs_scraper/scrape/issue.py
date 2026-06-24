import logging
import re
from typing import cast

from ojs_scraper.utils.soup import soupify
from ojs_scraper.utils.types import Issue, Link

logger = logging.getLogger(__name__)


def scrape_issue(
    issue_url: str,
    article_view_pattern: re.Pattern = re.compile(r"/article/view/[A-Za-z0-9-_.]+/?$"),
) -> list[Link]:
    issue: Issue = soupify(issue_url)
    all_article_a_tags = issue.find_all("a", href=article_view_pattern)

    return list(
        {
            cast("Link", a.get("href"))
            for a in all_article_a_tags
            if a.get("href") is not None
        }
    )
