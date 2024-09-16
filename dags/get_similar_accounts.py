from airflow import DAG
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.sensors.http_sensor import HttpSensor
from airflow.utils.dates import days_ago
from datetime import timedelta

dag = DAG(
    "get_similar_accounts",
    schedule_interval="0 17 26 1 *",
    start_date=days_ago(1),
    catchup=False,
)

# Define the HTTP endpoint sensor
http_sensor_task = HttpSensor(
    task_id='http_sensor_task',
    http_conn_id='your_http_connection',  # Specify the HTTP connection ID
    endpoint='your_endpoint',  # Specify the endpoint to hit
    response_check=lambda response: True if response.status_code == 200 else False,
    poke_interval=60,  # Set the interval to check the endpoint
    timeout=600,  # Set the timeout for the HTTP request
    dag=dag,
)

# Define the HTTP operator
http_task = SimpleHttpOperator(
    task_id='http_task',
    http_conn_id='your_http_connection',  # Specify the HTTP connection ID
    endpoint='instagram/scrapFollowersOrSimilarAccounts/',  # Specify the endpoint to hit
    method='POST',  # Specify the HTTP method
    headers={},  # Add any headers if needed
    data={'accounts': ['Booksybiz', 'Wahlpro', 'Titanbarber', 'Official cuts', 'Unitedbyshorthair', 'Behindthechair', 'Ruelrockstar', 'Underratedbarbers', 'Humblythegreatest', 'Arodpr23', 'Phillipwolf'], 'followers': 0},  # Add any data if needed
    log_response=True,  # Log the response in the Airflow UI
    dag=dag,
)

# Set up task dependencies
http_sensor_task >> http_task