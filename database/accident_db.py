import sqlite3
import pandas as pd
import re

# --- (전처리 함수들은 그대로 유지) ---
def offending_driver_age_data(file_path: str = "data/교통사고/TAAS_가해운전자 연령대별 교통사고.xlsx") -> pd.DataFrame:
    df = pd.read_excel(file_path, header=None)
    age_df = df.iloc[1:, [0, 1, 3, 4, 5, 6, 7]].copy()
    age_df.columns = ["age_group", "category", "2021", "2022", "2023", "2024", "2025"]
    age_df["age_group"] = age_df["age_group"].ffill()
    age_df = age_df[
        (age_df["category"].astype(str).str.contains("사고", na=False)) & 
        (age_df["age_group"].astype(str).str.strip() != "합계")
    ].copy()
    age_df = age_df[["age_group", "2021", "2022", "2023", "2024", "2025"]]
    age_df.columns = ["age_group", "accident_2021", "accident_2022", "accident_2023", "accident_2024", "accident_2025"]
    
    accident_cols = [f"accident_{year}" for year in range(2021, 2026)]
    for col in accident_cols:
        age_df[col] = age_df[col].astype(str).str.replace(",", "", regex=False).astype(float).astype(int)
    return age_df.reset_index(drop=True)

def offending_driver_time_data(file_path: str = "data/교통사고/TAAS_가해운전자 연령대별 및 시간대별 교통사고.xlsx") -> pd.DataFrame:
    df = pd.read_excel(file_path, header=None)
    time_df = pd.concat([df.iloc[1:, [0, 1]], df.iloc[1:, 3:]], axis=1).copy()
    time_cols = [
        "time_00_02", "time_02_04", "time_04_06", "time_06_08",
        "time_08_10", "time_10_12", "time_12_14", "time_14_16",
        "time_16_18", "time_18_20", "time_20_22", "time_22_24"
    ]
    time_df.columns = ["age_group", "category"] + time_cols
    time_df["age_group"] = time_df["age_group"].ffill()
    time_df = time_df[
        (time_df["category"].astype(str).str.contains("사고", na=False)) & 
        (time_df["age_group"].astype(str).str.strip() != "합계")
    ].copy()
    time_df = time_df[["age_group"] + time_cols]
    for col in time_cols:
        time_df[col] = time_df[col].astype(str).str.replace(",", "", regex=False).astype(float).astype(int)
    return time_df.reset_index(drop=True)

def offending_driver_weather_data(file_path: str = "data/교통사고/TAAS_기상상태별 교통사고 수.xlsx") -> pd.DataFrame:
    df = pd.read_excel(file_path, header=None)
    years = df.iloc[0].ffill()
    weathers = df.iloc[1]
    data_df = df.iloc[2:].copy()
    data_df[0] = data_df[0].ffill()
    accident_df = data_df[
        (data_df[1].astype(str).str.contains("사고", na=False)) & 
        (data_df[0].astype(str).str.strip() != "합계")
    ].copy()
    
    records = []
    weather_list = ["맑음", "흐림", "비", "안개", "눈", "기타/불명"]
    for _, row in accident_df.iterrows():
        age_group = str(row[0]).strip()
        for col_idx in range(3, len(df.columns)):
            year_val = str(years[col_idx]).strip()
            weather_val = str(weathers[col_idx]).strip()
            if any(y in year_val for y in ["2021", "2022", "2023", "2024", "2025"]) and weather_val in weather_list:
                val = str(row[col_idx]).replace(",", "").strip()
                try:
                    count = int(float(val))
                except ValueError:
                    count = 0
                records.append({
                    "age_group": age_group,
                    "year": int(year_val[:4]),
                    "weather": weather_val,
                    "accidents": count
                })
    return pd.DataFrame(records).reset_index(drop=True)

