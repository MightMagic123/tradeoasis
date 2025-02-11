from django.contrib.auth.models import AbstractUser
from django.db import models
import yfinance as yf
from decimal import Decimal

class CustomUser(AbstractUser):
    def __str__(self):
        return self.username

class Portfolio(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    cash_balance = models.DecimalField(max_digits=15, decimal_places=2, default=10000.00)  # Default $10,000 starting balance

    def get_total_value(self):
        total_value = self.cash_balance  # Start with cash balance
        portfolio_items = self.items.all()  # Get all portfolio items using the related name "items"

        for item in portfolio_items:
            total_value += item.get_current_value()

        return total_value

class PortfolioItem(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="items")
    ticker = models.CharField(max_length=10)
    quantity = models.DecimalField(max_digits=10, decimal_places=5)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_current_price(self):
        """Fetch the latest stock price using yfinance"""
        try:
            stock = yf.Ticker(self.ticker)
            current_price = stock.history(period="1d")["Close"].iloc[-1]  # Get the latest closing price
            return round(float(current_price), 2)  # Ensure it's a float and rounded to 2 decimals
        except Exception:
            return float(self.purchase_price)  # Default to purchase price if API fails

    def get_current_value(self):
        """Calculate current market value of this stock holding"""
        return self.quantity * Decimal(self.get_current_price())
