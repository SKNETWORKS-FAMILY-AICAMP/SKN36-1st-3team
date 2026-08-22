# 나이별 / 연도별 / 면허 대분류별 / 면허 세부종류별
# 나이 × 면허종류, 연도 × 나이

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

from models.visualization import (
    line_plot,
    bar_plot,
    heatmap_plot
)

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


# DB 불러오기
with sqlite3.connect("database/car.db") as conn:
    df = pd.read_sql(
        "SELECT * FROM license_holder_age",
        conn
    )

df["age"] = pd.to_numeric(df["age"])
df["year"] = pd.to_numeric(df["year"])
df["count"] = pd.to_numeric(df["count"])


# ============================================================
# 1. 나이별 전체 면허 보유 수
# ============================================================

line_plot(
    df,
    "age",
    "count",
    "나이별 운전면허 보유 현황"
)


# ============================================================
# 2. 연도별 전체 면허 보유 수
# ============================================================

line_plot(
    df,
    "year",
    "count",
    "연도별 운전면허 보유 추세"
)


# ============================================================
# 3. 면허 대분류별
# ============================================================

bar_plot(
    df,
    "license_main",
    "count",
    "면허 대분류별 보유 현황"
)


# ============================================================
# 4. 면허 세부종류별
# ============================================================

df["license_type"] = (
    df["license_main"]
    + " "
    + df["license_sub"]
)

bar_plot(
    df,
    "license_type",
    "count",
    "면허 종류별 보유 현황"
)


# ============================================================
# 5. 나이 × 면허 대분류
# ============================================================

heatmap_plot(
    df,
    row="age",
    column="license_main",
    value="count",
    title="나이별·면허 대분류별 보유 현황"
)


# ============================================================
# 6. 연도 × 면허 대분류
# ============================================================

heatmap_plot(
    df,
    row="year",
    column="license_main",
    value="count",
    title="연도별·면허 대분류별 보유 현황"
)


# ============================================================
# 7. 특정 면허 종류의 나이별 분포
# ============================================================

LICENSE_MAIN = "1종"
LICENSE_SUB = "보통"

license_df = df[
    (df["license_main"] == LICENSE_MAIN) &
    (df["license_sub"] == LICENSE_SUB)
].copy()

line_plot(
    license_df,
    "age",
    "count",
    f"{LICENSE_MAIN} {LICENSE_SUB} 나이별 면허 보유 현황"
)


# ============================================================
# 8. 고령운전자 면허 보유 추세
# ============================================================

old_df = df[
    df["age"] >= 65
].copy()

line_plot(
    old_df,
    "year",
    "count",
    "65세 이상 운전면허 보유 추세"
)