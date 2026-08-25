import pandas as pd
import re


# ============================================================
# 1. e-나라지표 지역별 인구
# ============================================================

def load_local_people_data(
    file_path: str = "data/인구/e-나라지표_지역별 인구.xlsx"
) -> pd.DataFrame:

    df = pd.read_excel(
        file_path,
        header=None
    )

    # 지역 + 2021~2025 인구
    local_people = df.iloc[
        4:,
        [0, 1, 3, 5, 7, 9]
    ].copy()

    local_people.columns = [
        "region",
        "population_2021",
        "population_2022",
        "population_2023",
        "population_2024",
        "population_2025",
    ]

    # 지역명 정리
    local_people["region"] = (
        local_people["region"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # 계 / 빈값 제외
    local_people = local_people[
        ~local_people["region"].isin([
            "계",
            "총계",
            "합계",
            "",
            "nan",
            "None",
        ])
    ].copy()

    # wide → long
    local_people = local_people.melt(
        id_vars=["region"],
        var_name="year",
        value_name="population"
    )

    # population_2021 → 2021
    local_people["year"] = (
        local_people["year"]
        .str.extract(r"(\d{4})")[0]
        .astype(int)
    )

    # 인구 숫자 변환
    local_people["population"] = (
        local_people["population"]
        .astype(str)
        .str.replace(",", "", regex=False)
    )

    local_people["population"] = pd.to_numeric(
        local_people["population"],
        errors="coerce"
    )

    # 숫자로 변환되지 않은 행 제거
    local_people = local_people.dropna(
        subset=["population"]
    )

    local_people["population"] = (
        local_people["population"]
        .astype(int)
    )

    return local_people.reset_index(drop=True)


# ============================================================
# 2. 행정안전부 연령별 인구 현황
# ============================================================

def load_age_population_data(
    file_path: str = "data/인구/행정안전부_연령별인구현황.csv"
) -> pd.DataFrame:

    df = pd.read_csv(
        file_path,
        encoding="cp949"
    )

    # 행정구역 정리
    # 서울특별시 (1100000000) → 서울특별시
    df["행정구역"] = (
        df["행정구역"]
        .astype(str)
        .str.replace(
            r"\s*\(\d+\)\s*$",
            "",
            regex=True
        )
        .str.strip()
    )

    df = df.rename(
        columns={
            "행정구역": "region"
        }
    )

    # 전국 / 합계 제외
    df = df[
        ~df["region"].isin([
            "전국",
            "계",
            "총계",
            "합계",
            "",
            "nan",
            "None",
        ])
    ].copy()

    # wide → long
    age_population = df.melt(
        id_vars=["region"],
        var_name="variable",
        value_name="population"
    )

    # 총인구수 / 연령구간인구수 제외
    age_population = age_population[
        ~age_population["variable"].str.contains(
            "총인구수|연령구간인구수",
            regex=True
        )
    ].copy()

    # 2026년07월_남_60~69세 → 2026
    age_population["year"] = (
        age_population["variable"]
        .str.extract(r"(\d{4})년")[0]
    )

    age_population["year"] = pd.to_numeric(
        age_population["year"],
        errors="coerce"
    )

    # 성별 추출
    age_population["gender"] = (
        age_population["variable"]
        .str.extract(r"월_(계|남|여)_")[0]
    )

    # 연령대 추출
    age_population["age_group"] = (
        age_population["variable"]
        .str.extract(
            r"월_(?:계|남|여)_(.+)$"
        )[0]
    )

    # 인구수 숫자 변환
    age_population["population"] = (
        age_population["population"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    age_population["population"] = pd.to_numeric(
        age_population["population"],
        errors="coerce"
    )

    # 결측치 제거
    age_population = age_population.dropna(
        subset=[
            "year",
            "gender",
            "age_group",
            "population",
        ]
    )

    # 자료형 변환
    age_population["year"] = (
        age_population["year"]
        .astype(int)
    )

    age_population["population"] = (
        age_population["population"]
        .astype(int)
    )

    # 필요한 컬럼만 남기기
    age_population = age_population[
        [
            "region",
            "year",
            "gender",
            "age_group",
            "population",
        ]
    ]

    return age_population.reset_index(drop=True)