import requests
import json

url = "http://127.0.0.1:8080/api/v1/predict"
payload = {
    "text": "merhaba s",
    "use_ai": True,
    "use_search": True,
    "max_suggestions": 5
}
headers = {
    "Content-Type": "application/json"
}

try:
    print(f"Sending POST to {url} with {payload}")
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")
