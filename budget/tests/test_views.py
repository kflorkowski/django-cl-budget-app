import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.test import Client
from budget.models import Goal, Contribution, Category, Income, Expense
from datetime import datetime

# tests - views.base
@pytest.mark.django_db
def test_base_view_status_code(client):
    """
    Test that the 'base' view returns a status code 200 (OK) when accessed.
    This ensures that the view is accessible and responds correctly.
    """
    url = reverse('base')
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_base_view_title(client):
    """
    Test that the 'base' view contains the correct title in the HTML response.
    This ensures that the page title is correctly set as 'Budget App'.
    """
    url = reverse('base')
    response = client.get(url)
    assert '<title>Budget App</title>' in response.content.decode()


# tests - views.user_register
@pytest.mark.django_db
def test_user_register_valid_data(client):
    """
    Test that a user can successfully register with valid data.
    This test checks if the user is redirected to the login page after a successful registration.
    """
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password1': 'Test123!!',
        'password2': 'Test123!!',
    }

    response = client.post(reverse('register'), data)

    assert response.status_code == 302
    assert response.url == reverse('login')

@pytest.mark.django_db
def test_user_register_invalid_data(client):
    """
    Test that the registration fails when invalid data is provided.
    This test checks if the user is not redirected and if the form validation error for password mismatch appears.
    """
    url = reverse('register')
    data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password1': 'Test123!',
        'password2': 'password124',
    }
    response = client.post(url, data)

    assert response.status_code == 200
    assert 'password2' in response.content.decode()


# tests - views.user_login
@pytest.mark.django_db
def test_user_login_valid_data(client):
    """
    Test that a user can log in successfully with valid credentials.
    This test checks if the user is redirected to the dashboard after a successful login.
    """
    user = User.objects.create_user(username='testuser', password='testpassword')

    url = reverse('login')
    response = client.post(url, {'username': 'testuser', 'password': 'testpassword'})

    assert response.status_code == 302
    assert response.url == reverse('dashboard')

@pytest.mark.django_db
def test_user_login_invalid_data(client):
    """
    Test that login fails with invalid credentials.
    This test checks if the user sees an error message when providing incorrect login data.
    """
    url = reverse('login')
    response = client.post(url, {'username': 'wronguser', 'password': 'wrongpassword'})

    assert response.status_code == 200
    assert 'Username or password is incorrect' in response.content.decode()


# tests - views.user_logout
@pytest.mark.django_db
def test_user_logout_redirects(client):
    """
    Test that a logged-in user is redirected to the login page upon logout.
    This test ensures that after logging out, the user is redirected to the login page.
    """
    user = User.objects.create_user(username='testuser', password='Test123!')
    
    client.login(username='testuser', password='Test123!')

    response = client.get(reverse('logout'))

    assert response.status_code == 302
    assert response.url == reverse('login')

@pytest.mark.django_db
def test_user_logout_no_user_logged_in(client):
    """
    Test that a user who is not logged in is redirected to the login page when attempting to log out.
    This test ensures that even without a logged-in user, a logout request redirects to the login page.
    """
    response = client.get(reverse('logout'))

    assert response.status_code == 302
    assert response.url == reverse('login')


# tests - views.dashboard
@pytest.mark.django_db
def test_dashboard_view_status_code(client):
    """
    Test if the dashboard page loads with status code 200.
    This test ensures that the dashboard view returns the correct status code when accessed by a logged-in user.
    """
    user = User.objects.create_user(username='testuser', password='Test123!')
    client.login(username='testuser', password='Test123!')
    url = reverse('dashboard')
    response = client.get(url)
    
    assert response.status_code == 200

