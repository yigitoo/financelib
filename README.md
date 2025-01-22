# 📈 FinanceLib

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Simple and efficient library for tracking BIST (Borsa Istanbul) stocks with real-time data and search capabilities.

## 🚀 Features

- 🔍 **Smart Search**: Search stocks by symbol or company name
- 💰 **Real-time Data**: Get current stock prices and changes
- 📊 **Rich Display**: Colored output for price changes
- 📈 **Market Data**: Track volume and price movements
- 🇹🇷 **BIST Focus**: Specialized for Turkish stock market
- 📰 **Data Crawler and News API**: News/Article API (100 query per day) and some news sites crawlers.

## 🛠️ Installation

```bash
# Using pip
$ pip install financelib

# From source
$ git clone https://github.com/yigitoo/financelib.git
$ cd financelib
$ pip install -e .

# and set api key
# Goto https://newsapi.org/ and get your api key
# And set this api key with that name if you want to use NewsAPI
$ export NEWS_API_APIKEY="your-api-key"

```

## 📖 Usage

### Basic Usage

```python
from financelib import Stock

# Search for a stock
results = Stock.search_stocks("THYAO", return_data=True)
print(results)

# Display stock information with colors
Stock.display_stock_info("THYAO.IS")
```

### Search Examples

```python
# Search by company name
Stock.search_stocks("Garanti")

# Search by symbol
Stock.search_stocks("SASA")

# Get all available stocks
all_stocks = Stock.get_all_stocks()
```

### Display Stock Information

The library provides beautiful colored output in the terminal:

```python
Stock.get_live_stock_state("THYAO.IS")
```

Output example:
```
THYAO.IS - 14:30:25
Price: 172.45 TRY
Change: ▲ 2.45 (1.44%)
Volume: 24,532,100
```

## 📊 Supported Stocks

Currently supported BIST, NASDAQ and NYSE stocks.
But in the future I/we should add other countries stock markets too.

## 🔧 Configuration

No additional configuration needed. The library works out of the box with default settings.

## 🧪 Testing

```bash
# Run all tests
python -m unittest discover tests

# Run specific test
python -m unittest tests.test_stock
```

## 📝 Requirements

- Python 3.9 or higher (Python 3.10+ is recommended)
- Dependencies:
  - yfinance>=0.2.36
  - pandas>=1.5.0
  - numpy
  - requests>=2.31.0
  - beautifulsoup4>=4.12.0
  - newsapi-python
  - python-dotenv
  - SQLAlchemy

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

## 🙏 Acknowledgments

- Data provided by Yahoo Finance
- Inspired by various financial libraries
- Used FinViz API for stock search
- Thanks to all contributors

## 📬 Contact

Yiğit GÜMÜŞ - [@yigitgumus_](https://twitter.com/yigitgumus_)

Project Link: [https://github.com/yigitgumus/financelib](https://github.com/yigitgumus/financelib)

---

Made with ❤️ for BIST traders and developers
