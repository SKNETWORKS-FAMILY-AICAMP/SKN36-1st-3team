import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests
import streamlit as st
import plotly.graph_objects as go
from sqlalchemy import text


# ============================================================
# PROJECT ROOT
# SAFE/streamlit/pages/accident/senior_region_month.py
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
def load_senior_region_month():

    engine = get_engine()

    query = text(
        """
        SELECT
            id,
            sido,
            sigungu,
            year,
            month,
            accidents
        FROM senior_accident_region_month
        ORDER BY year, month, sido, sigungu
        """
    )

    with engine.connect() as conn:

        return pd.read_sql(
            query,
            conn
        )


# ============================================================
# GEOJSON
# ============================================================

@st.cache_data(ttl=86400)
def load_korea_geojson():

    url = (
        "https://raw.githubusercontent.com/"
        "southkorea/southkorea-maps/master/"
        "kostat/2018/json/"
        "skorea-provinces-2018-geo.json"
    )

    response = requests.get(
        url,
        timeout=20
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# LOAD
# ============================================================

try:

    df = load_senior_region_month()

except Exception as e:

    st.error(
        f"MySQL 데이터 조회 실패\n\n{e}"
    )

    st.stop()


try:

    korea_geojson = load_korea_geojson()

except Exception as e:

    korea_geojson = None
    geo_error = str(e)


# ============================================================
# BASIC CLEAN
# ============================================================

df["sido"] = (
    df["sido"]
    .fillna("")
    .astype(str)
    .str.strip()
)


df["sigungu"] = (
    df["sigungu"]
    .fillna("")
    .astype(str)
    .str.strip()
)


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


df = (
    df[
        df["year"].notna()
        &
        df["month"].notna()
    ]
    .copy()
)


df["year"] = (
    df["year"]
    .astype(int)
)


df["month"] = (
    df["month"]
    .astype(int)
)


df = (
    df[
        (df["month"] >= 1)
        &
        (df["month"] <= 12)
    ]
    .copy()
)


# ============================================================
# REGION NORMALIZE
# ============================================================

SIDO_MAP = {

    "서울": "서울",
    "서울특별시": "서울",

    "부산": "부산",
    "부산광역시": "부산",

    "대구": "대구",
    "대구광역시": "대구",

    "인천": "인천",
    "인천광역시": "인천",

    "광주": "광주",
    "광주광역시": "광주",

    "대전": "대전",
    "대전광역시": "대전",

    "울산": "울산",
    "울산광역시": "울산",

    "세종": "세종",
    "세종특별자치시": "세종",

    "경기": "경기",
    "경기도": "경기",

    "강원": "강원",
    "강원도": "강원",
    "강원특별자치도": "강원",

    "충북": "충북",
    "충청북도": "충북",

    "충남": "충남",
    "충청남도": "충남",

    "전북": "전북",
    "전라북도": "전북",
    "전북특별자치도": "전북",

    "전남": "전남",
    "전라남도": "전남",

    "경북": "경북",
    "경상북도": "경북",

    "경남": "경남",
    "경상남도": "경남",

    "제주": "제주",
    "제주특별자치도": "제주",
}


GEO_NAME_MAP = {

    "서울": "서울특별시",
    "부산": "부산광역시",
    "대구": "대구광역시",
    "인천": "인천광역시",
    "광주": "광주광역시",
    "대전": "대전광역시",
    "울산": "울산광역시",
    "세종": "세종특별자치시",

    "경기": "경기도",
    "강원": "강원도",

    "충북": "충청북도",
    "충남": "충청남도",

    "전북": "전라북도",
    "전남": "전라남도",

    "경북": "경상북도",
    "경남": "경상남도",

    "제주": "제주특별자치도",
}


def normalize_sido(value):

    value = str(value).strip()

    return SIDO_MAP.get(
        value,
        value
    )


df["sido_name"] = (
    df["sido"]
    .apply(
        normalize_sido
    )
)


# ============================================================
# INVALID DATA
# ============================================================

INVALID_SIDO = [
    "",
    "계",
    "합계",
    "총계",
    "전국",
    "불명",
    "미상",
]


INVALID_SIGUNGU = [
    "",
    "계",
    "합계",
    "총계",
    "전체",
    "불명",
    "미상",
]


df = (
    df[
        ~df["sido_name"].isin(
            INVALID_SIDO
        )
    ]
    .copy()
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
# DUPLICATE GROUP
# ============================================================

df = (
    df
    .groupby(
        [
            "date",
            "year",
            "month",
            "sido_name",
            "sigungu",
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
    .dropna()
    .unique()
    .tolist(),
    reverse=True
)


sido_list = sorted(
    df["sido_name"]
    .dropna()
    .unique()
    .tolist()
)


if not years:

    st.warning(
        "고령운전자 지역별·월별 사고 데이터가 없습니다."
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

    background: rgba(255,255,255,.98);

    border-radius: 16px;

    padding: 10px 20px;

    margin-bottom: 20px;
}


.st-key-top_nav button {

    background: transparent !important;

    color: #30384D !important;

    border: none !important;

    box-shadow: none !important;

    font-size: 16px !important;

    font-weight: 500 !important;

    min-height: 44px !important;
}


.st-key-nav_logo button {

    color: #27314C !important;

    font-size: 31px !important;

    font-weight: 900 !important;

    justify-content: flex-start !important;

    padding-left: 0 !important;
}


.st-key-nav_accident button {

    color: #D6A348 !important;

    font-weight: 800 !important;
}


.st-key-nav_future button {

    background: #D9A64A !important;

    color: #172035 !important;

    font-weight: 800 !important;
}


/* ==========================================================
   PAGE
========================================================== */

.st-key-senior_region_month_page {

    background: #101625;

    border: 1px solid #34405A;

    border-radius: 20px;

    padding: 34px 36px 44px 36px;
}


/* ==========================================================
   HEADER
========================================================== */

.page-path {

    color: #D6A348;

    font-size: 13px;

    font-weight: 800;

    margin-bottom: 10px;
}


.page-title {

    color: #FFFFFF;

    font-size: 42px;

    font-weight: 900;

    margin-bottom: 12px;
}


.page-sub {

    color: #C3CBD8;

    font-size: 15px;

    line-height: 1.7;

    margin-bottom: 26px;
}


/* ==========================================================
   BACK
========================================================== */

.st-key-back_accident button {

    background: #192136 !important;

    color: #E3E7EE !important;

    border: 1px solid #39445D !important;

    border-radius: 11px !important;

    min-height: 44px !important;
}


/* ==========================================================
   INPUT
========================================================== */

label[data-testid="stWidgetLabel"] p {

    color: #E2E7EF !important;

    font-size: 13px !important;

    font-weight: 700 !important;
}


div[data-baseweb="select"] > div {

    background: #F4F5F8 !important;

    color: #1C2435 !important;

    min-height: 46px !important;

    border-radius: 8px !important;
}


div[data-baseweb="select"] span {

    color: #273149 !important;
}


div[role="radiogroup"] {

    background: #192136;

    border: 1px solid #3F4B68;

    border-radius: 11px;

    padding: 7px 12px;
}


div[role="radiogroup"] label p {

    color: #FFFFFF !important;

    font-weight: 700 !important;
}


/* ==========================================================
   KPI
========================================================== */

.kpi {

    min-height: 112px;

    background: #192136;

    border: 1px solid #394560;

    border-radius: 17px;

    padding: 18px 20px;
}


.kpi-label {

    color: #C4CCD9;

    font-size: 12px;

    margin-bottom: 15px;
}


.kpi-value {

    color: #FFFFFF;

    font-size: 25px;

    font-weight: 800;
}


/* ==========================================================
   PANEL
========================================================== */

.st-key-map_panel,
.st-key-region_rank_panel,
.st-key-sigungu_panel,
.st-key-month_trend_panel,
.st-key-heatmap_panel,
.st-key-predict_panel,
.st-key-model_compare_panel {

    background: #182035;

    border: 1px solid #3A4662;

    border-radius: 28px;

    padding: 24px 26px 22px 26px;

    margin-top: 24px;
}


.panel-title {

    color: #FFFFFF;

    font-size: 21px;

    font-weight: 800;

    margin-bottom: 8px;
}


.panel-sub {

    color: #C8D0DC;

    font-size: 13px;

    line-height: 1.7;

    margin-bottom: 10px;
}


.panel-sub b {

    color: #F3C867;
}


/* ==========================================================
   ANALYSIS
========================================================== */

.analysis-box,
.model-box {

    background: #121A2B;

    border: 1px solid #35415C;

    border-left: 4px solid #D6A348;

    border-radius: 7px 15px 15px 7px;

    padding: 20px 22px;

    margin-top: 18px;

    color: #E5EAF2;

    font-size: 13px;

    line-height: 1.95;
}


.analysis-title,
.model-title {

    color: #F3C867;

    font-size: 16px;

    font-weight: 900;

    margin-bottom: 10px;
}


.analysis-box b,
.model-box b {

    color: #FFFFFF;
}


/* ==========================================================
   MODEL TABLE
========================================================== */

.model-table-wrap {

    margin-top: 18px;

    width: 100%;

    overflow-x: auto;

    border-radius: 16px;

    border: 1px solid #3D4964;

    background: #121A2B;
}


.model-table {

    width: 100%;

    border-collapse: collapse;

    min-width: 1050px;

    font-size: 13px;
}


.model-table th {

    background: #202A42;

    color: #FFFFFF;

    padding: 15px 14px;

    text-align: left;

    font-weight: 800;

    border-bottom: 1px solid #46516B;
}


.model-table td {

    padding: 15px 14px;

    color: #DDE3EC;

    border-bottom: 1px solid #2E3951;

    line-height: 1.55;
}


.model-table tbody tr:hover {

    background: #1B2540;
}


.model-name {

    color: #FFFFFF !important;

    font-weight: 900;
}


.apply-badge {

    display: inline-block;

    padding: 5px 9px;

    border-radius: 999px;

    font-size: 11px;

    font-weight: 800;
}


.apply-on {

    background: rgba(121,197,162,.15);

    color: #8ED6B3 !important;

    border: 1px solid rgba(121,197,162,.38);
}


.apply-off {

    background: rgba(158,170,190,.10);

    color: #BAC3D0 !important;

    border: 1px solid rgba(158,170,190,.22);
}


.fit-high {

    color: #87D0AA !important;

    font-weight: 900;
}


.fit-medium {

    color: #E7BE69 !important;

    font-weight: 900;
}


/* ==========================================================
   EXPANDER
========================================================== */

[data-testid="stExpander"] {

    background: #182035 !important;

    border: 1px solid #46536F !important;

    border-radius: 14px !important;

    overflow: hidden !important;

    margin-top: 12px !important;
}


[data-testid="stExpander"] summary * {

    color: #FFFFFF !important;

    opacity: 1 !important;
}


[data-testid="stExpander"] summary svg {

    color: #D6A348 !important;

    fill: #D6A348 !important;
}


/* ==========================================================
   PLOT
========================================================== */

.js-plotly-plot .plotly .legendtext,
.js-plotly-plot .plotly .xtick text,
.js-plotly-plot .plotly .ytick text,
.js-plotly-plot .plotly .annotation-text {

    fill: #E8EDF5 !important;
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
    key="senior_region_month_page"
):

    # ========================================================
    # HEADER
    # ========================================================

    head_left, head_right = st.columns(
        [5, 1],
        vertical_alignment="center"
    )


    with head_left:

        st.html(
            """
            <div class="page-path">
                교통사고 &gt; 고령운전자 지역별·월별 사고
            </div>

            <div class="page-title">
                고령운전자 지역별·월별 교통사고 분석
            </div>

            <div class="page-sub">
                전국 고령운전자 교통사고의 지역별 분포와 월별 변화를 분석하고,
                월 단위 시계열 데이터를 기반으로 향후 사고 규모를 예측합니다.
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

    f1, f2, f3, empty = st.columns(
        [1, 1, 1, 2]
    )


    with f1:

        selected_year = st.selectbox(
            "기준 연도",
            years,
            key="senior_region_year"
        )


    with f2:

        selected_month = st.selectbox(
            "기준 월",
            ["전체"] + list(range(1, 13)),
            format_func=lambda x: (
                "전체"
                if x == "전체"
                else f"{x}월"
            ),
            key="senior_region_month"
        )


    with f3:

        selected_sido = st.selectbox(
            "시도",
            ["전체"] + sido_list,
            key="senior_region_sido"
        )


    # ========================================================
    # PERIOD DATA
    # ========================================================

    if selected_month == "전체":

        period_df = (
            df[
                df["year"] == selected_year
            ]
            .copy()
        )

        period_label = (
            f"{selected_year}년"
        )

    else:

        period_df = (
            df[
                (
                    df["year"] == selected_year
                )
                &
                (
                    df["month"] == selected_month
                )
            ]
            .copy()
        )

        period_label = (
            f"{selected_year}년 {selected_month}월"
        )


    # ========================================================
    # SIDO SUMMARY
    # ========================================================

    sido_summary = (
        period_df
        .groupby(
            "sido_name",
            as_index=False
        )["accidents"]
        .sum()
        .sort_values(
            "accidents",
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )


    national_total = int(
        sido_summary[
            "accidents"
        ].sum()
    )


    # ========================================================
    # TOP SIDO
    # ========================================================

    if not sido_summary.empty:

        top_sido = str(
            sido_summary.iloc[0][
                "sido_name"
            ]
        )

        top_sido_accidents = int(
            sido_summary.iloc[0][
                "accidents"
            ]
        )

    else:

        top_sido = "-"
        top_sido_accidents = 0


    # ========================================================
    # SELECT REGION
    # ========================================================

    if selected_sido == "전체":

        selected_total = (
            national_total
        )

        selected_share = (
            100.0
        )

        selected_label = (
            "전국"
        )

    else:

        selected_row = (
            sido_summary[
                sido_summary[
                    "sido_name"
                ] == selected_sido
            ]
        )


        selected_total = (
            int(
                selected_row.iloc[0][
                    "accidents"
                ]
            )

            if not selected_row.empty

            else 0
        )


        selected_share = (
            selected_total
            / national_total
            * 100

            if national_total > 0

            else 0
        )


        selected_label = (
            selected_sido
        )


    # ========================================================
    # TOP SIGUNGU
    # ========================================================

    analysis_sido = (
        top_sido
        if selected_sido == "전체"
        else selected_sido
    )


    sigungu_summary = (
        period_df[
            period_df[
                "sido_name"
            ] == analysis_sido
        ]
        .copy()
    )


    sigungu_summary = (
        sigungu_summary[
            ~sigungu_summary[
                "sigungu"
            ].isin(
                INVALID_SIGUNGU
            )
        ]
        .groupby(
            "sigungu",
            as_index=False
        )["accidents"]
        .sum()
        .sort_values(
            "accidents",
            ascending=False
        )
    )


    if not sigungu_summary.empty:

        top_sigungu = str(
            sigungu_summary.iloc[0][
                "sigungu"
            ]
        )

        top_sigungu_accidents = int(
            sigungu_summary.iloc[0][
                "accidents"
            ]
        )

    else:

        top_sigungu = "-"
        top_sigungu_accidents = 0


    # ========================================================
    # TOP 3
    # ========================================================

    top3_total = int(
        sido_summary
        .head(3)[
            "accidents"
        ]
        .sum()
    )


    top3_share = (
        top3_total
        / national_total
        * 100

        if national_total > 0

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
                    {period_label} 전국 고령운전자 사고
                </div>

                <div class="kpi-value">
                    {national_total:,}건
                </div>

            </div>
            """
        )


    with k2:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    사고 최다 시도
                </div>

                <div class="kpi-value">
                    {top_sido}
                </div>

            </div>
            """
        )


    with k3:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    {selected_label} 사고 건수
                </div>

                <div class="kpi-value">
                    {selected_total:,}건
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
                        "상위 3개 시도 집중도"
                        if selected_sido == "전체"
                        else f"{selected_sido} 전국 비중"
                    }
                </div>

                <div class="kpi-value">
                    {
                        f"{top3_share:.1f}%"
                        if selected_sido == "전체"
                        else f"{selected_share:.1f}%"
                    }
                </div>

            </div>
            """
        )


    # ========================================================
    # MAP + RANK
    # ========================================================

    left, right = st.columns(
        [1.3, 1],
        gap="medium"
    )


    # ========================================================
    # MAP
    # ========================================================

    with left:

        with st.container(
            key="map_panel"
        ):

            st.html(
                f"""
                <div class="panel-title">
                    {period_label} 시도별 고령운전자 사고 분포
                </div>

                <div class="panel-sub">
                    색상이 붉고 밝을수록 해당 지역에서
                    고령운전자 교통사고가 많이 발생했습니다.
                </div>
                """
            )


            if korea_geojson is None:

                st.warning(
                    f"대한민국 지도 데이터를 불러오지 못했습니다.\n\n{geo_error}"
                )

            else:

                map_df = (
                    sido_summary
                    .copy()
                )


                map_df["geo_name"] = (
                    map_df["sido_name"]
                    .map(
                        GEO_NAME_MAP
                    )
                )


                map_df = (
                    map_df[
                        map_df[
                            "geo_name"
                        ].notna()
                    ]
                    .copy()
                )


                fig_map = go.Figure(
                    go.Choropleth(

                        geojson=korea_geojson,

                        featureidkey=(
                            "properties.name"
                        ),

                        locations=map_df[
                            "geo_name"
                        ],

                        z=map_df[
                            "accidents"
                        ],

                        customdata=map_df[
                            [
                                "sido_name",
                                "accidents"
                            ]
                        ],

                        colorscale=[
                            [0.00, "#10233A"],
                            [0.12, "#174C6A"],
                            [0.27, "#1F7A7A"],
                            [0.42, "#49A078"],
                            [0.57, "#9EBB58"],
                            [0.72, "#D6B23F"],
                            [0.86, "#E8753B"],
                            [1.00, "#D84638"],
                        ],

                        marker_line_color=(
                            "#E1E7EF"
                        ),

                        marker_line_width=(
                            1.05
                        ),

                        colorbar=dict(

                            title=dict(
                                text="사고 건수",

                                font=dict(
                                    color="#FFFFFF",
                                    size=12
                                )
                            ),

                            tickfont=dict(
                                color="#FFFFFF"
                            ),

                            thickness=18,

                            len=.72
                        ),

                        hovertemplate=(
                            "<b>%{customdata[0]}</b>"
                            "<br>"
                            "사고: %{customdata[1]:,}건"
                            "<extra></extra>"
                        )
                    )
                )


                fig_map.update_geos(

                    fitbounds="locations",

                    visible=False,

                    bgcolor="#182035"
                )


                fig_map.update_layout(

                    height=610,

                    margin=dict(
                        l=10,
                        r=75,
                        t=10,
                        b=10
                    ),

                    paper_bgcolor="#182035",

                    plot_bgcolor="#182035",

                    font=dict(
                        color="#FFFFFF"
                    )
                )


                st.plotly_chart(

                    fig_map,

                    use_container_width=True,

                    config={
                        "displayModeBar": False
                    }
                )


    # ========================================================
    # REGION RANK
    # ========================================================

    with right:

        with st.container(
            key="region_rank_panel"
        ):

            st.html(
                f"""
                <div class="panel-title">
                    {period_label} 시도별 사고 순위
                </div>

                <div class="panel-sub">
                    시도별 고령운전자 사고 건수를 비교합니다.
                </div>
                """
            )


            rank_df = (
                sido_summary
                .sort_values(
                    "accidents",
                    ascending=True
                )
                .copy()
            )


            max_rank = (
                float(
                    rank_df[
                        "accidents"
                    ].max()
                )

                if not rank_df.empty

                else 1
            )


            if max_rank <= 0:
                max_rank = 1


            fig_rank = go.Figure(
                go.Bar(

                    x=rank_df[
                        "accidents"
                    ],

                    y=rank_df[
                        "sido_name"
                    ],

                    orientation="h",

                    marker_color=[
                        "#E8753B"

                        if (
                            selected_sido != "전체"
                            and region == selected_sido
                        )

                        else "#D9A64A"

                        if region == top_sido

                        else "#79B69B"

                        for region
                        in rank_df[
                            "sido_name"
                        ]
                    ],

                    text=[
                        f"{int(value):,}건"

                        for value
                        in rank_df[
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
                    )
                )
            )


            fig_rank.update_layout(

                height=610,

                margin=dict(
                    l=75,
                    r=100,
                    t=20,
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
                        max_rank * 1.23
                    ]
                ),

                yaxis=dict(
                    title=None
                )
            )


            st.plotly_chart(

                fig_rank,

                use_container_width=True,

                config={
                    "displayModeBar": False
                }
            )


    # ========================================================
    # DISTRIBUTION ANALYSIS
    # ========================================================

    top_sido_share = (
        top_sido_accidents
        / national_total
        * 100

        if national_total > 0

        else 0
    )


    st.html(
        f"""
        <div class="analysis-box">

            <div class="analysis-title">
                {period_label} 지역 사고 분석
            </div>

            고령운전자 사고가 가장 많이 발생한 시도는
            <b>{top_sido}</b>입니다.

            <br>

            {top_sido}에서는
            <b>{top_sido_accidents:,}건</b>의 사고가 발생하여,
            전국 고령운전자 사고의 약
            <b>{top_sido_share:.1f}%</b>를 차지했습니다.

            <br>

            사고 발생 상위 3개 시도의 사고를 합하면
            <b>{top3_total:,}건</b>으로
            전국 사고의 약
            <b>{top3_share:.1f}%</b>입니다.

            <br>

            현재 상세 분석 지역
            <b>{analysis_sido}</b>에서
            사고가 가장 많은 시군구는
            <b>{top_sigungu}</b>이며
            <b>{top_sigungu_accidents:,}건</b>이 발생했습니다.

        </div>
        """
    )


    # ========================================================
    # SIGUNGU + MONTH TREND
    # ========================================================

    bottom_left, bottom_right = st.columns(
        [1, 1],
        gap="medium"
    )


    # ========================================================
    # SIGUNGU
    # ========================================================

    with bottom_left:

        with st.container(
            key="sigungu_panel"
        ):

            st.html(
                f"""
                <div class="panel-title">
                    {period_label} {analysis_sido} 시군구별 사고
                </div>

                <div class="panel-sub">
                    {analysis_sido} 내부의 시군구별
                    고령운전자 교통사고 규모를 비교합니다.
                </div>
                """
            )


            sigungu_plot_df = (
                sigungu_summary
                .sort_values(
                    "accidents",
                    ascending=True
                )
                .copy()
            )


            if sigungu_plot_df.empty:

                st.info(
                    "해당 지역의 시군구별 사고 데이터가 없습니다."
                )

            else:

                max_sigungu = float(
                    sigungu_plot_df[
                        "accidents"
                    ].max()
                )


                if max_sigungu <= 0:
                    max_sigungu = 1


                fig_sigungu = go.Figure(
                    go.Bar(

                        x=sigungu_plot_df[
                            "accidents"
                        ],

                        y=sigungu_plot_df[
                            "sigungu"
                        ],

                        orientation="h",

                        marker_color=[
                            "#D9A64A"
                            if area == top_sigungu
                            else "#79B69B"

                            for area
                            in sigungu_plot_df[
                                "sigungu"
                            ]
                        ],

                        text=[
                            f"{int(value):,}건"

                            for value
                            in sigungu_plot_df[
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
                        )
                    )
                )


                fig_sigungu.update_layout(

                    height=max(
                        520,
                        len(
                            sigungu_plot_df
                        ) * 28
                    ),

                    margin=dict(
                        l=110,
                        r=100,
                        t=30,
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
                            max_sigungu * 1.25
                        ]
                    )
                )


                st.plotly_chart(

                    fig_sigungu,

                    use_container_width=True,

                    config={
                        "displayModeBar": False
                    }
                )


    # ========================================================
    # YEAR MONTH TREND
    # ========================================================

    with bottom_right:

        with st.container(
            key="month_trend_panel"
        ):

            trend_region = (
                analysis_sido
            )


            st.html(
                f"""
                <div class="panel-title">
                    {selected_year}년 {trend_region} 월별 사고 추이
                </div>

                <div class="panel-sub">
                    선택한 시도의 월별 고령운전자 사고 변화를 확인합니다.
                </div>
                """
            )


            month_trend_df = (
                df[
                    (
                        df["year"] == selected_year
                    )
                    &
                    (
                        df["sido_name"] == trend_region
                    )
                ]
                .groupby(
                    "month",
                    as_index=False
                )["accidents"]
                .sum()
                .sort_values(
                    "month"
                )
            )


            if not month_trend_df.empty:

                top_month_row = (
                    month_trend_df
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


            fig_month = go.Figure(
                go.Scatter(

                    x=[
                        f"{month}월"

                        for month
                        in month_trend_df[
                            "month"
                        ]
                    ],

                    y=month_trend_df[
                        "accidents"
                    ],

                    mode="lines+markers+text",

                    line=dict(
                        color="#91C7AA",
                        width=4
                    ),

                    marker=dict(

                        size=9,

                        color=[
                            "#D9A64A"
                            if month == top_month
                            else "#91C7AA"

                            for month
                            in month_trend_df[
                                "month"
                            ]
                        ]
                    ),

                    text=[
                        f"{int(value):,}"

                        for value
                        in month_trend_df[
                            "accidents"
                        ]
                    ],

                    textposition="top center",

                    hovertemplate=(
                        "<b>%{x}</b>"
                        "<br>"
                        "사고: %{y:,}건"
                        "<extra></extra>"
                    )
                )
            )


            fig_month.update_layout(

                height=520,

                margin=dict(
                    l=75,
                    r=55,
                    t=50,
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
                    rangemode="tozero"
                )
            )


            st.plotly_chart(

                fig_month,

                use_container_width=True,

                config={
                    "displayModeBar": False
                }
            )


            if top_month > 0:

                st.html(
                    f"""
                    <div class="analysis-box">

                        <div class="analysis-title">
                            {trend_region} 월별 사고 분석
                        </div>

                        {selected_year}년 {trend_region}에서
                        고령운전자 사고가 가장 많이 발생한 달은
                        <b>{top_month}월</b>입니다.

                        <br>

                        해당 월 사고는
                        <b>{top_month_accidents:,}건</b>입니다.

                    </div>
                    """
                )


    # ========================================================
    # REGION × MONTH HEATMAP
    # ========================================================

    with st.container(
        key="heatmap_panel"
    ):

        st.html(
            f"""
            <div class="panel-title">
                {selected_year}년 시도 × 월 사고 집중도
            </div>

            <div class="panel-sub">
                월별·지역별 고령운전자 사고를 동시에 비교합니다.
                붉고 밝은 영역일수록 사고 발생 건수가 많습니다.
            </div>
            """
        )


        heat_source = (
            df[
                df[
                    "year"
                ] == selected_year
            ]
            .groupby(
                [
                    "sido_name",
                    "month"
                ],
                as_index=False
            )["accidents"]
            .sum()
        )


        heat_df = (
            heat_source
            .pivot_table(
                index="sido_name",
                columns="month",
                values="accidents",
                aggfunc="sum",
                fill_value=0
            )
            .reindex(
                columns=range(1, 13),
                fill_value=0
            )
        )


        region_totals = (
            heat_df
            .sum(axis=1)
            .sort_values(
                ascending=True
            )
        )


        heat_df = heat_df.reindex(
            region_totals.index
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
                    "<b>%{y}</b>"
                    "<br>"
                    "%{x}"
                    "<br>"
                    "사고: %{z:,}건"
                    "<extra></extra>"
                )
            )
        )


        fig_heat.update_layout(

            height=650,

            margin=dict(
                l=100,
                r=80,
                t=35,
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
                title="시도"
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
    # FUTURE PREDICTION
    # ========================================================

    with st.container(
        key="predict_panel"
    ):

        st.html(
            """
            <div class="panel-title">
                지역별 고령운전자 사고 미래 예측
            </div>

            <div class="panel-sub">
                월별 사고 시계열을 기반으로 향후 사고 건수를 예측합니다.
                <br>
                데이터가 충분하고 모델이 안정적인 경우
                <b>SARIMA</b>를 적용하며,
                불안정한 경우
                <b>Linear Trend Regression</b>으로 자동 전환합니다.
            </div>
            """
        )


        p1, p2, p3, empty = st.columns(
            [1, 1, 1.5, 2]
        )


        with p1:

            predict_sido = st.selectbox(
                "예측 지역",
                ["전국"] + sido_list,
                index=(
                    0
                    if selected_sido == "전체"
                    else (
                        ["전국"] + sido_list
                    ).index(
                        selected_sido
                    )
                ),
                key="senior_region_predict_sido"
            )


        # ====================================================
        # SIGUNGU OPTION
        # ====================================================

        if predict_sido == "전국":

            predict_sigungu_list = [
                "전체"
            ]

        else:

            predict_sigungu_list = (
                df[
                    df[
                        "sido_name"
                    ] == predict_sido
                ][
                    "sigungu"
                ]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )


            predict_sigungu_list = sorted(
                [
                    x
                    for x
                    in predict_sigungu_list
                    if x not in INVALID_SIGUNGU
                ]
            )


            predict_sigungu_list = (
                ["전체"]
                + predict_sigungu_list
            )


        with p2:

            predict_sigungu = st.selectbox(
                "시군구",
                predict_sigungu_list,
                key="senior_region_predict_sigungu"
            )


        with p3:

            predict_period = st.radio(
                "예측 기간",
                [
                    "1년",
                    "5년",
                    "10년"
                ],
                horizontal=True,
                key="senior_region_predict_period"
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

        if predict_sido == "전국":

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

            predict_label = (
                "전국"
            )


        elif predict_sigungu == "전체":

            prediction_source = (
                df[
                    df[
                        "sido_name"
                    ] == predict_sido
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

            predict_label = (
                predict_sido
            )


        else:

            prediction_source = (
                df[
                    (
                        df[
                            "sido_name"
                        ] == predict_sido
                    )
                    &
                    (
                        df[
                            "sigungu"
                        ] == predict_sigungu
                    )
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

            predict_label = (
                f"{predict_sido} {predict_sigungu}"
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
                "예측을 수행하기 위한 월별 데이터가 부족합니다."
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


            future_values = None

            lower_values = None

            upper_values = None

            sarima_used = False

            sarima_fallback = False

            model_name = (
                "Linear Trend Regression"
            )


            model_reason = (
                "안정적인 장기 추세 예측을 위해 "
                "Linear Trend Regression을 적용했습니다."
            )


            # =================================================
            # SARIMA
            # 36개월 이상이면 시도
            # =================================================

            if len(
                prediction_source
            ) >= 36:

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


                    model = SARIMAX(

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


                    result = model.fit(
                        disp=False,
                        maxiter=200
                    )


                    forecast = (
                        result
                        .get_forecast(
                            steps=horizon_months
                        )
                    )


                    candidate_future = (
                        forecast
                        .predicted_mean
                        .to_numpy(
                            dtype=float
                        )
                    )


                    confidence = (
                        forecast
                        .conf_int(
                            alpha=0.05
                        )
                    )


                    candidate_lower = (
                        confidence
                        .iloc[:, 0]
                        .to_numpy(
                            dtype=float
                        )
                    )


                    candidate_upper = (
                        confidence
                        .iloc[:, 1]
                        .to_numpy(
                            dtype=float
                        )
                    )


                    # =================================================
                    # STABILITY CHECK
                    # =================================================

                    actual_max = max(
                        float(
                            np.nanmax(
                                actual_values
                            )
                        ),
                        1
                    )


                    actual_mean = max(
                        float(
                            np.nanmean(
                                actual_values
                            )
                        ),
                        1
                    )


                    valid = (

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


                    if valid:

                        forecast_max = float(
                            np.nanmax(
                                np.abs(
                                    candidate_future
                                )
                            )
                        )


                        upper_max = float(
                            np.nanmax(
                                candidate_upper
                            )
                        )


                        confidence_width = float(
                            np.nanmax(
                                candidate_upper
                                - candidate_lower
                            )
                        )


                        unstable = (

                            forecast_max
                            > actual_max * 5

                            or

                            upper_max
                            > actual_max * 8

                            or

                            confidence_width
                            > actual_mean * 10
                        )

                    else:

                        unstable = True


                    if unstable:

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

                        sarima_used = True

                        model_name = (
                            "SARIMA (1,1,0)(1,0,0,12)"
                        )

                        model_reason = (
                            "월별 데이터가 충분하고 SARIMA 예측값과 "
                            "신뢰구간이 안정성 검사를 통과하여 "
                            "12개월 계절성을 반영한 SARIMA를 적용했습니다."
                        )


                except Exception:

                    sarima_fallback = True


            # =================================================
            # LINEAR FALLBACK
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
                    )
                    + horizon_months,
                    dtype=float
                )


                future_values = (
                    slope
                    * future_x
                    + intercept
                )


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


                if sarima_fallback:

                    model_reason = (
                        "SARIMA를 시도했으나 예측값 또는 신뢰구간이 "
                        "현재 데이터 범위에 비해 불안정하게 계산되어 "
                        "Linear Trend Regression으로 자동 전환했습니다."
                    )

                elif len(
                    prediction_source
                ) < 36:

                    model_reason = (
                        "SARIMA 계절 패턴을 안정적으로 학습하기 위한 "
                        "월별 데이터가 부족하여 Linear Trend Regression을 적용했습니다."
                    )


            # =================================================
            # NEGATIVE REMOVE
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


            future_max = max(
                float(
                    np.nanmax(
                        future_values
                    )
                ),
                1
            )


            y_max = max(
                actual_max,
                future_max
            )


            if (
                sarima_used
                and upper_values is not None
            ):

                safe_upper_max = min(
                    float(
                        np.nanmax(
                            upper_values
                        )
                    ),
                    y_max * 3
                )


                y_max = max(
                    y_max,
                    safe_upper_max
                )


            y_axis_max = (
                y_max * 1.18
            )


            # =================================================
            # PLOT
            # =================================================

            fig_predict = go.Figure()


            # ACTUAL
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
                        color="#A0C9AC",
                        size=6
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


            # =================================================
            # FORECAST
            # =================================================

            prediction_x = (
                [
                    actual_dates.iloc[-1]
                ]
                +
                list(
                    future_dates
                )
            )


            prediction_y = (
                [
                    float(
                        actual_values[-1]
                    )
                ]
                +
                list(
                    future_values
                )
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


            # =================================================
            # PREDICTION START
            # =================================================

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

                height=590,

                margin=dict(
                    l=80,
                    r=60,
                    t=65,
                    b=70
                ),

                paper_bgcolor="#182035",

                plot_bgcolor="#182035",

                hovermode="x unified",

                font=dict(
                    color="#E8EDF5"
                ),

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

                    showgrid=False
                ),

                yaxis=dict(

                    title="교통사고 건수(건)",

                    gridcolor="#35405A",

                    rangemode="tozero",

                    range=[
                        0,
                        y_axis_max
                    ],

                    tickformat=","
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
            # PREDICTION RESULT
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


            change_value = (
                predicted_value
                - current_value
            )


            change_rate = (
                change_value
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
            # METRIC TEXT
            # =================================================

            metric_html = ""


            if (
                model_name
                ==
                "Linear Trend Regression"
            ):

                metric_html = f"""
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


            # =================================================
            # MODEL INFO
            # =================================================

            st.html(
                f"""
                <div class="model-box">

                    <div class="model-title">
                        예측 모델 정보
                    </div>

                    <b>예측 지역</b> :
                    {predict_label}

                    <br>

                    <b>적용 모델</b> :
                    {model_name}

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

                    {metric_html}

                    <br><br>

                    <b>모델 선택 이유</b>

                    <br>

                    {model_reason}

                </div>
                """
            )


            # =================================================
            # RESULT ANALYSIS
            # =================================================

            st.html(
                f"""
                <div class="analysis-box">

                    <div class="analysis-title">
                        {predict_label} 고령운전자 사고 예측 결과
                    </div>

                    마지막 실제 관측값은
                    <b>
                        {end_date.strftime("%Y-%m")}
                        {current_value:,}건
                    </b>입니다.

                    <br>

                    {
                        future_dates[-1]
                        .strftime("%Y-%m")
                    } 예상 사고 건수는
                    약
                    <b>{predicted_value:,}건</b>입니다.

                    <br>

                    마지막 실제 관측값과 비교하면
                    <b>{change_value:+,}건</b>,
                    약
                    <b>{change_rate:+.1f}%</b>
                    변화할 것으로 예측됩니다.

                    <br><br>

                    ※ 예측 결과는 과거 지역별 월간 사고 추세를 기반으로 하며,
                    향후 고령인구 변화, 면허 보유자 수, 교통량,
                    도로 환경 및 정책 변화는 반영하지 않습니다.

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
                지역별 월간 고령운전자 사고 예측에 활용할 수 있는
                주요 시계열 모델을 비교합니다.
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

                            <th>적용 기준</th>

                        </tr>

                    </thead>


                    <tbody>

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
                                월별 시계열과 12개월 반복 패턴을
                                동시에 학습
                            </td>

                            <td>
                                12개월 계절성
                            </td>

                            <td class="fit-high">
                                높음
                            </td>

                            <td>
                                36개월 이상 데이터 +
                                모델 안정성 검사 통과
                            </td>

                        </tr>


                        <tr>

                            <td class="model-name">
                                Linear Trend
                            </td>

                            <td>
                                <span class="apply-badge apply-on">
                                    Fallback
                                </span>
                            </td>

                            <td>
                                시간에 따른 사고의
                                장기 증가·감소 추세 분석
                            </td>

                            <td>
                                미반영
                            </td>

                            <td class="fit-high">
                                높음
                            </td>

                            <td>
                                SARIMA 데이터 부족 또는
                                불안정 시 적용
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
                                자기회귀와 이동평균을 이용해
                                시계열 값을 예측
                            </td>

                            <td>
                                기본 미반영
                            </td>

                            <td class="fit-medium">
                                보통
                            </td>

                            <td>
                                월간 데이터에서는
                                SARIMA가 계절성 처리에 유리
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
                                자동 모델링
                            </td>

                            <td>
                                반영 가능
                            </td>

                            <td class="fit-high">
                                높음
                            </td>

                            <td>
                                향후 비교 모델로 확장 가능
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
                    예측 모델 적용 기준
                </div>

                지역별 월간 사고 데이터가
                <b>36개월 이상</b> 존재하면
                12개월 계절성을 고려할 수 있는
                <b>SARIMA</b>를 우선 학습합니다.

                <br>

                단, 예측값이나 신뢰구간이 실제 데이터 범위에 비해
                비정상적으로 커지는 경우 해당 SARIMA 결과를 사용하지 않습니다.

                <br>

                이 경우 페이지가 오류를 발생시키지 않고
                자동으로
                <b>Linear Trend Regression</b>으로 전환하여
                안정적인 장기 추세 예측값을 제공합니다.

                <br><br>

                향후 데이터가 충분히 축적되면
                SARIMA·Prophet 등의 모델을 실제 검증 데이터에 대해
                MAE / RMSE 기준으로 비교하는 방식으로 확장할 수 있습니다.

            </div>
            """
        )


    # ========================================================
    # DETAIL TABLE
    # ========================================================

    st.write("")


    with st.expander(
        "고령운전자 지역별·월별 사고 데이터 상세 보기"
    ):

        detail_df = (
            df[
                [
                    "year",
                    "month",
                    "sido_name",
                    "sigungu",
                    "accidents"
                ]
            ]
            .copy()
            .sort_values(
                [
                    "year",
                    "month",
                    "sido_name",
                    "sigungu"
                ],
                ascending=[
                    False,
                    True,
                    True,
                    True
                ]
            )
        )


        detail_df.columns = [
            "연도",
            "월",
            "시도",
            "시군구",
            "사고건수"
        ]


        detail_df[
            "사고건수"
        ] = (
            detail_df[
                "사고건수"
            ]
            .round()
            .astype(int)
        )


        st.dataframe(

            detail_df,

            use_container_width=True,

            hide_index=True,

            height=460,

            column_config={

                "연도":
                    st.column_config.NumberColumn(
                        "연도",
                        format="%d년"
                    ),

                "월":
                    st.column_config.NumberColumn(
                        "월",
                        format="%d월"
                    ),

                "시도":
                    st.column_config.TextColumn(
                        "시도"
                    ),

                "시군구":
                    st.column_config.TextColumn(
                        "시군구"
                    ),

                "사고건수":
                    st.column_config.NumberColumn(
                        "사고건수",
                        format="%d건"
                    ),
            }
        )