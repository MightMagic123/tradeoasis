from django.db import models
""""Model is not used in this project"""
class Stock(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Stock name (e.g., Apple Inc.)
    ticker = models.CharField(max_length=10, unique=True)  # Stock symbol (e.g., AAPL)
    sector = models.CharField(max_length=100, blank=True, null=True)  # Industry sector (e.g., Technology)
    industry = models.CharField(max_length=100, blank=True, null=True)  # Specific industry (e.g., Consumer Electronics)
    short_info = models.TextField(blank=True, null=True)  # Company description
    market_cap = models.BigIntegerField(blank=True, null=True)  # Market capitalization
    country = models.CharField(max_length=100, blank=True, null=True)  # Country of the company
    website = models.URLField(blank=True, null=True)  # Company website
    full_time_employees = models.IntegerField(blank=True, null=True)  # Number of employees

    created_at = models.DateTimeField(auto_now_add=True)  # Auto timestamp

    def __str__(self):
        return f"{self.name} ({self.ticker})"
