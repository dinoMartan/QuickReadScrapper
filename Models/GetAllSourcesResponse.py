from typing import List


class Category:
    name: str
    href: str
    path: str

    def __init__(self, name: str, href: str, path: str) -> None:
        self.name = name
        self.href = href
        self.path = path


class Source:
    name: str
    idSource: str
    image: str
    category: List[Category]

    def __init__(self, name: str, idSource: str, category: List[Category]) -> None:
        self.name = name
        self.idSource = idSource
        self.category = category


class GetAllSourcesResponse:
    sources: List[Source]

    def __init__(self, sources: List[Source]) -> None:
        self.sources = sources
