import datetime
import requests

from newsapi import NewsApiClient

from bs4 import BeautifulSoup
from typing import List, Dict
import time, os

from settings import (
  NEWS_API_APIKEY,
  news_api_setup,
  NEWS_TITLE_CHAR_LIMIT,
  NEWS_CONTENT_CHAR_LIMIT
)
class News:
  title: str
  content: str
  date: str | datetime.date | datetime.datetime
  author: str | List[str]
  category: str = "news"
  source: str = 'from god :)'
  article_url: str = ""
  article_thumbnail_url: str = ""

  def __init__(self, data: Dict[str, str] = {}) -> None:
    data =  {k.lower(): v for k, v in data.items()}
    if data == {}:
      self._title = ""
      self._content = ""
      self._date = ""
      self._author = ""
      self._category = "news"
      self._source = "from god :)"
      self._article_thumbnail_url = ""
      self._article_url = ""
    else:
      self._title = data.get('title')
      self._content = data.get('content')
      self._date = data.get('date')
      self._author = data.get('author')
      self._category = data.get('category', 'news')
      self._source = data.get('source', 'from god :)')
      self._article_url = data.get('article_url', '')
      self._article_thumbnail_url = data.get('article_thumbnail_url', '')

  @property
  def category(self) -> str:
    return self._category

  @category.setter
  def category(self, category_name: str) -> None:
    self._category = category_name

  @property
  def title(self) -> str:
    return self._title

  @title.setter
  def title(self, title_name: str):
    if len(title_name) < NEWS_TITLE_CHAR_LIMIT:
      raise ValueError('Please set the news/article name a little bit longer. Minimum character limit is 10.')
    self._title = title_name

  @property
  def content(self) -> str:
    return self._content
  @content.setter
  def content(self, content_value: str) -> None:
    if len(content_value) < NEWS_CONTENT_CHAR_LIMIT:
      raise ValueError('Please set the content a little bit longer. Minimum character limit is 250')
    self._content = content_value
  @property
  def date(self) -> str | datetime.date | datetime.datetime:
    return self._date

  @date.setter
  def date(self, date_value: str | datetime.date | datetime.datetime) -> None:
     if type(date_value) not in [str, datetime.date, datetime.datetime]:
        raise TypeError('Please set the date as a string, datetime.date or datetime.datetime object')
     self._date = date_value

  @property
  def author(self) -> str | List[str]:
    if type(self._author) is str:
      return self._author
    if type(self._author) is list:
      return ', '.join(self._author)
  @author.setter
  def author(self, author_name: str) -> None:
    author_variable_type: str | List[str] = type(author_name)
    if author_variable_type is not list and author_variable_type is not str:
       raise TypeError('Please set the author name as a string or list of strings')

    if author_variable_type is str and len(author_name.split()) < 2:
      raise ValueError(
         'Please set news/article editor\'s name as full name (with name and surname). Example: u\'Yiğit GÜMÜŞ\''
      )

    if 'By ' in author_name[0,3]:
      author_name = author_name[3:]

    if author_variable_type is str and ' and ' in author_name:
       author_name = author_name.split(' and ')

    self._author = author_name

  @property
  def source(self) -> str:
    return self._source

  @source.setter
  def source(self, source_name: str) -> None:
    self._source = source_name

  @property
  def article_url(self) -> str:
    return self._article_url

  @article_url.setter
  def article_url(self, url: str) -> None:
    self._article_url = url

  @property
  def article_thumbnail_url(self) -> str:
    return self._article_thumbnail_url

  @article_thumbnail_url.setter
  def article_thumbnail_url(self, url: str) -> None:
    self._article_thumbnail_url = url

class BaseQueryClass:
    BASE_URL: str
    SEARCH_URL: str
    session: requests.Session
    headers: Dict[str, str] = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Referer': 'https://www.bloomberg.com',
      'DNT': '1'
    }

    def search_articles(self, query: str, limit: int = 5, print_results: bool = False) -> List[News]:
        raise NotImplementedError("Please implement this method in your subclass")


