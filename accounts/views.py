from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import CustomUserCreationForm
from django.urls import reverse
import logging
# Create your views here.

def accounts(request):
    return render(request, 'accounts.html', {'user': request.user})

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

