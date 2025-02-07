from django.contrib import admin
from .models import Stock

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("name", "ticker", "sector", "market_cap", "country")  # Columns shown in admin
    search_fields = ("name", "ticker", "sector", "industry")  # Searchable fields
    list_filter = ("sector", "country")  # Filters in sidebar