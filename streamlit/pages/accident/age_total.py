import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sqlalchemy import text


# ============================================================
# PROJECT ROOT
# SAFE/streamlit/pages/accident/age_total.py
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
# DB LOAD
# ============================================================

@st.cache_data(ttl=600)
def load_accident_age():

    engine = get_engine()

    query = text(
        """
        SELECT
            id,
            age_group,
            year,
            accidents
        FROM accident_age
        ORDER BY year, age_group
        """
    )

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df


@st.cache_data(ttl=600)
def load_driver_age_accident():

    engine = get_engine()

    query = text(
        """
        SELECT
            id,
            age_group,
            accident_2021,
            accident_2022,
            accident_2023,
            accident_2024,
            accident_2025
        FROM driver_age_accident
        ORDER BY id
        """
    )

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df


# ============================================================
# LOAD
# ============================================================

try:

    age_df = load_accident_age()
    driver_df = load_driver_age_accident()

except Exception as e:

    st.error(
        f"MySQL 데이터 조회 실패\n\n{e}"
    )

    st.stop()


# ============================================================
# BASIC CLEAN - AGE
# ============================================================

age_df["age_group"] = (
    age_df["age_group"]
    .fillna("")
    .astype(str)
    .str.strip()
)


age_df["year"] = pd.to_numeric(
    age_df["year"],
    errors="coerce"
)


age_df["accidents"] = pd.to_numeric(
    age_df["accidents"],
    errors="coerce"
).fillna(0)


age_df = age_df[
    age_df["year"].notna()
].copy()


age_df["year"] = (
    age_df["year"]
    .astype(int)
)


# ============================================================
# BASIC CLEAN - DRIVER
# ============================================================

driver_df["age_group"] = (
    driver_df["age_group"]
    .fillna("")
    .astype(str)
    .str.strip()
)


DRIVER_YEAR_COLUMNS = [
    "accident_2021",
    "accident_2022",
    "accident_2023",
    "accident_2024",
    "accident_2025",
]


for column in DRIVER_YEAR_COLUMNS:

    driver_df[column] = pd.to_numeric(
        driver_df[column],
        errors="coerce"
    ).fillna(0)


# ============================================================
# INVALID AGE
# ============================================================

INVALID_AGES = [
    "",
    "계",
    "합계",
    "총계",
    "전체",
]


age_df = age_df[
    ~age_df["age_group"].isin(
        INVALID_AGES
    )
].copy()


driver_df = driver_df[
    ~driver_df["age_group"].isin(
        INVALID_AGES
    )
].copy()


# ============================================================
# AGE NORMALIZE
# ============================================================

AGE_REPLACE = {

    "19세이하": "19세 이하",
    "19세 이하": "19세 이하",

    "20세이하": "20세 이하",
    "20세 이하": "20세 이하",

    "20-29세": "20~29세",
    "20~29세": "20~29세",

    "21-30세": "21~30세",
    "21~30세": "21~30세",

    "30-39세": "30~39세",
    "30~39세": "30~39세",

    "31-40세": "31~40세",
    "31~40세": "31~40세",

    "40-49세": "40~49세",
    "40~49세": "40~49세",

    "41-50세": "41~50세",
    "41~50세": "41~50세",

    "50-59세": "50~59세",
    "50~59세": "50~59세",

    "51-60세": "51~60세",
    "51~60세": "51~60세",

    "60-64세": "60~64세",
    "60~64세": "60~64세",

    "61-64세": "61~64세",
    "61~64세": "61~64세",

    "65세이상": "65세 이상",
    "65세 이상": "65세 이상",

    "불명": "불명",
}


def normalize_age(value):

    value = str(value).strip()

    return AGE_REPLACE.get(
        value,
        value
    )


age_df["age_group"] = (
    age_df["age_group"]
    .apply(
        normalize_age
    )
)


driver_df["age_group"] = (
    driver_df["age_group"]
    .apply(
        normalize_age
    )
)


# ============================================================
# AGE SORT
# ============================================================

def age_sort_key(value):

    value = str(value)

    if "불명" in value:
        return 9999

    temp = (
        value
        .replace("세", "")
        .replace("이상", "")
        .replace("이하", "")
        .replace("미만", "")
        .replace("~", " ")
        .replace("-", " ")
    )

    for item in temp.split():

        try:
            return int(item)

        except ValueError:
            continue

    return 9998


# ============================================================
# AGE GROUP
# ============================================================

age_df = (
    age_df
    .groupby(
        [
            "year",
            "age_group",
        ],
        as_index=False
    )["accidents"]
    .sum()
)


# ============================================================
# DRIVER WIDE -> LONG
# ============================================================

driver_long = (
    driver_df
    .melt(
        id_vars=[
            "age_group"
        ],
        value_vars=DRIVER_YEAR_COLUMNS,
        var_name="year",
        value_name="accidents",
    )
)


driver_long["year"] = (
    driver_long["year"]
    .str.replace(
        "accident_",
        "",
        regex=False
    )
)


