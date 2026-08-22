import sqlite3
import re
import pandas as pd

from models.visualization import line_plot, bar_plot


# ============================================================
# 1. DB 불러오기
# ============================================================

with sqlite3.connect("database/people.db") as conn:
    df = pd.read_sql(
        "SELECT * FROM resident_population",
        conn
    )


# ============================================================
# 2. 컬럼명 정리
# ============================================================

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
    .str.lower()
)

print("컬럼명:", df.columns.tolist())


# ============================================================
# 3. 지역 컬럼 찾기
# ============================================================

region_col = None

for col in df.columns:
    if "region" in col or "지역" in col:
        region_col = col
        break

if region_col is None:
    raise ValueError(
        "지역 컬럼을 찾을 수 없습니다.\n"
        f"현재 컬럼: {df.columns.tolist()}"
    )


# ============================================================
# 4. 지역명 뒤 행정코드 제거
#
# 서울특별시 (1100000000)
# → 서울특별시
# ============================================================

df[region_col] = (
    df[region_col]
    .astype(str)
    .str.replace(
        r"\s*\(\d+\)\s*$",
        "",
        regex=True
    )
    .str.strip()
)


# 컬럼명을 region으로 통일
df = df.rename(
    columns={
        region_col: "region"
    }
)


# ============================================================
# 5. wide → long 변환
#
# 2021년08월 총인구수
# 2021년09월 총인구수
# ...
#
# ↓
#
# region | year | month | date | population
# ============================================================

records = []

for _, row in df.iterrows():

    region = row["region"]

    for col in df.columns:

        match = re.search(
            r"(\d{4})년\s*(\d{1,2})월",
            str(col)
        )

        if not match:
            continue

        year = int(
            match.group(1)
        )

        month = int(
            match.group(2)
        )

        population = pd.to_numeric(
            row[col],
            errors="coerce"
        )

        if pd.isna(population):
            continue

        records.append({
            "region": region,
            "year": year,
            "month": month,
            "date": pd.Timestamp(
                year=year,
                month=month,
                day=1
            ),
            "population": population
        })


pop = pd.DataFrame(records)


# 데이터 확인
print("\n===== 변환 데이터 =====")
print(pop.head())


if pop.empty:
    raise ValueError(
        "월별 인구 데이터를 찾지 못했습니다. "
        "컬럼명을 확인해주세요."
    )


# ============================================================
# 6. 전국 월별 인구 추세
# ============================================================

national = pop[
    pop["region"] == "전국"
].copy()

if not national.empty:

    line_plot(
        national,
        "date",
        "population",
        "전국 월별 주민등록 인구 추세"
    )


# ============================================================
# 7. 최신 월 지역별 인구 비교
# ============================================================

latest_date = pop["date"].max()

latest = pop[
    (pop["date"] == latest_date) &
    (pop["region"] != "전국")
].copy()

bar_plot(
    latest,
    "region",
    "population",
    f"{latest_date.year}년 {latest_date.month}월 지역별 인구"
)


# ============================================================
# 8. 특정 지역 월별 인구 추세
# ============================================================

REGION = "서울특별시"

region_df = pop[
    pop["region"] == REGION
].copy()

if not region_df.empty:

    line_plot(
        region_df,
        "date",
        "population",
        f"{REGION} 월별 주민등록 인구 추세"
    )


# ============================================================
# 9. 최초 월 → 최근 월 지역별 증감
# ============================================================

first_date = pop["date"].min()

first = (
    pop[
        (pop["date"] == first_date) &
        (pop["region"] != "전국")
    ][
        [
            "region",
            "population"
        ]
    ]
    .rename(
        columns={
            "population":
            "first_population"
        }
    )
)

last = (
    pop[
        (pop["date"] == latest_date) &
        (pop["region"] != "전국")
    ][
        [
            "region",
            "population"
        ]
    ]
    .rename(
        columns={
            "population":
            "last_population"
        }
    )
)


change = pd.merge(
    first,
    last,
    on="region"
)


# ============================================================
# 10. 증감 / 증감률
# ============================================================

change["change"] = (
    change["last_population"]
    - change["first_population"]
)

change["change_rate"] = (
    change["change"]
    / change["first_population"]
    * 100
)

change = (
    change
    .sort_values(
        "change_rate",
        ascending=False
    )
    .reset_index(drop=True)
)


# ============================================================
# 결과 출력
# ============================================================

print("\n===== 분석 기간 =====")
print(
    first_date.strftime("%Y-%m"),
    "→",
    latest_date.strftime("%Y-%m")
)

print("\n===== 지역별 인구 증감 =====")

print(
    change.round(2)
)