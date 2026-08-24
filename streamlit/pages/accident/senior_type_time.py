import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sqlalchemy import text


# ============================================================
# PROJECT ROOT
# SAFE/streamlit/pages/accident/senior_type_time.py
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
def load_senior_type_time():

    engine = get_engine()

    query = text(
        """
        SELECT
            id,
            accident_type_main,
            accident_type_middle,
            accident_type_sub,
            year,
            time_slot,
            accidents
        FROM senior_accident_type_time
        ORDER BY
            year,
            accident_type_main,
            accident_type_middle,
            accident_type_sub,
            time_slot
        """
    )

    with engine.connect() as conn:
        return pd.read_sql(query, conn)


# ============================================================
# LOAD
# ============================================================

try:

    df = load_senior_type_time()

except Exception as e:

    st.error(
        f"MySQL 데이터 조회 실패\n\n{e}"
    )

    st.stop()


# ============================================================
# CLEAN
# ============================================================

TEXT_COLUMNS = [
    "accident_type_main",
    "accident_type_middle",
    "accident_type_sub",
    "time_slot",
]


for column in TEXT_COLUMNS:

    df[column] = (
        df[column]
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
# REMOVE TOTAL / INVALID
# ============================================================

INVALID_VALUES = [
    "",
    "계",
    "합계",
    "총계",
    "전체",
    "불명",
    "미상",
]


# 시간대에서만 합계 제거
df = (
    df[
        ~df["time_slot"].isin(
            INVALID_VALUES
        )
    ]
    .copy()
)


# ============================================================
# TIME NORMALIZE
# ============================================================

TIME_REPLACE = {

    "00~02": "00~02시",
    "00~02시": "00~02시",
    "0~2": "00~02시",
    "0~2시": "00~02시",

    "02~04": "02~04시",
    "02~04시": "02~04시",
    "2~4": "02~04시",
    "2~4시": "02~04시",

    "04~06": "04~06시",
    "04~06시": "04~06시",
    "4~6": "04~06시",
    "4~6시": "04~06시",

    "06~08": "06~08시",
    "06~08시": "06~08시",
    "6~8": "06~08시",
    "6~8시": "06~08시",

    "08~10": "08~10시",
    "08~10시": "08~10시",
    "8~10": "08~10시",
    "8~10시": "08~10시",

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

    return TIME_REPLACE.get(
        value,
        value
    )


df["time_slot"] = (
    df["time_slot"]
    .apply(
        normalize_time
    )
)


# ============================================================
# GROUP DUPLICATES
# ============================================================

df = (
    df
    .groupby(
        [
            "accident_type_main",
            "accident_type_middle",
            "accident_type_sub",
            "year",
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


main_types = sorted(
    [
        value
        for value
        in df["accident_type_main"]
        .dropna()
        .unique()
        .tolist()
        if value not in INVALID_VALUES
    ]
)


if not years:

    st.warning(
        "고령운전자 사고유형·시간대 데이터가 없습니다."
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

.st-key-senior_type_time_page {

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
   PANEL
========================================================== */

.st-key-type_rank_panel,
.st-key-time_panel,
.st-key-heatmap_panel,
.st-key-trend_panel,
.st-key-subtype_panel,
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
    key="senior_type_time_page"
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
                교통사고 &gt; 고령운전자 사고유형·시간대
            </div>

            <div class="page-title">
                고령운전자 사고유형·시간대 분석
            </div>

            <div class="page-sub">
                고령운전자 교통사고를 사고유형과 시간대 기준으로 분석하여
                사고가 집중되는 유형과 시간 구간을 파악하고,
                과거 연도별 사고 추세를 기반으로 향후 사고 규모를 예측합니다.
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
    # FILTER 1
    # ========================================================

    f1, f2, f3, empty = st.columns(
        [1, 1.3, 1.3, 1.4]
    )


    with f1:

        selected_year = st.selectbox(
            "기준 연도",
            years,
            key="senior_type_year"
        )


    with f2:

        selected_main = st.selectbox(
            "사고유형 대분류",
            ["전체"] + main_types,
            key="senior_type_main"
        )


    # ========================================================
    # MIDDLE OPTIONS
    # ========================================================

    if selected_main == "전체":

        middle_source = df

    else:

        middle_source = df[
            df[
                "accident_type_main"
            ] == selected_main
        ]


    middle_types = sorted(
        [
            value
            for value
            in middle_source[
                "accident_type_middle"
            ]
            .dropna()
            .unique()
            .tolist()
            if value not in INVALID_VALUES
        ]
    )


    with f3:

        selected_middle = st.selectbox(
            "중분류",
            ["전체"] + middle_types,
            key="senior_type_middle"
        )


    # ========================================================
    # SUB OPTIONS
    # ========================================================

    sub_source = middle_source.copy()


    if selected_middle != "전체":

        sub_source = sub_source[
            sub_source[
                "accident_type_middle"
            ] == selected_middle
        ]


    sub_types = sorted(
        [
            value
            for value
            in sub_source[
                "accident_type_sub"
            ]
            .dropna()
            .unique()
            .tolist()
            if value not in INVALID_VALUES
        ]
    )


    f4, empty2 = st.columns(
        [1, 4]
    )


    with f4:

        selected_sub = st.selectbox(
            "소분류",
            ["전체"] + sub_types,
            key="senior_type_sub"
        )


    # ========================================================
    # FILTER FUNCTION
    # ========================================================

    filtered_df = df.copy()


    if selected_main != "전체":

        filtered_df = filtered_df[
            filtered_df[
                "accident_type_main"
            ] == selected_main
        ]


    if selected_middle != "전체":

        filtered_df = filtered_df[
            filtered_df[
                "accident_type_middle"
            ] == selected_middle
        ]


    if selected_sub != "전체":

        filtered_df = filtered_df[
            filtered_df[
                "accident_type_sub"
            ] == selected_sub
        ]


    year_df = filtered_df[
        filtered_df[
            "year"
        ] == selected_year
    ].copy()


    # ========================================================
    # TYPE LABEL
    # ========================================================

    if selected_sub != "전체":

        selected_type_label = (
            selected_sub
        )

    elif selected_middle != "전체":

        selected_type_label = (
            selected_middle
        )

    elif selected_main != "전체":

        selected_type_label = (
            selected_main
        )

    else:

        selected_type_label = (
            "전체 사고유형"
        )


    # ========================================================
    # KPI
    # ========================================================

    total_accidents = int(
        year_df[
            "accidents"
        ].sum()
    )


    time_summary = (
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


    if not time_summary.empty:

        top_time = str(
            time_summary.iloc[0][
                "time_slot"
            ]
        )

        top_time_accidents = int(
            time_summary.iloc[0][
                "accidents"
            ]
        )

    else:

        top_time = "-"
        top_time_accidents = 0


    # ========================================================
    # MAIN TYPE SUMMARY
    # ========================================================

    year_all_df = (
        df[
            df[
                "year"
            ] == selected_year
        ]
        .copy()
    )


    main_summary = (
        year_all_df[
            ~year_all_df[
                "accident_type_main"
            ].isin(
                INVALID_VALUES
            )
        ]
        .groupby(
            "accident_type_main",
            as_index=False
        )["accidents"]
        .sum()
        .sort_values(
            "accidents",
            ascending=False
        )
    )


    if not main_summary.empty:

        top_type = str(
            main_summary.iloc[0][
                "accident_type_main"
            ]
        )

        top_type_accidents = int(
            main_summary.iloc[0][
                "accidents"
            ]
        )

    else:

        top_type = "-"
        top_type_accidents = 0


    top_time_share = (
        top_time_accidents
        / total_accidents
        * 100
        if total_accidents > 0
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
                    {selected_year}년 선택 유형 사고
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
                    사고 최다 시간대
                </div>

                <div class="kpi-value">
                    {top_time}
                </div>

            </div>
            """
        )


    with k3:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    최다 사고 대분류
                </div>

                <div class="kpi-value">
                    {top_type}
                </div>

            </div>
            """
        )


    with k4:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    최다 시간대 사고 비중
                </div>

                <div class="kpi-value">
                    {top_time_share:.1f}%
                </div>

            </div>
            """
        )


    # ========================================================
    # TYPE RANK + TIME
    # ========================================================

    left, right = st.columns(
        [1, 1],
        gap="medium"
    )


    # ========================================================
    # TYPE RANK
    # ========================================================

    with left:

        with st.container(
            key="type_rank_panel"
        ):

            st.html(
                f"""
                <div class="panel-title">
                    {selected_year}년 사고유형별 규모
                </div>

                <div class="panel-sub">
                    고령운전자 사고 대분류별 사고 발생 건수를 비교합니다.
                </div>
                """
            )


            type_rank_df = (
                main_summary
                .sort_values(
                    "accidents",
                    ascending=True
                )
                .copy()
            )


            max_type = (
                float(
                    type_rank_df[
                        "accidents"
                    ].max()
                )
                if not type_rank_df.empty
                else 1
            )


            if max_type <= 0:
                max_type = 1


            fig_type = go.Figure(
                go.Bar(

                    x=type_rank_df[
                        "accidents"
                    ],

                    y=type_rank_df[
                        "accident_type_main"
                    ],

                    orientation="h",

                    marker_color=[
                        "#D9A64A"
                        if value == top_type
                        else "#79B69B"

                        for value
                        in type_rank_df[
                            "accident_type_main"
                        ]
                    ],

                    text=[
                        f"{int(value):,}건"
                        for value
                        in type_rank_df[
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


            fig_type.update_layout(

                height=520,

                margin=dict(
                    l=120,
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
                        max_type * 1.25
                    ]
                ),

                yaxis=dict(
                    title=None
                )
            )


            st.plotly_chart(
                fig_type,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )


    # ========================================================
    # TIME
    # ========================================================

    with right:

        with st.container(
            key="time_panel"
        ):

            st.html(
                f"""
                <div class="panel-title">
                    {selected_year}년 {selected_type_label} 시간대별 사고
                </div>

                <div class="panel-sub">
                    선택한 사고유형에서 사고가 집중되는 시간대를 확인합니다.
                </div>
                """
            )


            time_plot_df = (
                time_summary
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
                        "#E8753B"
                        if value == top_time
                        else "#8DA9C4"

                        for value
                        in time_plot_df[
                            "time_slot"
                        ]
                    ],

                    text=[
                        f"{int(value):,}건"
                        for value
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
                    )
                )
            )


            fig_time.update_layout(

                height=520,

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
    # ANALYSIS
    # ========================================================

    st.html(
        f"""
        <div class="analysis-box">

            <div class="analysis-title">
                {selected_year}년 사고유형·시간대 분석
            </div>

            현재 선택한 사고유형은
            <b>{selected_type_label}</b>이며,
            총 <b>{total_accidents:,}건</b>의 사고가 발생했습니다.

            <br>

            이 유형에서 사고가 가장 많이 발생한 시간대는
            <b>{top_time}</b>로,
            <b>{top_time_accidents:,}건</b>입니다.

            <br>

            해당 시간대는 선택 유형 전체 사고의 약
            <b>{top_time_share:.1f}%</b>를 차지합니다.

            <br>

            같은 연도 전체 사고 대분류 기준으로
            사고가 가장 많은 유형은
            <b>{top_type}</b>이며,
            총 <b>{top_type_accidents:,}건</b>입니다.

        </div>
        """
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
                {selected_year}년 사고유형 × 시간대 집중도
            </div>

            <div class="panel-sub">
                사고 대분류와 시간대를 함께 비교합니다.
                밝고 붉은 영역일수록 사고가 많이 발생한 조합입니다.
            </div>
            """
        )


        heat_source = (
            year_all_df[
                ~year_all_df[
                    "accident_type_main"
                ].isin(
                    INVALID_VALUES
                )
            ]
            .groupby(
                [
                    "accident_type_main",
                    "time_slot"
                ],
                as_index=False
            )["accidents"]
            .sum()
        )


        heat_df = (
            heat_source
            .pivot_table(
                index="accident_type_main",
                columns="time_slot",
                values="accidents",
                aggfunc="sum",
                fill_value=0
            )
        )


        time_columns = [
            value
            for value in TIME_ORDER
            if value in heat_df.columns
        ]


        extra_columns = [
            value
            for value in heat_df.columns
            if value not in TIME_ORDER
        ]


        heat_df = (
            heat_df
            .reindex(
                columns=(
                    time_columns
                    + extra_columns
                )
            )
            .fillna(0)
        )


        fig_heat = go.Figure(
            go.Heatmap(

                z=heat_df.values,

                x=heat_df.columns,

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

            height=max(
                550,
                len(
                    heat_df.index
                ) * 55
            ),

            margin=dict(
                l=140,
                r=80,
                t=30,
                b=80
            ),

            paper_bgcolor="#182035",

            plot_bgcolor="#182035",

            font=dict(
                color="#E8EDF5"
            ),

            xaxis=dict(
                title="시간대",
                tickangle=-30
            ),

            yaxis=dict(
                title="사고유형"
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
    # MIDDLE / SUB TYPE
    # ========================================================

    with st.container(
        key="subtype_panel"
    ):

        st.html(
            f"""
            <div class="panel-title">
                {selected_year}년 세부 사고유형 분석
            </div>

            <div class="panel-sub">
                현재 필터 조건에서 중분류·소분류별 사고 발생 규모를 확인합니다.
            </div>
            """
        )


        if selected_middle == "전체":

            detail_type_df = (
                year_df[
                    ~year_df[
                        "accident_type_middle"
                    ].isin(
                        INVALID_VALUES
                    )
                ]
                .groupby(
                    "accident_type_middle",
                    as_index=False
                )["accidents"]
                .sum()
                .sort_values(
                    "accidents",
                    ascending=True
                )
            )

            detail_type_column = (
                "accident_type_middle"
            )

            detail_title = (
                "중분류"
            )

        else:

            detail_type_df = (
                year_df[
                    ~year_df[
                        "accident_type_sub"
                    ].isin(
                        INVALID_VALUES
                    )
                ]
                .groupby(
                    "accident_type_sub",
                    as_index=False
                )["accidents"]
                .sum()
                .sort_values(
                    "accidents",
                    ascending=True
                )
            )

            detail_type_column = (
                "accident_type_sub"
            )

            detail_title = (
                "소분류"
            )


        if detail_type_df.empty:

            st.info(
                "현재 조건에 해당하는 세부 사고유형 데이터가 없습니다."
            )

        else:

            top_detail = (
                detail_type_df
                .sort_values(
                    "accidents",
                    ascending=False
                )
                .iloc[0][
                    detail_type_column
                ]
            )


            max_detail = float(
                detail_type_df[
                    "accidents"
                ].max()
            )


            if max_detail <= 0:
                max_detail = 1


            fig_detail = go.Figure(
                go.Bar(

                    x=detail_type_df[
                        "accidents"
                    ],

                    y=detail_type_df[
                        detail_type_column
                    ],

                    orientation="h",

                    marker_color=[
                        "#D9A64A"
                        if value == top_detail
                        else "#79B69B"

                        for value
                        in detail_type_df[
                            detail_type_column
                        ]
                    ],

                    text=[
                        f"{int(value):,}건"
                        for value
                        in detail_type_df[
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


            fig_detail.update_layout(

                height=max(
                    500,
                    len(
                        detail_type_df
                    ) * 34
                ),

                margin=dict(
                    l=150,
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
                        max_detail * 1.25
                    ]
                ),

                yaxis=dict(
                    title=detail_title
                )
            )


            st.plotly_chart(
                fig_detail,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )


    # ========================================================
    # YEAR TREND
    # ========================================================

    with st.container(
        key="trend_panel"
    ):

        st.html(
            f"""
            <div class="panel-title">
                {selected_type_label} 연도별 사고 추이
            </div>

            <div class="panel-sub">
                현재 선택한 사고유형의 연도별 사고 발생 변화를 확인합니다.
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


    # ========================================================
    # FUTURE PREDICTION
    # ========================================================

    with st.container(
        key="predict_panel"
    ):

        st.html(
            """
            <div class="panel-title">
                사고유형별 미래 예측
            </div>

            <div class="panel-sub">
                과거 연도별 고령운전자 사고 건수를 기반으로
                향후 사고 발생 추세를 예측합니다.
                <br>
                현재 데이터는 연 단위이므로
                <b>Linear Trend Regression</b>을 적용합니다.
            </div>
            """
        )


        p1, p2, p3, p4 = st.columns(
            [1.3, 1.3, 1.3, 1.5]
        )


        with p1:

            predict_main = st.selectbox(
                "예측 대분류",
                ["전체"] + main_types,
                index=(
                    0
                    if selected_main == "전체"
                    else (
                        ["전체"]
                        + main_types
                    ).index(
                        selected_main
                    )
                ),
                key="predict_type_main"
            )


        # ====================================================
        # PREDICT MIDDLE
        # ====================================================

        if predict_main == "전체":

            predict_middle_source = df

        else:

            predict_middle_source = df[
                df[
                    "accident_type_main"
                ] == predict_main
            ]


        predict_middle_list = sorted(
            [
                value
                for value
                in predict_middle_source[
                    "accident_type_middle"
                ]
                .unique()
                .tolist()
                if value not in INVALID_VALUES
            ]
        )


        with p2:

            predict_middle = st.selectbox(
                "예측 중분류",
                ["전체"]
                + predict_middle_list,
                key="predict_type_middle"
            )


        # ====================================================
        # PREDICT SUB
        # ====================================================

        predict_sub_source = (
            predict_middle_source.copy()
        )


        if predict_middle != "전체":

            predict_sub_source = (
                predict_sub_source[
                    predict_sub_source[
                        "accident_type_middle"
                    ] == predict_middle
                ]
            )


        predict_sub_list = sorted(
            [
                value
                for value
                in predict_sub_source[
                    "accident_type_sub"
                ]
                .unique()
                .tolist()
                if value not in INVALID_VALUES
            ]
        )


        with p3:

            predict_sub = st.selectbox(
                "예측 소분류",
                ["전체"]
                + predict_sub_list,
                key="predict_type_sub"
            )


        with p4:

            predict_period = st.radio(
                "예측 기간",
                [
                    "1년",
                    "5년",
                    "10년"
                ],
                horizontal=True,
                key="predict_type_period"
            )


        # ====================================================
        # PREDICTION FILTER
        # ====================================================

        prediction_df = (
            df.copy()
        )


        if predict_main != "전체":

            prediction_df = prediction_df[
                prediction_df[
                    "accident_type_main"
                ] == predict_main
            ]


        if predict_middle != "전체":

            prediction_df = prediction_df[
                prediction_df[
                    "accident_type_middle"
                ] == predict_middle
            ]


        if predict_sub != "전체":

            prediction_df = prediction_df[
                prediction_df[
                    "accident_type_sub"
                ] == predict_sub
            ]


        if predict_sub != "전체":

            prediction_label = (
                predict_sub
            )

        elif predict_middle != "전체":

            prediction_label = (
                predict_middle
            )

        elif predict_main != "전체":

            prediction_label = (
                predict_main
            )

        else:

            prediction_label = (
                "전체 사고유형"
            )


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


        horizon = {
            "1년": 1,
            "5년": 5,
            "10년": 10
        }[
            predict_period
        ]


        # ====================================================
        # PREDICT
        # ====================================================

        if len(
            prediction_source
        ) < 2:

            st.warning(
                "미래 예측을 수행하려면 최소 2개 연도의 데이터가 필요합니다."
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


            predict_x = (
                [last_year]
                +
                future_years.tolist()
            )


            predict_y = (
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

                    x=predict_x,

                    y=predict_y,

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

                    <b>예측 사고유형</b> :
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

                    사고유형 데이터는 현재 연 단위로 구성되어 있으므로
                    월별 계절성을 분석하는 SARIMA보다
                    전체적인 장기 증가·감소 추세를 확인하기 쉬운
                    <b>Linear Trend Regression</b>을 적용합니다.

                </div>
                """
            )


            # =================================================
            # FORECAST SUMMARY
            # =================================================

            st.html(
                f"""
                <div class="analysis-box">

                    <div class="analysis-title">
                        {prediction_label} 사고 미래 예측
                    </div>

                    마지막 실제 데이터인
                    <b>{last_year}년</b>의 사고는
                    <b>{current_value:,}건</b>입니다.

                    <br>

                    현재 추세가 유지된다고 가정할 경우
                    <b>{last_year + horizon}년</b>
                    예상 사고 건수는
                    약 <b>{predicted_value:,}건</b>입니다.

                    <br>

                    마지막 실제 연도와 비교하면
                    <b>{change_value:+,}건</b>,
                    약
                    <b>{change_rate:+.1f}%</b>
                    변화할 것으로 추정됩니다.

                    <br><br>

                    ※ 장기 예측은 사고유형별 과거 추세만을 기반으로 하며,
                    법·제도 변화, 교통환경 변화,
                    고령운전자 규모 등의 외부 요인은 반영하지 않습니다.

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
                사고유형별 연도 데이터를 예측할 때 활용할 수 있는
                주요 시계열 모델의 특징을 비교합니다.
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
                                사고건수의 장기적인
                                증가·감소 추세를 직선으로 추정
                            </td>

                            <td>
                                적은 연도 데이터도 사용 가능
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
                                자기회귀와 이동평균을 사용한
                                시계열 예측
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
                                ARIMA에 계절 패턴을 추가
                            </td>

                            <td>
                                월별·분기별 장기 데이터
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
                                추세·변화점·계절성을
                                자동으로 모델링
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

                현재 사고유형별 데이터는
                <b>연도 단위</b>로 구성되어 있습니다.

                <br>

                따라서 월별·분기별 반복 패턴을 분석하는
                SARIMA와 같은 계절성 모델보다
                연도별 사고 규모의 장기적인 증가·감소 방향을
                설명할 수 있는
                <b>Linear Trend Regression</b>이
                현재 데이터 구조에 더 적합합니다.

                <br><br>

                향후 월별 사고유형 데이터가 확보되면
                ARIMA·SARIMA·Prophet 등을 추가하고,
                테스트 기간의 실제 사고건수와 예측값을 비교하여
                MAE / RMSE 기준으로 최종 모델을 선정할 수 있습니다.

            </div>
            """
        )


    # ========================================================
    # DETAIL
    # ========================================================

    st.write("")


    with st.expander(
        "고령운전자 사고유형·시간대 데이터 상세 보기"
    ):

        detail_df = (
            df[
                [
                    "year",
                    "accident_type_main",
                    "accident_type_middle",
                    "accident_type_sub",
                    "time_slot",
                    "accidents"
                ]
            ]
            .copy()
            .sort_values(
                [
                    "year",
                    "accident_type_main",
                    "accident_type_middle",
                    "accident_type_sub",
                    "time_slot"
                ],
                ascending=[
                    False,
                    True,
                    True,
                    True,
                    True
                ]
            )
        )


        detail_df.columns = [
            "연도",
            "대분류",
            "중분류",
            "소분류",
            "시간대",
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

            height=470,

            column_config={

                "연도":
                    st.column_config.NumberColumn(
                        "연도",
                        format="%d년"
                    ),

                "대분류":
                    st.column_config.TextColumn(
                        "대분류"
                    ),

                "중분류":
                    st.column_config.TextColumn(
                        "중분류"
                    ),

                "소분류":
                    st.column_config.TextColumn(
                        "소분류"
                    ),

                "시간대":
                    st.column_config.TextColumn(
                        "시간대"
                    ),

                "사고건수":
                    st.column_config.NumberColumn(
                        "사고건수",
                        format="%d건"
                    ),
            }
        )