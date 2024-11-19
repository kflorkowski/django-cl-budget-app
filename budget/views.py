from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm, IncomeForm, ExpenseForm, GoalForm, ContributionForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Income, Expense, Goal, Contribution, Category
from django.db.models import Sum
from datetime import datetime
from django.views.generic import TemplateView
from django.db import models

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

class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        user_goals = Goal.objects.filter(owner=self.request.user)
        goals_with_progress = []
        for goal in user_goals:
            total_contributions = Contribution.objects.filter(goal=goal).aggregate(total=Sum('amount'))['total'] or 0
            progress = (total_contributions / goal.target_amount) * 100 if goal.target_amount > 0 else 0
            goals_with_progress.append({
                'goal': goal,
                'total_contributions': total_contributions,
                'progress': progress,
            })
        
        user_contribution = Contribution.objects.filter(contributor=self.request.user)
        other_contribution = Contribution.objects.exclude(contributor=self.request.user).filter(goal__in=user_goals)
        
        last_month = datetime.now().month - 1 if datetime.now().month > 1 else 12
        category_summary = []
        
        total_expenses = 0
        total_incomes = 0
        
        for category in Category.objects.all():
            category_expenses = Expense.objects.filter(category=category, user=self.request.user, date__month=last_month)
            category_incomes = Income.objects.filter(category=category, user=self.request.user, date__month=last_month)

            total_expenses_in_category = category_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
            total_incomes_in_category = category_incomes.aggregate(Sum('amount'))['amount__sum'] or 0

            category_summary.append({
                'category': category,
                'total_expenses_in_category': total_expenses_in_category,
                'total_incomes_in_category': total_incomes_in_category,
            })
            
            total_expenses += total_expenses_in_category
            total_incomes += total_incomes_in_category
        
        total_balance = total_incomes - total_expenses
        
        context.update({
            'user_goals': goals_with_progress,
            'user_contribution': user_contribution,
            'other_contribution': other_contribution,
            'category_summary': category_summary,
            'total_expenses': total_expenses,
            'total_incomes': total_incomes,
            'total_balance': total_balance,
        })
        return context
    
@login_required
def goals(request):
    my_goals = Goal.objects.filter(owner=request.user)
    others_goals = Goal.objects.exclude(owner=request.user)

    for goal in my_goals:
        total_contributions = Contribution.objects.filter(goal=goal).aggregate(total_amount=models.Sum('amount'))['total_amount'] or 0
        goal.current_amount = total_contributions
        goal.current_percentage = round((total_contributions / goal.target_amount) * 100, 2) if goal.target_amount > 0 else 0

    for goal in others_goals:
        total_contributions = Contribution.objects.filter(goal=goal).aggregate(total_amount=models.Sum('amount'))['total_amount'] or 0
        goal.current_amount = total_contributions
        goal.current_percentage = round((total_contributions / goal.target_amount) * 100, 2) if goal.target_amount > 0 else 0

    return render(request, 'goals.html', {'my_goals': my_goals, 'others_goals': others_goals})

@login_required
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

@login_required
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

@login_required
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

@login_required
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

@login_required
def budgets(request):
    start_date = request.GET.get('start_date', datetime.today().replace(day=1).strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', datetime.today().strftime('%Y-%m-%d'))

    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        start_date_obj = datetime.today().replace(day=1)
        end_date_obj = datetime.today()

    total_income = Income.objects.filter(
        user=request.user,
        date__range=[start_date_obj, end_date_obj]
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    total_expenses = Expense.objects.filter(
        user=request.user,
        date__range=[start_date_obj, end_date_obj]
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    net_budget = total_income - total_expenses

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_budget': net_budget,
    }

    return render(request, 'budgets.html', context)