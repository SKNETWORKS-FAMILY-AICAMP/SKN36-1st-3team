from sqlalchemy import text

from database.connection import get_engine

from data_process.people_data import (
    load_local_people_data,
    load_age_population_data,
)


# ============================================================
# 테이블 생성
# ============================================================

def create_people_tables(engine):

    create_sql = {

        # 지역별 연도별 전체 인구
        "local_population": """
            CREATE TABLE IF NOT EXISTS local_population (
                id INT AUTO_INCREMENT PRIMARY KEY,
                region VARCHAR(100) NOT NULL,
                year INT NOT NULL,
                population BIGINT NOT NULL
            )
        """,

        # 지역별 연령대 / 성별 인구
        "age_population": """
            CREATE TABLE IF NOT EXISTS age_population (
                id INT AUTO_INCREMENT PRIMARY KEY,
                region VARCHAR(100) NOT NULL,
                year INT NOT NULL,
                gender VARCHAR(10) NOT NULL,
                age_group VARCHAR(30) NOT NULL,
                population BIGINT NOT NULL
            )
        """
    }

    with engine.begin() as conn:

        for table_name, sql in create_sql.items():

            conn.execute(text(sql))

            print(
                f"✅ 테이블 생성/확인 완료: {table_name}"
            )


# ============================================================
# 기존 데이터 초기화
# ============================================================

def clear_people_tables(engine):

    table_names = [
        "local_population",
        "age_population",
    ]

    with engine.begin() as conn:

        for table_name in table_names:

            conn.execute(
                text(f"TRUNCATE TABLE {table_name}")
            )

    print("\n🧹 인구 관련 기존 데이터 초기화 완료")


# ============================================================
# 데이터 적재
# ============================================================

def load_people_data():

    engine = get_engine()

    # 테이블 생성
    create_people_tables(engine)

    # 기존 데이터 초기화
    clear_people_tables(engine)

    # 테이블 ↔ 전처리 함수
    tables = {

        "local_population":
            load_local_people_data,

        "age_population":
            load_age_population_data,
    }

    success_count = 0
    fail_count = 0

    for table_name, preprocessing_func in tables.items():

        print(
            f"\n▶ {table_name} 전처리 중..."
        )

        try:

            # 전처리
            df = preprocessing_func()

            # 빈 데이터 확인
            if df.empty:

                print(
                    f"⚠️ {table_name}: 전처리 결과가 비어있음"
                )

                fail_count += 1
                continue

            # 컬럼 확인
            print(
                f"   컬럼: {list(df.columns)}"
            )

            # 데이터 미리보기
            print(df.head())

            # DB 적재
            df.to_sql(
                name=table_name,
                con=engine,
                if_exists="append",
                index=False,
                chunksize=1000,
            )

            print(
                f"✅ {table_name} 적재 완료 "
                f"({len(df):,}행 × {len(df.columns)}열)"
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

    # 결과
    print("\n" + "=" * 60)
    print("👥 인구 데이터 적재 결과")
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print("=" * 60)


if __name__ == "__main__":
    load_people_data()