import pandas as pd
import re

# 1. KOSIS_운전면허소지자현황_성별.csv
#          license_main license_sub  year gender    count
# 0             1종          대형  2019     남자  2337015
# 1             1종          대형  2019     여자    61233
# 2             1종          대형  2020     남자  2389215
# 3             1종          대형  2020     여자    65515
def license_holder_gender_data(file_path: str = "data/자동차/KOSIS_운전면허소지자현황_성별.csv") -> pd.DataFrame:

    # 1. 헤더 없이 CSV 읽기 (위치 기반 슬라이싱을 위해)
    df = pd.read_csv(file_path, encoding="cp949", header=None)

    # 2. 헤더 추출 (0행: 연도, 1행: 성별/구분)
    years = df.iloc[0].ffill()
    genders = df.iloc[1]
    
    # 3. 데이터 영역 (2행부터 시작, 헤더 제외)
    data_df = df.iloc[2:].copy()
    
    # 4. 면허종별 병합 셀 ffill 처리 (.iloc 사용으로 KeyError 방지)
    data_df.iloc[:, 0] = data_df.iloc[:, 0].replace("", None).ffill().fillna("").astype(str).str.strip()
    data_df.iloc[:, 1] = data_df.iloc[:, 1].fillna("").astype(str).str.strip()
    
    # 5. 불필요한 합계 행 제외 ('소계', '총계' 등)
    valid_df = data_df[
        (~data_df.iloc[:, 0].isin(["총계", "면허종별(1)", "면허종별(2)", "", "nan", "None"])) &
        (~data_df.iloc[:, 1].isin(["소계", "총계", "", "nan", "None"]))
    ].copy()
    
    records = []
    
    # 6. 데이터 언피벗(Unpivot) 순회
    for _, row in valid_df.iterrows():
        # iloc 사용으로 정수 위치 기반 접근
        license_type_main = row.iloc[0]
        license_type_sub = row.iloc[1]
        
        # C열(2번 인덱스)부터 끝까지 연도/성별 컬럼 순회
        for col_idx in range(2, len(df.columns)):
            year_val = str(years.iloc[col_idx]).strip()
            gender_val = str(genders.iloc[col_idx]).strip()
            
            # 4자리 연도 추출
            year_match = re.search(r'(\d{4})', year_val)
            
            # 성별이 '남자' 또는 '여자'인 열만 수집 ('계' 열 제외)
            if year_match and gender_val in ["남자", "여자"]:
                year_num = int(year_match.group(1))
                
                # 수치 정제 (쉼표 및 하이픈 '-' 0 처리)
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
                
    result_df = pd.DataFrame(records)
    return result_df.reset_index(drop=True)





