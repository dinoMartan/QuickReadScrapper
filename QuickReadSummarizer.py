import requests
import urllib.request
import re
import concurrent.futures
from Summarizer import Summarizer
from bs4 import BeautifulSoup
from datetime import datetime
from Common.bcolors import bcolors
from Models.GetAllSourcesResponse import GetAllSourcesResponse, Source
from Models.ArticleIdsResponse import ArticleIdsResponse
from typing import List
from Common.formatter import human_delta

headers = {'Authorization': ''}
APIUrl = ''
getAllArticlesUrl = APIUrl + "?getAllArticleUrls=1"
getAllSourcesUrl = APIUrl + "/getAllSources"
addArticleUrl = APIUrl + "/addArticle"
getArticleIds = APIUrl + "/getIdsOfArticlesForSourceCategory"
numberOfSentences = 4
minimumLenght = 250

articlesAdded = 0
debugPrint = False

def summarize(articleUrl, category, sourceId):

    summarizer = Summarizer(articleUrl, numberOfSentences)

    article = summarizer.getDetails()

    # filter out short articles
    if len(article.summary) < minimumLenght:
        return

    if not article.authors:
        article.authors = "N/A"
    if not article.publishData:
        now = datetime.now()
        dateString = now.strftime("%d/%m/%Y %H:%M:%S")
        article.publishData = dateString
    title = article.title
    title = title.replace("'", r"\'");
    sum = article.summary
    sum = sum.replace("'", r"\'");
    parameters = {
        'idUrl': article.articleUrl,
        'idSource': sourceId,
        'category': category['name'],
        'title': title,
        'imageUrl': article.image,
        'author': article.authors,
        'publishDate': article.publishData,
        'summary': sum
    }

    response = requests.post(addArticleUrl, data=parameters, headers=headers)
    if debugPrint:
        print("                Url: " + article.articleUrl)
        print("                Response: " + str(response.status_code) + " " + response.text)
    if response.status_code == 200 or response.status_code == 201:
        articlesAdded = articlesAdded + 1


def scrapCategory(category, sourceId):
    if debugPrint:
        print("        Scrapping category '" + bcolors.OKBLUE + category['name'] + bcolors.ENDC + "':")

    sourceUrl = sourceId
    portalUrl = sourceUrl + category['path']

    html_page = urllib.request.urlopen(portalUrl)
    soup = BeautifulSoup(html_page, "html.parser")
    soupList = soup.findAll('a', attrs={'href': re.compile(category['href'])})


    # check if article is in db

    parameters = {
        "idSource": str(sourceId),
        "category": str(category['name'])
    }
    response = requests.get(getArticleIds, params=parameters, headers=headers)
    responseJson = response.json()
    articleIdsResponse = ArticleIdsResponse(**responseJson)

    if debugPrint:
        print("            Creating list of new articles:")
    articleUrls = []
    for link in soupList:
        url = sourceUrl + link.get('href')
        if sourceUrl in url:
            url = url.replace(sourceUrl, "")
            url = sourceUrl + url

        skipUrl = False
        for existingUrl in articleIdsResponse.articleIDs:
            if existingUrl in url:
                skipUrl = True
                break

        if (url in articleIdsResponse.articleIDs) or skipUrl:
            continue
        else:
            articleUrls.append(url)
            if debugPrint:
                print("                " + url)

    # check if list of new articles is empty
    if not articleUrls:
        if debugPrint:
            print("                No new articles found!")
        return

    if debugPrint:
        print("            Starting summarization...")
    executors = concurrent.futures.ProcessPoolExecutor()
    futures = [executors.submit(summarize, articleUrl, category, sourceUrl) for articleUrl in articleUrls]
    concurrent.futures.wait(futures)

def prepareScrapper(item):
    source: Source
    source = item
    categoriesDict = source['category']

    if debugPrint:
        print("    Fetching categories for '" + bcolors.OKGREEN + source['name'] + bcolors.ENDC + "':")
    # for each source's category, scrap category

    for category in categoriesDict:
        scrapCategory(category, source['idSource'])


# fetch all sources and call prepareScrapper() on every source
def main():
    statDate = datetime.now()
    print("Scrappy start: " + statDate.strftime("%d-%m-%Y %H:%M:%S"))
    # get all sources
    if debugPrint:
        print("Fetching all sources from DB...")
    response = requests.get(getAllSourcesUrl, headers=headers)
    responseJson = response.json()

    getAllSourcesResponse = GetAllSourcesResponse(**responseJson)

    sources:List[Source]
    sources = getAllSourcesResponse.sources

    for source in sources:
        prepareScrapper(source)

    endDate = datetime.now()
    print("Scrappy end: " + endDate.strftime("%d-%m-%Y %H:%M:%S"))

    timeDelta = endDate - statDate
    print("Duration: " + human_delta(timeDelta))
    print("Articles added: " + str(articlesAdded) + "\n")


if __name__ == "__main__":
    main()