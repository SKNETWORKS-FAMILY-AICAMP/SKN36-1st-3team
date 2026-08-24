import sys
import re
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sqlalchemy import text


# ============================================================
# PROJECT ROOT
# SAFE/streamlit/pages/car/license_age.py
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
def load_license_age():

    engine = get_engine()

    query = text(
        """
        SELECT *
        FROM license_holder_age
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


try:
    df = load_license_age()

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


age_col = find_column(
    [
        "age_group",
        "age",
        "age_range",
    ]
)


year_col = find_column(
    [
        "year",
        "base_year",
    ]
)


count_col = find_column(
    [
        "count",
        "license_count",
        "holders",
        "holder_count",
    ]
)


license_main_col = find_column(
    [
        "license_main",
        "license_type",
        "license_class",
    ]
)


license_sub_col = find_column(
    [
        "license_sub",
        "license_detail",
        "license_grade",
    ]
)


# ============================================================
# REQUIRED COLUMN CHECK
# ============================================================

if age_col is None:

    st.error(
        f"""
        license_holder_age 테이블에서 연령 컬럼을 찾을 수 없습니다.

        현재 컬럼:
        {list(df.columns)}
        """
    )

    st.stop()


if count_col is None:

    st.error(
        f"""
        license_holder_age 테이블에서
        면허 소지자 수 컬럼을 찾을 수 없습니다.

        현재 컬럼:
        {list(df.columns)}
        """
    )

    st.stop()


# ============================================================
# TYPE CLEAN
# ============================================================

df[count_col] = pd.to_numeric(
    df[count_col],
    errors="coerce",
).fillna(0)


if year_col is not None:

    df[year_col] = pd.to_numeric(
        df[year_col],
        errors="coerce",
    )


df[age_col] = (
    df[age_col]
    .fillna("")
    .astype(str)
    .str.strip()
)


# ============================================================
# REMOVE TOTAL / UNKNOWN
# ============================================================

df = df[
    ~df[age_col].isin(
        [
            "",
            "계",
            "합계",
            "총계",
            "불명",
            "미상",
        ]
    )
].copy()


# ============================================================
# AGE PARSING
# ============================================================

def age_start(age_text):
    """
    정렬 및 고령자 판별용 숫자 추출

    예)
    53       -> 53
    65       -> 65
    20대     -> 20
    65세 이상 -> 65
    65~69세  -> 65
    """

    value = str(
        age_text
    ).strip()

    numbers = re.findall(
        r"\d+",
        value
    )

    if numbers:

        return int(
            numbers[0]
        )

    return 999


def is_senior(age_text):

    return (
        age_start(
            age_text
        )
        >= 65
    )


def format_age(age_text):
    """
    차트 Y축 표시용
    """

    value = str(
        age_text
    ).strip()

    if value.isdigit():
        return f"{value}세"

    return value


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


/* Streamlit 기본 요소 숨기기 */

header[data-testid="stHeader"] {
    display: none;
}

section[data-testid="stSidebar"] {
    display: none;
}

#MainMenu {
    display: none;
}

footer {
    display: none;
}


/* ==========================================================
   MAIN CONTAINER
========================================================== */

.block-container {

    max-width: 1600px;

    padding-top: 14px;

    padding-left: 30px;

    padding-right: 30px;

    padding-bottom: 50px;
}


/* ==========================================================
   TOP NAVIGATION
========================================================== */

.st-key-top_nav {

    background: rgba(
        255,
        255,
        255,
        .98
    );

    border-radius: 16px;

    padding:
        10px
        20px;

    margin-bottom: 20px;

    box-shadow:
        0 5px 20px
        rgba(0,0,0,.10);
}


.st-key-top_nav button {

    background:
        transparent
        !important;

    color:
        #30384D
        !important;

    border:
        none
        !important;

    box-shadow:
        none
        !important;

    font-size:
        16px
        !important;

    font-weight:
        500
        !important;

    min-height:
        44px
        !important;

    white-space:
        nowrap
        !important;

    transition:
        all .15s ease
        !important;
}


.st-key-top_nav button:hover {

    background:
        transparent
        !important;

    color:
        #D6A348
        !important;
}


/* ==========================================================
   LOGO
========================================================== */

.st-key-nav_logo button {

    color:
        #27314C
        !important;

    font-size:
        31px
        !important;

    font-weight:
        900
        !important;

    justify-content:
        flex-start
        !important;

    padding-left:
        0
        !important;

    letter-spacing:
        -1px
        !important;
}


/* ==========================================================
   ACTIVE NAV
========================================================== */

.st-key-nav_car button {

    color:
        #D6A348
        !important;

    font-weight:
        800
        !important;
}


/* ==========================================================
   FUTURE BUTTON
========================================================== */

.st-key-nav_future button {

    background:
        #D9A64A
        !important;

    color:
        #172035
        !important;

    font-size:
        15px
        !important;

    font-weight:
        800
        !important;

    border-radius:
        2px
        !important;

    padding-left:
        18px
        !important;

    padding-right:
        18px
        !important;
}


.st-key-nav_future button:hover {

    background:
        #C9973C
        !important;

    color:
        #172035
        !important;
}


/* ==========================================================
   PAGE PANEL
========================================================== */

.st-key-license_age_page {

    background:
        #101625;

    border:
        1px solid
        #34405A;

    border-radius:
        20px;

    padding:
        34px
        36px
        44px
        36px;

    box-shadow:
        0 12px 36px
        rgba(0,0,0,.18);
}


/* ==========================================================
   PAGE HEADER
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
   BACK BUTTON
========================================================== */

.st-key-back_car button {

    background:
        #192136
        !important;

    color:
        #D1D6E0
        !important;

    border:
        1px solid
        #39445D
        !important;

    border-radius:
        11px
        !important;

    font-size:
        13px
        !important;

    font-weight:
        600
        !important;

    min-height:
        44px
        !important;
}


.st-key-back_car button:hover {

    color:
        #D6A348
        !important;

    border-color:
        #D6A348
        !important;
}


/* ==========================================================
   FILTER LABEL
========================================================== */

label[data-testid="stWidgetLabel"] p {

    color:
        #C2C8D3
        !important;

    font-size:
        13px
        !important;

    font-weight:
        600
        !important;
}


/* ==========================================================
   SELECT BOX
========================================================== */

div[data-baseweb="select"] > div {

    background:
        #F4F5F8
        !important;

    border-color:
        #D1D5DE
        !important;

    color:
        #1C2435
        !important;

    min-height:
        46px
        !important;

    border-radius:
        8px
        !important;
}


div[data-baseweb="select"] span {

    color:
        #273149
        !important;

    font-size:
        14px
        !important;

    font-weight:
        500
        !important;
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
        18px
        20px;

    box-sizing:
        border-box;
}


.kpi-label {

    color:
        #A8B0C0;

    font-size:
        12px;

    font-weight:
        500;

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


/* ==========================================================
   CHART PANEL
========================================================== */

.st-key-chart_panel {

    background:
        #182035;

    border:
        1px solid
        #3A4662;

    border-radius:
        28px;

    padding:
        24px
        26px
        20px
        26px;

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
   SENIOR NOTE
========================================================== */

.senior-note {

    color:
        #E1B55E;

    font-size:
        12px;

    font-weight:
        600;

    margin-top:
        5px;

    margin-left:
        5px;
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


[data-testid="stExpander"] summary {

    color:
        #E7EAF0
        !important;

    font-size:
        14px
        !important;

    font-weight:
        600
        !important;
}


/* ==========================================================
   DATAFRAME
========================================================== */

[data-testid="stDataFrame"] {

    border-radius:
        12px;

    overflow:
        hidden;

    font-size:
        13px;
}


/* ==========================================================
   RESPONSIVE
========================================================== */

@media(max-width: 1100px) {

    .page-title {
        font-size: 34px;
    }

    .page-sub {
        font-size: 14px;
    }

    .st-key-license_age_page {

        padding:
            24px;
    }
}

</style>
"""
)


