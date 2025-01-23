# -*- coding: utf-8 -*-
"""
@title: settings.py
@author: Yiğit GÜMÜŞ
@date: 2025-01-22 01:39:31
"""
LIBRARY_NAME = "financelib"

# CONSTANTS
NEWS_TITLE_CHAR_LIMIT = 10
NEWS_CONTENT_CHAR_LIMIT = 150


from selenium import webdriver
import dotenv, os

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

def get_webdriver_chrome():
  global chrome_options
  return webdriver.Chrome(options=chrome_options)

NEWS_API_APIKEY = os.getenv('NEWS_API_APIKEY')

def news_api_setup(api_key: str = None, api_key_from_dotenv: bool = True, dotenv_path: str = "") -> str:
  global NEWS_API_APIKEY

  if api_key == '' and api_key_from_dotenv:

    if dotenv_path == "":
      dotenv.load_dotenv()

    else:
      dotenv.load_dotenv(dotenv_path)

    NEWS_API_APIKEY = os.getenv("NEWS_API_APIKEY")
  else:
    NEWS_API_APIKEY = api_key

  return NEWS_API_APIKEY


def change_news_api_key(api_key: str):
  global NEWS_API_APIKEY
  NEWS_API_APIKEY = api_key

def get_news_api_key():
  global NEWS_API_APIKEY
  return NEWS_API_APIKEY

def change_db_news_table_name(new_name: str):
  global DB_NEWS_TABLE_NAME
  DB_NEWS_TABLE_NAME = new_name

def get_db_news_table_name():
  global DB_NEWS_TABLE_NAME
  return DB_NEWS_TABLE_NAME

def set_news_title_char_limit(new_limit: int):
  global NEWS_TITLE_CHAR_LIMIT
  NEWS_TITLE_CHAR_LIMIT = new_limit

def get_news_title_char_limit():
  global NEWS_TITLE_CHAR_LIMIT
  return NEWS_TITLE_CHAR_LIMIT

def set_news_content_char_limit(new_limit: int):
  global NEWS_CONTENT_CHAR_LIMIT
  NEWS_CONTENT_CHAR_LIMIT = new_limit

def get_news_content_char_limit():
  global NEWS_CONTENT_CHAR_LIMIT
  return NEWS_CONTENT_CHAR_LIMIT
