import sqlite3
import pandas as pd

from models.visualization import line_plot, bar_plot
from models.time_series import forecast_best


# DB 불러오기
with sqlite3.connect("database/accident.db") as conn:
    df = pd.read_sql(
        "SELECT * FROM offending_driver_age",
        conn
    )


# wide → long 변환
df = df.melt(
    id_vars="age_group",
    var_name="year",
    value_name="accidents"
)

# accident_2021 → 2021
df["year"] = (
    df["year"]
    .str.extract(r"(\d{4})")[0]
    .astype(int)
)

df["accidents"] = pd.to_numeric(df["accidents"])


# ============================================================
# 1. 연령대별 전체 사고 비교
# ============================================================

bar_plot(
    df,
    "age_group",
    "accidents",
    "연령대별 가해운전자 교통사고 비교"
)


# ============================================================
# 2. 연도별 전체 사고 추세
# ============================================================

line_plot(
    df,
    "year",
    "accidents",
    "연도별 가해운전자 교통사고 추세"
)


# ============================================================
# 3. 특정 연령대 분석
# ============================================================

AGE_GROUP = "65세 이상"

age_df = df[
    df["age_group"] == AGE_GROUP
].copy()


line_plot(
    age_df,
    "year",
    "accidents",
    f"{AGE_GROUP} 가해운전자 교통사고 추세"
)


# ============================================================
# 4. ARIMA / Prophet 비교 + 최적 모델 미래예측
# ============================================================

age_df["date"] = pd.to_datetime(
    age_df["year"].astype(str) + "-01-01"
)

forecast = forecast_best(
    age_df,
    "date",
    "accidents",
    frequency="yearly",
    steps=3
)

print("\n===== 미래 예측 결과 =====")
print(forecast)


"""
연령대별 2021~2025 누적 사고 비교
전체 연도별 사고 추세
65세 이상 사고 추세
65세 이상 ARIMA vs Prophet 성능 비교
오차가 작은 모델 자동 선정
2026~2028 사고 건수 예측
최적 모델 미래예측 차트
"""