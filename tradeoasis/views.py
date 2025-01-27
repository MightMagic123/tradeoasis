from django.http import HttpResponse
from django.shortcuts import render

def about(request):
    return render(request, 'about.html')

def testing(request):
    return render(request, 'test.html')

def home(request):
    return render(request, 'home.html')

def stock(request):
    return render(request, 'stock.html')