from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Create your models here.
class Goal(models.Model):
    """
    Represents a financial goal that a user can set. The goal can be contributed to by multiple users.
    Each goal has a target amount and a description.
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_goals')
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    contributor = models.ManyToManyField(User, through='Contribution', related_name='contributed_goals')
    target_amount = models.DecimalField(max_digits=21, decimal_places=2)


class Contribution(models.Model):
    """
    Represents a contribution made by a user to a specific goal. Tracks the amount contributed and the date.
    """
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    contributor = models.ForeignKey(User, on_delete=models.CASCADE, )
    amount = models.DecimalField(max_digits=21, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.contributor} → {self.goal}: {self.amount}"


class Category(models.Model):
    """
    Represents a category for organizing expenses and income, such as 'Health', 'Personal', etc.
    """
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Expense(models.Model):
    """
    Represents an expense made by a user. An expense is associated with a category and a specific amount.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    amount = models.DecimalField(max_digits=21, decimal_places=2)
    category = models.ForeignKey(Category, related_name='expense', on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f'{self.name}: {self.amount}'


class Income(models.Model):
    """
    Represents an income earned by a user. An income is associated with a category and a specific amount.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    amount = models.DecimalField(max_digits=21, decimal_places=2)
    category = models.ForeignKey(Category, related_name='income', on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f'{self.name}: {self.amount}'
