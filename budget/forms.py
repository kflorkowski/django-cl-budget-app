from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Budget


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class UserLoginForm(AuthenticationForm):
    pass

class BudgetForm(Budget):
    class Meta:
        model = Budget
        fields = ('name', 'date')
        labels = {
            'name':'Budget name',
            'date':'Date',
        }
            
