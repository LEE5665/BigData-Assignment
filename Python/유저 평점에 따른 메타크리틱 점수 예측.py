import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import os

# 불러오기
df = pd.read_csv("./data_preprocessing/rawg_user_vs_meta.csv")

X = df[["rating"]]
y = df["metacritic"]

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

# 결과 이미지 저장
os.makedirs("./results", exist_ok=True)
plot_path = "./results/user_vs_meta_regression.png"
plt.savefig(plot_path, dpi=300)
plt.close()

while True:
    try:
        rating_input = input("\n유저 평점을 입력하세요 (0~5, 종료하려면 q 입력): ")
        if rating_input.lower() == "q":
            print("프로그램을 종료합니다.")
            break

        rating_value = float(rating_input)
        if not (0 <= rating_value <= 5):
            print("0~5 사이의 숫자를 입력하세요.")
            continue

        predicted_meta = model.predict([[rating_value]])[0]
        print(f"예측된 Metacritic 점수: {predicted_meta:.1f}점")
    except ValueError:
            print("숫자를 입력하거나 'q'로 종료하세요.")
