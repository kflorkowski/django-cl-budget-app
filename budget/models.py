from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal_name = models.CharField(max_length=64)
    goal_description = models.CharField(max_length=512)
    goal_value = models.DecimalField(max_digits=21, decimal_places=2)

    def __str__(self):
        return f'{self.user.username} - {self.goal_name}'


class Category(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name
    

class Budget(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    date = models.DateField()
    budget = models.ManyToManyField(Category, related_name='category')

    def __str__(self):
        return f'{self.name} - {self.date.strftime("%B %Y")}'


class Expense(models.Model):
    name = models.CharField(max_length=128)
    amount = models.DecimalField(max_digits=21, decimal_places=2)
    category = models.ForeignKey(Category, related_name='expense', on_delete=models.CASCADE)
    budget = models.ForeignKey(Budget, related_name='expense', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}: {self.amount}'


class Income(models.Model):
    name = models.CharField(max_length=128)
    amount = models.DecimalField(max_digits=21, decimal_places=2)
    category = models.ForeignKey(Category, related_name='income', on_delete=models.CASCADE)
    budget = models.ForeignKey(Budget, related_name='income', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}: {self.amount}'
