from typing import Any
from django import forms
from .models import DagModel, SimpleHttpOperatorModel, WorkflowModel,HttpOperatorConnectionModel, Endpoint, CustomFieldValue, CustomField
from .utils import dag_fields_to_exclude

dag_exclusions = dag_fields_to_exclude()

class DagModelForm(forms.ModelForm):
    class Meta:
        model = DagModel
        exclude = dag_exclusions
        widgets = {
            "dag_id": forms.TextInput(attrs={"class": "form-control", "placeholder": "Dag Id"}),
            "description": forms.TextInput(attrs={"class": "form-control", "placeholder": "Description"}),
            "schedule": forms.TextInput(attrs={"class": "form-control", "placeholder": "Schedule"}),
            "schedule_interval": forms.TextInput(attrs={"class": "form-control", "placeholder": "Schedule Interval"}),
        }
        

class SimpleHttpOperatorModelForm(forms.ModelForm):
    class Meta:
        model = SimpleHttpOperatorModel
        exclude = ['id','dag','http_conn_id','response_check','extra_options','xcom_push','log_response','urls','endpoint']
        widgets = {
            "task_id": forms.TextInput(attrs={"class": "form-control", "placeholder": "Task Id"}),
            "connection": forms.Select(attrs={"class": "form-control", "placeholder": "Connection"}),
            "method": forms.Select(choices=[("GET","GET"),("POST","POST")],attrs={"class": "form-control"}),    
            "endpointurl": forms.Select(attrs={"class": "form-control", "placeholder": "Endpointurl"}),
            "data": forms.TextInput(attrs={"class": "form-control", "placeholder": "Data"}),
            "headers": forms.TextInput(attrs={"class": "form-control", "placeholder": "Headers"}),
        }
        
class WorkflowModelForm(forms.ModelForm):
    class Meta:
        model = WorkflowModel
        fields = ['name', 'delay_durations','airflow_creds','workflow_type']
        extra_kwargs = {
            "id": {"required": False, "allow_null": True},
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Name"}),
            "delay_durations": forms.TextInput(attrs={"class": "form-control", "placeholder": "Delay Durations"}),
            "airflow_creds": forms.Select(attrs={"class": "form-control", "placeholder": "Airflow Creds"}),
            "workflow_type": forms.Select(
                choices=[
                    ("simple_httpoperators_sequential_run", "simple_httpoperators_sequential_run"),
                    ("simple_httpoperators_parallel_run", "simple_httpoperators_parallel_run"),
                ],
                attrs={"class": "form-control"}
            )
        }
        

    
class SimpleHttpOperatorBaseModelFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = SimpleHttpOperatorModel.objects.none()

class DagModelBaseModelFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = DagModel.objects.none()



SimpleHttpOperatorFormSet = forms.inlineformset_factory(DagModel,SimpleHttpOperatorModel, exclude=['id','dag','http_conn_id','response_check','extra_options','xcom_push','log_response','urls','endpoint'], extra=1,can_delete=True,can_delete_extra=False,form=SimpleHttpOperatorModelForm)
DagFormSet = forms.inlineformset_factory(WorkflowModel,DagModel, exclude=dag_exclusions, extra=1,can_delete=True,can_delete_extra=False,form=DagModelForm)



class HttpOperatorConnectionForm(forms.ModelForm):
    class Meta:
        model = HttpOperatorConnectionModel
        fields = ['connection_id', 'conn_type', 'host', 'port','login', 'password']



class WorkflowRunnerForm(forms.Form):

    push_to = forms.ChoiceField(choices=[('gcp','Google Cloud Platform'),('ssh','Secure Shell')],widget=forms.Select(attrs={"class": "form-control"}))
       


class EndpointForm(forms.ModelForm):
    class Meta:
        model = Endpoint
        fields = ['base_url','url', 'method']


# forms.py


class CustomFieldForm(forms.ModelForm):
    class Meta:
        model = CustomField
        fields = ['name', 'data_type']




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