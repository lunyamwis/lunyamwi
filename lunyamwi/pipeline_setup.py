import json
import requests
from .constants import LUNYAMWI_ML_BASE_URL


def setup_custom_field(payload=None):
    url = LUNYAMWI_ML_BASE_URL + '/custom-fields/'
    response = None
    try:
        resp = requests.post(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        response = resp.json()
    except Exception as err:
        print(err)
    return response

def update_custom_field(field_id, payload=None):
    url = LUNYAMWI_ML_BASE_URL + f'/custom-fields/{field_id}/'
    response = None
    try:
        resp = requests.patch(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        response = resp.json()
    except Exception as err:
        print(err)
    return response

def delete_custom_field(field_id):
    url = LUNYAMWI_ML_BASE_URL + f'/custom-fields/{field_id}/'
    response = None
    try:
        resp = requests.delete(url)
        response = resp.json()
    except Exception as err:
        print(err)
    return response

def list_custom_fields():
    url = LUNYAMWI_ML_BASE_URL + '/custom-fields/'
    response = None
    try:
        resp = requests.get(url)
        response = resp.json()
    except Exception as err:
        print(err)
    return response

def setup_custom_field_value(payload=None):
    url = LUNYAMWI_ML_BASE_URL + '/custom-field-values/'
    response = None
    try:
        resp = requests.post(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        response = resp.json()
    except Exception as err:
        print(err)
    return response

def update_custom_field_value(value_id, payload=None):
    url = LUNYAMWI_ML_BASE_URL + f'/custom-field-values/{value_id}/'
    response = None
    try:
        resp = requests.patch(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        response = resp.json()
    except Exception as err:
        print(err)
    return response

def delete_custom_field_value(value_id):
    url = LUNYAMWI_ML_BASE_URL + f'/custom-field-values/{value_id}/'
    response = None
    try:
        resp = requests.delete(url)
        response = resp.json()
    except Exception as err:
        print(err)
    return response

def list_custom_field_values():
    url = LUNYAMWI_ML_BASE_URL + '/custom-field-values/'
    response = None
    try:
        resp = requests.get(url)
        response = resp.json()
    except Exception as err:
        print(err)
    return response

def setup_endpoint(payload=None):
    url = LUNYAMWI_ML_BASE_URL + '/endpoints/'
    response = None
    try:
        resp = requests.post(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        response = resp.json()
    except Exception as err:
        print(err)
    return response

def update_endpoint(endpoint_id, payload=None):
    url = LUNYAMWI_ML_BASE_URL + f'/endpoints/{endpoint_id}/'
    response = None
    try:
        resp = requests.patch(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        response = resp.json()
    except Exception as err:
        print(err)
    return response

def delete_endpoint(endpoint_id):
    url = LUNYAMWI_ML_BASE_URL + f'/endpoints/{endpoint_id}/'
    response = None
    try:
        resp = requests.delete(url)
        response = resp.json()
    except Exception as err:
        print(err)
    return response

def list_endpoints():
    url = LUNYAMWI_ML_BASE_URL + '/endpoints/'
    response = None
    try:
        resp = requests.get(url)
        response = resp.json()
    except Exception as err:
        print(err)
    return response


def setup_connection(payload=None):
    url = LUNYAMWI_ML_BASE_URL + '/connections/'
    response = None
    try:
        resp = requests.post(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        response = resp.json()
    except Exception as err:
        print(err)
    return response

def update_connection(connection_id, payload=None):
    url = LUNYAMWI_ML_BASE_URL + f'/connections/{connection_id}/'
    response = None
    try:
        resp = requests.patch(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        response = resp.json()
    except Exception as err:
        print(err)
    return response

def delete_connection(connection_id):
    url = LUNYAMWI_ML_BASE_URL + f'/connections/{connection_id}/'
    response = None
    try:
        resp = requests.delete(url)
        response = resp.json()
    except Exception as err:
        print(err)
    return response

def list_connections():
    url = LUNYAMWI_ML_BASE_URL + '/connections/'
    response = None
    try:
        resp = requests.get(url)
        response = resp.json()
    except Exception as err:
        print(err)
    return response

def setup_workflow(payload=None):
    url = LUNYAMWI_ML_BASE_URL + '/workflows/'
    response = None
    try:
        resp = requests.post(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        response = resp.json()
    except Exception as err:
        print(err)
    return response

def update_workflow(workflow_id, payload=None):
   url = LUNYAMWI_ML_BASE_URL + f'/workflows/{workflow_id}/'
   response=None
   try:
       resp=requests.patch(url,data=json.dumps(payload),headers={'Content-Type':'application/json'})
       response=resp.json()
   except Exception as err:
       print(err)
   return response

def delete_workflow(workflow_id):
   url=LUNYAMWI_ML_BASE_URL+f'/workflows/{workflow_id}/'
   response=None
   try:
       resp=requests.delete(url)
       if(resp.status_code==204): # No content status code indicates successful deletion.
           return {'success': True}
       else: 
           return {'success': False,'message':'Deletion failed'}
   except Exception as err: 
       print(err) 
   return {'success': False,'message':'An error occurred'}

def list_workflows():
   url=LUNYAMWI_ML_BASE_URL+'/workflows/'
   responses=None 
   try: 
       responses=requests.get(url) 
       if(responses.status_code==200): 
           return responses.json() 
       else: 
           return {'success':False,'message':'Failed to fetch workflows'} 
   except Exception as err: 
       print(err) 
   return {'success':False,'message':'An error occurred'}