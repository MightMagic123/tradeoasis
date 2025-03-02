from django.urls import path
from . import views

app_name = 'education'

urlpatterns = [
    path('', views.education, name='education'),
    path('create/', views.create_lesson, name='create_lesson'),
    path('compound-interest/', views.compound_interest, name='compound_interest'),
    path('s&p500/', views.snp500, name='snp500'),
    path('<slug:slug>/', views.lesson_detail, name='lesson_detail'),
]