@pytest.mark.django_db
def test_dashboard_view_context_data(client):
    """
    Test if the correct context data is passed to the dashboard view.
    This test checks if the user's goals, category summary, and financial data are included in the context.
    """
    user = get_user_model().objects.create_user(username="testuser", password="password")
    client = Client()
    client.login(username="testuser", password="password")

    category = Category.objects.create(name="Test Category")
    goal = Goal.objects.create(
        owner=user,
        name="Test Goal",
        target_amount=500
    )
    Contribution.objects.create(goal=goal, contributor=user, amount=100)

    last_month = datetime.now().month - 1 if datetime.now().month > 1 else 12
    Income.objects.create(user=user, category=category, amount=200, date=datetime(datetime.now().year, last_month, 1))
    Expense.objects.create(user=user, category=category, amount=100, date=datetime(datetime.now().year, last_month, 1))

    response = client.get(reverse('dashboard'))

    assert response.status_code == 200

    assert 'user_goals' in response.context
    assert len(response.context['user_goals']) == 1
    assert response.context['user_goals'][0]['goal'].name == "Test Goal"
    assert response.context['user_goals'][0]['total_contributions'] == 100
    assert response.context['user_goals'][0]['progress'] == 20.0
    assert 'category_summary' in response.context
    assert len(response.context['category_summary']) == 1
    assert response.context['category_summary'][0]['category'].name == "Test Category"
    assert response.context['category_summary'][0]['total_expenses_in_category'] == 100
    assert response.context['category_summary'][0]['total_incomes_in_category'] == 200

    assert response.context['total_expenses'] == 100
    assert response.context['total_incomes'] == 200
    assert response.context['total_balance'] == 100


# tests - views.goals
@pytest.mark.django_db
def test_goals_view(client):
    """
    Test if the goals view displays the correct goal data for the user.
    This test checks if the user's goals, contributions, and the calculated amount and percentage are correctly shown.
    """
    user = User.objects.create_user(username='testuser', password='password')
    goal = Goal.objects.create(owner=user, name='Test Goal', target_amount=1000)
    Contribution.objects.create(goal=goal, contributor=user, amount=500)
    Contribution.objects.create(goal=goal, contributor=user, amount=100)

    client.login(username='testuser', password='password')

    response = client.get(reverse('goals'))

    assert 'my_goals' in response.context
    assert len(response.context['my_goals']) == 1

    goal = response.context['my_goals'][0]
    assert goal.current_amount == 600 
    assert goal.current_percentage == 60.0

@pytest.mark.django_db
def test_goals_view_no_goals(client):
    """
    Test if the goals view correctly handles the case when the user has no goals.
    This test checks if the correct message is displayed when the user has no goals.
    """
    user = User.objects.create_user(username='testuser2', password='password')

    client.login(username='testuser2', password='password')

    response = client.get(reverse('goals'))

    assert 'my_goals' in response.context
    assert len(response.context['my_goals']) == 0 

    assert 'No record yet.' in response.content.decode()


# tests - views.add_goal
@pytest.mark.django_db
def test_add_goal_form_render():
    """
    Test if the add goal form is rendered correctly for the user.
    This test checks if the form is displayed with the correct method and form elements.
    """
    user = User.objects.create_user(username='testuser', password='Testpassword1!')

    client = Client()
    client.login(username='testuser', password='Testpassword1!')

    response = client.get(reverse('add_goal'))

    assert response.status_code == 200
    assert 'Create Goal' in response.content.decode()
    assert '<form' in response.content.decode()
    assert 'method="POST"' in response.content.decode()

@pytest.mark.django_db
def test_add_goal_form_submission():
    """
    Test if the add goal form is submitted correctly and the goal is saved in the database.
    This test checks if the form data is correctly processed and if the user is redirected after submission.
    """
    user = User.objects.create_user(username='testuser', password='testpassword')
    client = Client()
    client.login(username='testuser', password='testpassword')

    data = {
        'name': 'New Goal',
        'description': 'This is a test goal.',
        'target_amount': 1000.00,
    }

    response = client.post(reverse('add_goal'), data)

    assert response.status_code == 302
    assert response.url == reverse('goals')

    goal = Goal.objects.first()
    assert goal is not None
    assert goal.name == 'New Goal'
    assert goal.description == 'This is a test goal.'
    assert goal.target_amount == 1000.00
    assert goal.owner == user


