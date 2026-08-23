from sqlalchemy import text

from database.connection import get_engine

from data_process.car_data import (
    license_holder_gender_data,
    license_holder_age_data,
    license_holder_region_data,
    return_driver_license_2023_data,
    return_driver_license_2025,
    driver_license_region_data,
    car_registration_data,
    car_registration_region_data,
)


# =========================================================
# 1. MySQL 테이블 생성
# =========================================================
def create_car_tables(engine):

    create_sql = {

        # 1. 운전면허 소지자 - 성별
        "license_holder_gender": """
            CREATE TABLE IF NOT EXISTS license_holder_gender (
                id INT AUTO_INCREMENT PRIMARY KEY,
                license_main VARCHAR(50),
                license_sub VARCHAR(100),
                year INT,
                gender VARCHAR(20),
                count BIGINT
            )
        """,

        # 2. 운전면허 소지자 - 연령별
        "license_holder_age": """
            CREATE TABLE IF NOT EXISTS license_holder_age (
                id INT AUTO_INCREMENT PRIMARY KEY,
                age INT,
                year INT,
                license_main VARCHAR(50),
                license_sub VARCHAR(100),
                count BIGINT
            )
        """,

        # 3. 운전면허 소지자 - 지역별
        "license_holder_region": """
            CREATE TABLE IF NOT EXISTS license_holder_region (
                id INT AUTO_INCREMENT PRIMARY KEY,
                region VARCHAR(100),
                year INT,
                license_main VARCHAR(50),
                license_sub VARCHAR(100),
                count BIGINT
            )
        """,

        # 4. 운전면허 자진반납 - 2023
        "return_driver_license_2023": """
            CREATE TABLE IF NOT EXISTS return_driver_license_2023 (
                id INT AUTO_INCREMENT PRIMARY KEY,
                region VARCHAR(100),
                age INT,
                age_label VARCHAR(50),
                count BIGINT
            )
        """,

        # 5. 운전면허 자진반납 - 2025
        "return_driver_license_2025": """
            CREATE TABLE IF NOT EXISTS return_driver_license_2025 (
                id INT AUTO_INCREMENT PRIMARY KEY,
                region VARCHAR(100),
                age INT,
                age_label VARCHAR(50),
                count BIGINT
            )
        """,

        # 6. 경찰청 운전면허 지역/성별/종별
        "driver_license_region": """
            CREATE TABLE IF NOT EXISTS driver_license_region (
                id INT AUTO_INCREMENT PRIMARY KEY,
                region VARCHAR(100),
                gender VARCHAR(20),
                license_type VARCHAR(100),
                count BIGINT
            )
        """,

        # 7. 자동차 등록 - 연도별
        "car_registration_year": """
            CREATE TABLE IF NOT EXISTS car_registration_year (
                id INT AUTO_INCREMENT PRIMARY KEY,
                year INT,
                vehicle_type VARCHAR(50),
                vehicle_usage VARCHAR(50),
                count BIGINT
            )
        """,

        # 8. 자동차 등록 - 지역/월별
        "car_registration_region": """
            CREATE TABLE IF NOT EXISTS car_registration_region (
                id INT AUTO_INCREMENT PRIMARY KEY,
                month VARCHAR(20),
                sido VARCHAR(50),
                sigungu VARCHAR(100),
                vehicle_type VARCHAR(50),
                vehicle_usage VARCHAR(50),
                count BIGINT
            )
        """
    }

    with engine.begin() as conn:
        for table_name, sql in create_sql.items():
            conn.execute(text(sql))
            print(f"✅ 테이블 생성/확인 완료: {table_name}")


# =========================================================
# 2. 기존 데이터 초기화
# =========================================================
def clear_car_tables(engine):

    table_names = [
        "license_holder_gender",
        "license_holder_age",
        "license_holder_region",
        "return_driver_license_2023",
        "return_driver_license_2025",
        "driver_license_region",
        "car_registration_year",
        "car_registration_region",
    ]

    with engine.begin() as conn:
        for table_name in table_names:
            conn.execute(text(f"TRUNCATE TABLE {table_name}"))

    print("\n🧹 자동차 관련 기존 데이터 초기화 완료")


# =========================================================
# 3. 자동차 데이터 적재
# =========================================================
def load_car_data():

    engine = get_engine()

    # 테이블 먼저 생성
    create_car_tables(engine)

    # 기존 데이터 비우기
    clear_car_tables(engine)

    tables = {
        "license_holder_gender": license_holder_gender_data,
        "license_holder_age": license_holder_age_data,
        "license_holder_region": license_holder_region_data,
        "return_driver_license_2023": return_driver_license_2023_data,
        "return_driver_license_2025": return_driver_license_2025,
        "driver_license_region": driver_license_region_data,
        "car_registration_year": car_registration_data,
        "car_registration_region": car_registration_region_data,
    }

    success_count = 0
    fail_count = 0

    for table_name, preprocessing_func in tables.items():

        print(f"\n▶ {table_name} 전처리 중...")

        try:
            # 전처리 함수 실행
            df = preprocessing_func()

            # 빈 DataFrame 체크
            if df.empty:
                print(f"⚠️ {table_name}: 전처리 결과가 비어있음")
                fail_count += 1
                continue

            # 컬럼 확인용
            print(f"   컬럼: {list(df.columns)}")

            # MySQL 적재
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
            print(f"❌ {table_name} 적재 실패")
            print(f"   오류: {e}")

            fail_count += 1

    print("\n" + "=" * 60)
    print("🚗 자동차 데이터 적재 결과")
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print("=" * 60)


# =========================================================
# 4. 실행
# =========================================================
if __name__ == "__main__":
    load_car_data()