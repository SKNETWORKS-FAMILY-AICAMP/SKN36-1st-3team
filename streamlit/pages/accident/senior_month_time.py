import sys
import re
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sqlalchemy import text


# ============================================================
# PROJECT ROOT
# SAFE/streamlit/pages/accident/senior_month_time.py
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[3]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


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
def load_senior_month_time():

    engine = get_engine()

    query = text(
        """
        SELECT
            id,
            year,
            month,
            time_slot,
            accidents
        FROM senior_accident_month_time
        ORDER BY year, month, time_slot
        """
    )

    with engine.connect() as conn:
        return pd.read_sql(
            query,
            conn
        )


# ============================================================
# LOAD
# ============================================================

try:

    df = load_senior_month_time()

except Exception as e:

    st.error(
        f"MySQL 데이터 조회 실패\n\n{e}"
    )

    st.stop()


# ============================================================
# CLEAN
# ============================================================

df["year"] = pd.to_numeric(
    df["year"],
    errors="coerce"
)

df["month"] = pd.to_numeric(
    df["month"],
    errors="coerce"
)

df["accidents"] = pd.to_numeric(
    df["accidents"],
    errors="coerce"
).fillna(0)

df["time_slot"] = (
    df["time_slot"]
    .fillna("")
    .astype(str)
    .str.strip()
)


df = df[
    df["year"].notna()
    &
    df["month"].notna()
].copy()


df["year"] = (
    df["year"]
    .astype(int)
)

df["month"] = (
    df["month"]
    .astype(int)
)


df = df[
    (df["month"] >= 1)
    &
    (df["month"] <= 12)
].copy()


# ============================================================
# INVALID
# ============================================================

INVALID_TIME = [
    "",
    "계",
    "합계",
    "총계",
    "전체",
]


df = df[
    ~df["time_slot"].isin(
        INVALID_TIME
    )
].copy()


# ============================================================
# TIME NORMALIZE
# ============================================================

TIME_REPLACE = {

    "00~02": "00~02시",
    "00~02시": "00~02시",
    "0~2시": "00~02시",

    "02~04": "02~04시",
    "02~04시": "02~04시",

    "04~06": "04~06시",
    "04~06시": "04~06시",

    "06~08": "06~08시",
    "06~08시": "06~08시",

    "08~10": "08~10시",
    "08~10시": "08~10시",

    "10~12": "10~12시",
    "10~12시": "10~12시",

    "12~14": "12~14시",
    "12~14시": "12~14시",

    "14~16": "14~16시",
    "14~16시": "14~16시",

    "16~18": "16~18시",
    "16~18시": "16~18시",

    "18~20": "18~20시",
    "18~20시": "18~20시",

    "20~22": "20~22시",
    "20~22시": "20~22시",

    "22~24": "22~24시",
    "22~24시": "22~24시",
}


TIME_ORDER = [
    "00~02시",
    "02~04시",
    "04~06시",
    "06~08시",
    "08~10시",
    "10~12시",
    "12~14시",
    "14~16시",
    "16~18시",
    "18~20시",
    "20~22시",
    "22~24시",
]


def normalize_time(value):

    value = str(value).strip()

    # 먼저 기존 매핑 확인
    if value in TIME_REPLACE:

        return TIME_REPLACE[
            value
        ]


    # --------------------------------------------------------
    # "0시~2시", "00시~02시", "0~2시", "00~02"
    # 같은 다양한 시간대 표기를 모두 "00~02시" 형태로 통일
    # --------------------------------------------------------

    numbers = re.findall(
        r"\d+",
        value
    )


    if len(numbers) >= 2:

        start_hour = int(
            numbers[0]
        )

        end_hour = int(
            numbers[1]
        )


        normalized = (
            f"{start_hour:02d}"
            f"~"
            f"{end_hour:02d}시"
        )


        if normalized in TIME_ORDER:

            return normalized


    return value


df["time_slot"] = (
    df["time_slot"]
    .apply(normalize_time)
)


# ============================================================
# DATE
# ============================================================

df["date"] = pd.to_datetime(
    dict(
        year=df["year"],
        month=df["month"],
        day=1
    )
)


# ============================================================
# GROUP DUPLICATES
# ============================================================

df = (
    df
    .groupby(
        [
            "date",
            "year",
            "month",
            "time_slot",
        ],
        as_index=False
    )["accidents"]
    .sum()
)


# ============================================================
# OPTIONS
# ============================================================

years = sorted(
    df["year"]
    .unique()
    .tolist(),
    reverse=True
)


time_slots = sorted(
    df["time_slot"]
    .dropna()
    .unique()
    .tolist(),
    key=lambda x: (
        TIME_ORDER.index(x)
        if x in TIME_ORDER
        else 999
    )
)


if not years:

    st.warning(
        "고령운전자 월별·시간대 사고 데이터가 없습니다."
    )

    st.stop()


# ============================================================
# CSS
# ============================================================

