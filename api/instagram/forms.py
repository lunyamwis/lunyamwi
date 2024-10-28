from django import forms
from .models import DagModel, SimpleHttpOperatorModel, WorkflowModel

class DagModelForm(forms.ModelForm):
    class Meta:
        model = DagModel
        exclude = ['id']
        

class SimpleHttpOperatorModelForm(forms.ModelForm):
    class Meta:
        model = SimpleHttpOperatorModel
        exclude = ['id']
        
class WorkflowModelForm(forms.ModelForm):
    class Meta:
        model = WorkflowModel
        fields = ['name', 'delay_durations']
        extra_kwargs = {
            "id": {"required": False, "allow_null": True},
        }

    

simpleHttpOperatorFormSet = forms.modelformset_factory(SimpleHttpOperatorModel, fields='__all__', extra=1)
dagFormSet = forms.modelformset_factory(DagModel, fields='__all__', extra=1)
