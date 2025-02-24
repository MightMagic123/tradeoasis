from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import CustomUserCreationForm
from django.urls import reverse
import logging
from .models import Portfolio, PortfolioItem
from decimal import Decimal, ROUND_HALF_UP
import yfinance as yf

def accounts(request):
    user = request.user

    if not user.is_authenticated:
        return redirect("login")  # Redirect to the login page instead of rendering "accounts.html"

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

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save() 
            logging.info("User registered successfully.")
            return redirect(reverse('login'))
        else:
            logging.warning("Form is not valid.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            logging.info("User logged in successfully.")
            return redirect('accounts')
        else:
            logging.warning("Invalid login credentials.")
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

def logout(request):
    auth_logout(request)
    logging.info("User logged out successfully.")
    return redirect('home')

