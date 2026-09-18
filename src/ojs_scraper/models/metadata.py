ArticleRawMetadata = list[tuple[str, str]]


class Metadata:
    def __init__(self, raw_metadata: ArticleRawMetadata):
        self.raw_metadata = raw_metadata

    def raw(self) -> ArticleRawMetadata:
        return self.raw_metadata

    def to_dict(self) -> dict[str, list[str]]:
        metadata = {}

        for key, _ in self.raw_metadata:
            metadata[key] = [v for k, v in self.raw_metadata if k == key]

        return metadata
