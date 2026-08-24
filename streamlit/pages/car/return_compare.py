import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sqlalchemy import text


# ============================================================
# PROJECT ROOT
# SAFE/streamlit/pages/car/return_compare.py
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[3]

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
# MYSQL DATA LOAD
# ============================================================

@st.cache_data(ttl=600)
def load_return_2023():

    engine = get_engine()

    query = text(
        """
        SELECT
            id,
            region,
            age,
            age_label,
            count
        FROM return_driver_license_2023
        """
    )

    with engine.connect() as conn:
        df = pd.read_sql(
            query,
            conn
        )

    return df


@st.cache_data(ttl=600)
def load_return_2025():

    engine = get_engine()

    query = text(
        """
        SELECT
            id,
            region,
            age,
            age_label,
            count
        FROM return_driver_license_2025
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

    df_2023 = load_return_2023()
    df_2025 = load_return_2025()

except Exception as e:

    st.error(
        f"MySQL 데이터 조회 실패\n\n{e}"
    )

    st.stop()


# ============================================================
# CLEAN FUNCTION
# ============================================================

def clean_return_df(df):

    df = df.copy()

    df["region"] = (
        df["region"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["age_label"] = (
        df["age_label"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["age"] = pd.to_numeric(
        df["age"],
        errors="coerce"
    )

    df["count"] = pd.to_numeric(
        df["count"],
        errors="coerce"
    ).fillna(0)

    df = df[
        ~df["region"].isin(
            [
                "",
                "계",
                "합계",
                "총계",
                "전국",
                "미상",
                "불명",
            ]
        )
    ].copy()

    df = df[
        df["age"].notna()
    ].copy()

    df["age"] = (
        df["age"]
        .astype(int)
    )

    return df


df_2023 = clean_return_df(
    df_2023
)

df_2025 = clean_return_df(
    df_2025
)


# ============================================================
# REGION NORMALIZE
# ============================================================

REGION_MAP = {

    "서울특별시": "서울",
    "서울": "서울",

    "부산광역시": "부산",
    "부산": "부산",

    "대구광역시": "대구",
    "대구": "대구",

    "인천광역시": "인천",
    "인천": "인천",

    "광주광역시": "광주",
    "광주": "광주",

    "대전광역시": "대전",
    "대전": "대전",

    "울산광역시": "울산",
    "울산": "울산",

    "세종특별자치시": "세종",
    "세종": "세종",

    "경기도": "경기",
    "경기": "경기",

    "경기남부": "경기남부",
    "경기북부": "경기북부",

    "강원도": "강원",
    "강원특별자치도": "강원",
    "강원": "강원",

    "충청북도": "충북",
    "충북": "충북",

    "충청남도": "충남",
    "충남": "충남",

    "전라북도": "전북",
    "전북특별자치도": "전북",
    "전북": "전북",

    "전라남도": "전남",
    "전남": "전남",

    "경상북도": "경북",
    "경북": "경북",

    "경상남도": "경남",
    "경남": "경남",

    "제주특별자치도": "제주",
    "제주": "제주",
}


def normalize_region(value):

    value = str(value).strip()

    return REGION_MAP.get(
        value,
        value
    )


df_2023["region_name"] = (
    df_2023["region"]
    .apply(
        normalize_region
    )
)


df_2025["region_name"] = (
    df_2025["region"]
    .apply(
        normalize_region
    )
)


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

    background:
        transparent !important;

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


.st-key-nav_car button {

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

    font-size:
        15px !important;

    font-weight:
        800 !important;

    border-radius:
        2px !important;
}


/* ==========================================================
   PAGE
========================================================== */

.st-key-return_compare_page {

    background:
        #101625;

    border:
        1px solid
        #34405A;

    border-radius:
        20px;

    padding:
        34px 36px 44px 36px;

    box-shadow:
        0 12px 36px
        rgba(0,0,0,.18);
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
        1.4px;

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
        12px;
}


.page-sub {

    color:
        #B4BCCB;

    font-size:
        15px;

    line-height:
        1.7;

    margin-bottom:
        26px;
}


/* ==========================================================
   BACK BUTTON
========================================================== */

.st-key-back_car button {

    background:
        #192136 !important;

    color:
        #D1D6E0 !important;

    border:
        1px solid
        #39445D !important;

    border-radius:
        11px !important;

    font-size:
        13px !important;

    font-weight:
        600 !important;

    min-height:
        44px !important;
}


/* ==========================================================
   FILTER
========================================================== */

label[data-testid="stWidgetLabel"] p {

    color:
        #C2C8D3 !important;

    font-size:
        13px !important;

    font-weight:
        600 !important;
}


div[data-baseweb="select"] > div {

    background:
        #F4F5F8 !important;

    color:
        #1C2435 !important;

    min-height:
        46px !important;

    border-radius:
        8px !important;
}


div[data-baseweb="select"] span {

    color:
        #273149 !important;

    font-size:
        14px !important;
}


/* ==========================================================
   RADIO
========================================================== */

div[role="radiogroup"] {

    background:
        #182035;

    border:
        1px solid
        #394560;

    border-radius:
        12px;

    padding:
        8px 14px;

    gap:
        18px;
}


/* 라디오 전체 항목 */
div[role="radiogroup"] label {

    color:
        #F4F6FA !important;

    font-size:
        14px !important;

    font-weight:
        600 !important;

    opacity:
        1 !important;
}


/* 라디오 내부 텍스트 */
div[role="radiogroup"] label p {

    color:
        #F4F6FA !important;

    font-size:
        14px !important;

    font-weight:
        600 !important;

    opacity:
        1 !important;
}


/* Streamlit 내부 span 텍스트 */
div[role="radiogroup"] label span {

    color:
        #F4F6FA !important;

    opacity:
        1 !important;
}


/* 선택되지 않은 항목도 흐려지지 않게 */
div[role="radiogroup"] label[data-baseweb="radio"] {

    color:
        #F4F6FA !important;

    opacity:
        1 !important;
}


/* 선택된 항목 */
div[role="radiogroup"] label:has(input:checked) p {

    color:
        #D9A64A !important;

    font-weight:
        800 !important;
}


/* radio 동그라미 */
div[role="radiogroup"] input[type="radio"] {

    accent-color:
        #E1665D !important;
}

/* ==========================================================
   KPI
========================================================== */

.kpi {

    min-height:
        112px;

    background:
        #192136;

    border:
        1px solid
        #394560;

    border-radius:
        17px;

    padding:
        18px 20px;
}


.kpi-label {

    color:
        #A8B0C0;

    font-size:
        12px;

    margin-bottom:
        15px;
}


.kpi-value {

    color:
        #FFFFFF;

    font-size:
        25px;

    font-weight:
        800;
}


.positive {

    color:
        #79C5A2;
}


.negative {

    color:
        #E17663;
}


/* ==========================================================
   PANELS
========================================================== */

.st-key-compare_panel,
.st-key-change_panel,
.st-key-growth_panel,
.st-key-age_compare_panel {

    background:
        #182035;

    border:
        1px solid
        #3A4662;

    border-radius:
        28px;

    padding:
        24px 26px 20px 26px;

    margin-top:
        24px;
}


.panel-title {

    color:
        #FFFFFF;

    font-size:
        21px;

    font-weight:
        800;

    margin-bottom:
        7px;
}


.panel-sub {

    color:
        #B8C0CF;

    font-size:
        13px;

    line-height:
        1.6;

    margin-bottom:
        10px;
}


/* ==========================================================
   INFO
========================================================== */

.info-box {

    background:
        #131B2E;

    border-left:
        3px solid
        #D6A348;

    padding:
        15px 17px;

    margin-top:
        22px;

    color:
        #B5BDCB;

    font-size:
        13px;

    line-height:
        1.8;
}


/* ==========================================================
   NOTICE
========================================================== */

.notice-box {

    background:
        rgba(214,163,72,.10);

    border:
        1px solid
        rgba(214,163,72,.35);

    border-radius:
        12px;

    padding:
        13px 16px;

    margin-top:
        10px;

    margin-bottom:
        15px;

    color:
        #D8C9A9;

    font-size:
        12px;

    line-height:
        1.7;
}


/* ==========================================================
   EXPANDER
========================================================== */

[data-testid="stExpander"] {

    background:
        #182035;

    border:
        1px solid
        #394560;

    border-radius:
        14px;
}


[data-testid="stExpander"] summary {

    color:
        #E7EAF0 !important;

    font-size:
        14px !important;

    font-weight:
        600 !important;
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
# PAGE
# ============================================================

with st.container(
    key="return_compare_page"
):

    # ========================================================
    # HEADER
    # ========================================================

    head_left, head_right = st.columns(
        [
            5,
            1,
        ],
        vertical_alignment="center"
    )


    with head_left:

        st.html(
            """
            <div class="page-path">
                자동차 &gt; 운전면허 자진반납
            </div>

            <div class="page-title">
                2023년 vs 2025년 지역별 자진반납 비교
            </div>

            <div class="page-sub">
                지역별 운전면허 자진반납 건수를 비교하여
                2023년 대비 2025년의 변화와 지역별 차이를 확인합니다.
            </div>
            """
        )


    with head_right:

        with st.container(
            key="back_car"
        ):

            if st.button(
                "← 자동차 분석",
                use_container_width=True
            ):
                go_car()


    # ========================================================
    # NOTICE
    # ========================================================

    st.html(
        """
        <div class="notice-box">

            ※ 2025년 지역별 운전면허 소지자 데이터가 확보되지 않아
            자진반납률은 계산하지 않았습니다.
            본 페이지에서는 2023년과 2025년의
            <b>자진반납 건수와 증감률</b>을 기준으로 비교합니다.

        </div>
        """
    )


    # ========================================================
    # FILTER
    # ========================================================

    f1, f2, empty = st.columns(
        [
            1,
            1.6,
            2.4,
        ]
    )


    # ========================================================
    # AGE OPTIONS
    # ========================================================

    age_option_df = pd.concat(
        [
            df_2023[
                [
                    "age",
                    "age_label",
                ]
            ],
            df_2025[
                [
                    "age",
                    "age_label",
                ]
            ],
        ],
        ignore_index=True
    )


    age_option_df = (
        age_option_df
        .drop_duplicates()
        .sort_values("age")
    )


    with f1:

        age_options = (
            ["전체"]
            + age_option_df[
                "age_label"
            ]
            .dropna()
            .astype(str)
            .tolist()
        )


        selected_age = st.selectbox(
            "연령",
            age_options
        )


    # ========================================================
    # DISPLAY MODE
    # ========================================================

    with f2:

        display_mode = st.radio(
            "비교 방식",
            [
                "2023 · 2025 비교",
                "2023",
                "2025",
            ],
            horizontal=True
        )


    # ========================================================
    # FILTER DATA
    # ========================================================

    r23 = df_2023.copy()
    r25 = df_2025.copy()


    if selected_age != "전체":

        r23 = r23[
            r23[
                "age_label"
            ] == selected_age
        ]


        r25 = r25[
            r25[
                "age_label"
            ] == selected_age
        ]


    # ========================================================
    # REGION AGGREGATION
    # ========================================================

    region_2023 = (
        r23

        .groupby(
            "region_name",
            as_index=False
        )["count"]

        .sum()

        .rename(
            columns={
                "count": "count_2023"
            }
        )
    )


    region_2025 = (
        r25

        .groupby(
            "region_name",
            as_index=False
        )["count"]

        .sum()

        .rename(
            columns={
                "count": "count_2025"
            }
        )
    )


    compare_df = (
        region_2023

        .merge(
            region_2025,
            on="region_name",
            how="outer"
        )
    )


    compare_df[
        [
            "count_2023",
            "count_2025",
        ]
    ] = (
        compare_df[
            [
                "count_2023",
                "count_2025",
            ]
        ]
        .fillna(0)
    )


    # ========================================================
    # CHANGE COUNT
    # ========================================================

    compare_df[
        "change_count"
    ] = (
        compare_df[
            "count_2025"
        ]
        - compare_df[
            "count_2023"
        ]
    )


    # ========================================================
    # CHANGE RATE
    #
    # (2025 - 2023) / 2023 * 100
    # ========================================================

    compare_df[
        "change_rate"
    ] = 0.0


    valid_base = (
        compare_df[
            "count_2023"
        ] > 0
    )


    compare_df.loc[
        valid_base,
        "change_rate"
    ] = (
        (
            compare_df.loc[
                valid_base,
                "count_2025"
            ]
            - compare_df.loc[
                valid_base,
                "count_2023"
            ]
        )
        / compare_df.loc[
            valid_base,
            "count_2023"
        ]
        * 100
    )


    # ========================================================
    # NATIONAL KPI
    # ========================================================

    total_2023 = int(
        compare_df[
            "count_2023"
        ].sum()
    )


    total_2025 = int(
        compare_df[
            "count_2025"
        ].sum()
    )


    national_change_count = (
        total_2025
        - total_2023
    )


    if total_2023 > 0:

        national_change_rate = (
            national_change_count
            / total_2023
            * 100
        )

    else:

        national_change_rate = 0


    # ========================================================
    # MAX INCREASE REGION
    # ========================================================

    if not compare_df.empty:

        increase_row = compare_df.loc[
            compare_df[
                "change_count"
            ].idxmax()
        ]


        max_increase_region = str(
            increase_row[
                "region_name"
            ]
        )


        max_increase_count = int(
            increase_row[
                "change_count"
            ]
        )


        # ====================================================
        # MAX DECREASE
        # ====================================================

        decrease_row = compare_df.loc[
            compare_df[
                "change_count"
            ].idxmin()
        ]


        max_decrease_region = str(
            decrease_row[
                "region_name"
            ]
        )


        max_decrease_count = int(
            decrease_row[
                "change_count"
            ]
        )


    else:

        max_increase_region = "-"
        max_increase_count = 0

        max_decrease_region = "-"
        max_decrease_count = 0


    # ========================================================
    # KPI
    # ========================================================

    st.write("")


    k1, k2, k3, k4 = st.columns(
        4
    )


    with k1:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    2023년 자진반납
                </div>

                <div class="kpi-value">
                    {total_2023:,}건
                </div>

            </div>
            """
        )


    with k2:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    2025년 자진반납
                </div>

                <div class="kpi-value">
                    {total_2025:,}건
                </div>

            </div>
            """
        )


    change_class = (
        "positive"
        if national_change_count >= 0
        else "negative"
    )


    with k3:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    2023 → 2025 증감
                </div>

                <div class="kpi-value {change_class}">
                    {national_change_count:+,}건
                </div>

            </div>
            """
        )


    with k4:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    전국 자진반납 증감률
                </div>

                <div class="kpi-value {change_class}">
                    {national_change_rate:+.1f}%
                </div>

            </div>
            """
        )


    # ========================================================
    # MAIN COMPARE CHART
    # ========================================================

    with st.container(
        key="compare_panel"
    ):

        st.html(
            """
            <div class="panel-title">
                지역별 운전면허 자진반납 건수 비교
            </div>

            <div class="panel-sub">
                X축: 지역 · Y축: 자진반납 건수(건) ·
                2023년과 2025년의 지역별 자진반납 규모를 비교합니다.
            </div>
            """
        )


        if display_mode == "2023":

            chart_df = (
                compare_df
                .sort_values(
                    "count_2023",
                    ascending=False
                )
                .copy()
            )


        else:

            chart_df = (
                compare_df
                .sort_values(
                    "count_2025",
                    ascending=False
                )
                .copy()
            )


        fig_compare = go.Figure()


        # ====================================================
        # BOTH
        # ====================================================

        if display_mode == "2023 · 2025 비교":

            fig_compare.add_trace(
                go.Bar(

                    x=chart_df[
                        "region_name"
                    ],

                    y=chart_df[
                        "count_2023"
                    ],

                    name="2023",

                    marker_color="#79B69B",

                    text=[
                        f"{int(value):,}"
                        for value
                        in chart_df[
                            "count_2023"
                        ]
                    ],

                    textposition="outside",

                    textfont=dict(
                        color="#F3F5F8",
                        size=11,
                    ),

                    hovertemplate=(
                        "<b>%{x}</b>"
                        "<br>"
                        "2023 자진반납: %{y:,}건"
                        "<extra></extra>"
                    ),
                )
            )


            fig_compare.add_trace(
                go.Bar(

                    x=chart_df[
                        "region_name"
                    ],

                    y=chart_df[
                        "count_2025"
                    ],

                    name="2025",

                    marker_color="#D9A64A",

                    text=[
                        f"{int(value):,}"
                        for value
                        in chart_df[
                            "count_2025"
                        ]
                    ],

                    textposition="outside",

                    textfont=dict(
                        color="#F3F5F8",
                        size=11,
                    ),

                    hovertemplate=(
                        "<b>%{x}</b>"
                        "<br>"
                        "2025 자진반납: %{y:,}건"
                        "<extra></extra>"
                    ),
                )
            )


        # ====================================================
        # 2023
        # ====================================================

        elif display_mode == "2023":

            fig_compare.add_trace(
                go.Bar(

                    x=chart_df[
                        "region_name"
                    ],

                    y=chart_df[
                        "count_2023"
                    ],

                    name="2023",

                    marker_color="#79B69B",

                    text=[
                        f"{int(value):,}"
                        for value
                        in chart_df[
                            "count_2023"
                        ]
                    ],

                    textposition="outside",

                    hovertemplate=(
                        "<b>%{x}</b>"
                        "<br>"
                        "%{y:,}건"
                        "<extra></extra>"
                    ),
                )
            )


        # ====================================================
        # 2025
        # ====================================================

        else:

            fig_compare.add_trace(
                go.Bar(

                    x=chart_df[
                        "region_name"
                    ],

                    y=chart_df[
                        "count_2025"
                    ],

                    name="2025",

                    marker_color="#D9A64A",

                    text=[
                        f"{int(value):,}"
                        for value
                        in chart_df[
                            "count_2025"
                        ]
                    ],

                    textposition="outside",

                    hovertemplate=(
                        "<b>%{x}</b>"
                        "<br>"
                        "%{y:,}건"
                        "<extra></extra>"
                    ),
                )
            )


        fig_compare.update_layout(

            height=570,

            barmode="group",

            bargap=.24,

            bargroupgap=.08,

            margin=dict(
                l=80,
                r=45,
                t=55,
                b=100,
            ),

            paper_bgcolor="#182035",

            plot_bgcolor="#182035",

            font=dict(
                color="#E7EAF0",
                size=13,
            ),

            legend=dict(

                orientation="h",

                yanchor="bottom",

                y=1.02,

                xanchor="right",

                x=1,

                font=dict(
                    color="#E7EAF0",
                    size=13,
                ),
            ),

            xaxis=dict(

                title="지역",

                showgrid=False,

                tickangle=-35,

                tickfont=dict(
                    color="#E5E9F0",
                    size=12,
                ),
            ),

            yaxis=dict(

                title="자진반납 건수(건)",

                showgrid=True,

                gridcolor="#35405A",

                zeroline=False,

                tickformat=",",

                tickfont=dict(
                    color="#C6CDD9",
                    size=12,
                ),
            ),
        )


        st.plotly_chart(

            fig_compare,

            use_container_width=True,

            config={
                "displayModeBar": False,
            }
        )


    # ========================================================
    # CHANGE COUNT + CHANGE RATE
    # ========================================================

    change_left, change_right = st.columns(
        [
            1,
            1,
        ],
        gap="medium"
    )


    # ========================================================
    # CHANGE COUNT
    # ========================================================

    with change_left:

        with st.container(
            key="change_panel"
        ):

            st.html(
                """
                <div class="panel-title">
                    지역별 자진반납 증감 건수
                </div>

                <div class="panel-sub">
                    2025년 자진반납 건수에서
                    2023년 자진반납 건수를 뺀 결과입니다.
                </div>
                """
            )


            change_df = (
                compare_df

                .sort_values(
                    "change_count"
                )

                .copy()
            )


            change_colors = [

                "#79C5A2"
                if value >= 0

                else "#E17663"

                for value
                in change_df[
                    "change_count"
                ]
            ]


            fig_change = go.Figure(
                go.Bar(

                    x=change_df[
                        "change_count"
                    ],

                    y=change_df[
                        "region_name"
                    ],

                    orientation="h",

                    marker_color=change_colors,

                    text=[
                        f"{int(value):+,}건"
                        for value
                        in change_df[
                            "change_count"
                        ]
                    ],

                    textposition="outside",

                    cliponaxis=False,

                    hovertemplate=(
                        "<b>%{y}</b>"
                        "<br>"
                        "증감: %{x:+,}건"
                        "<extra></extra>"
                    ),
                )
            )


            fig_change.add_vline(

                x=0,

                line_color="#A8B0BF",

                line_width=1.2,
            )


            max_abs_change = (
                change_df[
                    "change_count"
                ]
                .abs()
                .max()
            )


            if pd.isna(max_abs_change) or max_abs_change == 0:
                max_abs_change = 1


            fig_change.update_layout(

                height=570,

                margin=dict(
                    l=80,
                    r=115,
                    t=25,
                    b=65,
                ),

                paper_bgcolor="#182035",

                plot_bgcolor="#182035",

                showlegend=False,

                font=dict(
                    color="#E7EAF0",
                    size=13,
                ),

                xaxis=dict(

                    title="증감 건수",

                    showgrid=True,

                    gridcolor="#35405A",

                    zeroline=False,

                    tickformat=",",

                    range=[
                        -max_abs_change * 1.25,
                        max_abs_change * 1.25,
                    ],
                ),

                yaxis=dict(

                    title=None,

                    showgrid=False,

                    tickfont=dict(
                        color="#F0F2F6",
                        size=12,
                    ),
                ),
            )


            st.plotly_chart(

                fig_change,

                use_container_width=True,

                config={
                    "displayModeBar": False,
                }
            )


    # ========================================================
    # CHANGE RATE
    # ========================================================

    with change_right:

        with st.container(
            key="growth_panel"
        ):

            st.html(
                """
                <div class="panel-title">
                    지역별 자진반납 증감률
                </div>

                <div class="panel-sub">
                    2023년 자진반납 건수를 기준으로
                    2025년 자진반납 건수가 얼마나 증가·감소했는지 계산합니다.
                </div>
                """
            )


            growth_df = (
                compare_df[
                    compare_df[
                        "count_2023"
                    ] > 0
                ]
                .sort_values(
                    "change_rate"
                )
                .copy()
            )


            growth_colors = [

                "#79C5A2"
                if value >= 0

                else "#E17663"

                for value
                in growth_df[
                    "change_rate"
                ]
            ]


            fig_growth = go.Figure(
                go.Bar(

                    x=growth_df[
                        "change_rate"
                    ],

                    y=growth_df[
                        "region_name"
                    ],

                    orientation="h",

                    marker_color=growth_colors,

                    text=[
                        f"{value:+.1f}%"
                        for value
                        in growth_df[
                            "change_rate"
                        ]
                    ],

                    textposition="outside",

                    cliponaxis=False,

                    hovertemplate=(
                        "<b>%{y}</b>"
                        "<br>"
                        "증감률: %{x:+.1f}%"
                        "<extra></extra>"
                    ),
                )
            )


            fig_growth.add_vline(

                x=0,

                line_color="#A8B0BF",

                line_width=1.2,
            )


            fig_growth.update_layout(

                height=570,

                margin=dict(
                    l=80,
                    r=115,
                    t=25,
                    b=65,
                ),

                paper_bgcolor="#182035",

                plot_bgcolor="#182035",

                showlegend=False,

                font=dict(
                    color="#E7EAF0",
                    size=13,
                ),

                xaxis=dict(

                    title="2023년 대비 증감률(%)",

                    ticksuffix="%",

                    showgrid=True,

                    gridcolor="#35405A",

                    zeroline=False,
                ),

                yaxis=dict(

                    title=None,

                    showgrid=False,

                    tickfont=dict(
                        color="#F0F2F6",
                        size=12,
                    ),
                ),
            )


            st.plotly_chart(

                fig_growth,

                use_container_width=True,

                config={
                    "displayModeBar": False,
                }
            )


    # ========================================================
    # AGE COMPARISON
    # ========================================================

    with st.container(
        key="age_compare_panel"
    ):

        st.html(
            """
            <div class="panel-title">
                연령별 자진반납 건수 비교
            </div>

            <div class="panel-sub">
                전체 지역 기준으로 연령별 자진반납 건수가
                2023년과 2025년에 어떻게 달라졌는지 비교합니다.
            </div>
            """
        )


        age_2023 = (
            df_2023

            .groupby(
                [
                    "age",
                    "age_label",
                ],
                as_index=False
            )["count"]

            .sum()

            .rename(
                columns={
                    "count": "count_2023"
                }
            )
        )


        age_2025 = (
            df_2025

            .groupby(
                [
                    "age",
                    "age_label",
                ],
                as_index=False
            )["count"]

            .sum()

            .rename(
                columns={
                    "count": "count_2025"
                }
            )
        )


        age_compare_df = (
            age_2023

            .merge(
                age_2025,
                on=[
                    "age",
                    "age_label",
                ],
                how="outer"
            )

            .fillna(0)

            .sort_values(
                "age"
            )
        )


        fig_age = go.Figure()


        fig_age.add_trace(
            go.Scatter(

                x=age_compare_df[
                    "age_label"
                ],

                y=age_compare_df[
                    "count_2023"
                ],

                mode="lines+markers",

                name="2023",

                line=dict(
                    color="#79B69B",
                    width=4,
                ),

                marker=dict(
                    size=8,
                ),

                hovertemplate=(
                    "<b>%{x}</b>"
                    "<br>"
                    "2023: %{y:,}건"
                    "<extra></extra>"
                ),
            )
        )


        fig_age.add_trace(
            go.Scatter(

                x=age_compare_df[
                    "age_label"
                ],

                y=age_compare_df[
                    "count_2025"
                ],

                mode="lines+markers",

                name="2025",

                line=dict(
                    color="#D9A64A",
                    width=4,
                ),

                marker=dict(
                    size=8,
                ),

                hovertemplate=(
                    "<b>%{x}</b>"
                    "<br>"
                    "2025: %{y:,}건"
                    "<extra></extra>"
                ),
            )
        )


        fig_age.update_layout(

            height=450,

            margin=dict(
                l=80,
                r=45,
                t=40,
                b=90,
            ),

            paper_bgcolor="#182035",

            plot_bgcolor="#182035",

            font=dict(
                color="#E7EAF0",
                size=13,
            ),

            hovermode="x unified",

            legend=dict(

                orientation="h",

                yanchor="bottom",

                y=1.02,

                xanchor="right",

                x=1,
            ),

            xaxis=dict(

                title="연령",

                tickangle=-35,

                showgrid=False,
            ),

            yaxis=dict(

                title="자진반납 건수",

                tickformat=",",

                showgrid=True,

                gridcolor="#35405A",

                zeroline=False,
            ),
        )


        st.plotly_chart(

            fig_age,

            use_container_width=True,

            config={
                "displayModeBar": False,
            }
        )


    # ========================================================
    # SUMMARY
    # ========================================================

    national_direction = (
        "증가"
        if national_change_count > 0

        else "감소"
        if national_change_count < 0

        else "변화가 없"
    )


    st.html(
        f"""
        <div class="info-box">

            <b>2023년 → 2025년 운전면허 자진반납 비교 요약</b>
            <br><br>

            2023년 자진반납은
            <b>{total_2023:,}건</b>,
            2025년은
            <b>{total_2025:,}건</b>입니다.
            <br>

            2023년과 비교하면
            <b>{abs(national_change_count):,}건 {national_direction}</b>었으며,
            증감률은
            <b>{national_change_rate:+.1f}%</b>입니다.
            <br><br>

            자진반납 건수가 가장 많이 증가한 지역은
            <b>{max_increase_region}</b>으로
            <b>{max_increase_count:+,}건</b> 변화했습니다.
            <br>

            가장 크게 감소한 지역은
            <b>{max_decrease_region}</b>으로
            <b>{max_decrease_count:+,}건</b> 변화했습니다.

        </div>
        """
    )


    # ========================================================
    # DETAIL TABLE
    # ========================================================

    st.write("")


    with st.expander(
        "2023 · 2025 지역별 자진반납 비교 상세 보기"
    ):

        table_df = compare_df[
            [
                "region_name",
                "count_2023",
                "count_2025",
                "change_count",
                "change_rate",
            ]
        ].copy()


        table_df = (
            table_df

            .sort_values(
                "count_2025",
                ascending=False
            )

            .reset_index(
                drop=True
            )
        )


        table_df[
            [
                "count_2023",
                "count_2025",
                "change_count",
            ]
        ] = (
            table_df[
                [
                    "count_2023",
                    "count_2025",
                    "change_count",
                ]
            ]
            .round()
            .astype(int)
        )


        table_df[
            "change_rate"
        ] = (
            table_df[
                "change_rate"
            ]
            .round(1)
        )


        table_df.columns = [
            "지역",
            "2023 자진반납",
            "2025 자진반납",
            "증감 건수",
            "증감률",
        ]


        st.dataframe(

            table_df,

            use_container_width=True,

            hide_index=True,

            column_config={

                "지역":
                    st.column_config.TextColumn(
                        "지역"
                    ),

                "2023 자진반납":
                    st.column_config.NumberColumn(
                        "2023 자진반납",
                        format="%d건"
                    ),

                "2025 자진반납":
                    st.column_config.NumberColumn(
                        "2025 자진반납",
                        format="%d건"
                    ),

                "증감 건수":
                    st.column_config.NumberColumn(
                        "증감 건수",
                        format="%+d건"
                    ),

                "증감률":
                    st.column_config.NumberColumn(
                        "증감률",
                        format="%+.1f%%"
                    ),
            },
        )