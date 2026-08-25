import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sqlalchemy import text


# ============================================================
# PROJECT ROOT
# SAFE/streamlit/pages/car/registration_year.py
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
def load_registration_year():

    engine = get_engine()

    query = text(
        """
        SELECT *
        FROM car_registration_year
        """
    )

    with engine.connect() as conn:
        df = pd.read_sql(
            query,
            conn
        )

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    return df

# ============================================================
# LOAD
# ============================================================

try:

    df = load_registration_year()

except Exception as e:

    st.error(
        f"MySQL 데이터 조회 실패\n\n{e}"
    )

    st.stop()


# ============================================================
# BASIC CLEAN
# ============================================================

if "id" in df.columns:

    df = df.drop(
        columns=["id"]
    )


# ============================================================
# COLUMN FINDER
# ============================================================

def find_column(candidates):

    for col in candidates:

        if col in df.columns:
            return col

    return None


# ============================================================
# YEAR COLUMN
# ============================================================

year_col = find_column(
    [
        "year",
        "base_year",
        "registration_year",
        "년도",
        "연도",
    ]
)


# ============================================================
# COUNT COLUMN
# ============================================================

count_col = find_column(
    [
        "count",
        "registration_count",
        "registered_count",
        "vehicle_count",
        "car_count",
        "total",
        "등록대수",
    ]
)


# ============================================================
# VEHICLE TYPE
# ============================================================

car_type_col = find_column(
    [
        "car_type",
        "vehicle_type",
        "vehicle_category",
        "car_category",
        "type",
        "차종",
    ]
)


# ============================================================
# USAGE TYPE
# ============================================================

usage_col = find_column(
    [
        "usage",
        "use_type",
        "purpose",
        "vehicle_usage",
        "car_usage",
        "용도",
    ]
)


# ============================================================
# REQUIRED CHECK
# ============================================================

if year_col is None:

    st.error(
        f"""
        car_registration_yer 테이블에서
        연도 컬럼을 찾을 수 없습니다.

        현재 컬럼:
        {list(df.columns)}
        """
    )

    st.stop()


if count_col is None:

    st.error(
        f"""
        car_registration_yer 테이블에서
        자동차 등록대수 컬럼을 찾을 수 없습니다.

        현재 컬럼:
        {list(df.columns)}
        """
    )

    st.stop()


# ============================================================
# TYPE CLEAN
# ============================================================

df[year_col] = pd.to_numeric(
    df[year_col],
    errors="coerce"
)


df[count_col] = pd.to_numeric(
    df[count_col],
    errors="coerce"
).fillna(0)


df = df[
    df[year_col].notna()
].copy()


df[year_col] = (
    df[year_col]
    .astype(int)
)


# ============================================================
# TEXT CLEAN
# ============================================================

if car_type_col is not None:

    df[car_type_col] = (
        df[car_type_col]
        .fillna("")
        .astype(str)
        .str.strip()
    )


if usage_col is not None:

    df[usage_col] = (
        df[usage_col]
        .fillna("")
        .astype(str)
        .str.strip()
    )


# ============================================================
# TOTAL LABELS
# ============================================================

TOTAL_LABELS = [
    "계",
    "합계",
    "총계",
    "전체",
    "전국",
]


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
   TOP NAV
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


/* ==========================================================
   LOGO
========================================================== */

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

    letter-spacing:
        -1px !important;
}


/* ==========================================================
   ACTIVE
========================================================== */

.st-key-nav_car button {

    color:
        #D6A348 !important;

    font-weight:
        800 !important;
}


/* ==========================================================
   FUTURE BUTTON
========================================================== */

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

