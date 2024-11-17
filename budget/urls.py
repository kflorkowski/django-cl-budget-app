from django.urls import path
from . import views

urlpatterns = [
    path('', views.base, name='base'),
    path('login', views.user_login, name='login'),
    path('register', views.user_register, name='register'),
    path('logout', views.user_logout, name='logout'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('budgets', views.budgets ,name='budgets'),
    path('goals', views.goals ,name='goals'),
    path('transactions', views.transactions ,name='transactions'),
]
