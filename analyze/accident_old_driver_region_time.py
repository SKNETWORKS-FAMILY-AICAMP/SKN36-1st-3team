# 시도별 → 시군구별 → 연도별 → 월별 → 특정 지역 월별 추세

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

from models.visualization import line_plot, bar_plot, heatmap_plot

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


# DB 불러오기
with sqlite3.connect("database/accident.db") as conn:
    df = pd.read_sql(
        "SELECT * FROM old_driver_region_time",
        conn
    )

df["year"] = pd.to_numeric(df["year"])
df["month"] = pd.to_numeric(df["month"])
df["accidents"] = pd.to_numeric(df["accidents"])


# ============================================================
# 1. 시도별 사고 비교
# ============================================================

bar_plot(
    df,
    "sido",
    "accidents",
    "시도별 고령운전자 교통사고"
)


# ============================================================
# 2. 시군구별 사고 비교
#    같은 '중구' 등이 있으므로 시도+시군구 결합
# ============================================================

df["region"] = df["sido"] + " " + df["sigungu"]

bar_plot(
    df,
    "region",
    "accidents",
    "시군구별 고령운전자 교통사고",
    top_n=20
)


# ============================================================
# 3. 연도별 사고 추세
# ============================================================

line_plot(
    df,
    "year",
    "accidents",
    "연도별 고령운전자 교통사고 추세"
)


# ============================================================
# 4. 월별 사고 비교
# ============================================================

monthly = (
    df.groupby("month", as_index=False)["accidents"]
    .sum()
    .sort_values("month")
)

plt.figure(figsize=(10, 5))
plt.plot(
    monthly["month"],
    monthly["accidents"],
    marker="o"
)

plt.title("월별 고령운전자 교통사고")
plt.xlabel("월")
plt.ylabel("사고 건수")
plt.xticks(range(1, 13))
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()


# ============================================================
# 5. 시도별 × 월별 히트맵
# ============================================================

heatmap_plot(
    df,
    row="sido",
    column="month",
    value="accidents",
    title="시도별·월별 고령운전자 교통사고"
)


# ============================================================
# 6. 특정 시도 → 시군구별 비교
# ============================================================

SIDO = "서울"

sido_df = df[df["sido"] == SIDO]

bar_plot(
    sido_df,
    "sigungu",
    "accidents",
    f"{SIDO} 시군구별 고령운전자 교통사고"
)


# ============================================================
# 7. 특정 시군구 월별 추세
# ============================================================

SIGUNGU = "종로구"

region_df = df[
    (df["sido"] == SIDO) &
    (df["sigungu"] == SIGUNGU)
].copy()

region_month = (
    region_df
    .groupby(["year", "month"], as_index=False)["accidents"]
    .sum()
)

region_month["date"] = pd.to_datetime(
    dict(
        year=region_month["year"],
        month=region_month["month"],
        day=1
    )
)

plt.figure(figsize=(11, 5))

plt.plot(
    region_month["date"],
    region_month["accidents"],
    marker="o"
)

plt.title(f"{SIDO} {SIGUNGU} 월별 고령운전자 교통사고 추세")
plt.xlabel("연도")
plt.ylabel("사고 건수")
plt.grid(alpha=0.3)

plt.tight_layout()
plt.show()

"""
① 시도별 고령운전자 교통사고
        ↓ 창 닫기
② 시군구별 고령운전자 교통사고 TOP 20
        ↓
③ 연도별 고령운전자 교통사고 추세
        ↓
④ 월별 고령운전자 교통사고
        ↓
⑤ 시도별 × 월별 히트맵
        ↓
⑥ 서울 시군구별 교통사고
        ↓
⑦ 서울 종로구 월별 사고 추세
"""