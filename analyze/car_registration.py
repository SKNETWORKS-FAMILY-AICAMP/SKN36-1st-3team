#W 연도별 전체 등록대수, 차량 종류별 등록대수, 연도 × 차량 종류 추세

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

from models.visualization import line_plot, bar_plot

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


# DB 불러오기
with sqlite3.connect("database/car.db") as conn:
    df = pd.read_sql(
        "SELECT * FROM car_registration",
        conn
    )

df["year"] = pd.to_numeric(df["year"])
df["count"] = pd.to_numeric(df["count"])


# 1. 연도별 전체 자동차 등록대수
line_plot(
    df,
    "year",
    "count",
    "연도별 자동차 등록대수 추세"
)


# 2. 차량 종류별 전체 등록대수
bar_plot(
    df,
    "vehicle_type",
    "count",
    "차량 종류별 자동차 등록대수"
)


# 3. 연도별 × 차량 종류별 추세
trend = (
    df.groupby(
        ["year", "vehicle_type"],
        as_index=False
    )["count"]
    .sum()
)

plt.figure(figsize=(10, 5))

for vehicle in trend["vehicle_type"].unique():

    temp = trend[
        trend["vehicle_type"] == vehicle
    ]

    plt.plot(
        temp["year"],
        temp["count"],
        marker="o",
        label=vehicle
    )

plt.title("연도별·차량 종류별 자동차 등록대수")
plt.xlabel("연도")
plt.ylabel("등록대수")

plt.xticks(
    sorted(trend["year"].unique())
)

plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()


# 4. 용도별 자동차 등록대수
bar_plot(
    df,
    "usage",
    "count",
    "용도별 자동차 등록대수"
)


"""
연도별 전체 자동차 등록 추세
승용 / 승합 / 화물 등 차량 종류별 비교
2021~2025 차량 종류별 증감 추세
관용 / 자가용 / 영업용 비교
"""