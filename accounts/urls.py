from django.urls import path
from . import views

urlpatterns = [
    path('', views.accounts, name="accounts"),
    path('register/', views.register, name="register"),
    path('login/', views.login, name="login")
]
