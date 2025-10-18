# 프로젝트 계획
### 분석 할 내용
* 지역별 콘솔 매출 분석
  
### 사용 한 데이터
> [1980~2024 나라별 콘솔 게임 매출 - vgsales.csv](https://www.kaggle.com/datasets/asaniczka/video-game-sales-2024/data)

### 프로젝트 범위
- 데이터 수집
  - vgsales.csv
- 데이터 가공, 분석 결과
```
# 결측치 제거 및 필요 컬럼 선택
df = df.dropna(subset=["Platform", "NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"])
df = df[["Platform", "NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]]

# 플랫폼별 지역 매출 합계
region_sales = df.groupby("Platform")[["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]].sum()
```
- 데이터 시각화
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
