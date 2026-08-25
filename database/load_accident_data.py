import pandas as pd

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


# ============================================================
# 테이블 생성
# ============================================================

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
                accidents INT,
                deaths INT DEFAULT 0,
                injuries INT DEFAULT 0
            )
        """,

        # ====================================================
        # 수정
        # 사고건수 + 사망자수 + 부상자수
        # ====================================================

        "accident_region": """
            CREATE TABLE IF NOT EXISTS accident_region (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sido VARCHAR(50),
                sigungu VARCHAR(50),
                year INT,
                accidents INT,
                deaths INT DEFAULT 0,
                injuries INT DEFAULT 0
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


    # ========================================================
    # 기존 accident_region 테이블 컬럼 보완
    #
    # CREATE TABLE IF NOT EXISTS는 기존 테이블의 구조를
    # 변경하지 않으므로 deaths / injuries가 없는 경우 추가
    # ========================================================

    ensure_accident_region_columns(
        engine
    )

    ensure_accident_age_columns(
        engine
    )


# ============================================================
# accident_region 컬럼 자동 추가
# ============================================================

def ensure_accident_region_columns(
    engine
):

    required_columns = {

        "deaths":
            "INT DEFAULT 0",

        "injuries":
            "INT DEFAULT 0",
    }


    with engine.begin() as conn:

        # ----------------------------------------------------
        # 현재 컬럼 조회
        # ----------------------------------------------------

        result = conn.execute(
            text(
                """
                SHOW COLUMNS
                FROM accident_region
                """
            )
        )


        existing_columns = {
            row[0]
            for row
            in result.fetchall()
        }


        # ----------------------------------------------------
        # 없는 컬럼 추가
        # ----------------------------------------------------

        for column_name, column_type in (
            required_columns.items()
        ):

            if column_name not in (
                existing_columns
            ):

                conn.execute(
                    text(
                        f"""
                        ALTER TABLE
                            accident_region

                        ADD COLUMN
                            {column_name}
                            {column_type}
                        """
                    )
                )


                print(
                    f"✅ accident_region."
                    f"{column_name} 컬럼 추가 완료"
                )




# ============================================================
# accident_age 컬럼 자동 추가
# ============================================================

def ensure_accident_age_columns(
    engine
):

    required_columns = {

        "deaths":
            "INT DEFAULT 0",

        "injuries":
            "INT DEFAULT 0",
    }


    with engine.begin() as conn:

        result = conn.execute(
            text(
                """
                SHOW COLUMNS
                FROM accident_age
                """
            )
        )


        existing_columns = {
            row[0]
            for row
            in result.fetchall()
        }


        for column_name, column_type in (
            required_columns.items()
        ):

            if column_name not in (
                existing_columns
            ):

                conn.execute(
                    text(
                        f"""
                        ALTER TABLE
                            accident_age

                        ADD COLUMN
                            {column_name}
                            {column_type}
                        """
                    )
                )


                print(
                    f"✅ accident_age."
                    f"{column_name} 컬럼 추가 완료"
                )


# ============================================================
# 기존 데이터 초기화
# ============================================================

def clear_tables(
    engine
):

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

            conn.execute(
                text(
                    f"""
                    TRUNCATE TABLE
                        {table_name}
                    """
                )
            )


            print(
                f"🧹 초기화 완료: {table_name}"
            )


# ============================================================
# 데이터 적재
# ============================================================

def load_accident_data():

    engine = get_engine()


    # ========================================================
    # 1. 테이블 생성 / 구조 확인
    # ========================================================

    create_tables(
        engine
    )


    # ========================================================
    # 2. 기존 데이터 초기화
    # ========================================================

    clear_tables(
        engine
    )


    # ========================================================
    # 3. 전처리 함수 연결
    # ========================================================

    tables = {

        "driver_age_accident":
            offending_driver_age_data,

        "driver_time_accident":
            offending_driver_time_data,

        "driver_weather_accident":
            offending_driver_weather_data,

        "senior_accident_type_time":
            offending_driver_type_time_data,

        "senior_accident_month_time":
            offending_driver_month_time_data,

        "senior_accident_region_month":
            offending_driver_region_time_data,

        "accident_age":
            accident_age,

        "accident_region":
            accident_region_total,
    }


    success_count = 0

    fail_count = 0


    # ========================================================
    # 4. 테이블별 적재
    # ========================================================

    for (
        table_name,
        preprocessing_func
    ) in tables.items():

        print(
            f"\n▶ {table_name} 전처리 중..."
        )


        try:

            # ------------------------------------------------
            # 전처리
            # ------------------------------------------------

            df = preprocessing_func()


            # ------------------------------------------------
            # 빈 데이터 검사
            # ------------------------------------------------

            if df.empty:

                print(
                    f"⚠️ {table_name}: "
                    f"전처리 결과가 비어있음"
                )

                fail_count += 1

                continue


            # ------------------------------------------------
            # 전처리 결과 확인
            # ------------------------------------------------

            print(
                f"   컬럼: "
                f"{list(df.columns)}"
            )


            print(
                f"   크기: "
                f"{len(df):,}행 × "
                f"{len(df.columns)}열"
            )


            # ------------------------------------------------
            # accident_region 전용 검사
            # ------------------------------------------------

            if (
                table_name
                == "accident_region"
            ):

                required_columns = [

                    "sido",

                    "sigungu",

                    "year",

                    "accidents",

                    "deaths",

                    "injuries",
                ]


                missing_columns = [

                    column

                    for column
                    in required_columns

                    if column
                    not in df.columns
                ]


                if missing_columns:

                    raise ValueError(

                        "accident_region "
                        "전처리 결과에 필요한 컬럼이 "
                        "없습니다: "

                        f"{missing_columns}"
                    )


                # --------------------------------------------
                # 타입 보정
                # --------------------------------------------

                numeric_columns = [

                    "year",

                    "accidents",

                    "deaths",

                    "injuries",
                ]


                for column in numeric_columns:

                    df[column] = (
                        pd.to_numeric(
                            df[column],
                            errors="coerce"
                        )
                        .fillna(0)
                        .astype(int)
                    )


            # ------------------------------------------------
            # accident_age 전용 검사
            # ------------------------------------------------

            if (
                table_name
                == "accident_age"
            ):

                required_columns = [

                    "age_group",

                    "year",

                    "accidents",

                    "deaths",

                    "injuries",
                ]


                missing_columns = [

                    column

                    for column
                    in required_columns

                    if column
                    not in df.columns
                ]


                if missing_columns:

                    raise ValueError(

                        "accident_age "
                        "전처리 결과에 필요한 컬럼이 "
                        "없습니다: "

                        f"{missing_columns}"
                    )


                numeric_columns = [

                    "year",

                    "accidents",

                    "deaths",

                    "injuries",
                ]


                for column in numeric_columns:

                    df[column] = (
                        pd.to_numeric(
                            df[column],
                            errors="coerce"
                        )
                        .fillna(0)
                        .astype(int)
                    )


            # ------------------------------------------------
            # DB INSERT
            # ------------------------------------------------

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


            # ------------------------------------------------
            # accident_region 샘플 출력
            # ------------------------------------------------

            if (
                table_name
                == "accident_region"
            ):

                print(
                    "\n📊 accident_region "
                    "적재 샘플"
                )


                print(
                    df.head(
                        10
                    ).to_string(
                        index=False
                    )
                )


            # ------------------------------------------------
            # accident_age 샘플 출력
            # ------------------------------------------------

            if (
                table_name
                == "accident_age"
            ):

                print(
                    "\n📊 accident_age "
                    "적재 샘플"
                )


                print(
                    df.head(
                        10
                    ).to_string(
                        index=False
                    )
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


    # ========================================================
    # 5. 적재 결과
    # ========================================================

    print(
        "\n"
        + "=" * 60
    )


    print(
        "🚗 교통사고 데이터 적재 결과"
    )


    print(
        f"✅ 성공: {success_count}개"
    )


    print(
        f"❌ 실패: {fail_count}개"
    )


    print(
        "=" * 60
    )


# ============================================================
# 실행
# ============================================================

if __name__ == "__main__":

    load_accident_data()