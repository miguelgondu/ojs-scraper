from bs4 import BeautifulSoup


class MockWithHTMLClient:
    def __init__(self, html: list[str] | str):
        self.htmls = html if isinstance(html, list) else [html]

    def get(self, url: str) -> BeautifulSoup:
        if len(self.htmls) < 1:
            raise ValueError("Calling get after the htmls were exhausted in mock.")

        html = self.htmls.pop(0)
        return BeautifulSoup(html, features="lxml")
