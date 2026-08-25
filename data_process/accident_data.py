import pandas as pd
import re

# 1. TAAS_가해운전자 연령대별 교통사고.xlsx
#      age_group      accident_2021  accident_2022   accident_2023  accident_2024   accident_2025
# 0    19세 이하        5470           5317           4606           4736           4392
# 1    20-29세          27546          24872          22833          20951          19323
# 2    30-39세          29830          28260          27707          26780          25971
def offending_driver_age_data(file_path: str = "data/교통사고/TAAS_가해운전자 연령대별 교통사고.xlsx") -> pd.DataFrame:

    # 1. 엑셀 불러오기 (헤더 없이 읽어서 위치 기반으로 지정)
    df = pd.read_excel(file_path, header=None)
    
    # 2. 연령대(0번 열), 구분(1번 열), 2021~2025 수치(3, 4, 5, 6, 7번 열 / D~H열) 선택
    age_df = df.iloc[1:, [0, 1, 3, 4, 5, 6, 7]].copy()
    
    # 컬럼명 임시 지정
    age_df.columns = ["age_group", "category", "2021", "2022", "2023", "2024", "2025"]
    
    # 3. 병합된 연령대(age_group) 빈값 위에서 아래로 채우기
    age_df["age_group"] = age_df["age_group"].ffill()
    
    # 4. '사고[건]' 데이터 및 전체 합계("합계") 제외
    age_df = age_df[
        (age_df["category"].astype(str).str.contains("사고", na=False)) & 
        (age_df["age_group"].astype(str).str.strip() != "합계")
    ].copy()
    
    # 5. 불필요한 category 열 제거 후 컬럼명 재설정
    age_df = age_df[["age_group", "2021", "2022", "2023", "2024", "2025"]]
    age_df.columns = [
        "age_group",
        "accident_2021",
        "accident_2022",
        "accident_2023",
        "accident_2024",
        "accident_2025"
    ]
    
    # 6. 수치 데이터 쉼표(,) 제거 및 정수형(int) 변환
    accident_cols = [f"accident_{year}" for year in range(2021, 2026)]
    for col in accident_cols:
        age_df[col] = (
            age_df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .astype(float)  # 1차로 float 변환 ('5470.0' -> 5470.0)
            .astype(int)    # 2차로 int 변환 (5470.0 -> 5470)
        )
        
    return age_df.reset_index(drop=True)


