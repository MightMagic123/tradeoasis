from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import yfinance as yf
from stock.stocks import get_sp500_tickers
from django.http import JsonResponse, HttpResponse
from .models import Stock
from accounts.models import Portfolio, PortfolioItem
from decimal import Decimal, ROUND_HALF_UP

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
        # Fetch stock data from Yahoo Finance
        stock = yf.Ticker(ticker)
        name = stock.info.get("shortName", ticker)
        pe_ratio = stock.info.get("trailingPE")
        sector = stock.info.get("sector", "Unknown")
        short_info = stock.info.get("longBusinessSummary", "No description available.")
        
        # Get stock price in USD
        current_price_usd = stock.history(period="1d")['Close'].iloc[-1]

        # Get exchange rate for USD to EUR
        forex = yf.Ticker("EURUSD=X")  
        exchange_rate = Decimal(str(forex.history(period="1d")['Close'].iloc[-1]))

        # Convert USD price to EUR
        current_price_eur = (Decimal(str(current_price_usd)) / exchange_rate).quantize(Decimal("0.00001"), rounding=ROUND_HALF_UP)

        # Calculate total amount invested in the specific stock
        portfolio = Portfolio.objects.get(user=request.user)
        try:
            portfolio_item = PortfolioItem.objects.get(portfolio=portfolio, ticker=ticker)
            total_invested = (portfolio_item.quantity * portfolio_item.purchase_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except PortfolioItem.DoesNotExist:
            portfolio_item = None
            total_invested = Decimal("0.00")

        # Handle investment form submission
        if request.method == "POST":
            investment_amount = request.POST.get('investment_amount')
            sell_amount_eur = request.POST.get('sell_amount_eur')
            sell_all = request.POST.get('sell_all')

            try:
                portfolio, created = Portfolio.objects.get_or_create(user=request.user)

                if investment_amount:
                    investment_amount = Decimal(investment_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)  # Convert input to Decimal and round to 2 decimal places
                    if investment_amount <= 0:
                        raise ValueError("Investment amount must be greater than zero.")

                    # Check if the user has enough balance
                    if investment_amount > portfolio.cash_balance:
                        raise ValueError("Insufficient balance to make this investment.")

                    # Calculate number of shares
                    quantity = (investment_amount / current_price_eur).quantize(Decimal("0.00001"), rounding=ROUND_HALF_UP)  # Allow up to 5 decimal places

                    # Deduct investment amount from cash balance
                    portfolio.cash_balance -= investment_amount
                    portfolio.save()

                    if portfolio_item:
                        # Calculate the weighted average purchase price
                        total_quantity = portfolio_item.quantity + quantity
                        weighted_average_price = ((portfolio_item.quantity * portfolio_item.purchase_price) + (quantity * current_price_eur)) / total_quantity

                        # Update the existing portfolio item
                        portfolio_item.quantity = total_quantity
                        portfolio_item.purchase_price = weighted_average_price.quantize(Decimal("0.00001"), rounding=ROUND_HALF_UP)
                        portfolio_item.save()
                    else:
                        # Add new stock to portfolio
                        PortfolioItem.objects.create(
                            portfolio=portfolio,
                            ticker=ticker,
                            quantity=quantity,
                            purchase_price=current_price_eur
                        )

                elif sell_amount_eur:
                    sell_amount_eur = Decimal(sell_amount_eur).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)  # Convert input to Decimal and round to 2 decimal places
                    if sell_amount_eur <= 0:
                        raise ValueError("Sell amount must be greater than zero.")

                    # Find the portfolio item
                    portfolio_item = PortfolioItem.objects.get(portfolio=portfolio, ticker=ticker)

                    # Calculate the number of shares to sell
                    sell_quantity = (sell_amount_eur / current_price_eur).quantize(Decimal("0.00001"), rounding=ROUND_HALF_UP)

                    # Check if the user has enough shares to sell
                    if sell_quantity > portfolio_item.quantity:
                        raise ValueError("Insufficient shares to sell.")

                    # Calculate the amount to be credited to cash balance
                    sell_value = (sell_quantity * current_price_eur).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

                    # Update portfolio item quantity
                    portfolio_item.quantity -= sell_quantity
                    if portfolio_item.quantity == 0:
                        portfolio_item.delete()
                    else:
                        portfolio_item.save()

                    # Credit the sell value to cash balance
                    portfolio.cash_balance += sell_value
                    portfolio.save()

                elif sell_all:
                    # Find the portfolio item
                    portfolio_item = PortfolioItem.objects.get(portfolio=portfolio, ticker=ticker)

                    # Calculate the amount to be credited to cash balance
                    sell_value = (portfolio_item.quantity * current_price_eur).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

                    # Delete the portfolio item
                    portfolio_item.delete()

                    # Credit the sell value to cash balance
                    portfolio.cash_balance += sell_value
                    portfolio.save()

                return redirect('stock_detail', ticker=ticker)

            except Exception as e:
                return render(request, 'stock_detail.html', {
                    'name': name,
                    'ticker': ticker,
                    'current_price': current_price_eur,
                    'pe_ratio': pe_ratio,
                    'sector': sector,
                    'total_invested': total_invested,
                    'short_info': short_info,
                    'error_message': str(e)
                })

        return render(request, 'stock_detail.html', {
            'name': name,
            'ticker': ticker,
            'current_price': current_price_eur,
            'pe_ratio': pe_ratio,
            'sector': sector,
            'total_invested': total_invested,
            'short_info': short_info,
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

