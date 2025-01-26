from django.shortcuts import render
import yfinance as yf
from stock.stocks import get_sp500_tickers

def stock_home(request):
    tickers, company_names = get_sp500_tickers(True)
    ticker_company_pairs = zip(tickers, company_names)
    context = {
        'ticker_company_pairs': ticker_company_pairs
    }
    return render(request, 'stockhome.html', context)

# views.py
from django.shortcuts import render
import yfinance as yf

def stock_detail(request, ticker):
    try:
        # Fetch stock data using yfinance
        stock = yf.Ticker(ticker)
        stock_data = stock.history(period="1d")

        # Ensure there is data for the stock
        if stock_data.empty:
            context = {'error': f"No data available for ticker '{ticker}'."}
            return render(request, 'stocks/stock_detail.html', context)

        # Extract relevant data
        stock_info = {
            'ticker': ticker,
            'open': stock_data['Open'].iloc[0],
            'high': stock_data['High'].iloc[0],
            'low': stock_data['Low'].iloc[0],
            'close': stock_data['Close'].iloc[0],
            'volume': stock_data['Volume'].iloc[0],
        }

        # Add optional company information
        company_info = stock.info if stock.info else {}

        # Pass the extracted data to the template
        context = {
            'stock_info': stock_info,
            'company_info': company_info,
        }

        return render(request, 'stock_detail.html', context)

    except Exception as e:
        # Handle errors (e.g., invalid ticker or network issue)
        context = {'error': str(e)}
        return render(request, 'stock_detail.html', context)
