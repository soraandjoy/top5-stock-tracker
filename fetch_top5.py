#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
fetch_top5.py
Google Apps Script 웹앱(GAS)에서 데이터를 가져와
  - snapshots/YYYY-MM-DD_HHMM.json
  - data/latest.json
파일을 생성합니다.

✅ 실행 순서
1. 아래 CONFIG 부분에 본인의 GAS 웹앱 주소를 넣는다.
2. python fetch_top5.py 실행
3. 결과 JSON 파일을 커밋 & 푸시하면 index.html에서 자동 표시됨.
"""

import os, json, time, datetime as dt, requests
from pathlib import Path

# ==========================================================
# 🟢🟢🟢 여기에 본인의 Google Apps Script 웹앱(Deploy → /exec) URL을 넣으세요 🟢🟢🟢
GAS_ENDPOINT = "https://script.google.com/macros/s/AKfycbx16B3IAsUGttUiRS2BJg9gzut5BnRp7QdUx31-Yr9oCTdwzY96WhQXW5JV5aWh-qQA0A/exec"
# 예: "https://script.google.com/macros/s/AKfycbwACq7R.../exec"
# ==========================================================

DATA_DIR = Path("data")
SNAP_DIR = Path("snapshots")

# 미국 동부시간(ET)
ET_TZ = dt.timezone(dt.timedelta(hours=-4))


def now_et():
    return dt.datetime.now(ET_TZ)


def ts_ms():
    return int(time.time() * 1000)


def fetch_from_gas(params=None, timeout=20):
    if params is None:
        params = {}
    params["t"] = str(ts_ms())  # 캐시 방지
    r = requests.get(GAS_ENDPOINT, params=params, timeout=timeout, headers={
        "Cache-Control": "no-cache"
    })
    r.raise_for_status()
    try:
        return r.json()
    except Exception:
        raise RuntimeError(f"Invalid JSON from GAS: {r.text[:200]}...")


def save_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def main():
    DATA_DIR.mkdir(exist_ok=True)
    SNAP_DIR.mkdir(exist_ok=True)

    data = fetch_from_gas()
    now = now_et()
    if "date" not in data:
        data["date"] = now.strftime("%Y-%m-%d")
    if "updatedAt" not in data:
        data["updatedAt"] = ts_ms()

    snap_name = now.strftime("%Y-%m-%d_%H%M.json")
    save_json(SNAP_DIR / snap_name, data)
    save_json(DATA_DIR / "latest.json", data)

    print(f"[OK] snapshot → {SNAP_DIR / snap_name}")
    print(f"[OK] latest.json → {DATA_DIR / 'latest.json'}")
    print(f"Items: {len(data.get('items', []))}, Date(ET): {data['date']}")


if __name__ == "__main__":
    main()
