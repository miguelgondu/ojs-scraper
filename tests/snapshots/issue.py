import json
from pathlib import Path

import pytest

from ojs_scraper import scrape_issue
from tests.helpers.mocks import MockWithHTMLClient

SNAPSHOT_DATA_DIR = Path(__file__).parent / "data" / "issues"


def _load_html(journal_name: str) -> list[str]:
    htmls = []
    for html_path in sorted(
        (SNAPSHOT_DATA_DIR / f"journal={journal_name}").glob("*.html")
    ):
        with html_path.open() as fp:
            htmls.append(fp.read())

    return htmls


@pytest.mark.parametrize(("journal_name",), [("estudios_de_filosofia",)])
def test__issues_snapshot__matches_snapshot(journal_name: str):
    htmls = _load_html(journal_name)
    mock_client = MockWithHTMLClient(htmls)

    res = scrape_issue("test.url", client=mock_client)

    with (
        SNAPSHOT_DATA_DIR / f"journal={journal_name}" / "2026_11_20_results.json"
    ).open() as fp:
        expected = json.load(fp)

    assert set(res) == set(expected)


if __name__ == "__main__":
    htmls = _load_html("estudios_de_filosofia")

    print(htmls)
