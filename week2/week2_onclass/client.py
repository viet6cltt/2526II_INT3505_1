import requests

url = "http://localhost:5000/students"

response = requests.get(url)

print("Status code:", response.status_code)
print("Data:", response.json())