from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm, IncomeForm, ExpenseForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Income, Expense

# Create your views here.
def base(request):
    return render(request, 'base.html')

def user_register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Username or password is incorrect')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    # budgets = Budget.objects.filter(owner=request.user)
    # user_goals = UserGoal.objects.filter(user=request.user)

    # context = {
    #     'budgets': budgets,
    #     'user_goals': user_goals,
    # }
    # return render(request, 'dashboard.html', context)
    return render(request, 'dashboard.html')

@login_required
def budgets(request):
    return render(request, 'budgets.html')

@login_required
def goals(request):
    return render(request, 'goals.html')

@login_required
def transactions(request):
    expenses = Expense.objects.filter(user=request.user)
    incomes = Income.objects.filter(user=request.user)
    return render(request, 'transactions.html', {'expenses':expenses, 'incomes':incomes})

@login_required
def add_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income = form.save()
            return redirect('transactions')
    else:
        form = IncomeForm()
    return render(request, 'add_income.html', {'form': form})

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense = form.save()
            return redirect('transactions')
    else:
        form = ExpenseForm()
    return render(request, 'add_expense.html', {'form': form})
