import requests
import json
import time

url = "http://127.0.0.1:8000/api/v1/chat"
headers = {"Content-Type": "application/json"}
data = {"query": "What are the fees?"}

print(f"Testing API at {url}...")
try:
    response = requests.post(url, headers=headers, json=data, timeout=30)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Request Failed: {e}")
