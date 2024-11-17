from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Income, Expense

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class UserLoginForm(AuthenticationForm):
    pass

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ('name', 'category', 'amount', 'date')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be a positive number.")
        return amount

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ('name', 'category', 'amount', 'date')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be a positive number.")
        return amount