import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


# ============================================================
# DB 불러오기
# ============================================================

with sqlite3.connect("database/people.db") as conn:
    df = pd.read_sql(
        "SELECT * FROM local_population",
        conn
    )


# ============================================================
# wide → long 변환
# ============================================================

pop_cols = [
    "population_2021",
    "population_2022",
    "population_2023",
    "population_2024",
    "population_2025"
]

long_df = df.melt(
    id_vars="region",
    value_vars=pop_cols,
    var_name="year",
    value_name="population"
)

long_df["year"] = (
    long_df["year"]
    .str.replace("population_", "")
    .astype(int)
)

long_df["population"] = pd.to_numeric(
    long_df["population"]
)


# ============================================================
# 1. 2025년 지역별 인구
# ============================================================

latest = (
    long_df[long_df["year"] == 2025]
    .sort_values("population", ascending=False)
)

plt.figure(figsize=(12, 6))

plt.bar(
    latest["region"],
    latest["population"]
)

plt.title("2025년 지역별 인구")
plt.xlabel("지역")
plt.ylabel("인구")

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# ============================================================
# 2. 연도별 전국 인구 추세
# ============================================================

yearly = (
    long_df
    .groupby("year", as_index=False)["population"]
    .sum()
)

plt.figure(figsize=(9, 5))

plt.plot(
    yearly["year"],
    yearly["population"],
    marker="o"
)

plt.title("연도별 전국 인구 추세")
plt.xlabel("연도")
plt.ylabel("인구")

plt.xticks(yearly["year"])
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()


# ============================================================
# 3. 지역별 인구 변화
# ============================================================

plt.figure(figsize=(12, 6))

for region in long_df["region"].unique():

    temp = long_df[
        long_df["region"] == region
    ]

    plt.plot(
        temp["year"],
        temp["population"],
        marker="o",
        label=region
    )

plt.title("지역별 인구 변화")
plt.xlabel("연도")
plt.ylabel("인구")

plt.xticks(
    sorted(long_df["year"].unique())
)

plt.legend(
    bbox_to_anchor=(1.02, 1),
    loc="upper left"
)

plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()


# ============================================================
# 4. 2021 → 2025 인구 증감
# ============================================================

change = df[
    ["region", "population_2021", "population_2025"]
].copy()

change["증감"] = (
    change["population_2025"]
    - change["population_2021"]
)

change["증감률"] = (
    change["증감"]
    / change["population_2021"]
    * 100
)

change = change.sort_values(
    "증감률",
    ascending=False
)


# ============================================================
# 5. 지역별 인구 증감률
# ============================================================

plt.figure(figsize=(12, 6))

plt.bar(
    change["region"],
    change["증감률"]
)

plt.axhline(
    0,
    color="black",
    linewidth=1
)

plt.title("2021 → 2025 지역별 인구 증감률")
plt.xlabel("지역")
plt.ylabel("증감률 (%)")

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# ============================================================
# 결과 출력
# ============================================================

print("\n===== 2021 → 2025 지역별 인구 변화 =====")

print(
    change[
        [
            "region",
            "population_2021",
            "population_2025",
            "증감",
            "증감률"
        ]
    ].round(2)
)