from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
import json
import yfinance as yf
from stock.models import Stock
from accounts.models import Portfolio, PortfolioItem
from decimal import Decimal, ROUND_HALF_UP

def testing(request):
    return render(request, 'test.html')

def home(request):
    return render(request, 'home.html')

def stock(request):
    return render(request, 'stock.html')

def interest_calculator(request):
    return render(request, 'interest_calculator.html')

def help(request):
    return render(request, 'help.html')

def portfolio(request):
    user = request.user

    try:
        # Fetch user's portfolio
        portfolio = Portfolio.objects.get(user=user)
        portfolio_items = portfolio.items.all()  # Get all stocks in portfolio
    except Portfolio.DoesNotExist:
        # If no portfolio exists, create one with default cash balance
        portfolio = Portfolio.objects.create(user=user)
        portfolio_items = []
    
    # Initialize total portfolio value
    total_value = Decimal("0.00")

    # Get exchange rate for USD to EUR
    forex = yf.Ticker("EURUSD=X")
    exchange_rate = Decimal(str(forex.history(period="1d")['Close'].iloc[0]))

    # Update stock prices and calculate total portfolio value
    for item in portfolio_items:
        stock = yf.Ticker(item.ticker)
        current_price_usd = stock.history(period="1d")['Close'].iloc[0]
        current_price_eur = (Decimal(str(current_price_usd)) / exchange_rate).quantize(Decimal("0.00001"), rounding=ROUND_HALF_UP)  # Convert to EUR

        # Store updated price and calculate value
        item.current_price = current_price_eur
        item.current_value = (item.quantity * current_price_eur).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)  # Round to 2 decimal places

        # Add to total portfolio value
        total_value += item.current_value

    context = {
        "user": user,
        "portfolio": portfolio,
        "portfolio_items": portfolio_items,
        "total_value": total_value,
        "portfolio_value": (Decimal(portfolio.cash_balance) + total_value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)  # Round to 2 decimal places
    }
    
    return render(request, "yourprofile.html", context)  