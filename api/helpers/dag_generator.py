
from jinja2 import Environment, FileSystemLoader
# from airflow.models import TaskInstance
import yaml
import os

def generate_dag():
    file_dir  = os.path.dirname(os.path.abspath(f"{__file__}/"))
    print(file_dir)
    env = Environment(loader=FileSystemLoader(file_dir))
    template = env.get_template('include/templates/dag_template.jinja2')

    for filename in os.listdir(f"{file_dir}/include/dag_configs"):
        print(filename)
        if filename.endswith('yaml'):
            with open(f"{file_dir}/include/dag_configs/{filename}","r") as input_file:
                inputs = yaml.unsafe_load(input_file)
                with open(f"/opt/airflow/dags/{inputs['dag'][0]['dag_id']}.py","w") as f:
                    context = {
                        'task_instance': {}  # Example of task_instance context
                    }
                    f.write(template.render(inputs, **context))