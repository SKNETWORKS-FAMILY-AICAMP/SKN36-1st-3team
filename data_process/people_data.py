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
# 2. 행정안전부 주민등록인구 및 세대현황 - 월간
# ============================================================

def resident_regristration_data(
    file_path: str = "data/인구/행정안전부_주민등록인구및세대현황_월간.csv"
) -> pd.DataFrame:

    # CSV 읽기
    df = pd.read_csv(
        file_path,
        encoding="cp949"
    )

    # 첫 번째 컬럼 = 행정구역
    region_col = df.columns[0]

    # 총인구수 컬럼만 선택
    population_cols = [
        col
        for col in df.columns
        if "총인구수" in str(col)
    ]

    resident_people = df[
        [region_col] + population_cols
    ].copy()

    # 지역 컬럼명 통일
    resident_people.rename(
        columns={
            region_col: "region"
        },
        inplace=True
    )

    # 지역명 정리
    resident_people["region"] = (
        resident_people["region"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # 빈 지역 제거
    resident_people = resident_people[
        ~resident_people["region"].isin([
            "",
            "nan",
            "None",
        ])
    ].copy()

    # wide → long
    resident_people = resident_people.melt(
        id_vars=["region"],
        var_name="month_raw",
        value_name="population"
    )

    # 컬럼명에서 YYYYMM 추출
    resident_people["month"] = (
        resident_people["month_raw"]
        .astype(str)
        .str.extract(r"(\d{6})")[0]
    )

    # 혹시 2025년01월 형태라면 추가 처리
    missing_month = (
        resident_people["month"].isna()
    )

    if missing_month.any():

        extracted = (
            resident_people.loc[
                missing_month,
                "month_raw"
            ]
            .astype(str)
            .str.extract(
                r"(\d{4}).*?(\d{1,2})"
            )
        )

        resident_people.loc[
            missing_month,
            "month"
        ] = (
            extracted[0]
            + "-"
            + extracted[1].str.zfill(2)
        )

    # 202501 → 2025-01
    mask = (
        resident_people["month"]
        .astype(str)
        .str.match(r"^\d{6}$")
    )

    resident_people.loc[
        mask,
        "month"
    ] = (
        resident_people.loc[
            mask,
            "month"
        ].str[:4]
        + "-"
        + resident_people.loc[
            mask,
            "month"
        ].str[4:6]
    )

    # 인구 숫자 변환
    resident_people["population"] = (
        resident_people["population"]
        .astype(str)
        .str.replace(",", "", regex=False)
    )

    resident_people["population"] = pd.to_numeric(
        resident_people["population"],
        errors="coerce"
    )

    resident_people = resident_people.dropna(
        subset=[
            "month",
            "population"
        ]
    )

    resident_people["population"] = (
        resident_people["population"]
        .astype(int)
    )

    # 필요한 컬럼만 반환
    resident_people = resident_people[
        [
            "month",
            "region",
            "population"
        ]
    ]

    return resident_people.reset_index(drop=True)


# ============================================================
# 테스트
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("▶ 지역별 연간 인구")

    df1 = load_local_people_data()

    print(df1.head())
    print(df1.shape)
    print(df1.columns.tolist())

    print("\n" + "=" * 60)
    print("▶ 주민등록 월별 인구")

    df2 = resident_regristration_data()

    print(df2.head())
    print(df2.shape)
    print(df2.columns.tolist())