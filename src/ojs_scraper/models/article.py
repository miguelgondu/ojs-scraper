from enum import StrEnum
from datetime import datetime

from pydantic import BaseModel

ArticleRawMetadata = dict[str, str]


class ArticleFormat(StrEnum):
    """Possible formats an article can have."""

    XML = "xml"
    HTML = "html"
    PDF = "pdf"

    def __str__(self) -> str:
        return self.value


class BaseArticle(BaseModel):
    created_at: datetime
    journal: str
    url: str
    parsed: bool
    raw_metadata: ArticleRawMetadata
    format: ArticleFormat
    url_to_raw_file: str
