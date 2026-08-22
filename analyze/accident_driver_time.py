import sqlite3
import pandas as pd

from models.visualization import bar_plot, heatmap_plot

# 막대그래프, 히트맵

# DB 불러오기
with sqlite3.connect("database/accident.db") as conn:
    df = pd.read_sql(
        "SELECT * FROM offending_driver_time",
        conn
    )


# wide → long 변환
df = df.melt(
    id_vars="age_group",
    var_name="time_slot",
    value_name="accidents"
)

# time_00_02 → 00~02
df["time_slot"] = (
    df["time_slot"]
    .str.replace("time_", "", regex=False)
    .str.replace("_", "~", regex=False)
)

df["accidents"] = pd.to_numeric(df["accidents"])


# 불명 제외
df = df[df["age_group"] != "불명"]


# 1. 연령대별 전체 사고 비교
bar_plot(
    df,
    "age_group",
    "accidents",
    "연령대별 가해운전자 사고 비교"
)


# 2. 시간대별 전체 사고 비교
bar_plot(
    df,
    "time_slot",
    "accidents",
    "시간대별 가해운전자 사고 비교"
)


# 3. 연령대 × 시간대 히트맵
heatmap_plot(
    df,
    row="age_group",
    column="time_slot",
    value="accidents",
    title="연령대별·시간대별 가해운전자 교통사고"
)