from django.db import models
from django.contrib.auth.models import AbstractUser
from users.models import User

<<<<<<< HEAD
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

=======
>>>>>>> 03032025
class ExpenseCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=128)
    
    class Meta:
        verbose_name_plural = "expense_category"

    def __str__(self):
        return self.name
<<<<<<< HEAD
=======
    
class IncomeCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=128)
    
    class Meta:
        verbose_name_plural = "income_category"

    def __str__(self):
        return self.name

class Income(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date = models.DateField()
    description = models.CharField(max_length=256, default="")
    category = models.ForeignKey(IncomeCategory, on_delete=models.CASCADE, default=1)
    
    class Meta:
        verbose_name_plural = "income"

    def __str__(self):
        return f"{self.user.firstname} - {self.amount}"

>>>>>>> 03032025

class Expense(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
<<<<<<< HEAD
    amount = models.IntegerField()
    date = models.DateField()
    
=======
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date = models.DateField()
    description = models.CharField(max_length=256, default="")

>>>>>>> 03032025
    class Meta:
        verbose_name_plural = "expense"

    def __str__(self):
        return f"{self.user.firstname} - {self.amount} in {self.category.name}"

class MonthlyExpenseTarget(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
<<<<<<< HEAD
    target_amount = models.IntegerField()
=======
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
>>>>>>> 03032025
    month = models.IntegerField()
    
    class Meta:
        verbose_name_plural = "monthly_expense_target"

    def __str__(self):
        return f"{self.user.firstname} - {self.target_amount} for {self.category.name}"
