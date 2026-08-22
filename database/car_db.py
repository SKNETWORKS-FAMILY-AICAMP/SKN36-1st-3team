import sqlite3
import pandas as pd
import re

# 1. KOSIS_운전면허소지자현황_성별.csv
def license_holder_gender_data(file_path: str = "data/자동차/KOSIS_운전면허소지자현황_성별.csv") -> pd.DataFrame:
    df = pd.read_csv(file_path, encoding="cp949", header=None)
    years = df.iloc[0].ffill()
    genders = df.iloc[1]
    data_df = df.iloc[2:].copy()
    
    data_df.iloc[:, 0] = data_df.iloc[:, 0].replace("", None).ffill().fillna("").astype(str).str.strip()
    data_df.iloc[:, 1] = data_df.iloc[:, 1].fillna("").astype(str).str.strip()
    
    valid_df = data_df[
        (~data_df.iloc[:, 0].isin(["총계", "면허종별(1)", "면허종별(2)", "", "nan", "None"])) &
        (~data_df.iloc[:, 1].isin(["소계", "총계", "", "nan", "None"]))
    ].copy()
    
    records = []
    for _, row in valid_df.iterrows():
        license_type_main = row.iloc[0]
        license_type_sub = row.iloc[1]
        
        for col_idx in range(2, len(df.columns)):
            year_val = str(years.iloc[col_idx]).strip()
            gender_val = str(genders.iloc[col_idx]).strip()
            year_match = re.search(r'(\d{4})', year_val)
            
            if year_match and gender_val in ["남자", "여자"]:
                year_num = int(year_match.group(1))
                val = str(row.iloc[col_idx]).replace(",", "").strip()
                if val in ["-", "", "nan", "None"]:
                    count = 0
                else:
                    try:
                        count = int(float(val))
                    except (ValueError, TypeError):
                        count = 0
                        
                records.append({
                    "license_main": license_type_main,
                    "license_sub": license_type_sub,
                    "year": year_num,
                    "gender": gender_val,
                    "count": count
                })
    return pd.DataFrame(records).reset_index(drop=True)

# 2. KOSIS_운전면허소지자현황_연령대별.csv
def license_holder_age_data(file_path: str = "data/자동차/KOSIS_운전면허소지자현황_연령대별.csv") -> pd.DataFrame:
    df = None
    for enc in ["utf-8-sig", "cp949", "utf-8", "euc-kr"]:
        try:
            df = pd.read_csv(file_path, encoding=enc, header=None)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
            
    if df is None:
        raise ValueError("파일을 읽을 수 없습니다. 파일 경로 및 인코딩을 확인해주세요.")

    years = df.iloc[0].ffill()
    mains = df.iloc[1].fillna("").astype(str).str.strip()
    subs = df.iloc[2].fillna("").astype(str).str.strip()
    
    data_df = df.iloc[3:].copy()
    data_df.iloc[:, 0] = data_df.iloc[:, 0].fillna("").astype(str).str.strip()
    
    valid_df = data_df[
        ~data_df.iloc[:, 0].isin(["계", "총계", "연령대별(1)", "연령별", "", "nan", "None"])
    ].copy()
    
    records = []
    for _, row in valid_df.iterrows():
        age_raw = row.iloc[0]
        age_match = re.search(r'(\d+)', age_raw)
        if not age_match:
            continue
        age_num = int(age_match.group(1))
        
        for col_idx in range(1, len(df.columns)):
            year_val = str(years.iloc[col_idx]).strip()
            main_val = str(mains.iloc[col_idx]).strip()
            sub_val = str(subs.iloc[col_idx]).strip()
            year_match = re.search(r'(\d{4})', year_val)
            
            if year_match and sub_val not in ["소계", "총계", ""] and main_val not in ["총계", "계", ""]:
                year_num = int(year_match.group(1))
                val = str(row.iloc[col_idx]).replace(",", "").strip()
                if val in ["-", "", "nan", "None"]:
                    count = 0
                else:
                    try:
                        count = int(float(val))
                    except (ValueError, TypeError):
                        count = 0
                        
                records.append({
                    "age": age_num,
                    "year": year_num,
                    "license_main": main_val,
                    "license_sub": sub_val,
                    "count": count
                })
    return pd.DataFrame(records).reset_index(drop=True)

