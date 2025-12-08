# 프로젝트 주제 - 게임 장르 & 평점에 대한 분석
- 프로젝트 범위
  - 데이터 수집, 가공, 저장 분석, 시각화, 결과

<br>

- 분석할 내용
  - 연도별로 어떤 장르가 증가하고 감소했는지
  - 연도별로 장르의 출시 수 변화
  - 게임별 메타크리틱 점수와 실제 게임 평점 학습으로 메타 크리틱 점수로 유저 평점 예측

# 데이터 수집, 가공, 저장
## 1. 2010년부터 2025년까지 게임 데이터를 API로 호출해서 JSON으로 원본 저장
```
import requests
import json
import time
import os

API_KEY = "bc9bda5ee7564df4aeaf4253f0d0e7ec"

START_YEAR = 2015
END_YEAR = 2025
SAVE_DIR = "rawg_date"

os.makedirs(SAVE_DIR, exist_ok=True)

def fetch_year(year):
    print(f"\n{year}")
    all_games = []
    page = 1

    while True:
        url = (
            f"https://api.rawg.io/api/games"
            f"?key={API_KEY}"
            f"&dates={year}-01-01,{year}-12-31"
            f"&page_size=40&page={page}"
        )
        
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error {response.status_code} — stopping year {year}")
            break

        data = response.json()
        results = data.get("results", [])
        
        if not results:
            break

        for game in results:
            game["year"] = year  # 연도 칼럼 추가
            all_games.append(game)
        
        print(f"페이지 {page} ({len(results)}개)")
        page += 1
        
        time.sleep(0.2)

    # 연도별 저장
    save_path = f"{SAVE_DIR}/rawg_{year}.json"
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(all_games, f, indent=2, ensure_ascii=False)
    
    print(f"{year} data {save_path}  (총 {len(all_games)} 개)")
    return all_games


# 실행
for year in range(START_YEAR, END_YEAR + 1):
    fetch_year(year)

```
## 2. 연도별 데이터 JOSN 평탄화 및 필요한 데이터만 추출 후 CSV 로 저장
**분석에 필요없는 데이터 제외**<br>
id : 게임id / slug/name : 게임 이름 / released : 게임 출시일 / year : 분석용으로 released에서 가져온 출시년도<br>
playtime : 게임 플레이 평균 시간 / rating : 게임 평점 / ratings_count : 리뷰 개수 / metacritic : 메타크리틱 점수<br>
platforms : 출시 플랫폼 / stores : 출시한 상점 목록 / genres/tags : 장르 분류 / esrb_rating : 게임 등급 분류
```
import json
import glob
import pandas as pd

files = glob.glob("rawg_date/*.json")  # 연도별 JSON 파일 경로
all_data = []

def extract_platforms(p_list):
    if not isinstance(p_list, list):
        return None
    return [p["platform"]["name"] for p in p_list]

def extract_stores(s_list):
    if not isinstance(s_list, list):
        return None
    return [s["store"]["name"] for s in s_list]

def extract_genres(g_list):
    if not isinstance(g_list, list):
        return None
    return [g["name"] for g in g_list]

def extract_tags(t_list):
    if not isinstance(t_list, list):
        return None
    return [t["name"] for t in t_list]

def extract_esrb(esrb):
    if isinstance(esrb, dict):
        return esrb.get("name")
    return None


for file in files:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for g in data:
        all_data.append({
            "id": g.get("id"),
            "slug": g.get("slug"),
            "name": g.get("name"),
            "released": g.get("released"),
            "year": int(g["released"][:4]) if g.get("released") else None,
            "playtime": g.get("playtime"),
            "rating": g.get("rating"),
            "ratings_count": g.get("ratings_count"),
            "metacritic": g.get("metacritic"),
            "suggestions_count": g.get("suggestions_count"),

            # 리스트/딕셔너리 평탄화
            "platforms": extract_platforms(g.get("platforms")),
            "stores": extract_stores(g.get("stores")),
            "genres": extract_genres(g.get("genres")),
            "tags": extract_tags(g.get("tags")),
            "esrb_rating": extract_esrb(g.get("esrb_rating")),
        })

df = pd.DataFrame(all_data)
df.to_csv("rawg_flatten.csv", index=False)
print("rawg_flatten.csv")
```

