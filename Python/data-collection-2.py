import requests
import pandas as pd
from time import sleep
import os

API_KEY = "bc9bda5ee7564df4aeaf4253f0d0e7ec"
BASE_URL = "https://api.rawg.io/api/games"
SAVE_DIR = "./datasets/rawg_by_year"
os.makedirs(SAVE_DIR, exist_ok=True)

for year in range(2000, 2025):
    save_path = f"{SAVE_DIR}/rawg_{year}.csv"

    # 이미 수집된 연도는 스킵
    if os.path.exists(save_path):
        print(f"{year}년 데이터 이미 존재")
        continue

    print(f"\n📆 {year}년 데이터 수집")

    all_games = []
    page = 1

    while True:
        params = {
            "key": API_KEY,
            "dates": f"{year}-01-01,{year}-12-31",
            "page_size": 40,
            "page": page
        }

        try:
            r = requests.get(BASE_URL, params=params)
        except Exception as e:
            print(f"5초 후 재시도")
            sleep(5)
            continue

        if r.status_code != 200:
            print(f"{year}, page {page}")
            sleep(3)
            break

        try:
            data = r.json()
        except ValueError:
            print(f"디코딩 {year}, page {page}")
            print(r.text[:200])
            sleep(3)
            break

        if "results" not in data or not data["results"]:
            print(f"{year}년 {page}페이지 결과 없음")
            break

        # 데이터 추가
        all_games.extend(data["results"])
        print(f"{year}년 {page}페이지 수집 완료 ({len(data['results'])}개)")

        # 다음 페이지 없으면 중단
        if not data.get("next"):
            break

        page += 1
        sleep(1.2)

    # 데이터 저장
    if all_games:
        df = pd.json_normalize(all_games)
        df.to_csv(save_path, index=False, encoding="utf-8-sig")
        print(f"{year}년 데이터 저장 완료 ({len(df)}개)")
    else:
        print(f"{year}년은 데이터 없음")

    sleep(2)
