from django import forms
from .models import Entry, Profit, Budget


class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['date', 'description', 'cost']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.TextInput(attrs={'placeholder': 'coffee, textbooks, rent...'}),
            'cost': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
        }


class ProfitForm(forms.ModelForm):
    class Meta:
        model = Profit
        fields = ['date', 'amount', 'note']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
            'note': forms.TextInput(attrs={'placeholder': 'optional note'}),
        }


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['amount', 'period']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
        }

