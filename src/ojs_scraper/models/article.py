import hashlib
from datetime import datetime
from enum import StrEnum
from pathlib import Path

import requests
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
    formats: set[ArticleFormat]
    url_to_raw_files: dict[str, str]

    def __str__(self) -> str:
        return self.__repr__()

    def hash(self) -> str:
        return f"{hashlib.sha1(self.url.encode('utf-8')).hexdigest()}"[:8]

    @property
    def name(self) -> str:
        journal_words = self.journal.split(" ")
        journal_initials = "".join([w[0] for w in journal_words])
        journal_indentifier = self.url.split("/")[-1]

        return f"{journal_initials}.{journal_indentifier}"

    def _download_format(self, path: Path, format: ArticleFormat) -> None:
        if format not in self.url_to_raw_files:
            raise ValueError("...")

        res = requests.get(self.url_to_raw_files[format])
        with (path / f"{self.name}.{format.value}").open("wb") as fp:
            fp.write(res.content)

    def download(self, path: Path, format: ArticleFormat | None = None) -> None:
        """Downloads available raw files into the specificed path.

        Passing None as format means downloading _all_ available formats. If
        a format is passed, only that format is downloaded.
        """
        formats_to_download = [format] if format is not None else self.formats

        for format_ in formats_to_download:
            self._download_format(path, format_)
