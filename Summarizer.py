import re
import nltk
import heapq
from text_hr import get_all_std_words
from newspaper import Article
from Models.ArticleSummary import ArticleSummary

class Summarizer:
    def __init__(self, articleUrl, numberOfSentences):
        self.articleUrl = articleUrl
        self.numberOfSentences = numberOfSentences

    def getDetails(self):
        ## Fetching Articles from Url ##

        article = Article(self.articleUrl)
        article.download()
        article.parse()
        articleText = article.text

        articleTitle = ""
        articleImage = ""
        articlePublishDate = ""
        articleAuthors = []
        articleUrl = ""
        articleTitle = article.title
        articleImage = article.top_image
        articleAuthors = article.authors
        articlePublishDate = article.publish_date
        articleUrl = article.url

        ## Preprocessing ##

        # Removing Square Brackets and Extra Spaces
        articleText = re.sub(r'\[[0-9]*\]', ' ', articleText)
        articleText = re.sub(r'\s+', ' ', articleText)

        # Removing special characters and digits
        formattedArticleText = re.sub('[^a-žA-Ž]', ' ', articleText)
        formattedArticleText = re.sub(r'\s+', ' ', formattedArticleText)

        ## Converting Text To Sentences ##

        sentence_list = nltk.sent_tokenize(articleText)

        ## Find Weighted Frequency of Occurrence ##

        # nltk.download('stopwords')
        # stopwords = nltk.corpus.stopwords.words('english')

        stopwords = []
        for word_base, l_key, cnt, _suff_id, wform_key, wform in get_all_std_words():
            stopwords.append(word_base)
        stopwords = list(dict.fromkeys(stopwords))

        word_frequencies = {}
        for word in nltk.word_tokenize(formattedArticleText):
            if word not in stopwords:
                if word not in word_frequencies.keys():
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1

        maximum_frequncy = max(word_frequencies.values())

        for word in word_frequencies.keys():
            word_frequencies[word] = (word_frequencies[word] / maximum_frequncy)

        ## Calculating Sentence Scores ##

        sentence_scores = {}
        for sent in sentence_list:
            for word in nltk.word_tokenize(sent.lower()):
                if word in word_frequencies.keys():
                    if len(sent.split(' ')) < 30:
                        if sent not in sentence_scores.keys():
                            sentence_scores[sent] = word_frequencies[word]
                        else:
                            sentence_scores[sent] += word_frequencies[word]

        ## Getting the Summary ##

        summary_sentences = heapq.nlargest(self.numberOfSentences, sentence_scores, key=sentence_scores.get)

        # single string
        summary = ' '.join(summary_sentences)

        articleSummary = ArticleSummary(self.articleUrl, articleTitle, articleImage, articleAuthors, articlePublishDate, summary)
        return articleSummary
