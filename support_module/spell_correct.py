import requests
import json


def spelling_correct(text):
    url = "http://172.28.0.23:35213/spell-correct"
    data = json.dumps({
    "text": text
    })
    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=data)
    data = json.loads(response.content)
    return data['data']['result']
