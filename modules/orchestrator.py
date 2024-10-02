import gradio as gr
import requests
import json

def test_endpoint(url, method, data=None):
    headers = {"Content-Type": "application/json"}
    try:
        if data:
            data = json.loads(data)
        response = requests.request(method, url, json=data, headers=headers)
        return response.status_code, response.json()
    except Exception as e:
        return str(e)

iface = gr.Interface(fn=test_endpoint, inputs=["text", gr.Radio(["GET", "POST", "PUT", "PATCH"]), "text"], outputs=["text", "text"])
iface.launch()

