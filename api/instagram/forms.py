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
        exclude = ['id','dag','http_conn_id','response_check','extra_options','xcom_push','log_response','urls']
        widgets = {
            "task_id": forms.TextInput(attrs={"class": "form-control", "placeholder": "Task Id"}),
            "connection": forms.Select(attrs={"class": "form-control", "placeholder": "Connection"}),
            "method": forms.Select(choices=[("GET","GET"),("POST","POST")],attrs={"class": "form-control"}),    
            "endpoint": forms.TextInput(attrs={"class": "form-control", "placeholder": "Endpoint"}),
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



SimpleHttpOperatorFormSet = forms.inlineformset_factory(DagModel,SimpleHttpOperatorModel, exclude=['id','dag','http_conn_id','response_check','extra_options','xcom_push','log_response','urls'], extra=1,can_delete=True,can_delete_extra=False,form=SimpleHttpOperatorModelForm)
DagFormSet = forms.inlineformset_factory(WorkflowModel,DagModel, exclude=dag_exclusions, extra=1,can_delete=True,can_delete_extra=False,form=DagModelForm)



class HttpOperatorConnectionForm(forms.ModelForm):
    class Meta:
        model = HttpOperatorConnectionModel
        fields = ['connection_id', 'conn_type', 'host', 'port','login', 'password']



class WorkflowRunnerForm(forms.Form):

    push_to = forms.ChoiceField(choices=[('gcp','Google Cloud Platform'),('ssh','Secure Shell')],widget=forms.Select(attrs={"class": "form-control"}))
       