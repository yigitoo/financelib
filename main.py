"""
Stock market data viewer
"""
from src.financelib.stock import Stock

def main() -> None:
    # Test stock search and display
    stocks = ["THYAO.IS", "GARAN.IS", "SASA.IS"]

    # Arama örnekleri

    sasa_polyester = Stock.search_stocks("Sasa polyester", return_data=True)
    print(sasa_polyester)

    print("\nDetailed stock information:")
    for symbol in stocks:
        Stock.display_stock_info(symbol)


if __name__ == '__main__':
    main()

