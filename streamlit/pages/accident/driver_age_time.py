import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sqlalchemy import text


# ============================================================
# PROJECT ROOT
# SAFE/streamlit/pages/accident/driver_age_time.py
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
def load_driver_time_accident():

    engine = get_engine()

    query = text(
        """
        SELECT
            id,
            age_group,
            time_00_02,
            time_02_04,
            time_04_06,
            time_06_08,
            time_08_10,
            time_10_12,
            time_12_14,
            time_14_16,
            time_16_18,
            time_18_20,
            time_20_22,
            time_22_24
        FROM driver_time_accident
        ORDER BY id
        """
    )

    with engine.connect() as conn:
        df = pd.read_sql(
            query,
            conn
        )

    return df


# ============================================================
# LOAD DATA
# ============================================================

try:
    df = load_driver_time_accident()

except Exception as e:

    st.error(
        f"MySQL 데이터 조회 실패\n\n{e}"
    )

    st.stop()


# ============================================================
# TIME COLUMN
# ============================================================

TIME_COLUMNS = [
    "time_00_02",
    "time_02_04",
    "time_04_06",
    "time_06_08",
    "time_08_10",
    "time_10_12",
    "time_12_14",
    "time_14_16",
    "time_16_18",
    "time_18_20",
    "time_20_22",
    "time_22_24",
]


TIME_LABELS = {
    "time_00_02": "00~02시",
    "time_02_04": "02~04시",
    "time_04_06": "04~06시",
    "time_06_08": "06~08시",
    "time_08_10": "08~10시",
    "time_10_12": "10~12시",
    "time_12_14": "12~14시",
    "time_14_16": "14~16시",
    "time_16_18": "16~18시",
    "time_18_20": "18~20시",
    "time_20_22": "20~22시",
    "time_22_24": "22~24시",
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


# ============================================================
# BASIC CLEAN
# ============================================================

df["age_group"] = (
    df["age_group"]
    .fillna("")
    .astype(str)
    .str.strip()
)


for column in TIME_COLUMNS:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    ).fillna(0)


# ============================================================
# INVALID AGE
# ============================================================

INVALID_AGES = [
    "",
    "계",
    "합계",
    "총계",
    "전체",
]


df = df[
    ~df["age_group"].isin(
        INVALID_AGES
    )
].copy()


# ============================================================
# AGE NORMALIZE
# ============================================================