# 2. KOSIS_운전면허소지자현황_연령대별.csv
#      age  year license_main license_sub  count
# 0     16  2024           1종          대형      0
# 1     16  2024           1종          보통      0
# 2     16  2024           1종          소형      0
# 3     16  2024           1종       대형 견인      0
# 4     16  2024           1종       소형 견인      0
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

    # 2. 다중 헤더 추출 (0행: 연도, 1행: 대분류, 2행: 세부면허)
    years = df.iloc[0].ffill()
    mains = df.iloc[1].fillna("").astype(str).str.strip()
    subs = df.iloc[2].fillna("").astype(str).str.strip()
    
    # 3. 데이터 영역 (3행부터 시작)
    data_df = df.iloc[3:].copy()
    data_df.iloc[:, 0] = data_df.iloc[:, 0].fillna("").astype(str).str.strip()
    
    # 4. 연령 열 정제 (계/총계 행 제거)
    valid_df = data_df[
        ~data_df.iloc[:, 0].isin(["계", "총계", "연령대별(1)", "연령별", "", "nan", "None"])
    ].copy()
    
    records = []
    
    # 5. 행/열 순회 및 언피벗 (Unpivot)
    for _, row in valid_df.iterrows():
        age_raw = row.iloc[0]
        
        # 나이 숫자만 추출 (예: "16세" -> 16, "98세 이상" -> 98)
        age_match = re.search(r'(\d+)', age_raw)
        if not age_match:
            continue
        age_num = int(age_match.group(1))
        
        # B열(인덱스 1)부터 면허 종류 컬럼 순회
        for col_idx in range(1, len(df.columns)):
            year_val = str(years.iloc[col_idx]).strip()
            main_val = str(mains.iloc[col_idx]).strip()
            sub_val = str(subs.iloc[col_idx]).strip()
            
            year_match = re.search(r'(\d{4})', year_val)
            
            # '소계'나 '총계' 컬럼은 제외하고 순수 세부 면허 데이터만 수집
            if year_match and sub_val not in ["소계", "총계", ""] and main_val not in ["총계", "계", ""]:
                year_num = int(year_match.group(1))
                
                # 수치 정제 (쉼표 및 하이픈 0 처리)
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
#         region  year license_main   license_sub    count
# 0       서울  2020           1종          대형   261110
# 1       서울  2020           1종          보통  3102999
# 2       서울  2020           1종          소형        2
# 3       서울  2020           1종       대형 견인      165
# 4       서울  2020           1종       소형 견인      227
def license_holder_region_data(file_path: str = "data/자동차/KOSIS_운전면허소지자현황_지역별.csv") -> pd.DataFrame:

    df = pd.read_csv(file_path, encoding="cp949")
    # 1. CSV 파일 읽기 (header=None 필수 & 인코딩 예외 처리)
    df = None
    for enc in ["utf-8-sig", "cp949", "utf-8", "euc-kr"]:
        try:
            df = pd.read_csv(file_path, encoding=enc, header=None)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
            
    if df is None:
        raise ValueError("파일을 읽을 수 없습니다. 파일 경로 및 인코딩을 확인해주세요.")

    # 2. 다중 헤더 추출 (0행: 연도, 1행: 대분류, 2행: 세부면허)
    years = df.iloc[0].ffill()
    mains = df.iloc[1].fillna("").astype(str).str.strip()
    subs = df.iloc[2].fillna("").astype(str).str.strip()
    
    # 3. 데이터 영역 (4행부터 시작 - 3행 '계' 및 헤더 제외)
    data_df = df.iloc[3:].copy()
    data_df.iloc[:, 0] = data_df.iloc[:, 0].fillna("").astype(str).str.strip()
    
    # 4. 지역 열 정제 ('계', '총계' 전체 합계 행 제거)
    valid_df = data_df[
        ~data_df.iloc[:, 0].isin(["계", "총계", "지역별(1)", "시도", "", "nan", "None"])
    ].copy()
    
    records = []
    
    # 5. 행/열 순회 및 언피벗 (Unpivot)
    for _, row in valid_df.iterrows():
        region_name = row.iloc[0]  # 예: "서울", "부산", "경기남부" 등
        
        # B열(인덱스 1)부터 면허 종류 및 연도 컬럼 순회
        for col_idx in range(1, len(df.columns)):
            year_val = str(years.iloc[col_idx]).strip()
            main_val = str(mains.iloc[col_idx]).strip()
            sub_val = str(subs.iloc[col_idx]).strip()
            
            # 연도 4자리 추출 (2020~2024년 등)
            year_match = re.search(r'(\d{4})', year_val)
            
            # '소계'나 '총계' 컬럼 제외, 순수 세부 면허 데이터만 수집
            if year_match and sub_val not in ["소계", "총계", ""] and main_val not in ["총계", "계", ""]:
                year_num = int(year_match.group(1))
                
                # 수치 정제 (쉼표 및 하이픈 0 처리)
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
#       region  age age_label  count
# 0      서울특별시   64    65세 미만    190
# 1      서울특별시   65       65세     60
# 2      서울특별시   66       66세     73
# 3      서울특별시   67       67세     80
# 4      서울특별시   68       68세    115
def return_driver_license_2023_data(file_path: str = "data/자동차/경찰청_운전면허 자진반납 연령별 시도청별 취소처분현황_2023년도.csv") -> pd.DataFrame:

    df = pd.read_csv(file_path, encoding="cp949")
    # 1. CSV 파일 읽기 (인코딩 자동 시도)
    df = None
    for enc in ["utf-8-sig", "cp949", "utf-8", "euc-kr"]:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
            
    if df is None:
        raise ValueError("파일을 읽을 수 없습니다. 파일 경로 및 인코딩을 확인해주세요.")

    # 2. 첫 번째 컬럼(지역명) 정제 및 불필요한 전체 합계 행 제거
    df.rename(columns={df.columns[0]: "region"}, inplace=True)
    df["region"] = df["region"].fillna("").astype(str).str.strip()
    
    valid_df = df[
        ~df["region"].isin(["계", "총계", "합계", "지역", "지역별", "", "nan", "None"])
    ].copy()

    records = []

    # 3. 행(지역) / 열(연령) 순회
    for _, row in valid_df.iterrows():
        region_name = row["region"]

        # 2번째 컬럼부터 끝까지 순회 (age 컬럼들)
        for col_name in valid_df.columns[1:]:
            col_str = str(col_name).strip()
            
            # 수치 정제 (쉼표, 하이픈 0 처리)
            val_str = str(row[col_name]).replace(",", "").strip()
            if val_str in ["-", "", "nan", "None"]:
                count = 0
            else:
                try:
                    count = int(float(val_str))
                except (ValueError, TypeError):
                    count = 0

            # 연령(age) 파싱
            # 1) "65세 미만" -> 64 (또는 구분용 숫자)
            if "미만" in col_str:
                age_num = 64
            # 2) "90세 이상" 또는 일반 나이("65세", "89세") -> 숫자 추출
            else:
                age_match = re.search(r'(\d+)', col_str)
                if age_match:
                    age_num = int(age_match.group(1))
                else:
                    continue

            records.append({
                "region": region_name,
                "age": age_num,
                "age_label": col_str,  # '65세 미만', '90세 이상' 원본 라벨 유지용
                "count": count
            })

    return pd.DataFrame(records).reset_index(drop=True)