.st-key-registration_year_page {

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


.st-key-back_car button:hover {

    color:
        #D6A348 !important;

    border-color:
        #D6A348 !important;
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

    border-color:
        #D1D5DE !important;

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

    font-weight:
        500 !important;
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


.kpi-positive {

    color:
        #79C5A2;
}


.kpi-negative {

    color:
        #E07C64;
}


/* ==========================================================
   PANEL
========================================================== */

.st-key-line_panel,
.st-key-growth_panel {

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
        13px;

    line-height:
        1.8;
}



/* ==========================================================
   DETAIL TOGGLE BUTTON
========================================================== */

.st-key-year_detail_toggle button {

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


.st-key-year_detail_toggle button * {

    color: #E7EAF0 !important;

    -webkit-text-fill-color: #E7EAF0 !important;

    opacity: 1 !important;
}


.st-key-year_detail_toggle button:hover {

    background: #202A42 !important;

    border-color: #D6A348 !important;

    color: #F1C66A !important;
}


.st-key-year_detail_toggle button:hover * {

    color: #F1C66A !important;

    -webkit-text-fill-color: #F1C66A !important;
}


/* ==========================================================
   DETAIL TABLE PANEL
========================================================== */

.st-key-year_detail_panel {

    background: #182035;

    border: 1px solid #394560;

    border-radius: 14px;

    padding: 18px 18px 20px 18px;

    margin-top: 10px;
}

/* ==========================================================
   RESPONSIVE
========================================================== */

@media(max-width:1100px) {

    .page-title {
        font-size: 34px;
    }


    .st-key-registration_year_page {
        padding: 24px;
    }
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
    key="registration_year_page"
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
                자동차 &gt; 자동차 등록 현황
            </div>

            <div class="page-title">
                연도별 자동차 등록 현황
            </div>

            <div class="page-sub">
                연도별 자동차 등록대수 변화를 비교하여
                국내 자동차 보유 규모의 장기적인 증가·감소 추세를 확인합니다.
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
    # AVAILABLE YEARS
    # ========================================================

    all_years = sorted(
        df[
            year_col
        ]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )


    if not all_years:

        st.warning(
            "연도 데이터가 없습니다."
        )

        st.stop()


    # ========================================================
    # FILTERS
    # ========================================================

    f1, f2, f3, f4 = st.columns(
        [
            1.2,
            1,
            1,
            1.8,
        ]
    )


    # ========================================================
    # YEAR RANGE
    # ========================================================

    with f1:

        selected_year_range = st.select_slider(

            "연도 범위",

            options=all_years,

            value=(
                all_years[0],
                all_years[-1]
            )
        )


    # ========================================================
    # CAR TYPE
    # ========================================================

    with f2:

        if car_type_col is not None:

            car_type_values = sorted(
                [
                    value
                    for value
                    in df[
                        car_type_col
                    ]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                    if value not in TOTAL_LABELS
                    and value != ""
                ]
            )


            selected_car_type = st.selectbox(
                "차량 유형",
                [
                    "전체"
                ] + car_type_values
            )


        else:

            selected_car_type = "전체"


    # ========================================================
    # USAGE
    # ========================================================

    with f3:

        if usage_col is not None:

            usage_values = sorted(
                [
                    value
                    for value
                    in df[
                        usage_col
                    ]
                    .dropna()
                    .astype(str)
                    .unique()
                    .tolist()
                    if value not in TOTAL_LABELS
                    and value != ""
                ]
            )


            selected_usage = st.selectbox(
                "용도",
                [
                    "전체"
                ] + usage_values
            )


        else:

            selected_usage = "전체"


    # ========================================================
    # FILTER DATA
    # ========================================================

    start_year = int(
        selected_year_range[0]
    )


    end_year = int(
        selected_year_range[1]
    )


    filtered = df[
        (
            df[
                year_col
            ] >= start_year
        )
        &
        (
            df[
                year_col
            ] <= end_year
        )
    ].copy()


    # ========================================================
    # CAR TYPE FILTER
    # ========================================================

    if car_type_col is not None:

        if selected_car_type != "전체":

            filtered = filtered[
                filtered[
                    car_type_col
                ].astype(str)
                == selected_car_type
            ]


        else:

            # 합계 행 존재 시 합계 우선
            total_rows = filtered[
                filtered[
                    car_type_col
                ].astype(str)
                .isin(
                    TOTAL_LABELS
                )
            ]


            if not total_rows.empty:

                filtered = (
                    total_rows.copy()
                )


    # ========================================================
    # USAGE FILTER
    # ========================================================

    if usage_col is not None:

        if selected_usage != "전체":

            filtered = filtered[
                filtered[
                    usage_col
                ].astype(str)
                == selected_usage
            ]


        else:

            total_rows = filtered[
                filtered[
                    usage_col
                ].astype(str)
                .isin(
                    TOTAL_LABELS
                )
            ]


            if not total_rows.empty:

                filtered = (
                    total_rows.copy()
                )


    # ========================================================
    # YEAR AGGREGATION
    # ========================================================

    yearly_df = (
        filtered

        .groupby(
            year_col,
            as_index=False
        )[count_col]

        .sum()

        .sort_values(
            year_col
        )

        .reset_index(
            drop=True
        )
    )


    # ========================================================
    # YOY
    # ========================================================

    yearly_df[
        "yoy"
    ] = (
        yearly_df[
            count_col
        ]
        .pct_change()
        * 100
    )


    # ========================================================
    # KPI CALCULATIONS
    # ========================================================

    if yearly_df.empty:

        latest_year = "-"
        latest_count = 0

        previous_count = None
        yoy_latest = 0

        total_growth = 0
        cagr = 0


    else:

        latest_year = int(
            yearly_df.iloc[-1][
                year_col
            ]
        )


        latest_count = int(
            yearly_df.iloc[-1][
                count_col
            ]
        )


        # ====================================================
        # PREVIOUS YEAR
        # ====================================================

        if len(yearly_df) >= 2:

            previous_count = float(
                yearly_df.iloc[-2][
                    count_col
                ]
            )


            if previous_count != 0:

                yoy_latest = (
                    (
                        latest_count
                        - previous_count
                    )
                    / previous_count
                    * 100
                )

            else:

                yoy_latest = 0


        else:

            previous_count = None
            yoy_latest = 0


        # ====================================================
        # TOTAL GROWTH
        # ====================================================

        first_count = float(
            yearly_df.iloc[0][
                count_col
            ]
        )


        first_year = int(
            yearly_df.iloc[0][
                year_col
            ]
        )


        if first_count != 0:

            total_growth = (
                (
                    latest_count
                    - first_count
                )
                / first_count
                * 100
            )

        else:

            total_growth = 0


        # ====================================================
        # CAGR
        # ====================================================

        year_gap = (
            latest_year
            - first_year
        )


        if (
            first_count > 0
            and latest_count > 0
            and year_gap > 0
        ):

            cagr = (
                (
                    latest_count
                    / first_count
                )
                ** (
                    1 / year_gap
                )
                - 1
            ) * 100

        else:

            cagr = 0


    # ========================================================
    # KPI CLASS
    # ========================================================

    yoy_class = (
        "kpi-positive"
        if yoy_latest >= 0
        else "kpi-negative"
    )


    growth_class = (
        "kpi-positive"
        if total_growth >= 0
        else "kpi-negative"
    )


    cagr_class = (
        "kpi-positive"
        if cagr >= 0
        else "kpi-negative"
    )


    yoy_symbol = (
        "▲"
        if yoy_latest > 0
        else "▼"
        if yoy_latest < 0
        else "－"
    )


    growth_symbol = (
        "▲"
        if total_growth > 0
        else "▼"
        if total_growth < 0
        else "－"
    )


    # ========================================================
    # KPI CARDS
    # ========================================================

    st.write("")


    k1, k2, k3, k4 = st.columns(
        4
    )


    # 최신 자동차 등록대수
    with k1:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    {latest_year}년 자동차 등록대수
                </div>

                <div class="kpi-value">
                    {latest_count:,}대
                </div>

            </div>
            """
        )


    # 전년 대비
    with k2:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    전년 대비 증감률
                </div>

                <div class="kpi-value {yoy_class}">
                    {yoy_symbol} {abs(yoy_latest):.2f}%
                </div>

            </div>
            """
        )


    # 기간 전체 증감률
    with k3:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    {start_year}년 대비 증감률
                </div>

                <div class="kpi-value {growth_class}">
                    {growth_symbol} {abs(total_growth):.2f}%
                </div>

            </div>
            """
        )


    # CAGR
    with k4:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    연평균 증가율 CAGR
                </div>

                <div class="kpi-value {cagr_class}">
                    {cagr:+.2f}%
                </div>

            </div>
            """
        )


    # ========================================================
    # MAIN LINE CHART
    # ========================================================

    with st.container(
        key="line_panel"
    ):

        st.html(
            """
            <div class="panel-title">
                연도별 자동차 등록대수 추이
            </div>

            <div class="panel-sub">
                X축: 연도 ·
                Y축: 자동차 등록대수(대) ·
                각 연도의 등록대수를 연결하여 장기적인 변화 추이를 확인합니다.
            </div>
            """
        )


        if yearly_df.empty:

            st.warning(
                "선택한 조건에 해당하는 데이터가 없습니다."
            )


        else:

            fig_line = go.Figure()


            # =================================================
            # AREA
            # =================================================

            fig_line.add_trace(
                go.Scatter(

                    x=yearly_df[
                        year_col
                    ],

                    y=yearly_df[
                        count_col
                    ],

                    mode="lines+markers+text",

                    name="자동차 등록대수",

                    line=dict(
                        color="#79C5A2",
                        width=4,
                    ),

                    marker=dict(
                        size=10,
                        color="#D9A64A",
                        line=dict(
                            color="#182035",
                            width=2
                        )
                    ),

                    text=[
                        f"{int(value):,}"
                        for value
                        in yearly_df[
                            count_col
                        ]
                    ],

                    textposition="top center",

                    textfont=dict(
                        color="#F2F4F8",
                        size=12,
                    ),

                    fill="tozeroy",

                    fillcolor="rgba(121,197,162,0.08)",

                    hovertemplate=(
                        "<b>%{x}년</b>"
                        "<br>"
                        "자동차 등록대수: %{y:,}대"
                        "<extra></extra>"
                    ),
                )
            )


            # =================================================
            # LAYOUT
            # =================================================

            fig_line.update_layout(

                height=520,

                margin=dict(
                    l=95,
                    r=55,
                    t=60,
                    b=75,
                ),

                paper_bgcolor="#182035",

                plot_bgcolor="#182035",

                showlegend=False,

                font=dict(
                    color="#E7EAF0",
                    size=13,
                ),

                hovermode="x unified",

                xaxis=dict(

                    title=dict(
                        text="연도",

                        font=dict(
                            color="#D8DEE8",
                            size=14,
                        ),
                    ),

                    dtick=1,

                    tickformat=".0f",

                    showgrid=False,

                    tickfont=dict(
                        color="#C6CDD9",
                        size=13,
                    ),

                    linecolor="#48546B",
                ),

                yaxis=dict(

                    title=dict(
                        text="자동차 등록대수(대)",

                        font=dict(
                            color="#D8DEE8",
                            size=14,
                        ),
                    ),

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
                fig_line,

                use_container_width=True,

                config={
                    "displayModeBar": False,
                },
            )


    # ========================================================
    # YOY GROWTH CHART
    # ========================================================

    with st.container(
        key="growth_panel"
    ):

        st.html(
            """
            <div class="panel-title">
                연도별 자동차 등록 증감률
            </div>

            <div class="panel-sub">
                전년도 대비 자동차 등록대수가 얼마나 증가하거나 감소했는지
                백분율로 비교합니다.
            </div>
            """
        )


        growth_df = yearly_df[
            yearly_df[
                "yoy"
            ].notna()
        ].copy()


        if growth_df.empty:

            st.info(
                "증감률을 계산하려면 최소 2개 연도의 데이터가 필요합니다."
            )


        else:

            bar_colors = [

                "#79C5A2"
                if value >= 0

                else "#D5725B"

                for value
                in growth_df[
                    "yoy"
                ]
            ]


            fig_growth = go.Figure(
                go.Bar(

                    x=growth_df[
                        year_col
                    ],

                    y=growth_df[
                        "yoy"
                    ],

                    marker=dict(
                        color=bar_colors
                    ),

                    text=[
                        f"{value:+.2f}%"
                        for value
                        in growth_df[
                            "yoy"
                        ]
                    ],

                    textposition="outside",

                    textfont=dict(
                        color="#F2F4F8",
                        size=12,
                    ),

                    hovertemplate=(
                        "<b>%{x}년</b>"
                        "<br>"
                        "전년 대비: %{y:.2f}%"
                        "<extra></extra>"
                    ),
                )
            )


            fig_growth.add_hline(

                y=0,

                line_color="#8B95A8",

                line_width=1.2,
            )


            fig_growth.update_layout(

                height=420,

                margin=dict(
                    l=80,
                    r=45,
                    t=40,
                    b=70,
                ),

                paper_bgcolor="#182035",

                plot_bgcolor="#182035",

                showlegend=False,

                font=dict(
                    color="#E7EAF0",
                    size=13,
                ),

                xaxis=dict(

                    title="연도",

                    dtick=1,

                    tickformat=".0f",

                    showgrid=False,

                    tickfont=dict(
                        color="#C6CDD9",
                        size=12,
                    ),
                ),

                yaxis=dict(

                    title="전년 대비 증감률(%)",

                    ticksuffix="%",

                    showgrid=True,

                    gridcolor="#35405A",

                    zeroline=False,

                    tickfont=dict(
                        color="#C6CDD9",
                        size=12,
                    ),
                ),
            )


            st.plotly_chart(

                fig_growth,

                use_container_width=True,

                config={
                    "displayModeBar": False,
                },
            )


    # ========================================================
    # SUMMARY
    # ========================================================

    if not yearly_df.empty:

        first_year_value = int(
            yearly_df.iloc[0][
                year_col
            ]
        )


        first_count_value = int(
            yearly_df.iloc[0][
                count_col
            ]
        )


        difference = (
            latest_count
            - first_count_value
        )


        direction_text = (
            "증가"
            if difference > 0
            else "감소"
            if difference < 0
            else "변화 없음"
        )


        st.html(
            f"""
            <div class="info-box">

                <b>연도별 자동차 등록 추세 요약</b>
                <br><br>

                {first_year_value}년 자동차 등록대수는
                <b>{first_count_value:,}대</b>,
                {latest_year}년 등록대수는
                <b>{latest_count:,}대</b>입니다.
                <br>

                해당 기간 동안 자동차 등록대수는
                총 <b>{abs(difference):,}대 {direction_text}</b>했으며,
                전체 변화율은
                <b>{total_growth:+.2f}%</b>입니다.
                <br>

                기간의 연평균 증가율(CAGR)은
                <b>{cagr:+.2f}%</b>입니다.

            </div>
            """
        )


    # ========================================================
    # DETAIL TABLE
    # ========================================================

    st.write("")


    # --------------------------------------------------------
    # DETAIL STATE
    # --------------------------------------------------------

    if "show_registration_year_detail" not in st.session_state:

        st.session_state[
            "show_registration_year_detail"
        ] = False


    # --------------------------------------------------------
    # DETAIL TOGGLE
    # --------------------------------------------------------

    with st.container(
        key="year_detail_toggle"
    ):

        detail_open = st.session_state[
            "show_registration_year_detail"
        ]


        detail_button_label = (
            "▲ 연도별 자동차 등록 데이터 닫기"
            if detail_open
            else "▼ 연도별 자동차 등록 데이터 상세 보기"
        )


        if st.button(
            detail_button_label,
            key="registration_year_detail_button",
            use_container_width=True
        ):

            st.session_state[
                "show_registration_year_detail"
            ] = (
                not detail_open
            )

            st.rerun()


    # --------------------------------------------------------
    # DETAIL CONTENT
    # --------------------------------------------------------

    if st.session_state[
        "show_registration_year_detail"
    ]:

        with st.container(
            key="year_detail_panel"
        ):

            table_df = (
                yearly_df[
                    [
                        year_col,
                        count_col,
                        "yoy",
                    ]
                ]
                .copy()
            )


            table_df[
                count_col
            ] = (
                table_df[
                    count_col
                ]
                .round()
                .astype(int)
            )


            table_df[
                "yoy"
            ] = (
                table_df[
                    "yoy"
                ]
                .round(2)
            )


            table_df.columns = [
                "연도",
                "자동차 등록대수",
                "전년 대비 증감률",
            ]


            display_df = (
                table_df
                .copy()
            )


            display_df[
                "연도"
            ] = (
                display_df[
                    "연도"
                ]
                .astype(int)
                .astype(str)
                + "년"
            )


            display_df[
                "자동차 등록대수"
            ] = (
                display_df[
                    "자동차 등록대수"
                ]
                .map(
                    lambda value:
                        f"{int(value):,}대"
                )
            )


            display_df[
                "전년 대비 증감률"
            ] = (
                display_df[
                    "전년 대비 증감률"
                ]
                .map(
                    lambda value:
                        "-"
                        if pd.isna(value)
                        else f"{value:.2f}%"
                )
            )


            table_rows = ""


            for _, row in display_df.iterrows():

                table_rows += f"""
                    <tr>

                        <td>
                            {row["연도"]}
                        </td>

                        <td>
                            {row["자동차 등록대수"]}
                        </td>

                        <td>
                            {row["전년 대비 증감률"]}
                        </td>

                    </tr>
                """


            st.html(
                f"""
                <style>

                .registration-dark-table-wrap {{

                    width: 100%;

                    overflow-x: auto;

                    background: #182035;

                    border: 1px solid #3A4662;

                    border-radius: 12px;
                }}


                .registration-dark-table {{

                    width: 100%;

                    border-collapse: collapse;

                    background: #182035;

                    color: #E7EAF0;

                    font-size: 13px;
                }}


                .registration-dark-table thead {{

                    background: #202A42;
                }}


                .registration-dark-table th {{

                    background: #202A42;

                    color: #D6A348;

                    font-weight: 900;

                    text-align: center;

                    padding: 14px 16px;

                    border-bottom: 1px solid #4A5670;

                    white-space: nowrap;
                }}


                .registration-dark-table td {{

                    background: #182035;

                    color: #E7EAF0;

                    font-weight: 600;

                    text-align: center;

                    padding: 13px 16px;

                    border-bottom: 1px solid #303B55;

                    white-space: nowrap;
                }}


                .registration-dark-table tbody tr:nth-child(even) td {{

                    background: #1B243A;
                }}


                .registration-dark-table tbody tr:hover td {{

                    background: #222D47;

                    color: #FFFFFF;
                }}


                .registration-dark-table tbody tr:last-child td {{

                    border-bottom: none;
                }}

                </style>


                <div class="registration-dark-table-wrap">

                    <table class="registration-dark-table">

                        <thead>

                            <tr>

                                <th>
                                    연도
                                </th>

                                <th>
                                    자동차 등록대수
                                </th>

                                <th>
                                    전년 대비 증감률
                                </th>

                            </tr>

                        </thead>


                        <tbody>

                            {table_rows}

                        </tbody>

                    </table>

                </div>
                """
            )