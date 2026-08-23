import pandas as pd


# ============================================================
# 공통 유틸
# ============================================================

def clean_string_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    지정한 문자열 컬럼들의 결측치/공백을 정리한다.
    """
    for col in columns:
        if col in df.columns:
            df[col] = (
                df[col]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    return df


# ============================================================
# 1. 고령운전자 교통안전교육 예약정보
# ============================================================

def education_reservation_data(
    file_path: str = "data/제도/도로교통공단_고령운전자 교통안전교육_교육예약정보.xlsx"
) -> pd.DataFrame:

    df = pd.read_excel(file_path)

    # 컬럼 공백 제거
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    # 컬럼명 표준화
    df = df.rename(columns={
        "교육일자": "edu_date",
        "지부코드": "branch_name",
        "교육반코드": "course_name",
        "예약정원": "capacity"
    })

    # 날짜 변환
    if "edu_date" in df.columns:
        df["edu_date"] = pd.to_datetime(
            df["edu_date"],
            errors="coerce"
        ).dt.strftime("%Y-%m-%d")

    # 문자열 정리
    df = clean_string_columns(
        df,
        [
            "branch_name",
            "course_name"
        ]
    )

    # 예약정원 숫자 변환
    if "capacity" in df.columns:
        df["capacity"] = (
            df["capacity"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
        )

        df["capacity"] = pd.to_numeric(
            df["capacity"],
            errors="coerce"
        ).fillna(0).astype(int)

    # 날짜 없는 행 제거
    df = df.dropna(
        subset=["edu_date"]
    ).copy()

    # DB 적재 컬럼만 선택
    result = df[
        [
            "edu_date",
            "branch_name",
            "course_name",
            "capacity"
        ]
    ].copy()

    return result.reset_index(drop=True)


# ============================================================
# 2. 전국 고령운전자 정책 제도
# ============================================================

def old_driver_policy_data(
    file_path: str = "data/제도/전국 고령운전자 정책 제도.xlsx"
) -> pd.DataFrame:

    df = pd.read_excel(
        file_path,
        header=3
    )

    # 컬럼명 공백 제거
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    # 컬럼명 표준화
    df = df.rename(columns={
        "구분": "category",
        "현재 정책/제도": "policy_name",
        "시행 상태": "status",
        "대상": "target",
        "핵심 내용": "content",
        "지원·운영 규모": "scale",
        "시행/적용 시점": "start_date",
        "담당기관": "agency",
        "SaaS 활용 아이디어": "saas_idea",
        "추가 수집 필요 데이터": "needed_data",
        "출처 URL": "source_url",
        "확인일": "confirm_date"
    })

    # 문자열 정리
    df = clean_string_columns(
        df,
        [
            "category",
            "policy_name",
            "status",
            "target",
            "content",
            "scale",
            "start_date",
            "agency",
            "saas_idea",
            "needed_data",
            "source_url"
        ]
    )

    # 확인일 날짜 변환
    if "confirm_date" in df.columns:
        df["confirm_date"] = pd.to_datetime(
            df["confirm_date"],
            errors="coerce"
        ).dt.strftime("%Y-%m-%d")

    # 정책명 없는 행 제거
    if "policy_name" in df.columns:
        df = df[
            df["policy_name"] != ""
        ].copy()

    result = df[
        [
            "category",
            "policy_name",
            "status",
            "target",
            "content",
            "scale",
            "start_date",
            "agency",
            "saas_idea",
            "needed_data",
            "source_url",
            "confirm_date"
        ]
    ].copy()

    return result.reset_index(drop=True)


# ============================================================
# 3. 지역 특화 고령운전자 안전정책
# 실제 내용이 "지역별 운전면허 자진반납 지원.xlsx"에 들어있음
# ============================================================

def region_old_driver_policy_data(
    file_path: str = "data/제도/지역별 운전면허 자진반납 지원.xlsx"
) -> pd.DataFrame:

    df = pd.read_excel(
        file_path,
        header=3
    )

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    df = df.rename(columns={
        "지역": "region",
        "정책/사업": "policy_project",
        "기준연도": "base_year",
        "대상": "target",
        "지원·규모": "scale",
        "핵심 내용": "content",
        "현재 단계": "current_stage",
        "SaaS 활용 아이디어": "saas_idea",
        "출처 URL": "source_url",
        "비고": "note"
    })

    string_cols = [
        "region",
        "policy_project",
        "target",
        "scale",
        "content",
        "current_stage",
        "saas_idea",
        "source_url",
        "note"
    ]

    for col in string_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    df["base_year"] = pd.to_numeric(
        df["base_year"],
        errors="coerce"
    ).fillna(0).astype(int)

    df = df[
        df["region"] != ""
    ].copy()

    return df[
        [
            "region",
            "policy_project",
            "base_year",
            "target",
            "scale",
            "content",
            "current_stage",
            "saas_idea",
            "source_url",
            "note"
        ]
    ].reset_index(drop=True)


# ============================================================
# 4. 지역별 운전면허 자진반납 지원
# 실제 내용이 "지역 특화 고령운전자 안전정책.xlsx"에 들어있음
# ============================================================

def return_license_policy_data(
    file_path: str = "data/제도/지역 특화 고령운전자 안전정책.xlsx"
) -> pd.DataFrame:

    df = pd.read_excel(
        file_path,
        header=3
    )

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    df = df.rename(columns={
        "지역": "region",
        "정책명": "policy_name",
        "기준연도": "base_year",
        "대상 연령/조건": "target_condition",
        "일반 반납자 지원": "general_support",
        "실운전자 지원": "active_driver_support",
        "지원 형태": "support_type",
        "신청 방법": "apply_method",
        "거주/특이 조건": "residence_condition",
        "정책 상태": "status",
        "SaaS에서 볼 지표": "saas_metric",
        "출처 URL": "source_url",
        "검증 메모": "verify_memo"
    })

    string_cols = [
        "region",
        "policy_name",
        "target_condition",
        "general_support",
        "active_driver_support",
        "support_type",
        "apply_method",
        "residence_condition",
        "status",
        "saas_metric",
        "source_url",
        "verify_memo"
    ]

    for col in string_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .fillna("")
                .astype(str)
                .str.strip()
            )

    df["base_year"] = pd.to_numeric(
        df["base_year"],
        errors="coerce"
    ).fillna(0).astype(int)

    df = df[
        df["region"] != ""
    ].copy()

    return df[
        [
            "region",
            "policy_name",
            "base_year",
            "target_condition",
            "general_support",
            "active_driver_support",
            "support_type",
            "apply_method",
            "residence_condition",
            "status",
            "saas_metric",
            "source_url",
            "verify_memo"
        ]
    ].reset_index(drop=True)

# ============================================================
# 테스트
# ============================================================

if __name__ == "__main__":

    functions = {
        "education_reservation":
            education_reservation_data,

        "old_driver_policy":
            old_driver_policy_data,

        "region_old_driver_policy":
            region_old_driver_policy_data,

        "return_license_policy":
            return_license_policy_data,
    }

    for name, func in functions.items():

        print("\n" + "=" * 70)
        print(f"▶ {name}")

        try:
            df = func()

            print(f"✅ 전처리 성공: {len(df):,}행")
            print(f"컬럼: {list(df.columns)}")
            print(df.head())

        except Exception as e:
            print(f"❌ 전처리 실패")
            print(e)