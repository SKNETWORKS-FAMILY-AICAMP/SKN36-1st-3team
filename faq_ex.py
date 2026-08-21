import streamlit as st
import pandas as pd
import re

# 1. 전처리 함수 정의
def traffic_faq_data(file_path: str = "data/FAQ/고령운전자 및 교통안전 관련 FAQ.xlsx") -> pd.DataFrame:
    # 1. 헤더 없이 전체 파일을 그대로 읽어옵니다.
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path, encoding="cp949", header=None)
    else:
        df = pd.read_excel(file_path, header=None)
    
    # 2. 실제 데이터가 시작하는 행(인덱스 2부터 끝까지)을 추출하고 필요한 5개 열 선택
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

# 2. Streamlit 화면 구성 함수 (메뉴 연동용)
def render_faq_page():
    st.subheader("💡 교통사고 및 고령운전자 FAQ 질의응답")
    st.markdown("궁금한 키워드(예: '가해자', '면허반납', '중상')를 검색하여 관련 규정과 상세 출처를 확인하세요.")
    
    try:
        # 데이터 로드 (실제 파일 경로에 맞게 수정)
        df_faq = traffic_faq_data("data/FAQ/고령운전자 및 교통안전 관련 FAQ.xlsx")
        
        # --- 검색 및 필터 영역 ---
        col1, col2 = st.columns([3, 1])
        with col1:
            search_keyword = st.text_input("🔍 검색어 입력 (질문 내용, 답변, 분류 통합 검색)", "")
        with col2:
            # 카테고리 필터 옵션 추가
            categories = ["전체"] + list(df_faq["category"].unique())
            selected_category = st.selectbox("📁 분류 선택", categories)
            
        # 필터링 로직
        filtered_df = df_faq.copy()
        
        if selected_category != "전체":
            filtered_df = filtered_df[filtered_df["category"] == selected_category]
            
        if search_keyword:
            # 질문, 답변, 분류 중 하나라도 키워드가 포함되어 있으면 추출
            mask = (
                filtered_df["question"].str.contains(search_keyword, case=False, na=False) |
                filtered_df["answer"].str.contains(search_keyword, case=False, na=False) |
                filtered_df["category"].str.contains(search_keyword, case=False, na=False)
            )
            filtered_df = filtered_df[mask]
            
        st.markdown(f"**검색 결과: 총 {len(filtered_df)}건**")
        st.divider()
        
        # --- 결과 카드/표 형태로 출력 ---
        if len(filtered_df) == 0:
            st.warning("검색 결과가 없습니다. 다른 검색어를 입력해 보세요.")
        else:
            for _, row in filtered_df.iterrows():
                with st.expander(f"[{row['category']}] {row['question']}"):
                    st.markdown("**답변 및 상세 설명**")
                    st.write(row['answer'])
                    
                    if row['source_url'] and row['source_url'].startswith("http"):
                        st.markdown(f"🔗 **출처 링크:** [원문 바로가기]({row['source_url']})")
                    else:
                        st.markdown(f"🔗 **출처:** {row['source_url']}")
                        
        # 전체 데이터 표로도 함께 확인하고 싶을 때용 접기 메뉴
        with st.expander("📋 전체 FAQ 데이터 표로 보기"):
            st.dataframe(filtered_df, use_container_width=True)
            
    except Exception as e:
        st.error(f"FAQ 파일을 불러오는 중 오류가 발생했습니다: {e}")
        st.info("💡 파일 경로(`data/FAQ/고령운전자 및 교통안전 관련 FAQ.xlsx`)와 파일 존재 여부를 확인해 주세요.")

# 대시보드 메인에서 호출할 때
if __name__ == "__main__":
    render_faq_page()