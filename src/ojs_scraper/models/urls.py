from pydantic import BaseModel


class Tags(BaseModel):
    parent: str
    child: str | None


class OJSArchiveConfig(BaseModel):
    archive_url: str
    issue_tags: Tags
    article_tags: Tags
    article_galley_class: str = "obj_galley_link"
    country: str | None = None
