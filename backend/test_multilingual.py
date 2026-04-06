import requests
import json

url = "http://127.0.0.1:8000/api/v1/chat"
headers = {"Content-Type": "application/json"}

queries = [
    "Namaste", 
    "What is the fee for B.Tech?", 
    "Kem cho?"
]

for q in queries:
    print(f"\n--- Testing: '{q}' ---")
    data = {"query": q}
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        res_json = response.json()
        print(f"Response: {res_json.get('response')}")
        print(f"Language: {res_json.get('detected_language')}")
    except Exception as e:
        print(f"Error: {e}")
