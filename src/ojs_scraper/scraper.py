import logging
from urllib.error import URLError
from urllib.parse import urlparse, urlunparse
from urllib.robotparser import RobotFileParser
from warnings import filterwarnings

from ojs_scraper.models.urls import OJSArchiveConfig
from ojs_scraper.protocols.registry import RegistryProtocol
from ojs_scraper.scrape.archive import ArchiveScraper
from ojs_scraper.scrape.article import ArticleScraper
from ojs_scraper.scrape.issue import IssueScraper

# Headers for requests
DEFAULT_HEADERS = {
    "User-Agent": "LatinAmericanPhilosophyMiningBot/1.0 (jloaiza@uahurtado.cl, "
    "miguelgondu@gmail.com, nicolas.duque@ucaldas.edu.co)",
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ignore SSL warnings
filterwarnings("ignore", message="Unverified HTTPS request is being made to host")


class Scraper:
    def __init__(
        self,
        archive_config: OJSArchiveConfig,
        registry: RegistryProtocol,
        headers: dict = DEFAULT_HEADERS,
    ):
        """Scraper for OJS archives.

        In initialization, we get all the archive URLs by
        following "next" until we reach the end of the archive.

        """
        self.archive_urls = []
        self.headers = headers
        self.registry = registry

        self.archive_config = archive_config
        self.delay = self.compute_delay_from_robots()

    def compute_delay_from_robots(self) -> int:
        """Computes the delay from the robots.txt file of the archive URL."""
        # Parse the URL to extract the root domain
        parsed_url = urlparse(self.archive_config.archive_url)
        robots_url = urlunparse(
            (
                "https",
                parsed_url.netloc,
                "robots.txt",
                "",
                "",
                "",
            )
        )

        try:
            robot_parser = RobotFileParser(robots_url)
            robot_parser.read()
        except URLError:
            robot_parser = RobotFileParser(robots_url.replace("https", "http"))
            robot_parser.read()

        # Default to 5 seconds if not specified
        return int(robot_parser.crawl_delay("*") or 5)

    def scrape(self) -> None:
        archive_scraper = ArchiveScraper(
            base_url=self.archive_config.archive_url,
            a_tag_for_issue__parent=self.archive_config.archive_a_tag_for_issue__parent,
            a_tag_for_issue__child=self.archive_config.archive_a_tag_for_issue__child,
        )

        issue_links = archive_scraper.scrape_links_for_issues()
        for issue_link in issue_links:
            issue_scraper = IssueScraper(
                issue_url=issue_link,
                issue_a_tag_for_article__parent=self.archive_config.issue_a_tag_for_article__parent,
            )
            article_links = issue_scraper.scrape_links_for_articles()
            for article_link in article_links:
                art = ArticleScraper(
                    article_url=article_link,
                    article_galley_class=self.archive_config.article_galley_class,
                ).scrape_article()
                self.registry.create_article(art)
