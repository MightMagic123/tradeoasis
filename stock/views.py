from django.shortcuts import render
import yfinance as yf
from stock.stocks import get_sp500_tickers
from django.http import JsonResponse

def stock_home(request):
    tickers, company_names = get_sp500_tickers(True)
    ticker_company_pairs = zip(tickers, company_names)
    context = {
        'ticker_company_pairs': ticker_company_pairs
    }
    return render(request, 'stockhome.html', context)

# views.py

from django.shortcuts import render
from django.http import JsonResponse
import yfinance as yf

def stock_detail(request, ticker):
    try:
        # Fetch stock data from Yahoo Finance for the last year (1 year)
        stock = yf.Ticker(ticker)
        stock_data = stock.history(period="1y")  # Last 1 year data
        
        # Get current stock price, market cap, and P/E ratio
        current_price = stock.history(period="1d")['Close'].iloc[0]
        market_cap = stock.info.get('marketCap', 'N/A')
        pe_ratio = stock.info.get('trailingPE', 'N/A')

        # Prepare the stock data for the chart
        dates = stock_data.index.strftime('%Y-%m-%d').tolist()
        close_prices = stock_data['Close'].tolist()

        # Render the stock details page
        return render(request, 'stock_detail.html', {
            'ticker': ticker,
            'current_price': current_price,
            'market_cap': market_cap,
            'pe_ratio': pe_ratio,
            'stock_data': {
                'dates': dates,
                'close_prices': close_prices
            }
        })
    
    except Exception as e:
        return render(request, 'error.html', {'message': str(e)})

def stock_data(request, ticker):
    try:
        # Fetch historical stock data
        stock = yf.Ticker(ticker)
        stock_data = stock.history(period="6mo")  # Fetch 6 months of data

        # Ensure data exists
        if stock_data.empty:
            return JsonResponse({'error': f"No data available for ticker '{ticker}'."}, status=404)

        # Prepare data for the chart
        chart_data = {
            'dates': stock_data.index.strftime('%Y-%m-%d').tolist(),
            'close_prices': stock_data['Close'].tolist(),
        }

        return JsonResponse(chart_data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)