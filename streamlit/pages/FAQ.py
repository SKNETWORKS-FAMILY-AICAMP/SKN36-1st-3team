import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import text


# ============================================================
# PROJECT ROOT
# SAFE/streamlit/pages/FAQ.py
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


# ============================================================
# PROJECT MODULE
# ============================================================

from database.connection import get_engine


# ============================================================
# PAGE MOVE
# ============================================================

def go_main():
    st.switch_page("main.py")


def go_people():
    st.switch_page("pages/people.py")


def go_car():
    st.switch_page("pages/car.py")


def go_accident():
    st.switch_page("pages/accident.py")


def go_policy():
    st.switch_page("pages/policy.py")


def go_faq():
    st.switch_page("pages/FAQ.py")


# ============================================================
# MYSQL LOAD
# ============================================================

@st.cache_data(ttl=600)
def load_faq_data():

    engine = get_engine()

    query = text(
        """
        SELECT
            id,
            no,
            category,
            question,
            answer,
            source_url
        FROM traffic_faq
        ORDER BY no, id
        """
    )

    with engine.connect() as conn:

        df = pd.read_sql(
            query,
            conn
        )

    return df


# ============================================================
# LOAD
# ============================================================

try:

    df = load_faq_data()

except Exception as e:

    st.error(
        f"MySQL FAQ 데이터 조회 실패\n\n{e}"
    )

    st.stop()


# ============================================================
# BASIC CLEAN
# ============================================================

TEXT_COLUMNS = [
    "category",
    "question",
    "answer",
    "source_url",
]


for column in TEXT_COLUMNS:

    df[column] = (
        df[column]
        .fillna("")
        .astype(str)
        .str.strip()
    )


df["no"] = pd.to_numeric(
    df["no"],
    errors="coerce"
)


# ============================================================
# CATEGORY CLEAN
# ============================================================

df = df[
    df["question"] != ""
].copy()


categories = (
    df["category"]
    .replace("", "기타")
    .dropna()
    .unique()
    .tolist()
)


# 원하는 순서가 있다면 우선 배치
CATEGORY_ORDER = [
    "자동차 등록·교통사고 관련",
    "고령화·고령운전자 관련",
    "미래 전망 관련",
    "정책 관련",
    "서비스 이용 관련",
]


ordered_categories = []


for category in CATEGORY_ORDER:

    if category in categories:

        ordered_categories.append(
            category
        )


for category in categories:

    if category not in ordered_categories:

        ordered_categories.append(
            category
        )


# ============================================================
# SESSION STATE
# ============================================================

if "faq_category" not in st.session_state:

    st.session_state.faq_category = "전체"


# ============================================================
# CSS
# ============================================================

