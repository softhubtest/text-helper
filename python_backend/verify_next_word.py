import requests
import json

def test_next_word():
    url = "http://localhost:8080/api/v1/predict"
    
    # Text with second word prefix
    payload = {
        "text": "merhaba s",
        "max_suggestions": 5,
        "use_ai": True,
        "use_search": True
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        data = response.json()
        print("Suggestions:")
        for s in data.get("suggestions", []):
            print(f"- {s['text']} ({s['type']}) score: {s['score']}")
            
        if not data.get("suggestions"):
            print("FAIL: No suggestions returned for 'merhaba '")
        else:
            print("SUCCESS: Suggestions returned")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_next_word()
