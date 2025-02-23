# import models
from finance.models import Income, Expense, ExpenseCategory, MonthlyExpenseTarget, IncomeCategory
from users.models import User
# import forms
from django import forms

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['date', 'category', 'amount', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('initial', {}).get('user', None)
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = IncomeCategory.objects.all()
        if user:
            self.fields['amount'].label = f"Amount ({user.currency})"

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'category', 'amount', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('initial', {}).get('user', None)
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ExpenseCategory.objects.all()
        if user:
            self.fields['amount'].label = f"Amount ({user.currency})"
