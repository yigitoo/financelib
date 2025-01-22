import sqlite3 as db
import os

from financelib.utils import today_str_underline
from financelib.settings import LIBRARY_NAME
from financelib.databases.modals import NewsModel

from financelib.databases.settings import (
    DB_NEWS_TABLE_NAME,
    check_table_exist,
    create_table_query,
    make_insert_query
)

class SQLite:
    def __init__(self, db_name):
        self.filename = f'{LIBRARY_NAME}_{db_name}_{today_str_underline()}.db'
        self.db_name = db_name
        if not os.path.exists(self.filename):
          with open(self.filename, 'w+') as f:
              pass  # Create the file
        self.conn = db.connect(db_name)
        self.cursor = self.conn.cursor()

    def insert_article(self, news: NewsModel) -> None:
        query = make_insert_query(news)
        self.cursor.execute(query)
        self.conn.commit()

    def insert_articles(self, news_list: list[NewsModel]) -> None:
        for news in news_list:
            self.insert_article(news)
        self.conn.commit()

    def check_table(self, table_name):
        return check_table_exist(self.cursor, table_name)
    def execute(self, query):
        self.cursor.execute(query)
        self.conn.commit()

    def fetchall(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def fetchone(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchone()

    def close(self):
        self.conn.close()
