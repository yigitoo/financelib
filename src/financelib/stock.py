"""
Simple finance library for stock market data
"""
import yfinance as yf
from yahooquery import search as yahoo_search_stock

import numpy as np
import pandas as pd

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class Stock:
    # Common BIST stocks for quick access
    COMMON_STOCKS = {
        'THYAO': 'Türk Hava Yolları',
        'GARAN': 'Garanti BBVA',
        'ASELS': 'ASELSAN',
        'SASA': 'SASA Polyester',
        'KCHOL': 'Koç Holding',
        'AKBNK': 'Akbank',
        'EREGL': 'Ereğli Demir Çelik',
        'BIMAS': 'BİM Mağazalar',
        'TUPRS': 'Tüpraş',
        'YKBNK': 'Yapı Kredi',
        'PGSUS': 'Pegasus',
        'TAVHL': 'TAV Havalimanları',
        'SAHOL': 'Sabancı Holding',
        'TOASO': 'Tofaş Oto',
        'FROTO': 'Ford Otosan',
    }


    @classmethod
    def search_stocks(cls, query_list: List[str], return_info: bool = False) -> Optional[List[Dict[str, Any]]]:
        try:
            info = []
            for query in query_list:
                if return_info:
                    temp = cls.search_stock(query, return_info=return_info)
                    info.append(temp)
                else:
                    cls.search_stock(query)

            if return_info:
                return info
        except Exception as e:
            return {"error": str(e), "info": e.with_traceback()}

    @classmethod
    def search_stock(cls, company_name: str, return_info: bool = False) -> List[Dict[str, Any]]:
        try:
            info = []
            # Search for the company by name
            search_result = yahoo_search_stock(company_name)

            # Check if there are any results
            if not search_result or 'quotes' not in search_result or len(search_result['quotes']) == 0:
                return {"error": "No matching company found"}

            # Get the first result (assuming it's the best match)
            if search_result is not None:
                for quote in search_result['quotes']:
                    stock = yf.Ticker(quote.get("symbol"))
                    print(stock)
                    stock_info = stock.info

                    # Extract and return relevant information
                    info.append({
                        "symbol": stock_info.get("symbol"),
                        "short_name": stock_info.get("shortName"),
                        "long_name": stock_info.get("longName"),
                        "score": quote.get("score"),
                        "exchange": quote.get("exchange"),
                        "current_price": stock_info.get("currentPrice"),
                        "market_cap": stock_info.get("marketCap"),
                        "sector": stock_info.get("sector"),
                        "industry": stock_info.get("industry"),
                    })

            if return_info:
                return info

            __import__('pprint').pprint(info)
        except Exception as e:
            return {"error": str(e), "info": e.with_traceback()}
    @classmethod
    def display_stock_info(cls, company_name: str) -> Dict[str, Any]:
        try:
            # Search for the company by name
            search_result = yahoo_search_stock(company_name)

            # Check if there are any results
            if not search_result or 'quotes' not in search_result or len(search_result['quotes']) == 0:
                return {"error": "No matching company found"}

            # Get the first result (assuming it's the best match)
            first_match = search_result['quotes'][0]
            symbol = first_match.get("symbol")

            # Fetch detailed stock information using yfinance
            import yfinance as yf
            stock = yf.Ticker(symbol)
            stock_info = stock.info

            # Extract and return relevant information
            return {
                "symbol": stock_info.get("symbol"),
                "short_name": stock_info.get("shortName"),
                "current_price": stock_info.get("currentPrice"),
                "market_cap": stock_info.get("marketCap"),
                "sector": stock_info.get("sector"),
                "industry": stock_info.get("industry"),
            }
        except Exception as e:
            return {"error": str(e)}