st.html(
    """
<style>

/* ==========================================================
   GLOBAL
========================================================== */

html,
body,
[data-testid="stAppViewContainer"],
.stApp {

    min-height: 100vh;

    background:
        linear-gradient(
            135deg,
            #0B1626 0%,
            #263B62 45%,
            #A38E68 78%,
            #E0A945 100%
        );

    background-attachment: fixed;
}


header[data-testid="stHeader"],
section[data-testid="stSidebar"],
#MainMenu,
footer {

    display: none;
}


.block-container {

    max-width: 1600px;

    padding-top: 14px;
    padding-left: 30px;
    padding-right: 30px;
    padding-bottom: 50px;
}


/* ==========================================================
   NAV
========================================================== */

.st-key-top_nav {

    background:
        rgba(255,255,255,.98);

    border-radius: 16px;

    padding:
        10px 20px;

    margin-bottom: 20px;

    box-shadow:
        0 5px 20px
        rgba(0,0,0,.10);
}


.st-key-top_nav button {

    background:
        transparent !important;

    color:
        #30384D !important;

    border:
        none !important;

    box-shadow:
        none !important;

    font-size:
        16px !important;

    font-weight:
        500 !important;

    min-height:
        44px !important;

    white-space:
        nowrap !important;
}


.st-key-top_nav button:hover {

    color:
        #D6A348 !important;
}


.st-key-nav_logo button {

    color:
        #27314C !important;

    font-size:
        31px !important;

    font-weight:
        900 !important;

    justify-content:
        flex-start !important;

    padding-left:
        0 !important;
}


.st-key-nav_faq button {

    color:
        #D6A348 !important;

    font-weight:
        800 !important;
}


.st-key-nav_future button {

    background:
        #D9A64A !important;

    color:
        #172035 !important;

    font-weight:
        800 !important;

    border-radius:
        2px !important;
}


/* ==========================================================
   PAGE
========================================================== */

.st-key-faq_page {

    background:
        #101625;

    border:
        1px solid
        #34405A;

    border-radius:
        20px;

    padding:
        36px 38px 48px 38px;

    box-shadow:
        0 12px 36px
        rgba(0,0,0,.18);

    min-height:
        760px;
}


/* ==========================================================
   HEADER
========================================================== */

.page-path {

    color:
        #D6A348;

    font-size:
        13px;

    font-weight:
        800;

    letter-spacing:
        1.3px;

    margin-bottom:
        10px;
}


.page-title {

    color:
        #FFFFFF;

    font-size:
        42px;

    font-weight:
        900;

    letter-spacing:
        -2px;

    line-height:
        1.15;

    margin-bottom:
        13px;
}


.page-sub {

    color:
        #B4BCCB;

    font-size:
        15px;

    line-height:
        1.7;

    margin-bottom:
        30px;
}


/* ==========================================================
   SEARCH
========================================================== */

.st-key-faq_search input {

    min-height:
        54px !important;

    border-radius:
        14px !important;

    background:
        #F4F5F8 !important;

    color:
        #20283B !important;

    font-size:
        15px !important;

    padding-left:
        16px !important;
}


.st-key-faq_search input::placeholder {

    color:
        #7D8595 !important;
}


/* ==========================================================
   CATEGORY
========================================================== */

.category-title {

    color:
        #FFFFFF;

    font-size:
        15px;

    font-weight:
        800;

    margin-top:
        24px;

    margin-bottom:
        10px;
}


.st-key-category_buttons button {

    background:
        #182035 !important;

    border:
        1px solid
        #414D69 !important;

    border-radius:
        22px !important;

    color:
        #D1D6E0 !important;

    min-height:
        42px !important;

    font-size:
        13px !important;

    font-weight:
        700 !important;

    white-space:
        nowrap !important;
}


.st-key-category_buttons button:hover {

    background:
        #202A44 !important;

    border-color:
        #D6A348 !important;

    color:
        #FFFFFF !important;
}


/* ==========================================================
   SUMMARY
========================================================== */

.faq-result-info {

    margin-top:
        34px;

    margin-bottom:
        14px;

    color:
        #B8C0CF;

    font-size:
        14px;
}


.faq-result-info strong {

    color:
        #D6A348;

    font-size:
        17px;
}


/* ==========================================================
   FAQ EXPANDER
========================================================== */

[data-testid="stExpander"] {

    background:
        #182035;

    border:
        1px solid
        #394560;

    border-radius:
        15px;

    margin-bottom:
        10px;

    overflow:
        hidden;
}


[data-testid="stExpander"] summary {

    padding:
        5px 3px !important;
}


[data-testid="stExpander"] summary p {

    color:
        #F2F4F8 !important;

    font-size:
        15px !important;

    font-weight:
        700 !important;

    line-height:
        1.5 !important;
}


[data-testid="stExpander"] summary:hover p {

    color:
        #D6A348 !important;
}


/* ==========================================================
   FAQ ANSWER
========================================================== */

.answer-wrap {

    background:
        #131B2E;

    border-left:
        3px solid
        #79B69B;

    padding:
        18px 20px;

    margin:
        5px 0 10px 0;

    border-radius:
        4px;

    color:
        #CDD3DE;

    font-size:
        14px;

    line-height:
        1.9;
}


.answer-label {

    color:
        #79C5A2;

    font-size:
        13px;

    font-weight:
        900;

    margin-bottom:
        8px;
}


.category-badge {

    display:
        inline-block;

    background:
        rgba(214,163,72,.10);

    border:
        1px solid
        rgba(214,163,72,.30);

    color:
        #E1B966;

    font-size:
        11px;

    font-weight:
        700;

    border-radius:
        20px;

    padding:
        5px 10px;

    margin-bottom:
        13px;
}


/* ==========================================================
   LINKS
========================================================== */

.st-key-source_button a {

    display:
        inline-flex;

    align-items:
        center;

    justify-content:
        center;

    min-height:
        38px;

    padding:
        0 15px;

    border-radius:
        9px;

    border:
        1px solid
        #46516B;

    background:
        #192136;

    color:
        #D9E0EB !important;

    font-size:
        12px;

    font-weight:
        700;

    text-decoration:
        none !important;
}


.st-key-source_button a:hover {

    border-color:
        #D6A348;

    color:
        #D6A348 !important;
}


/* ==========================================================
   EMPTY
========================================================== */

.empty-box {

    margin-top:
        20px;

    padding:
        50px 20px;

    text-align:
        center;

    background:
        #182035;

    border:
        1px solid
        #394560;

    border-radius:
        18px;

    color:
        #9CA6B9;

    font-size:
        14px;
}


/* ==========================================================
   FOOT INFO
========================================================== */

.faq-info {

    margin-top:
        35px;

    padding:
        16px 18px;

    background:
        #131B2E;

    border-left:
        3px solid
        #D6A348;

    color:
        #AAB4C5;

    font-size:
        12px;

    line-height:
        1.8;
}

</style>
"""
)


