import pandas as pd
import glob
import os

input_folder = "./datasets/rawg_by_year"
output_folder = "./data_preprocessing"
os.makedirs(output_folder, exist_ok=True)

files = sorted(glob.glob(os.path.join(input_folder, "rawg_*.csv")))

all_data = []
for file in files:
    df = pd.read_csv(file, low_memory=False)
    keep_cols = [
        "name", "released", "rating", "metacritic", "genres",
        "platforms", "stores", "added_by_status.owned",
        "added", "playtime"
    ]
    df = df[[col for col in keep_cols if col in df.columns]]

    # 결측치 제거 & 중복 제거
    df = df.drop_duplicates(subset=["name"])
    df = df.dropna(subset=["name", "released"])

    # 연도 추가
    df["year"] = pd.to_datetime(df["released"], errors="coerce").dt.year

    all_data.append(df)

# 전체 병합
merged = pd.concat(all_data, ignore_index=True)

# 불필요하게 문자열 리스트형 데이터 문자열화
for col in ["genres", "platforms", "stores"]:
    merged[col] = merged[col].astype(str).str.replace(r"[\[\]\{\}']", "", regex=True)

# 저장
output_path = os.path.join(output_folder, "rawg_cleaned.csv")
merged.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"RAWG 데이터 전처리 완료: {merged.shape[0]}개 게임 저장됨")
