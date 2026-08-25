import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sqlalchemy import text


# ============================================================
# PROJECT ROOT
# SAFE/streamlit/pages/accident/weather.py
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
def load_weather_accident():

    engine = get_engine()

    query = text(
        """
        SELECT
            id,
            age_group,
            year,
            weather,
            accidents
        FROM driver_weather_accident
        ORDER BY year, age_group, weather
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

    df = load_weather_accident()

except Exception as e:

    st.error(
        f"MySQL 기상별 교통사고 데이터 조회 실패\n\n{e}"
    )

    st.stop()


# ============================================================
# CLEAN
# ============================================================

df["age_group"] = (
    df["age_group"]
    .fillna("")
    .astype(str)
    .str.strip()
)


df["weather"] = (
    df["weather"]
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


df = (
    df[
        df["year"].notna()
    ]
    .copy()
)


df["year"] = (
    df["year"]
    .astype(int)
)


# ============================================================
# INVALID
# ============================================================

INVALID_VALUES = [
    "",
    "계",
    "합계",
    "총계",
    "전체",
]


df = (
    df[
        ~df["weather"].isin(
            INVALID_VALUES
        )
    ]
    .copy()
)


# ============================================================
# AGE NORMALIZE
# ============================================================

AGE_REPLACE = {

    "19세이하": "19세 이하",
    "19세 이하": "19세 이하",

    "20-29세": "20~29세",
    "20~29세": "20~29세",

    "30-39세": "30~39세",
    "30~39세": "30~39세",

    "40-49세": "40~49세",
    "40~49세": "40~49세",

    "50-59세": "50~59세",
    "50~59세": "50~59세",

    "60-64세": "60~64세",
    "60~64세": "60~64세",

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


df["age_group"] = (
    df["age_group"]
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
# WEATHER NORMALIZE
# ============================================================

WEATHER_REPLACE = {

    "맑음": "맑음",
    "맑음 ": "맑음",

    "흐림": "흐림",

    "비": "비",
    "우천": "비",

    "눈": "눈",
    "강설": "눈",

    "안개": "안개",

    "기타": "기타",

    "불명": "불명",
    "미상": "불명",
}


def normalize_weather(value):

    value = str(value).strip()

    return WEATHER_REPLACE.get(
        value,
        value
    )


WEATHER_ICONS = {
    "전체": "🌦️",
    "맑음": "☀️",
    "흐림": "☁️",
    "비": "🌧️",
    "눈": "❄️",
    "안개": "🌫️",
    "기타": "🌤️",
}


def weather_with_icon(value):

    value = str(value)

    if value in ["", "-"]:
        return value

    icon = WEATHER_ICONS.get(value, "🌡️")

    return f"{value} {icon}"


df["weather"] = (
    df["weather"]
    .apply(
        normalize_weather
    )
)


# ============================================================
# GROUP DUPLICATE
# ============================================================

df = (
    df
    .groupby(
        [
            "age_group",
            "year",
            "weather",
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


age_groups = sorted(
    df["age_group"]
    .dropna()
    .unique()
    .tolist(),
    key=age_sort_key
)


weather_list = sorted(
    df["weather"]
    .dropna()
    .unique()
    .tolist()
)


if not years:

    st.warning(
        "기상상태별 교통사고 데이터가 없습니다."
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

.st-key-weather_page {

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

    letter-spacing: 1.3px;

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

    word-break: keep-all;
}


/* ==========================================================
   PANELS
========================================================== */

.st-key-weather_rank_panel,
.st-key-age_panel,
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


.fit-low {

    color: #E7BE69 !important;

    font-weight: 900;
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

/* ==========================================================
   ANALYSIS / PREDICTION SECTION
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

.section-divider {
    height: 1px;
    margin: 42px 0 4px 0;
    background: linear-gradient(
        90deg,
        rgba(217,166,74,0),
        rgba(217,166,74,.9) 18%,
        rgba(92,107,137,.9) 82%,
        rgba(92,107,137,0)
    );
}



/* ==========================================================
   DETAIL TOGGLE
========================================================== */

.st-key-weather_detail_toggle button {
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

.st-key-weather_detail_toggle button * {
    color: #E7EAF0 !important;
    -webkit-text-fill-color: #E7EAF0 !important;
    opacity: 1 !important;
}

.st-key-weather_detail_toggle button:hover {
    background: #202A42 !important;
    border-color: #D6A348 !important;
    color: #F1C66A !important;
}

.st-key-weather_detail_toggle button:hover * {
    color: #F1C66A !important;
    -webkit-text-fill-color: #F1C66A !important;
}

.st-key-weather_detail_panel {
    background: #182035;
    border: 1px solid #394560;
    border-radius: 14px;
    padding: 18px;
    margin-top: 10px;
}

.weather-dark-table-wrap {
    width: 100%;
    max-height: 560px;
    overflow-y: auto;
    overflow-x: auto;
    background: #182035;
    border: 1px solid #3A4662;
    border-radius: 12px;
}

.weather-dark-table {
    width: 100%;
    border-collapse: collapse;
    background: #182035;
    color: #E7EAF0;
    font-size: 13px;
}

.weather-dark-table thead {
    position: sticky;
    top: 0;
    z-index: 2;
}

.weather-dark-table th {
    background: #202A42;
    color: #D6A348;
    font-weight: 900;
    text-align: center;
    padding: 14px 16px;
    border-bottom: 1px solid #4A5670;
    white-space: nowrap;
}

.weather-dark-table td {
    background: #182035;
    color: #E7EAF0;
    font-weight: 600;
    text-align: center;
    padding: 12px 16px;
    border-bottom: 1px solid #303B55;
    white-space: nowrap;
}

.weather-dark-table tbody tr:nth-child(even) td {
    background: #1B243A;
}

.weather-dark-table tbody tr:hover td {
    background: #222D47;
    color: #FFFFFF;
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
    key="weather_page"
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
                교통사고 &gt; 기상상태별 사고
            </div>

            <div class="page-title">
                기상상태별 교통사고 분석
            </div>

            <div class="page-sub">
                가해운전자 연령대와 기상상태에 따른 교통사고 발생 규모를 비교하고,
                연도별 사고 추세를 기반으로 향후 사고 규모를 예측합니다.
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
            key="weather_year"
        )


    with f2:

        weather_age_options = [
            "전체"
        ] + age_groups


        default_weather_age_index = (
            weather_age_options.index(
                "65세 이상"
            )
            if "65세 이상" in weather_age_options
            else 0
        )


        selected_age = st.selectbox(
            "연령대",
            weather_age_options,
            index=default_weather_age_index,
            key="weather_age"
        )


    with f3:

        selected_weather = st.selectbox(
            "기상상태",
            ["전체"] + weather_list,
            format_func=weather_with_icon,
            key="weather_type"
        )


    # ========================================================
    # FILTER DATA
    # ========================================================

    filtered_df = (
        df.copy()
    )


    if selected_age != "전체":

        filtered_df = filtered_df[
            filtered_df[
                "age_group"
            ] == selected_age
        ]


    if selected_weather != "전체":

        filtered_df = filtered_df[
            filtered_df[
                "weather"
            ] == selected_weather
        ]


    year_filtered_df = filtered_df[
        filtered_df[
            "year"
        ] == selected_year
    ].copy()


    year_all_df = df[
        df[
            "year"
        ] == selected_year
    ].copy()


    # ========================================================
    # KPI
    # ========================================================

    selected_accidents = int(
        year_filtered_df[
            "accidents"
        ].sum()
    )


    weather_summary = (
        year_all_df
        .groupby(
            "weather",
            as_index=False
        )["accidents"]
        .sum()
        .sort_values(
            "accidents",
            ascending=False
        )
    )


    if not weather_summary.empty:

        top_weather = str(
            weather_summary.iloc[0][
                "weather"
            ]
        )


        top_weather_accidents = int(
            weather_summary.iloc[0][
                "accidents"
            ]
        )

    else:

        top_weather = "-"
        top_weather_accidents = 0


    age_summary = (
        year_all_df
        .groupby(
            "age_group",
            as_index=False
        )["accidents"]
        .sum()
        .sort_values(
            "accidents",
            ascending=False
        )
    )


    if not age_summary.empty:

        top_age = str(
            age_summary.iloc[0][
                "age_group"
            ]
        )


        top_age_accidents = int(
            age_summary.iloc[0][
                "accidents"
            ]
        )

    else:

        top_age = "-"
        top_age_accidents = 0


    annual_total = int(
        year_all_df[
            "accidents"
        ].sum()
    )


    selected_share = (
        selected_accidents
        / annual_total
        * 100
        if annual_total > 0
        else 0
    )


    # ========================================================
    # KPI CARDS
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
                    {annual_total:,}건
                </div>

            </div>
            """
        )


    with k2:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    사고 최다 기상상태
                </div>

                <div class="kpi-value">
                    {weather_with_icon(top_weather)}
                </div>

            </div>
            """
        )


    with k3:

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


    with k4:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    현재 조건 사고 비중
                </div>

                <div class="kpi-value">
                    {selected_share:.1f}%
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
    # WEATHER RANK + AGE RANK
    # ========================================================

    left, right = st.columns(
        [1, 1],
        gap="medium"
    )


    # ========================================================
    # WEATHER RANK
    # ========================================================

    with left:

        with st.container(
            key="weather_rank_panel"
        ):

            st.html(
                f"""
                <div class="panel-title">
                    {selected_year}년 기상상태별 사고
                </div>

                <div class="panel-sub">
                    기상상태별 교통사고 발생 규모를 비교합니다.
                </div>
                """
            )


            weather_plot = (
                weather_summary
                .sort_values(
                    "accidents",
                    ascending=True
                )
                .copy()
            )


            weather_plot["weather_label"] = (
                weather_plot["weather"]
                .apply(weather_with_icon)
            )


            max_weather = (
                float(
                    weather_plot[
                        "accidents"
                    ].max()
                )
                if not weather_plot.empty
                else 1
            )


            if max_weather <= 0:
                max_weather = 1


            fig_weather = go.Figure(
                go.Bar(

                    x=weather_plot[
                        "accidents"
                    ],

                    y=weather_plot[
                        "weather_label"
                    ],

                    orientation="h",

                    marker_color=[
                        "#D9A64A"
                        if weather == top_weather
                        else "#79B69B"

                        for weather
                        in weather_plot[
                            "weather"
                        ]
                    ],

                    text=[
                        f"{int(value):,}건"
                        for value
                        in weather_plot[
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


            fig_weather.update_layout(

                height=500,

                margin=dict(
                    l=90,
                    r=100,
                    t=35,
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
                        max_weather * 1.25
                    ]
                ),

                yaxis=dict(
                    title=None
                )
            )


            st.plotly_chart(
                fig_weather,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )


    # ========================================================
    # AGE RANK
    # ========================================================

    with right:

        with st.container(
            key="age_panel"
        ):

            st.html(
                f"""
                <div class="panel-title">
                    {selected_year}년 연령대별 사고
                </div>

                <div class="panel-sub">
                    전체 기상상태를 기준으로 가해운전자 연령대별 사고 규모를 비교합니다.
                </div>
                """
            )


            age_plot = (
                age_summary
                .copy()
            )


            age_plot[
                "sort_key"
            ] = (
                age_plot[
                    "age_group"
                ]
                .apply(
                    age_sort_key
                )
            )


            age_plot = (
                age_plot
                .sort_values(
                    "sort_key",
                    ascending=False
                )
            )


            max_age = (
                float(
                    age_plot[
                        "accidents"
                    ].max()
                )
                if not age_plot.empty
                else 1
            )


            if max_age <= 0:
                max_age = 1


            fig_age = go.Figure(
                go.Bar(

                    x=age_plot[
                        "accidents"
                    ],

                    y=age_plot[
                        "age_group"
                    ],

                    orientation="h",

                    marker_color=[
                        "#E8753B"
                        if age == top_age
                        else "#8DA9C4"

                        for age
                        in age_plot[
                            "age_group"
                        ]
                    ],

                    text=[
                        f"{int(value):,}건"
                        for value
                        in age_plot[
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


            fig_age.update_layout(

                height=500,

                margin=dict(
                    l=90,
                    r=100,
                    t=35,
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
                        max_age * 1.25
                    ]
                ),

                yaxis=dict(
                    title=None
                )
            )


            st.plotly_chart(
                fig_age,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )


    # ========================================================
    # AUTO ANALYSIS
    # ========================================================

    top_weather_share = (
        top_weather_accidents
        / annual_total
        * 100
        if annual_total > 0
        else 0
    )


    top_age_share = (
        top_age_accidents
        / annual_total
        * 100
        if annual_total > 0
        else 0
    )


    st.html(
        f"""
        <div class="analysis-box">

            <div class="analysis-title">
                {selected_year}년 기상상태·연령대 사고 분석
            </div>

            {selected_year}년 전체 교통사고는
            <b>{annual_total:,}건</b>입니다.

            <br>

            사고가 가장 많이 집계된 기상상태는
            <b>{weather_with_icon(top_weather)}</b>으로
            <b>{top_weather_accidents:,}건</b>이며,
            전체의 약
            <b>{top_weather_share:.1f}%</b>를 차지합니다.

            <br>

            사고건수가 가장 많은 가해운전자 연령대는
            <b>{top_age}</b>로
            <b>{top_age_accidents:,}건</b>이며,
            전체의 약
            <b>{top_age_share:.1f}%</b>입니다.

            <br><br>

            ※ 기상상태별 사고건수만으로
            특정 날씨의 사고 위험도가 더 높다고 단정할 수는 없습니다.
            실제 위험도를 비교하려면 각 기상상태의 노출시간,
            교통량 등의 추가 정보가 필요합니다.

        </div>
        """
    )


    # ========================================================
    # TREND
    # ========================================================

    with st.container(
        key="trend_panel"
    ):

        trend_label_parts = []


        if selected_age != "전체":

            trend_label_parts.append(
                selected_age
            )


        if selected_weather != "전체":

            trend_label_parts.append(
                weather_with_icon(selected_weather)
            )


        trend_label = (
            " · ".join(
                trend_label_parts
            )
            if trend_label_parts
            else "전체"
        )


        st.html(
            f"""
            <div class="panel-title">
                {trend_label} 연도별 사고 추이
            </div>

            <div class="panel-sub">
                현재 선택한 연령대와 기상상태 조건의
                연도별 교통사고 변화를 확인합니다.
            </div>
            """
        )


        trend_df = (
            filtered_df
            .groupby(
                "year",
                as_index=False
            )["accidents"]
            .sum()
            .sort_values(
                "year"
            )
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
                    width=4
                ),

                marker=dict(
                    color="#D9A64A",
                    size=9
                ),

                text=[
                    f"{int(value):,}"
                    for value
                    in trend_df[
                        "accidents"
                    ]
                ],

                textposition="top center",

                hovertemplate=(
                    "<b>%{x}년</b>"
                    "<br>"
                    "사고: %{y:,}건"
                    "<extra></extra>"
                )
            )
        )


        fig_trend.update_layout(

            height=520,

            margin=dict(
                l=80,
                r=60,
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
                title="연도",
                dtick=1,
                showgrid=False
            ),

            yaxis=dict(
                title="교통사고 건수(건)",
                gridcolor="#35405A",
                tickformat=",",
                rangemode="tozero"
            )
        )


        st.plotly_chart(
            fig_trend,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
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
                기상상태별 교통사고 미래 예측
            </div>

            <div class="panel-sub">
                과거 연도별 사고건수를 기반으로
                향후 사고 발생 추세를 예측합니다.
                <br>
                현재 데이터는 연 단위이므로
                <b>Linear Trend Regression</b>을 적용합니다.
            </div>
            """
        )


        p1, p2, p3, empty = st.columns(
            [1, 1, 1.5, 2]
        )


        with p1:

            predict_age_options = [
                "전체"
            ] + age_groups


            predict_age_index = (
                predict_age_options.index(
                    selected_age
                )
                if selected_age in predict_age_options
                else (
                    predict_age_options.index(
                        "65세 이상"
                    )
                    if "65세 이상" in predict_age_options
                    else 0
                )
            )


            predict_age = st.selectbox(
                "예측 연령대",
                predict_age_options,
                index=predict_age_index,
                key="weather_predict_age"
            )


        with p2:

            predict_weather = st.selectbox(
                "예측 기상상태",
                ["전체"] + weather_list,
                index=(
                    0
                    if selected_weather == "전체"
                    else (
                        ["전체"] + weather_list
                    ).index(
                        selected_weather
                    )
                ),
                format_func=weather_with_icon,
                key="weather_predict_weather"
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
                key="weather_predict_period"
            )


        # ====================================================
        # PREDICTION FILTER
        # ====================================================

        prediction_df = (
            df.copy()
        )


        if predict_age != "전체":

            prediction_df = prediction_df[
                prediction_df[
                    "age_group"
                ] == predict_age
            ]


        if predict_weather != "전체":

            prediction_df = prediction_df[
                prediction_df[
                    "weather"
                ] == predict_weather
            ]


        prediction_source = (
            prediction_df
            .groupby(
                "year",
                as_index=False
            )["accidents"]
            .sum()
            .sort_values(
                "year"
            )
        )


        prediction_label_parts = []


        if predict_age != "전체":

            prediction_label_parts.append(
                predict_age
            )


        if predict_weather != "전체":

            prediction_label_parts.append(
                weather_with_icon(predict_weather)
            )


        prediction_label = (
            " · ".join(
                prediction_label_parts
            )
            if prediction_label_parts
            else "전체"
        )


        horizon = {
            "1년": 1,
            "5년": 5,
            "10년": 10
        }[
            predict_period
        ]


        if len(
            prediction_source
        ) < 2:

            st.warning(
                "미래 예측을 수행하려면 최소 2개 연도의 데이터가 필요합니다."
            )

        else:

            # =================================================
            # MODEL
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


            slope, intercept = (
                np.polyfit(
                    x,
                    y,
                    1
                )
            )


            fitted = (
                slope * x
                + intercept
            )


            residuals = (
                y - fitted
            )


            # =================================================
            # METRICS
            # =================================================

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
            # FUTURE
            # =================================================

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
            # GRAPH
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
                        color="#A0C9AC",
                        size=9
                    ),

                    hovertemplate=(
                        "<b>%{x}년</b>"
                        "<br>"
                        "실제 사고: %{y:,}건"
                        "<extra></extra>"
                    )
                )
            )


            prediction_x = (
                [last_year]
                +
                future_years.tolist()
            )


            prediction_y = (
                [
                    float(
                        y[-1]
                    )
                ]
                +
                future_values.tolist()
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
                        color="#DD8469",
                        size=9
                    ),

                    text=[
                        ""
                    ]
                    +
                    [
                        f"{int(round(value)):,}"
                        for value
                        in future_values
                    ],

                    textposition="top center",

                    hovertemplate=(
                        "<b>%{x}년</b>"
                        "<br>"
                        "예측 사고: %{y:,.0f}건"
                        "<extra></extra>"
                    )
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


            y_max = max(
                float(
                    np.max(y)
                ),
                float(
                    np.max(
                        future_values
                    )
                ),
                1
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
                    title="연도",
                    dtick=1,
                    showgrid=False
                ),

                yaxis=dict(
                    title="교통사고 건수(건)",
                    gridcolor="#35405A",
                    tickformat=",",
                    range=[
                        0,
                        y_max * 1.18
                    ]
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
                    y[-1]
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


            # =================================================
            # MODEL INFO
            # =================================================

            st.html(
                f"""
                <div class="model-box">

                    <div class="model-title">
                        예측 모델 정보
                    </div>

                    <b>예측 대상</b> :
                    {prediction_label}

                    <br>

                    <b>적용 모델</b> :
                    Linear Trend Regression

                    <br>

                    <b>학습 기간</b> :
                    {int(x.min())}년 ~
                    {int(x.max())}년

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

                    현재 데이터는 연도 단위이므로
                    계절성을 분석하는 SARIMA보다
                    장기적인 사고 증가·감소 추세를 설명하기 쉬운
                    <b>Linear Trend Regression</b>을 사용합니다.

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
                        {prediction_label} 사고 미래 예측
                    </div>

                    마지막 실제 연도인
                    <b>{last_year}년</b> 사고는
                    <b>{current_value:,}건</b>입니다.

                    <br>

                    현재 추세가 지속된다고 가정할 경우
                    <b>{last_year + horizon}년</b>
                    예상 사고건수는 약
                    <b>{predicted_value:,}건</b>입니다.

                    <br>

                    마지막 실제 연도 대비
                    <b>{change_value:+,}건</b>,
                    약
                    <b>{change_rate:+.1f}%</b>
                    변화할 것으로 추정됩니다.

                    <br><br>

                    ※ 본 예측은 과거 사고건수 추세만을 이용하며,
                    향후 실제 기상 발생 빈도, 교통량,
                    운전자 수 변화 등의 외부 요인은 반영하지 않습니다.

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
                예측 모델 비교
            </div>

            <div class="panel-sub">
                기상상태별 사고 예측에 활용할 수 있는
                주요 모델의 특징을 비교합니다.
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
                            <th>필요 데이터</th>
                            <th>계절성</th>
                            <th>현재 적합성</th>
                        </tr>

                    </thead>

                    <tbody>

                        <tr>

                            <td class="model-name">
                                Linear Trend
                            </td>

                            <td>
                                <span class="apply-badge apply-on">
                                    적용
                                </span>
                            </td>

                            <td>
                                연도별 사고건수의
                                장기 증가·감소 방향을 추정
                            </td>

                            <td>
                                적은 연도 데이터도 가능
                            </td>

                            <td>
                                미반영
                            </td>

                            <td class="fit-high">
                                높음
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
                                과거 관측값과 오차 구조를
                                기반으로 시계열을 예측
                            </td>

                            <td>
                                충분한 연속 시계열
                            </td>

                            <td>
                                기본 미반영
                            </td>

                            <td class="fit-low">
                                낮음
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
                                ARIMA에 반복적인
                                계절 패턴을 추가
                            </td>

                            <td>
                                월별 또는 분기별 장기 데이터
                            </td>

                            <td>
                                반영 가능
                            </td>

                            <td class="fit-low">
                                매우 낮음
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
                                추세와 변화점,
                                계절성을 자동 모델링
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
                    현재 모델 선정 이유
                </div>

                현재 기상상태별 사고 데이터는
                <b>연도 단위</b>로 구성되어 있습니다.

                <br>

                이 구조에서는 특정 계절의 반복 패턴을 직접 학습하기 어렵기 때문에
                SARIMA보다 연도별 장기 추세를 보여주는
                <b>Linear Trend Regression</b>이 더 적합합니다.

                <br><br>

                향후 월별 기상상태 사고 데이터와
                실제 강수일수·적설일수·안개일수 등의 데이터가 확보되면
                사고건수뿐 아니라 기상 노출량을 고려한
                상대적인 사고 위험 분석으로 확장할 수 있습니다.

            </div>
            """
        )


    # ========================================================
    # DETAIL TABLE
    # ========================================================

    st.write("")


    if "show_weather_detail" not in st.session_state:

        st.session_state[
            "show_weather_detail"
        ] = False


    with st.container(
        key="weather_detail_toggle"
    ):

        detail_open = st.session_state[
            "show_weather_detail"
        ]


        detail_label = (
            "▲ 연령별 교통사고 데이터 닫기"
            if detail_open
            else "▼ 연령별 교통사고 데이터 상세 보기"
        )


        if st.button(
            detail_label,
            key="weather_detail_button",
            use_container_width=True
        ):

            st.session_state[
                "show_weather_detail"
            ] = not detail_open

            st.rerun()


    if st.session_state[
        "show_weather_detail"
    ]:

        with st.container(
            key="weather_detail_panel"
        ):

            detail_df = (
                df[
                    [
                        "year",
                        "age_group",
                        "weather",
                        "accidents",
                    ]
                ]
                .copy()
                .sort_values(
                    [
                        "year",
                        "age_group",
                        "weather",
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
                "연령대",
                "기상상태",
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
                        <td>{row["연령대"]}</td>
                        <td>{weather_with_icon(row["기상상태"])}</td>
                        <td>{row["사고건수"]}</td>
                    </tr>
                """


            st.html(
                f"""
                <div class="weather-dark-table-wrap">

                    <table class="weather-dark-table">

                        <thead>
                            <tr>
                                <th>연도</th>
                                <th>연령대</th>
                                <th>기상상태</th>
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