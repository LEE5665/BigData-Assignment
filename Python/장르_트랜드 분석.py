import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager
import seaborn as sns
import ast
import re

input_path = "./data_preprocessing/rawg_cleaned.csv"
output_folder = "./analysis_results"
os.makedirs(output_folder, exist_ok=True)


df = pd.read_csv(input_path)

# name: 만 추출 되어있는 장르 파싱 함수
def extract_genres(x):
    """RAWG genres 문자열에서 'name: XXX' 패턴만 추출"""
    if pd.isna(x) or not isinstance(x, str):
        return []
    # "name: Action, slug: action" → ["Action"]
    names = re.findall(r"name:\s*([A-Za-z\s\-']+)", x)
    return [n.strip() for n in names if n.strip()]

df["genre_list"] = df["genres"].apply(extract_genres)
df = df.explode("genre_list").dropna(subset=["genre_list"])
df["genre_list"] = df["genre_list"].str.lower().str.strip()
df = df[df["genre_list"] != "indie"]

# 장르 한글 매핑
genre_map = {
    "action": "액션",
    "shooter": "슈팅",
    "rpg": "롤플레잉",
    "role-playing-games-rpg": "롤플레잉",
    "adventure": "어드벤처",
    "strategy": "전략",
    "sports": "스포츠",
    "simulation": "시뮬레이션",
    "platformer": "플랫포머",
    "puzzle": "퍼즐",
    "indie": "인디",
    "arcade": "아케이드",
    "fighting": "격투",
    "racing": "레이싱",
    "family": "패밀리",
    "card": "카드게임",
    "educational": "교육",
    "board-games": "보드게임",
    "massively-multiplayer": "MMO",
    "casual": "캐주얼",
    "horror": "호러",
    "stealth": "잠입",
    "music": "음악",
}

df["genre_kr"] = df["genre_list"].map(genre_map).fillna(df["genre_list"])

# 자료형 숫자로 변환 및 연도 필터링
df["added_by_status.owned"] = pd.to_numeric(df["added_by_status.owned"], errors="coerce").fillna(0)
df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
df = df[(df["year"] >= 2000) & (df["year"] <= 2024)]

# 개발자 관점 (출시된 게임 수 기준)
dev_trend = (
    df.groupby(["year", "genre_kr"])["name"]
    .count()
    .reset_index(name="game_count")
)
dev_trend["total_year"] = dev_trend.groupby("year")["game_count"].transform("sum")
dev_trend["ratio"] = dev_trend["game_count"] / dev_trend["total_year"] * 100

# 사용자 관점 (보유량 기준)
user_trend = (
    df.groupby(["year", "genre_kr"])["added_by_status.owned"]
    .sum()
    .reset_index(name="owned_sum")
)
user_trend["total_year"] = user_trend.groupby("year")["owned_sum"].transform("sum")
user_trend["ratio"] = user_trend["owned_sum"] / user_trend["total_year"] * 100

# 상위 5개 장르 선택
top_dev = dev_trend.groupby("genre_kr")["ratio"].sum().nlargest(5).index
top_user = user_trend.groupby("genre_kr")["ratio"].sum().nlargest(5).index

dev_top5 = dev_trend[dev_trend["genre_kr"].isin(top_dev)]
user_top5 = user_trend[user_trend["genre_kr"].isin(top_user)]


plt.style.use("seaborn-v0_8-darkgrid")

font_path = "C:/Windows/Fonts/malgun.ttf"
font_name = font_manager.FontProperties(fname=font_path).get_name()
matplotlib.rcParams['font.family'] = font_name
matplotlib.rcParams['axes.unicode_minus'] = False

# ---- 개발자 관점 ----
plt.figure(figsize=(10, 5))
sns.lineplot(data=dev_top5, x="year", y="ratio", hue="genre_kr", marker="o")
plt.title("연도별 장르 비중 변화 (개발자 관점: 출시된 게임 비율)", fontsize=13)
plt.xlabel("연도")
plt.ylabel("비율 (%)")
plt.legend(title="장르", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "trend_dev_ratio_kr.png"))
plt.show()

# ---- 사용자 관점 ----
plt.figure(figsize=(10, 5))
sns.lineplot(data=user_top5, x="year", y="ratio", hue="genre_kr", marker="o")
plt.title("연도별 장르 비중 변화 (사용자 관점: 보유량 비율)", fontsize=13)
plt.xlabel("연도")
plt.ylabel("비율 (%)")
plt.legend(title="장르", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "trend_user_ratio_kr.png"))
plt.show()

