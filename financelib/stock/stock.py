"""
Simple finance library for stock market data
"""
import yfinance as yf
import yahooquery as yq

import numpy as np
import pandas as pd

from typing import Dict, Any, Optional, List
from datetime import datetime

from settings import logger

class Stock:
    def __init__(self, symbol: str):
        """Initialize stock with symbol"""
        self.symbol = symbol.upper()
        self._ticker = yf.Ticker(symbol)

    # Common BIST stocks for quick access
    COMMON_STOCKS: Dict[str, str] = {
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

    def get_data(self):
        """Get current price score"""
        if self.symbol in ['', None]:
            raise ValueError({"error": "No stock symbol provided"})

        data: dict = yq.search(self.symbol)
        if data is None:
            raise ValueError({"error": "No matching company found"})

        quote = data['quotes'][0]
        return quote

    @classmethod
    def display_stock_infos(cls, query_list: List[str], return_info: bool = False) -> Optional[List[Dict[str, Any]]]:
        try:
            info = []
            for query in query_list:
                if return_info:
                    temp = cls.display_stock_info(query, return_info=return_info)
                    info.append(temp)
                else:
                    cls.display_stock_info(query)

            if return_info:
                return info
        except Exception as e:
            return {"error": str(e), "info": e.with_traceback()}

    @classmethod
    def display_stock_info(cls, company_name: str, return_info: bool = False) -> List[Dict[str, Any]]:
        try:
            info = []
            # Search for the company by name
            search_result = yq.search(company_name)

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
    def get_live_stock_state(cls, symbol: str) -> None:
        """
        symbol: str

        Display formatted stock information
        But you must set the stock code suitable with
        Yahoo Finance Stock Code
        I mean you must set 'THYAO' (Turkish Airlines) instead of 'THYAO.IS'
        """
        stock = cls(symbol)
        data = stock._get_stock()

        if data:
            change_symbol = '▲' if data['change'] > 0 else '▼' if data['change'] < 0 else '■'
            change_color = '\033[92m' if data['change'] > 0 else '\033[91m' if data['change'] < 0 else '\033[0m'

            print(f"\n{data['symbol']} - {data['timestamp']}")
            print(f"Price: {data['price']} {data['currency']}")
            print(f"Change: {change_color}{change_symbol} {data['change']} ({data['change_percent']}%)\033[0m")
            print(f"Volume: {data['volume']:,}")
        else:
            print(f"\nUnable to fetch data for {symbol}")

    def _get_stock(self) -> Optional[Dict[str, Any]]:
        """Get current price and basic info"""
        try:
            df = self._ticker.history(period='1d')
            if df.empty:
                return None

            last_price = df['Close'].iloc[-1]
            open_price = df['Open'].iloc[0]
            change = last_price - open_price
            change_percent = (change / open_price) * 100

            return {
                'symbol': self.symbol,
                'price': round(last_price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'currency': 'TRY',
                'volume': int(df['Volume'].iloc[-1]),
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }

        except Exception as e:
            logger.error(f"Error fetching price data for {self.symbol}: {e}")
            return None

    @classmethod
    def display_stock_info(cls, symbol: str) -> None:
        """Display formatted stock information"""
        stock = cls(symbol)
        data = stock.get_price_data()

        if data:
            change_symbol = '▲' if data['change'] > 0 else '▼' if data['change'] < 0 else '■'
            change_color = '\033[92m' if data['change'] > 0 else '\033[91m' if data['change'] < 0 else '\033[0m'

            print(f"\n{data['symbol']} - {data['timestamp']}")
            print(f"Price: {data['price']} {data['currency']}")
            print(f"Change: {change_color}{change_symbol} {data['change']} ({data['change_percent']}%)\033[0m")
            print(f"Volume: {data['volume']:,}")
        else:
            print(f"\nUnable to fetch data for {symbol}")

    @classmethod
    def search_stock(cls, company_name: str) -> Dict[str, Any]:
        try:
            # Search for the company by name
            search_result = yq.search(company_name)

            # Check if there are any results
            if not search_result or 'quotes' not in search_result or len(search_result['quotes']) == 0:
                return {"error": "No matching company found"}

            # Get the first result (assuming it's the best match)
            first_match = search_result.get('quotes')[0]
            return first_match

        except Exception as e:
            return {"error": str(e)}