# 2. TAAS_가해운전자 시간대별 교통사고.xlsx
#      age_group  time_00_02  time_02_04  time_04_06  time_06_08  time_08_10  time_10_12  time_12_14  time_14_16  time_16_18  time_18_20  time_20_22  time_22_24
# 0    19세 이하       209         156          99         130         345         197         307         530         827         695         488         409
# 1    20-29세        1065         673         600        1152        1877        1402        1778        1815        2353        2909        2114        1585
# 2    30-39세        1089         570         601        1528        3035        2277        2672        2758        3410        3797        2409        1825
def offending_driver_time_data(file_path: str = "data/교통사고/TAAS_가해운전자 연령대별 및 시간대별 교통사고.xlsx") -> pd.DataFrame:

    # 1. 엑셀 불러오기 (헤더 없이 읽어서 위치 기반으로 지정)
    df = pd.read_excel(file_path, header=None)
    
    # 2. 0번(연령대), 1번(구분) 열과 3번 열부터 끝까지(시간대 데이터)를 동적으로 선택
    # C열(합계/2번 열) 제외: 0~1번 열 + 3번 열부터 끝까지
    time_df = pd.concat([df.iloc[1:, [0, 1]], df.iloc[1:, 3:]], axis=1).copy()
    
    # 3. 컬럼명 동적 부여
    time_cols = [
        "time_00_02", "time_02_04", "time_04_06", "time_06_08",
        "time_08_10", "time_10_12", "time_12_14", "time_14_16",
        "time_16_18", "time_18_20", "time_20_22", "time_22_24"
    ]
    time_df.columns = ["age_group", "category"] + time_cols
    
    # 4. 병합 셀 채우기 (ffill)
    time_df["age_group"] = time_df["age_group"].ffill()
    
    # 5. '사고[건]' 데이터 및 전체 합계("합계") 제외
    time_df = time_df[
        (time_df["category"].astype(str).str.contains("사고", na=False)) & 
        (time_df["age_group"].astype(str).str.strip() != "합계")
    ].copy()
    
    # 6. 불필요한 category 열 제외
    time_df = time_df[["age_group"] + time_cols]
    
    # 7. 수치 데이터 정수형(int) 변환
    for col in time_cols:
        time_df[col] = (
            time_df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .astype(float)
            .astype(int)
        )
        
    return time_df.reset_index(drop=True)



    # 1. 엑셀 파일 읽기 (이 줄이 빠졌거나 변수명이 달랐을 수 있습니다)
    df = pd.read_excel(file_path, header=None)
    
    # 2. 0번(연령대), 1번(구분) 열과 3번 열부터 끝까지(0시~2시 ~ 22시~24시 시간대) 추출
    # (C열/2번 열인 '합계'는 자동으로 제외됩니다)
    time_df = pd.concat([df.iloc[1:, [0, 1]], df.iloc[1:, 3:]], axis=1).copy()
    
    # 3. 직관적인 시간대 컬럼명 지정
    time_cols = [
        "time_00_02", "time_02_04", "time_04_06", "time_06_08",
        "time_08_10", "time_10_12", "time_12_14", "time_14_16",
        "time_16_18", "time_18_20", "time_20_22", "time_22_24"
    ]
    time_df.columns = ["age_group", "category"] + time_cols
    
    # 4. 병합 셀 채우기 (ffill)
    time_df["age_group"] = time_df["age_group"].ffill()
    
    # 5. '사고[건]' 데이터 및 '합계' 행 제외
    time_df = time_df[
        (time_df["category"].astype(str).str.contains("사고", na=False)) & 
        (time_df["age_group"].astype(str).str.strip() != "합계")
    ].copy()
    
    # 6. 불필요한 category 열 제거
    time_df = time_df[["age_group"] + time_cols]
    
    # 7. 수치 데이터 정수형(int) 변환 (float 거쳐 안전하게 int 변환)
    for col in time_cols:
        time_df[col] = (
            time_df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .astype(float)
            .astype(int)
        )
        
    return time_df.reset_index(drop=True)



# 3. TAAS_기상상태별 교통사고 수 .xlsx
#        age_group  year     weather  accidents
# 0      19세 이하  2021      맑음       4933
# 1      19세 이하  2021      흐림        160
# 2      19세 이하  2021       비        284
def offending_driver_weather_data(file_path: str = "data/교통사고/TAAS_기상상태별 교통사고 수.xlsx") -> pd.DataFrame:
    # 1. 헤더 없이 데이터 로드
    df = pd.read_excel(file_path, header=None)
    
    # 2. 1행(연도), 2행(기상상태) 정보 가져오기 (병합된 연도 위에서 아래/옆으로 채우기)
    years = df.iloc[0].ffill()
    weathers = df.iloc[1]
    
    # 3. 3행부터 실제 데이터 시작
    data_df = df.iloc[2:].copy()
    
    # 4. A열(연령대) 병합 셀 채우기 & '사고[건]' 행만 필터링
    data_df[0] = data_df[0].ffill()
    accident_df = data_df[
        (data_df[1].astype(str).str.contains("사고", na=False)) & 
        (data_df[0].astype(str).str.strip() != "합계")
    ].copy()
    
    # 5. 데이터 재구조화 (컬럼 순회하며 필요한 데이터만 추출)
    records = []
    weather_list = ["맑음", "흐림", "비", "안개", "눈", "기타/불명"]
    
    for _, row in accident_df.iterrows():
        age_group = str(row[0]).strip()
        
        for col_idx in range(3, len(df.columns)):
            year_val = str(years[col_idx]).strip()
            weather_val = str(weathers[col_idx]).strip()
            
            # 2021~2025년 사이이고 지정한 기상상태 항목인 경우만 추출
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
                
    result_df = pd.DataFrame(records)
    return result_df


