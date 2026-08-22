import sqlite3
import pandas as pd

# 1. e-나라지표 지역별 인구 데이터 전처리 함수 (수정됨)
def load_local_people_data(file_path: str = "data/인구/e-나라지표_지역별 인구.xlsx") -> pd.DataFrame:
    """e-나라지표 지역별 인구 엑셀 데이터를 정제하여 데이터프레임으로 반환합니다."""
    
    # 엑셀 데이터 로드 및 필요한 열 추출
    df = pd.read_excel(file_path, header=None)
    local_people = df.iloc[4:, [0, 1, 3, 5, 7, 9]].copy()
    
    # 컬럼명 변경
    local_people.columns = [
        "region",
        "population_2021",
        "population_2022",
        "population_2023",
        "population_2024",
        "population_2025"
    ]
    
    # "계" 제외 및 주석/결측치 행 제거 (지역명에 특정 문구가 들어가거나 숫자가 아닌 행 필터링)
    local_people = local_people[local_people["region"].notna()].copy()
    local_people["region"] = local_people["region"].astype(str).str.strip()
    
    # "계"이거나 설명글("국가데이터처" 등)이 포함된 행 제거
    local_people = local_people[
        (local_people["region"] != "계") & 
        (~local_people["region"].str.contains("국가데이터처|출처|주:", na=False))
    ].copy()
    
    # 정수형 변환 (변환할 수 없는 값은 NaN으로 바꾼 뒤 0 또는 적절히 처리하거나 에러 방지)
    population_cols = [f"population_{year}" for year in range(2021, 2026)]
    for col in population_cols:
        local_people[col] = (
            local_people[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
        )
        # 숫자로 변환 가능한 것만 변환하고, 불가능한 경우(주석 등)는 처리
        local_people[col] = pd.to_numeric(local_people[col], errors='coerce').fillna(0).astype(int)
        
    return local_people.reset_index(drop=True)

# 2. 행정안전부 주민등록인구 CSV 데이터 전처리 함수
def resident_regristration_data(file_path: str = "data/인구/행정안전부_주민등록인구및세대현황_월간.csv") -> pd.DataFrame:
    """행정안전부 주민등록인구 및 세대현황 CSV 데이터를 정제하여 데이터프레임으로 반환합니다."""
    
    df = pd.read_csv(file_path, encoding="cp949")
    
    # 1. 행정구역 및 '총인구수'가 포함된 열만 추출
    target_cols = [df.columns[0]] + [col for col in df.columns if "총인구수" in col]
    resident_people = df[target_cols].copy()
    
    # 2. 첫 컬럼명 변경
    resident_people.rename(columns={df.columns[0]: "region"}, inplace=True)
    
    # 3. 쉼표(,) 제거 및 정수형 변환
    pop_cols = [col for col in resident_people.columns if col != "region"]
    for col in pop_cols:
        resident_people[col] = (
            resident_people[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
        )
        resident_people[col] = pd.to_numeric(resident_people[col], errors='coerce').fillna(0).astype(int)
        
    return resident_people.reset_index(drop=True)

# --- DB 생성 및 적재 파이프라인 (`people_db`) ---
def build_people_database():
    db_path = "people_db.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🧹 기존 people_db에 남아있는 모든 테이블을 정리합니다...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        table_name = table[0]
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        print(f"🗑️ 삭제됨: {table_name}")
    
    conn.commit()
    print("\n🚀 인구 데이터를 'people_db'에 적재합니다...\n")

    tasks = [
        ("local_population", load_local_people_data),
        ("resident_population", resident_regristration_data)
    ]

    for table_name, func in tasks:
        try:
            df = func()
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"✅ [성공] 테이블 생성 완료: {table_name} (총 {len(df)}행)")
        except Exception as e:
            print(f"❌ [실패] 테이블 생성 오류 ({table_name}): {e}")

    conn.close()
    print("\n🎉 people_db 데이터베이스 구축 완료!")

if __name__ == "__main__":
    build_people_database()