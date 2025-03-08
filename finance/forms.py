# import models
from finance.models import Income, Expense, ExpenseCategory, MonthlyExpenseTarget, IncomeCategory
from users.models import User
# import forms
# from finance.views import fetch_exchange_rates
from django import forms


class IncomeForm(forms.ModelForm):
    # 添加一個隱藏的貨幣字段用於存儲貨幣代碼
    currency_code = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Income
        fields = ['date', 'category', 'amount', 'description']  # 移除 currency
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('initial', {}).get('user', None)
        exchange_rates = kwargs.pop('exchange_rates', {})
        super().__init__(*args, **kwargs)

        self.fields['category'].queryset = IncomeCategory.objects.all()

        if user and user.currency:
            self.fields['amount'].label = f"Amount ({user.currency})"

        # 添加一個選擇貨幣的下拉選單，但不是模型字段
        if exchange_rates and 'rates' in exchange_rates:
            rates = exchange_rates['rates']
            currency_choices = [(currency, currency)
                                for currency in rates.keys()]
            self.fields['currency_display'] = forms.ChoiceField(
                choices=currency_choices,
                label="Currency",
                initial=user.currency.currency if user and user.currency else None
            )


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'category', 'currency', 'amount', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('initial', {}).get('user', None)
        # Get exchange rates from kwargs
        exchange_rates = kwargs.pop('exchange_rates', {})
        super().__init__(*args, **kwargs)

        # Set the category queryset
        self.fields['category'].queryset = ExpenseCategory.objects.all()

        # Update the amount label with the user's currency
        if user and user.currency:
            self.fields['amount'].label = f"Amount ({user.currency})"

        # Populate the currency field with the exchange rates
        if exchange_rates and 'rates' in exchange_rates:
            rates = exchange_rates['rates']  # Access the 'rates' key
            currency_choices = [(currency, currency)
                                for currency in rates.keys()]
            self.fields['currency'].widget = forms.Select(
                choices=currency_choices)