# 4번 안됨
# 4. TAAS_노인운전자 사고유형별 및 시간대별 교통사고.xlsx
def offending_driver_type_time_data(
    file_path: str = "data/교통사고/TAAS_노인운전자 사고유형별 및 시간대별 교통사고.xlsx"
) -> pd.DataFrame:

    df = pd.read_excel(file_path, header=None)

    # -----------------------------
    # 1. 연도 / 시간대 헤더 처리
    # -----------------------------
    years = (
        df.iloc[0]
        .replace("", None)
        .ffill()
        .fillna("")
        .astype(str)
        .str.strip()
    )

    time_slots = (
        df.iloc[1]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # -----------------------------
    # 2. 실제 데이터 영역
    # -----------------------------
    data_df = df.iloc[2:].copy()

    # A열: 대분류
    data_df[0] = (
        data_df[0]
        .replace("", None)
        .ffill()
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # B열: 중분류
    data_df[1] = (
        data_df[1]
        .replace("", None)
        .ffill()
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # C열: 소분류
    data_df[2] = (
        data_df[2]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    # D열: 사고[건] / 사망[명] / 부상[명]
    data_df[3] = (
        data_df[3]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # -----------------------------
    # 3. 사고 건수만 추출
    # -----------------------------
    accident_df = data_df[
        (data_df[3].str.contains("사고", na=False)) &
        (~data_df[0].isin(["합계", "", "nan", "None"])) &
        (~data_df[1].isin(["합계", "", "nan", "None"]))
    ].copy()

    records = []

    # -----------------------------
    # 4. 행별 데이터 추출
    # -----------------------------
    for _, row in accident_df.iterrows():

        main_type = row[0]
        middle_type = row[1]
        sub_type = row[2]

        # E열(4)은 합계이므로
        # F열(5)부터 시간대 데이터
        for col_idx in range(5, len(df.columns)):

            year_val = years.iloc[col_idx]
            time_val = time_slots.iloc[col_idx]

            # 2021 ~ 2025
            year_match = re.search(r"202[1-5]", year_val)

            if not year_match:
                continue

            # 시간대가 없는 열 제외
            if time_val in ["", "합계", "nan", "None"]:
                continue

            val = row[col_idx]

            if pd.isna(val):
                accidents = 0
            else:
                val = str(val).replace(",", "").strip()

                try:
                    accidents = int(float(val))
                except (ValueError, TypeError):
                    accidents = 0

            records.append({
                "accident_type_main": main_type,
                "accident_type_middle": middle_type,
                "accident_type_sub": sub_type,
                "year": int(year_match.group()),
                "time_slot": time_val,
                "accidents": accidents
            })

    return pd.DataFrame(records).reset_index(drop=True)


# 5. TAAS_노인운전자 월별 및 시간대별 교통사고.xlsx
#      year    month  time_slot     accidents
# 0    2021      1     0시~2시         29
def offending_driver_month_time_data(file_path: str = "data/교통사고/TAAS_노인운전자 월별 및 시간대별 교통사고.xlsx") -> pd.DataFrame:
    # 1. 엑셀 불러오기 (헤더 없이)
    df = pd.read_excel(file_path, header=None)
    
    # 2. 헤더 정보 추출 (0행: 연도, 1행: 시간대)
    # 병합된 연도 셀을 풀기 위해 빈 문자열을 None으로 치환 후 ffill
    years = df.iloc[0].replace("", None).ffill().fillna("").astype(str).str.strip()
    time_slots = df.iloc[1].fillna("").astype(str).str.strip()
    
    # 3. 데이터 영역(2행부터) 분리 및 월(A열/0번 인덱스) ffill 처리
    data_df = df.iloc[2:].copy()
    data_df[0] = data_df[0].replace("", None).ffill().fillna("").astype(str).str.strip()
    data_df[1] = data_df[1].fillna("").astype(str).str.strip()
    
    # 4. '사고[건]' 행 필터링 및 전체 '합계' 월 제외
    # B열(1번 인덱스)이 '사고[건]'인 데이터만 추출
    accident_df = data_df[
        (data_df[1].str.contains("사고", na=False)) & 
        (~data_df[0].isin(["합계", "월", "", "nan", "None"]))
    ].copy()
    
    records = []
    # 제외할 시간대 컬럼
    invalid_time_slots = {"합계", "시간대", "", "nan", "None"}
    
    # 5. 행/열 순회하며 데이터 수집
    for _, row in accident_df.iterrows():
        month_str = row[0]  # 예: "01월", "12월"
        
        # 정규표현식으로 숫자만 추출 (예: '01월' -> 1)
        month_match = re.search(r'(\d+)', month_str)
        month_val = int(month_match.group(1)) if month_match else month_str
        
        # C열(2번)은 전체 누적 합계이므로 제외, D열(3번)부터 실제 연도별 데이터 순회
        for col_idx in range(3, len(df.columns)):
            year_val = years[col_idx]
            time_val = time_slots[col_idx]
            
            # 연도 4자리 추출 (2021~2025년 매칭)
            year_match = re.search(r'(202[1-5])', year_val)
            
            if year_match:
                year_digits = year_match.group(1)
                
                # '합계' 등이 아닌 실제 시간대만 추출
                if time_val not in invalid_time_slots:
                    val = str(row[col_idx]).replace(",", "").strip()
                    try:
                        count = int(float(val))
                    except (ValueError, TypeError):
                        count = 0
                        
                    records.append({
                        "year": int(year_digits),
                        "month": month_val,
                        "time_slot": time_val,
                        "accidents": count
                    })
                    
    result_df = pd.DataFrame(records)
    return result_df.reset_index(drop=True)


# 6. TAAS_노인운전자 지역별 및 월별 교통사고.xlsx
#       sido    sigungu  year    month  accidents
#0      서울     종로구  2025      1         18
#1      서울     종로구  2025      2         15
def offending_driver_region_time_data(file_path: str = "data/교통사고/TAAS_노인운전자 지역별 및 월별 교통사고.xlsx") -> pd.DataFrame:

    # 1. 헤더 없이 불러오기
    df = pd.read_excel(file_path, header=None)

    # 2. 헤더 정보 추출 (0행: 연도, 1행: 월)
    years = df.iloc[0].replace("", None).ffill().fillna("").astype(str).str.strip()
    months = df.iloc[1].fillna("").astype(str).str.strip()
    
    # 3. 데이터 영역 (2행부터) 분리 및 시도(A열), 시군구(B열) ffill 처리
    data_df = df.iloc[2:].copy()
    data_df[0] = data_df[0].replace("", None).ffill().fillna("").astype(str).str.strip() # 시도
    data_df[1] = data_df[1].replace("", None).ffill().fillna("").astype(str).str.strip() # 시군구
    data_df[2] = data_df[2].fillna("").astype(str).str.strip() # 사고/사망/부상 구분
    
    # 4. '사고[건]' 행만 추출 (합계 행 및 헤더 텍스트 제외)
    accident_df = data_df[
        (data_df[2].str.contains("사고", na=False)) & 
        (~data_df[0].isin(["시도", "합계", "", "nan", "None"])) &
        (~data_df[1].isin(["시군구", "합계", "", "nan", "None"]))
    ].copy()
    
    records = []
    
    # 5. 행/열 순회하며 데이터 수집
    for _, row in accident_df.iterrows():
        sido = row[0]
        sigungu = row[1]
        
        # D열(3번 인덱스)은 연도/월 전체 '합계'열이므로, E열(4번 인덱스: 01월)부터 순회
        for col_idx in range(4, len(df.columns)):
            year_val = years[col_idx]
            month_val = months[col_idx]
            
            # 연도 4자리 추출 (예: '2025' 또는 '2025년')
            year_match = re.search(r'(\d{4})', year_val)
            # 월 숫자 추출 (예: '01월' -> 1)
            month_match = re.search(r'(\d+)', month_val)
            
            if year_match and month_match:
                year_num = int(year_match.group(1))
                month_num = int(month_match.group(1))
                
                val = str(row[col_idx]).replace(",", "").strip()
                try:
                    count = int(float(val))
                except (ValueError, TypeError):
                    count = 0
                    
                records.append({
                    "sido": sido,
                    "sigungu": sigungu,
                    "year": year_num,
                    "month": month_num,
                    "accidents": count
                })
                
    result_df = pd.DataFrame(records)
    return result_df.reset_index(drop=True)


# 7. TAAS_연령대별 교통사고 수.xlsx
#       age_group  year    accidents
# 0     19세 이하  2021       5470
# 1     19세 이하  2022       5317
# 2     19세 이하  2023       4606
# 3     19세 이하  2024       4736
# 4     19세 이하  2025       4392
def accident_age(
    file_path: str = "data/교통사고/TAAS_연령대별 교통사고 수.xlsx"
) -> pd.DataFrame:

    # ========================================================
    # 1. 엑셀 불러오기
    # ========================================================

    df = pd.read_excel(
        file_path,
        header=None
    )


    # ========================================================
    # 2. 연도 헤더
    # ========================================================

    years = (
        df.iloc[0]
        .fillna("")
        .astype(str)
        .str.strip()
    )


    # ========================================================
    # 3. 데이터 영역
    # ========================================================

    data_df = (
        df.iloc[1:]
        .copy()
    )


    # 연령대
    data_df[0] = (
        data_df[0]
        .replace("", None)
        .ffill()
        .fillna("")
        .astype(str)
        .str.strip()
    )


    # 사고 / 사망 / 부상 구분
    data_df[1] = (
        data_df[1]
        .fillna("")
        .astype(str)
        .str.strip()
    )


    # ========================================================
    # 4. 필요 행만 사용
    # ========================================================

    data_df = data_df[
        ~data_df[0].isin(
            [
                "",
                "합계",
                "가해운전자(1당) 연령대",
                "운전자(1당) 연령",
                "연령",
                "nan",
                "None",
                "불명",
            ]
        )
    ].copy()


    # 사고 / 사망 / 부상만 사용
    data_df = data_df[
        data_df[1].isin(
            [
                "사고[건]",
                "사망[명]",
                "부상[명]",
            ]
        )
    ].copy()


    # ========================================================
    # 5. LONG 형태 생성
    # ========================================================

    records = []


    for _, row in data_df.iterrows():

        age_group = str(
            row[0]
        ).strip()

        category = str(
            row[1]
        ).strip()


        # C열(index 2)은 합계
        # D열(index 3)부터 2021~2025
        for col_idx in range(
            3,
            len(df.columns)
        ):

            year_value = str(
                years[col_idx]
            ).strip()


            # 핵심 수정 부분
            # 2021.0 / 2021 모두 잡힘
            year_match = re.search(
                r"(20\d{2})",
                year_value
            )


            if not year_match:
                continue


            year = int(
                year_match.group(1)
            )


            # 2021~2025만 사용
            if year < 2021 or year > 2025:
                continue


            value = (
                str(
                    row[col_idx]
                )
                .replace(",", "")
                .strip()
            )


            count = pd.to_numeric(
                value,
                errors="coerce"
            )


            if pd.isna(count):
                count = 0


            records.append(
                {
                    "age_group": age_group,
                    "year": year,
                    "category": category,
                    "value": int(count),
                }
            )


    # ========================================================
    # 6. LONG DATAFRAME
    # ========================================================

    long_df = pd.DataFrame(
        records
    )


    if long_df.empty:

        print(
            "⚠️ accident_age records가 생성되지 않았습니다."
        )

        print(
            "연도 헤더:",
            years.tolist()
        )

        print(
            "구분 값:",
            data_df[1].unique().tolist()
        )


        return pd.DataFrame(
            columns=[
                "age_group",
                "year",
                "accidents",
                "deaths",
                "injuries",
            ]
        )


    # ========================================================
    # 7. 사고 / 사망 / 부상 PIVOT
    # ========================================================

    result_df = (
        long_df
        .pivot_table(
            index=[
                "age_group",
                "year",
            ],
            columns="category",
            values="value",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
    )


    # ========================================================
    # 8. 컬럼명 변경
    # ========================================================

    result_df = result_df.rename(
        columns={
            "사고[건]":
                "accidents",

            "사망[명]":
                "deaths",

            "부상[명]":
                "injuries",
        }
    )


    # ========================================================
    # 9. 필수 컬럼 보장
    # ========================================================

    required_columns = [
        "accidents",
        "deaths",
        "injuries",
    ]


    for column in required_columns:

        if column not in result_df.columns:

            result_df[
                column
            ] = 0


    # ========================================================
    # 10. 숫자 타입
    # ========================================================

    result_df[
        "year"
    ] = (
        pd.to_numeric(
            result_df[
                "year"
            ],
            errors="coerce"
        )
        .fillna(0)
        .astype(int)
    )


    for column in required_columns:

        result_df[
            column
        ] = (
            pd.to_numeric(
                result_df[
                    column
                ],
                errors="coerce"
            )
            .fillna(0)
            .astype(int)
        )


    # ========================================================
    # 11. 연령대 정렬
    # ========================================================

    def age_sort_key(
        age_group: str
    ) -> int:

        age_group = str(
            age_group
        ).strip()


        if age_group == "19세 이하":
            return 19


        if age_group == "65세 이상":
            return 65


        match = re.search(
            r"(\d+)",
            age_group
        )


        if match:

            return int(
                match.group(1)
            )


        return 999


    result_df[
        "age_order"
    ] = (
        result_df[
            "age_group"
        ]
        .apply(
            age_sort_key
        )
    )


    result_df = (
        result_df
        .sort_values(
            [
                "year",
                "age_order",
            ]
        )
        .drop(
            columns=[
                "age_order"
            ]
        )
        .reset_index(
            drop=True
        )
    )


    # ========================================================
    # 12. 최종 컬럼 순서
    # ========================================================

    result_df = result_df[
        [
            "age_group",
            "year",
            "accidents",
            "deaths",
            "injuries",
        ]
    ]


    # 확인용 출력
    print(
        "\n📊 accident_age 전처리 결과"
    )

    print(
        result_df.head(
            10
        ).to_string(
            index=False
        )
    )


    print(
        f"\n총 {len(result_df):,}행"
    )


    return result_df

# 8. TAAS_연령대별 교통사고 수.xlsx
#        sido    sigungu  year     accidents
# 0      서울     종로구  2021        778
# 1      서울     종로구  2022        974
# 2      서울     종로구  2023        988
import pandas as pd
import re


# ============================================================
# 지역별 전체 교통사고
# 사고건수 + 사망자수 + 부상자수
# ============================================================

def accident_region_total(
    file_path: str = "data/교통사고/TAAS_지역별 전체 교통사고 건수.xlsx"
) -> pd.DataFrame:

    # ========================================================
    # 1. 엑셀 불러오기
    # ========================================================

    df = pd.read_excel(
        file_path,
        header=None
    )


    # ========================================================
    # 2. 연도 헤더 추출
    #
    # 0행:
    # 시도 / 시군구 / 연도 / 합계 / 2021 / 2022 / ...
    # ========================================================

    years = (
        df.iloc[0]
        .fillna("")
        .astype(str)
        .str.strip()
    )


    # ========================================================
    # 3. 실제 데이터 영역
    # ========================================================

    data_df = (
        df.iloc[1:]
        .copy()
    )


    # --------------------------------------------------------
    # 시도
    # --------------------------------------------------------

    data_df[0] = (
        data_df[0]
        .fillna("")
        .astype(str)
        .str.strip()
    )


    # --------------------------------------------------------
    # 시군구
    # --------------------------------------------------------

    data_df[1] = (
        data_df[1]
        .fillna("")
        .astype(str)
        .str.strip()
    )


    # --------------------------------------------------------
    # 구분
    # 사고[건] / 사망[명] / 부상[명]
    # --------------------------------------------------------

    data_df[2] = (
        data_df[2]
        .fillna("")
        .astype(str)
        .str.strip()
    )


    # ========================================================
    # 4. 불필요한 행 제외
    # ========================================================

    data_df = data_df[
        ~data_df[0].isin(
            [
                "",
                "시도",
                "nan",
                "None",
            ]
        )
    ].copy()


    # 주석 행 제거
    data_df = data_df[
        ~data_df[0].str.contains(
            "주\\)",
            regex=True,
            na=False
        )
    ].copy()


    # 사고 / 사망 / 부상만 사용
    data_df = data_df[
        data_df[2].isin(
            [
                "사고[건]",
                "사망[명]",
                "부상[명]",
            ]
        )
    ].copy()


    # ========================================================
    # 5. long 형태로 변환
    # ========================================================

    records = []


    for _, row in data_df.iterrows():

        sido = str(
            row[0]
        ).strip()


        sigungu = str(
            row[1]
        ).strip()


        category = str(
            row[2]
        ).strip()


        # ----------------------------------------------------
        # D열(index=3)은 2021~2025 합계이므로 제외
        # E열(index=4)부터 실제 연도
        # ----------------------------------------------------

        for col_idx in range(
            4,
            len(df.columns)
        ):

            year_value = str(
                years[col_idx]
            ).strip()


            # ------------------------------------------------
            # 2021.0 → 2021
            # ------------------------------------------------

            year_match = re.search(
                r"(20\d{2})",
                year_value
            )


            if not year_match:
                continue


            year = int(
                year_match.group(1)
            )


            # ------------------------------------------------
            # 값 숫자 변환
            # ------------------------------------------------

            value = (
                str(
                    row[col_idx]
                )
                .replace(",", "")
                .strip()
            )


            count = pd.to_numeric(
                value,
                errors="coerce"
            )


            if pd.isna(count):
                count = 0


            records.append(
                {
                    "sido": sido,
                    "sigungu": sigungu,
                    "year": year,
                    "category": category,
                    "value": int(count),
                }
            )


    # ========================================================
    # 6. DataFrame 생성
    # ========================================================

    long_df = pd.DataFrame(
        records
    )


    # ========================================================
    # 7. 사고 / 사망 / 부상 컬럼으로 pivot
    # ========================================================

    result_df = (
        long_df
        .pivot_table(
            index=[
                "sido",
                "sigungu",
                "year",
            ],
            columns="category",
            values="value",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
    )


    # ========================================================
    # 8. 컬럼명 변경
    # ========================================================

    result_df = result_df.rename(
        columns={
            "사고[건]": "accidents",
            "사망[명]": "deaths",
            "부상[명]": "injuries",
        }
    )


    # 혹시 특정 구분이 없더라도 컬럼 생성
    required_columns = [
        "accidents",
        "deaths",
        "injuries",
    ]


    for column in required_columns:

        if column not in result_df.columns:

            result_df[column] = 0


    # ========================================================
    # 9. 타입 정리
    # ========================================================

    result_df["year"] = (
        pd.to_numeric(
            result_df["year"],
            errors="coerce"
        )
        .fillna(0)
        .astype(int)
    )


    for column in required_columns:

        result_df[column] = (
            pd.to_numeric(
                result_df[column],
                errors="coerce"
            )
            .fillna(0)
            .astype(int)
        )


    # ========================================================
    # 10. 정렬
    # ========================================================

    result_df = (
        result_df[
            [
                "sido",
                "sigungu",
                "year",
                "accidents",
                "deaths",
                "injuries",
            ]
        ]
        .sort_values(
            [
                "year",
                "sido",
                "sigungu",
            ]
        )
        .reset_index(
            drop=True
        )
    )


    return result_df

if __name__ == "__main__":
    file_path = "data/교통사고/TAAS_노인운전자 사고유형별 및 시간대별 교통사고.xlsx"

    df = pd.read_excel(file_path, header=None)

    print("=== 크기 ===")
    print(df.shape)

    print("\n=== 앞 15행 ===")
    print(df.head(15).to_string())

    print("\n=== 0행 ===")
    print(df.iloc[0].tolist())

    print("\n=== 1행 ===")
    print(df.iloc[1].tolist())

    print("\n=== 2열 값 ===")
    print(df.iloc[:, 2].dropna().unique())