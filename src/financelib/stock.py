"""
Simple finance library for stock market data
"""
import yfinance as yf
from typing import Dict, Any, Optional, List
import pandas as pd
import requests
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

    FINVIZ_URL = "https://finviz.com/quote.ashx"
    CACHE_TIMEOUT = 3600  # 1 hour cache
    _stock_cache = {'timestamp': 0, 'data': {}}

    def __init__(self, symbol: str):
        """Initialize stock with symbol"""
        self.symbol = symbol.upper()
        self._ticker = yf.Ticker(symbol)

    @classmethod
    def search_stocks(cls, query: str, return_data: bool = False) -> None:
        """Search for stocks"""
        results = cls.search_symbol(query)

        # If return_data is True, return the results
        # Else print the results
        if return_data:
            return results

        print(f"\nSearch results for '{query}':")
        for result in results:
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                print(result)



    @classmethod
    def get_all_stocks(cls) -> Dict[str, str]:
        """Get all predefined BIST stocks"""
        return cls.COMMON_STOCKS

    @classmethod
    def search_symbol(cls, query: str) -> List[Dict[str, Any]]:
        """
        Search for stocks in BIST
        Args:
            query: Search term (company name or symbol)
        Returns:
            List of matching stocks with their details
        """
        try:
            query = query.upper().strip()
            results = []

            # Search in predefined stocks
            for symbol, name in cls.COMMON_STOCKS.items():
                if query in symbol or query.upper() in name.upper():
                    stock_info = {
                        'symbol': f'{symbol}.IS',
                        'name': name,
                        'exchange': 'BIST',
                        'type': 'Equity'
                    }

                    # Try to get current price
                    try:
                        price_data = cls(f'{symbol}.IS').get_price_data()
                        if price_data:
                            stock_info.update({
                                'price': price_data['price'],
                                'currency': price_data['currency']
                            })
                    except Exception:
                        pass

                    results.append(stock_info)

            return results if results else [{'error': f"No matching stocks found for '{query}'"}]

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return [{'error': 'Search failed. Please try again later.'}]

    def get_price_data(self) -> Optional[Dict[str, Any]]:
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
