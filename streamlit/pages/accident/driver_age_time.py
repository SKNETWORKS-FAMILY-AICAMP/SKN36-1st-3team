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
.st-key-age_compare_panel {

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
   EXPANDER
========================================================== */

[data-testid="stExpander"] {

    background: #182035 !important;

    border: 1px solid #46536F !important;

    border-radius: 14px !important;

    overflow: hidden !important;

    margin-top: 10px !important;
}


/* expander summary 전체 */
[data-testid="stExpander"] details summary {

    background: #182035 !important;

    color: #FFFFFF !important;

    padding: 14px 18px !important;

    cursor: pointer !important;
}


/* expander 제목 */
[data-testid="stExpander"] details summary p {

    color: #FFFFFF !important;

    font-size: 14px !important;

    font-weight: 700 !important;

    opacity: 1 !important;
}


/* Streamlit 버전별 span 대응 */
[data-testid="stExpander"] details summary span {

    color: #FFFFFF !important;

    font-size: 14px !important;

    font-weight: 700 !important;

    opacity: 1 !important;
}


/* expander 내부 모든 텍스트 */
[data-testid="stExpander"] summary * {

    color: #FFFFFF !important;

    opacity: 1 !important;
}


/* 화살표 */
[data-testid="stExpander"] summary svg {

    color: #D6A348 !important;

    fill: #D6A348 !important;

    opacity: 1 !important;
}


/* hover */
[data-testid="stExpander"] details summary:hover {

    background: #202A42 !important;
}


/* 펼친 내부 */
[data-testid="stExpanderDetails"] {

    background: #182035 !important;

    color: #FFFFFF !important;

    padding: 10px 16px 18px 16px !important;
}


/* ==========================================================
   DATAFRAME
========================================================== */

[data-testid="stDataFrame"] {

    border: 1px solid #3C4863;

    border-radius: 10px;

    overflow: hidden;
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

        selected_age = st.selectbox(
            "연령대",
            age_groups,
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
                    전체 사고 최다 연령대
                </div>

                <div class="kpi-value">
                    {overall_top_age}
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
    # ALL AGE TIME CHART
    # ========================================================

    with right:

        with st.container(
            key="total_time_panel"
        ):

            st.html(
                """
                <div class="panel-title">
                    전체 연령 시간대별 사고 규모
                </div>

                <div class="panel-sub">
                    모든 연령대의 사고를 합산하여 시간대별 사고 집중 구간을 확인합니다.
                </div>
                """
            )


            overall_peak = (
                total_time_df
                .sort_values(
                    "accidents",
                    ascending=False
                )
                .iloc[0]["time_slot"]
            )


            fig_total = go.Figure(
                go.Scatter(

                    x=total_time_df["time_slot"],

                    y=total_time_df["accidents"],

                    mode="lines+markers+text",

                    line=dict(
                        color="#91C7AA",
                        width=4,
                    ),

                    marker=dict(
                        size=9,

                        color=[
                            "#D9A64A"
                            if time == overall_peak
                            else "#91C7AA"

                            for time
                            in total_time_df["time_slot"]
                        ],
                    ),

                    text=[
                        f"{int(value):,}"
                        for value
                        in total_time_df["accidents"]
                    ],

                    textposition="top center",

                    textfont=dict(
                        color="#FFFFFF",
                        size=9,
                    ),

                    hovertemplate=(
                        "<b>%{x}</b>"
                        "<br>"
                        "사고: %{y:,}건"
                        "<extra></extra>"
                    ),
                )
            )


            fig_total.update_layout(

                height=520,

                margin=dict(
                    l=70,
                    r=40,
                    t=50,
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

                    tickfont=dict(
                        color="#D7DEE9",
                    ),
                ),
            )


            st.plotly_chart(
                fig_total,

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
    # AGE COMPARISON
    # ========================================================

    with st.container(
        key="age_compare_panel"
    ):

        st.html(
            """
            <div class="panel-title">
                시간대별 연령대 사고 비교
            </div>

            <div class="panel-sub">
                시간대마다 어떤 연령대의 사고 규모가 높은지 비교합니다.
                확인할 시간대를 선택하세요.
            </div>
            """
        )


        c1, empty = st.columns(
            [
                1,
                4,
            ]
        )


        with c1:

            selected_time = st.selectbox(
                "시간대",
                TIME_ORDER,
                key="driver_selected_time"
            )


        time_age_df = (
            long_df[
                long_df["time_slot"] == selected_time
            ]
            .copy()
        )


        time_age_df["age_order"] = (
            time_age_df["age_group"]
            .apply(age_sort_key)
        )


        time_age_df = (
            time_age_df
            .sort_values(
                "age_order",
                ascending=True
            )
        )


        max_time_age = (
            time_age_df["accidents"].max()
            if not time_age_df.empty
            else 1
        )


        if max_time_age <= 0:
            max_time_age = 1


        top_time_age = (
            time_age_df
            .sort_values(
                "accidents",
                ascending=False
            )
            .iloc[0]["age_group"]

            if not time_age_df.empty

            else "-"
        )


        fig_age_compare = go.Figure(
            go.Bar(

                x=time_age_df["accidents"],

                y=time_age_df["age_group"],

                orientation="h",

                marker_color=[
                    "#D9A64A"
                    if age == top_time_age
                    else "#79B69B"

                    for age
                    in time_age_df["age_group"]
                ],

                text=[
                    f"{int(value):,}건"
                    for value
                    in time_age_df["accidents"]
                ],

                textposition="outside",

                textfont=dict(
                    color="#FFFFFF",
                    size=11,
                ),

                cliponaxis=False,

                hovertemplate=(
                    "<b>%{y}</b>"
                    "<br>"
                    "사고: %{x:,}건"
                    "<extra></extra>"
                ),
            )
        )


        fig_age_compare.update_layout(

            height=520,

            margin=dict(
                l=90,
                r=110,
                t=40,
                b=65,
            ),

            paper_bgcolor="#182035",

            plot_bgcolor="#182035",

            showlegend=False,

            font=dict(
                color="#E8EDF5",
                size=12,
            ),

            xaxis=dict(

                title="교통사고 건수(건)",

                showgrid=True,

                gridcolor="#35405A",

                zeroline=False,

                tickformat=",",

                range=[
                    0,
                    max_time_age * 1.20
                ],
            ),

            yaxis=dict(

                title=None,

                showgrid=False,
            ),
        )


        st.plotly_chart(
            fig_age_compare,

            use_container_width=True,

            config={
                "displayModeBar": False
            }
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


    with st.expander(
        "가해운전자 시간대별 사고 데이터 상세 보기"
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


        detail_df["age_order"] = (
            detail_df["age_group"]
            .apply(age_sort_key)
        )


        detail_df["time_order"] = (
            detail_df["time_slot"]
            .apply(
                lambda x:
                TIME_ORDER.index(x)
                if x in TIME_ORDER
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
            .reset_index(drop=True)
        )


        detail_df.columns = [
            "연령대",
            "시간대",
            "사고건수",
        ]


        detail_df["사고건수"] = (
            detail_df["사고건수"]
            .round()
            .astype(int)
        )


        st.dataframe(

            detail_df,

            use_container_width=True,

            hide_index=True,

            height=420,

            column_config={

                "연령대":
                    st.column_config.TextColumn(
                        "연령대",
                        width="medium"
                    ),

                "시간대":
                    st.column_config.TextColumn(
                        "시간대",
                        width="medium"
                    ),

                "사고건수":
                    st.column_config.NumberColumn(
                        "사고건수",
                        format="%d건"
                    ),
            }
        )