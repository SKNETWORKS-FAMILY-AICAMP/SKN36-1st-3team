import pandas as pd
import re


# 1. 도로교통공단_고령운전자 교통안전교육_교육예약정보.xlsx
#         edu_date        branch_name     course_name       capacity
# 0     2020-01-02       도봉시험장   고령자교육(의무)        30
# 1     2020-01-02       도봉시험장   고령자교육(의무)        20
# 2     2020-01-02       제주시험장   고령자교육(의무)        11
# 3     2020-01-02       제주시험장   고령자교육(의무)        11
# 4     2020-01-02       전남시험장   고령자교육(의무)        15
def education_reservation_data(file_path: str = "data/제도/도로교통공단_고령운전자 교통안전교육_교육예약정보.xlsx") -> pd.DataFrame:
    # 1. 엑셀 불러오기 (첫 번째 행을 컬럼명/헤더로 지정)
    df = pd.read_excel(file_path) # header=0 이 기본값입니다.
    
    # 2. 컬럼명 공백 제거 및 표준화
    df.columns = df.columns.astype(str).str.strip()

    # 컬럼명 매핑 (영문 변환)
    df = df.rename(columns={
        "교육일자": "edu_date",
        "지부코드": "branch_name",
        "교육반코드": "course_name",
        "예약정원": "capacity"
    })

    # 3. 데이터 타입 정제
    # 날짜 정제 (YYYY-MM-DD)
    df["edu_date"] = pd.to_datetime(df["edu_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    
    # 문자기반 열 정제
    df["branch_name"] = df["branch_name"].fillna("").astype(str).str.strip()
    df["course_name"] = df["course_name"].fillna("").astype(str).str.strip()

    # 예약정원 수치 정제 (쉼표 제거 및 정수 변환)
    df["capacity"] = (
        df["capacity"]
        .astype(str)
        .str.replace(",", "")
        .str.strip()
    )
    df["capacity"] = pd.to_numeric(df["capacity"], errors="coerce").fillna(0).astype(int)

    # 4. 결측 날짜 제거 및 인덱스 재설정
    df = df.dropna(subset=["edu_date"]).reset_index(drop=True)

    return df


# 2. 전국 고령운전자 정책 제도.xlsx
#         category           policy_name               status  ...          needed_data                                 source_url confirm_date
# 0      면허관리       고령자 면허 갱신주기 단축      시행 중  ...     시도별 75세 이상 갱신 대상자·완료자 수  https://www.law.go.kr/LSW/lsInfoP.do?ancNo=210...   2026-08-20
def old_driver_policy_data(file_path: str = "data/제도/전국 고령운전자 정책 제도.xlsx") -> pd.DataFrame:
    # 1. 엑셀 불러오기 (4번째 행(인덱스 3)을 헤더로 지정)
    df = pd.read_excel(file_path, header=3)
    
    # 2. 컬럼명 공백 제거 및 표준화
    df.columns = df.columns.astype(str).str.strip()

    # 컬럼명 매핑 (영문 변환)
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

    # 3. 데이터 타입 정제
    # 문자기반 열 공백 제거 및 결측치 처리
    string_cols = ["category", "policy_name", "status", "target", "content", 
                   "scale", "start_date", "agency", "saas_idea", "needed_data", "source_url"]
    
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()

    # 날짜 정제 (YYYY-MM-DD)
    if "confirm_date" in df.columns:
        df["confirm_date"] = pd.to_datetime(df["confirm_date"], errors="coerce").dt.strftime("%Y-%m-%d")

    # 4. 결측 행(주요 필수 데이터 누락) 제거 및 인덱스 재설정
    df = df.dropna(subset=["policy_name"]).reset_index(drop=True)

    return df




# 3. 지역 특화 고령운전자 안전정책.xlsx
#          region               policy_project  ...                                         source_url                                        note
# 0    대전광역시           고령운전자 첨단안전장치 장착 지원  ...  https://tv.daejeon.go.kr/mobile/vodView.do?cco...  면허반납이 어려운 실제 운전자에게 '운전 지속+안전기술'을 지원하는 비교사례
# 1    부산광역시    고령 운수종사자 페달 오조작 방지장치 시범사업  ...          https://www.busan.go.kr/nbtnewsBU/1729826                  효과분석 결과에 따라 추가 확대 여부 검토 예정
def region_old_driver_policy_data(file_path: str = "data/제도/지역 특화 고령운전자 안전정책.xlsx") -> pd.DataFrame:
    # 1. 엑셀 불러오기 (4번째 행(인덱스 3)을 헤더로 지정)
    df = pd.read_excel(file_path, header=3)
    
    # 2. 컬럼명 공백 제거 및 표준화
    df.columns = df.columns.astype(str).str.strip()

    # 컬럼명 매핑 (영문 변환)
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

    # 3. 데이터 타입 정제
    # 문자기반 열 공백 제거 및 결측치 처리
    string_cols = [
        "region", "policy_project", "target", "scale", 
        "content", "current_stage", "saas_idea", "source_url", "note"
    ]
    
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()

    # 기준연도 수치 변환 (연도 형태 유지)
    if "base_year" in df.columns:
        df["base_year"] = pd.to_numeric(df["base_year"], errors="coerce").fillna(0).astype(int)

    # 4. 결측 행(지역명 누락) 제거 및 인덱스 재설정
    df = df.dropna(subset=["region"]).reset_index(drop=True)

    return df




# 4. 지역별 운전면허 자진반납 지원.xlsx
#            region              policy_name                           base_year  ...          saas_metric                                         source_url                                      verify_memo
# 0         서울특별시    어르신 운전면허 자진반납 교통카드 지원       2026  ...       반납률·지원예산·고령운전자 사고를 함께 비교  https://www.seoul.go.kr/news/news_report.do?nt...       사용자 원자료와 공식 2026 공고 일치
# 1         부산광역시     고령운전자 운전면허 자진반납 우대제도       2026  ...        실운전자 우대가 반납률에 미치는 영향 비교            https://www.busan.go.kr/jumin04/1717455 
def return_license_policy_data(file_path: str = "data/제도/지역별 운전면허 자진반납 지원.xlsx") -> pd.DataFrame:
    # 1. 엑셀 불러오기 (4번째 행(인덱스 3)을 헤더로 지정)
    df = pd.read_excel(file_path, header=3)
    
    # 2. 컬럼명 공백 제거 및 표준화
    df.columns = df.columns.astype(str).str.strip()

    # 컬럼명 매핑 (영문 변환)
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

    # 3. 데이터 타입 정제
    string_cols = [
        "region", "policy_name", "target_condition", "general_support",
        "active_driver_support", "support_type", "apply_method", 
        "residence_condition", "status", "saas_metric", "source_url", "verify_memo"
    ]
    
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()

    # 기준연도 수치 변환
    if "base_year" in df.columns:
        df["base_year"] = pd.to_numeric(df["base_year"], errors="coerce").fillna(0).astype(int)

    # 4. 결측 행(지역명 누락) 제거 및 인덱스 재설정
    df = df.dropna(subset=["region"]).reset_index(drop=True)

    return df


