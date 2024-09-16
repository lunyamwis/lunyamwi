from airflow import DAG
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.sensors.http_sensor import HttpSensor
from airflow.utils.dates import days_ago
from datetime import timedelta
import json

dag = DAG(
    "get_followers",
    schedule_interval="10 10 29 1 *",
    start_date=days_ago(1),
    catchup=False,
)

# Define the HTTP operator
http_task = SimpleHttpOperator(
    task_id='http_task',
    http_conn_id='your_http_connection',  # Specify the HTTP connection ID
    endpoint='instagram/scrapFollowersOrSimilarAccounts/',  # Specify the endpoint to hit
    method='POST',  # Specify the HTTP method
    headers={'Content-Type': 'application/json'}, # Add any headers if needed
    data=json.dumps({'accounts': ['Booksybiz', 'Wahlpro', 'Titanbarber', 'Official cuts', 'Unitedbyshorthair', 'Behindthechair', 'Ruelrockstar', 'Underratedbarbers', 'Humblythegreatest', 'Arodpr23', 'Phillipwolf'], 'get_followers': 1, 'negative_keywords': ['booksy', 'Supplier', 'Supply', 'supplies', 'manufacturer', 'wholesaler', 'shipping', 'dentist', 'Massage Therapist', 'Therapist', 'onlyfans'], 'positive_keywords': ['hair', 'appointment', 'appointments', 'book', 'call', 'licensed', 'cutz', 'kutz', 'cuts', 'cut', 'hairstylist', 'salon', 'salons', 'educator', 'specialist', 'beauty', 'walk', 'text', 'dm', 'hair', 'stylist', 'colour', 'colouring', 'loreal', 'olaplex', 'hairspray', 'mousse', 'pomade', 'hair oil', 'hair serum', 'scissors', 'comb', 'brush', 'blow dryer', 'flat iron', 'curling iron', 'hair rollers', 'hair clips', 'hair ties', 'headbands', 'hair accessories', 'updos', 'braids', 'twists', 'buns', 'ponytails', 'curls', 'waves', 'volume', 'texture', 'shine', 'frizz control', 'breakage', 'dryness', 'oiliness', 'thinning', 'hair loss', 'dandruff', 'scalp problems']}),  # Add any data if needed
    log_response=True,  # Log the response in the Airflow UI
    dag=dag,
)

# Set up task dependencies
http_task