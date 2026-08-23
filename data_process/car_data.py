import pandas as pd
import re


# ============================================================
# 공통 함수
# ============================================================

def read_csv_with_encoding(
    file_path: str,
    header=0,
    **kwargs
) -> pd.DataFrame:
    """
    여러 한글 인코딩을 순서대로 시도하여 CSV 파일을 읽는다.
    """

    encodings = [
        "utf-8-sig",
        "cp949",
        "utf-8",
        "euc-kr",
    ]

    for encoding in encodings:
        try:
            return pd.read_csv(
                file_path,
                encoding=encoding,
                header=header,
                **kwargs
            )
        except (UnicodeDecodeError, UnicodeError):
            continue

    raise ValueError(
        f"지원 가능한 인코딩으로 파일을 읽을 수 없습니다: {file_path}"
    )


def to_int(value, default: int = 0) -> int:
    """
    쉼표, 결측치, '-' 등이 포함된 값을 안전하게 int로 변환한다.
    """

    if pd.isna(value):
        return default

    value = str(value).replace(",", "").strip()

    if value in ["", "-", "nan", "None"]:
        return default

    try:
        return int(float(value))

    except (ValueError, TypeError):
        return default


# ============================================================
# 1. KOSIS 운전면허소지자 현황 - 성별
# ============================================================

