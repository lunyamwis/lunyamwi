# forms.py
from django import forms
from django.utils import timezone
from datetime import timedelta

class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.TextInput(attrs={'type': 'date'}),
        label='Start Date'
    )
    end_date = forms.DateField(
        widget=forms.TextInput(attrs={'type': 'date'}),
        label='End Date'
    )

    def __init__(self, *args, **kwargs):
        super(DateRangeForm, self).__init__(*args, **kwargs)
        # Set default values for the past week
        today = timezone.now().date()
        last_week = today - timedelta(days=7)
        self.fields['start_date'].initial = last_week
        self.fields['end_date'].initial = today