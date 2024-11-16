from django.contrib import admin
from .models import Goal, Contribution, Category, Expense, Income

# Register your models here.
admin.site.register(Goal)
admin.site.register(Contribution)
admin.site.register(Category)
admin.site.register(Expense)
admin.site.register(Income)