# 3. KOSIS_운전면허소지자현황_지역별.csv
def license_holder_region_data(file_path: str = "data/자동차/KOSIS_운전면허소지자현황_지역별.csv") -> pd.DataFrame:
    df = None
    for enc in ["utf-8-sig", "cp949", "utf-8", "euc-kr"]:
        try:
            df = pd.read_csv(file_path, encoding=enc, header=None)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
            
    if df is None:
        raise ValueError("파일을 읽을 수 없습니다. 파일 경로 및 인코딩을 확인해주세요.")

    years = df.iloc[0].ffill()
    mains = df.iloc[1].fillna("").astype(str).str.strip()
    subs = df.iloc[2].fillna("").astype(str).str.strip()
    
    data_df = df.iloc[3:].copy()
    data_df.iloc[:, 0] = data_df.iloc[:, 0].fillna("").astype(str).str.strip()
    
    valid_df = data_df[
        ~data_df.iloc[:, 0].isin(["계", "총계", "지역별(1)", "시도", "", "nan", "None"])
    ].copy()
    
    records = []
    for _, row in valid_df.iterrows():
        region_name = row.iloc[0]
        for col_idx in range(1, len(df.columns)):
            year_val = str(years.iloc[col_idx]).strip()
            main_val = str(mains.iloc[col_idx]).strip()
            sub_val = str(subs.iloc[col_idx]).strip()
            year_match = re.search(r'(\d{4})', year_val)
            
            if year_match and sub_val not in ["소계", "총계", ""] and main_val not in ["총계", "계", ""]:
                year_num = int(year_match.group(1))
                val = str(row.iloc[col_idx]).replace(",", "").strip()
                if val in ["-", "", "nan", "None"]:
                    count = 0
                else:
                    try:
                        count = int(float(val))
                    except (ValueError, TypeError):
                        count = 0
                        
                records.append({
                    "region": region_name,
                    "year": year_num,
                    "license_main": main_val,
                    "license_sub": sub_val,
                    "count": count
                })
    return pd.DataFrame(records).reset_index(drop=True)

# 4. 경찰청_운전면허 자진반납 연령별 시도청별 취소처분현황_2023년도.csv
def return_driver_license_2023_data(file_path: str = "data/자동차/경찰청_운전면허 자진반납 연령별 시도청별 취소처분현황_2023년도.csv") -> pd.DataFrame:
    df = None
    for enc in ["utf-8-sig", "cp949", "utf-8", "euc-kr"]:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
            
    if df is None:
        raise ValueError("파일을 읽을 수 없습니다. 파일 경로 및 인코딩을 확인해주세요.")

    df.rename(columns={df.columns[0]: "region"}, inplace=True)
    df["region"] = df["region"].fillna("").astype(str).str.strip()
    
    valid_df = df[
        ~df["region"].isin(["계", "총계", "합계", "지역", "지역별", "", "nan", "None"])
    ].copy()

    records = []
    for _, row in valid_df.iterrows():
        region_name = row["region"]
        for col_name in valid_df.columns[1:]:
            col_str = str(col_name).strip()
            val_str = str(row[col_name]).replace(",", "").strip()
            if val_str in ["-", "", "nan", "None"]:
                count = 0
            else:
                try:
                    count = int(float(val_str))
                except (ValueError, TypeError):
                    count = 0

            if "미만" in col_str:
                age_num = 64
            else:
                age_match = re.search(r'(\d+)', col_str)
                if age_match:
                    age_num = int(age_match.group(1))
                else:
                    continue

            records.append({
                "region": region_name,
                "age": age_num,
                "age_label": col_str,
                "count": count
            })
    return pd.DataFrame(records).reset_index(drop=True)

