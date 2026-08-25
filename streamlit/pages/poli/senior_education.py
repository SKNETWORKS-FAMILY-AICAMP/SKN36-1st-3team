import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sqlalchemy import text


# ============================================================
# PROJECT ROOT
# SAFE/streamlit/pages/poli/senior_education.py
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
def load_education():

    engine = get_engine()

    query = text(
        """
        SELECT
            id,
            edu_date,
            branch_name,
            course_name,
            capacity
        FROM education_reservation
        ORDER BY edu_date, branch_name, course_name
        """
    )

    with engine.connect() as conn:
        return pd.read_sql(query, conn)


# ============================================================
# LOAD
# ============================================================

try:
    df = load_education()

except Exception as e:

    st.error(
        f"MySQL 교육예약 데이터 조회 실패\n\n{e}"
    )

    st.stop()


# ============================================================
# CLEAN
# ============================================================

df["edu_date"] = pd.to_datetime(
    df["edu_date"],
    errors="coerce"
)

df["branch_name"] = (
    df["branch_name"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df["course_name"] = (
    df["course_name"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df["capacity"] = pd.to_numeric(
    df["capacity"],
    errors="coerce"
).fillna(0)

df = df[
    df["edu_date"].notna()
].copy()

df = df[
    (df["branch_name"] != "")
    &
    (df["course_name"] != "")
].copy()

df["year"] = (
    df["edu_date"]
    .dt.year
    .astype(int)
)

df = (
    df
    .groupby(
        [
            "edu_date",
            "year",
            "branch_name",
            "course_name",
        ],
        as_index=False
    )["capacity"]
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

if not years:

    st.warning(
        "교육예약 데이터가 없습니다."
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

    font-size: 18px !important;

    font-weight: 500 !important;

    min-height: 44px !important;
}


.st-key-nav_logo button {

    color: #27314C !important;

    font-size: 33px !important;

    font-weight: 900 !important;

    justify-content: flex-start !important;

    padding-left: 0 !important;
}


.st-key-nav_policy button {

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

.st-key-education_page {

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

    font-size: 15px;

    font-weight: 800;

    margin-bottom: 10px;
}


.page-title {

    color: #FFFFFF;

    font-size: 44px;

    font-weight: 900;

    margin-bottom: 12px;
}


.page-sub {

    color: #C3CBD8;

    font-size: 17px;

    line-height: 1.7;

    margin-bottom: 26px;
}


/* ==========================================================
   BACK
========================================================== */

.st-key-back_policy button {

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

    font-size: 15px !important;

    font-weight: 700 !important;
}


div[data-baseweb="select"] > div {

    background: #182035 !important;

    color: #FFFFFF !important;

    min-height: 46px !important;

    border: 1px solid #3A4662 !important;

    border-radius: 10px !important;

    box-shadow: none !important;
}


div[data-baseweb="select"] span {

    color: #E7ECF4 !important;
}


div[data-baseweb="select"] input {

    color: #E7ECF4 !important;

    caret-color: #F0C66E !important;
}


div[data-baseweb="select"] input::placeholder {

    color: #8F9AAF !important;

    opacity: 1 !important;
}


div[data-baseweb="select"] svg {

    color: #AEB8C8 !important;

    fill: #AEB8C8 !important;
}


div[data-baseweb="select"] > div:focus-within {

    border-color: #D6A348 !important;

    box-shadow:
        0 0 0 1px
        rgba(214,163,72,.25) !important;
}


/* ==========================================================
   GAP PANEL
========================================================== */

.st-key-gap_panel {

    background: #182035;

    border: 1px solid #3A4662;

    border-radius: 28px;

    padding: 26px 28px 24px 28px;

    margin-top: 24px;
}


.panel-title {

    color: #FFFFFF;

    font-size: 23px;

    font-weight: 800;

    margin-bottom: 8px;
}


.panel-sub {

    color: #C8D0DC;

    font-size: 15px;

    line-height: 1.7;

    margin-bottom: 16px;
}


/* ==========================================================
   GAP CARDS
========================================================== */

.gap-box {

    background: #121A2B;

    border: 1px solid #35415C;

    border-radius: 15px;

    padding: 20px;

    min-height: 135px;
}


.gap-label {

    color: #B8C1CF;

    font-size: 14px;

    margin-bottom: 12px;
}


.gap-value {

    color: #FFFFFF;

    font-size: 26px;

    font-weight: 900;
}


.gap-sub {

    color: #D6A348;

    font-size: 14px;

    margin-top: 8px;

    font-weight: 700;
}


/* ==========================================================
   ANALYSIS
========================================================== */

.analysis-box {

    background: #121A2B;

    border: 1px solid #35415C;

    border-left: 4px solid #D6A348;

    border-radius: 7px 15px 15px 7px;

    padding: 20px 22px;

    margin-top: 18px;

    color: #E5EAF2;

    font-size: 15px;

    line-height: 1.95;
}


.analysis-title {

    color: #F3C867;

    font-size: 18px;

    font-weight: 900;

    margin-bottom: 10px;
}


.analysis-box b {

    color: #FFFFFF;
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
    key="education_page"
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
                정책·제도 &gt; 교통안전교육 통계
            </div>

            <div class="page-title">
                고령운전자 교통안전교육 지역별 공급 격차
            </div>

            <div class="page-sub">
                도로교통공단 고령운전자 교통안전교육 데이터를 기반으로
                지역별 교육 공급 규모 차이를 비교합니다.
            </div>
            """
        )


    with head_right:

        with st.container(
            key="back_policy"
        ):

            if st.button(
                "← 정책·제도",
                use_container_width=True
            ):

                go_policy()


    # ========================================================
    # YEAR FILTER
    # ========================================================

    year_col, empty = st.columns(
        [1, 4]
    )

    with year_col:

        selected_year = st.selectbox(
            "기준 연도",
            years,
            key="education_year"
        )


    # ========================================================
    # YEAR DATA
    # ========================================================

    year_df = (
        df[
            df["year"] == selected_year
        ]
        .copy()
    )


    # ========================================================
    # BRANCH SUMMARY
    # ========================================================

    branch_summary = (
        year_df
        .groupby(
            "branch_name",
            as_index=False
        )["capacity"]
        .sum()
        .sort_values(
            "capacity",
            ascending=False
        )
        .reset_index(drop=True)
    )


    if branch_summary.empty:

        st.info(
            f"{selected_year}년 지역별 교육 공급 데이터가 없습니다."
        )

        st.stop()


    branch_avg = float(
        branch_summary[
            "capacity"
        ].mean()
    )


    branch_total = int(
        branch_summary[
            "capacity"
        ].sum()
    )


    branch_summary[
        "avg_diff_rate"
    ] = (
        (
            branch_summary[
                "capacity"
            ]
            - branch_avg
        )
        / branch_avg
        * 100
        if branch_avg > 0
        else 0
    )


    top_branch = str(
        branch_summary.iloc[0][
            "branch_name"
        ]
    )


    top_branch_capacity = int(
        branch_summary.iloc[0][
            "capacity"
        ]
    )


    bottom_row = (
        branch_summary
        .sort_values(
            "capacity",
            ascending=True
        )
        .iloc[0]
    )


    bottom_branch = str(
        bottom_row[
            "branch_name"
        ]
    )


    bottom_branch_capacity = int(
        bottom_row[
            "capacity"
        ]
    )


    branch_gap = (
        top_branch_capacity
        - bottom_branch_capacity
    )


    gap_ratio = (
        top_branch_capacity
        / bottom_branch_capacity
        if bottom_branch_capacity > 0
        else 0
    )


    top3_total = int(
        branch_summary
        .head(3)[
            "capacity"
        ]
        .sum()
    )


    top3_share = (
        top3_total
        / branch_total
        * 100
        if branch_total > 0
        else 0
    )


    # ========================================================
    # REGIONAL GAP
    # ========================================================

    with st.container(
        key="gap_panel"
    ):

        st.html(
            """
            <div class="panel-title">
                지역별 교육 공급 격차
            </div>

            <div class="panel-sub">
                각 지부의 교육 공급 규모를 비교하고,
                전체 지부 평균 대비 공급 수준 차이를 확인합니다.
            </div>
            """
        )


        g1, g2, g3, g4 = st.columns(
            4
        )


        with g1:

            st.html(
                f"""
                <div class="gap-box">

                    <div class="gap-label">
                        지부 평균 교육 규모
                    </div>

                    <div class="gap-value">
                        {branch_avg:,.0f}명
                    </div>

                    <div class="gap-sub">
                        평균 기준
                    </div>

                </div>
                """
            )


        with g2:

            st.html(
                f"""
                <div class="gap-box">

                    <div class="gap-label">
                        최대 - 최소 격차
                    </div>

                    <div class="gap-value">
                        {branch_gap:,}명
                    </div>

                    <div class="gap-sub">
                        {top_branch} ↔ {bottom_branch}
                    </div>

                </div>
                """
            )


        with g3:

            st.html(
                f"""
                <div class="gap-box">

                    <div class="gap-label">
                        최대 / 최소 배율
                    </div>

                    <div class="gap-value">
                        {
                            f"{gap_ratio:.1f}배"
                            if gap_ratio > 0
                            else "-"
                        }
                    </div>

                    <div class="gap-sub">
                        지역 간 상대 격차
                    </div>

                </div>
                """
            )


        with g4:

            st.html(
                f"""
                <div class="gap-box">

                    <div class="gap-label">
                        상위 3개 지부 집중도
                    </div>

                    <div class="gap-value">
                        {top3_share:.1f}%
                    </div>

                    <div class="gap-sub">
                        전체 교육 규모 대비
                    </div>

                </div>
                """
            )


        # ====================================================
        # GAP GRAPH
        # ====================================================

        gap_plot_df = (
            branch_summary
            .sort_values(
                "capacity",
                ascending=False
            )
            .copy()
        )


        fig_gap = go.Figure()


        fig_gap.add_trace(
            go.Bar(

                x=gap_plot_df[
                    "branch_name"
                ],

                y=gap_plot_df[
                    "capacity"
                ],

                marker_color=[
                    "#D9A64A"
                    if value >= branch_avg
                    else "#7086A8"

                    for value
                    in gap_plot_df[
                        "capacity"
                    ]
                ],

                text=[
                    f"{int(value):,}"
                    for value
                    in gap_plot_df[
                        "capacity"
                    ]
                ],

                textposition="outside",

                cliponaxis=False,

                hovertemplate=(
                    "<b>%{x}</b>"
                    "<br>"
                    "교육 규모: %{y:,}명"
                    "<extra></extra>"
                )
            )
        )


        fig_gap.add_hline(

            y=branch_avg,

            line_dash="dash",

            line_color="#E66B64",

            annotation_text=(
                f"지부 평균 {branch_avg:,.0f}명"
            ),

            annotation_position="top right",

            annotation_font_color="#FFFFFF"
        )


        gap_max = float(
            gap_plot_df[
                "capacity"
            ].max()
        )


        fig_gap.update_layout(

            height=580,

            margin=dict(
                l=75,
                r=60,
                t=55,
                b=100
            ),

            paper_bgcolor="#182035",

            plot_bgcolor="#182035",

            showlegend=False,

            font=dict(
                color="#E8EDF5",
                size=14
            ),

            xaxis=dict(
                title="지부",
                showgrid=False,
                tickangle=-30
            ),

            yaxis=dict(
                title="교육 규모(명)",
                gridcolor="#35405A",
                range=[
                    0,
                    gap_max * 1.20
                ]
            )
        )


        st.plotly_chart(
            fig_gap,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )


    # ========================================================
    # GAP ANALYSIS
    # ========================================================

    top_branch_avg_rate = float(
        branch_summary.iloc[0][
            "avg_diff_rate"
        ]
    )


    bottom_branch_avg_rate = float(
        bottom_row[
            "avg_diff_rate"
        ]
    )


    top3_names = ", ".join(
        branch_summary
        .head(3)[
            "branch_name"
        ]
        .astype(str)
        .tolist()
    )


    bottom3_names = ", ".join(
        branch_summary
        .tail(3)
        .sort_values(
            "capacity"
        )[
            "branch_name"
        ]
        .astype(str)
        .tolist()
    )


    st.html(
        f"""
        <div class="analysis-box">

            <div class="analysis-title">
                {selected_year}년 지역별 교육 공급 격차 분석
            </div>

            교육 공급 규모가 가장 큰 지부는
            <b>{top_branch}</b>로
            <b>{top_branch_capacity:,}명</b>이며,
            가장 작은 지부는
            <b>{bottom_branch}</b>로
            <b>{bottom_branch_capacity:,}명</b>입니다.

            <br>

            두 지부 사이의 교육 공급 규모 차이는
            <b>{branch_gap:,}명</b>입니다.

            <br>

            {
                f"최대 지부의 공급 규모는 최소 지부의 약 <b>{gap_ratio:.1f}배</b>입니다."
                if gap_ratio > 0
                else ""
            }

            <br>

            전체 지부 평균은
            <b>{branch_avg:,.0f}명</b>이며,
            {top_branch}은 평균보다
            <b>{top_branch_avg_rate:+.1f}%</b>,
            {bottom_branch}은 평균보다
            <b>{bottom_branch_avg_rate:+.1f}%</b>
            수준입니다.

            <br>

            교육 공급 규모 상위 3개 지부
            <b>{top3_names}</b>의 합계는
            전체의 약 <b>{top3_share:.1f}%</b>를 차지합니다.

            <br>

            교육 공급 규모가 상대적으로 작은 지부는
            <b>{bottom3_names}</b>입니다.


            <br><br>

            ※ 본 결과는 각 지부의 <b>capacity 합계</b>를 이용한
            교육 공급 규모 비교입니다.
            지역별 고령운전자 인구 또는 실제 교육 신청 수요를 반영한
            수요 대비 공급 격차 지표는 아닙니다.

        </div>
        """
    )
    