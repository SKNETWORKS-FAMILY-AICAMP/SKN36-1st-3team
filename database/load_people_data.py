from sqlalchemy import text

from database.connection import get_engine

from data_process.people_data import (
    load_local_people_data,
    resident_regristration_data,
)


# ============================================================
# 테이블 생성
# ============================================================

def create_people_tables(engine):

    create_sql = {

        "local_population": """
            CREATE TABLE IF NOT EXISTS local_population (
                id INT AUTO_INCREMENT PRIMARY KEY,
                region VARCHAR(100) NOT NULL,
                year INT NOT NULL,
                population BIGINT NOT NULL
            )
        """,

        "resident_population_monthly": """
            CREATE TABLE IF NOT EXISTS resident_population_monthly (
                id INT AUTO_INCREMENT PRIMARY KEY,
                month VARCHAR(7) NOT NULL,
                region VARCHAR(150) NOT NULL,
                population BIGINT NOT NULL
            )
        """
    }

    with engine.begin() as conn:

        for table_name, sql in create_sql.items():

            conn.execute(
                text(sql)
            )

            print(
                f"✅ 테이블 생성/확인 완료: {table_name}"
            )


# ============================================================
# 기존 데이터 초기화
# ============================================================

def clear_people_tables(engine):

    table_names = [
        "local_population",
        "resident_population_monthly",
    ]

    with engine.begin() as conn:

        for table_name in table_names:

            conn.execute(
                text(
                    f"TRUNCATE TABLE {table_name}"
                )
            )

    print(
        "\n🧹 인구 관련 기존 데이터 초기화 완료"
    )


# ============================================================
# 데이터 적재
# ============================================================

def load_people_data():

    engine = get_engine()

    create_people_tables(engine)
    clear_people_tables(engine)

    tables = {

        "local_population":
            load_local_people_data,

        "resident_population_monthly":
            resident_regristration_data,
    }

    success_count = 0
    fail_count = 0

    for table_name, preprocessing_func in tables.items():

        print(
            f"\n▶ {table_name} 전처리 중..."
        )

        try:

            df = preprocessing_func()

            if df.empty:

                print(
                    f"⚠️ {table_name}: "
                    f"전처리 결과가 비어있음"
                )

                fail_count += 1
                continue

            print(
                f"   컬럼: {list(df.columns)}"
            )

            df.to_sql(
                name=table_name,
                con=engine,
                if_exists="append",
                index=False,
                chunksize=1000,
            )

            print(
                f"✅ {table_name} 적재 완료 "
                f"({len(df):,}행 × "
                f"{len(df.columns)}열)"
            )

            success_count += 1

        except Exception as e:

            print(
                f"❌ {table_name} 적재 실패"
            )

            print(
                f"   오류: {e}"
            )

            fail_count += 1

    print("\n" + "=" * 60)
    print("👥 인구 데이터 적재 결과")
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print("=" * 60)


if __name__ == "__main__":
    load_people_data()