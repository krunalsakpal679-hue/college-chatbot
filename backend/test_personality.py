import requests
import json

url = "http://127.0.0.1:8000/api/v1/chat"
headers = {"Content-Type": "application/json"}

queries = ["Hi", "Hello there", "What is the fee?"]

for q in queries:
    print(f"\n--- Testing: '{q}' ---")
    data = {"query": q}
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"Response: {response.json().get('response')}")
    except Exception as e:
        print(f"Error: {e}")
