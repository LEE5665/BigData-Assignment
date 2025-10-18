import requests
import pandas as pd

url = "https://steamspy.com/api.php"
params = {"request": "all"}
response = requests.get(url, params=params)
data = response.json()

steamspy = pd.DataFrame(data).T

print(steamspy.columns)

# cols = [c for c in ['name', 'owners', 'price', 'genre', 'average_forever', 'score_rank'] if c in steamspy.columns]
# steamspy = steamspy[cols]

print("데이터 저장:", steamspy)
steamspy.to_csv("./datasets/steamspy.csv", index=False)