def offending_driver_type_time_data(file_path: str = "data/교통사고/TAAS_노인운전자 사고유형별 및 시간대별 교통사고.xlsx") -> pd.DataFrame:
    df = pd.read_excel(file_path, header=None)
    years = df.iloc[0].replace("", None).ffill().fillna("").astype(str).str.strip()
    time_slots = df.iloc[1].fillna("").astype(str).str.strip()
    data_df = df.iloc[2:].copy()
    data_df[0] = data_df[0].replace("", None).ffill().fillna("").astype(str).str.strip()
    data_df[1] = data_df[1].replace("", None).ffill().fillna("").astype(str).str.strip()
    
    accident_df = data_df[
        (data_df[2].astype(str).str.strip() == "사고[건]") &
        (~data_df[0].isin(["합계", "", "nan", "None"])) &
        (~data_df[1].isin(["합계", "", "nan", "None"]))
    ].copy()
    
    invalid_time_slots = {"합계", "구분", "사고유형", "시간대", "", "nan", "None"}
    records = []
    for _, row in accident_df.iterrows():
        main_type, sub_type = row[0], row[1]
        for col_idx in range(3, len(df.columns)):
            year_val, time_val = years.iloc[col_idx], time_slots.iloc[col_idx]
            year_match = re.search(r"202[1-5]", year_val)
            if not year_match or time_val in invalid_time_slots:
                continue
            val = row[col_idx]
            if pd.isna(val):
                accidents = 0
            else:
                val = str(val).replace(",", "").strip()
                try:
                    accidents = int(float(val))
                except (ValueError, TypeError):
                    continue
            records.append({
                "accident_type_main": main_type,
                "accident_type_sub": sub_type,
                "year": int(year_match.group()),
                "time_slot": time_val,
                "accidents": accidents
            })
    return pd.DataFrame(records).reset_index(drop=True)

def offending_driver_month_time_data(file_path: str = "data/교통사고/TAAS_노인운전자 월별 및 시간대별 교통사고.xlsx") -> pd.DataFrame:
    df = pd.read_excel(file_path, header=None)
    years = df.iloc[0].replace("", None).ffill().fillna("").astype(str).str.strip()
    time_slots = df.iloc[1].fillna("").astype(str).str.strip()
    data_df = df.iloc[2:].copy()
    data_df[0] = data_df[0].replace("", None).ffill().fillna("").astype(str).str.strip()
    data_df[1] = data_df[1].fillna("").astype(str).str.strip()
    
    accident_df = data_df[
        (data_df[1].str.contains("사고", na=False)) & 
        (~data_df[0].isin(["합계", "월", "", "nan", "None"]))
    ].copy()
    
    records = []
    invalid_time_slots = {"합계", "시간대", "", "nan", "None"}
    for _, row in accident_df.iterrows():
        month_str = row[0]
        month_match = re.search(r'(\d+)', month_str)
        month_val = int(month_match.group(1)) if month_match else month_str
        
        for col_idx in range(3, len(df.columns)):
            year_val, time_val = years[col_idx], time_slots[col_idx]
            year_match = re.search(r'(202[1-5])', year_val)
            if year_match and time_val not in invalid_time_slots:
                val = str(row[col_idx]).replace(",", "").strip()
                try:
                    count = int(float(val))
                except (ValueError, TypeError):
                    count = 0
                records.append({
                    "year": int(year_match.group(1)),
                    "month": month_val,
                    "time_slot": time_val,
                    "accidents": count
                })
    return pd.DataFrame(records).reset_index(drop=True)

def offending_driver_region_time_data(file_path: str = "data/교통사고/TAAS_노인운전자 지역별 및 월별 교통사고.xlsx") -> pd.DataFrame:
    df = pd.read_excel(file_path, header=None)
    years = df.iloc[0].replace("", None).ffill().fillna("").astype(str).str.strip()
    months = df.iloc[1].fillna("").astype(str).str.strip()
    data_df = df.iloc[2:].copy()
    data_df[0] = data_df[0].replace("", None).ffill().fillna("").astype(str).str.strip()
    data_df[1] = data_df[1].replace("", None).ffill().fillna("").astype(str).str.strip()
    data_df[2] = data_df[2].fillna("").astype(str).str.strip()
    
    accident_df = data_df[
        (data_df[2].str.contains("사고", na=False)) & 
        (~data_df[0].isin(["시도", "합계", "", "nan", "None"])) &
        (~data_df[1].isin(["시군구", "합계", "", "nan", "None"]))
    ].copy()
    
    records = []
    for _, row in accident_df.iterrows():
        sido, sigungu = row[0], row[1]
        for col_idx in range(4, len(df.columns)):
            year_match = re.search(r'(\d{4})', years[col_idx])
            month_match = re.search(r'(\d+)', months[col_idx])
            if year_match and month_match:
                val = str(row[col_idx]).replace(",", "").strip()
                try:
                    count = int(float(val))
                except (ValueError, TypeError):
                    count = 0
                records.append({
                    "sido": sido, "sigungu": sigungu,
                    "year": int(year_match.group(1)),
                    "month": int(month_match.group(1)),
                    "accidents": count
                })
    return pd.DataFrame(records).reset_index(drop=True)

