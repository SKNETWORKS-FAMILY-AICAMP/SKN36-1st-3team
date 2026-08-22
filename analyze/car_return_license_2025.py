import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from models.visualization import bar_plot, line_plot, heatmap_plot

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


# ============================================================
# 데이터 불러오기
# ============================================================

with sqlite3.connect("database/car.db") as conn:
    df23 = pd.read_sql(
        "SELECT * FROM return_driver_license_2023",
        conn
    )

    df25 = pd.read_sql(
        "SELECT * FROM return_driver_license_2025",
        conn
    )


for df in [df23, df25]:
    df["age"] = pd.to_numeric(df["age"])
    df["count"] = pd.to_numeric(df["count"])


# 65세 이상
df23 = df23[df23["age"] >= 65]
df25 = df25[df25["age"] >= 65]



## 2025년도만

# ============================================================
# 1. 전체 지역별 자진반납
# ============================================================

bar_plot(
    df,
    "region",
    "count",
    "2025년 지역별 운전면허 자진반납 현황"
)


# ============================================================
# 2. 전체 연령별 자진반납
# ============================================================

age_df = (
    df.groupby("age", as_index=False)["count"]
    .sum()
    .sort_values("age")
)

line_plot(
    age_df,
    "age",
    "count",
    "2025년 연령별 운전면허 자진반납 현황"
)


# ============================================================
# 3. 65세 이상만 추출
# ============================================================

old_df = df[
    df["age"] >= 65
].copy()


# ============================================================
# 4. 65세 이상 지역별 자진반납
# ============================================================

bar_plot(
    old_df,
    "region",
    "count",
    "2025년 지역별 65세 이상 운전면허 자진반납"
)


# ============================================================
# 5. 65세 이상 연령별 자진반납
# ============================================================

old_age = (
    old_df
    .groupby("age", as_index=False)["count"]
    .sum()
    .sort_values("age")
)

line_plot(
    old_age,
    "age",
    "count",
    "2025년 65세 이상 연령별 운전면허 자진반납"
)


# ============================================================
# 6. 지역 × 연령 히트맵
# ============================================================

heatmap_plot(
    old_df,
    row="region",
    column="age",
    value="count",
    title="2025년 지역별·연령별 운전면허 자진반납"
)


# ============================================================
# 7. 자진반납이 많은 연령 TOP 10
# ============================================================

top_age = (
    old_df
    .groupby("age", as_index=False)["count"]
    .sum()
    .sort_values("count", ascending=False)
    .head(10)
)

plt.figure(figsize=(10, 5))

plt.bar(
    top_age["age"].astype(str),
    top_age["count"]
)

plt.title("2025년 65세 이상 자진반납 연령 TOP 10")
plt.xlabel("연령")
plt.ylabel("자진반납 건수")

plt.tight_layout()
plt.show()


# ============================================================
# 8. 결과 출력
# ============================================================

print("\n===== 2025년 운전면허 자진반납 =====")

print(
    f"전체 자진반납: {df['count'].sum():,}건"
)

print(
    f"65세 이상 자진반납: {old_df['count'].sum():,}건"
)

rate = (
    old_df["count"].sum()
    / df["count"].sum()
    * 100
)

print(
    f"전체 반납 중 65세 이상 비율: {rate:.2f}%"
)


print("\n===== 65세 이상 자진반납 연령 TOP 10 =====")

print(
    top_age.to_string(index=False)
)


# ============================================================
# 1. 2023 vs 2025 전체 자진반납
# ============================================================

total = pd.DataFrame({
    "year": [2023, 2025],
    "count": [
        df23["count"].sum(),
        df25["count"].sum()
    ]
})

plt.figure(figsize=(7, 5))

plt.bar(
    total["year"].astype(str),
    total["count"]
)

plt.title("65세 이상 운전면허 자진반납 비교")
plt.xlabel("연도")
plt.ylabel("자진반납 건수")

plt.tight_layout()
plt.show()


# ============================================================
# 2. 연령별 2023 vs 2025 비교
# ============================================================

age23 = (
    df23.groupby("age")["count"]
    .sum()
)

age25 = (
    df25.groupby("age")["count"]
    .sum()
)

age_compare = pd.concat(
    [age23, age25],
    axis=1
).fillna(0)

age_compare.columns = [
    "2023",
    "2025"
]

age_compare.plot(
    kind="bar",
    figsize=(13, 6)
)

plt.title("65세 이상 연령별 자진반납 비교")
plt.xlabel("연령")
plt.ylabel("자진반납 건수")
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()


# ============================================================
# 3. 지역별 2023 vs 2025 비교
# ============================================================

region23 = (
    df23.groupby("region")["count"]
    .sum()
)

region25 = (
    df25.groupby("region")["count"]
    .sum()
)

region_compare = pd.concat(
    [region23, region25],
    axis=1
).fillna(0)

region_compare.columns = [
    "2023",
    "2025"
]

region_compare.plot(
    kind="bar",
    figsize=(13, 6)
)

plt.title("지역별 65세 이상 운전면허 자진반납 비교")
plt.xlabel("지역")
plt.ylabel("자진반납 건수")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()
plt.show()


# ============================================================
# 4. 지역별 증감률
# ============================================================

region_compare["증감률"] = (
    (region_compare["2025"] - region_compare["2023"])
    / region_compare["2023"]
    * 100
)

change = (
    region_compare["증감률"]
    .sort_values(ascending=False)
)

plt.figure(figsize=(12, 6))

plt.bar(
    change.index,
    change.values
)

plt.axhline(
    0,
    color="black",
    linewidth=1
)

plt.title("2023 → 2025 지역별 자진반납 증감률")
plt.xlabel("지역")
plt.ylabel("증감률 (%)")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()
plt.show()


# ============================================================
# 결과 출력
# ============================================================

print("\n===== 65세 이상 자진반납 =====")

print(
    f"2023년: {df23['count'].sum():,}건"
)

print(
    f"2025년: {df25['count'].sum():,}건"
)

change_rate = (
    (df25["count"].sum() - df23["count"].sum())
    / df23["count"].sum()
    * 100
)

print(
    f"2023 → 2025 증감률: {change_rate:.2f}%"
)

print("\n===== 지역별 비교 =====")
print(region_compare.round(2))




"""
car_return_license_2023.py
→ 2023년 단독 분석

car_return_license_2025.py
→ 2025년 단독 분석

car_return_license_compare.py
→ 2023년 vs 2025년 비교

compare_old_license_return.py
→ 65세 이상 면허 보유자 vs 자진반납자
"""