import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sqlalchemy import text


# ============================================================
# PROJECT ROOT
# SAFE/streamlit/pages/car/return_2023.py
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
def load_return_2023():

    engine = get_engine()

    query = text(
        """
        SELECT
            id,
            region,
            age,
            age_label,
            count
        FROM return_driver_license_2023
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
    df = load_return_2023()

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


df["age_label"] = (
    df["age_label"]
    .fillna("")
    .astype(str)
    .str.strip()
)


df["age"] = pd.to_numeric(
    df["age"],
    errors="coerce"
)


df["count"] = pd.to_numeric(
    df["count"],
    errors="coerce"
).fillna(0)


# ============================================================
# REMOVE INVALID
# ============================================================

df = df[
    ~df["region"].isin(
        [
            "",
            "계",
            "합계",
            "총계",
            "전국",
            "미상",
            "불명",
        ]
    )
].copy()


df = df[
    df["age"].notna()
].copy()


df["age"] = df["age"].astype(int)


# ============================================================
# REGION SHORT NAME
# ============================================================

REGION_MAP = {

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


def short_region(value):

    return REGION_MAP.get(
        str(value).strip(),
        str(value).strip()
    )


df["short_region"] = (
    df["region"]
    .apply(short_region)
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
   NAVIGATION
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


.st-key-nav_car button {

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

.st-key-return_2023_page {

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


/* ==========================================================
   PANELS
========================================================== */

.st-key-region_panel,
.st-key-age_panel,
.st-key-heatmap_panel {

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
        #E7EAF0 !important;

    font-size:
        14px !important;

    font-weight:
        600 !important;
}


/* ==========================================================
   RESPONSIVE
========================================================== */

@media(max-width:1100px) {

    .page-title {
        font-size:34px;
    }

    .st-key-return_2023_page {
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
    key="return_2023_page"
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
                자동차 &gt; 운전면허 자진반납
            </div>

            <div class="page-title">
                2023년 운전면허 자진반납 현황
            </div>

            <div class="page-sub">
                2023년 지역별·연령별 운전면허 자진반납 현황을 분석하여
                어느 지역과 연령에서 자진반납이 많이 이루어졌는지 확인합니다.
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
    # FILTER
    # ========================================================

    f1, f2, empty = st.columns(
        [
            1,
            1,
            3,
        ]
    )


    # ========================================================
    # REGION FILTER
    # ========================================================

    with f1:

        region_options = [
            "전체"
        ] + sorted(
            df[
                "short_region"
            ]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )


        selected_region = st.selectbox(
            "지역",
            region_options
        )


    # ========================================================
    # AGE FILTER
    # ========================================================

    with f2:

        age_options_df = (
            df[
                [
                    "age",
                    "age_label",
                ]
            ]
            .drop_duplicates()
            .sort_values(
                "age"
            )
        )


        age_options = [
            "전체"
        ] + age_options_df[
            "age_label"
        ].tolist()


        selected_age = st.selectbox(
            "연령",
            age_options
        )


    # ========================================================
    # FILTER DATA
    # ========================================================

    filtered = df.copy()


    if selected_region != "전체":

        filtered = filtered[
            filtered[
                "short_region"
            ] == selected_region
        ]


    if selected_age != "전체":

        filtered = filtered[
            filtered[
                "age_label"
            ] == selected_age
        ]


    # ========================================================
    # KPI
    # ========================================================

    total_return = int(
        filtered[
            "count"
        ].sum()
    )


    # ========================================================
    # TOP REGION
    # ========================================================

    region_sum = (
        filtered
        .groupby(
            "short_region",
            as_index=False
        )["count"]
        .sum()
    )


    if not region_sum.empty:

        top_region_row = region_sum.loc[
            region_sum[
                "count"
            ].idxmax()
        ]


        top_region = str(
            top_region_row[
                "short_region"
            ]
        )


        top_region_count = int(
            top_region_row[
                "count"
            ]
        )

    else:

        top_region = "-"
        top_region_count = 0


    # ========================================================
    # TOP AGE
    # ========================================================

    age_sum = (
        filtered
        .groupby(
            [
                "age",
                "age_label",
            ],
            as_index=False
        )["count"]
        .sum()
    )


    if not age_sum.empty:

        top_age_row = age_sum.loc[
            age_sum[
                "count"
            ].idxmax()
        ]


        top_age = str(
            top_age_row[
                "age_label"
            ]
        )


        top_age_count = int(
            top_age_row[
                "count"
            ]
        )

    else:

        top_age = "-"
        top_age_count = 0


    # ========================================================
    # KPI CARDS
    # ========================================================

    st.write("")


    k1, k2, k3 = st.columns(
        3
    )


    with k1:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    2023년 자진반납 건수
                </div>

                <div class="kpi-value">
                    {total_return:,}건
                </div>

            </div>
            """
        )


    with k2:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    자진반납 최다 지역
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
                    자진반납 최다 연령
                </div>

                <div class="kpi-value">
                    {top_age}
                </div>

            </div>
            """
        )


    # ========================================================
    # REGION + AGE CHART
    # ========================================================

    left, right = st.columns(
        [
            1.5,
            1,
        ],
        gap="medium"
    )


    # ========================================================
    # REGION BAR CHART
    # ========================================================

    with left:

        with st.container(
            key="region_panel"
        ):

            st.html(
                """
                <div class="panel-title">
                    지역별 운전면허 자진반납 현황
                </div>

                <div class="panel-sub">
                    2023년 지역별 운전면허 자진반납 건수를 비교합니다.
                </div>
                """
            )


            region_chart_df = (
                region_sum
                .sort_values(
                    "count",
                    ascending=True
                )
                .copy()
            )


            if region_chart_df.empty:

                st.warning(
                    "표시할 데이터가 없습니다."
                )


            else:

                max_value = float(
                    region_chart_df[
                        "count"
                    ].max()
                )


                if max_value <= 0:
                    max_value = 1


                colors = [
                    (
                        "#E0A548"
                        if value == max_value
                        else "#8A7652"
                    )
                    for value
                    in region_chart_df[
                        "count"
                    ]
                ]


                fig_region = go.Figure(
                    go.Bar(

                        x=region_chart_df[
                            "count"
                        ],

                        y=region_chart_df[
                            "short_region"
                        ],

                        orientation="h",

                        marker=dict(
                            color=colors
                        ),

                        text=[
                            f"{int(value):,}건"
                            for value
                            in region_chart_df[
                                "count"
                            ]
                        ],

                        textposition="outside",

                        textfont=dict(
                            color="#F2F4F8",
                            size=12,
                        ),

                        cliponaxis=False,

                        hovertemplate=(
                            "<b>%{y}</b>"
                            "<br>"
                            "자진반납: %{x:,}건"
                            "<extra></extra>"
                        ),
                    )
                )


                fig_region.update_layout(

                    height=560,

                    margin=dict(
                        l=75,
                        r=140,
                        t=25,
                        b=65,
                    ),

                    paper_bgcolor="#182035",

                    plot_bgcolor="#182035",

                    showlegend=False,

                    bargap=.25,

                    font=dict(
                        color="#E7EAF0",
                        size=13,
                    ),

                    xaxis=dict(

                        title="자진반납 건수",

                        showgrid=True,

                        gridcolor="#35405A",

                        zeroline=False,

                        tickformat=",",

                        tickfont=dict(
                            color="#C6CDD9",
                            size=11,
                        ),

                        range=[
                            0,
                            max_value * 1.23,
                        ],
                    ),

                    yaxis=dict(

                        title=None,

                        showgrid=False,

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
                    },
                )


    # ========================================================
    # AGE BAR CHART
    # ========================================================

    with right:

        with st.container(
            key="age_panel"
        ):

            st.html(
                """
                <div class="panel-title">
                    연령별 운전면허 자진반납 현황
                </div>

                <div class="panel-sub">
                    연령별 자진반납 규모를 비교하여
                    어떤 연령에서 반납이 집중되는지 확인합니다.
                </div>
                """
            )


            age_chart_df = (
                age_sum
                .sort_values(
                    "age",
                    ascending=True
                )
                .copy()
            )


            if age_chart_df.empty:

                st.warning(
                    "표시할 데이터가 없습니다."
                )


            else:

                max_age_count = float(
                    age_chart_df[
                        "count"
                    ].max()
                )


                if max_age_count <= 0:
                    max_age_count = 1


                age_colors = [
                    (
                        "#D9A64A"
                        if value == max_age_count
                        else "#79B69B"
                    )
                    for value
                    in age_chart_df[
                        "count"
                    ]
                ]


                fig_age = go.Figure(
                    go.Bar(

                        x=age_chart_df[
                            "age_label"
                        ],

                        y=age_chart_df[
                            "count"
                        ],

                        marker=dict(
                            color=age_colors
                        ),

                        text=[
                            f"{int(value):,}"
                            for value
                            in age_chart_df[
                                "count"
                            ]
                        ],

                        textposition="outside",

                        textfont=dict(
                            color="#F2F4F8",
                            size=11,
                        ),

                        hovertemplate=(
                            "<b>%{x}</b>"
                            "<br>"
                            "자진반납: %{y:,}건"
                            "<extra></extra>"
                        ),
                    )
                )


                fig_age.update_layout(

                    height=560,

                    margin=dict(
                        l=70,
                        r=35,
                        t=25,
                        b=90,
                    ),

                    paper_bgcolor="#182035",

                    plot_bgcolor="#182035",

                    showlegend=False,

                    font=dict(
                        color="#E7EAF0",
                        size=13,
                    ),

                    xaxis=dict(

                        title="연령",

                        showgrid=False,

                        tickangle=-45,

                        tickfont=dict(
                            color="#F0F2F6",
                            size=11,
                        ),
                    ),

                    yaxis=dict(

                        title="자진반납 건수",

                        showgrid=True,

                        gridcolor="#35405A",

                        zeroline=False,

                        tickformat=",",

                        tickfont=dict(
                            color="#C6CDD9",
                            size=11,
                        ),
                    ),
                )


                st.plotly_chart(

                    fig_age,

                    use_container_width=True,

                    config={
                        "displayModeBar": False,
                    },
                )


    # ========================================================
    # HEATMAP
    # ========================================================

    with st.container(
        key="heatmap_panel"
    ):

        st.html(
            """
            <div class="panel-title">
                지역 × 연령 운전면허 자진반납 Heatmap
            </div>

            <div class="panel-sub">
                지역과 연령을 동시에 비교하여
                자진반납이 집중되는 구간을 확인합니다.
            </div>
            """
        )


        heatmap_source = df.copy()


        # 지역 필터가 선택되어 있으면 반영
        if selected_region != "전체":

            heatmap_source = heatmap_source[
                heatmap_source[
                    "short_region"
                ] == selected_region
            ]


        # 연령 필터 선택 반영
        if selected_age != "전체":

            heatmap_source = heatmap_source[
                heatmap_source[
                    "age_label"
                ] == selected_age
            ]


        heatmap_df = (
            heatmap_source

            .pivot_table(

                index="short_region",

                columns="age_label",

                values="count",

                aggfunc="sum",

                fill_value=0
            )
        )


        # ====================================================
        # AGE ORDER
        # ====================================================

        age_order = (
            heatmap_source[
                [
                    "age",
                    "age_label",
                ]
            ]
            .drop_duplicates()
            .sort_values(
                "age"
            )[
                "age_label"
            ]
            .tolist()
        )


        existing_age_order = [
            age
            for age in age_order
            if age in heatmap_df.columns
        ]


        heatmap_df = (
            heatmap_df[
                existing_age_order
            ]
        )


        if heatmap_df.empty:

            st.warning(
                "히트맵을 표시할 데이터가 없습니다."
            )


        else:

            fig_heatmap = go.Figure(
                go.Heatmap(

                    z=heatmap_df.values,

                    x=heatmap_df.columns,

                    y=heatmap_df.index,

                    colorscale=[

                        [0.00, "#172338"],

                        [0.25, "#2E5D73"],

                        [0.50, "#56A18A"],

                        [0.75, "#D2AE52"],

                        [1.00, "#D15A45"],
                    ],

                    colorbar=dict(

                        title=dict(
                            text="반납 건수",

                            font=dict(
                                color="#E7EAF0",
                                size=12,
                            ),
                        ),

                        tickfont=dict(
                            color="#D5DAE4",
                            size=11,
                        ),

                        thickness=17,
                    ),

                    hovertemplate=(
                        "<b>%{y}</b>"
                        "<br>"
                        "연령: %{x}"
                        "<br>"
                        "자진반납: %{z:,}건"
                        "<extra></extra>"
                    ),
                )
            )


            fig_heatmap.update_layout(

                height=540,

                margin=dict(
                    l=80,
                    r=80,
                    t=25,
                    b=85,
                ),

                paper_bgcolor="#182035",

                plot_bgcolor="#182035",

                font=dict(
                    color="#E7EAF0",
                    size=13,
                ),

                xaxis=dict(

                    title="연령",

                    tickangle=-45,

                    tickfont=dict(
                        color="#D7DCE5",
                        size=11,
                    ),
                ),

                yaxis=dict(

                    title="지역",

                    tickfont=dict(
                        color="#D7DCE5",
                        size=11,
                    ),
                ),
            )


            st.plotly_chart(

                fig_heatmap,

                use_container_width=True,

                config={
                    "displayModeBar": False,
                },
            )


    # ========================================================
    # SUMMARY
    # ========================================================

    if not filtered.empty:

        st.html(
            f"""
            <div class="info-box">

                <b>2023년 운전면허 자진반납 현황 요약</b>
                <br><br>

                선택 조건에서 운전면허 자진반납 건수는
                <b>{total_return:,}건</b>입니다.
                <br>

                자진반납이 가장 많은 지역은
                <b>{top_region}</b>으로
                <b>{top_region_count:,}건</b>입니다.
                <br>

                가장 많은 자진반납이 발생한 연령은
                <b>{top_age}</b>이며
                <b>{top_age_count:,}건</b>입니다.

            </div>
            """
        )


    # ========================================================
    # DETAIL TABLE
    # ========================================================

    st.write("")


    with st.expander(
        "2023년 자진반납 데이터 상세 보기"
    ):

        table_df = (
            filtered[
                [
                    "short_region",
                    "age",
                    "age_label",
                    "count",
                ]
            ]
            .copy()
        )


        table_df = (
            table_df

            .sort_values(
                [
                    "short_region",
                    "age",
                ]
            )

            .reset_index(
                drop=True
            )
        )


        table_df[
            "count"
        ] = (
            table_df[
                "count"
            ]
            .round()
            .astype(int)
        )


        table_df.columns = [
            "지역",
            "연령",
            "연령 구분",
            "자진반납 건수",
        ]


        st.dataframe(

            table_df,

            use_container_width=True,

            hide_index=True,

            column_config={

                "지역":
                    st.column_config.TextColumn(
                        "지역"
                    ),

                "연령":
                    st.column_config.NumberColumn(
                        "연령",
                        format="%d세"
                    ),

                "연령 구분":
                    st.column_config.TextColumn(
                        "연령 구분"
                    ),

                "자진반납 건수":
                    st.column_config.NumberColumn(
                        "자진반납 건수",
                        format="%d건"
                    ),
            },
        )