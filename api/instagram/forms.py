from typing import Any
from django import forms
from .models import DagModel, SimpleHttpOperatorModel, WorkflowModel,HttpOperatorConnectionModel
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
        exclude = ['id','dag']
        widgets = {
            "task_id": forms.TextInput(attrs={"class": "form-control", "placeholder": "Task Id"}),
            "http_conn_id": forms.TextInput(attrs={"class": "form-control", "placeholder": "Http Connection Id"}),
            "method": forms.TextInput(attrs={"class": "form-control", "placeholder": "Method"}),
            "endpoint": forms.TextInput(attrs={"class": "form-control", "placeholder": "Endpoint"}),
            "data": forms.TextInput(attrs={"class": "form-control", "placeholder": "Data"}),
            "headers": forms.TextInput(attrs={"class": "form-control", "placeholder": "Headers"}),
            "response_check": forms.TextInput(attrs={"class": "form-control", "placeholder": "Response Check"}),
            "extra_options": forms.TextInput(attrs={"class": "form-control", "placeholder": "Extra Options"}),
            "xcom_push": forms.CheckboxInput(attrs={"class": "form-control", "placeholder": "Xcom Push"}),
            "log_response": forms.CheckboxInput(attrs={"class": "form-control", "placeholder": "Log Response"}),
            "urls": forms.TextInput(attrs={"class": "form-control", "placeholder": "Urls"}),
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
                    ("simple_httpoperators_sequential_run", "Simple HTTP Operators Sequential Run"),
                    ("simple_httpoperators_parallel_run", "Simple HTTP Operators Parallel Run"),
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



SimpleHttpOperatorFormSet = forms.inlineformset_factory(DagModel,SimpleHttpOperatorModel, exclude=['id','dag'], extra=1,can_delete=True,can_delete_extra=False,formset=SimpleHttpOperatorBaseModelFormSet,form=SimpleHttpOperatorModelForm)
DagFormSet = forms.inlineformset_factory(WorkflowModel,DagModel, exclude=dag_exclusions, extra=1,can_delete=True,can_delete_extra=False,formset=DagModelBaseModelFormSet,form=DagModelForm)



class HttpOperatorConnectionForm(forms.ModelForm):
    class Meta:
        model = HttpOperatorConnectionModel
        fields = ['connection_id', 'conn_type', 'host', 'port','login', 'password']



class WorkflowRunnerForm(forms.Form):

    push_to = forms.ChoiceField(choices=[('gcp','Google Cloud Platform'),('ssh','Secure Shell')],widget=forms.Select(attrs={"class": "form-control"}))
       