AGE_REPLACE = {

    "19세이하": "19세 이하",
    "19세 이하": "19세 이하",

    "20세이하": "20세 이하",
    "20세 이하": "20세 이하",

    "20-29세": "20~29세",
    "20~29세": "20~29세",

    "21-30세": "21~30세",
    "21~30세": "21~30세",

    "30-39세": "30~39세",
    "30~39세": "30~39세",

    "31-40세": "31~40세",
    "31~40세": "31~40세",

    "40-49세": "40~49세",
    "40~49세": "40~49세",

    "41-50세": "41~50세",
    "41~50세": "41~50세",

    "50-59세": "50~59세",
    "50~59세": "50~59세",

    "51-60세": "51~60세",
    "51~60세": "51~60세",

    "60-64세": "60~64세",
    "60~64세": "60~64세",

    "61-64세": "61~64세",
    "61~64세": "61~64세",

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
    .apply(normalize_age)
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
        .replace("미만", "")
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
# DUPLICATE CLEAN
# ============================================================

df = (
    df
    .groupby(
        "age_group",
        as_index=False
    )[TIME_COLUMNS]
    .sum()
)


# ============================================================
# WIDE -> LONG
# ============================================================

long_df = (
    df
    .melt(
        id_vars=["age_group"],
        value_vars=TIME_COLUMNS,
        var_name="time_code",
        value_name="accidents",
    )
)


long_df["time_slot"] = (
    long_df["time_code"]
    .map(TIME_LABELS)
)


# ============================================================
# AGE LIST
# ============================================================

age_groups = sorted(
    df["age_group"]
    .dropna()
    .unique()
    .tolist(),
    key=age_sort_key
)


if not age_groups:

    st.warning(
        "가해운전자 연령대별 시간대 사고 데이터가 없습니다."
    )

    st.stop()


# ============================================================
# CSS
# ============================================================

st.html(
    """
<style>

/* ==========================================================
   APP BACKGROUND
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

    background: rgba(255,255,255,.98);

    border-radius: 16px;

    padding: 10px 20px;

    margin-bottom: 20px;

    box-shadow:
        0 5px 20px
        rgba(0,0,0,.10);
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

.st-key-driver_time_page {

    background: #101625;

    border: 1px solid #34405A;

    border-radius: 20px;

    padding: 34px 36px 44px 36px;

    box-shadow:
        0 12px 36px
        rgba(0,0,0,.18);
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

    letter-spacing: -2px;

    line-height: 1.15;

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
   FILTER
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

    font-size: 14px !important;
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

    line-height: 1.2;
}


/* ==========================================================
   PANEL
========================================================== */

.st-key-age_time_panel,
.st-key-total_time_panel,
.st-key-heatmap_panel,
.st-key-insight_panel {

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


/* ==========================================================
   INFO BOX
========================================================== */

.info-box {

    background: #121A2B;

    border: 1px solid #35415C;

    border-left: 3px solid #D6A348;

    border-radius: 8px;

    padding: 18px 20px;

    margin-top: 22px;

    color: #E3E8F0;

    font-size: 13px;

    line-height: 1.9;
}


.info-box b {
    color: #FFFFFF;
}


/* ==========================================================
   PLOT TEXT
========================================================== */

.js-plotly-plot .plotly .legendtext,
.js-plotly-plot .plotly .xtick text,
.js-plotly-plot .plotly .ytick text,
.js-plotly-plot .plotly .annotation-text {

    fill: #E8EDF5 !important;
}




/* ==========================================================
   SECTION HEADING
========================================================== */

.section-heading {

    display: flex;

    align-items: center;

    gap: 12px;

    margin: 34px 0 14px 4px;

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
   DETAIL TOGGLE BUTTON
========================================================== */

.st-key-driver_time_detail_toggle button {

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


.st-key-driver_time_detail_toggle button * {

    color: #E7EAF0 !important;

    -webkit-text-fill-color: #E7EAF0 !important;

    opacity: 1 !important;
}


.st-key-driver_time_detail_toggle button:hover {

    background: #202A42 !important;

    border-color: #D6A348 !important;

    color: #F1C66A !important;
}


.st-key-driver_time_detail_toggle button:hover * {

    color: #F1C66A !important;

    -webkit-text-fill-color: #F1C66A !important;
}


/* ==========================================================
   DETAIL TABLE PANEL
========================================================== */

.st-key-driver_time_detail_panel {

    background: #182035;

    border: 1px solid #394560;

    border-radius: 14px;

    padding: 18px 18px 20px 18px;

    margin-top: 10px;
}


/* ==========================================================
   INSIGHT / PREDICTION PANEL
========================================================== */

.st-key-insight_panel {

    background: #182035;

    border: 1px solid #3A4662;

    border-radius: 24px;

    padding: 24px 26px 22px 26px;

    margin-top: 24px;
}


.insight-grid {

    display: grid;

    grid-template-columns: repeat(3, 1fr);

    gap: 14px;

    margin-top: 18px;
}


.insight-card {

    background: #131B2E;

    border: 1px solid #394560;

    border-radius: 16px;

    padding: 18px 20px;

    min-height: 128px;
}


.insight-index {

    color: #D6A348;

    font-size: 11px;

    font-weight: 900;

    margin-bottom: 8px;
}


.insight-title {

    color: #FFFFFF;

    font-size: 14px;

    font-weight: 800;

    margin-bottom: 8px;
}


.insight-body {

    color: #B8C0CF;

    font-size: 12px;

    line-height: 1.7;
}














@media(max-width:1000px) {

    .insight-grid {

        grid-template-columns: 1fr;
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
    key="driver_time_page"
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
                교통사고 &gt; 가해운전자 시간대별 사고
            </div>

            <div class="page-title">
                가해운전자 연령대·시간대 사고 분석
            </div>

            <div class="page-sub">
                가해운전자 연령대와 시간대에 따른 교통사고 분포를 비교하여
                사고가 집중되는 연령대와 시간 구간을 분석합니다.
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

    f1, empty = st.columns(
        [
            1,
            4,
        ]
    )


    with f1:

        default_age_index = (
            age_groups.index(
                "65세 이상"
            )
            if "65세 이상" in age_groups
            else 0
        )

        selected_age = st.selectbox(
            "연령대",
            age_groups,
            index=default_age_index,
            key="driver_time_age"
        )


    # ========================================================
    # SELECTED AGE
    # ========================================================

    selected_df = (
        long_df[
            long_df["age_group"] == selected_age
        ]
        .copy()
    )


    selected_df["time_slot"] = pd.Categorical(
        selected_df["time_slot"],
        categories=TIME_ORDER,
        ordered=True
    )


    selected_df = (
        selected_df
        .sort_values("time_slot")
        .reset_index(drop=True)
    )


    # ========================================================
    # TOTAL TIME
    # ========================================================

    total_time_df = (
        long_df
        .groupby(
            "time_slot",
            as_index=False,
            observed=False
        )["accidents"]
        .sum()
    )


    total_time_df["time_slot"] = pd.Categorical(
        total_time_df["time_slot"],
        categories=TIME_ORDER,
        ordered=True
    )


    total_time_df = (
        total_time_df
        .sort_values("time_slot")
        .reset_index(drop=True)
    )


    # ========================================================
    # KPI CALCULATION
    # ========================================================

    total_selected = int(
        selected_df["accidents"].sum()
    )


    if not selected_df.empty:

        peak_row = (
            selected_df
            .sort_values(
                "accidents",
                ascending=False
            )
            .iloc[0]
        )


        peak_time = str(
            peak_row["time_slot"]
        )


        peak_accidents = int(
            peak_row["accidents"]
        )

    else:

        peak_time = "-"
        peak_accidents = 0


    # ========================================================
    # AGE TOTAL
    # ========================================================

    age_total_df = (
        long_df
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


    if not age_total_df.empty:

        overall_top_age = str(
            age_total_df.iloc[0]["age_group"]
        )

    else:

        overall_top_age = "-"


    # ========================================================
    # NIGHT ACCIDENT
    # ========================================================

    NIGHT_SLOTS = [
        "00~02시",
        "02~04시",
        "04~06시",
        "20~22시",
        "22~24시",
    ]


    night_accidents = int(
        selected_df[
            selected_df["time_slot"].isin(
                NIGHT_SLOTS
            )
        ]["accidents"].sum()
    )


    night_ratio = (
        night_accidents
        / total_selected
        * 100
        if total_selected > 0
        else 0
    )


    st.html(
        """
        <div class="section-heading">
            분석
        </div>
        """
    )


    # ========================================================
    # KPI
    # ========================================================

    st.write("")


    k1, k2, k3, k4 = st.columns(4)


    with k1:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    {selected_age} 전체 사고
                </div>

                <div class="kpi-value">
                    {total_selected:,}건
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
                    {peak_time}
                </div>

            </div>
            """
        )


    with k3:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    {peak_time} 사고 건수
                </div>

                <div class="kpi-value">
                    {peak_accidents:,}건
                </div>

            </div>
            """
        )


    with k4:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    {selected_age} 야간 사고 비중
                </div>

                <div class="kpi-value">
                    {night_ratio:.1f}%
                </div>

            </div>
            """
        )


    # ========================================================
    # ROW 1
    # ========================================================

    left, right = st.columns(
        [
            1,
            1,
        ],
        gap="medium"
    )


    # ========================================================
    # SELECTED AGE TIME CHART
    # ========================================================

    with left:

        with st.container(
            key="age_time_panel"
        ):

            st.html(
                f"""
                <div class="panel-title">
                    {selected_age} 시간대별 사고 분포
                </div>

                <div class="panel-sub">
                    선택한 연령대의 2시간 단위 교통사고 발생 규모를 비교합니다.
                </div>
                """
            )


            bar_colors = [

                "#D9A64A"
                if time == peak_time

                else "#79B69B"

                for time in selected_df["time_slot"]
            ]


            fig_selected = go.Figure(
                go.Bar(

                    x=selected_df["time_slot"],

                    y=selected_df["accidents"],

                    marker_color=bar_colors,

                    text=[
                        f"{int(value):,}"
                        for value
                        in selected_df["accidents"]
                    ],

                    textposition="outside",

                    textfont=dict(
                        color="#FFFFFF",
                        size=10,
                    ),

                    hovertemplate=(
                        "<b>%{x}</b>"
                        "<br>"
                        "사고: %{y:,}건"
                        "<extra></extra>"
                    ),
                )
            )


            max_value = (
                float(
                    selected_df["accidents"].max()
                )
                if not selected_df.empty
                else 1
            )


            if max_value <= 0:
                max_value = 1


            average_accidents = (
                float(
                    selected_df[
                        "accidents"
                    ].mean()
                )
                if not selected_df.empty
                else 0
            )


            if average_accidents > 0:

                fig_selected.add_hline(
                    y=average_accidents,
                    line_dash="dot",
                    line_color="#F0B95C",
                    line_width=2,
                    annotation_text=(
                        f"평균 {average_accidents:,.0f}건"
                    ),
                    annotation_position="top right",
                    annotation_font=dict(
                        color="#F0B95C",
                        size=11,
                    ),
                )


            fig_selected.update_layout(

                height=520,

                margin=dict(
                    l=70,
                    r=40,
                    t=40,
                    b=85,
                ),

                paper_bgcolor="#182035",

                plot_bgcolor="#182035",

                showlegend=False,

                font=dict(
                    color="#E8EDF5",
                    size=12,
                ),

                xaxis=dict(

                    title="시간대",

                    showgrid=False,

                    tickangle=-35,

                    tickfont=dict(
                        color="#D7DEE9",
                    ),
                ),

                yaxis=dict(

                    title="교통사고 건수(건)",

                    showgrid=True,

                    gridcolor="#35405A",

                    zeroline=False,

                    tickformat=",",

                    range=[
                        0,
                        max_value * 1.18
                    ],

                    tickfont=dict(
                        color="#D7DEE9",
                    ),
                ),
            )


            st.plotly_chart(
                fig_selected,

                use_container_width=True,

                config={
                    "displayModeBar": False
                }
            )


    # ========================================================
    # SELECTED AGE VS ALL AGE SHARE
    # ========================================================

    with right:

        with st.container(
            key="total_time_panel"
        ):

            st.html(
                f"""
                <div class="panel-title">
                    {selected_age} vs 전체 연령 시간대별 사고 비중
                </div>

                <div class="panel-sub">
                    사고건수 자체가 아니라 각 집단 내부에서
                    시간대별 사고가 차지하는 비율을 비교합니다.
                </div>
                """
            )


            selected_share_df = (
                selected_df[
                    [
                        "time_slot",
                        "accidents",
                    ]
                ]
                .copy()
            )


            selected_share_total = (
                selected_share_df[
                    "accidents"
                ].sum()
            )


            selected_share_df[
                "share"
            ] = (
                selected_share_df[
                    "accidents"
                ]
                / selected_share_total
                * 100

                if selected_share_total > 0

                else 0
            )


            overall_share_df = (
                total_time_df[
                    [
                        "time_slot",
                        "accidents",
                    ]
                ]
                .copy()
            )


            overall_share_total = (
                overall_share_df[
                    "accidents"
                ].sum()
            )


            overall_share_df[
                "share"
            ] = (
                overall_share_df[
                    "accidents"
                ]
                / overall_share_total
                * 100

                if overall_share_total > 0

                else 0
            )


            fig_compare = go.Figure()


            fig_compare.add_trace(
                go.Scatter(

                    x=overall_share_df[
                        "time_slot"
                    ],

                    y=overall_share_df[
                        "share"
                    ],

                    mode="lines+markers",

                    name="전체 연령",

                    line=dict(
                        color="#8EA2B8",
                        width=3,
                    ),

                    marker=dict(
                        size=7,
                        color="#8EA2B8",
                    ),

                    hovertemplate=(
                        "<b>%{x}</b>"
                        "<br>"
                        "전체 연령 비중: %{y:.1f}%"
                        "<extra></extra>"
                    ),
                )
            )


            fig_compare.add_trace(
                go.Scatter(

                    x=selected_share_df[
                        "time_slot"
                    ],

                    y=selected_share_df[
                        "share"
                    ],

                    mode="lines+markers",

                    name=selected_age,

                    line=dict(
                        color="#D9A64A",
                        width=4,
                    ),

                    marker=dict(
                        size=8,
                        color="#D9A64A",
                    ),

                    hovertemplate=(
                        "<b>%{x}</b>"
                        "<br>"
                        f"{selected_age} 비중: "
                        "%{y:.1f}%"
                        "<extra></extra>"
                    ),
                )
            )


            fig_compare.update_layout(

                height=520,

                margin=dict(
                    l=70,
                    r=40,
                    t=50,
                    b=85,
                ),

                paper_bgcolor="#182035",

                plot_bgcolor="#182035",

                font=dict(
                    color="#E8EDF5",
                    size=12,
                ),

                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    bgcolor="rgba(0,0,0,0)",
                ),

                xaxis=dict(
                    title="시간대",
                    showgrid=False,
                    tickangle=-35,
                    tickfont=dict(
                        color="#D7DEE9",
                    ),
                ),

                yaxis=dict(
                    title="사고 비중(%)",
                    showgrid=True,
                    gridcolor="#35405A",
                    zeroline=False,
                    ticksuffix="%",
                    tickfont=dict(
                        color="#D7DEE9",
                    ),
                ),
            )


            st.plotly_chart(
                fig_compare,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
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
                연령대 × 시간대 사고 집중도
            </div>

            <div class="panel-sub">
                색상이 밝을수록 해당 연령대와 시간대에서
                교통사고가 많이 발생한 구간입니다.
            </div>
            """
        )


        heatmap_df = (
            long_df
            .pivot_table(
                index="age_group",
                columns="time_slot",
                values="accidents",
                aggfunc="sum",
                fill_value=0,
            )
        )


        ordered_age = sorted(
            heatmap_df.index.tolist(),
            key=age_sort_key
        )


        heatmap_df = (
            heatmap_df
            .reindex(
                index=ordered_age,
                columns=TIME_ORDER
            )
            .fillna(0)
        )


        fig_heatmap = go.Figure(
            data=go.Heatmap(

                z=heatmap_df.values,

                x=heatmap_df.columns,

                y=heatmap_df.index,

                colorscale=[
                    [0.00, "#1E293C"],
                    [0.25, "#385765"],
                    [0.50, "#668D7D"],
                    [0.75, "#B79A58"],
                    [1.00, "#E0A945"],
                ],

                colorbar=dict(

                    title=dict(
                        text="사고건수",
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
                ),
            )
        )


        fig_heatmap.update_layout(

            height=620,

            margin=dict(
                l=90,
                r=90,
                t=35,
                b=80,
            ),

            paper_bgcolor="#182035",

            plot_bgcolor="#182035",

            font=dict(
                color="#E8EDF5",
                size=12,
            ),

            xaxis=dict(

                title="시간대",

                tickangle=-30,

                tickfont=dict(
                    color="#D7DEE9",
                ),
            ),

            yaxis=dict(

                title="연령대",

                tickfont=dict(
                    color="#D7DEE9",
                ),
            ),
        )


        st.plotly_chart(
            fig_heatmap,

            use_container_width=True,

            config={
                "displayModeBar": False
            }
        )


    # ========================================================
    # AUTOMATED INSIGHTS
    # ========================================================

    selected_share_lookup = (
        selected_share_df
        .set_index(
            "time_slot"
        )[
            "share"
        ]
        .to_dict()
    )


    overall_share_lookup = (
        overall_share_df
        .set_index(
            "time_slot"
        )[
            "share"
        ]
        .to_dict()
    )


    share_gap_df = (
        selected_share_df[
            [
                "time_slot",
                "share",
            ]
        ]
        .rename(
            columns={
                "share":
                    "selected_share"
            }
        )
        .merge(
            overall_share_df[
                [
                    "time_slot",
                    "share",
                ]
            ].rename(
                columns={
                    "share":
                        "overall_share"
                }
            ),
            on="time_slot",
            how="left"
        )
    )


    share_gap_df[
        "gap"
    ] = (
        share_gap_df[
            "selected_share"
        ]
        - share_gap_df[
            "overall_share"
        ]
    )


    if not share_gap_df.empty:

        highest_gap_row = (
            share_gap_df
            .sort_values(
                "gap",
                ascending=False
            )
            .iloc[0]
        )

        highest_gap_time = str(
            highest_gap_row[
                "time_slot"
            ]
        )

        highest_gap = float(
            highest_gap_row[
                "gap"
            ]
        )

    else:

        highest_gap_time = "-"
        highest_gap = 0


    with st.container(
        key="insight_panel"
    ):

        st.html(
            f"""
            <div class="panel-title">
                주요 분석 결과
            </div>

            <div class="panel-sub">
                선택한 연령대의 시간대별 사고 패턴을
                자동으로 요약한 결과입니다.
            </div>


            <div class="insight-grid">

                <div class="insight-card">

                    <div class="insight-index">
                        01
                    </div>

                    <div class="insight-title">
                        사고 집중 시간
                    </div>

                    <div class="insight-body">
                        {selected_age} 사고는
                        <b>{peak_time}</b>에 가장 많이 발생했으며,
                        사고건수는
                        <b>{peak_accidents:,}건</b>입니다.
                    </div>

                </div>


                <div class="insight-card">

                    <div class="insight-index">
                        02
                    </div>

                    <div class="insight-title">
                        야간 사고
                    </div>

                    <div class="insight-body">
                        00~06시 및 20~24시 사고는
                        전체 {selected_age} 사고의
                        <b>{night_ratio:.1f}%</b>입니다.
                    </div>

                </div>


                <div class="insight-card">

                    <div class="insight-index">
                        03
                    </div>

                    <div class="insight-title">
                        전체 연령과의 차이
                    </div>

                    <div class="insight-body">
                        전체 연령 대비 {selected_age} 사고 비중이
                        가장 크게 높은 시간대는
                        <b>{highest_gap_time}</b>이며,
                        차이는
                        <b>{highest_gap:+.1f}%p</b>입니다.
                    </div>

                </div>

            </div>
            """
        )


    # ========================================================
    # SUMMARY
    # ========================================================

    st.html(
        f"""
        <div class="info-box">

            <b>{selected_age} 시간대별 사고 분석 요약</b>

            <br><br>

            {selected_age}의 전체 시간대 사고 건수는
            <b>{total_selected:,}건</b>입니다.

            <br>

            가장 많은 사고가 발생한 시간대는
            <b>{peak_time}</b>로,
            <b>{peak_accidents:,}건</b>이 발생했습니다.

            <br>

            00~06시 및 20~24시를 야간 시간대로 구분했을 때
            {selected_age}의 야간 사고 비중은
            약 <b>{night_ratio:.1f}%</b>입니다.

            <br>

            전체 연령대 기준으로 사고 건수가 가장 많은 연령대는
            <b>{overall_top_age}</b>입니다.

            <br><br>

            ※ 본 분석은 가해운전자 연령대와 2시간 단위 사고 발생 건수를
            기준으로 한 분포 분석입니다.

        </div>
        """
    )


    # ========================================================
    # DETAIL TABLE
    # ========================================================

    st.write("")


    if "show_driver_time_detail" not in st.session_state:

        st.session_state[
            "show_driver_time_detail"
        ] = False


    with st.container(
        key="driver_time_detail_toggle"
    ):

        detail_open = st.session_state[
            "show_driver_time_detail"
        ]


        detail_button_label = (
            "▲ 연령별 교통사고 데이터 닫기"
            if detail_open
            else "▼ 연령별 교통사고 데이터 상세 보기"
        )


        if st.button(
            detail_button_label,
            key="driver_time_detail_button",
            use_container_width=True
        ):

            st.session_state[
                "show_driver_time_detail"
            ] = (
                not detail_open
            )

            st.rerun()


    if st.session_state[
        "show_driver_time_detail"
    ]:

        with st.container(
            key="driver_time_detail_panel"
        ):

            detail_df = (
                long_df[
                    [
                        "age_group",
                        "time_slot",
                        "accidents",
                    ]
                ]
                .copy()
            )


            detail_df[
                "age_order"
            ] = (
                detail_df[
                    "age_group"
                ]
                .apply(
                    age_sort_key
                )
            )


            detail_df[
                "time_order"
            ] = (
                detail_df[
                    "time_slot"
                ]
                .apply(
                    lambda value:
                        TIME_ORDER.index(
                            value
                        )
                        if value in TIME_ORDER
                        else 999
                )
            )


            detail_df = (
                detail_df
                .sort_values(
                    [
                        "age_order",
                        "time_order",
                    ]
                )
                .drop(
                    columns=[
                        "age_order",
                        "time_order",
                    ]
                )
                .reset_index(
                    drop=True
                )
            )


            detail_df.columns = [
                "연령대",
                "시간대",
                "사고건수",
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


            display_df = (
                detail_df
                .copy()
            )


            display_df[
                "사고건수"
            ] = (
                display_df[
                    "사고건수"
                ]
                .map(
                    lambda value:
                        f"{int(value):,}건"
                )
            )


            table_rows = ""


            for _, row in display_df.iterrows():

                senior_class = (
                    "senior-row"
                    if age_sort_key(
                        row["연령대"]
                    ) >= 65
                    else ""
                )


                table_rows += f"""
                    <tr class="{senior_class}">
                        <td>{row["연령대"]}</td>
                        <td>{row["시간대"]}</td>
                        <td>{row["사고건수"]}</td>
                    </tr>
                """


            st.html(
                f"""
                <style>

                .driver-time-dark-table-wrap {{

                    width: 100%;

                    max-height: 520px;

                    overflow-y: auto;

                    overflow-x: auto;

                    background: #182035;

                    border: 1px solid #3A4662;

                    border-radius: 12px;
                }}


                .driver-time-dark-table {{

                    width: 100%;

                    border-collapse: collapse;

                    background: #182035;

                    color: #E7EAF0;

                    font-size: 13px;
                }}


                .driver-time-dark-table thead {{

                    position: sticky;

                    top: 0;

                    z-index: 2;
                }}


                .driver-time-dark-table th {{

                    background: #202A42;

                    color: #D6A348;

                    font-weight: 900;

                    text-align: center;

                    padding: 14px 16px;

                    border-bottom: 1px solid #4A5670;
                }}


                .driver-time-dark-table td {{

                    background: #182035;

                    color: #E7EAF0;

                    font-weight: 600;

                    text-align: center;

                    padding: 12px 16px;

                    border-bottom: 1px solid #303B55;
                }}


                .driver-time-dark-table tbody tr:nth-child(even) td {{

                    background: #1B243A;
                }}


                .driver-time-dark-table tbody tr.senior-row td {{

                    color: #F1C66A;
                }}


                .driver-time-dark-table tbody tr:hover td {{

                    background: #222D47;

                    color: #FFFFFF;
                }}

                </style>


                <div class="driver-time-dark-table-wrap">

                    <table class="driver-time-dark-table">

                        <thead>
                            <tr>
                                <th>연령대</th>
                                <th>시간대</th>
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