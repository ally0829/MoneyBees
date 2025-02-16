from django.db import models
from django.contrib.auth.models import AbstractUser
from users.models import User

class Income(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()
    date = models.DateField()
    description = models.CharField(max_length=128)
    
    class Meta:
        verbose_name_plural = "income"

    def __str__(self):
        return f"{self.user.firstname} - {self.amount}"

class ExpenseCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=128)
    
    class Meta:
        verbose_name_plural = "expense_category"

    def __str__(self):
        return self.name

class Expense(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    amount = models.IntegerField()
    date = models.DateField()
    
    class Meta:
        verbose_name_plural = "expense"

    def __str__(self):
        return f"{self.user.firstname} - {self.amount} in {self.category.name}"

class MonthlyExpenseTarget(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    target_amount = models.IntegerField()
    month = models.IntegerField()
    
    class Meta:
        verbose_name_plural = "monthly_expense_target"

    def __str__(self):
        return f"{self.user.firstname} - {self.target_amount} for {self.category.name}"
