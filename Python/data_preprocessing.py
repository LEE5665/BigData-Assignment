import pandas as pd
import os

input_path = "./data_preprocessing/rawg_cleaned.csv"
output_folder = "./data_preprocessing"
os.makedirs(output_folder, exist_ok=True)

df = pd.read_csv(input_path, low_memory=False)

# 필요한 컬럼만 남기기
keep_cols = ["name", "year", "rating", "metacritic"]
df = df[[col for col in keep_cols if col in df.columns]].copy()

# 타깃 결측 제거 (Metacritic 점수가 없는 게임은 제거)
df = df.dropna(subset=["metacritic", "rating"])

# 점수 범위 이상치 제거
df = df[(df["rating"] > 0) & (df["rating"] <= 5)]
df = df[(df["metacritic"] > 20) & (df["metacritic"] <= 100)]

# 저장
output_path = os.path.join(output_folder, "rawg_user_vs_meta.csv")
df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"전처리 완료: {df.shape[0]}개 게임 (유저평점 기반 예측용 데이터)")
