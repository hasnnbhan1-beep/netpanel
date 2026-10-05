import requests

url = "https://api.binance.com/api/v3/ticker/price"
headers = {"User-Agent": "Mozilla/5.0"}

resp = requests.get(url, headers=headers, timeout=30)
resp.raise_for_status()
data = resp.json()
print(data)
