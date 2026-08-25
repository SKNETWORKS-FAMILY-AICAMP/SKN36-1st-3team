import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sqlalchemy import text


# ============================================================
# PROJECT ROOT
# SAFE/streamlit/pages/poli/senior_policy.py
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
# DATABASE LOAD
# ============================================================

@st.cache_data(ttl=600)
def load_policy_data():

    engine = get_engine()

    query = text(
        """
        SELECT
            id,
            category,
            policy_name,
            status,
            target,
            content,
            scale,
            start_date,
            agency,
            saas_idea,
            needed_data,
            source_url,
            confirm_date
        FROM old_driver_policy
        ORDER BY category, policy_name
        """
    )

    with engine.connect() as conn:
        return pd.read_sql(query, conn)


# ============================================================
# LOAD
# ============================================================

try:
    df = load_policy_data()

except Exception as e:

    st.error(
        f"MySQL 정책 데이터 조회 실패\n\n{e}"
    )

    st.stop()


# ============================================================
# CLEAN
# ============================================================

TEXT_COLS = [
    "category",
    "policy_name",
    "status",
    "target",
    "content",
    "scale",
    "agency",
    "saas_idea",
    "needed_data",
    "source_url",
]


for col in TEXT_COLS:

    df[col] = (
        df[col]
        .fillna("")
        .astype(str)
        .str.strip()
    )


df["start_date"] = pd.to_datetime(
    df["start_date"],
    errors="coerce"
)


df["confirm_date"] = pd.to_datetime(
    df["confirm_date"],
    errors="coerce"
)


INVALID_VALUES = [
    "",
    "-",
    "nan",
    "None",
    "없음",
]


def safe_text(value, default="-"):

    value = str(value).strip()

    if value in INVALID_VALUES:
        return default

    return value


def safe_date(value):

    if pd.isna(value):
        return "-"

    return value.strftime("%Y-%m-%d")


# ============================================================
# OPTIONS
# ============================================================

categories = sorted(
    [
        value
        for value in df["category"].unique().tolist()
        if value not in INVALID_VALUES
    ]
)


statuses = sorted(
    [
        value
        for value in df["status"].unique().tolist()
        if value not in INVALID_VALUES
    ]
)


agencies = sorted(
    [
        value
        for value in df["agency"].unique().tolist()
        if value not in INVALID_VALUES
    ]
)


if df.empty:

    st.warning(
        "고령운전자 정책 데이터가 없습니다."
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
    padding-bottom: 55px;
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

    white-space: nowrap !important;
}


.st-key-nav_logo button {

    color: #27314C !important;

    font-size: 31px !important;

    font-weight: 900 !important;

    justify-content: flex-start !important;

    padding-left: 0 !important;
}


.st-key-nav_policy button {

    color: #D6A348 !important;

    font-weight: 900 !important;
}


.st-key-nav_future button {

    background: #D9A64A !important;

    color: #172035 !important;

    font-weight: 800 !important;
}


/* ==========================================================
   PAGE
========================================================== */

.st-key-policy_detail_page {

    background: #101625;

    border: 1px solid #34405A;

    border-radius: 20px;

    padding: 34px 36px 48px 36px;
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

    line-height: 1.75;

    margin-bottom: 24px;
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

    font-size: 24px;

    font-weight: 900;

    word-break: keep-all;
}


/* ==========================================================
   PANELS
========================================================== */

.st-key-category_panel,
.st-key-status_panel,
.st-key-agency_panel,
.st-key-policy_list_panel,
.st-key-saas_panel,
.st-key-data_panel {

    background: #182035;

    border: 1px solid #3A4662;

    border-radius: 28px;

    padding: 24px 26px 24px 26px;

    margin-top: 24px;
}


.panel-title {

    color: #FFFFFF;

    font-size: 21px;

    font-weight: 900;

    margin-bottom: 8px;
}