# tests - views.donation
@pytest.mark.django_db
def test_donation_form_render():
    """
    Test if the donation form is rendered correctly with the goal details.
    This test ensures the form is displayed with the correct method and includes necessary form elements.
    """
    user = User.objects.create_user(username='testuser', password='Testpassword1!')
    goal = Goal.objects.create(owner=user, name="Test Goal", target_amount=500)

    client = Client()
    client.login(username='testuser', password='Testpassword1!')

    response = client.get(reverse('donation', kwargs={'goal_id': goal.id}))

    assert response.status_code == 200
    assert f"Donate to goal: {goal.name}" in response.content.decode()
    assert '<form method="POST">' in response.content.decode()
    assert '<button type="submit">Donate</button>' in response.content.decode()

@pytest.mark.django_db
def test_donation_submission():
    """
    Test if the donation submission works correctly and the donation is saved.
    This test checks if the form submission redirects to the correct page and saves the donation in the database.
    """
    user = User.objects.create_user(username='testuser', password='Testpassword1!')
    goal = Goal.objects.create(owner=user, name="Test Goal", target_amount=500)

    client = Client()
    client.login(username='testuser', password='Testpassword1!')

    response = client.post(
        reverse('donation', kwargs={'goal_id': goal.id}),
        data={'amount': 100}
    )

    assert response.status_code == 302
    assert response.url == reverse('goals')

    contribution = Contribution.objects.filter(goal=goal, contributor=user).first()
    assert contribution is not None
    assert contribution.amount == 100


# tests - views.transactions
@pytest.mark.django_db
def test_transactions_view():
    """
    Test if the transactions view correctly displays the expense and income records.
    This test ensures that both expenses and incomes are displayed on the transactions page when they exist.
    """
    user = User.objects.create_user(username='testuser', password='Testpassword1!')
    category = Category.objects.create(name="Housing")

    expense = Expense.objects.create(user=user, name="Expense 1", amount=100, date="2024-11-19", category=category)
    income = Income.objects.create(user=user, name="Income 1", amount=200, date="2024-11-19", category=category)

    client = Client()
    client.login(username='testuser', password='Testpassword1!')

    response = client.get(reverse('transactions'))

    assert response.status_code == 200
    assert "Outcome" in response.content.decode()
    assert "Income" in response.content.decode()
    assert "Expense 1" in response.content.decode()
    assert "Income 1" in response.content.decode()

@pytest.mark.django_db 
def test_transactions_no_records():
    """
    Test if the transactions view displays a message when no transactions exist.
    This test checks that the 'No record yet.' message is shown when there are no expenses or incomes.
    """
    user = User.objects.create_user(username='testuser', password='Testpassword1!')

    client = Client()
    client.login(username='testuser', password='Testpassword1!')

    response = client.get(reverse('transactions'))

    assert response.status_code == 200
    assert "No record yet." in response.content.decode()


# tests - views.add_income
@pytest.mark.django_db
def test_add_income_form_render():
    """
    Test if the 'Add Income' form is rendered correctly.
    This test ensures that when the user visits the 'add_income' page, the form is displayed with the correct HTML.
    """
    user = User.objects.create_user(username='testuser', password='Testpassword1!')
    
    client = Client()
    client.login(username='testuser', password='Testpassword1!')
    
    response = client.get(reverse('add_income'))
    
    assert response.status_code == 200
    assert 'Add Income' in response.content.decode()
    assert '<form method="POST">' in response.content.decode()
    assert 'Add Income' in response.content.decode()

