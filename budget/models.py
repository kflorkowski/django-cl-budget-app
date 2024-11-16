from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

# Create your models here.
class Goal(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_goals')
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    contributor = models.ManyToManyField(User, through='Contribution', related_name='contributed_goals')
    target_amount = models.DecimalField(max_digits=21, decimal_places=2)


class Contribution(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)
    contributor = models.ForeignKey(User, on_delete=models.CASCADE, )
    amount = models.DecimalField(max_digits=21, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.contributor} → {self.goal}: {self.amount}"


class Category(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


class Expense(models.Model):
    name = models.CharField(max_length=128)
    amount = models.DecimalField(max_digits=21, decimal_places=2)
    category = models.ForeignKey(Category, related_name='expense', on_delete=models.CASCADE)
    date = models.DateField(default=now)

    def __str__(self):
        return f'{self.name}: {self.amount}'


class Income(models.Model):
    name = models.CharField(max_length=128)
    amount = models.DecimalField(max_digits=21, decimal_places=2)
    category = models.ForeignKey(Category, related_name='income', on_delete=models.CASCADE)
    date = models.DateField(default=now)

    def __str__(self):
        return f'{self.name}: {self.amount}'
