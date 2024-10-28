import os
import json
import yaml
from .models import SimpleHttpOperatorModel, WorkflowModel, DagModel
from django.conf import settings
from api.helpers.dag_generator import generate_dag

def generate_dag_script(workflow):
    # if "trigger_url" in dag_data:
        
    #     data = {
    #         "dag":[entry for entry in DagModel.objects.filter(id = workflow.dag.id).values()],
    #         "operators":[entry for entry in workflow.simplehttpoperators.values()],
    #         "data_seconds":workflow.delay_durations,
    #         "trigger_url":dag_data.get("trigger_url"),
    #         "trigger_url_expected_response":dag_data.get("trigger_url_expected_response")
    #     }
    # else:
    data = {
        "dag":[entry for entry in DagModel.objects.filter(id = workflow.dag.id).values()],
        "operators":[entry for entry in workflow.simplehttpoperators.values()],
        "data_seconds":workflow.delay_durations
    }

    
    # Write the dictionary to a YAML file
    yaml_file_path = os.path.join(settings.BASE_DIR, 'api', 'helpers', 'include', 'dag_configs', f"{workflow.dag.dag_id}_config.yaml")
    with open(yaml_file_path, 'w') as yaml_file:
        try:
            yaml.dump(data, yaml_file, default_flow_style=False)
        except Exception as error:
            print(str(error))

    try:
        generate_dag()
    except Exception as error:
        print(str(error))