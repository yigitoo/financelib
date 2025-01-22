
# -*- coding: utf-8 -*-
"""
@title: settings.py
@author: Yiğit GÜMÜŞ
@date: 2025-01-22 01:53:36
"""
import sqlite3

from financelib.databases.modals import (
  NewsModel,
  StockDataModel
)

# Database settings
DB_NEWS_TABLE_NAME = "news"

NEWS_TITLE_COLUMN_NAME = "title"
NEWS_CONTENT_COLUMN_NAME = "content"
NEWS_PUBLISHED_AT_COLUMN_NAME = "published_at"
NEWS_AUTHOR_COLUMN_NAME = "author"
NEWS_CATEGORY_COLUMN_NAME = "category"
NEWS_SOURCE_COLUMN_NAME = "source"
NEWS_ARTICLE_URL_COLUMN_NAME = "article_url"
NEWS_ARTICLE_THUMBNAIL_URL_COLUMN_NAME = "article_thumbnail_url"


DB_NEWS_COLUMN_NAMES = [
  NEWS_TITLE_COLUMN_NAME,
  NEWS_CONTENT_COLUMN_NAME,
  NEWS_PUBLISHED_AT_COLUMN_NAME,
  NEWS_AUTHOR_COLUMN_NAME,
  NEWS_CATEGORY_COLUMN_NAME,
  NEWS_SOURCE_COLUMN_NAME,
  NEWS_ARTICLE_URL_COLUMN_NAME,
  NEWS_ARTICLE_THUMBNAIL_URL_COLUMN_NAME,
]


check_table_query = "SELECT name FROM sqlite_master WHERE type='table' AND name='{}'"
def check_table_exist(cursor: sqlite3.Cursor, table_name: str = DB_NEWS_TABLE_NAME) -> str:
  cursor.execute(check_table_query.format(table_name))
  result = cursor.fetchone()
  return True if result is not None else False

create_table_query = f"CREATE TABLE IF NOT EXISTS {DB_NEWS_TABLE_NAME} (id INTEGER PRIMARY KEY, {NEWS_TITLE_COLUMN_NAME} TEXT, {NEWS_CONTENT_COLUMN_NAME} TEXT, {NEWS_PUBLISHED_AT_COLUMN_NAME} TEXT, {NEWS_AUTHOR_COLUMN_NAME} TEXT, {NEWS_CATEGORY_COLUMN_NAME} TEXT, {NEWS_SOURCE_COLUMN_NAME} TEXT, {NEWS_ARTICLE_URL_COLUMN_NAME} TEXT, {NEWS_ARTICLE_THUMBNAIL_URL_COLUMN_NAME} TEXT)"

def make_insert_article_query(news: NewsModel) -> str:
  return (
    f"INSERT INTO {DB_NEWS_TABLE_NAME} ({NEWS_TITLE_COLUMN_NAME}, {NEWS_CONTENT_COLUMN_NAME}, {NEWS_PUBLISHED_AT_COLUMN_NAME}, {NEWS_AUTHOR_COLUMN_NAME}, {NEWS_CATEGORY_COLUMN_NAME}, {NEWS_SOURCE_COLUMN_NAME}, {NEWS_ARTICLE_URL_COLUMN_NAME}, {NEWS_ARTICLE_THUMBNAIL_URL_COLUMN_NAME}) VALUES ('{news.title}', '{news.content}', '{news.published_at}', '{news.author}', '{news.category}', '{news.source}', '{news.article_url}', '{news.article_thumbnail_url}')"
  )

def make_insert_stock_data_query(stock_data: StockDataModel) -> str:
  #TODO: Implement this function.
  return (
    f""
  )