@pytest.mark.django_db
def test_add_income_form_submission():
    """
    Test if the 'Add Income' form successfully submits data and redirects.
    This test checks if valid data is posted to the form, causing the income to be created and the user to be redirected.
    """
    user = User.objects.create_user(username='testuser', password='Testpassword1!')
    category = Category.objects.create(name='Salary')
    
    client = Client()
    client.login(username='testuser', password='Testpassword1!')
    
    income_data = {
        'name': 'Salary',
        'amount': 2000,
        'category': category.id,
        'date': '2024-11-19',
    }
    response = client.post(reverse('add_income'), data=income_data)
    
    assert response.status_code == 302
    assert response.url == reverse('transactions')
    assert Income.objects.filter(name='Salary', amount=2000).exists()


# tests - views.add_expanse
@pytest.mark.django_db
def test_add_expense_form_render():
    """
    Test if the 'Add Expense' form is rendered correctly.
    This test ensures that when the user visits the 'add_expense' page, the form is displayed with the correct HTML.
    """
    user = User.objects.create_user(username='testuser', password='Testpassword1!')

    client = Client()
    client.login(username='testuser', password='Testpassword1!')

    response = client.get(reverse('add_expense'))

    assert response.status_code == 200
    assert 'Add Expense' in response.content.decode()
    assert '<form method="POST">' in response.content.decode()
    assert '<button type="submit">Add Expense</button>' in response.content.decode()

@pytest.mark.django_db
def test_add_expense_form_submission():
    """
    Test if the 'Add Expense' form successfully submits data and redirects.
    This test checks if valid data is posted to the form, causing the expense to be created and the user to be redirected.
    """
    user = User.objects.create_user(username='testuser', password='Testpassword1!')
    category = Category.objects.create(name='Housing')

    client = Client()
    client.login(username='testuser', password='Testpassword1!')

    data = {
        'name': 'Test Expense',
        'amount': 100,
        'date': '2024-11-19',
        'category': category.id,
    }

    response = client.post(reverse('add_expense'), data)

    assert response.status_code == 302
    assert Expense.objects.filter(name='Test Expense', amount=100).exists()


# tests - views.edit_income
@pytest.mark.django_db
def test_edit_income_form_submission(client):
    """
    Test if the 'Edit Income' form successfully updates an income transaction.
    This test checks if the user can update an existing income, with the correct category, amount, and date.
    """
    user = User.objects.create_user(username='testuser', password='Testpassword1!')
    category = Category.objects.create(name='Salary')
    
    income = Income.objects.create(
        user=user,
        name="Salary",
        amount=1000,
        category=category,
        date="2024-11-01"
    )
    
    client.login(username='testuser', password='Testpassword1!')
    
    form_data = {
        'name': 'Updated Salary',
        'category': category.id, 
        'amount': 1200,
        'date': '2024-11-15',
        'edit': 'edit', 
    }

    response = client.post(reverse('edit_income', kwargs={'transaction_id': income.id}), data=form_data)
    
    assert response.status_code == 302
    assert response.url == reverse('transactions')
    
    income.refresh_from_db()
    assert income.name == 'Updated Salary'
    assert income.amount == 1200

@pytest.mark.django_db
def test_delete_income():
    """
    Test if the 'Delete Income' action successfully deletes an income transaction.
    This test checks if the user can delete an existing income, and ensures it is removed from the database.
    """
    user = User.objects.create_user(username='testuser', password='Testpassword1!')
    category = Category.objects.create(name="Salary")  # Create category instance
    income = Income.objects.create(user=user, name="Test Income", amount=100, category=category, date="2024-01-01")
    
    client = Client()
    client.login(username='testuser', password='Testpassword1!')
    
    response = client.post(reverse('edit_income', kwargs={'transaction_id': income.id}), {'delete': 'Delete'})
    
    assert response.status_code == 302
    assert response.url == reverse('transactions')
    
    with pytest.raises(Income.DoesNotExist):
        Income.objects.get(id=income.id)


