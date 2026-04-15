from pydantic import BaseModel


class OJSArchiveConfig(BaseModel):
    archive_url: str
    country: str
    archive_a_tag_for_issue__parent: str = "obj_issue_summary"
    archive_a_tag_for_issue__child: str | None = "title"
    issue_a_tag_for_article__parent: str = "obj_article_summary"
    issue_a_tag_for_article__child: str | None = "title"
    article_galley_class: str = "obj_galley_link"
