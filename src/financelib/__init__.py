"""
FinanceLib - Simple finance library for financial analysis and research.

"""
import financelib.settings as settings
import financelib.stock as stock
import financelib.kap as kap
import financelib.news as news
import financelib.utils as utils

from financelib.stock import Stock

__version__ = "v0.1.0dev"
__author__ = "Yiğit GÜMÜŞ"
__email__ = "gumusyigit101@gmail.com"
__all__ = ["settings", "Stock","stock", "kap", "news", "utils"]

def get_version():
    return __version__
