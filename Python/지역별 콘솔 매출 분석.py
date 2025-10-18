
# 플랫폼별 지역 매출 분석 + 지역별 최고 플랫폼

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 데이터 불러오기

df = pd.read_csv("./datasets/vgsales.csv")

# 결측치 제거 및 필요 컬럼 선택
df = df.dropna(subset=["Platform", "NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"])
df = df[["Platform", "NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]]

# 플랫폼별 지역 매출 합계
region_sales = df.groupby("Platform")[["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]].sum()

# 플랫폼별 지역 매출 누적 그래프
region_sales.plot(
    kind="bar",
    stacked=True,
    color=["#3498db", "#e74c3c", "#9b59b6", "#2ecc71"],
    width=0.8,
)

plt.title("💰 Platform-wise Total Sales by Region", fontsize=14)
plt.xlabel("Platform")
plt.ylabel("Total Videogame Sales (in millions)")
plt.legend(["NA", "EU", "JP", "Other"], title="Region")
plt.tight_layout()
plt.grid(True, axis="y", linestyle="--", alpha=0.7)
plt.show()

# ----------------------------------------
# 🎯 (2) 각 지역별 최고 매출 플랫폼
# ----------------------------------------
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

plt.title("🌍 Region-wise Best-Selling Platform", fontsize=14)
plt.xlabel("Region")
plt.ylabel("Total Sales (in millions)")
plt.legend(title="Platform", loc="upper right")
plt.tight_layout()
plt.show()
