from sqlalchemy import text

from database.connection import get_engine

from data_process.policy_data import (
    education_reservation_data,
    old_driver_policy_data,
    region_old_driver_policy_data,
    return_license_policy_data,
)


# ============================================================
# 1. 정책 테이블 생성
# ============================================================

def create_policy_tables(engine):

    create_sql = {

        # ----------------------------------------------------
        # 고령운전자 교통안전교육 예약
        # ----------------------------------------------------
        "education_reservation": """
            CREATE TABLE IF NOT EXISTS education_reservation (
                id INT AUTO_INCREMENT PRIMARY KEY,
                edu_date DATE,
                branch_name VARCHAR(100),
                course_name VARCHAR(100),
                capacity INT
            )
        """,

        # ----------------------------------------------------
        # 전국 고령운전자 정책
        # ----------------------------------------------------
        "old_driver_policy": """
            CREATE TABLE IF NOT EXISTS old_driver_policy (
                id INT AUTO_INCREMENT PRIMARY KEY,
                category VARCHAR(100),
                policy_name VARCHAR(255),
                status VARCHAR(100),
                target TEXT,
                content TEXT,
                scale TEXT,
                start_date VARCHAR(100),
                agency VARCHAR(255),
                saas_idea TEXT,
                needed_data TEXT,
                source_url TEXT,
                confirm_date DATE
            )
        """,

        # ----------------------------------------------------
        # 지역 특화 고령운전자 정책
        # ----------------------------------------------------
        "region_old_driver_policy": """
            CREATE TABLE IF NOT EXISTS region_old_driver_policy (
                id INT AUTO_INCREMENT PRIMARY KEY,
                region VARCHAR(100),
                policy_project VARCHAR(255),
                base_year INT,
                target TEXT,
                scale TEXT,
                content TEXT,
                current_stage VARCHAR(100),
                saas_idea TEXT,
                source_url TEXT,
                note TEXT
            )
        """,

        # ----------------------------------------------------
        # 지역별 면허 자진반납 정책
        # ----------------------------------------------------
        "return_license_policy": """
            CREATE TABLE IF NOT EXISTS return_license_policy (
                id INT AUTO_INCREMENT PRIMARY KEY,
                region VARCHAR(100),
                policy_name VARCHAR(255),
                base_year INT,
                target_condition TEXT,
                general_support TEXT,
                active_driver_support TEXT,
                support_type VARCHAR(255),
                apply_method TEXT,
                residence_condition TEXT,
                status VARCHAR(100),
                saas_metric TEXT,
                source_url TEXT,
                verify_memo TEXT
            )
        """
    }

    with engine.begin() as conn:

        for table_name, sql in create_sql.items():

            conn.execute(
                text(sql)
            )

            print(
                f"✅ 테이블 생성/확인 완료: "
                f"{table_name}"
            )


# ============================================================
# 2. 기존 데이터 삭제
# ============================================================

def clear_policy_tables(engine):

    table_names = [
        "education_reservation",
        "old_driver_policy",
        "region_old_driver_policy",
        "return_license_policy",
    ]

    with engine.begin() as conn:

        for table_name in table_names:

            conn.execute(
                text(
                    f"TRUNCATE TABLE {table_name}"
                )
            )

    print(
        "\n🧹 정책/제도 기존 데이터 초기화 완료"
    )


# ============================================================
# 3. MySQL 적재
# ============================================================

def load_policy_data():

    engine = get_engine()

    # 테이블 생성
    create_policy_tables(engine)

    # 기존 데이터 삭제
    clear_policy_tables(engine)

    tables = {

        "education_reservation":
            education_reservation_data,

        "old_driver_policy":
            old_driver_policy_data,

        "region_old_driver_policy":
            region_old_driver_policy_data,

        "return_license_policy":
            return_license_policy_data,
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
    print("📋 정책/제도 데이터 적재 결과")
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print("=" * 60)


# ============================================================
# 4. 실행
# ============================================================

if __name__ == "__main__":
    load_policy_data()