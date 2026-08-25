import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sqlalchemy import text


# ============================================================
# PROJECT ROOT
# SAFE/streamlit/pages/people/local_population.py
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
def load_population_data():

    engine = get_engine()

    query = text(
        """
        SELECT
            id,
            region,
            year,
            population
        FROM local_population
        ORDER BY year, region
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

    df = load_population_data()

except Exception as e:

    st.error(
        f"MySQL 데이터 조회 실패\n\n{e}"
    )

    st.stop()


# ============================================================
# BASIC CLEAN
# ============================================================

df["region"] = (
    df["region"]
    .fillna("")
    .astype(str)
    .str.strip()
)


df["year"] = pd.to_numeric(
    df["year"],
    errors="coerce"
)


df["population"] = pd.to_numeric(
    df["population"],
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
# REGION CODE REMOVE
#
# 경기도 (4100000000) -> 경기도
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
    "수도권": "수도권",

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


df["region_name"] = (
    df["region"]
    .apply(
        normalize_region
    )
)


# ============================================================
# INVALID / AGGREGATE REGION
#
# 수도권은 별도 집계행이므로 그래프에서는 제외
# 전국은 KPI 계산용이므로 유지
# ============================================================

INVALID_REGIONS = [
    "",
    "계",
    "합계",
    "총계",
    "수도권",
    "미상",
    "불명",
]


df = df[
    ~df["region_name"].isin(
        INVALID_REGIONS
    )
].copy()


# ============================================================
# DUPLICATE CLEAN
#
# 같은 연도 + 같은 지역 중복 방지
# ============================================================

df = (
    df
    .groupby(
        [
            "year",
            "region_name",
        ],
        as_index=False
    )["population"]
    .max()
)


# ============================================================
# FORMAT FUNCTIONS
#
# local_population의 population 단위 = 천 명
#
# 51,685 -> 51,685,000명
# ============================================================

def population_to_people(value):

    return int(
        round(
            float(value) * 1000
        )
    )


def format_korean_people(value_thousand):

    people = population_to_people(
        value_thousand
    )

    if people >= 100_000_000:

        return (
            f"{people / 100_000_000:.1f}억 명"
        )

    elif people >= 10_000:

        return (
            f"{people / 10_000:,.0f}만 명"
        )

    elif people >= 1_000:

        return (
            f"{people / 1_000:,.0f}천 명"
        )

    else:

        return (
            f"{people:,}명"
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
        18px !important;

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
        33px !important;

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

.st-key-local_population_page {

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
        15px;

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
        44px;

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
        17px;

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
        15px !important;

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
        16px !important;
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
        14px;

    margin-bottom:
        15px;
}


.kpi-value {

    color:
        #FFFFFF;

    font-size:
        27px;

    font-weight:
        800;

    line-height:
        1.2;
}


/* ==========================================================
   PANELS
========================================================== */

.st-key-region_bar_panel,
.st-key-region_pie_panel,
.st-key-table_panel {

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
        23px;

    font-weight:
        800;

    margin-bottom:
        7px;
}


.panel-sub {

    color:
        #B8C0CF;

    font-size:
        15px;

    line-height:
        1.6;

    margin-bottom:
        10px;
}


/* ==========================================================
   STREAMLIT DATAFRAME - SAFER STYLE
========================================================== */

.st-key-table_panel [data-testid="stDataFrame"] {

    margin-top: 18px;

    border: 1px solid #46536F !important;

    border-radius: 16px !important;

    overflow: hidden !important;

    background: #131B2E !important;

    box-shadow:
        0 10px 26px
        rgba(0,0,0,.16);
}

.st-key-table_panel [data-testid="stDataFrame"] > div {

    border-radius: 16px !important;
}

.st-key-table_panel [data-testid="stDataFrame"] button {

    color: #DCE3ED !important;
}

.st-key-table_panel [data-testid="stDataFrame"] svg {

    color: #AEB8C9 !important;
}


/* ==========================================================
   SAFER DARK DETAIL TABLE
========================================================== */

.safer-table {
    margin-top: 20px;
    width: 100%;
    overflow: hidden;
    border: 1px solid #3E4B67;
    border-radius: 18px;
    background: #121A2B;
    box-shadow: 0 12px 30px rgba(0,0,0,.18);
}

.safer-table-header,
.safer-table-row {
    display: grid;
    grid-template-columns: .55fr 1fr 1.7fr 2fr;
    align-items: center;
}

.safer-table-header {
    min-height: 52px;
    padding: 0 18px;
    background: #263149;
    border-bottom: 1px solid #46536F;
    color: #F2C86B;
    font-size: 16px;
    font-weight: 800;
}

.safer-table-row {
    min-height: 54px;
    padding: 0 18px;
    background: #151E31;
    border-bottom: 1px solid rgba(78,91,119,.52);
    color: #E8EDF5;
    font-size: 15px;
    transition: background .15s ease, transform .15s ease;
}

.safer-table-row:nth-child(odd) {
    background: #172136;
}

.safer-table-row:last-child {
    border-bottom: none;
}

.safer-table-row:hover {
    background: #202C45;
}

.safer-cell {
    padding: 13px 8px;
}

.safer-rank {
    color: #C7D0DE;
    font-weight: 800;
}

.safer-rank.rank-top {
    color: #F3C867;
}

.safer-region {
    color: #FFFFFF;
    font-weight: 800;
}

.safer-population {
    color: #E9EDF4;
    font-variant-numeric: tabular-nums;
    text-align: right;
    padding-right: 28px;
}

.safer-progress-wrap {
    display: flex;
    align-items: center;
    gap: 14px;
}

.safer-progress-track {
    flex: 1;
    height: 10px;
    overflow: hidden;
    border-radius: 999px;
    background: #2C354A;
    border: 1px solid #3D4861;
}

.safer-progress-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #B8862F 0%, #D9A64A 55%, #F1C96D 100%);
    box-shadow: 0 0 10px rgba(217,166,74,.22);
}

.safer-share-value {
    width: 72px;
    color: #F4D487;
    font-weight: 800;
    text-align: right;
    font-variant-numeric: tabular-nums;
}

@media (max-width: 900px) {
    .safer-table-header,
    .safer-table-row {
        grid-template-columns: .55fr .9fr 1.35fr 1.7fr;
    }

    .safer-table-header {
        font-size: 14px;
    }

    .safer-table-row {
        font-size: 14px;
    }
}

/* ==========================================================
   SUMMARY
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
        15px;

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
# PAGE
# ============================================================

with st.container(
    key="local_population_page"
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
                인구 &gt; 지역별 인구
            </div>

            <div class="page-title">
                지역별 인구 현황
            </div>

            <div class="page-sub">
                e-나라지표 지역별 인구 데이터를 기반으로
                전국 17개 시도의 인구 규모와 전국 대비 비중을 비교합니다.
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
    # YEAR FILTER
    # ========================================================

    years = sorted(
        df[
            "year"
        ]
        .dropna()
        .unique()
        .tolist(),
        reverse=True
    )


    f1, empty = st.columns(
        [
            1,
            4,
        ]
    )


    with f1:

        selected_year = st.selectbox(
            "연도",
            years,
            key="local_population_year"
        )


    # ========================================================
    # SELECTED YEAR
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
    # NATIONAL ROW
    # ========================================================

    national_row = (
        year_df[
            year_df[
                "region_name"
            ] == "전국"
        ]
        .copy()
    )


    # ========================================================
    # REGION DATA
    # ========================================================

    region_df = (
        year_df[
            year_df[
                "region_name"
            ] != "전국"
        ]
        .copy()
    )


    region_df = (
        region_df[
            region_df[
                "population"
            ] > 0
        ]
        .copy()
    )


    # ========================================================
    # NATIONAL POPULATION
    # ========================================================

    if not national_row.empty:

        national_population = float(
            national_row.iloc[0][
                "population"
            ]
        )

    else:

        national_population = float(
            region_df[
                "population"
            ].sum()
        )


    # ========================================================
    # SHARE
    # ========================================================

    if national_population > 0:

        region_df[
            "share"
        ] = (
            region_df[
                "population"
            ]
            / national_population
            * 100
        )

    else:

        region_df[
            "share"
        ] = 0


    # ========================================================
    # RANK
    # ========================================================

    region_df = (
        region_df
        .sort_values(
            "population",
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )


    region_df[
        "rank"
    ] = (
        region_df.index
        + 1
    )


    # ========================================================
    # TOP / LOW REGION
    # ========================================================

    if not region_df.empty:

        top_region = str(
            region_df.iloc[0][
                "region_name"
            ]
        )


        top_population = float(
            region_df.iloc[0][
                "population"
            ]
        )


        low_region = str(
            region_df.iloc[-1][
                "region_name"
            ]
        )


        low_population = float(
            region_df.iloc[-1][
                "population"
            ]
        )

    else:

        top_region = "-"
        top_population = 0

        low_region = "-"
        low_population = 0


    # ========================================================
    # CAPITAL AREA
    #
    # 수도권 = 서울 + 경기 + 인천
    # ========================================================

    CAPITAL_REGIONS = [
        "서울",
        "경기",
        "인천",
    ]


    capital_population = float(
        region_df[
            region_df[
                "region_name"
            ].isin(
                CAPITAL_REGIONS
            )
        ][
            "population"
        ].sum()
    )


    capital_share = (
        capital_population
        / national_population
        * 100
        if national_population > 0
        else 0
    )


    # ========================================================
    # AVERAGE
    # ========================================================

    if not region_df.empty:

        average_population = float(
            region_df[
                "population"
            ].mean()
        )

    else:

        average_population = 0


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
                    {selected_year}년 전국 인구
                </div>

                <div class="kpi-value">
                    {format_korean_people(national_population)}
                </div>

            </div>
            """
        )


    with k2:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    인구 최다 지역
                </div>

                <div class="kpi-value">
                    {top_region}
                </div>

            </div>
            """
        )


    with k3:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    수도권 전국 비중
                </div>

                <div class="kpi-value">
                    {capital_share:.1f}%
                </div>

            </div>
            """
        )


    with k4:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    시도 평균 인구
                </div>

                <div class="kpi-value">
                    {format_korean_people(average_population)}
                </div>

            </div>
            """
        )


    # ========================================================
    # BAR + DONUT
    # ========================================================

    left, right = st.columns(
        [
            1.25,
            1,
        ],
        gap="medium"
    )


    # ========================================================
    # LEFT - BAR
    # ========================================================

    with left:

        with st.container(
            key="region_bar_panel"
        ):

            st.html(
                f"""
                <div class="panel-title">
                    {selected_year}년 지역별 인구수 비교
                </div>

                <div class="panel-sub">
                    전국 17개 시도의 인구 규모를 비교합니다.
                    X축 단위는 만 명입니다.
                </div>
                """
            )


            chart_df = (
                region_df
                .sort_values(
                    "population",
                    ascending=True
                )
                .copy()
            )


            # --------------------------------------------
            # DB 단위: 천 명
            # 그래프 X축: 만 명
            #
            # 13,768천 명
            # -> 1,376.8만 명
            # --------------------------------------------

            chart_df[
                "population_10k"
            ] = (
                chart_df[
                    "population"
                ]
                / 10
            )


            if chart_df.empty:

                st.warning(
                    "표시할 지역별 인구 데이터가 없습니다."
                )

            else:

                max_population_10k = float(
                    chart_df[
                        "population_10k"
                    ].max()
                )


                bar_colors = [

                    "#D9A64A"
                    if region == top_region

                    else "#79B69B"

                    for region
                    in chart_df[
                        "region_name"
                    ]
                ]


                fig_bar = go.Figure(
                    go.Bar(

                        x=chart_df[
                            "population_10k"
                        ],

                        y=chart_df[
                            "region_name"
                        ],

                        orientation="h",

                        marker_color=bar_colors,

                        text=[
                            format_korean_people(
                                value
                            )
                            for value
                            in chart_df[
                                "population"
                            ]
                        ],

                        textposition="outside",

                        textfont=dict(
                            color="#F2F4F8",
                            size=13,
                        ),

                        cliponaxis=False,

                        customdata=chart_df[
                            [
                                "population",
                                "share",
                            ]
                        ],

                        hovertemplate=(
                            "<b>%{y}</b>"
                            "<br>"
                            "인구: %{customdata[0]:,.0f}천 명"
                            "<br>"
                            "전국 대비: %{customdata[1]:.1f}%"
                            "<extra></extra>"
                        ),
                    )
                )


                # --------------------------------------------
                # X AXIS
                # 0 / 500만 / 1,000만 / 1,500만
                # --------------------------------------------

                tick_values = [
                    0,
                    500,
                    1000,
                    1500,
                ]


                tick_text = [
                    "0",
                    "500만",
                    "1,000만",
                    "1,500만",
                ]


                fig_bar.update_layout(

                    height=650,

                    margin=dict(
                        l=85,
                        r=135,
                        t=35,
                        b=70,
                    ),

                    paper_bgcolor="#182035",

                    plot_bgcolor="#182035",

                    showlegend=False,

                    bargap=.25,

                    font=dict(
                        color="#E7EAF0",
                        size=15,
                    ),

                    xaxis=dict(

                        title="인구수 (만 명)",

                        showgrid=True,

                        gridcolor="#35405A",

                        zeroline=False,

                        tickmode="array",

                        tickvals=tick_values,

                        ticktext=tick_text,

                        range=[
                            0,
                            max_population_10k * 1.20
                        ],

                        tickfont=dict(
                            color="#C8CFDB",
                            size=13,
                        ),
                    ),

                    yaxis=dict(

                        title=None,

                        showgrid=False,

                        automargin=True,

                        tickfont=dict(
                            color="#F0F2F6",
                            size=14,
                        ),
                    ),
                )


                st.plotly_chart(

                    fig_bar,

                    use_container_width=True,

                    config={
                        "displayModeBar": False
                    }
                )


    # ========================================================
    # RIGHT - DONUT
    # ========================================================

    with right:

        with st.container(
            key="region_pie_panel"
        ):

            st.html(
                f"""
                <div class="panel-title">
                    {selected_year}년 전국 대비 인구 비중
                </div>

                <div class="panel-sub">
                    각 시도의 인구가 전국 인구에서
                    차지하는 비율을 확인합니다.
                </div>
                """
            )


            pie_df = (
                region_df
                .copy()
                .sort_values(
                    "population",
                    ascending=False
                )
            )


            if pie_df.empty:

                st.warning(
                    "표시할 인구 비중 데이터가 없습니다."
                )

            else:

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


                pie_custom_data = [
                    population_to_people(
                        value
                    )
                    for value
                    in pie_df[
                        "population"
                    ]
                ]


                fig_pie = go.Figure(
                    go.Pie(

                        labels=pie_df[
                            "region_name"
                        ],

                        values=pie_df[
                            "population"
                        ],

                        customdata=pie_custom_data,

                        hole=.58,

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
                            size=12,
                        ),

                        hovertemplate=(
                            "<b>%{label}</b>"
                            "<br>"
                            "인구: %{customdata:,}명"
                            "<br>"
                            "전국 대비: %{percent}"
                            "<extra></extra>"
                        ),
                    )
                )


                fig_pie.add_annotation(

                    x=.5,
                    y=.52,

                    text=(
                        "<b>전국 인구</b>"
                        "<br>"
                        f"{format_korean_people(national_population)}"
                    ),

                    showarrow=False,

                    font=dict(
                        color="#FFFFFF",
                        size=18,
                    ),

                    align="center",
                )


                fig_pie.update_layout(

                    height=650,

                    margin=dict(
                        l=65,
                        r=65,
                        t=35,
                        b=60,
                    ),

                    paper_bgcolor="#182035",

                    plot_bgcolor="#182035",

                    showlegend=False,

                    font=dict(
                        color="#E7EAF0",
                        size=13,
                    ),

                    uniformtext_minsize=11,

                    uniformtext_mode="hide",
                )


                st.plotly_chart(

                    fig_pie,

                    use_container_width=True,

                    config={
                        "displayModeBar": False
                    }
                )


    # ========================================================
    # DETAIL TABLE
    # ========================================================

    with st.container(
        key="table_panel"
    ):

        st.html(
            f"""
            <div class="panel-title">
                {selected_year}년 지역별 인구 상세
            </div>

            <div class="panel-sub">
                지역별 인구수와 전국 대비 비중,
                인구 규모 순위를 한눈에 비교합니다.
            </div>
            """
        )


        table_df = (
            region_df[
                [
                    "rank",
                    "region_name",
                    "population",
                    "share",
                ]
            ]
            .copy()
        )


        table_df[
            "population_people"
        ] = (
            table_df[
                "population"
            ]
            * 1000
        )


        table_df = (
            table_df[
                [
                    "rank",
                    "region_name",
                    "population_people",
                    "share",
                ]
            ]
            .copy()
        )


        table_df.columns = [
            "순위",
            "지역",
            "인구수",
            "전국 대비(%)",
        ]


        table_df[
            "순위"
        ] = (
            table_df[
                "순위"
            ]
            .astype(int)
        )


        table_df[
            "인구수"
        ] = (
            table_df[
                "인구수"
            ]
            .round()
            .astype(int)
        )


        table_df[
            "전국 대비(%)"
        ] = (
            table_df[
                "전국 대비(%)"
            ]
            .round(2)
        )


        max_share_for_bar = (
            max(
                float(
                    table_df[
                        "전국 대비(%)"
                    ].max()
                ),
                1.0
            )
            if not table_df.empty
            else 1.0
        )


        # ====================================================
        # SAFER DARK HTML TABLE
        # ====================================================

        if table_df.empty:
            st.info("표시할 지역별 인구 데이터가 없습니다.")
        else:
            max_share = max(float(table_df["전국 대비(%)"].max()), 1.0)

            rows_html = []

            for _, row in table_df.sort_values("순위").iterrows():
                rank = int(row["순위"])
                region = str(row["지역"])
                population = int(row["인구수"])
                share = float(row["전국 대비(%)"])
                bar_width = max(0.0, min(100.0, share / max_share * 100))

                rank_class = " rank-top" if rank <= 3 else ""

                rows_html.append(
                    f"""
                    <div class="safer-table-row">
                        <div class="safer-cell safer-rank{rank_class}">{rank}위</div>
                        <div class="safer-cell safer-region">{region}</div>
                        <div class="safer-cell safer-population">{population:,}명</div>
                        <div class="safer-cell safer-share">
                            <div class="safer-progress-wrap">
                                <div class="safer-progress-track">
                                    <div class="safer-progress-fill" style="width:{bar_width:.2f}%"></div>
                                </div>
                                <span class="safer-share-value">{share:.2f}%</span>
                            </div>
                        </div>
                    </div>
                    """
                )

            st.html(
                f"""
                <div class="safer-table">
                    <div class="safer-table-header">
                        <div>순위</div>
                        <div>지역</div>
                        <div>인구수</div>
                        <div>전국 대비 비중</div>
                    </div>
                    {''.join(rows_html)}
                </div>
                """
            )


    # ========================================================
    # SUMMARY
    # ========================================================

    national_people = (
        population_to_people(
            national_population
        )
    )


    top_people = (
        population_to_people(
            top_population
        )
    )


    low_people = (
        population_to_people(
            low_population
        )
    )


    capital_people = (
        population_to_people(
            capital_population
        )
    )


    st.html(
        f"""
        <div class="info-box">

            <b>{selected_year}년 지역별 인구 분석 요약</b>
            <br><br>

            {selected_year}년 전국 인구는
            <b>{national_people:,}명</b>입니다.
            <br>

            인구가 가장 많은 지역은
            <b>{top_region}</b>으로
            <b>{top_people:,}명</b>입니다.
            <br>

            서울·경기·인천을 합한 수도권 인구는
            <b>{capital_people:,}명</b>으로,
            전국 인구의 약
            <b>{capital_share:.1f}%</b>를 차지합니다.
            <br>

            인구가 가장 적은 지역은
            <b>{low_region}</b>으로
            <b>{low_people:,}명</b>입니다.

        </div>
        """
    )