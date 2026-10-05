import requests
import csv

url = "https://api.binance.com/api/v3/ticker/price"
data = requests.get(url, timeout=30).json()

# احتفظ فقط بأزواج USDT ورتّبها أبجدياً
rows = sorted(
    [(d["symbol"], float(d["price"])) for d in data if d["symbol"].endswith("USDT")],
    key=lambda x: x[0]
)

with open("prices.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["symbol", "price"])
    w.writerows(rows)

print(f"تم حفظ {len(rows)} زوج USDT في prices.csv")
