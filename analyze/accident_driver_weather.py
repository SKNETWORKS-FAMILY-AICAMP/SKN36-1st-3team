import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

"""
각 연령대의 날씨별 전체 사고 규모
각 연령대의 연도별 × 날씨별 사고 추세
"""

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


# DB 불러오기
with sqlite3.connect("database/accident.db") as conn:
    df = pd.read_sql(
        "SELECT * FROM offending_driver_weather",
        conn
    )

df["year"] = pd.to_numeric(df["year"])
df["accidents"] = pd.to_numeric(df["accidents"])

# 불명 연령 제외
df = df[df["age_group"] != "불명"]


# ============================================================
# 연령대별 분석
# ============================================================

for age in df["age_group"].unique():

    age_df = df[df["age_group"] == age]

    # --------------------------------------------------------
    # 1. 날씨별 사고 규모
    # --------------------------------------------------------

    weather = (
        age_df
        .groupby("weather", as_index=False)["accidents"]
        .sum()
        .sort_values("accidents", ascending=False)
    )

    plt.figure(figsize=(8, 5))
    plt.bar(weather["weather"], weather["accidents"])

    plt.title(f"{age} 날씨별 교통사고")
    plt.xlabel("날씨")
    plt.ylabel("사고 건수")

    plt.tight_layout()
    plt.show()


    # --------------------------------------------------------
    # 2. 연도별 × 날씨별 사고 추세
    # --------------------------------------------------------

    trend = (
        age_df
        .groupby(["year", "weather"], as_index=False)["accidents"]
        .sum()
    )

    plt.figure(figsize=(10, 5))

    for w in trend["weather"].unique():

        temp = trend[trend["weather"] == w]

        plt.plot(
            temp["year"],
            temp["accidents"],
            marker="o",
            label=w
        )

    plt.title(f"{age} 연도별·날씨별 교통사고 추세")
    plt.xlabel("연도")
    plt.ylabel("사고 건수")

    plt.xticks(
        sorted(trend["year"].unique())
    )

    plt.legend()
    plt.grid(alpha=0.3)

    plt.tight_layout()
    plt.show()