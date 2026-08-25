import sys
import re
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sqlalchemy import text


# ============================================================
# PROJECT ROOT
# SAFE/streamlit/pages/people/resident_population_monthly.py
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
def load_population_data():

    engine = get_engine()

    query = text(
        """
        SELECT
            id,
            region,
            year,
            gender,
            age_group,
            population
        FROM age_population
        ORDER BY
            year,
            region,
            gender,
            age_group
        """
    )

    with engine.connect() as conn:
        return pd.read_sql(query, conn)


# ============================================================
# LOAD DATA
# ============================================================

try:

    df = load_population_data()

except Exception as e:

    st.error(
        f"MySQL 연령별 인구 데이터 조회 실패\n\n{e}"
    )

    st.stop()


# ============================================================
# EMPTY CHECK
# ============================================================

if df.empty:

    st.warning(
        "조회된 연령별 인구 데이터가 없습니다."
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


df["gender"] = (
    df["gender"]
    .fillna("")
    .astype(str)
    .str.strip()
)


df["age_group"] = (
    df["age_group"]
    .fillna("")
    .astype(str)
    .str.strip()
)


df["year"] = pd.to_numeric(
    df["year"],
    errors="coerce"
)


df["population"] = pd.to_numeric(
    df["population"],
    errors="coerce"
).fillna(0)


df = (
    df
    .dropna(
        subset=["year"]
    )
    .copy()
)


df["year"] = (
    df["year"]
    .astype(int)
)


df["population"] = (
    df["population"]
    .astype(int)
)


# ============================================================
# REGION CLEAN
# ============================================================

def clean_region_text(region):

    region = str(region).strip()

    # 행정구역 코드 제거
    # ex) 서울특별시 (1100000000)
    region = re.sub(
        r"\(\s*\d+\s*\)",
        "",
        region
    )

    # 남아있는 숫자 제거
    region = re.sub(
        r"\d+",
        "",
        region
    )

    # 공백 제거
    region = re.sub(
        r"\s+",
        "",
        region
    )

    region = region.strip(
        "-_/.,()[]{}"
    )

    return region


# ============================================================
# REGION NORMALIZATION
# ============================================================

def normalize_region(region):

    region = clean_region_text(region)

    # --------------------------------------------------------
    # 서울
    # --------------------------------------------------------

    if region in [
        "서울",
        "서울특별시",
    ]:
        return "서울특별시"


    # --------------------------------------------------------
    # 부산
    # --------------------------------------------------------

    if region in [
        "부산",
        "부산광역시",
    ]:
        return "부산광역시"


    # --------------------------------------------------------
    # 대구
    # --------------------------------------------------------

    if region in [
        "대구",
        "대구광역시",
    ]:
        return "대구광역시"


    # --------------------------------------------------------
    # 인천
    # --------------------------------------------------------

    if region in [
        "인천",
        "인천광역시",
    ]:
        return "인천광역시"


    # --------------------------------------------------------
    # 광주
    # --------------------------------------------------------

    if region in [
        "광주",
        "광주광역시",
    ]:
        return "광주광역시"


    # --------------------------------------------------------
    # 대전
    # --------------------------------------------------------

    if region in [
        "대전",
        "대전광역시",
    ]:
        return "대전광역시"


    # --------------------------------------------------------
    # 울산
    # --------------------------------------------------------

    if region in [
        "울산",
        "울산광역시",
    ]:
        return "울산광역시"


    # --------------------------------------------------------
    # 세종
    # --------------------------------------------------------

    if region in [
        "세종",
        "세종특별자치시",
    ]:
        return "세종특별자치시"


    # --------------------------------------------------------
    # 경기
    # --------------------------------------------------------

    if region in [
        "경기",
        "경기도",
    ]:
        return "경기도"


    # --------------------------------------------------------
    # 강원
    # --------------------------------------------------------

    if region in [
        "강원",
        "강원도",
        "강원특별자치도",
    ]:
        return "강원특별자치도"


    # --------------------------------------------------------
    # 충북
    # --------------------------------------------------------

    if region in [
        "충북",
        "충청북도",
    ]:
        return "충청북도"


    # --------------------------------------------------------
    # 충남
    # --------------------------------------------------------

    if region in [
        "충남",
        "충청남도",
    ]:
        return "충청남도"


    # --------------------------------------------------------
    # 전북
    # --------------------------------------------------------

    if region in [
        "전북",
        "전라북도",
        "전북특별자치도",
    ]:
        return "전북특별자치도"


    # --------------------------------------------------------
    # 전남
    #
    # 데이터에 이상한 지역명이 들어가더라도
    # 내부적으로 전라남도로 통일
    # --------------------------------------------------------

    if region in [
        "전남",
        "전라남도",
        "전남특별시",
        "전남특별자치도",
        "전남광주통합특별시",
        "전남광주통합특별자치도",
        "광주전남통합특별시",
        "광주전남통합특별자치도",
    ]:
        return "전라남도"


    # 전남으로 시작하면서
    # 통합/특별 명칭이 붙어있는 경우도 처리
    if (
        region.startswith("전남")
        and (
            "특별" in region
            or "통합" in region
        )
    ):
        return "전라남도"


    # 광주전남 통합 명칭
    if (
        "광주" in region
        and "전남" in region
        and "통합" in region
    ):
        return "전라남도"


    # --------------------------------------------------------
    # 경북
    # --------------------------------------------------------

    if region in [
        "경북",
        "경상북도",
    ]:
        return "경상북도"


    # --------------------------------------------------------
    # 경남
    # --------------------------------------------------------

    if region in [
        "경남",
        "경상남도",
    ]:
        return "경상남도"


    # --------------------------------------------------------
    # 제주
    # --------------------------------------------------------

    if region in [
        "제주",
        "제주도",
        "제주특별자치도",
    ]:
        return "제주특별자치도"


    return region


# ============================================================
# APPLY REGION NORMALIZATION
# ============================================================

df["region"] = (
    df["region"]
    .apply(normalize_region)
)


# ============================================================
# EMPTY REGION REMOVE
# ============================================================

df = (
    df[
        df["region"].str.strip() != ""
    ]
    .copy()
)


# ============================================================
# SAME REGION MERGE
#
# 전남 관련 명칭이 여러 개 있었다면
# 정규화 후 동일 지역으로 다시 합산
# ============================================================

df = (
    df
    .groupby(
        [
            "year",
            "region",
            "gender",
            "age_group",
        ],
        as_index=False
    )["population"]
    .sum()
)


# ============================================================
# DISPLAY REGION
# ============================================================

DISPLAY_REGION_MAP = {

    "서울특별시": "서울",
    "부산광역시": "부산",
    "대구광역시": "대구",
    "인천광역시": "인천",
    "광주광역시": "광주",

    "대전광역시": "대전",
    "울산광역시": "울산",
    "세종특별자치시": "세종",

    "경기도": "경기",

    "강원특별자치도": "강원",

    "충청북도": "충북",
    "충청남도": "충남",

    "전북특별자치도": "전북",

    # 중요
    "전라남도": "전남",
    "전남특별시": "전남",
    "전남특별자치도": "전남",
    "전남광주통합특별시": "전남",
    "전남광주통합특별자치도": "전남",
    "광주전남통합특별시": "전남",

    "경상북도": "경북",
    "경상남도": "경남",

    "제주특별자치도": "제주",
}


def display_region(region):

    region = str(region).strip()

    # 혹시 정규화를 뚫고 이상한 전남 이름이 들어와도
    # 화면에서는 무조건 전남
    if (
        region.startswith("전남")
        or (
            "전남" in region
            and "광주" in region
        )
    ):
        return "전남"

    return DISPLAY_REGION_MAP.get(
        region,
        region
    )


# ============================================================
# AGE SORT
# ============================================================

def age_sort_key(age_group):

    age_group = str(age_group)

    numbers = re.findall(
        r"\d+",
        age_group
    )

    if numbers:

        return int(
            numbers[0]
        )

    return 999


# ============================================================
# KOREAN NUMBER
# ============================================================

def korean_number(value):

    if pd.isna(value):

        return "-"

    value = int(
        round(value)
    )

    eok = (
        value
        // 100_000_000
    )

    remain = (
        value
        % 100_000_000
    )

    man = (
        remain
        // 10_000
    )

    remain = (
        remain
        % 10_000
    )

    cheon = (
        remain
        // 1_000
    )

    result = []

    if eok > 0:

        result.append(
            f"{eok}억"
        )


    if man > 0:

        result.append(
            f"{man:,}만"
        )


    if (
        eok == 0
        and man == 0
        and cheon > 0
    ):

        result.append(
            f"{cheon}천"
        )


    if not result:

        return f"{value:,}"


    return " ".join(
        result
    )


# ============================================================
# SENIOR AGE GROUP
# ============================================================

SENIOR_GROUPS = [

    "60~69세",
    "70~79세",
    "80~89세",
    "90~99세",
    "100세 이상",
]


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


.st-key-nav_people button {

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

.st-key-resident_page {

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

    line-height: 1.75;

    margin-bottom: 25px;
}


/* ==========================================================
   SELECT
========================================================== */

label[data-testid="stWidgetLabel"] p {

    color: #FFFFFF !important;

    font-size: 15px !important;

    font-weight: 800 !important;
}


div[data-baseweb="select"] > div {

    background: #F5F6F8 !important;

    color: #1C2435 !important;

    min-height: 48px !important;

    border-radius: 8px !important;
}


div[data-baseweb="select"] span {

    color: #273149 !important;

    font-size: 15px !important;
}


/* ==========================================================
   KPI
========================================================== */

.kpi {

    min-height: 118px;

    background: #192136;

    border: 1px solid #394560;

    border-radius: 17px;

    padding: 20px 22px;
}


.kpi-label {

    color: #C4CCD9;

    font-size: 14px;

    margin-bottom: 15px;
}


.kpi-value {

    color: #FFFFFF;

    font-size: 27px;

    font-weight: 900;
}


/* ==========================================================
   CHART PANEL
========================================================== */

.st-key-region_panel,
.st-key-share_panel,
.st-key-trend_panel {

    background: #182035;

    border: 1px solid #3A4662;

    border-radius: 28px;

    padding: 24px 26px;

    margin-top: 24px;
}


.panel-title {

    color: #FFFFFF;

    font-size: 23px;

    font-weight: 900;

    margin-bottom: 8px;
}


.panel-sub {

    color: #C8D0DC;

    font-size: 15px;

    line-height: 1.75;

    margin-bottom: 12px;
}


/* ==========================================================
   ANALYSIS
========================================================== */

.analysis-box {

    background: #121A2B;

    border: 1px solid #35415C;

    border-left: 4px solid #D6A348;

    border-radius: 7px 15px 15px 7px;

    padding: 22px 24px;

    margin-top: 20px;

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
    key="resident_page"
):

    # ========================================================
    # HEADER
    # ========================================================

    st.html(
        """
        <div class="page-path">
            인구 &gt; 연령별 인구 현황
        </div>

        <div class="page-title">
            지역별 연령 인구 현황
        </div>

        <div class="page-sub">
            지역과 성별을 선택하여 연령대별 인구 구조를 비교하고,
            지역별 60세 이상 인구 비율을 확인합니다.
            데이터는 7월 기준입니다.
        </div>
        """
    )


    # ========================================================
    # FILTER OPTIONS
    # ========================================================

    years = sorted(
        df["year"]
        .dropna()
        .unique()
        .tolist(),
        reverse=True
    )


    if not years:

        st.warning(
            "조회 가능한 연도 데이터가 없습니다."
        )

        st.stop()


    regions = sorted(
        df["region"]
        .dropna()
        .unique()
        .tolist(),
        key=lambda x: display_region(x)
    )


    available_genders = (
        df["gender"]
        .dropna()
        .unique()
        .tolist()
    )


    genders = [
        gender
        for gender in [
            "계",
            "남",
            "여",
        ]
        if gender in available_genders
    ]


    if not genders:

        st.warning(
            "조회 가능한 성별 데이터가 없습니다."
        )

        st.stop()


    # ========================================================
    # FILTER
    # ========================================================

    f1, f2, f3, empty = st.columns(
        [
            1,
            1.3,
            1,
            2.5
        ]
    )


    with f1:

        selected_year = st.selectbox(
            "연도 선택",
            years,
            key="resident_year"
        )


    with f2:

        selected_region = st.selectbox(
            "지역 선택",
            ["전국"] + regions,
            format_func=lambda x: (
                x
                if x == "전국"
                else display_region(x)
            ),
            key="resident_region"
        )


    with f3:

        selected_gender = st.selectbox(
            "성별 선택",
            genders,
            key="resident_gender"
        )


    # ========================================================
    # BASE DATA
    # ========================================================

    base_df = (
        df[
            (df["year"] == selected_year)
            &
            (df["gender"] == selected_gender)
        ]
        .copy()
    )


    if base_df.empty:

        st.warning(
            "선택한 조건에 해당하는 데이터가 없습니다."
        )

        st.stop()


    # ========================================================
    # SELECTED REGION DATA
    # ========================================================

    if selected_region == "전국":

        selected_df = (
            base_df
            .groupby(
                "age_group",
                as_index=False
            )["population"]
            .sum()
        )

        current_region_label = "전국"

    else:

        selected_df = (
            base_df[
                base_df["region"]
                == selected_region
            ]
            .groupby(
                "age_group",
                as_index=False
            )["population"]
            .sum()
        )

        current_region_label = (
            display_region(
                selected_region
            )
        )


    # ========================================================
    # AGE SORT
    # ========================================================

    selected_df["age_order"] = (
        selected_df["age_group"]
        .apply(age_sort_key)
    )


    selected_df = (
        selected_df
        .sort_values(
            "age_order"
        )
        .drop(
            columns=["age_order"]
        )
        .reset_index(drop=True)
    )


    # ========================================================
    # TOTAL POPULATION
    # ========================================================

    total_population = int(
        selected_df[
            "population"
        ].sum()
    )


    # ========================================================
    # 60+ POPULATION
    # ========================================================

    senior_population = int(
        selected_df.loc[
            selected_df[
                "age_group"
            ].isin(
                SENIOR_GROUPS
            ),
            "population"
        ].sum()
    )


    senior_share = (
        senior_population
        / total_population
        * 100

        if total_population > 0

        else 0
    )


    # ========================================================
    # MAX AGE GROUP
    # ========================================================

    if not selected_df.empty:

        max_age_row = (
            selected_df
            .sort_values(
                "population",
                ascending=False
            )
            .iloc[0]
        )

        max_age_group = (
            max_age_row[
                "age_group"
            ]
        )

        max_age_population = int(
            max_age_row[
                "population"
            ]
        )

    else:

        max_age_group = "-"
        max_age_population = 0


    # ========================================================
    # KPI
    # ========================================================

    k1, k2, k3, k4 = st.columns(4)


    with k1:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    선택 지역
                </div>

                <div class="kpi-value">
                    {current_region_label}
                </div>

            </div>
            """
        )


    with k2:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    전체 인구
                </div>

                <div class="kpi-value">
                    {korean_number(total_population)}
                </div>

            </div>
            """
        )


    with k3:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    60세 이상 인구
                </div>

                <div class="kpi-value">
                    {korean_number(senior_population)}
                </div>

            </div>
            """
        )


    with k4:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    60세 이상 인구 비율
                </div>

                <div class="kpi-value">
                    {senior_share:.1f}%
                </div>

            </div>
            """
        )


    # ========================================================
    # CHART AREA
    # ========================================================

    chart_left, chart_right = st.columns(
        [
            1.15,
            1
        ],
        gap="medium"
    )


    # ========================================================
    # LEFT : AGE POPULATION
    # ========================================================

    with chart_left:

        with st.container(
            key="region_panel"
        ):

            st.html(
                f"""
                <div class="panel-title">
                    {current_region_label} 연령대별 인구
                </div>

                <div class="panel-sub">
                    {selected_year}년 7월 기준
                    {selected_gender} 인구의 연령대별 규모를 비교합니다.
                </div>
                """
            )


            plot_df = (
                selected_df
                .copy()
            )


            if plot_df.empty:

                st.info(
                    "연령대별 데이터가 없습니다."
                )

            else:

                plot_max = max(
                    float(
                        plot_df[
                            "population"
                        ].max()
                    ),
                    1
                )


                fig_age = go.Figure(
                    go.Bar(

                        x=plot_df[
                            "age_group"
                        ],

                        y=plot_df[
                            "population"
                        ],

                        marker_color=[
                            "#D9A64A"
                            if age in SENIOR_GROUPS
                            else "#79B69B"

                            for age
                            in plot_df[
                                "age_group"
                            ]
                        ],

                        text=[
                            korean_number(
                                value
                            )
                            for value
                            in plot_df[
                                "population"
                            ]
                        ],

                        textfont=dict(
                            size=12,
                            color="#FFFFFF"
                        ),

                        textposition="outside",

                        cliponaxis=False,

                        hovertemplate=(
                            "<b>%{x}</b>"
                            "<br>"
                            "인구: %{y:,.0f}명"
                            "<extra></extra>"
                        )
                    )
                )


                fig_age.update_layout(

                    height=610,

                    margin=dict(
                        l=80,
                        r=45,
                        t=45,
                        b=90
                    ),

                    paper_bgcolor="#182035",

                    plot_bgcolor="#182035",

                    font=dict(
                        color="#E8EDF5",
                        size=14
                    ),

                    showlegend=False,

                    xaxis=dict(
                        title="연령대",
                        showgrid=False
                    ),

                    yaxis=dict(

                        title="인구(명)",

                        tickformat=",",

                        gridcolor="#35405A",

                        range=[
                            0,
                            plot_max * 1.2
                        ]
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
    # RIGHT : AGE SHARE
    # ========================================================

    with chart_right:

        with st.container(
            key="share_panel"
        ):

            st.html(
                f"""
                <div class="panel-title">
                    연령대별 인구 비중
                </div>

                <div class="panel-sub">
                    {current_region_label} 전체 인구에서
                    각 연령대가 차지하는 비율을 확인합니다.
                </div>
                """
            )


            share_df = (
                selected_df
                .copy()
            )


            pie_colors = [
                "#D9B45C",
                "#91B99F",
                "#91A8CE",
                "#9B83C1",
                "#BC8265",
                "#D9C165",
                "#8EB2BA",
                "#B18E89",
                "#A3B47A",
                "#839BB5",
                "#9582AB",
            ]


            if share_df.empty:

                st.info(
                    "연령대 비중 데이터가 없습니다."
                )

            else:

                fig_share = go.Figure(
                    go.Pie(

                        labels=share_df[
                            "age_group"
                        ],

                        values=share_df[
                            "population"
                        ],

                        hole=.55,

                        sort=False,

                        textinfo="label+percent",

                        textposition="outside",

                        textfont=dict(
                            color="#FFFFFF",
                            size=12
                        ),

                        marker=dict(

                            colors=pie_colors,

                            line=dict(
                                color="#182035",
                                width=2
                            )
                        ),

                        hovertemplate=(
                            "<b>%{label}</b>"
                            "<br>"
                            "인구: %{value:,.0f}명"
                            "<br>"
                            "비율: %{percent}"
                            "<extra></extra>"
                        )
                    )
                )


                fig_share.add_annotation(

                    x=.5,
                    y=.5,

                    showarrow=False,

                    text=(
                        "<b>전체 인구</b>"
                        "<br>"
                        f"{korean_number(total_population)}"
                    ),

                    font=dict(
                        color="#FFFFFF",
                        size=18
                    )
                )


                fig_share.update_layout(

                    height=610,

                    margin=dict(
                        l=80,
                        r=80,
                        t=45,
                        b=45
                    ),

                    paper_bgcolor="#182035",

                    plot_bgcolor="#182035",

                    showlegend=False,

                    font=dict(
                        color="#FFFFFF",
                        size=14
                    )
                )


                st.plotly_chart(
                    fig_share,
                    use_container_width=True,
                    config={
                        "displayModeBar": False
                    }
                )


    # ========================================================
    # REGION SENIOR COMPARISON
    # ========================================================

    with st.container(
        key="trend_panel"
    ):

        st.html(
            f"""
            <div class="panel-title">
                지역별 60세 이상 인구 비율
            </div>

            <div class="panel-sub">
                {selected_year}년 7월 기준
                각 지역 전체 인구에서 60세 이상 인구가
                차지하는 비율을 비교합니다.
            </div>
            """
        )


        compare_source = (
            df[
                (df["year"] == selected_year)
                &
                (df["gender"] == selected_gender)
            ]
            .copy()
        )


        # 지역별 전체 인구
        total_region_df = (
            compare_source
            .groupby(
                "region",
                as_index=False
            )["population"]
            .sum()
            .rename(
                columns={
                    "population":
                        "total_population"
                }
            )
        )


        # 지역별 60세 이상 인구
        senior_region_df = (
            compare_source[
                compare_source[
                    "age_group"
                ].isin(
                    SENIOR_GROUPS
                )
            ]
            .groupby(
                "region",
                as_index=False
            )["population"]
            .sum()
            .rename(
                columns={
                    "population":
                        "senior_population"
                }
            )
        )


        compare_df = (
            total_region_df
            .merge(
                senior_region_df,
                on="region",
                how="left"
            )
        )


        compare_df[
            "senior_population"
        ] = (
            compare_df[
                "senior_population"
            ]
            .fillna(0)
        )


        compare_df[
            "senior_share"
        ] = (
            compare_df[
                "senior_population"
            ]
            /
            compare_df[
                "total_population"
            ]
            *
            100
        )


        compare_df[
            "region_label"
        ] = (
            compare_df[
                "region"
            ]
            .apply(
                display_region
            )
        )


        compare_df = (
            compare_df
            .sort_values(
                "senior_share",
                ascending=True
            )
            .reset_index(drop=True)
        )


        if compare_df.empty:

            st.info(
                "지역별 비교 데이터가 없습니다."
            )

        else:

            max_share = max(
                float(
                    compare_df[
                        "senior_share"
                    ].max()
                ),
                1
            )


            fig_compare = go.Figure(
                go.Bar(

                    x=compare_df[
                        "senior_share"
                    ],

                    y=compare_df[
                        "region_label"
                    ],

                    orientation="h",

                    marker_color=[
                        "#D9A64A"
                        if (
                            selected_region != "전국"
                            and region == selected_region
                        )
                        else "#79B69B"

                        for region
                        in compare_df[
                            "region"
                        ]
                    ],

                    text=[
                        f"{value:.1f}%"
                        for value
                        in compare_df[
                            "senior_share"
                        ]
                    ],

                    textposition="outside",

                    cliponaxis=False,

                    hovertemplate=(
                        "<b>%{y}</b>"
                        "<br>"
                        "60세 이상 비율: %{x:.1f}%"
                        "<extra></extra>"
                    )
                )
            )


            fig_compare.update_layout(

                height=650,

                margin=dict(
                    l=100,
                    r=90,
                    t=40,
                    b=65
                ),

                paper_bgcolor="#182035",

                plot_bgcolor="#182035",

                font=dict(
                    color="#E8EDF5",
                    size=14
                ),

                showlegend=False,

                xaxis=dict(

                    title="60세 이상 인구 비율(%)",

                    gridcolor="#35405A",

                    range=[
                        0,
                        max_share * 1.15
                    ],

                    ticksuffix="%"
                ),

                yaxis=dict(
                    title=None
                )
            )


            st.plotly_chart(
                fig_compare,
                use_container_width=True,
                config={
                    "displayModeBar": False
                }
            )


    # ========================================================
    # REGION RANK
    # ========================================================

    if not compare_df.empty:

        rank_desc = (
            compare_df
            .sort_values(
                "senior_share",
                ascending=False
            )
            .reset_index(drop=True)
        )


        top_region = (
            rank_desc
            .iloc[0][
                "region_label"
            ]
        )


        top_share = float(
            rank_desc
            .iloc[0][
                "senior_share"
            ]
        )

    else:

        top_region = "-"
        top_share = 0


    # ========================================================
    # SELECTED REGION RANK
    # ========================================================

    selected_rank_text = ""


    if (
        selected_region != "전국"
        and not compare_df.empty
    ):

        rank_desc = (
            compare_df
            .sort_values(
                "senior_share",
                ascending=False
            )
            .reset_index(drop=True)
        )


        rank_match = (
            rank_desc[
                rank_desc[
                    "region"
                ]
                == selected_region
            ]
        )


        if not rank_match.empty:

            selected_rank = (
                rank_match.index[0]
                + 1
            )


            selected_rank_text = f"""
            <br>

            <b>{current_region_label}</b>의
            60세 이상 인구 비율은
            전국 지역 중
            <b>{selected_rank}위</b> 수준입니다.
            """


    # ========================================================
    # ANALYSIS
    # ========================================================

    st.html(
        f"""
        <div class="analysis-box">

            <div class="analysis-title">
                {selected_year}년 7월
                {current_region_label} 인구 분석
            </div>

            선택한 조건은
            <b>{selected_gender}</b> 기준이며,
            전체 인구는
            <b>{total_population:,}명</b>입니다.

            <br>

            이 중 60세 이상 인구는
            <b>{senior_population:,}명</b>으로,
            전체 인구의 약
            <b>{senior_share:.1f}%</b>를 차지합니다.

            <br>

            인구가 가장 많은 연령대는
            <b>{max_age_group}</b>이며,
            해당 연령대의 인구는
            <b>{max_age_population:,}명</b>입니다.

            <br>

            지역별 비교에서
            60세 이상 인구 비율이 가장 높은 지역은
            <b>{top_region}</b>으로,
            약
            <b>{top_share:.1f}%</b>입니다.

            {selected_rank_text}

            <br><br>

            본 데이터는
            <b>{selected_year}년 7월 기준 연령별 인구 현황</b>을
            기반으로 분석합니다.

            <br>

            원자료의 연령 구간이
            <b>10세 단위</b>로 제공되므로,
            현재 화면에서는
            <b>60세 이상</b>을 기준으로
            고연령 인구 비중을 비교합니다.

        </div>
        """
    )