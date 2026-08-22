import sqlite3
import pandas as pd

from models.visualization import (
    line_plot,
    bar_plot
)

from models.time_series import forecast_best


# ============================================================
# DB 불러오기
# ============================================================

with sqlite3.connect(
    "database/accident.db"
) as conn:

    df = pd.read_sql(
        """
        SELECT
            sido,
            sigungu,
            year,
            accidents
        FROM accident_region_total
        """,
        conn
    )


df["year"] = pd.to_numeric(df["year"])
df["accidents"] = pd.to_numeric(df["accidents"])


# ============================================================
# 1. 전체 연도별 교통사고 추세
# ============================================================

line_plot(
    df,
    "year",
    "accidents",
    "연도별 전체 교통사고 추세"
)


# ============================================================
# 2. 시도별 교통사고 비교
# ============================================================

bar_plot(
    df,
    "sido",
    "accidents",
    "시도별 교통사고 비교"
)


# ============================================================
# 3. 특정 지역 선택
# ============================================================

SIDO = "서울"
SIGUNGU = "종로구"

region = df[
    (df["sido"] == SIDO) &
    (df["sigungu"] == SIGUNGU)
].copy()


# ============================================================
# 4. 특정 지역 연도별 추세
# ============================================================

line_plot(
    region,
    "year",
    "accidents",
    f"{SIDO} {SIGUNGU} 연도별 교통사고 추세"
)


# ============================================================
# 5. 날짜 컬럼 생성
# ============================================================

region["date"] = pd.to_datetime(
    region["year"]
    .astype(int)
    .astype(str)
    + "-01-01"
)


# ============================================================
# 6. ARIMA / Prophet 비교
#    + 최적 모델 선정
#    + 미래 3년 예측
# ============================================================

forecast = forecast_best(
    region,
    "date",
    "accidents",
    frequency="yearly",
    steps=3
)

print(forecast)