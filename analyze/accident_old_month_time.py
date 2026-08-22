"""
연도별 전체 사고 추세
월별 전체 사고 규모
시간대별 전체 사고 규모
월 × 시간대 히트맵
월별 시계열 생성
ARIMA / SARIMA / Prophet 비교
오차가 가장 작은 모델로 미래 12개월 예측
"""

# analyze/old_driver_month_time.py

import sqlite3
import pandas as pd

from models.visualization import (
    line_plot,
    bar_plot,
    heatmap_plot
)

from models.time_series import forecast_best


# ============================================================
# DB 불러오기
# ============================================================

with sqlite3.connect("database/accident.db") as conn:
    df = pd.read_sql(
        "SELECT * FROM old_driver_month_time",
        conn
    )


# 숫자형 변환
df["year"] = pd.to_numeric(df["year"])
df["month"] = pd.to_numeric(df["month"])
df["accidents"] = pd.to_numeric(df["accidents"])


# ============================================================
# 1. 연도별 전체 사고 추세
# ============================================================

line_plot(
    df,
    "year",
    "accidents",
    "고령운전자 연도별 교통사고 추세"
)


# ============================================================
# 2. 월별 전체 사고 비교
# ============================================================

bar_plot(
    df,
    "month",
    "accidents",
    "고령운전자 월별 교통사고 비교"
)


# ============================================================
# 3. 시간대별 전체 사고 비교
# ============================================================

bar_plot(
    df,
    "time_slot",
    "accidents",
    "고령운전자 시간대별 교통사고 비교"
)


# ============================================================
# 4. 월 × 시간대 히트맵
# ============================================================

heatmap_plot(
    df,
    row="month",
    column="time_slot",
    value="accidents",
    title="고령운전자 월별·시간대별 교통사고"
)


# ============================================================
# 5. 월별 시계열 데이터 생성
# ============================================================

monthly = (
    df.groupby(
        ["year", "month"],
        as_index=False
    )["accidents"]
    .sum()
)

monthly["date"] = pd.to_datetime(
    dict(
        year=monthly["year"],
        month=monthly["month"],
        day=1
    )
)


# ============================================================
# 6. 월별 실제 사고 추세
# ============================================================

line_plot(
    monthly,
    "date",
    "accidents",
    "고령운전자 월별 교통사고 시계열"
)


# ============================================================
# 7. ARIMA / SARIMA / Prophet 비교
#    → 최적 모델 선정
#    → 미래 12개월 예측
# ============================================================

forecast = forecast_best(
    monthly,
    "date",
    "accidents",
    frequency="monthly",
    steps=12
)


# ============================================================
# 결과 출력
# ============================================================

print("\n===== 미래 12개월 예측 =====")
print(forecast)