# 5. 경찰청_운전면허 자진반납 연령별 시도청별 취소처분현황_2025년도.csv
# 지역  65세 미만  65세  66세  67세  68세  69세   70세   71세  ...   82세   83세  84세  85세  86세  87세  88세  89세  90세 이상
# 0     서울특별시     431  141  171  195  212  283  2957  2681  ...  1175  1148  880  597  481  327  211  160   300
# 1     부산광역시     136  358  413  406  556  580   777   762  ...   396   377  242  189  160  122   79   40  
def return_driver_license_2025(file_path: str = "data/자동차/경찰청_운전면허 자진반납 연령별 시도청별 취소처분현황_2025년도.csv", **kwargs) -> pd.DataFrame:

    encodings = ["utf-8-sig", "cp949", "utf-8", "euc-kr"]
    
    for enc in encodings:
        try:
            return pd.read_csv(file_path, encoding=enc, **kwargs)
        except (UnicodeDecodeError, UnicodeError):
            continue
            
    raise ValueError(f"지원하는 인코딩으로 파일은 읽을 수 없습니다: {file_path}")
            
    if df is None:
        raise ValueError("파일을 읽을 수 없습니다. 파일 경로 및 인코딩을 확인해주세요.")

    # 2. 첫 번째 컬럼(지역명) 정제
    df.rename(columns={df.columns[0]: "region"}, inplace=True)
    df["region"] = df["region"].fillna("").astype(str).str.strip()
    
    # 불필요한 전체 합계 행 제거
    valid_df = df[
        ~df["region"].isin(["계", "총계", "합계", "지역", "지역별", "", "nan", "None"])
    ].copy()

    records = []

    # 3. 행(지역) / 열(연령) 순회
    for _, row in valid_df.iterrows():
        region_name = row["region"]

        # 2번째 컬럼부터 끝까지 순회 (89세, 90세 이상 등 모든 연령 컬럼 자동 대응)
        for col_name in valid_df.columns[1:]:
            col_str = str(col_name).strip()
            
            # 수치 정제 (쉼표 및 하이픈 0 처리)
            val_str = str(row[col_name]).replace(",", "").strip()
            if val_str in ["-", "", "nan", "None"]:
                count = 0
            else:
                try:
                    count = int(float(val_str))
                except (ValueError, TypeError):
                    count = 0

            # 연령(age) 파싱
            if "미만" in col_str:
                age_num = 64  # '65세 미만' 처리
            else:
                age_match = re.search(r'(\d+)', col_str)
                if age_match:
                    age_num = int(age_match.group(1)) # '89세' -> 89, '90세 이상' -> 90
                else:
                    continue

            records.append({
                "region": region_name,
                "age": age_num,
                "age_label": col_str,  # '65세 미만', '90세 이상' 등 원본 헤더 텍스트 보존
                "count": count
            })

    return pd.DataFrame(records).reset_index(drop=True)