# ============================================================
# TOP NAVIGATION
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
        gap="small",
    )


    # SAFER
    with logo:

        if st.button(
            "SAFER",
            key="nav_logo",
        ):

            go_main()


    # 인구
    with n1:

        if st.button(
            "인구",
            key="nav_people",
            use_container_width=True,
        ):

            go_people()


    # 자동차
    with n2:

        if st.button(
            "자동차",
            key="nav_car",
            use_container_width=True,
        ):

            go_car()


    # 교통사고
    with n3:

        if st.button(
            "교통사고",
            key="nav_accident",
            use_container_width=True,
        ):

            go_accident()


    # 제도
    with n4:

        if st.button(
            "제도",
            key="nav_policy",
            use_container_width=True,
        ):

            go_policy()


    # FAQ
    with n5:

        if st.button(
            "FAQ",
            key="nav_faq",
            use_container_width=True,
        ):

            go_faq()


    # 미래 전망
    with nf:

        if st.button(
            "미래 전망 예측하기 ▶",
            key="nav_future",
            use_container_width=True,
        ):

            st.toast(
                "미래 전망 페이지는 준비 중입니다.",
                icon="📈",
            )


# ============================================================
# PAGE
# ============================================================

with st.container(
    key="license_age_page"
):

    # ========================================================
    # HEADER
    # ========================================================

    head_left, head_right = st.columns(
        [
            5,
            1,
        ],
        vertical_alignment="center",
    )


    with head_left:

        st.html(
            """
            <div class="page-path">
                자동차 &gt; 운전면허 소지자 현황
            </div>

            <div class="page-title">
                연령별 운전면허 소지자 현황
            </div>

            <div class="page-sub">
                연령별 운전면허 소지자 규모를 비교하고
                65세 이상 고령운전자의 규모와 비중을 확인합니다.
            </div>
            """
        )


    with head_right:

        with st.container(
            key="back_car"
        ):

            if st.button(
                "← 자동차 분석",
                use_container_width=True,
            ):

                go_car()


    # ========================================================
    # FILTER
    # ========================================================

    f1, f2, f3, empty = st.columns(
        [
            1,
            1,
            1,
            2,
        ]
    )


    # ========================================================
    # YEAR
    # ========================================================

    with f1:

        if year_col is not None:

            years = sorted(
                df[
                    year_col
                ]
                .dropna()
                .astype(int)
                .unique(),
                reverse=True,
            )


            selected_year = st.selectbox(
                "연도",
                years,
            )

        else:

            selected_year = None


    # ========================================================
    # LICENSE MAIN
    # ========================================================

    with f2:

        if license_main_col is not None:

            main_options = [
                "전체"
            ] + sorted(
                df[
                    license_main_col
                ]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )


            selected_main = st.selectbox(
                "면허 구분",
                main_options,
            )

        else:

            selected_main = "전체"


    # ========================================================
    # LICENSE SUB
    # ========================================================

    with f3:

        temp_df = df.copy()


        if (
            license_main_col is not None
            and selected_main != "전체"
        ):

            temp_df = temp_df[
                temp_df[
                    license_main_col
                ].astype(str)
                == selected_main
            ]


        if license_sub_col is not None:

            sub_options = [
                "전체"
            ] + sorted(
                temp_df[
                    license_sub_col
                ]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )


            selected_sub = st.selectbox(
                "면허 세부",
                sub_options,
            )

        else:

            selected_sub = "전체"


    # ========================================================
    # FILTER DATA
    # ========================================================

    filtered = df.copy()


    if (
        year_col is not None
        and selected_year is not None
    ):

        filtered = filtered[
            filtered[
                year_col
            ] == selected_year
        ]


    if (
        license_main_col is not None
        and selected_main != "전체"
    ):

        filtered = filtered[
            filtered[
                license_main_col
            ].astype(str)
            == selected_main
        ]


    if (
        license_sub_col is not None
        and selected_sub != "전체"
    ):

        filtered = filtered[
            filtered[
                license_sub_col
            ].astype(str)
            == selected_sub
        ]


    # ========================================================
    # AGGREGATE BY AGE
    # ========================================================

    chart_df = (
        filtered
        .groupby(
            age_col,
            as_index=False,
        )[count_col]
        .sum()
    )


    chart_df[
        "age_order"
    ] = chart_df[
        age_col
    ].apply(
        age_start
    )


    chart_df[
        "is_senior"
    ] = chart_df[
        age_col
    ].apply(
        is_senior
    )


    # 낮은 연령 -> 높은 연령
    chart_df = (
        chart_df
        .sort_values(
            "age_order",
            ascending=True,
        )
        .reset_index(
            drop=True,
        )
    )


    # ========================================================
    # KPI CALCULATION
    # ========================================================

    total_count = int(
        chart_df[
            count_col
        ].sum()
    )


    senior_count = int(
        chart_df.loc[
            chart_df[
                "is_senior"
            ],
            count_col,
        ].sum()
    )


    if total_count > 0:

        senior_ratio = (
            senior_count
            / total_count
            * 100
        )

    else:

        senior_ratio = 0


    if not chart_df.empty:

        max_row = chart_df.loc[
            chart_df[
                count_col
            ].idxmax()
        ]

        largest_age = format_age(
            max_row[
                age_col
            ]
        )

    else:

        largest_age = "-"


    st.write("")


    # ========================================================
    # KPI CARDS
    # ========================================================

    k1, k2, k3, k4 = st.columns(
        4
    )


    # 전체
    with k1:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    전체 면허 소지자
                </div>

                <div class="kpi-value">
                    {total_count:,}명
                </div>

            </div>
            """
        )


    # 고령자
    with k2:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    65세 이상 면허 소지자
                </div>

                <div class="kpi-value">
                    {senior_count:,}명
                </div>

            </div>
            """
        )


    # 고령자 비율
    with k3:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    고령운전자 비중
                </div>

                <div class="kpi-value">
                    {senior_ratio:.1f}%
                </div>

            </div>
            """
        )


    # 최다 연령
    with k4:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    면허 소지 최다 연령
                </div>

                <div class="kpi-value">
                    {largest_age}
                </div>

            </div>
            """
        )


    # ========================================================
    # CHART
    # ========================================================

    with st.container(
        key="chart_panel"
    ):

        st.html(
            """
            <div class="panel-title">
                연령별 운전면허 소지자 현황
            </div>

            <div class="panel-sub">
                X축: 운전면허 소지자 수(명) ·
                Y축: 연령 ·
                65세 이상 고령운전자는 금색으로 강조하여 표시합니다.
            </div>
            """
        )


        if chart_df.empty:

            st.warning(
                "선택한 조건에 해당하는 데이터가 없습니다."
            )


        else:

            chart_df = (
                chart_df.copy()
            )


            # =================================================
            # Y POSITION
            # =================================================

            chart_df[
                "y_position"
            ] = range(
                len(
                    chart_df
                )
            )


            # =================================================
            # NORMAL / SENIOR
            # =================================================

            normal_df = chart_df[
                ~chart_df[
                    "is_senior"
                ]
            ].copy()


            senior_df = chart_df[
                chart_df[
                    "is_senior"
                ]
            ].copy()


            # =================================================
            # FIGURE
            # =================================================

            fig = go.Figure()


            # =================================================
            # 65세 미만
            # =================================================

            fig.add_trace(
                go.Bar(

                    x=normal_df[
                        count_col
                    ],

                    y=normal_df[
                        "y_position"
                    ],

                    orientation="h",

                    name="65세 미만",

                    marker=dict(
                        color="#74B89A",
                    ),

                    text=[
                        f"{int(v):,}명"
                        for v in normal_df[
                            count_col
                        ]
                    ],

                    textposition="outside",

                    textfont=dict(
                        color="#F4F6FA",
                        size=14,
                    ),

                    cliponaxis=False,

                    customdata=normal_df[
                        age_col
                    ],

                    hovertemplate=(
                        "연령: %{customdata}"
                        "<br>"
                        "면허 소지자: %{x:,}명"
                        "<extra></extra>"
                    ),
                )
            )


            # =================================================
            # 65세 이상
            # =================================================

            fig.add_trace(
                go.Bar(

                    x=senior_df[
                        count_col
                    ],

                    y=senior_df[
                        "y_position"
                    ],

                    orientation="h",

                    name="65세 이상",

                    marker=dict(
                        color="#D8A64F",
                    ),

                    text=[
                        f"{int(v):,}명"
                        for v in senior_df[
                            count_col
                        ]
                    ],

                    textposition="outside",

                    textfont=dict(
                        color="#F4F6FA",
                        size=14,
                    ),

                    cliponaxis=False,

                    customdata=senior_df[
                        age_col
                    ],

                    hovertemplate=(
                        "연령: %{customdata}"
                        "<br>"
                        "면허 소지자: %{x:,}명"
                        "<extra></extra>"
                    ),
                )
            )


            # =================================================
            # 65세 기준선
            # =================================================

            first_senior_positions = (
                chart_df.loc[
                    chart_df[
                        "is_senior"
                    ],
                    "y_position",
                ]
            )


            if not first_senior_positions.empty:

                first_senior = (
                    first_senior_positions.min()
                )


                fig.add_hline(

                    y=first_senior - 0.5,

                    line_dash="dot",

                    line_color="#F0B95C",

                    line_width=2,

                    annotation_text="65세 이상",

                    annotation_position="top right",

                    annotation_font=dict(
                        color="#F0B95C",
                        size=13,
                    ),
                )


            # =================================================
            # MAX VALUE
            # =================================================

            max_count = float(
                chart_df[
                    count_col
                ].max()
            )


            if max_count <= 0:

                max_count = 1


            # =================================================
            # CHART LAYOUT
            # =================================================

            fig.update_layout(

                # 연령이 많으면 차트 높이 자동 증가
                height=max(
                    620,
                    37 * len(
                        chart_df
                    ),
                ),

                margin=dict(
                    l=105,
                    r=190,
                    t=70,
                    b=80,
                ),

                paper_bgcolor="#182035",

                plot_bgcolor="#182035",

                font=dict(
                    color="#E6EAF1",
                    size=13,
                ),

                barmode="overlay",

                bargap=0.22,

                showlegend=True,


                # =============================================
                # LEGEND
                # =============================================

                legend=dict(

                    orientation="h",

                    yanchor="bottom",

                    y=1.015,

                    xanchor="right",

                    x=1,

                    font=dict(
                        color="#E8EBF1",
                        size=13,
                    ),

                    bgcolor="rgba(0,0,0,0)",
                ),


                # =============================================
                # X AXIS
                # =============================================

                xaxis=dict(

                    title=dict(

                        text=(
                            "운전면허 소지자 수(명)"
                        ),

                        font=dict(
                            color="#D8DEE8",
                            size=14,
                        ),
                    ),

                    showgrid=True,

                    gridcolor="#35405A",

                    gridwidth=1,

                    zeroline=False,

                    tickformat=",",

                    tickfont=dict(
                        color="#C2C9D5",
                        size=12,
                    ),

                    range=[
                        0,
                        max_count * 1.25,
                    ],
                ),


                # =============================================
                # Y AXIS
                # =============================================

                yaxis=dict(

                    title=None,

                    tickmode="array",

                    tickvals=chart_df[
                        "y_position"
                    ],

                    ticktext=[
                        format_age(
                            value
                        )
                        for value in chart_df[
                            age_col
                        ]
                    ],

                    tickfont=dict(
                        color="#F0F2F6",
                        size=13,
                    ),

                    showgrid=False,

                    zeroline=False,

                    autorange=True,
                ),
            )


            # =================================================
            # PLOT
            # =================================================

            st.plotly_chart(

                fig,

                use_container_width=True,

                config={
                    "displayModeBar": False,
                    "responsive": True,
                },
            )


            st.html(
                """
                <div class="senior-note">
                    ─ ─ 65세 이상 고령운전자 구간
                </div>
                """
            )


    # ========================================================
    # DETAIL DATA
    # ========================================================

    st.write("")


    with st.expander(
        "연령별 데이터 상세 보기"
    ):

        if chart_df.empty:

            st.info(
                "표시할 데이터가 없습니다."
            )

        else:

            table_df = chart_df[
                [
                    age_col,
                    count_col,
                ]
            ].copy()


            table_df[
                "구분"
            ] = chart_df[
                "is_senior"
            ].map(
                {
                    True: "65세 이상",
                    False: "65세 미만",
                }
            )


            table_df[
                age_col
            ] = table_df[
                age_col
            ].apply(
                format_age
            )


            table_df[
                count_col
            ] = table_df[
                count_col
            ].astype(
                int
            )


            table_df.columns = [
                "연령",
                "면허 소지자 수",
                "구분",
            ]


            st.dataframe(
                table_df,
                use_container_width=True,
                hide_index=True,

                column_config={

                    "연령":
                        st.column_config.TextColumn(
                            "연령",
                            width="small",
                        ),

                    "면허 소지자 수":
                        st.column_config.NumberColumn(
                            "면허 소지자 수",
                            format="%d명",
                        ),

                    "구분":
                        st.column_config.TextColumn(
                            "구분",
                            width="medium",
                        ),
                },
            )