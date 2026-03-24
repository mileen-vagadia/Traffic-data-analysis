import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from dotenv import load_dotenv

os.makedirs("visuals", exist_ok=True)
load_dotenv()

engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

df = pd.read_sql("select * from traffic_observations", engine, parse_dates=["timestamp"])
print(df.shape)
print(df.isnull().sum())
print(df.describe())

# basic feature extraction
df["hour"] = df["timestamp"].dt.hour
df["day_name"] = df["timestamp"].dt.day_name()
df["day_num"] = df["timestamp"].dt.dayofweek
df["is_weekend"] = df["day_num"].isin([5, 6])

def tod(h):
    if 6 <= h < 10: return "morning peak"
    if 10 <= h < 17: return "midday"
    if 17 <= h < 21: return "evening peak"
    return "night"

df["time_of_day"] = df["hour"].apply(tod)

# -- peak hour analysis --

hourly = df.groupby("hour")["traffic_volume"].mean().reset_index()
print(hourly.sort_values("traffic_volume", ascending=False).head(5))

fig, ax = plt.subplots(figsize=(12, 4))
ax.bar(hourly["hour"], hourly["traffic_volume"], color="steelblue", width=0.7)
ax.set_xlabel("hour")
ax.set_ylabel("avg vehicle count")
ax.set_title("traffic by hour")
ax.set_xticks(range(0, 24))
plt.tight_layout()
plt.savefig("visuals/peak_hour.png")
plt.show()

# weekday vs weekend
wd = df.groupby(["hour", "is_weekend"])["traffic_volume"].mean().reset_index()
wd["label"] = wd["is_weekend"].map({False: "weekday", True: "weekend"})

fig, ax = plt.subplots(figsize=(12, 4))
for label, grp in wd.groupby("label"):
    ax.plot(grp["hour"], grp["traffic_volume"], marker="o", label=label)
ax.set_xlabel("hour")
ax.set_ylabel("avg vehicle count")
ax.set_title("weekday vs weekend")
ax.legend()
plt.tight_layout()
plt.savefig("visuals/weekday_weekend.png")
plt.show()

# heatmap
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
pivot = df.groupby(["day_name", "hour"])["traffic_volume"].mean().unstack()
pivot = pivot.reindex(day_order)

fig, ax = plt.subplots(figsize=(14, 5))
sns.heatmap(pivot, cmap="YlOrRd", linewidths=0.2, ax=ax)
ax.set_title("traffic heatmap")
plt.tight_layout()
plt.savefig("visuals/heatmap.png")
plt.show()

# -- weather vs traffic volume --

weather = df.groupby("weather_condition")["traffic_volume"].mean().sort_values(ascending=False).reset_index()
print(weather)

fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(weather["weather_condition"], weather["traffic_volume"], color="steelblue")
ax.set_xlabel("weather condition")
ax.set_ylabel("avg traffic volume")
ax.set_title("traffic volume by weather condition")
plt.tight_layout()
plt.savefig("visuals/weather_vs_traffic.png")
plt.show()

# does temperature affect traffic?
fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(df["temperature"], df["traffic_volume"], alpha=0.3, s=12, color="steelblue")
z = np.polyfit(df["temperature"], df["traffic_volume"], 1)
p = np.poly1d(z)
x_range = np.linspace(df["temperature"].min(), df["temperature"].max(), 200)
ax.plot(x_range, p(x_range), "k-", linewidth=1.5)
ax.set_xlabel("temperature (C)")
ax.set_ylabel("traffic volume")
ax.set_title("temperature vs traffic volume")
plt.tight_layout()
plt.savefig("visuals/temp_vs_traffic.png")
plt.show()

print("temp vs traffic correlation:", round(df["temperature"].corr(df["traffic_volume"]), 3))
print("humidity vs traffic correlation:", round(df["humidity"].corr(df["traffic_volume"]), 3))


fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(acc["label"], acc["traffic_volume"], color=["steelblue", "tomato"])
ax.set_ylabel("avg traffic volume")
ax.set_title("traffic volume — accident vs no accident")
plt.tight_layout()
plt.savefig("visuals/accident_vs_traffic.png")
plt.show()
