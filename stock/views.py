from django.shortcuts import render
import yfinance as yf

def stock_home(request):
    return render(request, 'stockhome.html')

def stock_detail(request, ticker):
    # Fetch stock data using yfinance
    stock = yf.Ticker(ticker)

    # Get the historical stock data for the last day (can adjust as needed)
    stock_data = stock.history(period="1d")
    
    # Optionally, you can fetch additional info (like company info, dividends, etc.)
    company_info = stock.info
    
    # Pass the stock data to the template
    context = {
        'ticker': ticker,
        'stock_data': stock_data,
        'company_info': company_info,
    }
    
    return render(request, 'stock_detail.html', context)
