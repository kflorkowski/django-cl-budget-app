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
    path('transactions/add-income', views.add_income, name='add_income'),
    path('transactions/add-expense', views.add_expense, name='add_expense'),
    path('transactions/edit-income/<int:transaction_id>', views.edit_income, name='edit_income'),
    path('transactions/edit-expense/<int:transaction_id>', views.edit_expense, name='edit_expense'),
]
