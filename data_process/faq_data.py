import pandas as pd
import re


#  no        category                         question                                                     answer                                                         source_url
# 0    1  자동차 등록·교통사고 관련      '가해 운전자'의 기준은 무엇인가?  교통사고 발생 시 과실 비율이 높거나 사고 원인에 직접적인 책임을 지는 제1당사자를...  https://www.scribd.com/document/914537849/2024...
# 1    2  자동차 등록·교통사고 관련      교통사고의 중상·경상은 어떻게 구분되는가?  중상은 3주 이상의 치료가 필요한 상해이며, 경상은 5일 이상 3주 미만의 치료가 ...  https://www.data.go.kr/data/15070199/fileData....
def traffic_faq_data(file_path: str = "data/FAQ/고령운전자 및 교통안전 관련 FAQ.xlsx") -> pd.DataFrame:

    # 1. 헤더 없이 전체 파일을 그대로 읽어옵니다.
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path, encoding="cp949", header=None)
    else:
        df = pd.read_excel(file_path, header=None)
    
    # 2. 실제 데이터가 시작하는 행(인덱스 2부터 끝까지)을 추출하고 필요한 5개 열 선택
    # 이미지 기준: 0열(질문 번호), 1열(질문 분류), 2열(질문 내용), 3열(답변), 4열(링크)
    faq_df = df.iloc[2:, [0, 1, 2, 3, 4]].copy()
    
    # 3. 컬럼명 재정의
    faq_df.columns = ["no", "category", "question", "answer", "source_url"]
    
    # 4. 문자열 공백 제거 및 결측치(NaN) 제거
    string_cols = ["category", "question", "answer", "source_url"]
    for col in string_cols:
        faq_df[col] = (
            faq_df[col]
            .astype(str)
            .str.strip()
            .replace({"nan": "", "None": "", "nat": ""})
        )
    
    # 5. 질문 번호(no)를 정수형으로 변환 (숫자가 아닌 경우 필터링)
    faq_df["no"] = pd.to_numeric(faq_df["no"], errors="coerce")
    faq_df = faq_df.dropna(subset=["no"]).copy()
    faq_df["no"] = faq_df["no"].astype(int)
    
    return faq_df.reset_index(drop=True)

print(traffic_faq_data())