driver_long["year"] = pd.to_numeric(
    driver_long["year"],
    errors="coerce"
)


driver_long = (
    driver_long[
        driver_long["year"].notna()
    ]
    .copy()
)


driver_long["year"] = (
    driver_long["year"]
    .astype(int)
)


driver_long = (
    driver_long
    .groupby(
        [
            "year",
            "age_group",
        ],
        as_index=False
    )["accidents"]
    .sum()
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

    margin-bottom:
        20px;

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


.st-key-nav_accident button {

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

.st-key-age_accident_page {

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
        12px;
}


.page-sub {

    color:
        #C3CBD8;

    font-size:
        15px;

    line-height:
        1.7;

    margin-bottom:
        26px;
}


/* ==========================================================
   BACK
========================================================== */

.st-key-back_accident button {

    background:
        #192136 !important;

    color:
        #E3E7EE !important;

    border:
        1px solid
        #39445D !important;

    border-radius:
        11px !important;

    min-height:
        44px !important;
}


/* ==========================================================
   FILTER
========================================================== */

label[data-testid="stWidgetLabel"] p {

    color:
        #E2E7EF !important;

    font-size:
        13px !important;

    font-weight:
        700 !important;
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
        #192136;

    border:
        1px solid
        #3F4B68;

    border-radius:
        11px;

    padding:
        7px 12px;
}


div[role="radiogroup"] label p {

    color:
        #FFFFFF !important;

    font-weight:
        700 !important;
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
        #C4CCD9;

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

    line-height:
        1.2;
}


.positive {

    color:
        #EF8D76;
}


.negative {

    color:
        #8ED0AD;
}


/* ==========================================================
   PANEL
========================================================== */

.st-key-age_size_panel,
.st-key-age_trend_panel,
.st-key-driver_compare_panel,
.st-key-predict_panel,
.st-key-model_compare_panel {

    background:
        #182035;

    border:
        1px solid
        #3A4662;

    border-radius:
        28px;

    padding:
        24px 26px 22px 26px;

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
        8px;
}


.panel-sub {

    color:
        #C8D0DC;

    font-size:
        13px;

    line-height:
        1.7;

    margin-bottom:
        10px;
}


.panel-sub b {

    color:
        #F3C867;
}


/* ==========================================================
   PLOTLY TEXT VISIBILITY
========================================================== */

.js-plotly-plot .plotly .legendtext,
.js-plotly-plot .plotly .xtick text,
.js-plotly-plot .plotly .ytick text,
.js-plotly-plot .plotly .gtitle,
.js-plotly-plot .plotly .annotation-text {

    fill:
        #E8EDF5 !important;

    color:
        #E8EDF5 !important;
}


/* ==========================================================
   MODEL INFO BOX
========================================================== */

.model-box {

    background:
        #121A2B;

    border:
        1px solid
        #46516D;

    border-radius:
        16px;

    padding:
        22px 24px;

    margin-top:
        18px;

    color:
        #E6EBF3 !important;

    font-size:
        13px;

    line-height:
        1.95;
}


.model-box * {

    color:
        #E6EBF3 !important;
}


.model-box b {

    color:
        #FFFFFF !important;

    font-weight:
        800 !important;
}


.model-title {

    color:
        #F3C867 !important;

    font-size:
        16px;

    font-weight:
        900;

    margin-bottom:
        12px;
}


/* ==========================================================
   INFO BOX
========================================================== */

.info-box {

    background:
        #121A2B;

    border-left:
        3px solid
        #D6A348;

    padding:
        18px 20px;

    margin-top:
        18px;

    color:
        #E3E8F0;

    font-size:
        13px;

    line-height:
        1.9;
}


.info-box b {

    color:
        #FFFFFF;
}


/* ==========================================================
   MODEL TABLE
========================================================== */

.model-table-wrap {

    margin-top:
        18px;

    width:
        100%;

    overflow-x:
        auto;

    border-radius:
        16px;

    border:
        1px solid
        #3D4964;

    background:
        #121A2B;
}


.model-table {

    width:
        100%;

    border-collapse:
        collapse;

    min-width:
        1080px;

    font-size:
        13px;
}


.model-table thead th {

    background:
        #202A42;

    color:
        #F6F8FB;

    padding:
        15px 14px;

    text-align:
        left;

    font-weight:
        800;

    border-bottom:
        1px solid
        #46516B;

    white-space:
        nowrap;
}


.model-table tbody td {

    padding:
        15px 14px;

    color:
        #DDE3EC;

    border-bottom:
        1px solid
        #2E3951;

    line-height:
        1.55;

    vertical-align:
        middle;
}


.model-table tbody tr:last-child td {

    border-bottom:
        none;
}


.model-table tbody tr:hover {

    background:
        #1B2540;
}


.model-name {

    color:
        #FFFFFF !important;

    font-weight:
        900;

    font-size:
        14px;
}


.apply-badge {

    display:
        inline-block;

    padding:
        5px 9px;

    border-radius:
        999px;

    font-size:
        11px;

    font-weight:
        800;
}


.apply-on {

    background:
        rgba(121, 197, 162, .15);

    color:
        #8ED6B3 !important;

    border:
        1px solid
        rgba(121, 197, 162, .38);
}


.apply-off {

    background:
        rgba(158,170,190,.10);

    color:
        #BAC3D0 !important;

    border:
        1px solid
        rgba(158,170,190,.22);
}


.fit-high {

    color:
        #87D0AA !important;

    font-weight:
        900;
}


.fit-low {

    color:
        #E7BE69 !important;

    font-weight:
        900;
}


.fit-very-low {

    color:
        #E48A75 !important;

    font-weight:
        900;
}


/* ==========================================================
   MODEL REASON
========================================================== */

.model-reason-box {

    margin-top:
        20px;

    background:
        #121A2B;

    border-left:
        4px solid
        #D9A64A;

    border-radius:
        4px 14px 14px 4px;

    padding:
        20px 22px;

    color:
        #E3E8F0;

    font-size:
        13px;

    line-height:
        1.9;
}


.model-reason-title {

    color:
        #F3C867;

    font-size:
        15px;

    font-weight:
        900;

    margin-bottom:
        10px;
}


.model-reason-box b {

    color:
        #FFFFFF;
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
    key="age_accident_page"
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
                교통사고 &gt; 연령별 사고
            </div>

            <div class="page-title">
                연령별 교통사고 분석
            </div>

            <div class="page-sub">
                연령대별 교통사고 규모와 연도별 변화,
                가해운전자 사고 현황 및 미래 사고 추세를 분석합니다.
            </div>
            """
        )


    with head_right:

        with st.container(
            key="back_accident"
        ):

            if st.button(
                "← 교통사고 분석",
                use_container_width=True
            ):

                go_accident()


    # ========================================================
    # OPTIONS
    # ========================================================

    years = sorted(
        age_df[
            "year"
        ]
        .dropna()
        .unique()
        .tolist(),
        reverse=True
    )


    age_groups = sorted(
        age_df[
            "age_group"
        ]
        .dropna()
        .unique()
        .tolist(),
        key=age_sort_key
    )


    if not years or not age_groups:

        st.warning(
            "연령별 교통사고 데이터가 없습니다."
        )

        st.stop()


    # ========================================================
    # FILTER
    # ========================================================

    f1, f2, empty = st.columns(
        [
            1,
            1,
            3,
        ]
    )


    with f1:

        selected_year = st.selectbox(
            "기준 연도",
            years,
            key="age_accident_year"
        )


    with f2:

        selected_age = st.selectbox(
            "연령대",
            age_groups,
            key="age_accident_group"
        )


    # ========================================================
    # SELECTED YEAR DATA
    # ========================================================

    selected_year_df = (
        age_df[
            age_df[
                "year"
            ] == selected_year
        ]
        .copy()
        .sort_values(
            "accidents",
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )


    # ========================================================
    # KPI DATA
    # ========================================================

    total_accidents = int(
        selected_year_df[
            "accidents"
        ].sum()
    )


    if not selected_year_df.empty:

        top_age = str(
            selected_year_df.iloc[0][
                "age_group"
            ]
        )

    else:

        top_age = "-"


    current_row = (
        age_df[
            (
                age_df[
                    "year"
                ] == selected_year
            )
            &
            (
                age_df[
                    "age_group"
                ] == selected_age
            )
        ]
    )


    selected_age_accidents = (
        int(
            current_row.iloc[0][
                "accidents"
            ]
        )
        if not current_row.empty
        else 0
    )


    previous_years = [
        year
        for year in years
        if year < selected_year
    ]


    if previous_years:

        previous_year = max(
            previous_years
        )


        prev_row = (
            age_df[
                (
                    age_df[
                        "year"
                    ] == previous_year
                )
                &
                (
                    age_df[
                        "age_group"
                    ] == selected_age
                )
            ]
        )


        previous_accidents = (
            int(
                prev_row.iloc[0][
                    "accidents"
                ]
            )
            if not prev_row.empty
            else 0
        )

    else:

        previous_year = None
        previous_accidents = 0


    age_change = (
        selected_age_accidents
        - previous_accidents
    )


    age_change_rate = (
        age_change
        / previous_accidents
        * 100
        if previous_accidents > 0
        else 0
    )


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
                    {selected_year}년 전체 사고
                </div>

                <div class="kpi-value">
                    {total_accidents:,}건
                </div>

            </div>
            """
        )


    with k2:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    사고 최다 연령대
                </div>

                <div class="kpi-value">
                    {top_age}
                </div>

            </div>
            """
        )


    with k3:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    {selected_age} 사고 건수
                </div>

                <div class="kpi-value">
                    {selected_age_accidents:,}건
                </div>

            </div>
            """
        )


    with k4:

        change_class = (
            "positive"
            if age_change > 0
            else "negative"
        )


        change_text = (
            f"{age_change_rate:+.1f}%"
            if previous_year is not None
            else "-"
        )


        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    {selected_age} 전년 대비
                </div>

                <div class="kpi-value {change_class}">
                    {change_text}
                </div>

            </div>
            """
        )


    # ========================================================
    # ROW 1
    # ========================================================

    left, right = st.columns(
        [
            1,
            1,
        ],
        gap="medium"
    )


    # ========================================================
    # 1. AGE SIZE
    # ========================================================

    with left:

        with st.container(
            key="age_size_panel"
        ):

            st.html(
                f"""
                <div class="panel-title">
                    {selected_year}년 연령대별 사고 규모
                </div>

                <div class="panel-sub">
                    연령대별 교통사고 발생 건수를 비교합니다.
                </div>
                """
            )


            bar_df = (
                selected_year_df
                .copy()
            )


            bar_df[
                "age_order"
            ] = (
                bar_df[
                    "age_group"
                ]
                .apply(
                    age_sort_key
                )
            )


            bar_df = (
                bar_df
                .sort_values(
                    "age_order",
                    ascending=False
                )
            )


            bar_colors = [

                "#E17663"
                if age == selected_age

                else "#D9A64A"
                if age == top_age

                else "#79B69B"

                for age
                in bar_df[
                    "age_group"
                ]
            ]


            fig_age = go.Figure(
                go.Bar(

                    x=bar_df[
                        "accidents"
                    ],

                    y=bar_df[
                        "age_group"
                    ],

                    orientation="h",

                    marker_color=bar_colors,

                    text=[
                        f"{int(value):,}건"
                        for value
                        in bar_df[
                            "accidents"
                        ]
                    ],

                    textposition="outside",

                    textfont=dict(
                        color="#FFFFFF",
                        size=11,
                    ),

                    cliponaxis=False,

                    hovertemplate=(
                        "<b>%{y}</b>"
                        "<br>"
                        "사고: %{x:,}건"
                        "<extra></extra>"
                    ),
                )
            )


            max_accident = (
                float(
                    bar_df[
                        "accidents"
                    ].max()
                )
                if not bar_df.empty
                else 1
            )


            fig_age.update_layout(

                height=520,

                margin=dict(
                    l=90,
                    r=110,
                    t=30,
                    b=65,
                ),

                paper_bgcolor="#182035",

                plot_bgcolor="#182035",

                showlegend=False,

                bargap=.28,

                font=dict(
                    color="#E8EDF5",
                    size=12,
                ),

                xaxis=dict(

                    title="교통사고 건수(건)",

                    showgrid=True,

                    gridcolor="#35405A",

                    zeroline=False,

                    tickformat=",",

                    range=[
                        0,
                        max_accident * 1.22
                    ],

                    tickfont=dict(
                        color="#CDD5E2",
                        size=11,
                    ),

                    title_font=dict(
                        color="#AEB9CB",
                    ),
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
                fig_age,

                use_container_width=True,

                config={
                    "displayModeBar": False
                }
            )


    # ========================================================
    # 2. AGE TREND
    # ========================================================

    with right:

        with st.container(
            key="age_trend_panel"
        ):

            st.html(
                f"""
                <div class="panel-title">
                    {selected_age} 연도별 사고 변화
                </div>

                <div class="panel-sub">
                    선택한 연령대의 연도별 교통사고 발생 추이를 확인합니다.
                </div>
                """
            )


            trend_df = (
                age_df[
                    age_df[
                        "age_group"
                    ] == selected_age
                ]
                .sort_values(
                    "year"
                )
                .copy()
            )


            fig_trend = go.Figure(
                go.Scatter(

                    x=trend_df[
                        "year"
                    ],

                    y=trend_df[
                        "accidents"
                    ],

                    mode="lines+markers+text",

                    line=dict(
                        color="#91C7AA",
                        width=4,
                    ),

                    marker=dict(
                        size=9,
                        color="#D9A64A",
                    ),

                    text=[
                        f"{int(value):,}"
                        for value
                        in trend_df[
                            "accidents"
                        ]
                    ],

                    textposition="top center",

                    textfont=dict(
                        color="#FFFFFF",
                        size=10,
                    ),

                    hovertemplate=(
                        "<b>%{x}년</b>"
                        "<br>"
                        "사고: %{y:,}건"
                        "<extra></extra>"
                    ),
                )
            )


            fig_trend.update_layout(

                height=520,

                margin=dict(
                    l=80,
                    r=55,
                    t=50,
                    b=65,
                ),

                paper_bgcolor="#182035",

                plot_bgcolor="#182035",

                showlegend=False,

                font=dict(
                    color="#E8EDF5",
                    size=12,
                ),

                xaxis=dict(

                    title="연도",

                    dtick=1,

                    showgrid=False,

                    tickfont=dict(
                        color="#CDD5E2",
                    ),

                    title_font=dict(
                        color="#AEB9CB",
                    ),
                ),

                yaxis=dict(

                    title="교통사고 건수(건)",

                    showgrid=True,

                    gridcolor="#35405A",

                    zeroline=False,

                    tickformat=",",

                    tickfont=dict(
                        color="#CDD5E2",
                    ),

                    title_font=dict(
                        color="#AEB9CB",
                    ),
                ),
            )


            st.plotly_chart(
                fig_trend,

                use_container_width=True,

                config={
                    "displayModeBar": False
                }
            )


    # ========================================================
    # 3. DRIVER AGE COMPARE
    # ========================================================

    with st.container(
        key="driver_compare_panel"
    ):

        st.html(
            """
            <div class="panel-title">
                가해운전자 연령대별 사고 비교
            </div>

            <div class="panel-sub">
                가해운전자 연령대별 교통사고를
                2021년부터 2025년까지 비교합니다.
            </div>
            """
        )


        driver_age_groups = sorted(
            driver_long[
                "age_group"
            ]
            .dropna()
            .unique()
            .tolist(),
            key=age_sort_key
        )


        driver_years = sorted(
            driver_long[
                "year"
            ]
            .unique()
            .tolist()
        )


        YEAR_COLORS = {

            2021: "#6F86B5",

            2022: "#8EA2B8",

            2023: "#95B9A5",

            2024: "#C4B078",

            2025: "#D9A64A",
        }


        fig_driver = go.Figure()


        for year in driver_years:

            temp_df = (
                driver_long[
                    driver_long[
                        "year"
                    ] == year
                ]
                .set_index(
                    "age_group"
                )
                .reindex(
                    driver_age_groups
                )
                .reset_index()
            )


            temp_df[
                "accidents"
            ] = (
                temp_df[
                    "accidents"
                ]
                .fillna(0)
            )


            fig_driver.add_trace(
                go.Bar(

                    name=f"{year}년",

                    x=temp_df[
                        "age_group"
                    ],

                    y=temp_df[
                        "accidents"
                    ],

                    marker=dict(
                        color=YEAR_COLORS.get(
                            year,
                            "#8FA0B8"
                        )
                    ),

                    hovertemplate=(
                        f"<b>{year}년</b>"
                        "<br>"
                        "%{x}"
                        "<br>"
                        "사고: %{y:,}건"
                        "<extra></extra>"
                    ),
                )
            )


        fig_driver.update_layout(

            height=570,

            barmode="group",

            margin=dict(
                l=80,
                r=50,
                t=45,
                b=90,
            ),

            paper_bgcolor="#182035",

            plot_bgcolor="#182035",

            font=dict(
                color="#E8EDF5",
                size=12,
            ),

            legend=dict(

                orientation="h",

                yanchor="bottom",

                y=1.02,

                xanchor="right",

                x=1,

                bgcolor="rgba(0,0,0,0)",

                font=dict(
                    color="#F0F3F8",
                    size=12,
                ),
            ),

            xaxis=dict(

                title="연령대",

                showgrid=False,

                tickfont=dict(
                    color="#CDD5E2",
                ),

                title_font=dict(
                    color="#AEB9CB",
                ),
            ),

            yaxis=dict(

                title="교통사고 건수(건)",

                showgrid=True,

                gridcolor="#35405A",

                zeroline=False,

                tickformat=",",

                tickfont=dict(
                    color="#CDD5E2",
                ),

                title_font=dict(
                    color="#AEB9CB",
                ),
            ),
        )


        st.plotly_chart(
            fig_driver,

            use_container_width=True,

            config={
                "displayModeBar": False
            }
        )


    # ========================================================
    # 4. FUTURE PREDICTION
    # ========================================================

    with st.container(
        key="predict_panel"
    ):

        st.html(
            """
            <div class="panel-title">
                연령대별 사고 미래 예측
            </div>

            <div class="panel-sub">
                과거 연도별 사고 건수를 기반으로 향후 사고 발생 추세를 예측합니다.
                <br>
                현재 적용 모델 :
                <b>선형 추세 분석 (Linear Trend Regression)</b>
            </div>
            """
        )


        p1, p2, empty = st.columns(
            [
                1,
                1.5,
                2.5,
            ]
        )


        with p1:

            predict_age = st.selectbox(
                "예측 연령대",
                age_groups,
                index=(
                    age_groups.index(
                        selected_age
                    )
                    if selected_age in age_groups
                    else 0
                ),
                key="prediction_age_group"
            )


        with p2:

            predict_period = st.radio(
                "예측 기간",
                [
                    "1년",
                    "5년",
                    "10년",
                ],
                horizontal=True,
                key="prediction_period"
            )


        horizon_map = {

            "1년": 1,

            "5년": 5,

            "10년": 10,
        }


        horizon = horizon_map[
            predict_period
        ]


        prediction_source = (
            age_df[
                age_df[
                    "age_group"
                ] == predict_age
            ][
                [
                    "year",
                    "accidents",
                ]
            ]
            .sort_values(
                "year"
            )
            .drop_duplicates(
                subset=[
                    "year"
                ]
            )
            .copy()
        )


        if len(prediction_source) < 2:

            st.warning(
                "예측을 수행하려면 최소 2개 연도의 데이터가 필요합니다."
            )

        else:

            # =================================================
            # TRAIN DATA
            # =================================================

            x = (
                prediction_source[
                    "year"
                ]
                .to_numpy(
                    dtype=float
                )
            )


            y = (
                prediction_source[
                    "accidents"
                ]
                .to_numpy(
                    dtype=float
                )
            )


            # =================================================
            # LINEAR TREND REGRESSION
            # =================================================

            slope, intercept = np.polyfit(
                x,
                y,
                1
            )


            fitted_values = (
                slope * x
                + intercept
            )


            # =================================================
            # METRICS
            # =================================================

            residuals = (
                y - fitted_values
            )


            mae = float(
                np.mean(
                    np.abs(
                        residuals
                    )
                )
            )


            rmse = float(
                np.sqrt(
                    np.mean(
                        residuals ** 2
                    )
                )
            )


            ss_res = float(
                np.sum(
                    residuals ** 2
                )
            )


            ss_tot = float(
                np.sum(
                    (
                        y
                        - np.mean(y)
                    ) ** 2
                )
            )


            r2 = (
                1 - ss_res / ss_tot
                if ss_tot > 0
                else 0
            )


            # =================================================
            # PREDICT
            # =================================================

            last_year = int(
                prediction_source[
                    "year"
                ].max()
            )


            future_years = np.arange(
                last_year + 1,
                last_year + horizon + 1
            )


            future_values = (
                slope
                * future_years
                + intercept
            )


            future_values = np.maximum(
                future_values,
                0
            )


            # =================================================
            # CHART
            # =================================================

            fig_predict = go.Figure()


            # 실제값
            fig_predict.add_trace(
                go.Scatter(

                    x=x,

                    y=y,

                    mode="lines+markers",

                    name="실제 사고",

                    line=dict(
                        color="#A0C9AC",
                        width=4,
                    ),

                    marker=dict(
                        size=9,
                        color="#A0C9AC",
                    ),

                    hovertemplate=(
                        "<b>%{x:.0f}년</b>"
                        "<br>"
                        "실제 사고: %{y:,.0f}건"
                        "<extra></extra>"
                    ),
                )
            )


            prediction_x = (
                [
                    last_year
                ]
                + future_years.tolist()
            )


            prediction_y = (
                [
                    float(
                        y[-1]
                    )
                ]
                + future_values.tolist()
            )


            # 예측값
            fig_predict.add_trace(
                go.Scatter(

                    x=prediction_x,

                    y=prediction_y,

                    mode="lines+markers+text",

                    name="예측 사고",

                    line=dict(
                        color="#DD8469",
                        width=4,
                        dash="dash",
                    ),

                    marker=dict(
                        size=9,
                        color="#DD8469",
                    ),

                    text=[
                        ""
                    ] + [
                        f"{int(round(value)):,}"
                        for value
                        in future_values
                    ],

                    textposition="top center",

                    textfont=dict(
                        color="#FFFFFF",
                        size=10,
                    ),

                    hovertemplate=(
                        "<b>%{x}년</b>"
                        "<br>"
                        "예측 사고: %{y:,.0f}건"
                        "<extra></extra>"
                    ),
                )
            )


            # 예측 시작
            fig_predict.add_vline(

                x=last_year,

                line_width=1.5,

                line_dash="dot",

                line_color="#D6A348",
            )


            fig_predict.add_annotation(

                x=last_year,

                y=1,

                yref="paper",

                text="예측 시작",

                showarrow=False,

                yshift=16,

                font=dict(
                    color="#F3C867",
                    size=11,
                ),
            )


            fig_predict.update_layout(

                height=540,

                margin=dict(
                    l=80,
                    r=65,
                    t=60,
                    b=70,
                ),

                paper_bgcolor="#182035",

                plot_bgcolor="#182035",

                hovermode="x unified",

                font=dict(
                    color="#E8EDF5",
                    size=12,
                ),

                legend=dict(

                    orientation="h",

                    yanchor="bottom",

                    y=1.02,

                    xanchor="right",

                    x=1,

                    bgcolor="rgba(0,0,0,0)",

                    font=dict(
                        color="#F0F3F8",
                        size=12,
                    ),
                ),

                xaxis=dict(

                    title="연도",

                    dtick=1,

                    showgrid=False,

                    tickfont=dict(
                        color="#CDD5E2",
                        size=11,
                    ),

                    title_font=dict(
                        color="#AEB9CB",
                        size=13,
                    ),
                ),

                yaxis=dict(

                    title="교통사고 건수(건)",

                    showgrid=True,

                    gridcolor="#35405A",

                    zeroline=False,

                    tickformat=",",

                    tickfont=dict(
                        color="#CDD5E2",
                        size=11,
                    ),

                    title_font=dict(
                        color="#AEB9CB",
                        size=13,
                    ),
                ),
            )


            st.plotly_chart(
                fig_predict,

                use_container_width=True,

                config={
                    "displayModeBar": False
                }
            )


            # =================================================
            # RESULT
            # =================================================

            predicted_last = int(
                round(
                    future_values[-1]
                )
            )


            current_last = int(
                y[-1]
            )


            prediction_change = (
                predicted_last
                - current_last
            )


            prediction_change_rate = (
                prediction_change
                / current_last
                * 100
                if current_last > 0
                else 0
            )


            train_start_year = int(
                prediction_source[
                    "year"
                ].min()
            )


            train_end_year = int(
                prediction_source[
                    "year"
                ].max()
            )


            # =================================================
            # MODEL INFO
            # =================================================

            st.html(
                f"""
                <div class="model-box">

                    <div class="model-title">
                        예측 모델 정보
                    </div>

                    <b>현재 적용 모델</b> :
                    선형 추세 분석
                    (Linear Trend Regression)

                    <br>

                    <b>학습 데이터</b> :
                    {train_start_year}년 ~
                    {train_end_year}년
                    {predict_age} 교통사고 건수

                    <br>

                    <b>학습 데이터 개수</b> :
                    {len(prediction_source)}개 연도

                    <br>

                    <b>예측 기간</b> :
                    {predict_period}

                    <br>

                    <b>연평균 추세</b> :
                    {slope:+,.1f}건 / 년

                    <br>

                    <b>MAE</b> :
                    {mae:,.1f}건

                    <br>

                    <b>RMSE</b> :
                    {rmse:,.1f}건

                    <br>

                    <b>R²</b> :
                    {r2:.3f}

                    <br><br>

                    새로운 연도 데이터가 DB에 추가되면
                    해당 데이터를 자동으로 학습에 포함하여
                    회귀식과 미래 예측값을 다시 계산합니다.

                </div>
                """
            )


            # =================================================
            # RESULT SUMMARY
            # =================================================

            st.html(
                f"""
                <div class="info-box">

                    <b>{predict_age} 사고 예측 결과</b>

                    <br><br>

                    마지막 실제 데이터는
                    <b>
                        {last_year}년 {current_last:,}건
                    </b>
                    입니다.

                    <br>

                    선형 추세 분석 결과
                    <b>
                        {last_year + horizon}년
                    </b>
                    예상 사고 건수는 약
                    <b>
                        {predicted_last:,}건
                    </b>
                    입니다.

                    <br>

                    마지막 실제 연도 대비
                    약
                    <b>
                        {prediction_change:+,}건
                    </b>,
                    <b>
                        {prediction_change_rate:+.1f}%
                    </b>
                    변화할 것으로 추정됩니다.

                    <br><br>

                    ※ 본 결과는 과거 사고 건수의 선형적인 추세를
                    기반으로 계산한 참고용 예측입니다.
                    정책 변화, 인구구조, 면허소지자 수,
                    교통환경 등의 외부 변수는 반영하지 않습니다.

                </div>
                """
            )


    # ========================================================
    # 5. MODEL COMPARISON
    # ========================================================

    with st.container(
        key="model_compare_panel"
    ):

        st.html(
            """
            <div class="panel-title">
                시계열 예측 모델 비교
            </div>

            <div class="panel-sub">
                연령대별 교통사고 예측에 활용할 수 있는 주요 모델의
                특징과 현재 데이터에 대한 적합성을 비교합니다.
            </div>
            """
        )


        model_table_html = """
        <div class="model-table-wrap">

            <table class="model-table">

                <thead>

                    <tr>

                        <th>
                            예측 모델
                        </th>

                        <th>
                            현재 적용
                        </th>

                        <th>
                            주요 특징
                        </th>

                        <th>
                            필요 데이터
                        </th>

                        <th>
                            계절성
                        </th>

                        <th>
                            현재 적합성
                        </th>

                        <th>
                            비고
                        </th>

                    </tr>

                </thead>


                <tbody>

                    <tr>

                        <td class="model-name">
                            Linear Trend
                        </td>

                        <td>
                            <span class="apply-badge apply-on">
                                ✓ 적용
                            </span>
                        </td>

                        <td>
                            연도와 사고 건수 사이의
                            직선적인 증가·감소 추세를 추정
                        </td>

                        <td>
                            적은 데이터도 가능
                        </td>

                        <td>
                            반영하지 않음
                        </td>

                        <td class="fit-high">
                            높음
                        </td>

                        <td>
                            현재 5개 연도 데이터에서
                            구조가 단순하고 결과 해석이 쉬움
                        </td>

                    </tr>


                    <tr>

                        <td class="model-name">
                            ARIMA
                        </td>

                        <td>
                            <span class="apply-badge apply-off">
                                미적용
                            </span>
                        </td>

                        <td>
                            과거 관측값과 예측 오차를 활용하여
                            다음 시점의 값을 예측
                        </td>

                        <td>
                            충분한 연속 시계열
                        </td>

                        <td>
                            기본적으로 반영하지 않음
                        </td>

                        <td class="fit-low">
                            낮음
                        </td>

                        <td>
                            연도 데이터가 더 누적되면
                            적용을 검토할 수 있음
                        </td>

                    </tr>


                    <tr>

                        <td class="model-name">
                            SARIMA
                        </td>

                        <td>
                            <span class="apply-badge apply-off">
                                미적용
                            </span>
                        </td>

                        <td>
                            ARIMA에 반복되는 계절 패턴을
                            추가한 시계열 모델
                        </td>

                        <td>
                            긴 계절성 시계열
                        </td>

                        <td>
                            반영 가능
                        </td>

                        <td class="fit-very-low">
                            매우 낮음
                        </td>

                        <td>
                            현재 연간 데이터보다는
                            월별·분기별 사고 데이터에 적합
                        </td>

                    </tr>


                    <tr>

                        <td class="model-name">
                            Prophet
                        </td>

                        <td>
                            <span class="apply-badge apply-off">
                                미적용
                            </span>
                        </td>

                        <td>
                            추세·변화점·계절성을
                            비교적 자동으로 모델링
                        </td>

                        <td>
                            비교적 많은 시계열 데이터
                        </td>

                        <td>
                            반영 가능
                        </td>

                        <td class="fit-low">
                            낮음
                        </td>

                        <td>
                            월별 사고 데이터가 확보되면
                            활용 가치가 높음
                        </td>

                    </tr>

                </tbody>

            </table>

        </div>
        """


        st.html(
            model_table_html
        )


        st.html(
            f"""
            <div class="model-reason-box">

                <div class="model-reason-title">
                    현재 모델 선정 이유
                </div>

                현재 <b>{predict_age}</b> 예측에 사용할 수 있는
                실제 연도 데이터는
                <b>{len(prediction_source)}개</b>입니다.

                <br><br>

                현재 데이터는 관측치가 적기 때문에
                ARIMA·SARIMA·Prophet과 같은 복잡한 시계열 모델을
                적용하더라도 모델의 패턴을 충분히 학습하고
                검증하기 어렵습니다.

                <br>

                따라서 현재 SAFER에서는
                <b>Linear Trend Regression</b>을
                기본 예측 모델로 사용합니다.

                <br><br>

                향후 연도별 데이터가 충분히 축적되거나
                월별 교통사고 데이터가 확보되면,
                ARIMA·SARIMA·Prophet을 실제로 학습한 뒤
                <b>MAE / RMSE 등의 성능 지표를 기준으로
                모델 성능을 비교</b>할 수 있습니다.

            </div>
            """
        )


    # ========================================================
    # DETAIL
    # ========================================================

    st.write("")


    with st.expander(
        "연령별 교통사고 데이터 상세 보기"
    ):

        tab1, tab2 = st.tabs(
            [
                "연령대별 교통사고",
                "가해운전자 연령대별 사고",
            ]
        )


        # ====================================================
        # AGE DETAIL
        # ====================================================

        with tab1:

            detail_age = (
                age_df
                .sort_values(
                    [
                        "year",
                        "age_group",
                    ],
                    ascending=[
                        False,
                        True,
                    ]
                )
                .copy()
            )


            detail_age.columns = [
                "연도",
                "연령대",
                "사고건수",
            ]


            detail_age[
                "사고건수"
            ] = (
                detail_age[
                    "사고건수"
                ]
                .round()
                .astype(int)
            )


            st.dataframe(

                detail_age,

                use_container_width=True,

                hide_index=True,

                column_config={

                    "연도":
                        st.column_config.NumberColumn(
                            "연도",
                            format="%d년"
                        ),

                    "연령대":
                        st.column_config.TextColumn(
                            "연령대"
                        ),

                    "사고건수":
                        st.column_config.NumberColumn(
                            "사고건수",
                            format="%d건"
                        ),
                }
            )


        # ====================================================
        # DRIVER DETAIL
        # ====================================================

        with tab2:

            detail_driver = (
                driver_long
                .sort_values(
                    [
                        "year",
                        "age_group",
                    ],
                    ascending=[
                        False,
                        True,
                    ]
                )
                .copy()
            )


            detail_driver.columns = [
                "연도",
                "연령대",
                "사고건수",
            ]


            detail_driver[
                "사고건수"
            ] = (
                detail_driver[
                    "사고건수"
                ]
                .round()
                .astype(int)
            )


            st.dataframe(

                detail_driver,

                use_container_width=True,

                hide_index=True,

                column_config={

                    "연도":
                        st.column_config.NumberColumn(
                            "연도",
                            format="%d년"
                        ),

                    "연령대":
                        st.column_config.TextColumn(
                            "연령대"
                        ),

                    "사고건수":
                        st.column_config.NumberColumn(
                            "사고건수",
                            format="%d건"
                        ),
                }
            )