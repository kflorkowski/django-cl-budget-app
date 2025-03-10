from django.urls import path
from . import views
from .views import DashboardView

urlpatterns = [
    path('', views.base, name='base'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('budgets/', views.budgets ,name='budgets'),
    path('goals/', views.goals, name='goals'),
    path('goals/add-goal', views.add_goal ,name='add_goal'),
    path('goals/donate/<int:goal_id>', views.donation, name='donation'),
    path('transactions/', views.transactions ,name='transactions'),
    path('transactions/add-income', views.add_income, name='add_income'),
    path('transactions/add-expense', views.add_expense, name='add_expense'),
    path('transactions/edit-income/<int:transaction_id>', views.edit_income, name='edit_income'),
    path('transactions/edit-expense/<int:transaction_id>', views.edit_expense, name='edit_expense'),
]