.panel-sub {

    color: #C8D0DC;

    font-size: 13px;

    line-height: 1.75;

    margin-bottom: 12px;
}


.panel-sub b {

    color: #FFFFFF;
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

    font-size: 13px;

    line-height: 1.95;
}


.analysis-title {

    color: #F3C867;

    font-size: 16px;

    font-weight: 900;

    margin-bottom: 10px;
}


.analysis-box b {

    color: #FFFFFF;
}


/* ==========================================================
   POLICY CARD
========================================================== */

.policy-detail-card {

    background: #121A2B;

    border: 1px solid #3A4662;

    border-radius: 18px;

    padding: 22px 23px;

    margin: 14px 0;

    position: relative;
}


.policy-category {

    display: inline-block;

    padding: 5px 9px;

    border-radius: 999px;

    background: rgba(214,163,72,.12);

    border: 1px solid rgba(214,163,72,.32);

    color: #E7BC67;

    font-size: 11px;

    font-weight: 900;

    margin-bottom: 12px;
}


.policy-name {

    color: #FFFFFF;

    font-size: 20px;

    font-weight: 900;

    margin-bottom: 12px;
}


.policy-meta {

    color: #C9D0DB;

    font-size: 12px;

    line-height: 1.85;

    margin-bottom: 13px;
}


.policy-meta b {

    color: #FFFFFF;
}


.policy-content {

    color: #DDE3EC;

    font-size: 13px;

    line-height: 1.9;

    border-top: 1px solid #2E3951;

    padding-top: 14px;
}


/* ==========================================================
   SOURCE
========================================================== */

.policy-source {

    display: flex;

    align-items: center;

    gap: 12px;

    margin-top: 18px;

    padding-top: 14px;

    border-top: 1px solid #2E3951;

    font-size: 12px;
}


.policy-source-label {

    color: #8F9AAF;

    font-weight: 800;
}


.policy-source-link {

    display: inline-flex;

    align-items: center;

    padding: 6px 11px;

    background: rgba(214,163,72,.10);

    border: 1px solid rgba(214,163,72,.35);

    border-radius: 7px;

    color: #F0C66E !important;

    font-size: 12px;

    font-weight: 800;

    text-decoration: none !important;

    transition: .15s ease;
}


.policy-source-link:hover {

    background: rgba(214,163,72,.20);

    border-color: #D6A348;

    color: #FFD985 !important;
}


.policy-source-empty {

    color: #737E93;

    font-size: 12px;
}


/* ==========================================================
   STATUS
========================================================== */

.status-active {

    color: #88D5AE;

    font-weight: 900;
}


.status-etc {

    color: #E7BC67;

    font-weight: 900;
}


/* ==========================================================
   SAAS
========================================================== */

.saas-card {

    background:
        linear-gradient(
            120deg,
            #172338 0%,
            #1B2941 62%,
            #302D28 100%
        );

    border: 1px solid #A77E35;

    border-radius: 20px;

    padding: 23px 24px;

    margin: 14px 0;

    position: relative;

    overflow: hidden;
}


.saas-card::after {

    content: "SAFER";

    position: absolute;

    right: 18px;

    top: 4px;

    font-size: 55px;

    font-weight: 900;

    color: rgba(214,163,72,.05);
}


.saas-label {

    color: #E7B955;

    font-size: 11px;

    font-weight: 900;

    letter-spacing: 1.3px;

    margin-bottom: 10px;
}


.saas-policy {

    color: #FFFFFF;

    font-size: 17px;

    font-weight: 900;

    margin-bottom: 10px;
}


.saas-idea {

    color: #E1E6EE;

    font-size: 13px;

    line-height: 1.9;
}


/* ==========================================================
   NEEDED DATA
========================================================== */

.data-card {

    background: #121A2B;

    border: 1px solid #35415C;

    border-radius: 16px;

    padding: 18px 20px;

    margin: 10px 0;
}


