import json
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent.resolve()


class FileManager:
    def __init__(self) -> None:
        pass

    def load(self, path: Path | str):
        """Loads the json file, assuming that the path starts at the base folder."""
        if isinstance(path, str):
            path = Path(path)

        path = ROOT_DIR / path
        with path.open() as file:
            return json.load(file)

    def update(self, path, new_info: dict):
        article = self.load(path)

        for key, value in new_info.items():
            article[key] = value

        self.save(article, path)

    def save(self, article, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w") as file:
            json.dump(article, file, indent=True)

    def save_raw_data(self, id, format, raw_content, raw_folder):
        raw_folder = Path(raw_folder)
        raw_filepath = raw_folder / f"{id}.{format}"

        raw_folder.mkdir(parents=True, exist_ok=True)

        if format == "pdf":
            with raw_filepath.open("wb") as f:
                f.write(raw_content)
        elif format == "html":
            with raw_filepath.open("w") as f:
                f.write(str(raw_content))
        elif format == "json":
            with (raw_folder / f"{id}.json").open("w", encoding="utf-8") as f:
                json.dump(raw_content, f, indent=True)
