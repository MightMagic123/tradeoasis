from django.shortcuts import render

def stock_home(request):
    return render(request, 'stockhome.html')
