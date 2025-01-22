"""
Simple finance library for stock market data
"""
import investpy
import numpy as np

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from financelib.utils import yesterday_str_slash_dmy

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

    def __init__(self, symbol: str = ""):
        """Initialize stock with symbol"""
        self.symbol = symbol.upper()

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
    def get_all_stocks(cls, country_name: str = 'turkey') -> Dict[str, str]:
        """Get all predefined BIST stocks"""
        try:
            # Get all stock data for the specified country
            stocks = investpy.stocks.get_stocks(country=country_name.lower())

            # Display the stocks
            for _, stock in stocks.iterrows():
                stocks.full_name
        except Exception as e:
            print(f"An error occurred: {e}")

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

    def get_price_data(self, compare_from: str | datetime.date = yesterday_str_slash_dmy) -> Optional[Dict[str, Any]]:
        """Get current price and basic info"""
        try:
            df = investpy.get_stock_historical_data(stock=self.symbol, country='turkey', from_date=compare_from, to_date=datetime.now().strftime('%d/%m/%Y'))
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
                'timestamp': datetime.datetime.now().strftime('%H:%M:%S')
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
