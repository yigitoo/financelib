"""
Main Test
"""
from financelib.news import NewsAPIQuery
import unittest


class TestStock(unittest.TestCase):
    def news_api_test(self):
      news_client = NewsAPIQuery()
      self.assertIsNotNone(news_client.get_all_news_source_ids())
      self.assertIn('status', news_client.get_all_news_source_ids())

if __name__ == '__main__':
    unittest.main()

