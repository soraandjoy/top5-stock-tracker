import yfinance as yf
import pandas as pd
import json, os
from datetime import datetime

# 폴더 준비
os.makedirs("data", exist_ok=True)

# 오늘 날짜
today = datetime.now().strftime("%Y-%m-%d")

# 사용자가 지정한 주식 5개
stocks_to_fetch = [
    {"symbol": "TSLA", "name": "Tesla"},
    {"symbol": "AMZN", "name": "Amazon"},
    {"symbol": "AAPL", "name": "Apple"},
    {"symbol": "META", "name": "Facebook"},
    {"symbol": "GOOGL", "name": "Google"}
]

results = []

for stock in stocks_to_fetch:
    symbol = stock["symbol"]
    print(f"Fetching data for {symbol}...")
    try:
        # 오늘 하루 15분 단위 데이터
        hist = yf.download(symbol, period="1d", interval="15m", progress=False)
        hist.reset_index(inplace=True)
        hist["Datetime"] = hist["Datetime"].astype(str)
        data_list = hist.to_dict(orient="records")

        # 전일 대비 상승률
        prev = yf.download(symbol, period="2d", interval="1d", progress=False)
        change = 0
        if len(prev) == 2:
            change = round((prev["Close"].iloc[-1] - prev["Close"].iloc[-2]) / prev["Close"].iloc[-2] * 100, 2)

        results.append({
            "symbol": symbol,
            "name": stock["name"],
            "change": change,
            "today_data": data_list
        })
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")

# JSON 저장
output_path = "data/stocks.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump({"date": today, "stocks": results}, f, indent=2, ensure_ascii=False)

print(f"✅ Saved {output_path}")
