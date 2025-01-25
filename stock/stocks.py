import pandas as pd
import yfinance as yf
import requests

# Function to get the list of S&P 500 tickers
def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)  # Read all tables from the page
    sp500 = tables[0]  # The first table contains the S&P 500 companies
    tickers = sp500['Symbol'].tolist()  # Extract stock symbols from the table
    return tickers

# Function to fetch stock data for each ticker using yfinance
def get_stock_data(tickers):
    stock_data = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            stock_data[ticker] = stock.history(period="1d")  # Fetch 1 day of stock data
            print(f"Fetched data for {ticker}")
        except Exception as e:
            print(f"Could not fetch data for {ticker}: {e}")
    return stock_data

# Main execution
def main():
    print("Fetching S&P 500 stock tickers...")
    tickers = get_sp500_tickers()
    print(f"Found {len(tickers)} tickers in the S&P 500.")
    
    # Fetch stock data for each ticker (here we limit to first 20 tickers to avoid hitting API limits)
    stock_data = get_stock_data(tickers[:20])  # Limit to first 20 to prevent rate limiting
    
    # Display a sample of the fetched data for the first 5 tickers
    for ticker, data in stock_data.items():
        print(f"\nData for {ticker}:\n", data.head())

if __name__ == "__main__":
    main()
