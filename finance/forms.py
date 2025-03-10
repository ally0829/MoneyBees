# import models
from finance.models import Income, Expense, ExpenseCategory, MonthlyExpenseTarget, IncomeCategory
from users.models import User
# import forms
# from finance.views import fetch_exchange_rates
from django import forms
from datetime import date


class IncomeForm(forms.ModelForm):
    currency_code = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Income
        fields = ['date', 'category', 'amount', 'description']  # Currency is third in order
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'max': date.today().strftime('%Y-%m-%d')}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('initial', {}).get('user', None)
        exchange_rates = kwargs.pop('exchange_rates', {})
        super().__init__(*args, **kwargs)

        self.fields['category'].queryset = IncomeCategory.objects.all()

        if user and user.currency:
            self.fields['amount'].label = "Amount"

        if exchange_rates and 'rates' in exchange_rates:
            rates = exchange_rates['rates']
            currency_choices = [(currency, currency) for currency in rates.keys()]

            # Adding a new currency field at the third position
            self.fields['currency_display'] = forms.ChoiceField(
                choices=currency_choices,
                label="Currency",
                initial=user.currency.currency if user and user.currency else 'USD',  # Default to 'USD'
            )

            # Reorder fields to ensure currency is third in display order
            self.order_fields(['date', 'category', 'currency_display', 'currency', 'amount', 'description'])


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'category', 'amount', 'description']  # Currency remains third in order
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'max': date.today().strftime('%Y-%m-%d')}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('initial', {}).get('user', None)
        exchange_rates = kwargs.pop('exchange_rates', {})
        super().__init__(*args, **kwargs)

        # Set the category queryset
        self.fields['category'].queryset = ExpenseCategory.objects.all()

        # Update the amount label with the user's currency
        if user and user.currency:
            self.fields['amount'].label = "Amount"

        # Populate the currency field with the exchange rates
        if exchange_rates and 'rates' in exchange_rates:
            rates = exchange_rates['rates']
            currency_choices = [(currency, currency) for currency in rates.keys()]

            # Adding a new currency display field
            self.fields['currency_display'] = forms.ChoiceField(
                choices=currency_choices,
                label="Currency",
                initial=user.currency.currency if user and user.currency else 'USD',  # Default to 'USD'
            )

            # Reorder fields to ensure currency is third in display order
            self.order_fields(['date', 'category', 'currency_display', 'currency', 'amount', 'description'])