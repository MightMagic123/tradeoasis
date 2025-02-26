from django.urls import path
from . import views

app_name = 'education'

urlpatterns = [
    path('', views.education, name='education'),
    path('create/', views.create_lesson, name='create_lesson'),
    path('<slug:slug>/', views.lesson_detail, name='lesson_detail'),
]