from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Income, Expense, Goal, Contribution

class UserRegisterForm(UserCreationForm):
    """
    Form used for user registration, extending the default UserCreationForm.
    It includes the username, email, and password fields.
    """
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class UserLoginForm(AuthenticationForm):
    """
    Form used for user login, extending the default AuthenticationForm.
    It includes the username and password fields.
    """
    pass


class IncomeForm(forms.ModelForm):
    """
    Form used to create or update an income transaction.
    Validates that the amount is a positive number.
    """
    class Meta:
        model = Income
        fields = ('name', 'category', 'amount', 'date')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_amount(self):
        """
        Validates that the income amount is positive.

        Returns:
            amount (float): The valid income amount.

        Raises:
            forms.ValidationError: If the amount is less than or equal to 0.
        """
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be a positive number.")
        return amount


class ExpenseForm(forms.ModelForm):
    """
    Form used to create or update an expense transaction.
    Validates that the amount is a positive number.
    """
    class Meta:
        model = Expense
        fields = ('name', 'category', 'amount', 'date')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_amount(self):
        """
        Validates that the expense amount is positive.

        Returns:
            amount (float): The valid expense amount.

        Raises:
            forms.ValidationError: If the amount is less than or equal to 0.
        """
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be a positive number.")
        return amount


class GoalForm(forms.ModelForm):
    """
    Form used to create or update a goal, excluding the contributor field.
    """
    class Meta:
        model = Goal
        fields = ('name', 'description', 'target_amount')
        exclude = ['contributor']


class ContributionForm(forms.ModelForm):
    """
    Form used to create or update a contribution towards a goal.
    Validates that the contribution amount is positive.
    """
    class Meta:
        model = Contribution
        fields = ['amount']

    def clean_amount(self):
        """
        Validates that the contribution amount is positive.

        Returns:
            amount (float): The valid contribution amount.

        Raises:
            forms.ValidationError: If the amount is less than or equal to 0.
        """
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError('Amount must be positive.')
        return amount
