import requests
import os
import json
from .constants import LUNYAMWI_ML_BASE_URL

def setup_analysis(payload=None):
    url = LUNYAMWI_ML_BASE_URL + '/api/dashboard/'
    response = None
    try:
        resp = requests.post(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        response = resp.json()
    except Exception as err:
        print(err)
    return response