# 5. 경찰청_운전면허 자진반납 연령별 시도청별 취소처분현황_2025년도.csv
def return_driver_license_2025(file_path: str = "data/자동차/경찰청_운전면허 자진반납 연령별 시도청별 취소처분현황_2025년도.csv") -> pd.DataFrame:
    df = None
    for enc in ["utf-8-sig", "cp949", "utf-8", "euc-kr"]:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
            
    if df is None:
        raise ValueError("파일을 읽을 수 없습니다. 파일 경로 및 인코딩을 확인해주세요.")

    df.rename(columns={df.columns[0]: "region"}, inplace=True)
    df["region"] = df["region"].fillna("").astype(str).str.strip()
    
    valid_df = df[
        ~df["region"].isin(["계", "총계", "합계", "지역", "지역별", "", "nan", "None"])
    ].copy()

    records = []
    for _, row in valid_df.iterrows():
        region_name = row["region"]
        for col_name in valid_df.columns[1:]:
            col_str = str(col_name).strip()
            val_str = str(row[col_name]).replace(",", "").strip()
            if val_str in ["-", "", "nan", "None"]:
                count = 0
            else:
                try:
                    count = int(float(val_str))
                except (ValueError, TypeError):
                    count = 0

            if "미만" in col_str:
                age_num = 64
            else:
                age_match = re.search(r'(\d+)', col_str)
                if age_match:
                    age_num = int(age_match.group(1))
                else:
                    continue

            records.append({
                "region": region_name,
                "age": age_num,
                "age_label": col_str,
                "count": count
            })
    return pd.DataFrame(records).reset_index(drop=True)

# 6. 경찰청_운전면허소지자 지역별 종별 현황_20251231.csv
def driver_license_region_data(file_path: str = "data/자동차/경찰청_운전면허소지자 지역별 종별 현황_20251231.csv") -> pd.DataFrame:
    df = None
    for enc in ["utf-8-sig", "cp949", "utf-8", "euc-kr"]:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
            
    if df is None:
        raise ValueError("파일을 읽을 수 없습니다. 파일 경로 및 인코딩을 확인해주세요.")

    df.rename(columns={df.columns[0]: "region", df.columns[1]: "gender"}, inplace=True)
    df["region"] = df["region"].fillna("").astype(str).str.strip()
    df["gender"] = df["gender"].fillna("").astype(str).str.strip()
    
    valid_df = df[
        (~df["region"].isin(["계", "총계", "합계", "지역별", "", "nan", "None"])) &
        (df["gender"].isin(["남", "여", "남자", "여자"]))
    ].copy()

    records = []
    for _, row in valid_df.iterrows():
        region_val = row["region"]
        gender_val = row["gender"]

        for col_name in valid_df.columns[2:]:
            license_type = str(col_name).strip()
            val_str = str(row[col_name]).replace(",", "").strip()
            if val_str in ["-", "", "nan", "None"]:
                count = 0
            else:
                try:
                    count = int(float(val_str))
                except (ValueError, TypeError):
                    count = 0

            records.append({
                "region": region_val,
                "gender": gender_val,
                "license_type": license_type,
                "count": count
            })
    return pd.DataFrame(records).reset_index(drop=True)