# 6. 경찰청_운전면허소지자 지역별 종별 현황_20251231.csv
#     region gender license_type    count
# 0       서울      남        1종_대형   252789
# 1       서울      남        1종_보통  2468340
# 2       서울      남        1종_소형       53
# 3       서울      남      1종_대형견인    24599
# 4       서울      남      1종_소형견인     7997
def driver_license_region_data(file_path: str = "data/자동차/경찰청_운전면허소지자 지역별 종별 현황_20251231.csv") -> pd.DataFrame:

    df = pd.read_csv(file_path, encoding="cp949")
    df = None
    for enc in ["utf-8-sig", "cp949", "utf-8", "euc-kr"]:
        try:
            # 1행이 헤더이므로 header=0(기본값) 사용
            df = pd.read_csv(file_path, encoding=enc)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
            
    if df is None:
        raise ValueError("파일을 읽을 수 없습니다. 파일 경로 및 인코딩을 확인해주세요.")

    # 2. 첫 두 컬럼 이름 표준화 (지역, 성별)
    df.rename(columns={df.columns[0]: "region", df.columns[1]: "gender"}, inplace=True)
    
    # 3. 데이터 정제 (A열, B열 공백 제거 및 불필요한 합계 행 제외)
    df["region"] = df["region"].fillna("").astype(str).str.strip()
    df["gender"] = df["gender"].fillna("").astype(str).str.strip()
    
    valid_df = df[
        (~df["region"].isin(["계", "총계", "합계", "지역별", "", "nan", "None"])) &
        (df["gender"].isin(["남", "여", "남자", "여자"]))
    ].copy()

    records = []

    # 4. 행/열 순회하여 데이터 언피벗 (Unpivot)
    for _, row in valid_df.iterrows():
        region_val = row["region"]
        gender_val = row["gender"]

        # C열(3번째 컬럼)부터 끝까지 면허 종류 컬럼 순회
        for col_name in valid_df.columns[2:]:
            license_type = str(col_name).strip()
            
            # 수치 정제 (쉼표 제거 및 정수 변환)
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
#        region  gender   license_type    count
#     year      vehicle_type usage  count
# 0   2021           승용    관용     34
# 1   2021           승용   자가용    548
# 2   2021           승용   영업용     19
# 3   2021           승합    관용    262
# 4   2021           승합   자가용      1
# 5   2021           승합   영업용    207
def car_registration_data(file_path: str = "data/자동차/국토교통통계누리_자동차등록현황보고_연도별.csv") -> pd.DataFrame:

    # 1. CSV 파일 읽기 (names=range(100)을 주어 컬럼 개수 불일치 에러 완벽 방지)
    df = None
    for enc in ["utf-8-sig", "cp949", "utf-8", "euc-kr"]:
        try:
            # 넉넉하게 100개의 임시 컬럼을 생성하며 파싱
            df = pd.read_csv(
                file_path, 
                encoding=enc, 
                header=None, 
                names=range(100), 
                engine='python'
            )
            # 전부 비어있는(NaN) 우측 열 자동 제거
            df = df.dropna(how='all', axis=1)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
            
    if df is None:
        raise ValueError("파일을 읽을 수 없습니다. 파일 경로 및 인코딩을 확인해주세요.")

    # 2. 다중 헤더 추출
    # 1행: 차종 대분류(승용, 승합, 화물, 특수, 총계 등) -> 병합 셀 ffill 처리
    vehicle_types = df.iloc[0].ffill()
    # 2행: 용도 구분(관용, 자가용, 영업용, 계 등)
    usages = df.iloc[1].fillna("").astype(str).str.strip()

    # 3. 데이터 영역 (3행부터 시작)
    data_df = df.iloc[2:].copy()
    
    records = []

    # 4. 행(연도) 및 열(차종/용도) 순회
    for _, row in data_df.iterrows():
        year_raw = str(row.iloc[0]).strip()
        
        # 4자리 연도 추출 (예: 2021 ~ 2025)
        year_match = re.search(r'(\d{4})', year_raw)
        if not year_match:
            continue
        year_num = int(year_match.group(1))

        # B열(1번 인덱스)부터 끝까지 전체 컬럼 순회
        for col_idx in range(1, len(df.columns)):
            v_type = str(vehicle_types.iloc[col_idx]).strip()
            usage_val = str(usages.iloc[col_idx]).strip()

            # 빈 컬럼 및 '계'/'총계' 합계 열 제외
            if usage_val not in ["계", "총계", ""] and v_type not in ["총계", "계", "nan", "None", ""]:
                
                # 수치 정제 (쉼표 및 하이픈 0 처리)
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
#           month sido sigungu vehicle_type usage  count
# 0       2021-08   서울     강남구           승용    관용    155
# 1       2021-08   서울     강남구           승용   자가용    199
# 2       2021-08   서울     강남구           승용   영업용    246
# 3       2021-08   서울     강남구           승합    관용    550
# 4       2021-08   서울     강남구           승합   자가용    215
def car_registration_region_data(file_path: str = "data/자동차/국토교통통계누리_자동차증록현황보고.csv") -> pd.DataFrame:

    df = None
    for enc in ["utf-8-sig", "cp949", "utf-8", "euc-kr"]:
        try:
            df = pd.read_csv(
                file_path, 
                encoding=enc, 
                header=None, 
                names=range(100), 
                engine='python'
            )
            # 전체가 비어있는 우측 열 자동 제거
            df = df.dropna(how='all', axis=1)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
            
    if df is None:
        raise ValueError("파일을 읽을 수 없습니다. 파일 경로 및 인코딩을 확인해주세요.")

    # 2. 다중 헤더 추출
    # 0행: 차종 대분류(승용, 승합, 화물, 특수, 총계 등) -> ffill 병합
    vehicle_types = df.iloc[0].ffill()
    # 1행: 용도 구분(관용, 자가용, 영업용, 계 등)
    usages = df.iloc[1].fillna("").astype(str).str.strip()

    # 3. 데이터 영역 (2행부터 시작)
    data_df = df.iloc[2:].copy()
    records = []

    # 4. 행(지역/월) 및 열(차종/용도) 언피벗(Unpivot)
    for _, row in data_df.iterrows():
        month_val = str(row.iloc[0]).strip()     # 연월 (예: 2021-08)
        sido_val = str(row.iloc[1]).strip()      # 시도 (예: 서울)
        sigungu_val = str(row.iloc[2]).strip()   # 시군구 (예: 강남구)

        # 3번 컬럼(D열)부터 끝까지 차종/용도 컬럼 순회
        for col_idx in range(3, len(df.columns)):
            v_type = str(vehicle_types.iloc[col_idx]).strip()
            usage_val = str(usages.iloc[col_idx]).strip()

            # 빈 컬럼 및 소계/총계 열 제외
            if usage_val not in ["계", "총계", ""] and v_type not in ["총계", "계", "nan", "None", ""]:
                
                # 수치 정제 (쉼표 및 결측치 0 처리)
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

