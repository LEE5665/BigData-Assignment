# 프로젝트 계획1
### 분석 할 내용
* 게임 리뷰 평점에 따른 메타크리틱 점수 예측
  
### 사용 한 데이터
> https://api.rawg.io/api/games API 사용해서 2000-2024년 게임 데이터 모두 추출

### 프로젝트 범위
**[데이터 수집]**
  - rawg_2000.csv ~ rawg_2024.csv
<details>
  <summary>데이터 가공, 분석 결과</summary>
  
```
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
```
  
</details>

**[데이터 시각화]**
  
<details>
  <summary>평점, 메타크래틱을 활용한 회귀 예측</summary>

```
# 학습
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LinearRegression()
model.fit(X_train, y_train)

# 예측, 성능 평가
y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print(f"MAE: {mae:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"\n회귀식: Metacritic = {model.coef_[0]:.2f} * Rating + {model.intercept_:.2f}")

font_path = "C:/Windows/Fonts/malgun.ttf"
font_name = font_manager.FontProperties(fname=font_path).get_name()
matplotlib.rcParams['font.family'] = font_name
matplotlib.rcParams['axes.unicode_minus'] = False

# 시각화
plt.figure(figsize=(8, 6))
plt.scatter(X_test, y_test, alpha=0.5, label="실제 값")
plt.plot(X_test, y_pred, color="red", label="예측 회귀선")
plt.xlabel("유저 평점 (rating)")
plt.ylabel("Metacritic 점수")
plt.title(f"유저 평점 → Metacritic 점수 예측")
plt.legend()
```
  
</details>

### 시각화
<img width="795" height="631" alt="image" src="https://github.com/user-attachments/assets/e962bec7-d627-420a-ad3b-c8895dd78012" />



### 결과
- 모델 평가
  - MAE: 6.79
  - RMSE: 8.87
- 평점 3점 시 AI 예측 결과 : 60점, 모델 예측 결과 : 68점

<details>
  <summary>생성형 AI 결과</summary>
  <img width="769" height="253" alt="image" src="https://github.com/user-attachments/assets/2fb37677-1d06-48ec-b917-545df99be778" />
</details>

---
---
---

# 프로젝트 계획2
### 분석 할 내용
* 지역별 콘솔 매출 분석
  
### 사용 한 데이터
> [1980~2024 나라별 콘솔 게임 매출 - vgsales.csv](https://www.kaggle.com/datasets/asaniczka/video-game-sales-2024/data)

### 프로젝트 범위
**[데이터 수집]**
- vgsales.csv
**[데이터 가공, 분석 결과]**
```
# 결측치 제거 및 필요 컬럼 선택
df = df.dropna(subset=["Platform", "NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"])
df = df[["Platform", "NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]]

# 플랫폼별 지역 매출 합계
region_sales = df.groupby("Platform")[["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]].sum()
```
**[데이터 시각화]**
<details>
  <summary>플랫폼별 지역 매출 누적 그래프 & 각 지역별 최고 매출 플랫폼</summary>
  
```
region_sales.plot(
    kind="bar",
    stacked=True,
    color=["#3498db", "#e74c3c", "#9b59b6", "#2ecc71"],
    width=0.8,
)

plt.title("Platform-wise Total Sales by Region", fontsize=14)
plt.xlabel("Platform")
plt.ylabel("Total Videogame Sales (in millions)")
plt.legend(["NA", "EU", "JP", "Other"], title="Region")
plt.tight_layout()
plt.grid(True, axis="y", linestyle="--", alpha=0.7)
plt.show()

# 각 지역별 최고 매출 플랫폼
best_platforms = {}
for region in ["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]:
    best = region_sales[region].idxmax()
    value = region_sales[region].max()
    best_platforms[region.replace("_Sales", "")] = (best, value)

best_df = pd.DataFrame(best_platforms).T
best_df.columns = ["Platform", "Total_Sales"]
best_df = best_df.sort_values("Total_Sales", ascending=False)

plt.figure(figsize=(8, 5))
sns.barplot(
    data=best_df,
    x=best_df.index,
    y="Total_Sales",
    hue="Platform",
    dodge=False,
    palette="tab10"
)

plt.title("Region-wise Best-Selling Platform", fontsize=14)
plt.xlabel("Region")
plt.ylabel("Total Sales (in millions)")
plt.legend(title="Platform", loc="upper right")
plt.tight_layout()
plt.show()
```
  
</details>

### 시각화
<img width="624" height="455" alt="image" src="https://github.com/user-attachments/assets/e3f53a4d-687f-4e95-b2e4-6e2012e2b994" />
<img width="784" height="477" alt="image" src="https://github.com/user-attachments/assets/b162abaa-2134-4c00-8d8f-298df90a2fac" />

### 결과
- 모든 지역에서 가장 많이 팔린 플랫폼은 PS2
- 지역별로 가장 많이 팔린 플랫폼
  - NA - X360
  - EU - PS3
  - Other - PS2
  - JP - DS


  

<details>
  <summary>생성형 AI 결과</summary>
  <img width="585" height="818" alt="Image" src="https://github.com/user-attachments/assets/0f8fcf46-dda1-4969-ac36-c6134ac08997" />
</details>
