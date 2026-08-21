import pandas as pd

def load_local_people_data(file_path: str = "data/인구/e-나라지표_지역별 인구.xlsx") -> pd.DataFrame:
    """e-나라지표 지역별 인구 엑셀 데이터를 정제하여 데이터프레임으로 반환합니다."""
    
    # 엑셀 데이터 로드 및 필요한 열 추출
    df = pd.read_excel(file_path, header=None)
    local_people = df.iloc[4:, [0, 1, 3, 5, 7, 9]].copy()
    
    # 컬럼명 변경
    local_people.columns = [
        "region",
        "population_2021",
        "population_2022",
        "population_2023",
        "population_2024",
        "population_2025"
    ]
    
    # "계" 제외
    local_people = local_people[local_people["region"].str.strip() != "계"].copy()
    
    # 정수형 변환
    population_cols = [f"population_{year}" for year in range(2021, 2026)]
    for col in population_cols:
        local_people[col] = (
            local_people[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .astype(int)
        )
        
    return local_people


# 2. 행정안전부 주민등록인구 CSV 데이터를 정제하여 데이터프레임으로 반환합니다.
def resident_regristration_data(file_path: str = "data/인구/행정안전부_주민등록인구및세대현황_월간.csv") -> pd.DataFrame:

    
    # read_excel -> read_csv 로 수정
    df = pd.read_csv(file_path, encoding="cp949")
    
    # 1. 행정구역 및 '총인구수'가 포함된 열만 추출
    target_cols = [df.columns[0]] + [col for col in df.columns if "총인구수" in col]
    resident_people = df[target_cols].copy()
    
    # 2. 첫 컬럼명 변경
    resident_people.rename(columns={df.columns[0]: "region"}, inplace=True)
    
    # 3. 쉼표(,) 제거 및 정수형 변환
    pop_cols = [col for col in resident_people.columns if col != "region"]
    for col in pop_cols:
        resident_people[col] = (
            resident_people[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .astype(int)
        )
        
    return resident_people

print(resident_regristration_data())