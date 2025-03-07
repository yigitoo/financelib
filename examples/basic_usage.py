from financelib import Stock

def main():
    # Search for a stock
    results = Stock.search_stock("THYAO", return_data=True)
    print("Search results:", results)

    # Display stock information
    Stock.display_stock_info("THYAO.IS")

if __name__ == "__main__":
    main()
