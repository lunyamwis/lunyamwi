import os
import json
import yaml

from django.contrib.contenttypes.models import ContentType
from .models import SimpleHttpOperatorModel, WorkflowModel, Endpoint, CustomFieldValue, CustomField, DagModel,HttpOperatorConnectionModel
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
    dag_ = DagModel.objects.filter(workflow__id = workflow.id)
    dag = dag_.latest('created_at')
    operators = [entry for entry in dag.simplehttpoperatormodel_set.filter().values()]
    for operator in operators:
        try:
            operator['http_conn_id'] = HttpOperatorConnectionModel.objects.get(id=operator['connection_id']).connection_id
            endpoint = Endpoint.objects.get(id=operator['endpointurl_id'])
            operator['endpoint'] = endpoint.url
            operator['method'] = endpoint.method
            # Get the content type for the Endpoint model
            endpoint_content_type = ContentType.objects.get_for_model(Endpoint)
            # Query to get all custom fields and their values for the given end
            custom_fields_with_value = CustomFieldValue.objects.filter(
                content_type=endpoint_content_type,
                object_id=endpoint.id
            ).select_related('field').latest('created_at')
            operator['data'] = custom_fields_with_value.value
            
        except Exception as error:
            print(str(error))

    
    data = {
        "dag":[entry for entry in dag_.values()],
        "operators":operators,
        "data_seconds":[str(workflow.delay_durations)]
    }

    
    # Write the dictionary to a YAML file
    yaml_file_path = os.path.join(settings.BASE_DIR, 'api', 'helpers', 'include', 'dag_configs', f"{dag.dag_id}_config.yaml")
    with open(yaml_file_path, 'w') as yaml_file:
        try:
            yaml.dump(data, yaml_file, default_flow_style=False)
        except Exception as error:
            print(str(error))

    try:
        generate_dag(workflow_type=workflow.workflow_type)
    except Exception as error:
        print(str(error))


def dag_fields_to_exclude():
    return [
            "id",
            "timetable",
            "start_date",
            "end_date",
            "full_filepath",
            "template_searchpath",
            "template_undefined",
            "user_defined_macros",
            "user_defined_filters",
            "default_args",
            "concurrency",
            "max_active_tasks",
            "max_active_runs",
            "dagrun_timeout",
            "sla_miss_callback",
            "default_view",
            "orientation",
            "catchup",
            "on_success_callback",
            "on_failure_callback",
            "doc_md",
            "params",
            "access_control",
            "is_paused_upon_creation",
            "jinja_environment_kwargs",
            "render_template_as_native_obj",
            "tags",
            "owner_links",
            "auto_register",
            "fail_stop",
            "trigger_url",
            "trigger_url_expected_response",
            "workflow",
        ]