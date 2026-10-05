import requests
import csv
from datetime import datetime

url = "https://api.binance.com/api/v3/ticker/24hr"
data = requests.get(url, timeout=30).json()
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

rows = [d for d in data if d["symbol"].endswith("USDT")]
rows.sort(key=lambda x: float(x["priceChangePercent"]), reverse=True)

with open("prices_24h.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["updated_at", "symbol", "price", "changePercent", "high", "low", "volume"])
    for d in rows:
        w.writerow([
            now,
            d["symbol"],
            d["lastPrice"],
            d["priceChangePercent"],
            d["highPrice"],
            d["lowPrice"],
            d["volume"],
        ])

print(f"[{now}] تم حفظ {len(rows)} زوج USDT")
