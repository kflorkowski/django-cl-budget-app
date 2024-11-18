from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm, IncomeForm, ExpenseForm, GoalForm, ContributionForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Income, Expense, Goal, Contribution

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
    user_goals = Goal.objects.filter(owner=request.user)
    user_contribution = Contribution.objects.filter(contributor=request.user)
    other_contribution = Contribution.objects.exclude(contributor=request.user).filter(goal__in=user_goals)

    context = {
    #     'budgets': budgets,
        'user_goals': user_goals,
        'user_contribution': user_contribution,
        'other_contribution': other_contribution,
    }
    return render(request, 'dashboard.html', context)

@login_required
def budgets(request):
    return render(request, 'budgets.html')

@login_required
def goals(request):
    my_goals = Goal.objects.filter(owner=request.user)
    others_goals = Goal.objects.exclude(owner=request.user)
    return render(request, 'goals.html', {'my_goals':my_goals, 'others_goals':others_goals})

def add_goal(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.owner = request.user
            goal = form.save()
            return redirect('goals')
    else:
        form = GoalForm()
    return render(request, 'add_goal.html', {'form':form})

def donation(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id)

    if request.method == 'POST':
        form = ContributionForm(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.goal = goal
            contribution.contributor = request.user
            contribution.save()
            return redirect('goals')
    else:
        form = ContributionForm
    return render(request, 'donate.html', {'form':form, 'goal':goal})

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

def edit_income(request, transaction_id):
    transaction = get_object_or_404(Income, id=transaction_id)
    form = IncomeForm(request.POST or None, instance=transaction)
    if request.method == 'POST':
        if 'edit' in request.POST and form.is_valid():
            form.save()
            return redirect('transactions')
        elif 'delete' in request.POST:
            transaction.delete()
            return redirect('transactions')
    return render(request, 'edit_transaction.html', {'form': form, 'type': 'income'})


def edit_expense(request, transaction_id):
    transaction = get_object_or_404(Expense, id=transaction_id)
    form = ExpenseForm(request.POST or None, instance=transaction)
    if request.method == 'POST':
        if 'edit' in request.POST and form.is_valid():
            form.save()
            return redirect('transactions')
        elif 'delete' in request.POST:
            transaction.delete()
            return redirect('transactions')
    return render(request, 'edit_transaction.html', {'form': form, 'type': 'expense'})
