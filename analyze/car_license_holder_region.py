# 지역별 → 연도별 → 면허별 → 특정 지역 상세 추세

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

from models.visualization import line_plot, bar_plot, heatmap_plot

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


# ============================================================
# DB 불러오기
# ============================================================

with sqlite3.connect("database/car.db") as conn:
    df = pd.read_sql(
        "SELECT * FROM license_holder_region",
        conn
    )

df["year"] = pd.to_numeric(df["year"])
df["count"] = pd.to_numeric(df["count"])

df["license_type"] = (
    df["license_main"] + " " + df["license_sub"]
)


# ============================================================
# 1. 지역별 면허 보유 현황
# ============================================================

bar_plot(
    df,
    "region",
    "count",
    "지역별 운전면허 보유 현황"
)


# ============================================================
# 2. 연도별 전국 면허 보유 추세
# ============================================================

line_plot(
    df,
    "year",
    "count",
    "연도별 운전면허 보유 추세"
)


# ============================================================
# 3. 면허 대분류별 현황
# ============================================================

bar_plot(
    df,
    "license_main",
    "count",
    "면허 대분류별 보유 현황"
)


# ============================================================
# 4. 면허 세부 종류별 현황
# ============================================================

bar_plot(
    df,
    "license_type",
    "count",
    "면허 종류별 보유 현황"
)


# ============================================================
# 5. 지역 × 연도
# ============================================================

heatmap_plot(
    df,
    row="region",
    column="year",
    value="count",
    title="지역별·연도별 운전면허 보유 현황"
)


# ============================================================
# 6. 지역별 연도 변화
# ============================================================

trend = (
    df.groupby(
        ["year", "region"],
        as_index=False
    )["count"]
    .sum()
)

plt.figure(figsize=(12, 6))

for region in trend["region"].unique():

    temp = trend[
        trend["region"] == region
    ]

    plt.plot(
        temp["year"],
        temp["count"],
        marker="o",
        label=region
    )

plt.title("지역별 운전면허 보유 추세")
plt.xlabel("연도")
plt.ylabel("면허 보유 수")

plt.xticks(
    sorted(trend["year"].unique())
)

plt.legend(
    bbox_to_anchor=(1.02, 1),
    loc="upper left"
)

plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()


# ============================================================
# 7. 특정 지역 분석
# ============================================================

REGION = "서울"

region_df = df[
    df["region"] == REGION
].copy()


# 특정 지역 연도별 추세
line_plot(
    region_df,
    "year",
    "count",
    f"{REGION} 연도별 운전면허 보유 추세"
)


# ============================================================
# 8. 특정 지역 면허 종류별
# ============================================================

bar_plot(
    region_df,
    "license_type",
    "count",
    f"{REGION} 면허 종류별 보유 현황"
)


# ============================================================
# 9. 특정 지역 면허별 연도 변화
# ============================================================

license_trend = (
    region_df
    .groupby(
        ["year", "license_type"],
        as_index=False
    )["count"]
    .sum()
)

plt.figure(figsize=(12, 6))

for license_type in license_trend["license_type"].unique():

    temp = license_trend[
        license_trend["license_type"] == license_type
    ]

    plt.plot(
        temp["year"],
        temp["count"],
        marker="o",
        label=license_type
    )

plt.title(f"{REGION} 면허 종류별 연도 변화")
plt.xlabel("연도")
plt.ylabel("면허 보유 수")

plt.xticks(
    sorted(license_trend["year"].unique())
)

plt.legend(
    bbox_to_anchor=(1.02, 1),
    loc="upper left"
)

plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()