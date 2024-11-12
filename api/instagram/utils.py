import os
import json
import yaml

from django.contrib.contenttypes.models import ContentType
from .models import SimpleHttpOperatorModel, WorkflowModel, Endpoint, CustomFieldValue, CustomField, DagModel,HttpOperatorConnectionModel
from django.conf import settings

from api.helpers.dag_generator import generate_dag

import pandas as pd



def combine_dicts(group):
    combined_dict = {}
    for _, row in group.iterrows():
        combined_dict.update(row.dropna().to_dict())
    return combined_dict


def merge_lists_by_timestamp(dict_list):
    df = pd.DataFrame(dict_list)
    df['created_at'] = pd.to_datetime(df['created_at'])

    # Round the created_at values to the nearest minute
    df['created_at'] = df['created_at'].dt.round('min')
    return df.groupby('created_at').apply(combine_dicts).tolist()



def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if not parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def flatten_dict_list(dict_list, parent_key='', sep='_'):
    items = []
    for d in dict_list:
        if isinstance(d, dict):
            items.extend(flatten_dict(d, parent_key, sep=sep).items())
        else:
            items.append((parent_key, d))
    return dict(items)

def remove_timestamp(dict_):
    if "_created_at" in dict_:
        try:
            del dict_['_created_at']
        except Exception as err:
            print(err)
    return dict_



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
    data_points = []
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
            ).select_related('field')

            for custom_field_value in custom_fields_with_value:
                data_points.append({
                    custom_field_value.field.name: custom_field_value.value,
                    "created_at": custom_field_value.created_at
                })

            operator['data'] = remove_timestamp(flatten_dict_list(merge_lists_by_timestamp(data_points)))
            
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