# tests - views.edit_expense
@pytest.mark.django_db
def test_edit_expense_form_submission(client):
    """
    Test if the 'Edit Expense' form successfully updates an expense transaction.
    This test checks if the user can update an existing expense with the correct category, amount, and date.
    """
    user = User.objects.create_user(username='testuser', password='Testpassword1!')
    category = Category.objects.create(name='Food')
    
    expense = Expense.objects.create(
        user=user,
        name="Lunch",
        amount=50,
        category=category,
        date="2024-11-01"
    )

    client.login(username='testuser', password='Testpassword1!')

    form_data = {
        'name': 'Updated Lunch',
        'category': category.id,  
        'amount': 60,
        'date': '2024-11-02',
        'edit': 'Save'
    }

    response = client.post(reverse('edit_expense', kwargs={'transaction_id': expense.id}), data=form_data)

    assert response.status_code == 302

    expense.refresh_from_db()
    assert expense.name == 'Updated Lunch'
    assert expense.amount == 60
    assert str(expense.date) == '2024-11-02'

@pytest.mark.django_db
def test_delete_expense(client):
    """
    Test if the 'Delete Expense' action successfully deletes an expense transaction.
    This test checks if the user can delete an existing expense, and ensures it is removed from the database.
    """
    user = User.objects.create_user(username='testuser', password='Testpassword1!')
    category = Category.objects.create(name='Transportation') 
    
    expense = Expense.objects.create(
        user=user,
        name="Taxi Ride",
        amount=30,
        category=category,
        date="2024-11-01"
    )

    client.login(username='testuser', password='Testpassword1!')

    response = client.post(reverse('edit_expense', kwargs={'transaction_id': expense.id}), data={'delete': 'Delete'})

    assert response.status_code == 302

    with pytest.raises(Expense.DoesNotExist):
        expense.refresh_from_db()


# tests - views.budgets
@pytest.mark.django_db
def test_budgets_view(client):
    """
    Test if the 'Budgets' view correctly calculates total income, total expenses, 
    and net budget for a given date range.
    This test checks if the view works correctly when a custom date range is provided.
    """
    user = User.objects.create_user(username='testuser', password='Testpassword1!')
    category1 = Category.objects.create(name='Salary')
    category2 = Category.objects.create(name='Rent')

    Income.objects.create(user=user, name='Salary', amount=2000, category=category1, date='2024-11-01')
    Expense.objects.create(user=user, name='Rent', amount=800, category=category2, date='2024-11-01')

    client.login(username='testuser', password='Testpassword1!')

    response = client.get(reverse('budgets') + '?start_date=2024-11-01&end_date=2024-11-30')

    assert response.status_code == 200

    assert 'start_date' in response.context
    assert 'end_date' in response.context
    assert response.context['start_date'] == '2024-11-01'
    assert response.context['end_date'] == '2024-11-30'
    assert response.context['total_income'] == 2000
    assert response.context['total_expenses'] == 800
    assert response.context['net_budget'] == 1200

@pytest.mark.django_db
def test_budgets_view_default_dates(client):
    """
    Test if the 'Budgets' view correctly calculates total income, total expenses, 
    and net budget using the default date range (current month).
    This test checks if the view works correctly when no date range is provided and defaults are used.
    """
    user = User.objects.create_user(username='testuser', password='Testpassword1!')
    category1 = Category.objects.create(name='Salary')
    category2 = Category.objects.create(name='Rent')

    Income.objects.create(user=user, name='Salary', amount=2000, category=category1, date='2024-11-01')
    Expense.objects.create(user=user, name='Rent', amount=800, category=category2, date='2024-11-01')

    client.login(username='testuser', password='Testpassword1!')

    response = client.get(reverse('budgets'))

    assert response.status_code == 200

    assert 'start_date' in response.context
    assert 'end_date' in response.context
    assert response.context['start_date'] == datetime.today().replace(day=1).strftime('%Y-%m-%d')
    assert response.context['end_date'] == datetime.today().strftime('%Y-%m-%d')
    assert response.context['total_income'] == 2000
    assert response.context['total_expenses'] == 800
    assert response.context['net_budget'] == 1200
