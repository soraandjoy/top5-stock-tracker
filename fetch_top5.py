#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
fetch_top5.py
- Google Apps Script 웹앱(GAS)에서 Top5 데이터를 가져와 저장소에 스냅샷/최신본을 생성합니다.
- 사용 전 아래 CONFIG 값을 본인 레포 구조에 맞게 수정하세요.
- 일반적으로 로컬(또는 GitHub Actions)에서 실행 후 커밋/푸시하면 됩니다.

요구사항:
- Python 3.9+
- requests

pip install requests
"""

import os
import json
import time
import datetime as dt
from pathlib import Path
import requests

# ================== CONFIG ==================
# GAS 웹앱(배포된 /exec) 엔드포인트
GAS_ENDPOINT = "https://script.google.com/macros/s/AKfycbwACq7RUHXNYDv6Qod_mSGjhzSIjatJZz4_2h-Lw5aRkuwSlIeAIJqlPQuxxrBnlsVGGw/exec"

# 저장 경로 (레포 루트 기준)
DATA_DIR = Path("data")
SNAP_DIR = Path("snapshots")

# 타임존: 미국 동부시간(장 운영 기준)
ET_TZ = dt.timezone(dt.timedelta(hours=-4))  # 일단 EDT 고정. 필요시 pytz/zoneinfo로 보완 가능.
# ============================================


def now_et():
    # 간단 EDT 고정. (서머타임 자동 전환까지 하려면 zoneinfo 사용 권장)
    return dt.datetime.now(ET_TZ)


def ts_ms():
    return int(time.time() * 1000)


def fetch_from_gas(params=None, timeout=20):
    if params is None:
        params = {}
    # 캐시 바스터
    params = {**params, "t": str(ts_ms())}
    r = requests.get(GAS_ENDPOINT, params=params, timeout=timeout, headers={
        "Cache-Control": "no-cache"
    })
    r.raise_for_status()
    try:
        return r.json()
    except Exception:
        # JSON이 아니면 원문 저장 확인을 위해 예외 발생
        raise RuntimeError(f"Invalid JSON from GAS: {r.text[:200]}...")


def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SNAP_DIR.mkdir(parents=True, exist_ok=True)


def save_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def main():
    ensure_dirs()

    # 1) GAS에서 데이터 가져오기
    data = fetch_from_gas()
    # 기대 형태 예시:
    # {
    #   "date": "2025-10-20",        # ET 기준 날짜(서버에서 내려주지 않으면 여기서 생성)
    #   "updatedAt": 1697800000000,  # ms epoch
    #   "items": [
    #       {"symbol":"AAPL","price":...,"changePct":...},
    #       ...
    #   ]
    # }

    # 서버가 날짜/타임스탬프를 주지 않으면 여기서 보강
    now = now_et()
    if "date" not in data:
        data["date"] = now.strftime("%Y-%m-%d")
    if "updatedAt" not in data:
        data["updatedAt"] = ts_ms()

    # 2) 스냅샷 파일명: YYYY-MM-DD_HHMM.json (ET 기준)
    snap_name = now.strftime("%Y-%m-%d_%H%M.json")
    snap_path = SNAP_DIR / snap_name
    save_json(snap_path, data)

    # 3) 최신본 갱신: data/latest.json
    latest_path = DATA_DIR / "latest.json"
    save_json(latest_path, data)

    print(f"[OK] Saved snapshot: {snap_path}")
    print(f"[OK] Updated latest : {latest_path}")
    print(f"Items: {len(data.get('items', []))}, Date(ET): {data['date']}")


if __name__ == "__main__":
    main()
