from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
import json

def about(request):
    return render(request, 'about.html')

def testing(request):
    return render(request, 'test.html')

def home(request):
    return render(request, 'home.html')

def stock(request):
    return render(request, 'stock.html')

def interest_calculator(request):
    return render(request, 'interest_calculator.html')

def education(request):
    return render(request, 'education.html')
