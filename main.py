"""
Stock market data viewer
"""
from financelib.news import NewsAPIQuery

news_client = NewsAPIQuery()
print(news_client.get_all_news_source_ids())