st.html(
    """
<style>

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

    border-radius:
        16px;

    padding:
        10px 20px;

    margin-bottom:
        20px;
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
}


/* ==========================================================
   PAGE
========================================================== */

.st-key-senior_month_time_page {

    background:
        #101625;

    border:
        1px solid
        #34405A;

    border-radius:
        20px;

    padding:
        34px 36px 44px 36px;
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
   INPUT
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
}


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
}


/* ==========================================================
   PANEL
========================================================== */

.st-key-month_panel,
.st-key-time_panel,
.st-key-heatmap_panel,
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
   ANALYSIS
========================================================== */

.analysis-box,
.model-box {

    background:
        #121A2B;

    border:
        1px solid
        #35415C;

    border-left:
        4px solid
        #D6A348;

    border-radius:
        7px 15px 15px 7px;

    padding:
        20px 22px;

    margin-top:
        18px;

    color:
        #E5EAF2;

    font-size:
        13px;

    line-height:
        1.95;
}


.analysis-title,
.model-title {

    color:
        #F3C867;

    font-size:
        16px;

    font-weight:
        900;

    margin-bottom:
        10px;
}


.analysis-box b,
.model-box b {

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
        1050px;

    font-size:
        13px;
}


.model-table th {

    background:
        #202A42;

    color:
        #FFFFFF;

    padding:
        15px 14px;

    text-align:
        left;

    font-weight:
        800;

    border-bottom:
        1px solid
        #46516B;
}


.model-table td {

    padding:
        15px 14px;

    color:
        #DDE3EC;

    border-bottom:
        1px solid
        #2E3951;

    line-height:
        1.55;
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
        rgba(121,197,162,.15);

    color:
        #8ED6B3 !important;

    border:
        1px solid
        rgba(121,197,162,.38);
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


.fit-medium {

    color:
        #E7BE69 !important;

    font-weight:
        900;
}


/* ==========================================================
   PLOT TEXT
========================================================== */

.js-plotly-plot .plotly .legendtext,
.js-plotly-plot .plotly .xtick text,
.js-plotly-plot .plotly .ytick text,
.js-plotly-plot .plotly .annotation-text {

    fill:
        #E8EDF5 !important;
}

/* ==========================================================
   ANALYSIS / PREDICTION SECTION TITLES
========================================================== */

.section-heading {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 32px 0 14px 4px;
    color: #FFFFFF;
    font-size: 25px;
    font-weight: 900;
    letter-spacing: -1px;
}

.section-heading::before {
    content: "";
    width: 5px;
    height: 27px;
    border-radius: 4px;
    background: #D9A64A;
}



/* ==========================================================
   ANALYSIS / PREDICTION DIVIDER
========================================================== */

.section-divider {

    height: 1px;

    margin: 46px 0 8px 0;

    background:
        linear-gradient(
            90deg,
            rgba(217,166,74,0),
            rgba(217,166,74,.95) 18%,
            rgba(85,101,134,.9) 82%,
            rgba(85,101,134,0)
        );
}


/* ==========================================================
   DETAIL TOGGLE BUTTON
========================================================== */

.st-key-senior_month_detail_toggle button {

    width: 100% !important;

    min-height: 52px !important;

    background: #182035 !important;

    color: #E7EAF0 !important;

    border: 1px solid #394560 !important;

    border-radius: 14px !important;

    box-shadow: none !important;

    justify-content: flex-start !important;

    padding-left: 18px !important;

    font-size: 14px !important;

    font-weight: 800 !important;
}


.st-key-senior_month_detail_toggle button * {

    color: #E7EAF0 !important;

    -webkit-text-fill-color: #E7EAF0 !important;

    opacity: 1 !important;
}


.st-key-senior_month_detail_toggle button:hover {

    background: #202A42 !important;

    border-color: #D6A348 !important;

    color: #F1C66A !important;
}


.st-key-senior_month_detail_toggle button:hover * {

    color: #F1C66A !important;

    -webkit-text-fill-color: #F1C66A !important;
}


/* ==========================================================
   DETAIL TABLE PANEL
========================================================== */

.st-key-senior_month_detail_panel {

    background: #182035;

    border: 1px solid #394560;

    border-radius: 14px;

    padding: 18px 18px 20px 18px;

    margin-top: 10px;
}


</style>
"""
)


