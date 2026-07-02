import logging

from ojs_scraper.scrape.archive import scrape_archive
from ojs_scraper.scrape.article import scrape_article
from ojs_scraper.scrape.issue import scrape_issue
from ojs_scraper.scraper import scrape

logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = ["scrape", "scrape_archive", "scrape_issue", "scrape_article"]
