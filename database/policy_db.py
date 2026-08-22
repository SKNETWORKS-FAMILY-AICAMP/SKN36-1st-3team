import sqlite3
import pandas as pd
import re

# 1. 도로교통공단_고령운전자 교통안전교육_교육예약정보.xlsx
def education_reservation_data(file_path: str = "data/제도/도로교통공단_고령운전자 교통안전교육_교육예약정보.xlsx") -> pd.DataFrame:
    df = pd.read_excel(file_path)
    df.columns = df.columns.astype(str).str.strip()

    df = df.rename(columns={
        "교육일자": "edu_date",
        "지부코드": "branch_name",
        "교육반코드": "course_name",
        "예약정원": "capacity"
    })

    df["edu_date"] = pd.to_datetime(df["edu_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df["branch_name"] = df["branch_name"].fillna("").astype(str).str.strip()
    df["course_name"] = df["course_name"].fillna("").astype(str).str.strip()

    df["capacity"] = (
        df["capacity"]
        .astype(str)
        .str.replace(",", "")
        .str.strip()
    )
    df["capacity"] = pd.to_numeric(df["capacity"], errors="coerce").fillna(0).astype(int)
    df = df.dropna(subset=["edu_date"]).reset_index(drop=True)

    return df

# 2. 전국 고령운전자 정책 제도.xlsx
def old_driver_policy_data(file_path: str = "data/제도/전국 고령운전자 정책 제도.xlsx") -> pd.DataFrame:
    df = pd.read_excel(file_path, header=3)
    df.columns = df.columns.astype(str).str.strip()

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

    string_cols = ["category", "policy_name", "status", "target", "content", 
                   "scale", "start_date", "agency", "saas_idea", "needed_data", "source_url"]
    
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()

    if "confirm_date" in df.columns:
        df["confirm_date"] = pd.to_datetime(df["confirm_date"], errors="coerce").dt.strftime("%Y-%m-%d")

    df = df.dropna(subset=["policy_name"]).reset_index(drop=True)
    return df

# 3. 지역 특화 고령운전자 안전정책.xlsx
def region_old_driver_policy_data(file_path: str = "data/제도/지역 특화 고령운전자 안전정책.xlsx") -> pd.DataFrame:
    df = pd.read_excel(file_path, header=3)
    df.columns = df.columns.astype(str).str.strip()

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
        "region", "policy_project", "target", "scale", 
        "content", "current_stage", "saas_idea", "source_url", "note"
    ]
    
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()

    if "base_year" in df.columns:
        df["base_year"] = pd.to_numeric(df["base_year"], errors="coerce").fillna(0).astype(int)

    df = df.dropna(subset=["region"]).reset_index(drop=True)
    return df

# 4. 지역별 운전면허 자진반납 지원.xlsx
def return_license_policy_data(file_path: str = "data/제도/지역별 운전면허 자진반납 지원.xlsx") -> pd.DataFrame:
    df = pd.read_excel(file_path, header=3)
    df.columns = df.columns.astype(str).str.strip()

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
        "region", "policy_name", "target_condition", "general_support",
        "active_driver_support", "support_type", "apply_method", 
        "residence_condition", "status", "saas_metric", "source_url", "verify_memo"
    ]
    
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()

    if "base_year" in df.columns:
        df["base_year"] = pd.to_numeric(df["base_year"], errors="coerce").fillna(0).astype(int)

    df = df.dropna(subset=["region"]).reset_index(drop=True)
    return df


# --- DB 생성 및 적재 파이프라인 (`policy_db`) ---
def build_policy_database():
    db_path = "policy_db.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🧹 기존 policy_db에 남아있는 모든 테이블을 정리합니다...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        table_name = table[0]
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        print(f"🗑️ 삭제됨: {table_name}")
    
    conn.commit()
    print("\n🚀 제도 및 정책 데이터를 'policy_db'에 적재합니다...\n")

    tasks = [
        ("education_reservation", education_reservation_data),
        ("old_driver_policy", old_driver_policy_data),
        ("region_old_driver_policy", region_old_driver_policy_data),
        ("return_license_policy", return_license_policy_data)
    ]

    for table_name, func in tasks:
        try:
            df = func()
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"✅ [성공] 테이블 생성 완료: {table_name} (총 {len(df)}행)")
        except Exception as e:
            print(f"❌ [실패] 테이블 생성 오류 ({table_name}): {e}")

    conn.close()
    print("\n🎉 policy_db 데이터베이스 구축 완료!")

if __name__ == "__main__":
    build_policy_database()