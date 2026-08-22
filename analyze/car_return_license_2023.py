# 지역별 자진반납 규모, 연령별 자진반납 규모, 지역 × 연령 비교, 
# 특정 지역 연령 분포

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

from models.visualization import (
    bar_plot,
    line_plot,
    heatmap_plot
)

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


# DB 불러오기
with sqlite3.connect("database/car.db") as conn:
    df = pd.read_sql(
        "SELECT * FROM return_driver_license_2023",
        conn
    )

df["age"] = pd.to_numeric(df["age"])
df["count"] = pd.to_numeric(df["count"])


# ============================================================
# 1. 지역별 자진반납 현황
# ============================================================

bar_plot(
    df,
    "region",
    "count",
    "2023년 지역별 운전면허 자진반납 현황"
)


# ============================================================
# 2. 연령별 자진반납 현황
# ============================================================

line_plot(
    df,
    "age",
    "count",
    "2023년 연령별 운전면허 자진반납 현황"
)


# ============================================================
# 3. 지역 × 연령 히트맵
# ============================================================

heatmap_plot(
    df,
    row="region",
    column="age",
    value="count",
    title="2023년 지역별·연령별 운전면허 자진반납 현황"
)


# ============================================================
# 4. 특정 지역 연령별 자진반납
# ============================================================

REGION = "서울특별시"

region_df = df[
    df["region"] == REGION
].copy()

line_plot(
    region_df,
    "age",
    "count",
    f"{REGION} 연령별 운전면허 자진반납 현황"
)


# ============================================================
# 5. 65세 이상만 분석
# ============================================================

old_df = df[
    df["age"] >= 65
].copy()

bar_plot(
    old_df,
    "region",
    "count",
    "2023년 지역별 65세 이상 운전면허 자진반납 현황"
)


# ============================================================
# 6. 가장 많이 반납한 연령 TOP 10
# ============================================================

age_rank = (
    df.groupby("age", as_index=False)["count"]
    .sum()
    .sort_values("count", ascending=False)
    .head(10)
)

plt.figure(figsize=(10, 5))

plt.bar(
    age_rank["age"].astype(str),
    age_rank["count"]
)

plt.title("2023년 운전면허 자진반납 연령 TOP 10")
plt.xlabel("연령")
plt.ylabel("반납 건수")

plt.tight_layout()
plt.show()