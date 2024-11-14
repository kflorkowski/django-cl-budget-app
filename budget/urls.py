from django.urls import path
from . import views

urlpatterns = [
    path('', views.base, name='base'),
    path('login', views.user_login, name='login'),
    path('register', views.user_register, name='register'),
    path('dashboard', views.dashboard, name='dashboard'),
]
