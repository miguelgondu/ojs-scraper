from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

ArticleRawMetadata = dict[str, str]


class ArticleFormat(StrEnum):
    """Possible formats an article can have."""

    XML = "xml"
    HTML = "html"
    PDF = "pdf"

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return self.value


class Article(BaseModel):
    created_at: datetime
    journal: str
    url: str
    parsed: bool
    raw_metadata: ArticleRawMetadata = Field(repr=False)
    format: ArticleFormat
    url_to_raw_file: str

    def __str__(self) -> str:
        return self.__repr__()
