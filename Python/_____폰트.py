import matplotlib
import matplotlib.pyplot as plt
from matplotlib import font_manager

font_path = "C:/Windows/Fonts/malgun.ttf"
font_name = font_manager.FontProperties(fname=font_path).get_name()
matplotlib.rcParams['font.family'] = font_name
matplotlib.rcParams['axes.unicode_minus'] = False

plt.title("한글 폰트 테스트 🎮 - 액션 / 전략 / 시뮬레이션 / 슈팅")
plt.plot([1,2,3],[2,3,5], marker="o")
plt.show()
