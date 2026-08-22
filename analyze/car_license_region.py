# 지역별/성별/면허종류별



import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

from models.visualization import bar_plot, heatmap_plot


# DB 불러오기
with sqlite3.connect("database/car.db") as conn:
    df = pd.read_sql(
        "SELECT * FROM driver_license_region",
        conn
    )

df["count"] = pd.to_numeric(df["count"])


# ============================================================
# 1. 지역별 전체 면허 보유 수
# ============================================================

bar_plot(
    df,
    "region",
    "count",
    "지역별 운전면허 보유 현황"
)


# ============================================================
# 2. 남 / 여 비교
# ============================================================

bar_plot(
    df,
    "gender",
    "count",
    "성별 운전면허 보유 현황"
)


# ============================================================
# 3. 면허 종류별 비교
# ============================================================

bar_plot(
    df,
    "license_type",
    "count",
    "면허 종류별 보유 현황"
)


# ============================================================
# 4. 지역 × 성별 히트맵
# ============================================================

heatmap_plot(
    df,
    row="region",
    column="gender",
    value="count",
    title="지역별·성별 운전면허 보유 현황"
)


# ============================================================
# 5. 특정 지역 남 / 여 비교
# ============================================================

REGION = "서울"

region_df = df[
    df["region"] == REGION
].copy()

bar_plot(
    region_df,
    "gender",
    "count",
    f"{REGION} 성별 운전면허 보유 현황"
)


# ============================================================
# 6. 특정 지역 면허종류별 비교
# ============================================================

bar_plot(
    region_df,
    "license_type",
    "count",
    f"{REGION} 면허 종류별 보유 현황"
)


# ============================================================
# 7. 특정 지역에서 남 / 여 × 면허종류 비교
# ============================================================

pivot = pd.pivot_table(
    region_df,
    index="license_type",
    columns="gender",
    values="count",
    aggfunc="sum",
    fill_value=0
)

pivot.plot(
    kind="bar",
    figsize=(12, 6)
)

plt.title(f"{REGION} 성별·면허종류별 운전면허 보유 현황")
plt.xlabel("면허 종류")
plt.ylabel("보유 수")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()
plt.show()


"""
지역별 전체 면허 보유 수
남성 vs 여성 전체 비교
1종 대형 / 1종 보통 / 2종 보통 등 면허종류별 비교
지역 × 성별 히트맵
서울 남/여 비교
서울 면허종류별 비교
서울에서 각 면허종류별 남/여 차이
"""