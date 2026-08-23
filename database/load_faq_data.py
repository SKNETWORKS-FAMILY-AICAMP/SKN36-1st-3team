from sqlalchemy import text

from database.connection import get_engine
from data_process.faq_data import traffic_faq_data


# ============================================================
# FAQ 테이블 생성
# ============================================================

def create_faq_table(engine):

    sql = """
        CREATE TABLE IF NOT EXISTS traffic_faq (
            id INT AUTO_INCREMENT PRIMARY KEY,
            no INT NOT NULL,
            category VARCHAR(100) NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            source_url TEXT
        )
    """

    with engine.begin() as conn:
        conn.execute(text(sql))

    print("✅ 테이블 생성/확인 완료: traffic_faq")


# ============================================================
# 기존 데이터 초기화
# ============================================================

def clear_faq_table(engine):

    with engine.begin() as conn:
        conn.execute(
            text("TRUNCATE TABLE traffic_faq")
        )

    print("🧹 FAQ 기존 데이터 초기화 완료")


# ============================================================
# FAQ 데이터 적재
# ============================================================

def load_faq_data():

    engine = get_engine()

    create_faq_table(engine)
    clear_faq_table(engine)

    print("\n▶ traffic_faq 전처리 중...")

    try:
        df = traffic_faq_data()

        if df.empty:
            print("⚠️ FAQ 전처리 결과가 비어있음")
            return

        print(f"   컬럼: {list(df.columns)}")

        df.to_sql(
            name="traffic_faq",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=1000,
        )

        print(
            f"✅ traffic_faq 적재 완료 "
            f"({len(df):,}행 × {len(df.columns)}열)"
        )

    except Exception as e:
        print("❌ traffic_faq 적재 실패")
        print(f"   오류: {e}")
        return

    print("\n" + "=" * 60)
    print("💬 FAQ 데이터 적재 완료")
    print("=" * 60)


if __name__ == "__main__":
    load_faq_data()