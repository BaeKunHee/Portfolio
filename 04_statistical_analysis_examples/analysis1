#STN 별 TA, WS의 평균 비교
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_parquet("datasets/hourly_base.parquet")

stn_mean = (
    df.groupby("STN")[["TA", "WS", "HM"]]
      .mean()
      .reset_index()
)

plt.figure(figsize=(8, 4))
sns.scatterplot(data=stn_mean, x="TA", y="WS")
plt.xlabel("Mean Temperature (TA)")
plt.ylabel("Mean Wind Speed (WS)")
plt.title("STN-level Mean Comparison")
plt.tight_layout()
plt.show()
