import sqlite3
import pandas as pd
import re

# 고령운전자 및 교통안전 관련 FAQ 전처리 함수
def traffic_faq_data(file_path: str = "data/FAQ/고령운전자 및 교통안전 관련 FAQ.xlsx") -> pd.DataFrame:
    # 1. 파일 확장자에 따라 헤더 없이 읽어오기
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path, encoding="cp949", header=None)
    else:
        df = pd.read_excel(file_path, header=None)
    
    # 2. 실제 데이터가 시작하는 행(인덱스 2부터 끝까지)을 추출하고 필요한 5개 열 선택
    faq_df = df.iloc[2:, [0, 1, 2, 3, 4]].copy()
    
    # 3. 컬럼명 재정의
    faq_df.columns = ["no", "category", "question", "answer", "source_url"]
    
    # 4. 문자열 공백 제거 및 결측치(NaN) 제거
    string_cols = ["category", "question", "answer", "source_url"]
    for col in string_cols:
        faq_df[col] = (
            faq_df[col]
            .astype(str)
            .str.strip()
            .replace({"nan": "", "None": "", "nat": ""})
        )
    
    # 5. 질문 번호(no)를 정수형으로 변환 (숫자가 아닌 경우 필터링)
    faq_df["no"] = pd.to_numeric(faq_df["no"], errors="coerce")
    faq_df = faq_df.dropna(subset=["no"]).copy()
    faq_df["no"] = faq_df["no"].astype(int)
    
    return faq_df.reset_index(drop=True)

# --- DB 생성 및 적재 파이프라인 (`faq_db`) ---
def build_faq_database():
    db_path = "faq_db.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🧹 기존 faq_db에 남아있는 모든 테이블을 정리합니다...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        table_name = table[0]
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        print(f"🗑️ 삭제됨: {table_name}")
    
    conn.commit()
    print("\n🚀 FAQ 데이터를 'faq_db'에 적재합니다...\n")

    table_name = "traffic_faq"
    try:
        df = traffic_faq_data()
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"✅ [성공] 테이블 생성 완료: {table_name} (총 {len(df)}행)")
    except Exception as e:
        print(f"❌ [실패] 테이블 생성 오류 ({table_name}): {e}")

    conn.close()
    print("\n🎉 faq_db 데이터베이스 구축 완료!")

if __name__ == "__main__":
    build_faq_database()