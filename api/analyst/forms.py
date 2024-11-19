# forms.py
from django import forms
from django.utils import timezone
from datetime import timedelta
from api.instagram.models import CustomFieldValue, CustomField
from .models import DataEntry


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


class DataEntryForm(forms.ModelForm):
    class Meta:
        model = DataEntry
        fields = ['name', 'chart_type', 'query']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'chart_type': forms.Select(attrs={'class': 'form-control'}),
            'query': forms.Textarea(attrs={'class': 'form-control'}),
        }
        extra_kwargs = {
            "id": {"required": False, "allow_null": True},
        }

class CustomFieldValueForm(forms.ModelForm):
    class Meta:
        model = CustomFieldValue
        fields = ['field', 'value']

    def __init__(self, *args, **kwargs):
        endpoint_id = kwargs.pop('endpoint_id', None)
        super().__init__(*args, **kwargs)
        
        # Filter fields if necessary
        if endpoint_id:
            self.fields['field'].queryset = CustomField.objects.all()  # Adjust as needed
        
        # Dynamically set widget based on field type
        if 'field' in self.data:
            try:
                field = CustomField.objects.get(id=self.data.get('field'))
                if field.data_type == 'text':
                    self.fields['value'] = forms.CharField(label='Value')
                elif field.data_type == 'number':
                    self.fields['value'] = forms.IntegerField(label='Value')
                elif field.data_type == 'date':
                    self.fields['value'] = forms.DateField(label='Value', widget=forms.SelectDateWidget())
                elif field.data_type == 'boolean':
                    self.fields['value'] = forms.BooleanField(label='Value', required=False)
                elif field.data_type == 'json':
                    self.fields['value'] = forms.CharField(label='Value')  # Accept JSON as string
            except CustomField.DoesNotExist:
                pass




class CombinedDataEntryForm(forms.ModelForm):
    # Assuming DataEntry has fields like 'name', 'chart_type', and 'query'
    class Meta:
        model = DataEntry
        fields = ['name', 'chart_type', 'query']  # Include the field for custom fields

    # Custom field value input will be dynamically updated in the view or template
    # value = forms.CharField(required=False)  # This will be dynamically updated based on selected custom field

    # Add a dropdown for selecting custom fields
    # field = forms.ModelChoiceField(queryset=CustomField.objects.all(), required=True)
    # In your forms.py
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
        self.fields['chart_type'].widget.attrs.update({'class': 'form-control'})
        self.fields['query'].widget.attrs.update({'class': 'form-control'})
        # self.fields['field'].widget.attrs.update({'class': 'form-control'})
        # self.fields['value'] = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))  # Add value field with class