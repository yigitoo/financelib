import unittest
from financelib import Stock

class TestStock(unittest.TestCase):
    def test_search_stock(self):
        results = Stock.search_stock("THYAO")
        self.assertIsNotNone(results)

    def test_get_stock_data_via_class(self):
        stock = Stock("THYAO.IS")
        data = stock.get_data()
        self.assertIsNotNone(data)


if __name__ == '__main__':
    unittest.main()
