import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sqlalchemy import text


# ============================================================
# PROJECT ROOT
# SAFE/streamlit/pages/people/resident_population_monthly.py
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
# MYSQL LOAD
# ============================================================

@st.cache_data(ttl=600)
def load_monthly_population():

    engine = get_engine()

    query = text(
        """
        SELECT
            id,
            month,
            region,
            population
        FROM resident_population_monthly
        ORDER BY month, region
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

    df = load_monthly_population()

except Exception as e:

    st.error(
        f"MySQL 데이터 조회 실패\n\n{e}"
    )

    st.stop()


# ============================================================
# BASIC CLEAN
# ============================================================

df["month"] = (
    df["month"]
    .fillna("")
    .astype(str)
    .str.strip()
)


df["region"] = (
    df["region"]
    .fillna("")
    .astype(str)
    .str.strip()
)


df["population"] = pd.to_numeric(
    df["population"],
    errors="coerce"
).fillna(0)


# ============================================================
# REGION CODE REMOVE
#
# 강원도 (4200000000) -> 강원도
# 서울특별시 (1100000000) -> 서울특별시
# ============================================================

df["region"] = (
    df["region"]
    .str.replace(
        r"\s*\(\d+\)\s*$",
        "",
        regex=True
    )
    .str.strip()
)


# ============================================================
# REGION NORMALIZATION
# ============================================================

REGION_MAP = {

    "전국": "전국",

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

    "강원도": "강원",
    "강원": "강원",

    "충청북도": "충북",
    "충북": "충북",

    "충청남도": "충남",
    "충남": "충남",

    "전라북도": "전북",
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


df["region_name"] = (
    df["region"]
    .apply(
        normalize_region
    )
)


# ============================================================
# INVALID REGION
# ============================================================

INVALID_REGIONS = [
    "",
    "계",
    "합계",
    "총계",
    "미상",
    "불명",
]


df = df[
    ~df["region_name"].isin(
        INVALID_REGIONS
    )
].copy()


# ============================================================
# MONTH DATETIME
# ============================================================

df["month_dt"] = pd.to_datetime(
    df["month"],
    format="%Y-%m",
    errors="coerce"
)


df = df[
    df["month_dt"].notna()
].copy()


# ============================================================
# DUPLICATE CLEAN
#
# 같은 월 + 같은 지역 데이터가 여러 행일 경우
# population 최대값 1개만 사용
# ============================================================

df = (
    df
    .groupby(
        [
            "month",
            "month_dt",
            "region_name",
        ],
        as_index=False
    )["population"]
    .max()
)


df = (
    df
    .sort_values(
        "month_dt"
    )
    .reset_index(
        drop=True
    )
)


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


.st-key-nav_people button {

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

.st-key-monthly_people_page {

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
   BACK
========================================================== */

.st-key-back_people button {

    background:
        #192136 !important;

    color:
        #D1D6E0 !important;

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

    line-height:
        1.2;
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
   PANEL
========================================================== */

.st-key-month_trend_panel,
.st-key-region_panel,
.st-key-pie_panel {

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
    key="monthly_people_page"
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
                인구 &gt; 주민등록 인구
            </div>

            <div class="page-title">
                주민등록 인구 현황
            </div>

            <div class="page-sub">
                월별 주민등록 인구 데이터를 통해
                최근 지역별 인구 규모와 변화 흐름을 확인합니다.
            </div>
            """
        )


    with head_right:

        with st.container(
            key="back_people"
        ):

            if st.button(
                "← 인구 분석",
                use_container_width=True
            ):

                go_people()


    # ========================================================
    # OPTIONS
    # ========================================================

    month_options = (
        df[
            [
                "month",
                "month_dt",
            ]
        ]
        .drop_duplicates()
        .sort_values(
            "month_dt",
            ascending=False
        )[
            "month"
        ]
        .tolist()
    )


    region_options = (
        ["전체"]
        + sorted(
            [
                region
                for region
                in df[
                    "region_name"
                ]
                .dropna()
                .unique()
                .tolist()
                if region != "전국"
            ]
        )
    )


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

        selected_month = st.selectbox(
            "기준 월",
            month_options,
            key="monthly_population_month"
        )


    with f2:

        selected_region = st.selectbox(
            "지역",
            region_options,
            key="monthly_population_region"
        )


    # ========================================================
    # SELECTED MONTH DATA
    # ========================================================

    selected_month_df = (
        df[
            df[
                "month"
            ] == selected_month
        ]
        .copy()
    )


    national_month_row = (
        selected_month_df[
            selected_month_df[
                "region_name"
            ] == "전국"
        ]
        .copy()
    )


    regional_month_df = (
        selected_month_df[
            selected_month_df[
                "region_name"
            ] != "전국"
        ]
        .copy()
    )


    # ========================================================
    # NATIONAL POPULATION
    # ========================================================

    if not national_month_row.empty:

        national_population = int(
            national_month_row.iloc[0][
                "population"
            ]
        )

    else:

        national_population = int(
            regional_month_df[
                "population"
            ].sum()
        )


    # ========================================================
    # ANALYSIS SCOPE
    # ========================================================

    analysis_scope = (
        "전국"
        if selected_region == "전체"
        else selected_region
    )


    # ========================================================
    # TREND DATA
    # ========================================================

    if selected_region == "전체":

        national_rows = (
            df[
                df[
                    "region_name"
                ] == "전국"
            ][
                [
                    "month",
                    "month_dt",
                    "population",
                ]
            ]
            .copy()
        )


        if not national_rows.empty:

            trend_df = (
                national_rows
                .sort_values(
                    "month_dt"
                )
                .reset_index(
                    drop=True
                )
            )

        else:

            trend_df = (
                df[
                    df[
                        "region_name"
                    ] != "전국"
                ]
                .groupby(
                    [
                        "month",
                        "month_dt",
                    ],
                    as_index=False
                )["population"]
                .sum()
                .sort_values(
                    "month_dt"
                )
                .reset_index(
                    drop=True
                )
            )

    else:

        trend_df = (
            df[
                df[
                    "region_name"
                ] == selected_region
            ][
                [
                    "month",
                    "month_dt",
                    "population",
                ]
            ]
            .sort_values(
                "month_dt"
            )
            .reset_index(
                drop=True
            )
        )


    # ========================================================
    # CURRENT POPULATION
    # ========================================================

    if selected_region == "전체":

        current_population = (
            national_population
        )

    else:

        current_region_row = (
            selected_month_df[
                selected_month_df[
                    "region_name"
                ] == selected_region
            ]
        )


        if not current_region_row.empty:

            current_population = int(
                current_region_row.iloc[0][
                    "population"
                ]
            )

        else:

            current_population = 0


    # ========================================================
    # PREVIOUS MONTH
    # ========================================================

    current_month_dt = pd.to_datetime(
        selected_month,
        format="%Y-%m",
        errors="coerce"
    )


    previous_rows = (
        trend_df[
            trend_df[
                "month_dt"
            ] < current_month_dt
        ]
    )


    if not previous_rows.empty:

        previous_row = (
            previous_rows
            .sort_values(
                "month_dt"
            )
            .iloc[-1]
        )


        previous_month = str(
            previous_row[
                "month"
            ]
        )


        previous_population = int(
            previous_row[
                "population"
            ]
        )


        month_change = (
            current_population
            - previous_population
        )


        month_change_rate = (
            month_change
            / previous_population
            * 100
            if previous_population > 0
            else 0
        )

    else:

        previous_month = "-"
        previous_population = 0
        month_change = 0
        month_change_rate = 0


    # ========================================================
    # REGION SUMMARY
    # ========================================================

    region_summary = (
        regional_month_df[
            [
                "region_name",
                "population",
            ]
        ]
        .sort_values(
            "population",
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )


    # 0 값은 그래프에서 제외
    region_summary = (
        region_summary[
            region_summary[
                "population"
            ] > 0
        ]
        .copy()
    )


    # ========================================================
    # TOP REGION
    # ========================================================

    if not region_summary.empty:

        top_region_row = (
            region_summary.iloc[0]
        )


        top_region = str(
            top_region_row[
                "region_name"
            ]
        )


        top_region_population = int(
            top_region_row[
                "population"
            ]
        )

    else:

        top_region = "-"
        top_region_population = 0


    # ========================================================
    # SHARE
    # ========================================================

    if selected_region == "전체":

        selected_share = (
            top_region_population
            / national_population
            * 100
            if national_population > 0
            else 0
        )

    else:

        selected_share = (
            current_population
            / national_population
            * 100
            if national_population > 0
            else 0
        )


    # ========================================================
    # KPI STYLE
    # ========================================================

    change_class = (
        "positive"
        if month_change >= 0
        else "negative"
    )


    change_symbol = (
        "▲"
        if month_change > 0

        else "▼"
        if month_change < 0

        else "－"
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
                    {selected_month} {analysis_scope} 주민등록 인구
                </div>

                <div class="kpi-value">
                    {current_population:,}명
                </div>

            </div>
            """
        )


    with k2:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    전월 대비 인구 변화
                </div>

                <div class="kpi-value {change_class}">
                    {change_symbol} {abs(month_change):,}명
                </div>

            </div>
            """
        )


    with k3:

        if selected_region == "전체":

            third_label = (
                "주민등록 인구 최다 지역"
            )

            third_value = (
                top_region
            )

        else:

            third_label = (
                "전월 대비 증감률"
            )

            third_value = (
                f"{month_change_rate:+.3f}%"
            )


        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    {third_label}
                </div>

                <div class="kpi-value">
                    {third_value}
                </div>

            </div>
            """
        )


    with k4:

        if selected_region == "전체":

            fourth_label = (
                f"{top_region} 전국 비중"
            )

        else:

            fourth_label = (
                f"전국 대비 {selected_region} 비중"
            )


        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    {fourth_label}
                </div>

                <div class="kpi-value">
                    {selected_share:.1f}%
                </div>

            </div>
            """
        )


    # ========================================================
    # MONTH TREND
    # ========================================================

    with st.container(
        key="month_trend_panel"
    ):

        st.html(
            f"""
            <div class="panel-title">
                {analysis_scope} 월별 주민등록 인구 추이
            </div>

            <div class="panel-sub">
                X축: 월 · Y축: 주민등록 인구(명) ·
                최근 인구 증가·감소 흐름을 확인합니다.
            </div>
            """
        )


        if trend_df.empty:

            st.warning(
                "월별 주민등록 인구 데이터가 없습니다."
            )

        else:

            min_pop = float(
                trend_df[
                    "population"
                ].min()
            )


            max_pop = float(
                trend_df[
                    "population"
                ].max()
            )


            pop_range = (
                max_pop
                - min_pop
            )


            padding = max(
                pop_range * .20,
                max_pop * .002,
                10000,
            )


            fig_trend = go.Figure(
                go.Scatter(

                    x=trend_df[
                        "month"
                    ],

                    y=trend_df[
                        "population"
                    ],

                    mode="lines+markers",

                    line=dict(
                        color="#79C5A2",
                        width=4,
                    ),

                    marker=dict(

                        size=7,

                        color="#D9A64A",

                        line=dict(
                            color="#182035",
                            width=1.5,
                        ),
                    ),

                    hovertemplate=(
                        "<b>%{x}</b>"
                        "<br>"
                        "주민등록 인구: %{y:,}명"
                        "<extra></extra>"
                    ),
                )
            )


            if current_population > 0:

                fig_trend.add_trace(
                    go.Scatter(

                        x=[
                            selected_month
                        ],

                        y=[
                            current_population
                        ],

                        mode="markers+text",

                        marker=dict(
                            size=15,
                            color="#E17663",
                        ),

                        text=[
                            f"{current_population:,}명"
                        ],

                        textposition="top center",

                        textfont=dict(
                            color="#FFFFFF",
                            size=12,
                        ),

                        showlegend=False,

                        hoverinfo="skip",
                    )
                )


            fig_trend.update_layout(

                height=500,

                margin=dict(
                    l=100,
                    r=55,
                    t=55,
                    b=95,
                ),

                paper_bgcolor="#182035",

                plot_bgcolor="#182035",

                showlegend=False,

                hovermode="x unified",

                font=dict(
                    color="#E7EAF0",
                    size=13,
                ),

                xaxis=dict(

                    title="월",

                    showgrid=False,

                    tickangle=-45,

                    tickfont=dict(
                        color="#D5DAE4",
                        size=11,
                    ),
                ),

                yaxis=dict(

                    title="주민등록 인구(명)",

                    showgrid=True,

                    gridcolor="#35405A",

                    zeroline=False,

                    tickformat=",",

                    range=[
                        max(
                            0,
                            min_pop - padding
                        ),
                        max_pop + padding,
                    ],

                    tickfont=dict(
                        color="#D5DAE4",
                        size=11,
                    ),
                ),
            )


            st.plotly_chart(

                fig_trend,

                use_container_width=True,

                config={
                    "displayModeBar": False,
                }
            )


    # ========================================================
    # REGION + DONUT
    # ========================================================

    left, right = st.columns(
        [
            1.25,
            1,
        ],
        gap="medium"
    )


    # ========================================================
    # LEFT - REGION BAR
    # ========================================================

    with left:

        with st.container(
            key="region_panel"
        ):

            st.html(
                f"""
                <div class="panel-title">
                    {selected_month} 지역별 주민등록 인구
                </div>

                <div class="panel-sub">
                    전국을 제외한 시도별 주민등록 인구 규모를 비교합니다.
                </div>
                """
            )


            region_chart_df = (
                region_summary

                .sort_values(
                    "population",
                    ascending=True
                )

                .copy()
            )


            if region_chart_df.empty:

                st.warning(
                    "지역별 주민등록 인구 데이터가 없습니다."
                )

            else:

                max_population = float(
                    region_chart_df[
                        "population"
                    ].max()
                )


                if max_population <= 0:
                    max_population = 1


                bar_colors = []


                for _, row in region_chart_df.iterrows():

                    if (
                        selected_region != "전체"
                        and row[
                            "region_name"
                        ] == selected_region
                    ):

                        color = "#E17663"


                    elif (
                        row[
                            "region_name"
                        ] == top_region
                    ):

                        color = "#D9A64A"


                    else:

                        color = "#79B69B"


                    bar_colors.append(
                        color
                    )


                fig_region = go.Figure(
                    go.Bar(

                        x=region_chart_df[
                            "population"
                        ],

                        y=region_chart_df[
                            "region_name"
                        ],

                        orientation="h",

                        marker_color=bar_colors,

                        text=[
                            f"{int(value):,}"
                            for value
                            in region_chart_df[
                                "population"
                            ]
                        ],

                        textposition="outside",

                        textfont=dict(
                            color="#F2F4F8",
                            size=11,
                        ),

                        cliponaxis=False,

                        hovertemplate=(
                            "<b>%{y}</b>"
                            "<br>"
                            "주민등록 인구: %{x:,}명"
                            "<extra></extra>"
                        ),
                    )
                )


                fig_region.update_layout(

                    height=610,

                    margin=dict(
                        l=85,
                        r=135,
                        t=25,
                        b=65,
                    ),

                    paper_bgcolor="#182035",

                    plot_bgcolor="#182035",

                    showlegend=False,

                    bargap=.28,

                    font=dict(
                        color="#E7EAF0",
                        size=13,
                    ),

                    xaxis=dict(

                        title="주민등록 인구(명)",

                        showgrid=True,

                        gridcolor="#35405A",

                        zeroline=False,

                        tickformat=",",

                        range=[
                            0,
                            max_population * 1.22
                        ],
                    ),

                    yaxis=dict(

                        title=None,

                        showgrid=False,

                        automargin=True,

                        tickfont=dict(
                            color="#F0F2F6",
                            size=12,
                        ),
                    ),
                )


                st.plotly_chart(

                    fig_region,

                    use_container_width=True,

                    config={
                        "displayModeBar": False,
                    }
                )


    # ========================================================
    # RIGHT - DONUT
    # ========================================================

    with right:

        with st.container(
            key="pie_panel"
        ):

            st.html(
                f"""
                <div class="panel-title">
                    {selected_month} 지역별 주민등록 인구 비중
                </div>

                <div class="panel-sub">
                    각 지역의 주민등록 인구가 전국 시도 인구에서
                    차지하는 비중을 확인합니다.
                </div>
                """
            )


            pie_df = (
                region_summary
                .copy()
                .sort_values(
                    "population",
                    ascending=False
                )
            )


            if pie_df.empty:

                st.warning(
                    "지역별 주민등록 인구 데이터가 없습니다."
                )

            else:

                regional_total = float(
                    pie_df[
                        "population"
                    ].sum()
                )


                # --------------------------------------------
                # 선택 지역 강조
                # --------------------------------------------

                pull_values = []


                for region in pie_df[
                    "region_name"
                ]:

                    if (
                        selected_region != "전체"
                        and region == selected_region
                    ):

                        pull_values.append(
                            0.08
                        )

                    else:

                        pull_values.append(
                            0
                        )


                # --------------------------------------------
                # COLORS
                # --------------------------------------------

                pie_colors = [
                    "#D9A64A",
                    "#79B69B",
                    "#88A8CF",
                    "#A58AC8",
                    "#C57B5E",
                    "#E2BA58",
                    "#83B39E",
                    "#85AEB8",
                    "#B78A8A",
                    "#9EA96D",
                    "#6E8FA5",
                    "#927FAB",
                    "#B58C68",
                    "#718D77",
                    "#7F809E",
                    "#9E766F",
                    "#657C8A",
                ]


                # --------------------------------------------
                # DONUT
                # --------------------------------------------

                fig_pie = go.Figure(
                    go.Pie(

                        labels=pie_df[
                            "region_name"
                        ],

                        values=pie_df[
                            "population"
                        ],

                        hole=.58,

                        pull=pull_values,

                        sort=False,

                        direction="clockwise",

                        marker=dict(

                            colors=pie_colors,

                            line=dict(
                                color="#182035",
                                width=2,
                            ),
                        ),

                        textinfo="label+percent",

                        textposition="outside",

                        textfont=dict(
                            color="#F2F4F8",
                            size=10,
                        ),

                        hovertemplate=(
                            "<b>%{label}</b>"
                            "<br>"
                            "주민등록 인구: %{value:,}명"
                            "<br>"
                            "비중: %{percent}"
                            "<extra></extra>"
                        ),
                    )
                )


                fig_pie.add_annotation(

                    x=.5,
                    y=.52,

                    text=(
                        "<b>시도 합계</b>"
                        "<br>"
                        f"{int(regional_total):,}명"
                    ),

                    showarrow=False,

                    font=dict(
                        color="#FFFFFF",
                        size=15,
                    ),

                    align="center",
                )


                fig_pie.update_layout(

                    height=610,

                    margin=dict(
                        l=70,
                        r=70,
                        t=35,
                        b=60,
                    ),

                    paper_bgcolor="#182035",

                    plot_bgcolor="#182035",

                    showlegend=False,

                    font=dict(
                        color="#E7EAF0",
                        size=11,
                    ),

                    uniformtext_minsize=9,

                    uniformtext_mode="hide",
                )


                st.plotly_chart(

                    fig_pie,

                    use_container_width=True,

                    config={
                        "displayModeBar": False,
                    }
                )


    # ========================================================
    # SUMMARY
    # ========================================================

    if selected_region == "전체":

        summary_text = f"""
            {selected_month} 기준 전국 주민등록 인구는
            <b>{current_population:,}명</b>입니다.
            <br>

            직전 월인 <b>{previous_month}</b>과 비교하면
            <b>{month_change:+,}명</b> 변화했으며,
            증감률은
            <b>{month_change_rate:+.3f}%</b>입니다.
            <br>

            주민등록 인구가 가장 많은 지역은
            <b>{top_region}</b>으로
            <b>{top_region_population:,}명</b>입니다.
            <br>

            {top_region}은 전국 주민등록 인구의
            약 <b>{selected_share:.1f}%</b>를 차지합니다.
        """

    else:

        summary_text = f"""
            {selected_month} 기준
            <b>{selected_region}</b> 주민등록 인구는
            <b>{current_population:,}명</b>입니다.
            <br>

            직전 월인 <b>{previous_month}</b>과 비교하면
            <b>{month_change:+,}명</b> 변화했으며,
            증감률은
            <b>{month_change_rate:+.3f}%</b>입니다.
            <br>

            전국 주민등록 인구에서
            {selected_region}이 차지하는 비중은
            약 <b>{selected_share:.1f}%</b>입니다.
        """


    st.html(
        f"""
        <div class="info-box">

            <b>주민등록 인구 현황 요약</b>
            <br><br>

            {summary_text}

        </div>
        """
    )


    # ========================================================
    # DETAIL
    # ========================================================

    st.write("")


    with st.expander(
        "월별 주민등록 인구 데이터 상세 보기"
    ):

        detail_df = (
            df[
                [
                    "month",
                    "region_name",
                    "population",
                ]
            ]
            .copy()
        )


        if selected_region != "전체":

            detail_df = (
                detail_df[
                    detail_df[
                        "region_name"
                    ] == selected_region
                ]
            )


        detail_df = (
            detail_df

            .sort_values(
                [
                    "month",
                    "population",
                ],
                ascending=[
                    False,
                    False,
                ]
            )

            .reset_index(
                drop=True
            )
        )


        detail_df[
            "population"
        ] = (
            detail_df[
                "population"
            ]
            .round()
            .astype(int)
        )


        detail_df.columns = [
            "월",
            "지역",
            "주민등록 인구",
        ]


        st.dataframe(

            detail_df,

            use_container_width=True,

            hide_index=True,

            column_config={

                "월":
                    st.column_config.TextColumn(
                        "월"
                    ),

                "지역":
                    st.column_config.TextColumn(
                        "지역"
                    ),

                "주민등록 인구":
                    st.column_config.NumberColumn(
                        "주민등록 인구",
                        format="%d명"
                    ),
            },
        )