# 7. 국토교통통계누리_자동차등록현황보고_연도별.csv
def car_registration_data(file_path: str = "data/자동차/국토교통통계누리_자동차등록현황보고_연도별.csv") -> pd.DataFrame:
    df = None
    for enc in ["utf-8-sig", "cp949", "utf-8", "euc-kr"]:
        try:
            df = pd.read_csv(
                file_path, encoding=enc, header=None, names=range(100), engine='python'
            )
            df = df.dropna(how='all', axis=1)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
            
    if df is None:
        raise ValueError("파일을 읽을 수 없습니다. 파일 경로 및 인코딩을 확인해주세요.")

    vehicle_types = df.iloc[0].ffill()
    usages = df.iloc[1].fillna("").astype(str).str.strip()
    data_df = df.iloc[2:].copy()
    
    records = []
    for _, row in data_df.iterrows():
        year_raw = str(row.iloc[0]).strip()
        year_match = re.search(r'(\d{4})', year_raw)
        if not year_match:
            continue
        year_num = int(year_match.group(1))

        for col_idx in range(1, len(df.columns)):
            v_type = str(vehicle_types.iloc[col_idx]).strip()
            usage_val = str(usages.iloc[col_idx]).strip()

            if usage_val not in ["계", "총계", ""] and v_type not in ["총계", "계", "nan", "None", ""]:
                val_str = str(row.iloc[col_idx]).replace(",", "").strip()
                if val_str in ["-", "", "nan", "None"]:
                    count = 0
                else:
                    try:
                        count = int(float(val_str))
                    except (ValueError, TypeError):
                        count = 0

                records.append({
                    "year": year_num,
                    "vehicle_type": v_type,
                    "usage": usage_val,
                    "count": count
                })
    return pd.DataFrame(records).reset_index(drop=True)

# 8. 국토교통통계누리_자동차증록현황보고.csv
def car_registration_region_data(file_path: str = "data/자동차/국토교통통계누리_자동차증록현황보고.csv") -> pd.DataFrame:
    df = None
    for enc in ["utf-8-sig", "cp949", "utf-8", "euc-kr"]:
        try:
            df = pd.read_csv(
                file_path, encoding=enc, header=None, names=range(100), engine='python'
            )
            df = df.dropna(how='all', axis=1)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
            
    if df is None:
        raise ValueError("파일을 읽을 수 없습니다. 파일 경로 및 인코딩을 확인해주세요.")

    vehicle_types = df.iloc[0].ffill()
    usages = df.iloc[1].fillna("").astype(str).str.strip()
    data_df = df.iloc[2:].copy()
    records = []

    for _, row in data_df.iterrows():
        month_val = str(row.iloc[0]).strip()
        sido_val = str(row.iloc[1]).strip()
        sigungu_val = str(row.iloc[2]).strip()

        for col_idx in range(3, len(df.columns)):
            v_type = str(vehicle_types.iloc[col_idx]).strip()
            usage_val = str(usages.iloc[col_idx]).strip()

            if usage_val not in ["계", "총계", ""] and v_type not in ["총계", "계", "nan", "None", ""]:
                val_str = str(row.iloc[col_idx]).replace(",", "").strip()
                if val_str in ["-", "", "nan", "None"]:
                    count = 0
                else:
                    try:
                        count = int(float(val_str))
                    except (ValueError, TypeError):
                        count = 0

                records.append({
                    "month": month_val,
                    "sido": sido_val,
                    "sigungu": sigungu_val,
                    "vehicle_type": v_type,
                    "usage": usage_val,
                    "count": count
                })
    return pd.DataFrame(records).reset_index(drop=True)


# --- DB 생성 및 적재 파이프라인 (`car_db`) ---
def build_car_database():
    db_path = "car_db.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🧹 기존 car_db에 남아있는 모든 테이블을 정리합니다...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        table_name = table[0]
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        print(f"🗑️ 삭제됨: {table_name}")
    
    conn.commit()
    print("\n🚀 자동차 및 운전면허 전처리 데이터를 'car_db'에 적재합니다...\n")

    tasks = [
        ("license_holder_gender", license_holder_gender_data),
        ("license_holder_age", license_holder_age_data),
        ("license_holder_region", license_holder_region_data),
        ("return_driver_license_2023", return_driver_license_2023_data),
        ("return_driver_license_2025", return_driver_license_2025),
        ("driver_license_region", driver_license_region_data),
        ("car_registration", car_registration_data),
        ("car_registration_region", car_registration_region_data),
    ]

    for table_name, func in tasks:
        try:
            df = func()
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"✅ [성공] 테이블 생성 완료: {table_name} (총 {len(df)}행)")
        except Exception as e:
            print(f"❌ [실패] 테이블 생성 오류 ({table_name}): {e}")

    conn.close()
    print("\n🎉 car_db 데이터베이스 구축 완료!")

if __name__ == "__main__":
    build_car_database()