# ============================================================
# TOP NAV
# ============================================================

with st.container(
    key="top_nav"
):

    logo, n1, n2, n3, n4, n5, nf = st.columns(
        [
            4.3,
            .75,
            .9,
            1.1,
            .7,
            .65,
            1.9,
        ],
        vertical_alignment="center",
        gap="small"
    )


    with logo:

        if st.button(
            "SAFER",
            key="nav_logo"
        ):
            go_main()


    with n1:

        if st.button(
            "인구",
            key="nav_people",
            use_container_width=True
        ):
            go_people()


    with n2:

        if st.button(
            "자동차",
            key="nav_car",
            use_container_width=True
        ):
            go_car()


    with n3:

        if st.button(
            "교통사고",
            key="nav_accident",
            use_container_width=True
        ):
            go_accident()


    with n4:

        if st.button(
            "제도",
            key="nav_policy",
            use_container_width=True
        ):
            go_policy()


    with n5:

        if st.button(
            "FAQ",
            key="nav_faq",
            use_container_width=True
        ):
            go_faq()


    with nf:

        if st.button(
            "미래 전망 예측하기 ▶",
            key="nav_future",
            use_container_width=True
        ):

            st.toast(
                "미래 전망 페이지는 준비 중입니다.",
                icon="📈"
            )


# ============================================================
# FAQ PAGE
# ============================================================