def accident_age(file_path: str = "data/교통사고/TAAS_연령대별 교통사고 수.xlsx") -> pd.DataFrame:
    df = pd.read_excel(file_path, header=None)
    years = df.iloc[0].fillna("").astype(str).str.strip()
    data_df = df.iloc[1:].copy()
    data_df[0] = data_df[0].replace("", None).ffill().fillna("").astype(str).str.strip()
    data_df[1] = data_df[1].fillna("").astype(str).str.strip()
    
    accident_df = data_df[
        (data_df[1].str.contains("사고", na=False)) & 
        (~data_df[0].isin(["합계", "운전자(1당) 연령", "연령", "", "nan", "None"]))
    ].copy()
    
    records = []
    for _, row in accident_df.iterrows():
        age_group = row[0]
        for col_idx in range(3, len(df.columns)):
            year_match = re.search(r'(202[1-5])', years[col_idx])
            if year_match:
                val = str(row[col_idx]).replace(",", "").strip()
                try:
                    count = int(float(val))
                except (ValueError, TypeError):
                    count = 0
                records.append({
                    "age_group": age_group,
                    "year": int(year_match.group(1)),
                    "accidents": count
                })
    return pd.DataFrame(records).reset_index(drop=True)

def accident_region_total(file_path: str = "data/교통사고/TAAS_지역별 전체 교통사고 건수.xlsx") -> pd.DataFrame:
    df = pd.read_excel(file_path, header=None)
    years = df.iloc[0].fillna("").astype(str).str.strip()
    data_df = df.iloc[1:].copy()
    data_df[0] = data_df[0].replace("", None).ffill().fillna("").astype(str).str.strip()
    data_df[1] = data_df[1].replace("", None).ffill().fillna("").astype(str).str.strip()
    data_df[2] = data_df[2].fillna("").astype(str).str.strip()
    
    accident_df = data_df[
        (data_df[2].str.contains("사고", na=False)) & 
        (~data_df[0].isin(["시도", "합계", "", "nan", "None"])) &
        (~data_df[1].isin(["시군구", "합계", "", "nan", "None"]))
    ].copy()
    
    records = []
    for _, row in accident_df.iterrows():
        sido, sigungu = row[0], row[1]
        for col_idx in range(4, len(df.columns)):
            year_match = re.search(r'(202[1-5])', years[col_idx])
            if year_match:
                val = str(row[col_idx]).replace(",", "").strip()
                try:
                    count = int(float(val))
                except (ValueError, TypeError):
                    count = 0
                records.append({
                    "sido": sido, "sigungu": sigungu,
                    "year": int(year_match.group(1)),
                    "accidents": count
                })
    return pd.DataFrame(records).reset_index(drop=True)


# --- DB 생성 및 적재 (기존 원본 테이블 청소 로직 포함) ---
def build_sqlite_database():
    db_path = "traffic_safety.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🧹 기존 DB에 남아있는 모든 테이블을 정리합니다...")
    # 기존에 있던 모든 테이블 목록 조회 후 삭제
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        table_name = table[0]
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        print(f"🗑️ 삭제됨: {table_name}")
    
    conn.commit()
    print("\n🚀 전처리된 깨끗한 데이터만 다시 적재합니다...\n")

    tasks = [
        ("offending_driver_age", offending_driver_age_data),
        ("offending_driver_time", offending_driver_time_data),
        ("offending_driver_weather", offending_driver_weather_data),
        ("old_driver_type_time", offending_driver_type_time_data),
        ("old_driver_month_time", offending_driver_month_time_data),
        ("old_driver_region_time", offending_driver_region_time_data),
        ("accident_age", accident_age),
        ("accident_region_total", accident_region_total)
    ]

    for table_name, func in tasks:
        try:
            df = func()
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"✅ [성공] 테이블 생성 완료: {table_name} (총 {len(df)}행)")
        except Exception as e:
            print(f"❌ [실패] 테이블 생성 오류 ({table_name}): {e}")

    conn.close()
    print("\n🎉 DB 갱신이 완료되었습니다! 툴에서 새로고침 후 확인해보세요.")

if __name__ == "__main__":
    build_sqlite_database()