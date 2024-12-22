import unittest
from financelib import Stock

class TestStock(unittest.TestCase):
    def test_search_stocks(self):
        results = Stock.search_stocks("THYAO", return_data=True)
        self.assertTrue(len(results) > 0)
        self.assertIn('symbol', results[0])

    def test_get_price_data(self):
        stock = Stock("THYAO.IS")
        data = stock.get_price_data()
        self.assertIsNotNone(data)
        self.assertIn('price', data)

if __name__ == '__main__':
    unittest.main()
