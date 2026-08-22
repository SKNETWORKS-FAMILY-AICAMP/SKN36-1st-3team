import sqlite3
import pandas as pd
import streamlit as st


# ============================================================
# 페이지 설정
# ============================================================

st.set_page_config(
    page_title="SAFE FAQ",
    page_icon="❓",
    layout="wide"
)


# ============================================================
# DB 불러오기
# ============================================================

@st.cache_data
def load_faq():
    with sqlite3.connect("database/faq.db") as conn:
        df = pd.read_sql(
            "SELECT * FROM traffic_faq",
            conn
        )

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
    )

    return df


df = load_faq()


# ============================================================
# 카테고리
# ============================================================

categories = [
    "전체",
    "자동차 등록·교통사고 관련",
    "고령화·고령운전자 관련",
    "미래 전망 관련",
    "정책 관련",
    "서비스 이용 관련"
]


# ============================================================
# 선택 카테고리 상태 저장
# ============================================================

if "faq_category" not in st.session_state:
    st.session_state.faq_category = "전체"


# ============================================================
# 제목
# ============================================================

st.title("❓ SAFE FAQ")

st.write(
    "교통안전, 고령운전자, 정책 및 서비스 이용과 관련된 "
    "자주 묻는 질문을 확인할 수 있습니다."
)


# ============================================================
# 검색
# ============================================================

keyword = st.text_input(
    "🔍 FAQ 검색",
    placeholder="예: 고령운전자, 면허 반납, 교통사고, 자동차 등록"
)


# ============================================================
# 카테고리 버튼
# ============================================================

st.subheader("카테고리")

cols = st.columns(3)

for i, category in enumerate(categories):

    with cols[i % 3]:

        if st.button(
            category,
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.faq_category == category
                else "secondary"
            )
        ):
            st.session_state.faq_category = category
            st.rerun()


selected_category = st.session_state.faq_category


# ============================================================
# 필터링
# ============================================================

filtered = df.copy()


# 카테고리 필터
if selected_category != "전체":

    filtered = filtered[
        filtered["category"] == selected_category
    ]


# 검색 필터
if keyword:

    keyword = keyword.strip()

    mask = (
        filtered["question"]
        .astype(str)
        .str.contains(
            keyword,
            case=False,
            na=False
        )
        |
        filtered["answer"]
        .astype(str)
        .str.contains(
            keyword,
            case=False,
            na=False
        )
        |
        filtered["category"]
        .astype(str)
        .str.contains(
            keyword,
            case=False,
            na=False
        )
    )

    filtered = filtered[mask]


# ============================================================
# 결과 정보
# ============================================================

st.divider()

left, right = st.columns([3, 1])

with left:

    if selected_category == "전체":
        st.subheader("전체 FAQ")
    else:
        st.subheader(selected_category)

with right:

    st.metric(
        "검색 결과",
        f"{len(filtered)}건"
    )


# ============================================================
# 검색 결과 없음
# ============================================================

if filtered.empty:

    st.info(
        "검색 결과가 없습니다. "
        "다른 키워드 또는 카테고리를 선택해주세요."
    )


# ============================================================
# FAQ 출력
# ============================================================

else:

    for _, row in filtered.iterrows():

        question = str(row["question"])
        answer = str(row["answer"])
        category = str(row["category"])

        with st.expander(
            f"Q. {question}"
        ):

            st.caption(
                f"카테고리 · {category}"
            )

            st.write(answer)

            # 출처 URL이 존재하는 경우
            if (
                "source_url" in row.index
                and pd.notna(row["source_url"])
                and str(row["source_url"]).strip()
            ):

                st.link_button(
                    "출처 확인",
                    str(row["source_url"])
                )