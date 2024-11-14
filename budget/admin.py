from django.contrib import admin
from .models import UserGoal, Budget, Category, Expense, Income

# Register your models here.
admin.site.register(UserGoal)
admin.site.register(Budget)
admin.site.register(Category)
admin.site.register(Expense)
admin.site.register(Income)