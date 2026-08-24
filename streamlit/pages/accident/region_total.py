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
# SAFE/streamlit/pages/accident/region_total.py
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
def load_accident_region():

    engine = get_engine()

    query = text(
        """
        SELECT
            id,
            sido,
            sigungu,
            year,
            accidents
        FROM accident_region
        ORDER BY year, sido, sigungu
        """
    )

    with engine.connect() as conn:
        return pd.read_sql(query, conn)


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

    df = load_accident_region()

except Exception as e:

    st.error(
        f"MySQL 지역별 교통사고 데이터 조회 실패\n\n{e}"
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

df["accidents"] = pd.to_numeric(
    df["accidents"],
    errors="coerce"
).fillna(0)

df = df[
    df["year"].notna()
].copy()

df["year"] = (
    df["year"]
    .astype(int)
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
    .apply(normalize_sido)
)


INVALID_SIDO = [
    "",
    "계",
    "합계",
    "총계",
    "전국",
    "미상",
    "불명",
]

INVALID_SIGUNGU = [
    "",
    "계",
    "합계",
    "총계",
    "전체",
]


df = df[
    ~df["sido_name"].isin(
        INVALID_SIDO
    )
].copy()


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


/* NAV */

.st-key-top_nav {

    background: rgba(255,255,255,.98);

    border-radius: 16px;

    padding: 10px 20px;

    margin-bottom: 20px;

    box-shadow:
        0 5px 20px
        rgba(0,0,0,.10);
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


/* PAGE */

.st-key-region_total_page {

    background: #101625;

    border: 1px solid #34405A;

    border-radius: 20px;

    padding: 34px 36px 44px 36px;
}


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


/* BACK */

.st-key-back_accident button {

    background: #192136 !important;

    color: #E3E7EE !important;

    border: 1px solid #39445D !important;

    border-radius: 11px !important;

    min-height: 44px !important;
}


/* INPUT */

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


/* SECTION TITLE */

.section-title {
    color: #FFFFFF;
    font-size: 28px;
    font-weight: 900;
    letter-spacing: -0.5px;
    margin-top: 34px;
    margin-bottom: 4px;
    padding-bottom: 10px;
    border-bottom: 2px solid #D6A348;
}

/* KPI */

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


/* PANELS */

.st-key-map_panel,
.st-key-rank_panel,
.st-key-sigungu_panel,
.st-key-trend_panel,
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


/* INFO */

.analysis-box,
.info-box {

    background: #121A2B;

    border: 1px solid #35415C;

    border-left: 4px solid #D6A348;

    border-radius: 7px 15px 15px 7px;

    padding: 20px 22px;

    margin-top: 20px;

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
.info-box b {

    color: #FFFFFF;
}


/* MODEL INFO */

.model-box {

    background: #121A2B;

    border: 1px solid #46516D;

    border-radius: 16px;

    padding: 22px 24px;

    margin-top: 18px;

    color: #E6EBF3;

    font-size: 13px;

    line-height: 1.95;
}


.model-box b {

    color: #FFFFFF;
}


/* MODEL TABLE */

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

    min-width: 1080px;

    font-size: 13px;
}


.model-table thead th {

    background: #202A42;

    color: #F6F8FB;

    padding: 15px 14px;

    text-align: left;

    font-weight: 800;

    border-bottom: 1px solid #46516B;
}


.model-table tbody td {

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


.fit-low {

    color: #E7BE69 !important;

    font-weight: 900;
}


.fit-very-low {

    color: #E48A75 !important;

    font-weight: 900;
}


/* EXPANDER */

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


/* PLOT */

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
    key="region_total_page"
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
                교통사고 &gt; 지역별 사고
            </div>

            <div class="page-title">
                지역별 교통사고 분석
            </div>

            <div class="page-sub">
                전국 시도 및 시군구별 사고 현황과
                연도별 변화, 미래 사고 추세를 분석합니다.
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


    f1, f2, empty = st.columns(
        [1, 1, 3]
    )


    with f1:

        selected_year = st.selectbox(
            "기준 연도",
            years,
            key="region_accident_year"
        )


    with f2:

        selected_sido = st.selectbox(
            "시도",
            ["전체"] + sido_list,
            key="region_accident_sido"
        )


    # ========================================================
    # YEAR SUMMARY
    # ========================================================

    year_df = df[
        df["year"] == selected_year
    ].copy()


    sido_summary = (
        year_df
        .groupby(
            "sido_name",
            as_index=False
        )["accidents"]
        .sum()
        .sort_values(
            "accidents",
            ascending=False
        )
        .reset_index(drop=True)
    )


    national_total = int(
        sido_summary[
            "accidents"
        ].sum()
    )


    top_sido = (
        str(
            sido_summary.iloc[0]["sido_name"]
        )
        if not sido_summary.empty
        else "-"
    )


    top_accidents = (
        int(
            sido_summary.iloc[0]["accidents"]
        )
        if not sido_summary.empty
        else 0
    )


    lowest_sido = (
        str(
            sido_summary.iloc[-1]["sido_name"]
        )
        if not sido_summary.empty
        else "-"
    )


    lowest_accidents = (
        int(
            sido_summary.iloc[-1]["accidents"]
        )
        if not sido_summary.empty
        else 0
    )


    top_share = (
        top_accidents
        / national_total
        * 100
        if national_total > 0
        else 0
    )


    top3_total = int(
        sido_summary
        .head(3)["accidents"]
        .sum()
    )


    top3_share = (
        top3_total
        / national_total
        * 100
        if national_total > 0
        else 0
    )


    if selected_sido == "전체":

        selected_total = national_total
        selected_share = 100
        selected_label = "전국"

    else:

        selected_row = sido_summary[
            sido_summary[
                "sido_name"
            ] == selected_sido
        ]


        selected_total = (
            int(
                selected_row.iloc[0]["accidents"]
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


        selected_label = selected_sido


    # ========================================================
    # ANALYSIS SECTION
    # ========================================================

    st.html(
        '''
        <div class="section-title">분석</div>
        '''
    )

    # ========================================================
    # KPI
    # ========================================================

    st.write("")


    k1, k2, k3, k4 = st.columns(4)


    with k1:

        st.html(
            f"""
            <div class="kpi">
                <div class="kpi-label">
                    {selected_year}년 전국 사고
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
                    {selected_label} 사고
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
                        "상위 3개 지역 집중도"
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
                    {selected_year}년 대한민국 시도별 교통사고 분포
                </div>

                <div class="panel-sub">
                    남색 → 청록 → 녹색 → 골드 → 주황 → 빨강 순으로
                    사고 발생 규모가 커집니다.
                </div>
                """
            )


            if korea_geojson is None:

                st.warning(
                    f"지도 로드 실패\n\n{geo_error}"
                )

            else:

                map_df = sido_summary.copy()


                map_df["geo_name"] = (
                    map_df["sido_name"]
                    .map(GEO_NAME_MAP)
                )


                map_df = map_df[
                    map_df["geo_name"].notna()
                ].copy()


                fig_map = go.Figure(
                    go.Choropleth(

                        geojson=korea_geojson,

                        featureidkey="properties.name",

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

                        marker_line_color="#E1E7EF",

                        marker_line_width=1.05,

                        colorbar=dict(

                            title=dict(
                                text="사고 건수",
                                font=dict(
                                    color="#FFFFFF"
                                )
                            ),

                            tickfont=dict(
                                color="#FFFFFF"
                            ),

                            thickness=18,

                            len=.72,
                        ),

                        hovertemplate=(
                            "<b>%{customdata[0]}</b>"
                            "<br>"
                            "%{customdata[1]:,}건"
                            "<extra></extra>"
                        ),
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
                        r=70,
                        t=15,
                        b=10
                    ),

                    paper_bgcolor="#182035",

                    plot_bgcolor="#182035",
                )


                st.plotly_chart(
                    fig_map,
                    use_container_width=True,
                    config={
                        "displayModeBar": False
                    }
                )


    # ========================================================
    # RANK
    # ========================================================

    with right:

        with st.container(
            key="rank_panel"
        ):

            st.html(
                f"""
                <div class="panel-title">
                    {selected_year}년 시도별 사고 순위
                </div>

                <div class="panel-sub">
                    시도별 사고건수를 높은 지역부터 비교합니다.
                </div>
                """
            )


            rank_df = (
                sido_summary
                .sort_values(
                    "accidents",
                    ascending=True
                )
            )


            max_rank = (
                float(
                    rank_df["accidents"].max()
                )
                if not rank_df.empty
                else 1
            )


            fig_rank = go.Figure(
                go.Bar(

                    x=rank_df["accidents"],

                    y=rank_df["sido_name"],

                    orientation="h",

                    marker_color=[
                        "#E8753B"
                        if (
                            selected_sido != "전체"
                            and sido == selected_sido
                        )
                        else "#D9A64A"
                        if sido == top_sido
                        else "#79B69B"

                        for sido
                        in rank_df["sido_name"]
                    ],

                    text=[
                        f"{int(v):,}건"
                        for v
                        in rank_df["accidents"]
                    ],

                    textposition="outside",

                    cliponaxis=False,
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
                        max_rank * 1.22
                    ]
                ),
            )


            st.plotly_chart(
                fig_rank,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )


    # ========================================================
    # MAP ANALYSIS
    # ========================================================

    st.html(
        f"""
        <div class="analysis-box">

            <div class="analysis-title">
                {selected_year}년 지역 사고 분포 분석
            </div>

            전국 사고 최다 지역은
            <b>{top_sido}</b>으로
            <b>{top_accidents:,}건</b>입니다.

            <br>

            전국 사고의 약
            <b>{top_share:.1f}%</b>를 차지합니다.

            <br>

            사고 최저 지역은
            <b>{lowest_sido}</b>으로
            <b>{lowest_accidents:,}건</b>입니다.

            <br>

            사고 상위 3개 시도에는
            전국 사고의 약
            <b>{top3_share:.1f}%</b>가 집중되어 있습니다.

        </div>
        """
    )


    # ========================================================
    # SIGUNGU + TREND
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

            panel_region = (
                selected_sido
                if selected_sido != "전체"
                else top_sido
            )


            st.html(
                f"""
                <div class="panel-title">
                    {selected_year}년 {panel_region} 시군구별 사고
                </div>

                <div class="panel-sub">
                    시군구별 교통사고 규모를 비교합니다.
                </div>
                """
            )


            sigungu_df = year_df[
                year_df[
                    "sido_name"
                ] == panel_region
            ].copy()


            sigungu_df = sigungu_df[
                ~sigungu_df["sigungu"].isin(
                    INVALID_SIGUNGU
                )
            ]


            sigungu_df = (
                sigungu_df
                .groupby(
                    "sigungu",
                    as_index=False
                )["accidents"]
                .sum()
                .sort_values(
                    "accidents",
                    ascending=True
                )
            )


            if sigungu_df.empty:

                st.info(
                    "시군구 데이터가 없습니다."
                )

            else:

                max_sigungu = float(
                    sigungu_df[
                        "accidents"
                    ].max()
                )


                top_sigungu = (
                    sigungu_df
                    .sort_values(
                        "accidents",
                        ascending=False
                    )
                    .iloc[0]["sigungu"]
                )


                fig_sigungu = go.Figure(
                    go.Bar(

                        x=sigungu_df[
                            "accidents"
                        ],

                        y=sigungu_df[
                            "sigungu"
                        ],

                        orientation="h",

                        marker_color=[
                            "#D9A64A"
                            if x == top_sigungu
                            else "#79B69B"

                            for x
                            in sigungu_df["sigungu"]
                        ],

                        text=[
                            f"{int(v):,}건"
                            for v
                            in sigungu_df["accidents"]
                        ],

                        textposition="outside",

                        cliponaxis=False,
                    )
                )


                fig_sigungu.update_layout(

                    height=max(
                        520,
                        len(sigungu_df) * 28
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
    # TREND
    # ========================================================

    with bottom_right:

        with st.container(
            key="trend_panel"
        ):

            trend_label = (
                "전국"
                if selected_sido == "전체"
                else selected_sido
            )


            st.html(
                f"""
                <div class="panel-title">
                    {trend_label} 연도별 교통사고 추이
                </div>

                <div class="panel-sub">
                    연도별 사고건수 변화 추이를 확인합니다.
                </div>
                """
            )


            if selected_sido == "전체":

                trend_df = (
                    df
                    .groupby(
                        "year",
                        as_index=False
                    )["accidents"]
                    .sum()
                    .sort_values("year")
                )

            else:

                trend_df = (
                    df[
                        df[
                            "sido_name"
                        ] == selected_sido
                    ]
                    .groupby(
                        "year",
                        as_index=False
                    )["accidents"]
                    .sum()
                    .sort_values("year")
                )


            fig_trend = go.Figure(
                go.Scatter(

                    x=trend_df["year"],

                    y=trend_df["accidents"],

                    mode="lines+markers+text",

                    line=dict(
                        color="#91C7AA",
                        width=4
                    ),

                    marker=dict(
                        size=9,
                        color="#D9A64A"
                    ),

                    text=[
                        f"{int(v):,}"
                        for v
                        in trend_df["accidents"]
                    ],

                    textposition="top center",
                )
            )


            fig_trend.update_layout(

                height=520,

                paper_bgcolor="#182035",

                plot_bgcolor="#182035",

                showlegend=False,

                font=dict(
                    color="#E8EDF5"
                ),

                xaxis=dict(
                    title="연도",
                    dtick=1
                ),

                yaxis=dict(
                    title="교통사고 건수(건)",
                    gridcolor="#35405A"
                )
            )


            st.plotly_chart(
                fig_trend,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )


    # ========================================================
    # PREDICTION SECTION
    # ========================================================

    st.html(
        '''
        <div class="section-title">예측</div>
        '''
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
                지역별 사고 미래 예측
            </div>

            <div class="panel-sub">
                과거 지역별 사고 발생 추세를 기반으로
                향후 교통사고 건수를 예측합니다.
                <br>
                현재 적용 모델 :
                <b>
                    선형 추세 분석
                    (Linear Trend Regression)
                </b>
            </div>
            """
        )


        p1, p2, empty = st.columns(
            [1, 1.5, 2.5]
        )


        with p1:

            predict_region = st.selectbox(
                "예측 지역",
                ["전국"] + sido_list,
                index=(
                    0
                    if selected_sido == "전체"
                    else (
                        ["전국"] + sido_list
                    ).index(selected_sido)
                ),
                key="region_prediction_area"
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
                key="region_prediction_period"
            )


        horizon = {
            "1년": 1,
            "5년": 5,
            "10년": 10
        }[
            predict_period
        ]


        # ====================================================
        # PREDICTION SOURCE
        # ====================================================

        if predict_region == "전국":

            prediction_source = (
                df
                .groupby(
                    "year",
                    as_index=False
                )["accidents"]
                .sum()
                .sort_values("year")
                .drop_duplicates("year")
            )

        else:

            prediction_source = (
                df[
                    df[
                        "sido_name"
                    ] == predict_region
                ]
                .groupby(
                    "year",
                    as_index=False
                )["accidents"]
                .sum()
                .sort_values("year")
                .drop_duplicates("year")
            )


        if len(prediction_source) < 2:

            st.warning(
                "미래 예측을 수행하려면 최소 2개 연도 데이터가 필요합니다."
            )

        else:

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
            # LINEAR TREND
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


            residuals = (
                y - fitted_values
            )


            mae = float(
                np.mean(
                    np.abs(residuals)
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


            last_year = int(
                x.max()
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
            # PREDICT GRAPH
            # =================================================

            fig_predict = go.Figure()


            fig_predict.add_trace(
                go.Scatter(

                    x=x,

                    y=y,

                    mode="lines+markers",

                    name="실제 사고",

                    line=dict(
                        color="#A0C9AC",
                        width=4
                    ),

                    marker=dict(
                        size=9,
                        color="#A0C9AC"
                    ),
                )
            )


            prediction_x = (
                [last_year]
                + future_years.tolist()
            )


            prediction_y = (
                [float(y[-1])]
                + future_values.tolist()
            )


            fig_predict.add_trace(
                go.Scatter(

                    x=prediction_x,

                    y=prediction_y,

                    mode="lines+markers+text",

                    name="예측 사고",

                    line=dict(
                        color="#DD8469",
                        width=4,
                        dash="dash"
                    ),

                    marker=dict(
                        size=9,
                        color="#DD8469"
                    ),

                    text=[
                        ""
                    ] + [
                        f"{int(round(v)):,}"
                        for v
                        in future_values
                    ],

                    textposition="top center",
                )
            )


            fig_predict.add_vline(
                x=last_year,
                line_dash="dot",
                line_color="#D6A348"
            )


            fig_predict.add_annotation(

                x=last_year,

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

                height=560,

                margin=dict(
                    l=80,
                    r=65,
                    t=60,
                    b=70
                ),

                paper_bgcolor="#182035",

                plot_bgcolor="#182035",

                font=dict(
                    color="#E8EDF5"
                ),

                legend=dict(
                    orientation="h",
                    y=1.04,
                    x=1,
                    xanchor="right",

                    font=dict(
                        color="#FFFFFF"
                    )
                ),

                xaxis=dict(
                    title="연도",
                    dtick=1
                ),

                yaxis=dict(
                    title="교통사고 건수(건)",
                    gridcolor="#35405A"
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


            train_start = int(
                x.min()
            )


            train_end = int(
                x.max()
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
                    Linear Trend Regression

                    <br>

                    <b>예측 지역</b> :
                    {predict_region}

                    <br>

                    <b>학습 기간</b> :
                    {train_start}년 ~
                    {train_end}년

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
                    예측 모델이 해당 데이터를 자동으로 포함하여
                    회귀식과 미래 예측값을 다시 계산합니다.

                </div>
                """
            )


            # =================================================
            # PREDICTION SUMMARY
            # =================================================

            st.html(
                f"""
                <div class="analysis-box">

                    <div class="analysis-title">
                        {predict_region} 사고 예측 결과
                    </div>

                    마지막 실제 데이터는
                    <b>
                        {last_year}년 {current_last:,}건
                    </b>
                    입니다.

                    <br>

                    현재 사고 변화 추세가 지속된다고 가정하면
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
                    <b>
                        {prediction_change:+,}건
                    </b>,
                    약
                    <b>
                        {prediction_change_rate:+.1f}%
                    </b>
                    변화할 것으로 추정됩니다.

                    <br><br>

                    ※ 정책 변화, 자동차 등록대수,
                    인구 변화, 도로 환경 등 외부 변수는
                    본 예측에 반영하지 않습니다.

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
                지역별 사고 예측에 활용할 수 있는 주요 시계열 모델의
                특성과 현재 데이터에 대한 적합성을 비교합니다.
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
                        <th>현재 적용</th>
                        <th>특징</th>
                        <th>필요 데이터</th>
                        <th>계절성</th>
                        <th>현재 적합성</th>
                        <th>비고</th>
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
                            연도와 사고건수의
                            선형적인 증가·감소 추세 분석
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
                            현재 연도 단위 데이터에
                            단순하고 해석이 쉬움
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
                            과거 관측값과 오차를 기반으로
                            시계열을 예측
                        </td>

                        <td>
                            충분한 연속 시계열
                        </td>

                        <td>
                            기본 반영 안 함
                        </td>

                        <td class="fit-low">
                            낮음
                        </td>

                        <td>
                            장기간 연도 데이터가
                            확보되면 검토 가능
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
                            ARIMA에 계절 패턴을
                            추가한 모델
                        </td>

                        <td>
                            긴 계절 시계열
                        </td>

                        <td>
                            반영 가능
                        </td>

                        <td class="fit-very-low">
                            매우 낮음
                        </td>

                        <td>
                            월별 또는 분기별
                            사고 데이터에 적합
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
                            자동적으로 모델링
                        </td>

                        <td>
                            비교적 많은 시계열
                        </td>

                        <td>
                            반영 가능
                        </td>

                        <td class="fit-low">
                            낮음
                        </td>

                        <td>
                            월별 사고 데이터 확보 시
                            활용 가치가 높음
                        </td>

                    </tr>

                </tbody>

            </table>

            </div>
            """
        )


        st.html(
            f"""
            <div class="info-box">

                <b>현재 모델 선정 이유</b>

                <br><br>

                현재 {predict_region} 사고 예측에 사용 가능한 데이터는
                <b>{len(prediction_source)}개 연도</b>입니다.

                <br>

                관측치가 적은 상태에서
                ARIMA·SARIMA·Prophet을 적용하면
                충분한 시계열 패턴을 학습하고 검증하기 어렵습니다.

                <br>

                따라서 현재는
                <b>Linear Trend Regression</b>을 적용하며,
                향후 장기간 데이터 또는 월별 사고 데이터가 확보되면
                다른 모델과 MAE·RMSE 등을 기준으로
                성능 비교가 가능합니다.

            </div>
            """
        )


    # ========================================================
    # DETAIL TABLE
    # ========================================================

    st.write("")


    with st.expander(
        "지역별 교통사고 데이터 상세 보기"
    ):

        detail_df = (
            df[
                [
                    "year",
                    "sido_name",
                    "sigungu",
                    "accidents"
                ]
            ]
            .copy()
            .sort_values(
                [
                    "year",
                    "sido_name",
                    "sigungu"
                ],
                ascending=[
                    False,
                    True,
                    True
                ]
            )
        )


        detail_df.columns = [
            "연도",
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
            height=460
        )