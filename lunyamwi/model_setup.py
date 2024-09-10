import requests



def setup_agent(payload = None):
    url = os.getenv("SCRIPTING_URL") + '/agentSetup/'
    print(url)
    # import pdb;pdb.set_trace()
    resp = requests.post(url, data=json.dumps(payload),headers = {'Content-Type': 'application/json'})
    response = resp.json()
    return response

