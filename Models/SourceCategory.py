class SourceCategory:
    def __init__(self, source, category, path, href):
        self.source = source
        self.category = category
        self.path = path
        self.href = href

    def getPathUrl(self):
        url = self.source + self.path
        return url