class BloombergQuery(BaseQueryClass):
    BASE_URL = "https://www.bloomberg.com"
    SEARCH_URL = f"{BASE_URL}/search"

    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.bloomberg.com',
            'DNT': '1'
        }

    def print_article_details(self, article: News) -> None:
        print()
        print("-----------------------------------")
        print("Title:", article.title)
        print("-----------------------------------")
        print(article.content)
        print("-----------------------------------")
        print("Category:", article.category)
        print("Date of Upload:", article.date)
        print("Author:", article.author)
        print("-----------------------------------")
        print()


    def search_articles(self, query: str, limit: int = 5, print_results: bool = False) -> List[News]:
        articles = []
        try:
            params = {
                'query': query,
                'source': 'news',
                'sort': 'relevancy'
            }

            response = self.session.get(
                self.SEARCH_URL,
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            time.sleep(2)  # Add delay

            soup = BeautifulSoup(response.text, 'html.parser')

            # Try different article selectors
            article_elements = (
                soup.find_all('article') or
                soup.find_all('div', class_=lambda x: x and 'story' in x.lower()) or
                soup.find_all('div', class_=lambda x: x and 'article' in x.lower()) or
                soup.find_all('div', class_=lambda x: x and 'news' in x.lower())
            )

            for article in article_elements[:limit]:
                try:
                    # More flexible title search
                    title = (
                        article.find(['h1', 'h2', 'h3']) or
                        article.find(class_=lambda x: x and 'title' in x.lower()) or
                        article.find(class_=lambda x: x and 'headline' in x.lower()) or
                        article.find(class_=lambda x: x and 'name' in x.lower()) or
                        article.find(class_=lambda x: x and 'articlename' in x.lower()) or
                        article.find(class_=lambda x: x and 'articletitle' in x.lower()) or
                        article.find(class_=lambda x: x and 'article_name' in x.lower()) or
                        article.find(class_=lambda x: x and 'article_title' in x.lower())
                    )
                    title = title.get_text().strip() if title else ""

                    # More flexible content search
                    content = (
                        article.find('p') or
                        article.find(class_=lambda x: x and 'summary' in x.lower()) or
                        article.find(class_=lambda x: x and 'description' in x.lower()) or
                        article.find(class_=lambda x: x and 'content' in x.lower())
                    )
                    content = content.get_text().strip() if content else ""

                    # More flexible date search
                    date_element = (
                        article.find('time') or
                        article.find(class_=lambda x: x and 'time' in x.lower()) or
                        article.find(class_=lambda x: x and 'date' in x.lower()) or
                        article.find(class_=lambda x: x and 'publishedat' in x.lower()) or
                        article.find(class_=lambda x: x and 'published_at' in x.lower()) or
                        article.find(class_=lambda x: x and 'uploadat' in x.lower()) or
                        article.find(class_=lambda x: x and 'upload_at' in x.lower())
                    )
                    date = date_element.get_text().strip() if date_element else ""

                    # More flexible author search
                    author_element = (
                        article.find(class_=lambda x: x and 'author' in x.lower()) or
                        article.find(class_=lambda x: x and 'authors' in x.lower()) or
                        article.find(class_=lambda x: x and 'byline' in x.lower())
                    )
                    author = author_element.get_text().strip() if author_element else "Bloomberg"

                    category_element = (
                        article.find(class_=lambda x: x and 'category' in x.lower()) or
                        article.find(class_=lambda x: x and 'categories' in x.lower()) or
                        article.find(class_=lambda x: x and 'tag' in x.lower()) or
                        article.find(class_=lambda x: x and 'tags' in x.lower()) or
                        article.find(class_=lambda x: x and 'eyebrow' in x.lower())
                    )
                    category = category_element.get_text().strip().capitalize() if category_element else "news"

                    if title:  # Only add if we found a title
                        news = News({
                            'title': title,
                            'content': content,
                            'date': date,
                            'author': author,
                            'category': category
                        })
                        articles.append(news)

                except Exception as e:
                    print(f"Error parsing article: {str(e)}")
                    continue

            if print_results:
              for article in articles:
                print("-----------------------------------")
                print("Title:", article.title)
                print("-----------------------------------")
                print(article.content)
                print("-----------------------------------")
                print("Category:", article.category)
                print("Date of Upload:", article.date)
                print("Author:", article.author)
                print("-----------------------------------")
                print()

            return articles

        except Exception as e:
            print(f"Error fetching articles: {str(e)}")
            return []

class NewsAPIQuery(BaseQueryClass):

  def __init__(self, api_key: str = ''):
    global NEWS_API_APIKEY
    _api_key: str  = news_api_setup(api_key)
    self.newsapi: NewsApiClient = NewsApiClient(api_key=_api_key)

  def print_article_details(self, article: News) -> None:
        print()
        print("-----------------------------------")
        print("Title:", article['title'])
        print("-----------------------------------")
        print("Article Thumbnail:", article['urlToImage'])
        print('---')
        print(article['content'])
        print("-----------------------------------")
        print("Source:", article['source']['name'])
        print("Date of Publish:", article['publishedAt'])
        print("Article URL:", article['url'])
        print("-----------------------------------")
        print()

  def search_articles(self, query, sources_from_ids: str | List[str], limit: int = 5,
                      print_results: bool = False) -> List[News]:
    sources = ''
    if sources_from_ids is not None and type(sources_from_ids) is list:
       sources=','.join(sources_from_ids)

    all_articles = self.newsapi.get_everything(
      q=query,
      sources=sources,
    )

    if print_results:
      for article in all_articles['articles']:
       self.print_article_details(article)

    return all_articles['articles']
  def get_all_news_source_ids(self) -> List[str]:
    sources = self.newsapi.get_sources()
    return [source['id'] for source in sources['sources']]

  def get_all_news_sources_detailed(self) -> List[Dict[str, str]]:
    sources = self.newsapi.get_sources()
    return sources['sources']


if __name__ == '__main__':
  newsquery = NewsAPIQuery(api_key_from_dotenv=True)
  newsquery.search_articles('Apple', sources_from_ids=['bloomberg', 'bbc-news', 'cnn'], print_results=True)
