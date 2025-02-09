import requests

url = "http://127.0.0.1:8000/generate-qr/"
data = {"url": "https://example.com"}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=data, headers=headers)
print(response.json())