# ============================================================
# NAV
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
        vertical_alignment="center"
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
    key="senior_month_time_page"
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
                교통사고 &gt; 고령운전자 월별·시간대 사고
            </div>

            <div class="page-title">
                고령운전자 월별·시간대 교통사고 분석
            </div>

            <div class="page-sub">
                고령운전자 교통사고의 월별 변화와 시간대별 집중도를 분석하고,
                월 단위 시계열 데이터를 이용해 향후 사고 규모를 예측합니다.
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
            key="senior_month_year"
        )


    with f2:

        selected_time = st.selectbox(
            "시간대",
            [
                "전체"
            ] + time_slots,
            key="senior_month_time"
        )


    # ========================================================
    # YEAR DATA
    # ========================================================

    year_df = (
        df[
            df[
                "year"
            ] == selected_year
        ]
        .copy()
    )


    # ========================================================
    # MONTH TOTAL
    # ========================================================

    month_df = (
        year_df
        .groupby(
            "month",
            as_index=False
        )["accidents"]
        .sum()
        .sort_values(
            "month"
        )
    )


    # ========================================================
    # TIME TOTAL
    # ========================================================

    time_df = (
        year_df
        .groupby(
            "time_slot",
            as_index=False
        )["accidents"]
        .sum()
        .sort_values(
            "accidents",
            ascending=False
        )
    )


    # ========================================================
    # KPI
    # ========================================================

    total_accidents = int(
        year_df[
            "accidents"
        ].sum()
    )


    if not month_df.empty:

        top_month_row = (
            month_df
            .sort_values(
                "accidents",
                ascending=False
            )
            .iloc[0]
        )

        top_month = int(
            top_month_row[
                "month"
            ]
        )

        top_month_accidents = int(
            top_month_row[
                "accidents"
            ]
        )

    else:

        top_month = 0
        top_month_accidents = 0


    if not time_df.empty:

        top_time = str(
            time_df.iloc[0][
                "time_slot"
            ]
        )

        top_time_accidents = int(
            time_df.iloc[0][
                "accidents"
            ]
        )

    else:

        top_time = "-"
        top_time_accidents = 0


    if selected_time == "전체":

        selected_time_total = (
            total_accidents
        )

        selected_time_share = (
            100.0
        )

    else:

        selected_time_total = int(
            year_df[
                year_df[
                    "time_slot"
                ] == selected_time
            ][
                "accidents"
            ].sum()
        )


        selected_time_share = (
            selected_time_total
            / total_accidents
            * 100
            if total_accidents > 0
            else 0
        )


    # ========================================================
    # KPI CARD
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
                    {selected_year}년 고령운전자 사고
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
                    사고 최다 월
                </div>

                <div class="kpi-value">
                    {top_month}월
                </div>

            </div>
            """
        )


    with k3:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    사고 최다 시간대
                </div>

                <div class="kpi-value">
                    {top_time}
                </div>

            </div>
            """
        )


    with k4:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    {
                        "전체 사고"
                        if selected_time == "전체"
                        else f"{selected_time} 사고 비중"
                    }
                </div>

                <div class="kpi-value">
                    {
                        f"{selected_time_total:,}건"
                        if selected_time == "전체"
                        else f"{selected_time_share:.1f}%"
                    }
                </div>

            </div>
            """
        )


    st.html(
        """
        <div class="section-heading">분석</div>
        """
    )


    # ========================================================
    # MONTH + TIME
    # ========================================================

    left, right = st.columns(
        [
            1,
            1,
        ],
        gap="medium"
    )


    # ========================================================
    # MONTH CHART
    # ========================================================

    with left:

        with st.container(
            key="month_panel"
        ):

            st.html(
                f"""
                <div class="panel-title">
                    {selected_year}년 월별 사고 현황
                </div>

                <div class="panel-sub">
                    고령운전자 사고 발생 규모를 월별로 비교합니다.
                </div>
                """
            )


            max_month = (
                float(
                    month_df[
                        "accidents"
                    ].max()
                )
                if not month_df.empty
                else 1
            )


            if max_month <= 0:
                max_month = 1


            fig_month = go.Figure(
                go.Bar(

                    x=[
                        f"{month}월"
                        for month
                        in month_df[
                            "month"
                        ]
                    ],

                    y=month_df[
                        "accidents"
                    ],

                    marker_color=[
                        "#D9A64A"
                        if month == top_month
                        else "#79B69B"

                        for month
                        in month_df[
                            "month"
                        ]
                    ],

                    text=[
                        f"{int(v):,}"
                        for v
                        in month_df[
                            "accidents"
                        ]
                    ],

                    textposition="outside",

                    cliponaxis=False,

                    hovertemplate=(
                        "<b>%{x}</b>"
                        "<br>"
                        "사고: %{y:,}건"
                        "<extra></extra>"
                    ),
                )
            )


            fig_month.update_layout(

                height=500,

                margin=dict(
                    l=70,
                    r=40,
                    t=40,
                    b=65
                ),

                paper_bgcolor="#182035",

                plot_bgcolor="#182035",

                showlegend=False,

                font=dict(
                    color="#E8EDF5"
                ),

                xaxis=dict(
                    title="월",
                    showgrid=False
                ),

                yaxis=dict(
                    title="교통사고 건수(건)",
                    gridcolor="#35405A",
                    range=[
                        0,
                        max_month * 1.15
                    ]
                )
            )


            st.plotly_chart(
                fig_month,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )


    # ========================================================
    # TIME CHART
    # ========================================================

    with right:

        with st.container(
            key="time_panel"
        ):

            st.html(
                f"""
                <div class="panel-title">
                    {selected_year}년 시간대별 사고 현황
                </div>

                <div class="panel-sub">
                    고령운전자 사고 발생이 집중되는 시간대를 비교합니다.
                </div>
                """
            )


            time_plot_df = (
                time_df
                .sort_values(
                    "accidents",
                    ascending=True
                )
                .copy()
            )


            max_time = (
                float(
                    time_plot_df[
                        "accidents"
                    ].max()
                )
                if not time_plot_df.empty
                else 1
            )


            if max_time <= 0:
                max_time = 1


            fig_time = go.Figure(
                go.Bar(

                    x=time_plot_df[
                        "accidents"
                    ],

                    y=time_plot_df[
                        "time_slot"
                    ],

                    orientation="h",

                    marker_color=[
                        "#D9A64A"
                        if time == top_time
                        else "#79B69B"

                        for time
                        in time_plot_df[
                            "time_slot"
                        ]
                    ],

                    text=[
                        f"{int(v):,}건"
                        for v
                        in time_plot_df[
                            "accidents"
                        ]
                    ],

                    textposition="outside",

                    cliponaxis=False,

                    hovertemplate=(
                        "<b>%{y}</b>"
                        "<br>"
                        "사고: %{x:,}건"
                        "<extra></extra>"
                    ),
                )
            )


            fig_time.update_layout(

                height=500,

                margin=dict(
                    l=90,
                    r=100,
                    t=40,
                    b=65
                ),

                paper_bgcolor="#182035",

                plot_bgcolor="#182035",

                showlegend=False,

                font=dict(
                    color="#E8EDF5"
                ),

                xaxis=dict(
                    title="교통사고 건수(건)",
                    gridcolor="#35405A",
                    range=[
                        0,
                        max_time * 1.25
                    ]
                ),

                yaxis=dict(
                    title=None
                )
            )


            st.plotly_chart(
                fig_time,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )


    # ========================================================
    # HEATMAP
    # ========================================================

    with st.container(
        key="heatmap_panel"
    ):

        st.html(
            f"""
            <div class="panel-title">
                {selected_year}년 월 × 시간대 사고 집중도
            </div>

            <div class="panel-sub">
                색상이 밝고 붉을수록 해당 월과 시간대에서
                고령운전자 사고가 많이 발생한 구간입니다.
            </div>
            """
        )


        heat_df = (
            year_df
            .pivot_table(
                index="time_slot",
                columns="month",
                values="accidents",
                aggfunc="sum",
                fill_value=0
            )
        )


        ordered_time = [
            time
            for time in TIME_ORDER
            if time in heat_df.index
        ]


        extra_time = [
            time
            for time in heat_df.index
            if time not in TIME_ORDER
        ]


        heat_df = heat_df.reindex(
            ordered_time + extra_time
        )


        heat_df = heat_df.reindex(
            columns=range(1, 13),
            fill_value=0
        )


        fig_heat = go.Figure(
            go.Heatmap(

                z=heat_df.values,

                x=[
                    f"{month}월"
                    for month
                    in heat_df.columns
                ],

                y=heat_df.index,

                colorscale=[
                    [0.00, "#10233A"],
                    [0.15, "#174C6A"],
                    [0.30, "#1F7A7A"],
                    [0.45, "#49A078"],
                    [0.60, "#A3B95D"],
                    [0.75, "#D5B33F"],
                    [0.88, "#E8793E"],
                    [1.00, "#D94A3A"],
                ],

                colorbar=dict(

                    title=dict(
                        text="사고 건수",
                        font=dict(
                            color="#FFFFFF"
                        )
                    ),

                    tickfont=dict(
                        color="#FFFFFF"
                    )
                ),

                hovertemplate=(
                    "<b>%{x}</b>"
                    "<br>"
                    "%{y}"
                    "<br>"
                    "사고: %{z:,}건"
                    "<extra></extra>"
                )
            )
        )


        fig_heat.update_layout(

            height=620,

            margin=dict(
                l=100,
                r=80,
                t=40,
                b=70
            ),

            paper_bgcolor="#182035",

            plot_bgcolor="#182035",

            font=dict(
                color="#E8EDF5"
            ),

            xaxis=dict(
                title="월"
            ),

            yaxis=dict(
                title="시간대"
            )
        )


        st.plotly_chart(
            fig_heat,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


    # ========================================================
    # AUTO ANALYSIS
    # ========================================================

    annual_month_avg = (
        total_accidents / 12
        if total_accidents > 0
        else 0
    )


    peak_month_share = (
        top_month_accidents
        / total_accidents
        * 100
        if total_accidents > 0
        else 0
    )


    peak_time_share = (
        top_time_accidents
        / total_accidents
        * 100
        if total_accidents > 0
        else 0
    )


    st.html(
        f"""
        <div class="analysis-box">

            <div class="analysis-title">
                {selected_year}년 고령운전자 사고 분석
            </div>

            {selected_year}년 고령운전자 사고는
            총 <b>{total_accidents:,}건</b>입니다.

            <br>

            월 평균 사고는 약
            <b>{annual_month_avg:,.0f}건</b>입니다.

            <br>

            사고가 가장 많이 발생한 달은
            <b>{top_month}월</b>로
            <b>{top_month_accidents:,}건</b>이며,
            연간 사고의 약
            <b>{peak_month_share:.1f}%</b>를 차지합니다.

            <br>

            사고가 가장 많이 발생한 시간대는
            <b>{top_time}</b>로
            <b>{top_time_accidents:,}건</b>이며,
            전체 사고의 약
            <b>{peak_time_share:.1f}%</b>입니다.

        </div>
        """
    )


    st.html(
        """
        <div class="section-divider"></div>
        <div class="section-heading">예측</div>
        """
    )


    # ========================================================
    # FUTURE PREDICTION
    # ========================================================

    with st.container(
        key="predict_panel"
    ):

        st.html(
            """
            <div class="panel-title">
                고령운전자 사고 미래 예측
            </div>

            <div class="panel-sub">
                월별 시계열 데이터를 기반으로 향후 사고 건수를 예측합니다.
                <br>
                <b>전체 시간대</b>는 안정적인
                <b>Linear Trend Regression</b>을 적용하고,
                <b>개별 시간대</b>는 데이터가 충분하고 모델이 안정적인 경우
                <b>SARIMA</b>를 적용합니다.
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

            predict_time = st.selectbox(
                "예측 시간대",
                [
                    "전체"
                ] + time_slots,
                key="senior_prediction_time"
            )


        with p2:

            predict_period = st.radio(
                "예측 기간",
                [
                    "1년",
                    "5년",
                    "10년"
                ],
                horizontal=True,
                key="senior_prediction_period"
            )


        horizon_years = {
            "1년": 1,
            "5년": 5,
            "10년": 10
        }[
            predict_period
        ]


        horizon_months = (
            horizon_years * 12
        )


        # ====================================================
        # PREDICTION SOURCE
        # ====================================================

        if predict_time == "전체":

            prediction_source = (
                df
                .groupby(
                    "date",
                    as_index=False
                )["accidents"]
                .sum()
                .sort_values(
                    "date"
                )
            )

        else:

            prediction_source = (
                df[
                    df[
                        "time_slot"
                    ] == predict_time
                ]
                .groupby(
                    "date",
                    as_index=False
                )["accidents"]
                .sum()
                .sort_values(
                    "date"
                )
            )


        # ====================================================
        # MONTH FILL
        # ====================================================

        if not prediction_source.empty:

            prediction_source = (
                prediction_source
                .set_index(
                    "date"
                )
                .asfreq(
                    "MS"
                )
            )


            prediction_source[
                "accidents"
            ] = (
                prediction_source[
                    "accidents"
                ]
                .interpolate(
                    method="linear"
                )
                .ffill()
                .bfill()
            )


            prediction_source = (
                prediction_source
                .reset_index()
            )


        # ====================================================
        # PREDICTION
        # ====================================================

        if len(prediction_source) < 2:

            st.warning(
                "미래 예측을 수행할 데이터가 부족합니다."
            )

        else:

            actual_dates = (
                prediction_source[
                    "date"
                ]
            )


            actual_values = (
                prediction_source[
                    "accidents"
                ]
                .to_numpy(
                    dtype=float
                )
            )


            future_dates = pd.date_range(
                start=(
                    actual_dates.max()
                    + pd.offsets.MonthBegin(1)
                ),
                periods=horizon_months,
                freq="MS"
            )


            model_name = (
                "Linear Trend Regression"
            )


            model_reason = (
                "전체 시간대 집계 데이터에는 "
                "안정적인 선형 추세 분석을 적용했습니다."
            )


            future_values = None
            lower_values = None
            upper_values = None

            sarima_used = False
            sarima_fallback = False


            # =================================================
            # SARIMA
            # 전체에서는 사용하지 않음
            # 개별 시간대 + 최소 36개월
            # =================================================

            if (
                predict_time != "전체"
                and len(prediction_source) >= 36
            ):

                try:

                    from statsmodels.tsa.statespace.sarimax import SARIMAX


                    series = (
                        prediction_source
                        .set_index(
                            "date"
                        )[
                            "accidents"
                        ]
                    )


                    # 너무 복잡한 SARIMA 대신
                    # 조금 더 안정적인 단순 모델
                    sarima_model = SARIMAX(

                        series,

                        order=(
                            1,
                            1,
                            0
                        ),

                        seasonal_order=(
                            1,
                            0,
                            0,
                            12
                        ),

                        enforce_stationarity=False,

                        enforce_invertibility=False
                    )


                    sarima_result = (
                        sarima_model
                        .fit(
                            disp=False,
                            maxiter=200
                        )
                    )


                    forecast_result = (
                        sarima_result
                        .get_forecast(
                            steps=horizon_months
                        )
                    )


                    candidate_future = (
                        forecast_result
                        .predicted_mean
                        .to_numpy(
                            dtype=float
                        )
                    )


                    confidence = (
                        forecast_result
                        .conf_int(
                            alpha=0.05
                        )
                    )


                    candidate_lower = (
                        confidence.iloc[:, 0]
                        .to_numpy(
                            dtype=float
                        )
                    )


                    candidate_upper = (
                        confidence.iloc[:, 1]
                        .to_numpy(
                            dtype=float
                        )
                    )


                    # =================================================
                    # SARIMA SAFETY CHECK
                    # =================================================

                    actual_max = max(
                        float(
                            np.nanmax(
                                actual_values
                            )
                        ),
                        1.0
                    )


                    actual_mean = max(
                        float(
                            np.nanmean(
                                actual_values
                            )
                        ),
                        1.0
                    )


                    future_is_valid = (
                        np.all(
                            np.isfinite(
                                candidate_future
                            )
                        )
                        and
                        np.all(
                            np.isfinite(
                                candidate_lower
                            )
                        )
                        and
                        np.all(
                            np.isfinite(
                                candidate_upper
                            )
                        )
                    )


                    if future_is_valid:

                        upper_max = float(
                            np.nanmax(
                                candidate_upper
                            )
                        )


                        prediction_max = float(
                            np.nanmax(
                                np.abs(
                                    candidate_future
                                )
                            )
                        )


                        confidence_width = float(
                            np.nanmax(
                                candidate_upper
                                - candidate_lower
                            )
                        )


                        # -----------------------------------------
                        # 폭발 판정
                        #
                        # 1. 신뢰구간이 실제 최대값의 8배 초과
                        # 2. 예측값이 실제 최대값의 5배 초과
                        # 3. 신뢰구간 폭이 실제 평균의 10배 초과
                        # -----------------------------------------

                        unstable = (
                            upper_max
                            > actual_max * 8

                            or prediction_max
                            > actual_max * 5

                            or confidence_width
                            > actual_mean * 10
                        )

                    else:

                        unstable = True


                    if unstable:

                        future_values = None
                        lower_values = None
                        upper_values = None

                        sarima_fallback = True

                    else:

                        future_values = (
                            candidate_future
                        )

                        lower_values = (
                            candidate_lower
                        )

                        upper_values = (
                            candidate_upper
                        )

                        model_name = (
                            "SARIMA (1,1,0)(1,0,0,12)"
                        )

                        model_reason = (
                            "개별 시간대 월별 데이터가 충분하고 "
                            "SARIMA 예측 및 신뢰구간이 안정적으로 계산되어 "
                            "12개월 계절성을 고려한 SARIMA를 적용했습니다."
                        )

                        sarima_used = True


                except Exception:

                    future_values = None
                    lower_values = None
                    upper_values = None

                    sarima_fallback = True


            # =================================================
            # LINEAR TREND FALLBACK
            # =================================================

            if future_values is None:

                x = np.arange(
                    len(
                        actual_values
                    ),
                    dtype=float
                )


                slope, intercept = (
                    np.polyfit(
                        x,
                        actual_values,
                        1
                    )
                )


                fitted_values = (
                    slope * x
                    + intercept
                )


                future_x = np.arange(
                    len(
                        actual_values
                    ),
                    len(
                        actual_values
                    ) + horizon_months,
                    dtype=float
                )


                future_values = (
                    slope
                    * future_x
                    + intercept
                )


                # =================================================
                # LINEAR METRICS
                # =================================================

                residuals = (
                    actual_values
                    - fitted_values
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
                            actual_values
                            - np.mean(
                                actual_values
                            )
                        ) ** 2
                    )
                )


                r2 = (
                    1
                    - ss_res / ss_tot
                    if ss_tot > 0
                    else 0
                )


                model_name = (
                    "Linear Trend Regression"
                )


                if predict_time == "전체":

                    model_reason = (
                        "전체 시간대 사고는 여러 시간대가 합산된 시계열이므로 "
                        "현재 데이터 규모에서는 Linear Trend를 사용해 "
                        "안정적인 장기 추세를 예측합니다."
                    )

                elif sarima_fallback:

                    model_reason = (
                        "SARIMA를 시도했으나 예측값 또는 신뢰구간이 "
                        "비정상적으로 커지거나 모델 학습이 안정적이지 않아 "
                        "Linear Trend Regression으로 자동 전환했습니다."
                    )

                else:

                    model_reason = (
                        "현재 시간대 데이터가 SARIMA를 안정적으로 학습하기에 "
                        "충분하지 않아 Linear Trend Regression을 적용했습니다."
                    )


            # =================================================
            # NON NEGATIVE
            # =================================================

            future_values = np.maximum(
                future_values,
                0
            )


            if lower_values is not None:

                lower_values = np.maximum(
                    lower_values,
                    0
                )


            if upper_values is not None:

                upper_values = np.maximum(
                    upper_values,
                    0
                )


            # =================================================
            # Y AXIS SAFETY
            # =================================================

            actual_max = max(
                float(
                    np.nanmax(
                        actual_values
                    )
                ),
                1
            )


            forecast_max = max(
                float(
                    np.nanmax(
                        future_values
                    )
                ),
                1
            )


            y_max = max(
                actual_max,
                forecast_max
            )


            if upper_values is not None:

                confidence_max = float(
                    np.nanmax(
                        upper_values
                    )
                )

                # 마지막 안전장치
                confidence_max = min(
                    confidence_max,
                    y_max * 3
                )

                y_max = max(
                    y_max,
                    confidence_max
                )


            y_axis_max = (
                y_max * 1.18
            )


            # =================================================
            # GRAPH
            # =================================================

            fig_predict = go.Figure()


            # 실제
            fig_predict.add_trace(
                go.Scatter(

                    x=actual_dates,

                    y=actual_values,

                    mode="lines+markers",

                    name="실제 사고",

                    line=dict(
                        color="#A0C9AC",
                        width=3
                    ),

                    marker=dict(
                        size=6,
                        color="#A0C9AC"
                    ),

                    hovertemplate=(
                        "<b>%{x|%Y-%m}</b>"
                        "<br>"
                        "실제 사고: %{y:,.0f}건"
                        "<extra></extra>"
                    )
                )
            )


            # =================================================
            # CONFIDENCE INTERVAL
            # SARIMA 정상일 때만
            # =================================================

            if (
                sarima_used
                and lower_values is not None
                and upper_values is not None
            ):

                safe_upper = np.minimum(
                    upper_values,
                    y_axis_max
                )


                safe_lower = np.minimum(
                    lower_values,
                    safe_upper
                )


                fig_predict.add_trace(
                    go.Scatter(

                        x=future_dates,

                        y=safe_upper,

                        mode="lines",

                        line=dict(
                            width=0
                        ),

                        showlegend=False,

                        hoverinfo="skip"
                    )
                )


                fig_predict.add_trace(
                    go.Scatter(

                        x=future_dates,

                        y=safe_lower,

                        mode="lines",

                        fill="tonexty",

                        fillcolor=(
                            "rgba(221,132,105,0.15)"
                        ),

                        line=dict(
                            width=0
                        ),

                        name="95% 신뢰구간",

                        hoverinfo="skip"
                    )
                )


            # 예측
            prediction_x = [
                actual_dates.iloc[-1]
            ] + list(
                future_dates
            )


            prediction_y = [
                float(
                    actual_values[-1]
                )
            ] + list(
                future_values
            )


            fig_predict.add_trace(
                go.Scatter(

                    x=prediction_x,

                    y=prediction_y,

                    mode="lines+markers",

                    name="예측 사고",

                    line=dict(
                        color="#DD8469",
                        width=3,
                        dash="dash"
                    ),

                    marker=dict(
                        color="#DD8469",
                        size=6
                    ),

                    hovertemplate=(
                        "<b>%{x|%Y-%m}</b>"
                        "<br>"
                        "예측 사고: %{y:,.0f}건"
                        "<extra></extra>"
                    )
                )
            )


            # 예측 시작
            fig_predict.add_vline(

                x=actual_dates.iloc[-1],

                line_dash="dot",

                line_color="#D6A348"
            )


            fig_predict.add_annotation(

                x=actual_dates.iloc[-1],

                y=1,

                yref="paper",

                text="예측 시작",

                showarrow=False,

                yshift=15,

                font=dict(
                    color="#F3C867"
                )
            )


            fig_predict.update_layout(

                height=580,

                margin=dict(
                    l=80,
                    r=60,
                    t=65,
                    b=70
                ),

                paper_bgcolor="#182035",

                plot_bgcolor="#182035",

                font=dict(
                    color="#E8EDF5"
                ),

                hovermode="x unified",

                legend=dict(

                    orientation="h",

                    y=1.05,

                    x=1,

                    xanchor="right",

                    font=dict(
                        color="#FFFFFF"
                    )
                ),

                xaxis=dict(

                    title="월",

                    showgrid=False,
                ),

                yaxis=dict(

                    title="교통사고 건수(건)",

                    gridcolor="#35405A",

                    rangemode="tozero",

                    range=[
                        0,
                        y_axis_max
                    ],

                    tickformat=",",
                )
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

            current_value = int(
                round(
                    actual_values[-1]
                )
            )


            predicted_value = int(
                round(
                    future_values[-1]
                )
            )


            prediction_change = (
                predicted_value
                - current_value
            )


            prediction_rate = (
                prediction_change
                / current_value
                * 100

                if current_value > 0

                else 0
            )


            start_date = (
                prediction_source[
                    "date"
                ].min()
            )


            end_date = (
                prediction_source[
                    "date"
                ].max()
            )


            # =================================================
            # MODEL INFO
            # =================================================

            linear_metric_html = ""


            if model_name == "Linear Trend Regression":

                linear_metric_html = f"""
                    <br>

                    <b>MAE</b> :
                    {mae:,.1f}건

                    <br>

                    <b>RMSE</b> :
                    {rmse:,.1f}건

                    <br>

                    <b>R²</b> :
                    {r2:.3f}
                """


            st.html(
                f"""
                <div class="model-box">

                    <div class="model-title">
                        예측 모델 정보
                    </div>

                    <b>적용 모델</b> :
                    {model_name}

                    <br>

                    <b>예측 대상</b> :
                    {
                        "전체 시간대"
                        if predict_time == "전체"
                        else predict_time
                    }

                    <br>

                    <b>학습 기간</b> :
                    {start_date.strftime("%Y-%m")}
                    ~
                    {end_date.strftime("%Y-%m")}

                    <br>

                    <b>학습 데이터</b> :
                    {len(prediction_source)}개월

                    <br>

                    <b>예측 기간</b> :
                    {predict_period}
                    ({horizon_months}개월)

                    {linear_metric_html}

                    <br><br>

                    <b>모델 선택 이유</b>
                    <br>

                    {model_reason}

                </div>
                """
            )


            # =================================================
            # RESULT SUMMARY
            # =================================================

            st.html(
                f"""
                <div class="analysis-box">

                    <div class="analysis-title">
                        고령운전자 사고 예측 결과
                    </div>

                    현재 마지막 관측값은

                    <b>
                        {end_date.strftime("%Y-%m")}
                        {current_value:,}건
                    </b>
                    입니다.

                    <br>

                    {
                        future_dates[-1]
                        .strftime("%Y-%m")
                    } 예상 사고 건수는
                    약

                    <b>
                        {predicted_value:,}건
                    </b>
                    입니다.

                    <br>

                    마지막 실제 관측값 대비

                    <b>
                        {prediction_change:+,}건
                    </b>,

                    약

                    <b>
                        {prediction_rate:+.1f}%
                    </b>

                    변화할 것으로 예측됩니다.

                    <br><br>

                    ※ 5년·10년과 같은 장기 예측은
                    실제 정책 변화, 고령운전자 규모,
                    교통량 및 도로환경 변화를 반영하지 않으므로
                    추세 참고용으로 해석하는 것이 적절합니다.

                </div>
                """
            )


    # ========================================================
    # MODEL COMPARISON
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
                고령운전자 월별 사고 예측에 활용할 수 있는
                주요 모델의 특성과 현재 데이터 구조에 대한 적합성을 비교합니다.
            </div>
            """
        )


        st.html(
            """
            <div class="model-table-wrap">

                <table class="model-table">

                    <thead>

                        <tr>

                            <th>예측 모델</th>

                            <th>현재 활용</th>

                            <th>주요 특징</th>

                            <th>계절성</th>

                            <th>현재 적합성</th>

                            <th>적용 조건</th>

                        </tr>

                    </thead>


                    <tbody>

                        <tr>

                            <td class="model-name">
                                Linear Trend
                            </td>

                            <td>
                                <span class="apply-badge apply-on">
                                    기본 / Fallback
                                </span>
                            </td>

                            <td>
                                월별 사고의 장기적인
                                증가·감소 추세를 직선으로 추정
                            </td>

                            <td>
                                반영하지 않음
                            </td>

                            <td class="fit-high">
                                높음
                            </td>

                            <td>
                                전체 시간대 또는
                                SARIMA가 불안정한 경우 적용
                            </td>

                        </tr>


                        <tr>

                            <td class="model-name">
                                SARIMA
                            </td>

                            <td>
                                <span class="apply-badge apply-on">
                                    조건부 적용
                                </span>
                            </td>

                            <td>
                                과거 시계열과
                                반복되는 12개월 패턴을 함께 학습
                            </td>

                            <td>
                                12개월 계절성
                            </td>

                            <td class="fit-high">
                                높음
                            </td>

                            <td>
                                개별 시간대 + 36개월 이상 +
                                예측 안정성 검사 통과 시 적용
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
                                자기회귀와 이동평균으로
                                시계열 패턴을 예측
                            </td>

                            <td>
                                기본 미반영
                            </td>

                            <td class="fit-medium">
                                보통
                            </td>

                            <td>
                                월별 계절성이 존재한다면
                                SARIMA가 더 적합
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
                                자동으로 모델링
                            </td>

                            <td>
                                반영 가능
                            </td>

                            <td class="fit-high">
                                높음
                            </td>

                            <td>
                                향후 비교 모델로 추가 가능
                            </td>

                        </tr>

                    </tbody>

                </table>

            </div>
            """
        )


        st.html(
            """
            <div class="analysis-box">

                <div class="analysis-title">
                    모델 적용 기준
                </div>

                <b>전체 시간대</b>는 여러 시간대 사고가 합산된 값이기 때문에
                현재 데이터 규모에서는 장기 추세를 안정적으로 표현하는
                <b>Linear Trend Regression</b>을 사용합니다.

                <br><br>

                <b>개별 시간대</b>는 월별 데이터가 36개월 이상 존재하는 경우
                12개월 계절성을 고려한 <b>SARIMA</b>를 우선 시도합니다.

                <br>

                단, SARIMA의 예측값이나 95% 신뢰구간이
                실제 데이터 범위에 비해 비정상적으로 커지는 경우에는
                결과를 사용하지 않고 자동으로
                <b>Linear Trend Regression</b>으로 전환합니다.

            </div>
            """
        )


    # ========================================================
    # DETAIL
    # ========================================================

    st.write("")


    # --------------------------------------------------------
    # DETAIL STATE
    # --------------------------------------------------------

    if "show_senior_month_detail" not in st.session_state:

        st.session_state[
            "show_senior_month_detail"
        ] = False


    # --------------------------------------------------------
    # DETAIL TOGGLE
    # --------------------------------------------------------

    with st.container(
        key="senior_month_detail_toggle"
    ):

        detail_open = st.session_state[
            "show_senior_month_detail"
        ]


        detail_button_label = (
            "▲ 연령별 교통사고 데이터 닫기"
            if detail_open
            else "▼ 연령별 교통사고 데이터 상세 보기"
        )


        if st.button(
            detail_button_label,
            key="senior_month_detail_button",
            use_container_width=True
        ):

            st.session_state[
                "show_senior_month_detail"
            ] = (
                not detail_open
            )

            st.rerun()


    # --------------------------------------------------------
    # DETAIL CONTENT
    # --------------------------------------------------------

    if st.session_state[
        "show_senior_month_detail"
    ]:

        with st.container(
            key="senior_month_detail_panel"
        ):

            detail_df = (
                df[
                    [
                        "year",
                        "month",
                        "time_slot",
                        "accidents",
                    ]
                ]
                .copy()
                .sort_values(
                    [
                        "year",
                        "month",
                        "time_slot",
                    ],
                    ascending=[
                        False,
                        True,
                        True,
                    ]
                )
                .reset_index(
                    drop=True
                )
            )


            detail_df.columns = [
                "연도",
                "월",
                "시간대",
                "사고건수",
            ]


            detail_df[
                "연도"
            ] = (
                detail_df[
                    "연도"
                ]
                .astype(int)
                .astype(str)
                + "년"
            )


            detail_df[
                "월"
            ] = (
                detail_df[
                    "월"
                ]
                .astype(int)
                .astype(str)
                + "월"
            )


            detail_df[
                "사고건수"
            ] = (
                detail_df[
                    "사고건수"
                ]
                .round()
                .astype(int)
                .map(
                    lambda value:
                        f"{value:,}건"
                )
            )


            table_rows = ""


            for _, row in detail_df.iterrows():

                table_rows += f"""
                    <tr>

                        <td>{row["연도"]}</td>

                        <td>{row["월"]}</td>

                        <td>{row["시간대"]}</td>

                        <td>{row["사고건수"]}</td>

                    </tr>
                """


            st.html(
                f"""
                <style>

                .senior-month-dark-table-wrap {{

                    width: 100%;

                    max-height: 560px;

                    overflow-y: auto;

                    overflow-x: auto;

                    background: #182035;

                    border: 1px solid #3A4662;

                    border-radius: 12px;
                }}


                .senior-month-dark-table {{

                    width: 100%;

                    border-collapse: collapse;

                    background: #182035;

                    color: #E7EAF0;

                    font-size: 13px;
                }}


                .senior-month-dark-table thead {{

                    position: sticky;

                    top: 0;

                    z-index: 2;
                }}


                .senior-month-dark-table th {{

                    background: #202A42;

                    color: #D6A348;

                    font-weight: 900;

                    text-align: center;

                    padding: 14px 16px;

                    border-bottom: 1px solid #4A5670;

                    white-space: nowrap;
                }}


                .senior-month-dark-table td {{

                    background: #182035;

                    color: #E7EAF0;

                    font-weight: 600;

                    text-align: center;

                    padding: 12px 16px;

                    border-bottom: 1px solid #303B55;

                    white-space: nowrap;
                }}


                .senior-month-dark-table tbody tr:nth-child(even) td {{

                    background: #1B243A;
                }}


                .senior-month-dark-table tbody tr:hover td {{

                    background: #222D47;

                    color: #FFFFFF;
                }}


                .senior-month-dark-table tbody tr:last-child td {{

                    border-bottom: none;
                }}

                </style>


                <div class="senior-month-dark-table-wrap">

                    <table class="senior-month-dark-table">

                        <thead>

                            <tr>

                                <th>연도</th>

                                <th>월</th>

                                <th>시간대</th>

                                <th>사고건수</th>

                            </tr>

                        </thead>


                        <tbody>

                            {table_rows}

                        </tbody>

                    </table>

                </div>
                """
            )