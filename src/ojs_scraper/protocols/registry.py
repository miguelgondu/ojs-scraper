from typing import Protocol

from ojs_scraper.models.article import BaseArticle


class RegistryProtocol(Protocol):
    def create_article(self, article: BaseArticle) -> None:
        """Save the article to the registry."""
        raise NotImplementedError

    def check_if_article_exists(self, *, article: BaseArticle) -> bool:
        """Check if an article exists in the registry."""
        raise NotImplementedError
