from django.http import HttpResponse
from django.shortcuts import render

def about(request):
    return HttpResponse("About TradeOasis")

def testing(request):
    return render(request, 'test.html')

def home(request):
    return render(request, 'home.html')

def stock(request):
    return render(request, 'stock.html')