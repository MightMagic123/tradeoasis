from django.shortcuts import render

# Create your views here.

def accounts(request):
    return render(request, 'accounts.html')

def register(request):
    return render(request, 'register.html')

def login(request):
    return render(request, 'login.html')