class ArticleSummary:
    def __init__(self, articleUrl, title, image, authors, publishDate, summary):
        self.articleUrl = articleUrl
        self.title = title
        self.image = image
        self.authors = authors
        self.publishData = publishDate
        self.summary = summary

    def to_dict(self):
        return {"articleUrl": self.articleUrl, "title": self.title, "image": self.image, "author": self.authors, "publishDate": self.publishData, "summary": self.summary}