def license_holder_gender_data(
    file_path: str = "data/자동차/KOSIS_운전면허소지자현황_성별.csv"
) -> pd.DataFrame:

    df = read_csv_with_encoding(
        file_path,
        header=None
    )

    # 0행: 연도
    years = df.iloc[0].ffill()

    # 1행: 남자 / 여자 / 계
    genders = (
        df.iloc[1]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # 실제 데이터
    data_df = df.iloc[2:].copy()

    # 면허 대분류 병합 셀 처리
    data_df.iloc[:, 0] = (
        data_df.iloc[:, 0]
        .replace("", None)
        .ffill()
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # 면허 세부종류
    data_df.iloc[:, 1] = (
        data_df.iloc[:, 1]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # 합계 행 제외
    valid_df = data_df[
        (
            ~data_df.iloc[:, 0].isin([
                "총계",
                "면허종별(1)",
                "면허종별(2)",
                "",
                "nan",
                "None",
            ])
        )
        &
        (
            ~data_df.iloc[:, 1].isin([
                "소계",
                "총계",
                "",
                "nan",
                "None",
            ])
        )
    ].copy()

    records = []

    for _, row in valid_df.iterrows():

        license_main = row.iloc[0]
        license_sub = row.iloc[1]

        for col_idx in range(2, len(df.columns)):

            year_val = str(
                years.iloc[col_idx]
            ).strip()

            gender_val = str(
                genders.iloc[col_idx]
            ).strip()

            year_match = re.search(
                r"(\d{4})",
                year_val
            )

            # 남/여 데이터만 사용
            if (
                year_match
                and gender_val in ["남자", "여자"]
            ):

                records.append({
                    "license_main": license_main,
                    "license_sub": license_sub,
                    "year": int(year_match.group(1)),
                    "gender": gender_val,
                    "count": to_int(
                        row.iloc[col_idx]
                    ),
                })

    return pd.DataFrame(
        records
    ).reset_index(drop=True)


# ============================================================
# 2. KOSIS 운전면허소지자 현황 - 연령별
# ============================================================

def license_holder_age_data(
    file_path: str = "data/자동차/KOSIS_운전면허소지자현황_연령대별.csv"
) -> pd.DataFrame:

    df = read_csv_with_encoding(
        file_path,
        header=None
    )

    # 다중 헤더
    years = df.iloc[0].ffill()

    license_mains = (
        df.iloc[1]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    license_subs = (
        df.iloc[2]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # 실제 데이터
    data_df = df.iloc[3:].copy()

    data_df.iloc[:, 0] = (
        data_df.iloc[:, 0]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    valid_df = data_df[
        ~data_df.iloc[:, 0].isin([
            "계",
            "총계",
            "연령대별(1)",
            "연령별",
            "",
            "nan",
            "None",
        ])
    ].copy()

    records = []

    for _, row in valid_df.iterrows():

        age_raw = str(row.iloc[0])

        age_match = re.search(
            r"(\d+)",
            age_raw
        )

        if not age_match:
            continue

        age = int(age_match.group(1))

        for col_idx in range(
            1,
            len(df.columns)
        ):

            year_val = str(
                years.iloc[col_idx]
            ).strip()

            license_main = str(
                license_mains.iloc[col_idx]
            ).strip()

            license_sub = str(
                license_subs.iloc[col_idx]
            ).strip()

            year_match = re.search(
                r"(\d{4})",
                year_val
            )

            if (
                year_match
                and license_sub not in [
                    "소계",
                    "총계",
                    "",
                ]
                and license_main not in [
                    "총계",
                    "계",
                    "",
                ]
            ):

                records.append({
                    "age": age,
                    "year": int(
                        year_match.group(1)
                    ),
                    "license_main": license_main,
                    "license_sub": license_sub,
                    "count": to_int(
                        row.iloc[col_idx]
                    ),
                })

    return pd.DataFrame(
        records
    ).reset_index(drop=True)


# ============================================================
# 3. KOSIS 운전면허소지자 현황 - 지역별
# ============================================================

def license_holder_region_data(
    file_path: str = "data/자동차/KOSIS_운전면허소지자현황_지역별.csv"
) -> pd.DataFrame:

    df = read_csv_with_encoding(
        file_path,
        header=None
    )

    # 다중 헤더
    years = df.iloc[0].ffill()

    license_mains = (
        df.iloc[1]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    license_subs = (
        df.iloc[2]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    data_df = df.iloc[3:].copy()

    data_df.iloc[:, 0] = (
        data_df.iloc[:, 0]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    valid_df = data_df[
        ~data_df.iloc[:, 0].isin([
            "계",
            "총계",
            "지역별(1)",
            "시도",
            "",
            "nan",
            "None",
        ])
    ].copy()

    records = []

    for _, row in valid_df.iterrows():

        region = row.iloc[0]

        for col_idx in range(
            1,
            len(df.columns)
        ):

            year_val = str(
                years.iloc[col_idx]
            ).strip()

            license_main = str(
                license_mains.iloc[col_idx]
            ).strip()

            license_sub = str(
                license_subs.iloc[col_idx]
            ).strip()

            year_match = re.search(
                r"(\d{4})",
                year_val
            )

            if (
                year_match
                and license_sub not in [
                    "소계",
                    "총계",
                    "",
                ]
                and license_main not in [
                    "총계",
                    "계",
                    "",
                ]
            ):

                records.append({
                    "region": region,
                    "year": int(
                        year_match.group(1)
                    ),
                    "license_main": license_main,
                    "license_sub": license_sub,
                    "count": to_int(
                        row.iloc[col_idx]
                    ),
                })

    return pd.DataFrame(
        records
    ).reset_index(drop=True)


# ============================================================
# 4. 운전면허 자진반납 - 2023
# ============================================================

def return_driver_license_2023_data(
    file_path: str = (
        "data/자동차/"
        "경찰청_운전면허 자진반납 연령별 시도청별 취소처분현황_2023년도.csv"
    )
) -> pd.DataFrame:

    df = read_csv_with_encoding(
        file_path
    )

    # 첫 번째 열 → 지역
    df.rename(
        columns={
            df.columns[0]: "region"
        },
        inplace=True
    )

    df["region"] = (
        df["region"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    valid_df = df[
        ~df["region"].isin([
            "계",
            "총계",
            "합계",
            "지역",
            "지역별",
            "",
            "nan",
            "None",
        ])
    ].copy()

    records = []

    for _, row in valid_df.iterrows():

        region = row["region"]

        for col_name in valid_df.columns[1:]:

            age_label = str(
                col_name
            ).strip()

            # 65세 미만
            if "미만" in age_label:

                # 분석 편의를 위한 대표값
                age = 64

            else:

                age_match = re.search(
                    r"(\d+)",
                    age_label
                )

                if not age_match:
                    continue

                age = int(
                    age_match.group(1)
                )

            records.append({
                "region": region,
                "age": age,
                "age_label": age_label,
                "count": to_int(
                    row[col_name]
                ),
            })

    return pd.DataFrame(
        records
    ).reset_index(drop=True)


# ============================================================
# 5. 운전면허 자진반납 - 2025
# ============================================================

def return_driver_license_2025(
    file_path: str = (
        "data/자동차/"
        "경찰청_운전면허 자진반납 연령별 시도청별 취소처분현황_2025년도.csv"
    )
) -> pd.DataFrame:

    df = read_csv_with_encoding(
        file_path
    )

    # 첫 번째 컬럼명 통일
    df.rename(
        columns={
            df.columns[0]: "region"
        },
        inplace=True
    )

    df["region"] = (
        df["region"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    valid_df = df[
        ~df["region"].isin([
            "계",
            "총계",
            "합계",
            "지역",
            "지역별",
            "",
            "nan",
            "None",
        ])
    ].copy()

    records = []

    for _, row in valid_df.iterrows():

        region = row["region"]

        for col_name in valid_df.columns[1:]:

            age_label = str(
                col_name
            ).strip()

            # 65세 미만
            if "미만" in age_label:

                age = 64

            else:

                age_match = re.search(
                    r"(\d+)",
                    age_label
                )

                if not age_match:
                    continue

                age = int(
                    age_match.group(1)
                )

            records.append({
                "region": region,
                "age": age,
                "age_label": age_label,
                "count": to_int(
                    row[col_name]
                ),
            })

    return pd.DataFrame(
        records
    ).reset_index(drop=True)


# ============================================================
# 6. 경찰청 운전면허소지자 지역별 종별 현황 - 2025
# ============================================================

def driver_license_region_data(
    file_path: str = (
        "data/자동차/"
        "경찰청_운전면허소지자 지역별 종별 현황_20251231.csv"
    )
) -> pd.DataFrame:

    df = read_csv_with_encoding(
        file_path
    )

    # 첫 두 열 이름 통일
    df.rename(
        columns={
            df.columns[0]: "region",
            df.columns[1]: "gender",
        },
        inplace=True
    )

    df["region"] = (
        df["region"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["gender"] = (
        df["gender"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    valid_df = df[
        (
            ~df["region"].isin([
                "계",
                "총계",
                "합계",
                "지역별",
                "",
                "nan",
                "None",
            ])
        )
        &
        (
            df["gender"].isin([
                "남",
                "여",
                "남자",
                "여자",
            ])
        )
    ].copy()

    records = []

    for _, row in valid_df.iterrows():

        region = row["region"]
        gender = row["gender"]

        # C열부터 각 면허종별
        for col_name in valid_df.columns[2:]:

            license_type = str(
                col_name
            ).strip()

            records.append({
                "region": region,
                "gender": gender,
                "license_type": license_type,
                "count": to_int(
                    row[col_name]
                ),
            })

    return pd.DataFrame(
        records
    ).reset_index(drop=True)


# ============================================================
# 7. 자동차 등록 현황 - 연도별
# ============================================================

def car_registration_data(
    file_path: str = (
        "data/자동차/"
        "국토교통통계누리_자동차등록현황보고_연도별.csv"
    )
) -> pd.DataFrame:

    df = None

    for encoding in [
        "utf-8-sig",
        "cp949",
        "utf-8",
        "euc-kr",
    ]:

        try:

            df = pd.read_csv(
                file_path,
                encoding=encoding,
                header=None,
                names=range(100),
                engine="python",
            )

            # 완전히 빈 열 제거
            df = df.dropna(
                how="all",
                axis=1
            )

            break

        except (
            UnicodeDecodeError,
            UnicodeError
        ):
            continue

    if df is None:
        raise ValueError(
            "파일을 읽을 수 없습니다."
        )

    # 0행: 차종
    vehicle_types = (
        df.iloc[0]
        .ffill()
    )

    # 1행: 용도
    usages = (
        df.iloc[1]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # 2행부터 실제 데이터
    data_df = df.iloc[2:].copy()

    records = []

    for _, row in data_df.iterrows():

        year_raw = str(
            row.iloc[0]
        ).strip()

        year_match = re.search(
            r"(\d{4})",
            year_raw
        )

        if not year_match:
            continue

        year = int(
            year_match.group(1)
        )

        for col_idx in range(
            1,
            len(df.columns)
        ):

            vehicle_type = str(
                vehicle_types.iloc[col_idx]
            ).strip()

            vehicle_usage = str(
                usages.iloc[col_idx]
            ).strip()

            # 계 / 총계 제외
            if (
                vehicle_usage not in [
                    "계",
                    "총계",
                    "",
                ]
                and vehicle_type not in [
                    "총계",
                    "계",
                    "nan",
                    "None",
                    "",
                ]
            ):

                records.append({
                    "year": year,
                    "vehicle_type": vehicle_type,

                    # usage 대신 변경
                    "vehicle_usage": vehicle_usage,

                    "count": to_int(
                        row.iloc[col_idx]
                    ),
                })

    return pd.DataFrame(
        records
    ).reset_index(drop=True)


# ============================================================
# 8. 자동차 등록 현황 - 지역 / 월별
# ============================================================

def car_registration_region_data(
    file_path: str = (
        "data/자동차/"
        "국토교통통계누리_자동차증록현황보고.csv"
    )
) -> pd.DataFrame:

    df = None

    for encoding in [
        "utf-8-sig",
        "cp949",
        "utf-8",
        "euc-kr",
    ]:

        try:

            df = pd.read_csv(
                file_path,
                encoding=encoding,
                header=None,
                names=range(100),
                engine="python",
            )

            # 비어있는 우측 열 제거
            df = df.dropna(
                how="all",
                axis=1
            )

            break

        except (
            UnicodeDecodeError,
            UnicodeError
        ):
            continue

    if df is None:
        raise ValueError(
            "파일을 읽을 수 없습니다."
        )

    # 차종
    vehicle_types = (
        df.iloc[0]
        .ffill()
    )

    # 용도
    usages = (
        df.iloc[1]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    data_df = df.iloc[2:].copy()

    records = []

    for _, row in data_df.iterrows():

        month = str(
            row.iloc[0]
        ).strip()

        sido = str(
            row.iloc[1]
        ).strip()

        sigungu = str(
            row.iloc[2]
        ).strip()

        # 날짜 형식이 아닌 행 제외
        if not re.search(
            r"\d{4}[-./]\d{1,2}",
            month
        ):
            continue

        # D열부터 등록 대수
        for col_idx in range(
            3,
            len(df.columns)
        ):

            vehicle_type = str(
                vehicle_types.iloc[col_idx]
            ).strip()

            vehicle_usage = str(
                usages.iloc[col_idx]
            ).strip()

            if (
                vehicle_usage not in [
                    "계",
                    "총계",
                    "",
                ]
                and vehicle_type not in [
                    "총계",
                    "계",
                    "nan",
                    "None",
                    "",
                ]
            ):

                records.append({
                    "month": month,
                    "sido": sido,
                    "sigungu": sigungu,
                    "vehicle_type": vehicle_type,

                    # usage 대신 변경
                    "vehicle_usage": vehicle_usage,

                    "count": to_int(
                        row.iloc[col_idx]
                    ),
                })

    return pd.DataFrame(
        records
    ).reset_index(drop=True)


# ============================================================
# 테스트 실행
# ============================================================

if __name__ == "__main__":

    functions = {
        "license_holder_gender":
            license_holder_gender_data,

        "license_holder_age":
            license_holder_age_data,

        "license_holder_region":
            license_holder_region_data,

        "return_driver_license_2023":
            return_driver_license_2023_data,

        "return_driver_license_2025":
            return_driver_license_2025,

        "driver_license_region":
            driver_license_region_data,

        "car_registration_year":
            car_registration_data,

        "car_registration_region":
            car_registration_region_data,
    }

    for name, func in functions.items():

        print(
            f"\n{'=' * 60}"
        )

        print(
            f"▶ {name}"
        )

        try:

            result = func()

            print(
                result.head()
            )

            print(
                f"shape: {result.shape}"
            )

            print(
                f"columns: {list(result.columns)}"
            )

        except Exception as e:

            print(
                f"❌ 오류: {e}"
            )