# 분석 과정(전처리, 변환 과정) 및 시각화 결과
## 1. 연도별로 작년 대비 증가량 & 출시량 분석
> csv에 저장된 형태가 리스트 형태 df["genres"]를 파이썬의 리스트의 형태로 변환
> explode로 리스트 쪼갠 후 집계
```
df = pd.read_csv("rawg_flatten.csv")

# genres가 리스트 문자열 형태라면 eval() 또는 ast.literal_eval로 변환
import ast
df["genres"] = df["genres"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

# 장르 explode
df_ex = df.explode("genres")

# 연도별 장르별 출시 수 집계
genre_by_year = df_ex.groupby(["year", "genres"]).size().reset_index(name="count")

print(genre_by_year.head())
```
> 피벗 테이블로 년도별로 장르 개수 기록
> 전년 대비 증가량 계산 후 전체 증가량 기준으로 상위 5개 선택 후 히트맵으로 시각화
```
# 피벗 테이블 생성
pivot = genre_by_year.pivot(index="year", columns="genres", values="count").fillna(0)

# 각 장르별 전년 대비 증가량 계산
trend = pivot.diff().fillna(0)

print("=== 장르별 증가/감소 추세 ===")
print(trend)

# 증가량 합계 기준 상위 5개 장르 선택
top5_trend_genres = trend.sum().sort_values(ascending=False).head(5).index
trend_top5 = trend[top5_trend_genres]

# 히트맵 시각화
import seaborn as sns

plt.figure(figsize=(12, 8))
sns.heatmap(trend_top5, cmap="coolwarm", center=0, annot=True, fmt=".0f")
plt.title("전년 대비 증가량 기준 상위 5개 장르 히트맵")
plt.xlabel("Genre")
plt.ylabel("Year")
plt.show()
```
> 연도별 장르 출시 수 변화 상위 5개 line plot, 히트맵으로 시각화
```
# 상위 5개 장르 선택
top_genres = df_ex["genres"].value_counts().head(5).index
pivot_top = pivot[top_genres]

# 시각화
plt.figure(figsize=(14, 8))
for g in top_genres:
    plt.plot(pivot_top.index, pivot_top[g], marker='o', label=g)

plt.title("연도별 장르 출시 수 변화")
plt.xlabel("Year")
plt.ylabel("개수")
plt.legend()
plt.grid(True)
plt.show()

plt.figure(figsize=(14, 10))
sns.heatmap(pivot_top, cmap="Blues", linewidths=0.5)
plt.title("연도별 장르 출시 수 변화")
plt.show()
```
### 시각화 ###
<img width="800" height="500" alt="작년 대비 증가량" src="https://github.com/user-attachments/assets/db12c398-b0d3-430c-a616-9db96b833415" />
<img width="800" height="500" alt="연도별 장르 출시 수 변화1" src="https://github.com/user-attachments/assets/83ba8c34-7b83-4548-a293-5fe8698177a7" />
<img width="800" height="500" alt="연도별 장르 출시 수 변화2" src="https://github.com/user-attachments/assets/72bfb6c2-4347-4665-b435-932381e33d36" />

## 2. 연도별 플랫폼 비율
> platforms 열을 파이썬 리스트 형태로 변환 후 펼치기
> 그룹별로 매핑 -> 필요없는 값 제거 후 연도, 그룹, 개수로 변환 ->
> 연도별 전체 개수로 비율 계산 후 2차원 행렬로 재구성
```
df["platforms"] = df["platforms"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
df_pl = df.explode("platforms")

# 카테고리 매핑
platform_map = {
    "PC": "Windows",
    "macOS": "macOS",
    "Linux": "Linux",

    "PlayStation 3": "PlayStation",
    "PlayStation 4": "PlayStation",
    "PlayStation 5": "PlayStation",
    "PS Vita": "PlayStation",

    "Xbox 360": "Xbox",
    "Xbox One": "Xbox",
    "Xbox Series S/X": "Xbox",

    "Nintendo Switch": "Nintendo",
    "Wii U": "Nintendo",
    "Wii": "Nintendo",
}

# 매핑 적용
df_pl["platform_group"] = df_pl["platforms"].map(platform_map)

# 정의되지 않은 플랫폼 제거
df_pl = df_pl[df_pl["platform_group"].notna()]

# 플랫폼 그룹 확인
platform_counts = df_pl["platform_group"].value_counts()
platform_groups = platform_counts.index.tolist()
print("사용 플랫폼 그룹:", platform_groups)

df_pl_top = df_pl[df_pl["platform_group"].isin(platform_groups)]

# 연도 + 플랫폼 그룹별 개수
platform_by_year = (
    df_pl_top.groupby(["year", "platform_group"])
    .size()
    .reset_index(name="count")
)

# 연도별 전체 개수
total_by_year = df_pl_top.groupby("year").size()

# 비율 계산
platform_by_year["ratio"] = platform_by_year.apply(
    lambda row: row["count"] / total_by_year[row["year"]],
    axis=1
)

# 피벗 테이블
pivot_ratio = platform_by_year.pivot(
    index="year", columns="platform_group", values="ratio"
).fillna(0)
```
> 연도별 플랫폼 비율 Stacked Area Chart, Line Plot로 시각화
```
# Stacked Area Chart
plt.figure(figsize=(14, 8))

plt.stackplot(
    pivot_ratio.index,
    [pivot_ratio[col] for col in pivot_ratio.columns],
    labels=pivot_ratio.columns,
    alpha=0.8
)

plt.title("연도별 플랫폼 비율")
plt.xlabel("Year")
plt.ylabel("Ratio")
plt.legend(loc="upper left")
plt.grid(True, alpha=0.3)
plt.show()

# Line Plot
plt.figure(figsize=(14, 8))

for col in pivot_ratio.columns:
    plt.plot(pivot_ratio.index, pivot_ratio[col], marker='o', label=col)

plt.title("연도별 플랫폼 비율")
plt.xlabel("Year")
plt.ylabel("Ratio")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
```
### 시각화 ###
<img width="800" height="500" alt="연도별 플랫폼 비율1" src="https://github.com/user-attachments/assets/27eb4b05-68cc-4c29-b023-38298bc1aecb" />
<img width="800" height="500" alt="연도별 플랫폼 비율2" src="https://github.com/user-attachments/assets/181ec5aa-b634-4a0a-8eb0-bcd4993939d8" />