with st.container(
    key="faq_page"
):

    # ========================================================
    # HEADER
    # ========================================================

    st.html(
        """
        <div class="page-path">
            SAFER · FAQ
        </div>

        <div class="page-title">
            자주 묻는 질문
        </div>

        <div class="page-sub">
            자동차 등록, 교통사고, 고령운전자, 정책 및
            SAFER 서비스 이용과 관련된 질문을 빠르게 찾아보세요.
        </div>
        """
    )


    # ========================================================
    # SEARCH
    # ========================================================

    with st.container(
        key="faq_search"
    ):

        search_word = st.text_input(
            "FAQ 검색",
            placeholder="질문이나 답변의 키워드를 입력하세요.",
            label_visibility="collapsed",
        )


    # ========================================================
    # CATEGORY BUTTONS
    # ========================================================

    st.html(
        """
        <div class="category-title">
            카테고리
        </div>
        """
    )


    category_list = (
        ["전체"]
        + ordered_categories
    )


    with st.container(
        key="category_buttons"
    ):

        # 카테고리가 많아도 한 줄이 너무 길어지지 않도록
        # 최대 6칸
        cols = st.columns(
            len(category_list)
            if len(category_list) <= 6
            else 6
        )


        for index, category in enumerate(
            category_list
        ):

            column_index = (
                index
                % len(cols)
            )


            with cols[column_index]:

                label = (
                    f"✓ {category}"
                    if st.session_state.faq_category == category
                    else category
                )


                if st.button(
                    label,
                    key=f"faq_category_{index}",
                    use_container_width=True,
                ):

                    st.session_state.faq_category = category

                    st.rerun()


    # ========================================================
    # FILTER DATA
    # ========================================================

    filtered_df = (
        df.copy()
    )


    selected_category = (
        st.session_state.faq_category
    )


    # --------------------------------------------------------
    # CATEGORY FILTER
    # --------------------------------------------------------

    if selected_category != "전체":

        filtered_df = (
            filtered_df[
                filtered_df[
                    "category"
                ] == selected_category
            ]
            .copy()
        )


    # --------------------------------------------------------
    # SEARCH FILTER
    # question + answer + category
    # --------------------------------------------------------

    search_word = (
        search_word.strip()
    )


    if search_word:

        mask = (

            filtered_df[
                "question"
            ].str.contains(
                search_word,
                case=False,
                na=False,
            )

            |

            filtered_df[
                "answer"
            ].str.contains(
                search_word,
                case=False,
                na=False,
            )

            |

            filtered_df[
                "category"
            ].str.contains(
                search_word,
                case=False,
                na=False,
            )

        )


        filtered_df = (
            filtered_df[
                mask
            ]
            .copy()
        )


    # ========================================================
    # SORT
    # ========================================================

    filtered_df = (
        filtered_df

        .sort_values(
            by=[
                "no",
                "id",
            ],

            na_position="last",
        )

        .reset_index(
            drop=True
        )
    )


    # ========================================================
    # RESULT INFO
    # ========================================================

    st.html(
        f"""
        <div class="faq-result-info">

            <strong>
                {len(filtered_df):,}
            </strong>
            개의 질문을 찾았습니다.

            &nbsp;&nbsp;·&nbsp;&nbsp;

            선택 카테고리:
            <b>
                {selected_category}
            </b>

        </div>
        """
    )


    # ========================================================
    # FAQ LIST
    # ========================================================

    if filtered_df.empty:

        st.html(
            """
            <div class="empty-box">

                검색 조건에 해당하는 FAQ가 없습니다.
                <br><br>

                다른 검색어나 카테고리를 선택해보세요.

            </div>
            """
        )


    else:

        for index, row in filtered_df.iterrows():

            question = (
                str(
                    row[
                        "question"
                    ]
                ).strip()
            )


            answer = (
                str(
                    row[
                        "answer"
                    ]
                ).strip()
            )


            category = (
                str(
                    row[
                        "category"
                    ]
                ).strip()
            )


            source_url = (
                str(
                    row[
                        "source_url"
                    ]
                ).strip()
            )


            # -----------------------------------------------
            # EXPANDER
            # -----------------------------------------------

            with st.expander(
                f"Q. {question}",
                expanded=False,
            ):

                st.html(
                    f"""
                    <div class="category-badge">
                        {category if category else "기타"}
                    </div>

                    <div class="answer-wrap">

                        <div class="answer-label">
                            A.
                        </div>

                        {answer}

                    </div>
                    """
                )


                # -------------------------------------------
                # SOURCE
                # -------------------------------------------

                if (
                    source_url
                    and source_url.lower()
                    not in [
                        "nan",
                        "none",
                        "null",
                    ]
                ):

                    with st.container(
                        key=f"source_button_{index}"
                    ):

                        st.link_button(
                            "출처 확인 ↗",
                            source_url,
                        )


    # ========================================================
    # BOTTOM INFO
    # ========================================================

    st.html(
        """
        <div class="faq-info">

            FAQ는 SAFER 데이터베이스에 등록된 정보를 기준으로 제공됩니다.
            출처가 등록된 항목은 답변 하단의
            <b>출처 확인</b> 버튼을 통해 원문을 확인할 수 있습니다.

        </div>
        """
    )