.data-policy {

    color: #FFFFFF;

    font-size: 14px;

    font-weight: 900;

    margin-bottom: 7px;
}


.data-text {

    color: #BCC6D5;

    font-size: 12px;

    line-height: 1.75;
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
    key="policy_detail_page"
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
                정책·제도 &gt; 전국 고령운전자 정책
            </div>

            <div class="page-title">
                전국 고령운전자 정책 현황
            </div>

            <div class="page-sub">
                고령운전자 교통안전을 위해 시행되는 주요 정책의
                유형·대상·운영기관·시행상태를 비교합니다.
                실제 정책의 출처와 함께 SAFER에서 활용할 수 있는
                정책·서비스 추천 아이디어도 확인할 수 있습니다.
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
    # FILTER
    # ========================================================

    f1, f2, f3, empty = st.columns(
        [1.2, 1, 1.5, 2]
    )


    with f1:

        selected_category = st.selectbox(
            "정책 카테고리",
            ["전체"] + categories,
            key="policy_category"
        )


    with f2:

        selected_status = st.selectbox(
            "시행 상태",
            ["전체"] + statuses,
            key="policy_status"
        )


    with f3:

        selected_agency = st.selectbox(
            "운영 기관",
            ["전체"] + agencies,
            key="policy_agency"
        )


    # ========================================================
    # FILTER DATA
    # ========================================================

    filtered_df = df.copy()


    if selected_category != "전체":

        filtered_df = (
            filtered_df[
                filtered_df[
                    "category"
                ] == selected_category
            ]
        )


    if selected_status != "전체":

        filtered_df = (
            filtered_df[
                filtered_df[
                    "status"
                ] == selected_status
            ]
        )


    if selected_agency != "전체":

        filtered_df = (
            filtered_df[
                filtered_df[
                    "agency"
                ] == selected_agency
            ]
        )


    # ========================================================
    # KPI
    # ========================================================

    total_policy_count = len(
        filtered_df
    )


    category_count = (
        filtered_df[
            "category"
        ]
        .replace(
            "",
            pd.NA
        )
        .nunique()
    )


    agency_count = (
        filtered_df[
            "agency"
        ]
        .replace(
            "",
            pd.NA
        )
        .nunique()
    )


    idea_count = (
        filtered_df[
            "saas_idea"
        ]
        .replace(
            "",
            pd.NA
        )
        .notna()
        .sum()
    )


    st.write("")


    k1, k2, k3, k4 = st.columns(4)


    with k1:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    조회 정책 수
                </div>

                <div class="kpi-value">
                    {total_policy_count:,}개
                </div>

            </div>
            """
        )


    with k2:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    정책 카테고리
                </div>

                <div class="kpi-value">
                    {category_count:,}개
                </div>

            </div>
            """
        )


    with k3:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    운영기관
                </div>

                <div class="kpi-value">
                    {agency_count:,}개
                </div>

            </div>
            """
        )


    with k4:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    SAFER 추천 아이디어
                </div>

                <div class="kpi-value">
                    {idea_count:,}개
                </div>

            </div>
            """
        )


    # ========================================================
    # CATEGORY / STATUS
    # ========================================================

    left, right = st.columns(
        [1, 1],
        gap="medium"
    )


    # ========================================================
    # CATEGORY
    # ========================================================

    with left:

        with st.container(
            key="category_panel"
        ):

            st.html(
                """
                <div class="panel-title">
                    정책 유형별 현황
                </div>

                <div class="panel-sub">
                    전체 정책에서 어떤 정책 유형이 많이 구성되어 있는지 비교합니다.
                </div>
                """
            )


            category_df = (
                df[
                    df[
                        "category"
                    ] != ""
                ]
                .groupby(
                    "category",
                    as_index=False
                )
                .size()
                .rename(
                    columns={
                        "size": "count"
                    }
                )
                .sort_values(
                    "count",
                    ascending=True
                )
            )


            max_category = (
                category_df[
                    "count"
                ].max()
                if not category_df.empty
                else 1
            )


            fig_category = go.Figure(
                go.Bar(

                    x=category_df[
                        "count"
                    ],

                    y=category_df[
                        "category"
                    ],

                    orientation="h",

                    marker_color=[
                        "#D9A64A"
                        if (
                            selected_category != "전체"
                            and category == selected_category
                        )
                        else "#79B69B"

                        for category
                        in category_df[
                            "category"
                        ]
                    ],

                    text=[
                        f"{int(value)}개"
                        for value
                        in category_df[
                            "count"
                        ]
                    ],

                    textposition="outside",

                    cliponaxis=False,

                    hovertemplate=(
                        "<b>%{y}</b>"
                        "<br>"
                        "정책: %{x}개"
                        "<extra></extra>"
                    )
                )
            )


            fig_category.update_layout(

                height=max(
                    440,
                    len(category_df) * 50
                ),

                margin=dict(
                    l=130,
                    r=85,
                    t=30,
                    b=60
                ),

                paper_bgcolor="#182035",

                plot_bgcolor="#182035",

                showlegend=False,

                font=dict(
                    color="#E8EDF5"
                ),

                xaxis=dict(
                    title="정책 수(개)",
                    gridcolor="#35405A",
                    dtick=1,
                    range=[
                        0,
                        max_category * 1.25
                    ]
                ),

                yaxis=dict(
                    title=None
                )
            )


            st.plotly_chart(
                fig_category,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )


    # ========================================================
    # STATUS
    # ========================================================

    with right:

        with st.container(
            key="status_panel"
        ):

            st.html(
                """
                <div class="panel-title">
                    정책 시행상태
                </div>

                <div class="panel-sub">
                    현재 수집된 정책을 시행상태별로 구분합니다.
                </div>
                """
            )


            status_df = (
                df[
                    df[
                        "status"
                    ] != ""
                ]
                .groupby(
                    "status",
                    as_index=False
                )
                .size()
                .rename(
                    columns={
                        "size": "count"
                    }
                )
                .sort_values(
                    "count",
                    ascending=False
                )
            )


            fig_status = go.Figure(
                go.Pie(

                    labels=status_df[
                        "status"
                    ],

                    values=status_df[
                        "count"
                    ],

                    hole=.58,

                    textinfo="label+percent",

                    textfont=dict(
                        color="#FFFFFF",
                        size=13
                    ),

                    marker=dict(

                        colors=[
                            "#D9A64A",
                            "#79B69B",
                            "#8DA9C4",
                            "#DD8469",
                            "#A28BC2",
                        ],

                        line=dict(
                            color="#182035",
                            width=2
                        )
                    ),

                    hovertemplate=(
                        "<b>%{label}</b>"
                        "<br>"
                        "%{value}개"
                        "<br>"
                        "%{percent}"
                        "<extra></extra>"
                    )
                )
            )


            fig_status.add_annotation(

                text=(
                    f"정책<br>"
                    f"<b>{len(df):,}개</b>"
                ),

                x=.5,
                y=.5,

                showarrow=False,

                font=dict(
                    color="#FFFFFF",
                    size=17
                )
            )


            fig_status.update_layout(

                height=440,

                margin=dict(
                    l=30,
                    r=30,
                    t=30,
                    b=30
                ),

                paper_bgcolor="#182035",

                showlegend=False,

                font=dict(
                    color="#FFFFFF"
                )
            )


            st.plotly_chart(
                fig_status,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )


    # ========================================================
    # AGENCY
    # ========================================================

    with st.container(
        key="agency_panel"
    ):

        st.html(
            """
            <div class="panel-title">
                운영기관별 정책 현황
            </div>

            <div class="panel-sub">
                어떤 기관이 고령운전자 정책을 담당하고 있는지 비교합니다.
            </div>
            """
        )


        agency_df = (
            df[
                df[
                    "agency"
                ] != ""
            ]
            .groupby(
                "agency",
                as_index=False
            )
            .size()
            .rename(
                columns={
                    "size": "count"
                }
            )
            .sort_values(
                "count",
                ascending=True
            )
        )


        if agency_df.empty:

            st.info(
                "운영기관 데이터가 없습니다."
            )

        else:

            max_agency = (
                agency_df[
                    "count"
                ].max()
            )


            fig_agency = go.Figure(
                go.Bar(

                    x=agency_df[
                        "count"
                    ],

                    y=agency_df[
                        "agency"
                    ],

                    orientation="h",

                    marker_color="#8DA9C4",

                    text=[
                        f"{int(value)}개"
                        for value
                        in agency_df[
                            "count"
                        ]
                    ],

                    textposition="outside",

                    cliponaxis=False,

                    hovertemplate=(
                        "<b>%{y}</b>"
                        "<br>"
                        "정책: %{x}개"
                        "<extra></extra>"
                    )
                )
            )


            fig_agency.update_layout(

                height=max(
                    450,
                    len(agency_df) * 42
                ),

                margin=dict(
                    l=180,
                    r=90,
                    t=30,
                    b=60
                ),

                paper_bgcolor="#182035",

                plot_bgcolor="#182035",

                showlegend=False,

                font=dict(
                    color="#E8EDF5"
                ),

                xaxis=dict(
                    title="정책 수(개)",
                    gridcolor="#35405A",
                    dtick=1,
                    range=[
                        0,
                        max_agency * 1.25
                    ]
                ),

                yaxis=dict(
                    title=None
                )
            )


            st.plotly_chart(
                fig_agency,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )


    # ========================================================
    # AUTO ANALYSIS
    # ========================================================

    category_all = (
        df[
            df[
                "category"
            ] != ""
        ]
        .groupby(
            "category"
        )
        .size()
        .sort_values(
            ascending=False
        )
    )


    if not category_all.empty:

        top_category = category_all.index[0]

        top_category_count = int(
            category_all.iloc[0]
        )

    else:

        top_category = "-"
        top_category_count = 0


    agency_all = (
        df[
            df[
                "agency"
            ] != ""
        ]
        .groupby(
            "agency"
        )
        .size()
        .sort_values(
            ascending=False
        )
    )


    if not agency_all.empty:

        top_agency = agency_all.index[0]

        top_agency_count = int(
            agency_all.iloc[0]
        )

    else:

        top_agency = "-"
        top_agency_count = 0


    idea_total = (
        df[
            "saas_idea"
        ]
        .replace(
            "",
            pd.NA
        )
        .notna()
        .sum()
    )


    needed_total = (
        df[
            "needed_data"
        ]
        .replace(
            "",
            pd.NA
        )
        .notna()
        .sum()
    )


    st.html(
        f"""
        <div class="analysis-box">

            <div class="analysis-title">
                전국 고령운전자 정책 분석
            </div>

            현재 DB에는 총
            <b>{len(df):,}개</b>의 고령운전자 관련 정책이 등록되어 있습니다.

            <br>

            가장 많은 정책이 포함된 카테고리는
            <b>{top_category}</b>로
            총 <b>{top_category_count:,}개</b>입니다.

            <br>

            가장 많은 정책을 담당하는 기관은
            <b>{top_agency}</b>로
            <b>{top_agency_count:,}개</b>의 정책과 연결되어 있습니다.

            <br>

            기존 정책을 기반으로 SAFER에서 활용 가능한
            정책·서비스 아이디어는
            <b>{idea_total:,}건</b>,
            추가 데이터가 필요하다고 기록된 정책은
            <b>{needed_total:,}건</b>입니다.

            <br><br>

            ※ 본 페이지는 전국 단위 정책의 종류와 내용을 비교합니다.
            지역별 정책 보유 여부는 지역 정책 비교 페이지에서 별도로 분석합니다.

        </div>
        """
    )


    # ========================================================
    # POLICY DETAIL LIST
    # ========================================================

    with st.container(
        key="policy_list_panel"
    ):

        st.html(
            f"""
            <div class="panel-title">
                정책 상세 보기
            </div>

            <div class="panel-sub">
                현재 필터 조건에 해당하는
                <b>{len(filtered_df):,}개</b> 정책의 주요 내용을 확인합니다.
            </div>
            """
        )


        if filtered_df.empty:

            st.info(
                "현재 조건에 해당하는 정책이 없습니다."
            )

        else:

            for _, row in filtered_df.iterrows():

                category = safe_text(
                    row["category"]
                )

                policy_name = safe_text(
                    row["policy_name"]
                )

                status = safe_text(
                    row["status"]
                )

                target = safe_text(
                    row["target"]
                )

                content = safe_text(
                    row["content"]
                )

                scale = safe_text(
                    row["scale"]
                )

                agency = safe_text(
                    row["agency"]
                )

                source_url = safe_text(
                    row["source_url"],
                    default=""
                )


                start_date = safe_date(
                    row["start_date"]
                )


                confirm_date = safe_date(
                    row["confirm_date"]
                )


                status_class = (
                    "status-active"
                    if any(
                        word in status
                        for word in [
                            "시행",
                            "운영",
                            "진행",
                            "적용",
                        ]
                    )
                    else "status-etc"
                )


                # =================================================
                # SOURCE
                # =================================================

                if source_url:

                    source_html = f"""
                    <div class="policy-source">

                        <span class="policy-source-label">
                            출처
                        </span>

                        <a
                            href="{source_url}"
                            target="_blank"
                            rel="noopener noreferrer"
                            class="policy-source-link"
                        >
                            원문 보기 ↗
                        </a>

                    </div>
                    """

                else:

                    source_html = """
                    <div class="policy-source">

                        <span class="policy-source-label">
                            출처
                        </span>

                        <span class="policy-source-empty">
                            출처 정보 없음
                        </span>

                    </div>
                    """


                st.html(
                    f"""
                    <div class="policy-detail-card">

                        <div class="policy-category">
                            {category}
                        </div>

                        <div class="policy-name">
                            {policy_name}
                        </div>

                        <div class="policy-meta">

                            <b>시행상태</b> :
                            <span class="{status_class}">
                                {status}
                            </span>

                            &nbsp;&nbsp; | &nbsp;&nbsp;

                            <b>대상</b> :
                            {target}

                            <br>

                            <b>운영기관</b> :
                            {agency}

                            &nbsp;&nbsp; | &nbsp;&nbsp;

                            <b>시행규모</b> :
                            {scale}

                            <br>

                            <b>시작일</b> :
                            {start_date}

                            &nbsp;&nbsp; | &nbsp;&nbsp;

                            <b>확인일</b> :
                            {confirm_date}

                        </div>

                        <div class="policy-content">
                            {content}
                        </div>

                        {source_html}

                    </div>
                    """
                )


    # ========================================================
    # SAFER RECOMMENDATIONS
    # ========================================================

    with st.container(
        key="saas_panel"
    ):

        st.html(
            """
            <div class="panel-title">
                SAFER 정책·서비스 추천
            </div>

            <div class="panel-sub">
                기존 정책 내용을 바탕으로 SAFER 서비스에서 활용할 수 있는
                정책·서비스 아이디어를 정리합니다.

                <br>

                <b style="color:#F3C867;">
                    아래 내용은 실제 시행 중인 정책이 아니라
                    SAFER 서비스 활용을 위한 추천 아이디어입니다.
                </b>
            </div>
            """
        )


        idea_df = (
            filtered_df[
                ~filtered_df[
                    "saas_idea"
                ].isin(
                    INVALID_VALUES
                )
            ]
            .copy()
        )


        if idea_df.empty:

            st.info(
                "현재 조건에 해당하는 SAFER 추천 아이디어가 없습니다."
            )

        else:

            for _, row in idea_df.iterrows():

                st.html(
                    f"""
                    <div class="saas-card">

                        <div class="saas-label">
                            SAFER RECOMMENDATION
                        </div>

                        <div class="saas-policy">
                            {safe_text(row["policy_name"])}
                        </div>

                        <div class="saas-idea">
                            {safe_text(row["saas_idea"])}
                        </div>

                    </div>
                    """
                )


    # ========================================================
    # NEEDED DATA
    # ========================================================

    with st.container(
        key="data_panel"
    ):

        st.html(
            """
            <div class="panel-title">
                추가 필요 데이터
            </div>

            <div class="panel-sub">
                정책 효과 분석이나 SAFER 서비스 확장을 위해
                추가 확보가 필요한 데이터 항목을 확인합니다.
            </div>
            """
        )


        needed_df = (
            filtered_df[
                ~filtered_df[
                    "needed_data"
                ].isin(
                    INVALID_VALUES
                )
            ]
            .copy()
        )


        if needed_df.empty:

            st.info(
                "현재 조건에서 별도로 기록된 추가 필요 데이터가 없습니다."
            )

        else:

            for _, row in needed_df.iterrows():

                st.html(
                    f"""
                    <div class="data-card">

                        <div class="data-policy">
                            {safe_text(row["policy_name"])}
                        </div>

                        <div class="data-text">
                            {safe_text(row["needed_data"])}
                        </div>

                    </div>
                    """
                )


    # ========================================================
    # DETAIL TABLE
    # ========================================================

    st.write("")


    with st.expander(
        "전국 고령운전자 정책 데이터 상세 보기"
    ):

        detail_df = (
            filtered_df[
                [
                    "category",
                    "policy_name",
                    "status",
                    "target",
                    "content",
                    "scale",
                    "start_date",
                    "agency",
                    "saas_idea",
                    "needed_data",
                    "confirm_date",
                    "source_url",
                ]
            ]
            .copy()
        )


        detail_df.columns = [
            "카테고리",
            "정책명",
            "시행상태",
            "대상",
            "정책내용",
            "시행규모",
            "시작일",
            "운영기관",
            "SAFER 추천 아이디어",
            "추가 필요 데이터",
            "확인일",
            "출처",
        ]


        st.dataframe(

            detail_df,

            use_container_width=True,

            hide_index=True,

            height=500,

            column_config={

                "카테고리":
                    st.column_config.TextColumn(
                        "카테고리"
                    ),

                "정책명":
                    st.column_config.TextColumn(
                        "정책명",
                        width="large"
                    ),

                "시행상태":
                    st.column_config.TextColumn(
                        "시행상태"
                    ),

                "대상":
                    st.column_config.TextColumn(
                        "대상",
                        width="medium"
                    ),

                "정책내용":
                    st.column_config.TextColumn(
                        "정책내용",
                        width="large"
                    ),

                "시행규모":
                    st.column_config.TextColumn(
                        "시행규모"
                    ),

                "시작일":
                    st.column_config.DateColumn(
                        "시작일",
                        format="YYYY-MM-DD"
                    ),

                "운영기관":
                    st.column_config.TextColumn(
                        "운영기관",
                        width="medium"
                    ),

                "SAFER 추천 아이디어":
                    st.column_config.TextColumn(
                        "SAFER 추천 아이디어",
                        width="large"
                    ),

                "추가 필요 데이터":
                    st.column_config.TextColumn(
                        "추가 필요 데이터",
                        width="large"
                    ),

                "확인일":
                    st.column_config.DateColumn(
                        "확인일",
                        format="YYYY-MM-DD"
                    ),

                "출처":
                    st.column_config.LinkColumn(
                        "출처",
                        display_text="원문 보기"
                    ),
            }
        )