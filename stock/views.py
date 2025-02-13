from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import yfinance as yf
from stock.stocks import get_sp500_tickers
from django.http import JsonResponse
from .models import Stock
from accounts.models import Portfolio, PortfolioItem
from decimal import Decimal

def stock_home(request):
    tickers, company_names = get_sp500_tickers(True)
    ticker_company_pairs = zip(tickers, company_names)
    context = {
        'ticker_company_pairs': ticker_company_pairs
    }
    return render(request, 'stockhome.html', context)


@login_required
def stock_detail(request, ticker):
    try:
        # Fetch stock details from the database
        stock_db = get_object_or_404(Stock, ticker=ticker)

        # Fetch stock data from Yahoo Finance
        stock = yf.Ticker(ticker)
        pe_ratio = stock.info.get("trailingPE")
        
        # Get stock price in USD
        current_price_usd = stock.history(period="1d")['Close'].iloc[-1]

        # Get exchange rate for USD to EUR
        forex = yf.Ticker("EURUSD=X")  
        exchange_rate = Decimal(str(forex.history(period="1d")['Close'].iloc[-1]))

        # Convert USD price to EUR
        current_price_eur = Decimal(str(current_price_usd)) / exchange_rate

        # Handle investment form submission
        if request.method == "POST":
            investment_amount = request.POST.get('investment_amount')

            try:
                investment_amount = Decimal(investment_amount)  # Convert input to Decimal
                if investment_amount <= 0:
                    raise ValueError("Investment amount must be greater than zero.")

                portfolio, created = Portfolio.objects.get_or_create(user=request.user)

                # Check if the user has enough balance
                if investment_amount > portfolio.cash_balance:
                    raise ValueError("Insufficient balance to make this investment.")

                # Calculate number of shares
                quantity = (investment_amount / current_price_eur).quantize(Decimal("0.00001"))  # Allow up to 5 decimal places

                # Deduct investment amount from cash balance
                portfolio.cash_balance -= investment_amount
                portfolio.save()

                # Add stock to portfolio
                PortfolioItem.objects.create(
                    portfolio=portfolio,
                    ticker=ticker,
                    quantity=quantity,
                    purchase_price=current_price_eur
                )

                return redirect('stock_detail', ticker=ticker)

            except Exception as e:
                return render(request, 'stock_detail.html', {
                    'stock_db': stock_db,
                    'ticker': ticker,
                    'current_price': current_price_eur,
                    'pe_ratio': pe_ratio,
                    'error_message': str(e)
                })

        return render(request, 'stock_detail.html', {
            'stock_db': stock_db,
            'ticker': ticker,
            'current_price': current_price_eur,
            'pe_ratio': pe_ratio,
        })

    except Exception as e:
        return render(request, 'error.html', {'message': str(e)})


def stock_data(request, ticker):
    try:
        # Fetch historical stock data
        stock = yf.Ticker(ticker)
        stock_data = stock.history(period="6mo")  # Fetch last 6 months of data

        # Ensure data exists
        if stock_data.empty:
            return JsonResponse({'error': f"No data available for ticker '{ticker}'."}, status=404)

        # Fetch exchange rate for USD to EUR
        forex = yf.Ticker("EURUSD=X")
        exchange_rate = Decimal(str(forex.history(period="1d")['Close'].iloc[-1]))

        # Convert historical prices to EUR
        dates = stock_data.index.strftime('%Y-%m-%d').tolist()
        close_prices_usd = [Decimal(str(price)) for price in stock_data['Close'].tolist()]
        close_prices_eur = [(price / exchange_rate).quantize(Decimal("0.000001")) for price in close_prices_usd]

        # Prepare and return JSON response
        chart_data = {
            'dates': dates,
            'close_prices': close_prices_eur,  # Prices now in EUR
        }

        return JsonResponse(chart_data)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