## 3. 게임별 메타크리틱 점수와 실제 게임 평점 학습으로 메타 크리틱 점수로 유저 평점 예측
> 매타크리틱, 평점, 평가 개수만 남기고 제거
> 리뷰 개수가 적은 게임이라면 결과가 많이 튈 수 있으므로 log로 변환
> 모델 생성 및 예측
```
df = pd.read_csv("rawg_flatten.csv")

# 메타크리틱, 유저 평점, 평점 개수 결측치 제거
df = df.dropna(subset=["metacritic", "rating", "ratings_count"])

# 입력 X, 출력 y
X = df[["metacritic", "ratings_count"]]
y = df["rating"]

# ratings_count log 변환(스케일 차이 해결)
X["ratings_count"] = np.log1p(X["ratings_count"])

# Train/Test 분리
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# GradientBoostingRegressor 비선형 모델 생성
model = GradientBoostingRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=3,
    random_state=42
)

model.fit(X_train, y_train)

# 예측
y_pred = model.predict(X_test)
```
> 정확도 평가 및 테스트
```
# 정확도 평가
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("Gradient Boosting 예측 성능")
print(f"MSE : {mse:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"MAE : {mae:.4f}")
print(f"R²  : {r2:.4f}")

# 테스트 예측
test_meta = 88
test_count = 5000

test_input = [[test_meta, np.log1p(test_count)]]
pred_example = model.predict(test_input)[0]

print(f"\n메타크리틱 {test_meta}점, 평점 수 {test_count}개 게임 예상 유저 평점: {pred_example:.3f}")
```
> 시각화 Scatter 그래프로 표시
```
plt.figure(figsize=(8, 6))

plt.scatter(X_test["metacritic"], y_test, alpha=0.4, label="실제", color="blue")
plt.scatter(X_test["metacritic"], y_pred, alpha=0.4, label="예측", color="red")

plt.xlabel("메타크리틱")
plt.ylabel("평점")
plt.title("실제 데이터, 예측 데이터 확인")
plt.legend()
plt.grid(True)
plt.show()
```

### 시각화 ###
<img width="676" height="544" alt="실제 예측 데이터 확인" src="https://github.com/user-attachments/assets/6b3e5728-699c-4f0c-87fd-116ca4436a13" />

# 결론
### 연도별로 어떤 장르가 증가하고 감소했는지 ###
2019년에는 전반적으로 게임 개수가 줄어들었고,
2024년에는 전반적으로 게임 개수가 폭발적으로 증가했다.
인디 장르가 가장 많은 변동을 보였고, 캐쥬얼 장르가 그 다음으로 많았으며,
액션 장르의 변동은 적었다.

### 연도별로 장르의 출시 수 변화 ###
인디 장르는 2015~2017년과 2024~2025년에 출시량이 크게 증가하며 가장 극적인 성장 패턴을 보였다.
액션과 어드벤처 장르는 전반적으로 비교적 일정한 수준을 유지했다.
캐주얼 장르는 2023년 이후부터 출시량이 눈에 띄게 증가하며 최근 강한 성장세를 나타냈다.
시뮬레이션 장르는 전체 기간 동안 출시량이 가장 적고, 변동 폭도 작아 일관적으로 작은 규모의 시장을 형성했다.

### 게임별 메타크리틱 점수와 실제 게임 평점 학습으로 메타 크리틱 점수로 유저 평점 예측 ###
선형으로 예측 했을 경우
MSE : 1.5897 RMSE: 1.2608 MAE : 0.8892 R² : 0.1481로 상당히 나쁜 수치를 보여주었지만
GradientBoosting 비선형 모델을 사용하고, 리뷰 개수를 고려 했을 때
MSE : 0.1806 RMSE: 0.4249 MAE : 0.2941 R²  : 0.9032의 굉장히 준수한 예측 성능을 보여줬다.






<details>
  <summary>생성형 AI 결과</summary>
  <img width="585" height="818" alt="Image" src="https://github.com/user-attachments/assets/0f8fcf46-dda1-4969-ac36-c6134ac08997" />
</details>
