import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sqlalchemy import text


# ============================================================
# PROJECT ROOT
# SAFE/streamlit/pages/car/license_gender.py
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
def load_license_gender():

    engine = get_engine()

    query = text(
        """
        SELECT *
        FROM license_holder_gender
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
    df = load_license_gender()

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


gender_col = find_column(
    [
        "gender",
        "sex",
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

if gender_col is None:

    st.error(
        f"""
        license_holder_gender 테이블에서
        성별 컬럼을 찾을 수 없습니다.

        현재 컬럼:
        {list(df.columns)}
        """
    )

    st.stop()


if count_col is None:

    st.error(
        f"""
        license_holder_gender 테이블에서
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


df[gender_col] = (
    df[gender_col]
    .fillna("")
    .astype(str)
    .str.strip()
)


# ============================================================
# GENDER NORMALIZE
# ============================================================

def normalize_gender(value):

    value = str(value).strip()

    if value in [
        "남",
        "남자",
        "남성",
        "male",
        "Male",
        "MALE",
        "M",
    ]:
        return "남성"

    if value in [
        "여",
        "여자",
        "여성",
        "female",
        "Female",
        "FEMALE",
        "F",
    ]:
        return "여성"

    return value


df["gender_name"] = (
    df[gender_col]
    .apply(
        normalize_gender
    )
)


# ============================================================
# REMOVE TOTAL / UNKNOWN
# ============================================================

df = df[
    ~df["gender_name"].isin(
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

    background: rgba(255,255,255,.98);

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
   ACTIVE CAR
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
   PAGE
========================================================== */

.st-key-license_gender_page {

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
   SELECTBOX
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

    min-height: 112px;

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


/* ==========================================================
   CHART PANELS
========================================================== */

.st-key-gender_panel,
.st-key-gender_ratio_panel,
.st-key-trend_panel {

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

    min-height:
        480px;
}


.st-key-trend_panel {
    min-height: auto;
}


/* ==========================================================
   PANEL TEXT
========================================================== */

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
   RESPONSIVE
========================================================== */

@media(max-width:1100px) {

    .page-title {
        font-size:34px;
    }

    .st-key-license_gender_page {
        padding:24px;
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


    with logo:

        if st.button(
            "SAFER",
            key="nav_logo",
        ):
            go_main()


    with n1:

        if st.button(
            "인구",
            key="nav_people",
            use_container_width=True,
        ):
            go_people()


    with n2:

        if st.button(
            "자동차",
            key="nav_car",
            use_container_width=True,
        ):
            go_car()


    with n3:

        if st.button(
            "교통사고",
            key="nav_accident",
            use_container_width=True,
        ):
            go_accident()


    with n4:

        if st.button(
            "제도",
            key="nav_policy",
            use_container_width=True,
        ):
            go_policy()


    with n5:

        if st.button(
            "FAQ",
            key="nav_faq",
            use_container_width=True,
        ):
            go_faq()


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
    key="license_gender_page"
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
                성별 운전면허 소지자 현황
            </div>

            <div class="page-sub">
                남성·여성 운전면허 소지자 규모와 구성비를 비교하고
                성별 면허 보유 구조를 확인합니다.
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
    # YEAR FILTER
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
    # GENDER AGGREGATE
    # ========================================================

    gender_df = (
        filtered
        .groupby(
            "gender_name",
            as_index=False,
        )[count_col]
        .sum()
    )


    gender_order = {
        "남성": 0,
        "여성": 1,
    }


    gender_df[
        "gender_order"
    ] = (
        gender_df[
            "gender_name"
        ]
        .map(
            gender_order
        )
        .fillna(99)
    )


    gender_df = (
        gender_df
        .sort_values(
            "gender_order"
        )
        .reset_index(
            drop=True
        )
    )


    # ========================================================
    # KPI CALCULATION
    # ========================================================

    total_count = int(
        gender_df[
            count_col
        ].sum()
    )


    male_count = int(
        gender_df.loc[
            gender_df[
                "gender_name"
            ] == "남성",
            count_col,
        ].sum()
    )


    female_count = int(
        gender_df.loc[
            gender_df[
                "gender_name"
            ] == "여성",
            count_col,
        ].sum()
    )


    # ========================================================
    # KPI CARDS
    # ========================================================

    st.write("")


    k1, k2, k3 = st.columns(
        3
    )


    # TOTAL
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


    # MALE
    with k2:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    남성 면허 소지자
                </div>

                <div class="kpi-value">
                    {male_count:,}명
                </div>

            </div>
            """
        )


    # FEMALE
    with k3:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    여성 면허 소지자
                </div>

                <div class="kpi-value">
                    {female_count:,}명
                </div>

            </div>
            """
        )


    # ========================================================
    # BAR + DONUT
    # ========================================================

    chart_left, chart_right = st.columns(
        [
            1.7,
            1,
        ],
        gap="medium",
    )


    # ========================================================
    # LEFT BAR CHART
    # ========================================================

    with chart_left:

        with st.container(
            key="gender_panel"
        ):

            st.html(
                """
                <div class="panel-title">
                    성별 운전면허 소지자 현황
                </div>

                <div class="panel-sub">
                    X축: 운전면허 소지자 수(명) ·
                    Y축: 성별 ·
                    실제 면허 소지자 규모를 비교합니다.
                </div>
                """
            )


            if gender_df.empty:

                st.warning(
                    "선택한 조건에 해당하는 데이터가 없습니다."
                )


            else:

                bar_df = gender_df[
                    gender_df[
                        "gender_name"
                    ].isin(
                        [
                            "남성",
                            "여성",
                        ]
                    )
                ].copy()


                colors = []

                for gender in bar_df[
                    "gender_name"
                ]:

                    if gender == "남성":

                        colors.append(
                            "#69A7C4"
                        )

                    else:

                        colors.append(
                            "#D8A64F"
                        )


                max_count = float(
                    bar_df[
                        count_col
                    ].max()
                )


                if max_count <= 0:

                    max_count = 1


                fig_bar = go.Figure(
                    go.Bar(

                        x=bar_df[
                            count_col
                        ],

                        y=bar_df[
                            "gender_name"
                        ],

                        orientation="h",

                        marker=dict(
                            color=colors,
                        ),

                        text=[
                            f"{int(value):,}명"
                            for value
                            in bar_df[
                                count_col
                            ]
                        ],

                        textposition="outside",

                        textfont=dict(
                            color="#F4F6FA",
                            size=15,
                        ),

                        cliponaxis=False,

                        hovertemplate=(
                            "<b>%{y}</b>"
                            "<br>"
                            "면허 소지자: %{x:,}명"
                            "<extra></extra>"
                        ),
                    )
                )


                fig_bar.update_layout(

                    height=380,

                    margin=dict(
                        l=80,
                        r=170,
                        t=35,
                        b=70,
                    ),

                    paper_bgcolor="#182035",

                    plot_bgcolor="#182035",

                    showlegend=False,

                    font=dict(
                        color="#E6EAF1",
                        size=14,
                    ),

                    bargap=.38,

                    xaxis=dict(

                        title=dict(
                            text="운전면허 소지자 수(명)",

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
                            color="#C2C9D5",
                            size=12,
                        ),

                        range=[
                            0,
                            max_count * 1.25,
                        ],
                    ),

                    yaxis=dict(

                        title=None,

                        showgrid=False,

                        tickfont=dict(
                            color="#F0F2F6",
                            size=16,
                        ),

                        categoryorder="array",

                        categoryarray=[
                            "남성",
                            "여성",
                        ],

                        autorange="reversed",
                    ),
                )


                st.plotly_chart(
                    fig_bar,
                    use_container_width=True,

                    config={
                        "displayModeBar": False,
                    },
                )


    # ========================================================
    # RIGHT DONUT
    # ========================================================

    with chart_right:

        with st.container(
            key="gender_ratio_panel"
        ):

            st.html(
                """
                <div class="panel-title">
                    성별 면허 소지자 구성비
                </div>

                <div class="panel-sub">
                    전체 면허 소지자 중
                    남성·여성의 구성 비율을 확인합니다.
                </div>
                """
            )


            pie_df = gender_df[
                gender_df[
                    "gender_name"
                ].isin(
                    [
                        "남성",
                        "여성",
                    ]
                )
            ].copy()


            if (
                pie_df.empty
                or total_count == 0
            ):

                st.warning(
                    "구성비를 계산할 데이터가 없습니다."
                )


            else:

                pie_colors = []

                for gender in pie_df[
                    "gender_name"
                ]:

                    if gender == "남성":

                        pie_colors.append(
                            "#69A7C4"
                        )

                    else:

                        pie_colors.append(
                            "#D8A64F"
                        )


                fig_pie = go.Figure(
                    go.Pie(

                        labels=pie_df[
                            "gender_name"
                        ],

                        values=pie_df[
                            count_col
                        ],

                        hole=.62,

                        sort=False,

                        marker=dict(

                            colors=pie_colors,

                            line=dict(
                                color="#182035",
                                width=4,
                            ),
                        ),

                        textinfo="percent",

                        textposition="inside",

                        textfont=dict(
                            color="#FFFFFF",
                            size=16,
                        ),

                        hovertemplate=(
                            "<b>%{label}</b>"
                            "<br>"
                            "%{value:,}명"
                            "<br>"
                            "%{percent}"
                            "<extra></extra>"
                        ),
                    )
                )


                fig_pie.add_annotation(

                    x=.5,
                    y=.5,

                    text=(
                        f"<b>{total_count:,}</b>"
                        "<br>"
                        "<span style='font-size:12px'>전체 면허소지자</span>"
                    ),

                    showarrow=False,

                    font=dict(
                        color="#FFFFFF",
                        size=17,
                    ),

                    align="center",
                )


                fig_pie.update_layout(

                    height=380,

                    margin=dict(
                        l=15,
                        r=15,
                        t=20,
                        b=50,
                    ),

                    paper_bgcolor="#182035",

                    plot_bgcolor="#182035",

                    font=dict(
                        color="#E6EAF1",
                        size=13,
                    ),

                    legend=dict(

                        orientation="h",

                        yanchor="bottom",

                        y=-.05,

                        xanchor="center",

                        x=.5,

                        font=dict(
                            color="#E6EAF1",
                            size=14,
                        ),
                    ),
                )


                st.plotly_chart(
                    fig_pie,
                    use_container_width=True,

                    config={
                        "displayModeBar": False,
                    },
                )


    # ========================================================
    # YEARLY TREND
    # ========================================================

    if year_col is not None:

        available_year_count = (
            df[
                year_col
            ]
            .dropna()
            .nunique()
        )


        if available_year_count >= 2:

            with st.container(
                key="trend_panel"
            ):

                st.html(
                    """
                    <div class="panel-title">
                        연도별 성별 운전면허 소지자 추세
                    </div>

                    <div class="panel-sub">
                        남성과 여성의 운전면허 소지자 수가
                        연도별로 어떻게 변화했는지 비교합니다.
                    </div>
                    """
                )


                trend_source = df.copy()


                # 면허 대분류 필터 유지
                if (
                    license_main_col is not None
                    and selected_main != "전체"
                ):

                    trend_source = trend_source[
                        trend_source[
                            license_main_col
                        ].astype(str)
                        == selected_main
                    ]


                # 면허 세부 필터 유지
                if (
                    license_sub_col is not None
                    and selected_sub != "전체"
                ):

                    trend_source = trend_source[
                        trend_source[
                            license_sub_col
                        ].astype(str)
                        == selected_sub
                    ]


                trend_df = (
                    trend_source

                    .groupby(
                        [
                            year_col,
                            "gender_name",
                        ],
                        as_index=False,
                    )[count_col]

                    .sum()
                )


                male_trend = trend_df[
                    trend_df[
                        "gender_name"
                    ] == "남성"
                ]


                female_trend = trend_df[
                    trend_df[
                        "gender_name"
                    ] == "여성"
                ]


                fig_trend = go.Figure()


                # =================================================
                # MALE
                # =================================================

                if not male_trend.empty:

                    fig_trend.add_trace(
                        go.Scatter(

                            x=male_trend[
                                year_col
                            ],

                            y=male_trend[
                                count_col
                            ],

                            mode="lines+markers",

                            name="남성",

                            line=dict(
                                color="#69A7C4",
                                width=4,
                            ),

                            marker=dict(
                                size=9,
                            ),

                            hovertemplate=(
                                "%{x}년"
                                "<br>"
                                "남성: %{y:,}명"
                                "<extra></extra>"
                            ),
                        )
                    )


                # =================================================
                # FEMALE
                # =================================================

                if not female_trend.empty:

                    fig_trend.add_trace(
                        go.Scatter(

                            x=female_trend[
                                year_col
                            ],

                            y=female_trend[
                                count_col
                            ],

                            mode="lines+markers",

                            name="여성",

                            line=dict(
                                color="#D8A64F",
                                width=4,
                            ),

                            marker=dict(
                                size=9,
                            ),

                            hovertemplate=(
                                "%{x}년"
                                "<br>"
                                "여성: %{y:,}명"
                                "<extra></extra>"
                            ),
                        )
                    )


                fig_trend.update_layout(

                    height=430,

                    margin=dict(
                        l=95,
                        r=40,
                        t=40,
                        b=70,
                    ),

                    paper_bgcolor="#182035",

                    plot_bgcolor="#182035",

                    font=dict(
                        color="#E6EAF1",
                        size=13,
                    ),

                    hovermode="x unified",

                    legend=dict(

                        orientation="h",

                        yanchor="bottom",

                        y=1.02,

                        xanchor="right",

                        x=1,

                        font=dict(
                            color="#E6EAF1",
                            size=13,
                        ),
                    ),

                    xaxis=dict(

                        title="연도",

                        showgrid=False,

                        dtick=1,

                        tickformat=".0f",

                        tickfont=dict(
                            color="#C6CDD9",
                            size=13,
                        ),
                    ),

                    yaxis=dict(

                        title="운전면허 소지자 수(명)",

                        showgrid=True,

                        gridcolor="#35405A",

                        zeroline=False,

                        tickformat=",",

                        tickfont=dict(
                            color="#C6CDD9",
                            size=13,
                        ),
                    ),
                )


                st.plotly_chart(
                    fig_trend,
                    use_container_width=True,

                    config={
                        "displayModeBar": False,
                    },
                )


    # ========================================================
    # DETAIL DATA
    # ========================================================

    st.write("")


    with st.expander(
        "성별 데이터 상세 보기"
    ):

        table_df = gender_df[
            [
                "gender_name",
                count_col,
            ]
        ].copy()


        # 상세표에서는 비율을 남겨둠
        # KPI에서만 제거한 것
        if total_count > 0:

            table_df[
                "ratio"
            ] = (
                table_df[
                    count_col
                ]
                / total_count
                * 100
            )

        else:

            table_df[
                "ratio"
            ] = 0


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
            "ratio"
        ] = (
            table_df[
                "ratio"
            ]
            .round(1)
        )


        table_df.columns = [
            "성별",
            "면허 소지자 수",
            "전체 비중",
        ]


        st.dataframe(
            table_df,

            use_container_width=True,

            hide_index=True,

            column_config={

                "성별":
                    st.column_config.TextColumn(
                        "성별",
                    ),

                "면허 소지자 수":
                    st.column_config.NumberColumn(
                        "면허 소지자 수",
                        format="%d명",
                    ),

                "전체 비중":
                    st.column_config.NumberColumn(
                        "전체 비중",
                        format="%.1f%%",
                    ),
            },
        )