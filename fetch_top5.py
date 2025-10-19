import yfinance as yf
import pandas as pd
import json, os
from datetime import datetime

# 📂 data 폴더가 없으면 자동으로 생성
os.makedirs("data", exist_ok=True)

# 📅 오늘 날짜 (파일명에 사용 가능)
today = datetime.now().strftime("%Y-%m-%d")

# 예시: 미국 대형주 리스트 (간단하게 일부만 사용)
tickers = ["AAPL", "MSFT", "AMZN", "GOOG", "META", "NVDA", "TSLA", "NFLX", "AVGO", "AMD"]

# 오늘 하루 주가 상승률 계산
data = []
for t in tickers:
    try:
        df = yf.download(t, period="2d", interval="1d", progress=False)
        if len(df) < 2:
            continue
        change = (df["Close"].iloc[-1] - df["Close"].iloc[-2]) / df["Close"].iloc[-2] * 100
        data.append({"symbol": t, "change": round(change, 2)})
    except Exception as e:
        print(f"Error for {t}: {e}")

# 상승률 기준으로 상위 5개 추리기
top5 = sorted(data, key=lambda x: x["change"], reverse=True)[:5]

# 각 주식의 오늘 1일 변동 데이터를 추가로 가져오기
results = []
for stock in top5:
    symbol = stock["symbol"]
    hist = yf.download(symbol, period="1d", interval="15m", progress=False)
    hist.reset_index(inplace=True)
    hist["Datetime"] = hist["Datetime"].astype(str)  # JSON 변환을 위해 문자열화
    stock["today_data"] = hist.to_dict(orient="records")
    results.append(stock)

# JSON 파일로 저장 (data/top5.json)
output_path = "data/top5.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump({"date": today, "top5": results}, f, indent=2, ensure_ascii=False)

print(f"✅ Saved {output_path}")
