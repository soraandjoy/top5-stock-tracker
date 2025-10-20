#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
fetch_top5.py
- Google Apps Script 웹앱(GAS)에서 JSON을 받아
  snapshots/YYYY-MM-DD_HHMM.json 과 data/latest.json 를 생성/갱신합니다.
- 로컬 없이도 GitHub Actions에서 실행하도록 설계.
"""

import os, json, time, datetime as dt, requests
from pathlib import Path

# ===== CONFIG =====
# ▶️ 우선순위: 환경변수 GAS_ENDPOINT > 아래 기본값
GAS_ENDPOINT = os.environ.get(
    "GAS_ENDPOINT",
    "https://script.google.com/macros/s/AKfycbwACq7RUHXNYDv6Qod_mSGjhzSIjatJZz4_2h-Lw5aRkuwSlIeAIJqlPQuxxrBnlsVGGw/exec"
)

DATA_DIR = Path("data")
SNAP_DIR = Path("snapshots")

# (간단 EDT 고정) — 필요시 zoneinfo로 개선 가능
ET_TZ = dt.timezone(dt.timedelta(hours=-4))

def now_et(): return dt.datetime.now(ET_TZ)
def ts_ms():  return int(time.time() * 1000)

def fetch_from_gas(params=None, timeout=30):
    if params is None: params = {}
    params["t"] = str(ts_ms())  # 캐시 바스터
    r = requests.get(GAS_ENDPOINT, params=params, timeout=timeout, headers={"Cache-Control": "no-cache"})
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
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SNAP_DIR.mkdir(parents=True, exist_ok=True)

    data = fetch_from_gas()
    now = now_et()

    # 최소 필드 보강
    data.setdefault("date", now.strftime("%Y-%m-%d"))
    data.setdefault("updatedAt", ts_ms())

    snap_name = now.strftime("%Y-%m-%d_%H%M.json")
    save_json(SNAP_DIR / snap_name, data)
    save_json(DATA_DIR / "latest.json", data)

    print(f"[OK] snapshot  → {SNAP_DIR / snap_name}")
    print(f"[OK] latest    → {DATA_DIR / 'latest.json'}")
    print(f"[INFO] items={len(data.get('items', []))} date(ET)={data['date']}")

if __name__ == "__main__":
    main()
