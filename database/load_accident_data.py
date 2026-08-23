from sqlalchemy import text

from database.connection import get_engine
from data_process.accident_data import (
    offending_driver_age_data,
    offending_driver_time_data,
    offending_driver_weather_data,
    offending_driver_type_time_data,
    offending_driver_month_time_data,
    offending_driver_region_time_data,
    accident_age,
    accident_region_total,
)


def create_tables(engine):
    create_sql = {
        "driver_age_accident": """
            CREATE TABLE IF NOT EXISTS driver_age_accident (
                id INT AUTO_INCREMENT PRIMARY KEY,
                age_group VARCHAR(50),
                accident_2021 INT,
                accident_2022 INT,
                accident_2023 INT,
                accident_2024 INT,
                accident_2025 INT
            )
        """,

        "driver_time_accident": """
            CREATE TABLE IF NOT EXISTS driver_time_accident (
                id INT AUTO_INCREMENT PRIMARY KEY,
                age_group VARCHAR(50),
                time_00_02 INT,
                time_02_04 INT,
                time_04_06 INT,
                time_06_08 INT,
                time_08_10 INT,
                time_10_12 INT,
                time_12_14 INT,
                time_14_16 INT,
                time_16_18 INT,
                time_18_20 INT,
                time_20_22 INT,
                time_22_24 INT
            )
        """,

        "driver_weather_accident": """
            CREATE TABLE IF NOT EXISTS driver_weather_accident (
                id INT AUTO_INCREMENT PRIMARY KEY,
                age_group VARCHAR(50),
                year INT,
                weather VARCHAR(50),
                accidents INT
            )
        """,

        "senior_accident_type_time": """
            CREATE TABLE IF NOT EXISTS senior_accident_type_time (
                id INT AUTO_INCREMENT PRIMARY KEY,
                accident_type_main VARCHAR(100),
                accident_type_middle VARCHAR(100),
                accident_type_sub VARCHAR(100),
                year INT,
                time_slot VARCHAR(50),
                accidents INT
            )
        """,

        "senior_accident_month_time": """
            CREATE TABLE IF NOT EXISTS senior_accident_month_time (
                id INT AUTO_INCREMENT PRIMARY KEY,
                year INT,
                month INT,
                time_slot VARCHAR(50),
                accidents INT
            )
        """,

        "senior_accident_region_month": """
            CREATE TABLE IF NOT EXISTS senior_accident_region_month (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sido VARCHAR(50),
                sigungu VARCHAR(50),
                year INT,
                month INT,
                accidents INT
            )
        """,

        "accident_age": """
            CREATE TABLE IF NOT EXISTS accident_age (
                id INT AUTO_INCREMENT PRIMARY KEY,
                age_group VARCHAR(50),
                year INT,
                accidents INT
            )
        """,

        "accident_region": """
            CREATE TABLE IF NOT EXISTS accident_region (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sido VARCHAR(50),
                sigungu VARCHAR(50),
                year INT,
                accidents INT
            )
        """
    }

    with engine.begin() as conn:
        for table_name, sql in create_sql.items():
            conn.execute(text(sql))
            print(f"✅ 테이블 생성/확인 완료: {table_name}")


def clear_tables(engine):
    table_names = [
        "driver_age_accident",
        "driver_time_accident",
        "driver_weather_accident",
        "senior_accident_type_time",
        "senior_accident_month_time",
        "senior_accident_region_month",
        "accident_age",
        "accident_region",
    ]

    with engine.begin() as conn:
        for table_name in table_names:
            conn.execute(text(f"TRUNCATE TABLE {table_name}"))


def load_accident_data():
    engine = get_engine()

    create_tables(engine)
    clear_tables(engine)

    tables = {
        "driver_age_accident": offending_driver_age_data,
        "driver_time_accident": offending_driver_time_data,
        "driver_weather_accident": offending_driver_weather_data,
        "senior_accident_type_time": offending_driver_type_time_data,
        "senior_accident_month_time": offending_driver_month_time_data,
        "senior_accident_region_month": offending_driver_region_time_data,
        "accident_age": accident_age,
        "accident_region": accident_region_total,
    }

    for table_name, preprocessing_func in tables.items():
        print(f"\n▶ {table_name} 전처리 중...")

        try:
            df = preprocessing_func()

            if df.empty:
                print(f"⚠️ {table_name}: 전처리 결과가 비어있음")
                continue

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

        except Exception as e:
            print(f"❌ {table_name} 적재 실패")
            print(f"   오류: {e}")


if __name__ == "__main__":
    load_accident_data()