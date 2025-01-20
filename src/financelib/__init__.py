"""
FinanceLib - Simple finance library for stock market data

"""
from financelib.stock import Stock
from financelib.news import (
  News,
  NEWS_TITLE_CHAR_LIMIT,
  NEWS_CONTENT_CHAR_LIMIT
)


__version__ = "0.1.0"
__author__ = "Yiğit GÜMÜŞ"
__email__ = "gumusyigit101@gmail.com"
__all__ = ["Stock", "News", "NEWS_TITLE_CHAR_LIMIT", "NEWS_CONTENT_CHAR_LIMIT"]
