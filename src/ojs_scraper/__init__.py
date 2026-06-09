import logging

from ojs_scraper.models.urls import OJSArchiveConfig
from ojs_scraper.scraper import Scraper

logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = ["Scraper", "OJSArchiveConfig"]
