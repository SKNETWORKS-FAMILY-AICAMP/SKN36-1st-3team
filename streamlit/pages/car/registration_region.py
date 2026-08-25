import sys
import json
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from sqlalchemy import text


# ============================================================
# PROJECT ROOT
# SAFE/streamlit/pages/car/registration_region.py
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
def load_registration_region():

    engine = get_engine()

    query = text(
        """
        SELECT *
        FROM car_registration_region
        """
    )

    with engine.connect() as conn:
        df = pd.read_sql(
            query,
            conn
        )

    # 컬럼명 정리
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    return df


# ============================================================
# GEOJSON
# ============================================================

GEOJSON_PATH = (
    ROOT_DIR
    / "data"
    / "geo"
    / "korea_sido.geojson"
)


@st.cache_data
def load_korea_geojson():

    if not GEOJSON_PATH.exists():

        raise FileNotFoundError(
            f"GeoJSON 파일이 없습니다.\n{GEOJSON_PATH}"
        )

    with open(
        GEOJSON_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        geojson = json.load(f)

    return geojson


# ============================================================
# LOAD MYSQL
# ============================================================

try:

    df = load_registration_region()

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
#
# 실제 DB 컬럼명이 약간 달라도 최대한 자동으로 찾도록 설정
# ============================================================

def find_column(candidates):

    for col in candidates:

        if col in df.columns:
            return col

    return None


# ------------------------------------------------------------
# 지역
# ------------------------------------------------------------

region_col = find_column(
    [
        "region",
        "sido",
        "region_name",
        "area",
        "city",
    ]
)


# ------------------------------------------------------------
# 연도
# ------------------------------------------------------------

year_col = find_column(
    [
        "year",
        "base_year",
        "registration_year",
    ]
)


# ------------------------------------------------------------
# 등록대수
# ------------------------------------------------------------

count_col = find_column(
    [
        "count",
        "registration_count",
        "registered_count",
        "vehicle_count",
        "car_count",
        "total",
    ]
)


# ------------------------------------------------------------
# 차종
# ------------------------------------------------------------

car_type_col = find_column(
    [
        "car_type",
        "vehicle_type",
        "vehicle_category",
        "car_category",
        "type",
    ]
)


# ------------------------------------------------------------
# 용도
# ------------------------------------------------------------

usage_col = find_column(
    [
        "usage",
        "use_type",
        "purpose",
        "vehicle_usage",
        "car_usage",
    ]
)


# ============================================================
# REQUIRED COLUMN CHECK
# ============================================================

if region_col is None:

    st.error(
        f"""
        car_registration_region 테이블에서
        지역 컬럼을 찾을 수 없습니다.

        현재 컬럼:
        {list(df.columns)}
        """
    )

    st.stop()


if count_col is None:

    st.error(
        f"""
        car_registration_region 테이블에서
        자동차 등록대수 컬럼을 찾을 수 없습니다.

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
    errors="coerce"
).fillna(0)


if year_col is not None:

    df[year_col] = pd.to_numeric(
        df[year_col],
        errors="coerce"
    )


df[region_col] = (
    df[region_col]
    .fillna("")
    .astype(str)
    .str.strip()
)


if car_type_col is not None:

    df[car_type_col] = (
        df[car_type_col]
        .fillna("")
        .astype(str)
        .str.strip()
    )


if usage_col is not None:

    df[usage_col] = (
        df[usage_col]
        .fillna("")
        .astype(str)
        .str.strip()
    )


# ============================================================
# REMOVE TOTAL / UNKNOWN REGION
# ============================================================

df = df[
    ~df[region_col].isin(
        [
            "",
            "계",
            "합계",
            "총계",
            "전국",
            "불명",
            "미상",
        ]
    )
].copy()


# ============================================================
# SHORT REGION NAME
#
# 오른쪽 막대그래프 / 표에서 사용할 이름
# ============================================================

SHORT_REGION_MAP = {

    "서울": "서울",
    "서울특별시": "서울",

    "부산": "부산",
    "부산광역시": "부산",

    "대구": "대구",
    "대구광역시": "대구",

    "인천": "인천",
    "인천광역시": "인천",

    "광주": "광주",
    "광주광역시": "광주",

    "대전": "대전",
    "대전광역시": "대전",

    "울산": "울산",
    "울산광역시": "울산",

    "세종": "세종",
    "세종특별자치시": "세종",

    "경기": "경기",
    "경기도": "경기",
    "경기남부": "경기남부",
    "경기북부": "경기북부",

    "강원": "강원",
    "강원도": "강원",
    "강원특별자치도": "강원",

    "충북": "충북",
    "충청북도": "충북",

    "충남": "충남",
    "충청남도": "충남",

    "전북": "전북",
    "전라북도": "전북",
    "전북특별자치도": "전북",

    "전남": "전남",
    "전라남도": "전남",

    "경북": "경북",
    "경상북도": "경북",

    "경남": "경남",
    "경상남도": "경남",

    "제주": "제주",
    "제주도": "제주",
    "제주특별자치도": "제주",
}


def short_region(value):

    value = str(value).strip()

    return SHORT_REGION_MAP.get(
        value,
        value
    )


# ============================================================
# MAP REGION NORMALIZATION
#
# korea_sido.geojson
# properties.name 값에 맞춤
# ============================================================

MAP_REGION_MAP = {

    # 서울
    "서울": "서울특별시",
    "서울시": "서울특별시",
    "서울특별시": "서울특별시",

    # 부산
    "부산": "부산광역시",
    "부산시": "부산광역시",
    "부산광역시": "부산광역시",

    # 대구
    "대구": "대구광역시",
    "대구시": "대구광역시",
    "대구광역시": "대구광역시",

    # 인천
    "인천": "인천광역시",
    "인천시": "인천광역시",
    "인천광역시": "인천광역시",

    # 광주
    "광주": "광주광역시",
    "광주시": "광주광역시",
    "광주광역시": "광주광역시",

    # 대전
    "대전": "대전광역시",
    "대전시": "대전광역시",
    "대전광역시": "대전광역시",

    # 울산
    "울산": "울산광역시",
    "울산시": "울산광역시",
    "울산광역시": "울산광역시",

    # 세종
    "세종": "세종특별자치시",
    "세종시": "세종특별자치시",
    "세종특별자치시": "세종특별자치시",

    # 경기
    "경기": "경기도",
    "경기도": "경기도",

    # 혹시 자동차 DB에도 남부/북부가 존재할 경우
    "경기남부": "경기도",
    "경기북부": "경기도",

    # GeoJSON이 기존 행정명칭 사용
    "강원": "강원도",
    "강원도": "강원도",
    "강원특별자치도": "강원도",

    "충북": "충청북도",
    "충청북도": "충청북도",

    "충남": "충청남도",
    "충청남도": "충청남도",

    "전북": "전라북도",
    "전라북도": "전라북도",
    "전북특별자치도": "전라북도",

    "전남": "전라남도",
    "전라남도": "전라남도",

    "경북": "경상북도",
    "경상북도": "경상북도",

    "경남": "경상남도",
    "경상남도": "경상남도",

    "제주": "제주특별자치도",
    "제주도": "제주특별자치도",
    "제주특별자치도": "제주특별자치도",
}


def map_region(value):

    value = str(value).strip()

    return MAP_REGION_MAP.get(
        value,
        value
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
   NAV
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

.st-key-registration_region_page {

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
   BACK BUTTON
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

.st-key-map_panel,
.st-key-ranking_panel {

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
   INFO
========================================================== */

.info-box {

    background:
        #131B2E;

    border-left:
        3px solid
        #D6A348;

    padding:
        14px 16px;

    margin-top:
        18px;

    color:
        #ADB5C4;

    font-size:
        12px;

    line-height:
        1.7;
}



/* ==========================================================
   DETAIL TOGGLE BUTTON
========================================================== */

.st-key-region_detail_toggle button {

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


.st-key-region_detail_toggle button * {

    color: #E7EAF0 !important;

    -webkit-text-fill-color: #E7EAF0 !important;

    opacity: 1 !important;
}


.st-key-region_detail_toggle button:hover {

    background: #202A42 !important;

    border-color: #D6A348 !important;

    color: #F1C66A !important;
}


.st-key-region_detail_toggle button:hover * {

    color: #F1C66A !important;

    -webkit-text-fill-color: #F1C66A !important;
}


/* ==========================================================
   DETAIL TABLE PANEL
========================================================== */

.st-key-region_detail_panel {

    background: #182035;

    border: 1px solid #394560;

    border-radius: 14px;

    padding: 18px 18px 20px 18px;

    margin-top: 10px;
}

/* ==========================================================
   RESPONSIVE
========================================================== */

@media(max-width:1100px) {

    .page-title {
        font-size: 34px;
    }


    .st-key-registration_region_page {
        padding: 24px;
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
    key="registration_region_page"
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
                자동차 &gt; 자동차 등록 현황
            </div>

            <div class="page-title">
                지역별 자동차 등록 현황
            </div>

            <div class="page-sub">
                대한민국 시도별 자동차 등록대수 분포를 지도에서 확인하고,
                지역별 자동차 보유 규모를 비교합니다.
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
    # FILTERS
    # ========================================================

    filter_columns = []


    if year_col is not None:
        filter_columns.append("year")


    if car_type_col is not None:
        filter_columns.append("car_type")


    if usage_col is not None:
        filter_columns.append("usage")


    # 필터가 하나도 없는 경우
    if len(filter_columns) == 0:

        selected_year = None
        selected_car_type = "전체"
        selected_usage = "전체"


    else:

        column_ratios = (
            [1] * len(filter_columns)
            + [max(1, 5 - len(filter_columns))]
        )

        filter_cols = st.columns(
            column_ratios
        )

        current_index = 0


        # ====================================================
        # YEAR FILTER
        # ====================================================

        if year_col is not None:

            with filter_cols[current_index]:

                years = sorted(
                    df[
                        year_col
                    ]
                    .dropna()
                    .astype(int)
                    .unique(),
                    reverse=True
                )


                selected_year = st.selectbox(
                    "연도",
                    years,
                    key="registration_year"
                )

            current_index += 1

        else:

            selected_year = None


        # ====================================================
        # CAR TYPE FILTER
        # ====================================================

        if car_type_col is not None:

            with filter_cols[current_index]:

                car_types = sorted(
                    [
                        value
                        for value
                        in df[
                            car_type_col
                        ]
                        .dropna()
                        .astype(str)
                        .unique()
                        .tolist()
                        if value not in [
                            "",
                            "계",
                            "합계",
                            "총계",
                        ]
                    ]
                )


                car_type_options = (
                    ["전체"]
                    + car_types
                )


                selected_car_type = st.selectbox(
                    "차종",
                    car_type_options,
                    key="registration_car_type"
                )

            current_index += 1

        else:

            selected_car_type = "전체"


        # ====================================================
        # USAGE FILTER
        # ====================================================

        if usage_col is not None:

            with filter_cols[current_index]:

                usage_values = sorted(
                    [
                        value
                        for value
                        in df[
                            usage_col
                        ]
                        .dropna()
                        .astype(str)
                        .unique()
                        .tolist()
                        if value not in [
                            "",
                            "계",
                            "합계",
                            "총계",
                        ]
                    ]
                )


                usage_options = (
                    ["전체"]
                    + usage_values
                )


                selected_usage = st.selectbox(
                    "용도",
                    usage_options,
                    key="registration_usage"
                )

        else:

            selected_usage = "전체"


    # ========================================================
    # FILTER DATA
    # ========================================================

    filtered = df.copy()


    # --------------------------------------------------------
    # YEAR
    # --------------------------------------------------------

    if (
        year_col is not None
        and selected_year is not None
    ):

        filtered = filtered[
            filtered[
                year_col
            ] == selected_year
        ]


    # --------------------------------------------------------
    # CAR TYPE
    # --------------------------------------------------------

    if (
        car_type_col is not None
        and selected_car_type != "전체"
    ):

        filtered = filtered[
            filtered[
                car_type_col
            ].astype(str)
            == selected_car_type
        ]


    # --------------------------------------------------------
    # USAGE
    # --------------------------------------------------------

    if (
        usage_col is not None
        and selected_usage != "전체"
    ):

        filtered = filtered[
            filtered[
                usage_col
            ].astype(str)
            == selected_usage
        ]


    # ========================================================
    # IMPORTANT:
    #
    # 데이터에 '합계' 행이 있는 경우
    # 세부 차종 + 합계를 동시에 더하면 중복 집계될 수 있음.
    #
    # 따라서 전체 선택 상태에서는
    # 차종/용도의 '합계' 값이 존재하면 합계 행 우선 사용.
    # ========================================================

    analysis_df = filtered.copy()


    # ========================================================
    # CAR TYPE TOTAL HANDLING
    # ========================================================

    if (
        car_type_col is not None
        and selected_car_type == "전체"
    ):

        total_labels = [
            "계",
            "합계",
            "총계",
            "전체",
        ]


        total_rows = analysis_df[
            analysis_df[
                car_type_col
            ].astype(str)
            .isin(total_labels)
        ]


        # 합계 행이 실제 존재하면 그것만 사용
        if not total_rows.empty:

            analysis_df = total_rows.copy()


    # ========================================================
    # USAGE TOTAL HANDLING
    # ========================================================

    if (
        usage_col is not None
        and selected_usage == "전체"
    ):

        total_labels = [
            "계",
            "합계",
            "총계",
            "전체",
        ]


        total_rows = analysis_df[
            analysis_df[
                usage_col
            ].astype(str)
            .isin(total_labels)
        ]


        if not total_rows.empty:

            analysis_df = total_rows.copy()


    # ========================================================
    # RANKING DATA
    # ========================================================

    ranking_df = (
        analysis_df

        .groupby(
            region_col,
            as_index=False
        )[count_col]

        .sum()
    )


    ranking_df[
        "short_name"
    ] = (
        ranking_df[
            region_col
        ]
        .apply(
            short_region
        )
    )


    # ========================================================
    # MAP DATA
    # ========================================================

    map_source = (
        analysis_df.copy()
    )


    map_source[
        "map_region"
    ] = (
        map_source[
            region_col
        ]
        .apply(
            map_region
        )
    )


    # 경기남부 / 경기북부가 있을 경우
    # map_region 둘 다 경기도이므로 여기서 자동 합산
    map_df = (
        map_source

        .groupby(
            "map_region",
            as_index=False
        )[count_col]

        .sum()
    )


    # ========================================================
    # KPI
    # ========================================================

    total_count = int(
        ranking_df[
            count_col
        ].sum()
    )


    if not ranking_df.empty:

        max_row = ranking_df.loc[
            ranking_df[
                count_col
            ].idxmax()
        ]


        top_region = str(
            max_row[
                "short_name"
            ]
        )


        top_region_count = int(
            max_row[
                count_col
            ]
        )


        if total_count > 0:

            top_share = (
                top_region_count
                / total_count
                * 100
            )

        else:

            top_share = 0


    else:

        top_region = "-"
        top_region_count = 0
        top_share = 0


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
                    전국 자동차 등록대수
                </div>

                <div class="kpi-value">
                    {total_count:,}대
                </div>

            </div>
            """
        )


    with k2:

        st.html(
            f"""
            <div class="kpi">

                <div class="kpi-label">
                    자동차 등록 최다 지역
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
                    {top_region} 자동차 등록대수
                </div>

                <div class="kpi-value">
                    {top_region_count:,}대
                </div>

            </div>
            """
        )


    # ========================================================
    # MAP + RANKING
    # ========================================================

    left, right = st.columns(
        [
            1.55,
            1,
        ],
        gap="medium"
    )


    # ========================================================
    # MAP PANEL
    # ========================================================

    with left:

        with st.container(
            key="map_panel"
        ):

            st.html(
                """
                <div class="panel-title">
                    대한민국 시도별 자동차 등록 분포
                </div>

                <div class="panel-sub">
                    색상이 높은 단계일수록 자동차 등록대수가 상대적으로 많은 지역입니다.
                    지역에 마우스를 올리면 실제 등록대수를 확인할 수 있습니다.
                </div>
                """
            )


            if map_df.empty:

                st.warning(
                    "선택한 조건에 해당하는 데이터가 없습니다."
                )


            else:

                try:

                    korea_geojson = (
                        load_korea_geojson()
                    )


                    # =========================================
                    # GEOJSON REGION NAMES
                    # =========================================

                    geo_region_names = {

                        str(
                            feature
                            .get(
                                "properties",
                                {}
                            )
                            .get(
                                "name",
                                ""
                            )
                        ).strip()

                        for feature
                        in korea_geojson[
                            "features"
                        ]
                    }


                    # =========================================
                    # MATCH
                    # =========================================

                    map_df[
                        "matched"
                    ] = (
                        map_df[
                            "map_region"
                        ]
                        .isin(
                            geo_region_names
                        )
                    )


                    matched_df = (
                        map_df[
                            map_df[
                                "matched"
                            ]
                        ]
                        .copy()
                    )


                    unmatched_df = (
                        map_df[
                            ~map_df[
                                "matched"
                            ]
                        ]
                        .copy()
                    )


                    # =========================================
                    # COLOR RANK
                    #
                    # 자동차 등록대수는 경기 등 일부 지역이
                    # 압도적으로 높기 때문에 실제 값으로
                    # 색상을 잡으면 다른 지역이 비슷하게 보임.
                    #
                    # 따라서 색상 표현만 상대 순위 사용.
                    # =========================================

                    if not matched_df.empty:

                        matched_df[
                            "color_rank"
                        ] = (
                            matched_df[
                                count_col
                            ]
                            .rank(
                                method="average",
                                pct=True
                            )
                        )


                    # =========================================
                    # MAP
                    # =========================================

                    if matched_df.empty:

                        st.error(
                            "DB 지역과 GeoJSON 지역이 매칭되지 않습니다."
                        )


                        st.write(
                            "DB 지역:",
                            map_df[
                                "map_region"
                            ].tolist()
                        )


                        st.write(
                            "GeoJSON 지역:",
                            sorted(
                                geo_region_names
                            )
                        )


                    else:

                        fig_map = px.choropleth(

                            matched_df,

                            geojson=korea_geojson,

                            locations="map_region",

                            featureidkey="properties.name",

                            # 색상용 상대순위
                            color="color_rank",

                            hover_name="map_region",

                            # 실제 등록대수
                            custom_data=[
                                count_col
                            ],

                            # =================================
                            # 대비 강한 색상
                            # =================================

                            color_continuous_scale=[

                                [0.00, "#172338"],

                                [0.12, "#213A56"],

                                [0.25, "#2E5D73"],

                                [0.38, "#397E82"],

                                [0.50, "#56A18A"],

                                [0.62, "#8CB875"],

                                [0.73, "#C7B458"],

                                [0.83, "#E5A33E"],

                                [0.91, "#E9783F"],

                                [1.00, "#C94444"],
                            ],

                            range_color=[
                                0,
                                1
                            ],
                        )


                        # =====================================
                        # MAP POSITION
                        # =====================================

                        fig_map.update_geos(

                            projection_type="mercator",

                            # 대한민국 전체 지역(제주 포함)이
                            # 지도 안에 모두 들어오도록 자동 맞춤
                            fitbounds="locations",

                            visible=False,

                            showcoastlines=False,

                            showcountries=False,

                            showland=False,

                            bgcolor="#182035",
                        )


                        # =====================================
                        # BORDER + HOVER
                        # =====================================

                        fig_map.update_traces(

                            marker_line_color="#D1D6DF",

                            marker_line_width=1.25,

                            hovertemplate=(
                                "<b>%{location}</b>"
                                "<br>"
                                "자동차 등록대수: "
                                "%{customdata[0]:,}대"
                                "<extra></extra>"
                            ),
                        )


                        # =====================================
                        # LAYOUT + COLORBAR
                        # =====================================

                        fig_map.update_layout(

                            # 맞춰진 전체 지도 화면에서 이동/확대 방지
                            dragmode=False,

                            height=650,

                            margin=dict(
                                l=0,
                                r=90,
                                t=5,
                                b=0,
                            ),

                            paper_bgcolor="#182035",

                            plot_bgcolor="#182035",

                            font=dict(
                                color="#E7EAF0",
                                size=15,
                            ),

                            coloraxis_colorbar=dict(

                                title=dict(

                                    text=(
                                        "자동차 등록"
                                        "<br>"
                                        "상대 수준"
                                    ),

                                    font=dict(
                                        color="#E7EAF0",
                                        size=15,
                                    ),
                                ),

                                tickmode="array",

                                tickvals=[
                                    0.1,
                                    0.3,
                                    0.5,
                                    0.7,
                                    0.9,
                                ],

                                ticktext=[
                                    "낮음",
                                    "↓",
                                    "중간",
                                    "↑",
                                    "높음",
                                ],

                                tickfont=dict(
                                    color="#D5DAE4",
                                    size=14,
                                ),

                                thickness=18,

                                len=.72,

                                x=1.03,

                                y=.50,

                                outlinewidth=0,

                                bgcolor="rgba(0,0,0,0)",
                            ),
                        )


                        st.plotly_chart(

                            fig_map,

                            use_container_width=True,

                            config={
                                "displayModeBar": False,
                                "responsive": True,
                                "scrollZoom": False,
                                "doubleClick": False,
                            },
                        )


                        # =====================================
                        # UNMATCHED
                        # =====================================

                        if not unmatched_df.empty:

                            unmatched_names = (
                                unmatched_df[
                                    "map_region"
                                ]
                                .astype(str)
                                .tolist()
                            )


                            st.caption(
                                "⚠ 지도 경계와 매칭되지 않은 지역: "
                                + ", ".join(
                                    unmatched_names
                                )
                            )


                except Exception as e:

                    st.error(
                        "대한민국 지도 표시 중 오류가 발생했습니다."
                    )

                    st.code(
                        str(e)
                    )


    # ========================================================
    # RANKING PANEL
    # ========================================================

    with right:

        with st.container(
            key="ranking_panel"
        ):

            st.html(
                """
                <div class="panel-title">
                    지역별 자동차 등록대수 순위
                </div>

                <div class="panel-sub">
                    선택한 조건을 기준으로 지역별 자동차 등록 규모를 비교합니다.
                </div>
                """
            )


            rank_chart_df = (
                ranking_df

                .sort_values(
                    count_col,
                    ascending=True
                )

                .copy()
            )


            if rank_chart_df.empty:

                st.warning(
                    "표시할 데이터가 없습니다."
                )


            else:

                max_value = float(
                    rank_chart_df[
                        count_col
                    ].max()
                )


                min_value = float(
                    rank_chart_df[
                        count_col
                    ].min()
                )


                if max_value <= 0:
                    max_value = 1


                value_range = (
                    max_value
                    - min_value
                )


                # =============================================
                # BAR COLORS
                # =============================================

                bar_colors = []


                for value in rank_chart_df[
                    count_col
                ]:

                    if value_range == 0:

                        ratio = 1

                    else:

                        ratio = (
                            value
                            - min_value
                        ) / value_range


                    if ratio >= .80:

                        color = "#E0A548"

                    elif ratio >= .60:

                        color = "#CE994B"

                    elif ratio >= .40:

                        color = "#B88C50"

                    elif ratio >= .20:

                        color = "#9C7D55"

                    else:

                        color = "#806E5A"


                    bar_colors.append(
                        color
                    )


                # =============================================
                # BAR CHART
                # =============================================

                fig_rank = go.Figure(
                    go.Bar(

                        x=rank_chart_df[
                            count_col
                        ],

                        y=rank_chart_df[
                            "short_name"
                        ],

                        orientation="h",

                        marker=dict(
                            color=bar_colors
                        ),

                        text=[
                            f"{int(value):,}"
                            for value
                            in rank_chart_df[
                                count_col
                            ]
                        ],

                        textposition="outside",

                        textfont=dict(
                            color="#F2F4F8",
                            size=14,
                        ),

                        cliponaxis=False,

                        hovertemplate=(
                            "<b>%{y}</b>"
                            "<br>"
                            "%{x:,}대"
                            "<extra></extra>"
                        ),
                    )
                )


                # =============================================
                # RANKING LAYOUT
                # =============================================

                fig_rank.update_layout(

                    height=650,

                    margin=dict(
                        l=75,
                        r=130,
                        t=10,
                        b=65,
                    ),

                    paper_bgcolor="#182035",

                    plot_bgcolor="#182035",

                    showlegend=False,

                    bargap=.28,

                    font=dict(
                        color="#E7EAF0",
                        size=15,
                    ),

                    xaxis=dict(

                        title=dict(
                            text="자동차 등록대수(대)",

                            font=dict(
                                color="#D8DEE8",
                                size=15,
                            ),
                        ),

                        showgrid=True,

                        gridcolor="#35405A",

                        zeroline=False,

                        tickformat=",",

                        tickfont=dict(
                            color="#C2C9D5",
                            size=13,
                        ),

                        range=[
                            0,
                            max_value * 1.22,
                        ],
                    ),

                    yaxis=dict(

                        title=None,

                        showgrid=False,

                        tickfont=dict(
                            color="#F0F2F6",
                            size=14,
                        ),
                    ),
                )


                st.plotly_chart(

                    fig_rank,

                    use_container_width=True,

                    config={
                        "displayModeBar": False,
                    },
                )


    # ========================================================
    # SUMMARY
    # ========================================================

    if not ranking_df.empty:

        st.html(
            f"""
            <div class="info-box">

                <b>지역별 자동차 등록 현황 요약</b>
                <br><br>

                선택한 조건에서 전국 자동차 등록대수는
                <b>{total_count:,}대</b>입니다.
                <br>

                자동차 등록대수가 가장 많은 지역은
                <b>{top_region}</b>이며,
                총 <b>{top_region_count:,}대</b>가 등록되어 있습니다.
                <br>

                이는 선택된 조건의 전국 자동차 등록대수 중
                약 <b>{top_share:.1f}%</b>에 해당합니다.
                <br><br>

                지도 색상은 실제 등록대수의 단순 선형값이 아니라
                <b>지역별 상대적 순위</b>를 이용해 표현하여
                지역 간 등록 규모 차이를 더 쉽게 비교할 수 있도록 구성했습니다.

            </div>
            """
        )


    # ========================================================
    # DETAIL TABLE
    # ========================================================

    st.write("")


    # --------------------------------------------------------
    # DETAIL STATE
    # --------------------------------------------------------

    if "show_registration_region_detail" not in st.session_state:

        st.session_state[
            "show_registration_region_detail"
        ] = False


    # --------------------------------------------------------
    # DETAIL TOGGLE
    # --------------------------------------------------------

    with st.container(
        key="region_detail_toggle"
    ):

        detail_open = st.session_state[
            "show_registration_region_detail"
        ]


        detail_button_label = (
            "▲ 지역별 자동차 등록 데이터 닫기"
            if detail_open
            else "▼ 지역별 자동차 등록 데이터 상세 보기"
        )


        if st.button(
            detail_button_label,
            key="registration_region_detail_button",
            use_container_width=True
        ):

            st.session_state[
                "show_registration_region_detail"
            ] = (
                not detail_open
            )

            st.rerun()


    # --------------------------------------------------------
    # DETAIL CONTENT
    # --------------------------------------------------------

    if st.session_state[
        "show_registration_region_detail"
    ]:

        with st.container(
            key="region_detail_panel"
        ):

            table_df = (
                ranking_df[
                    [
                        "short_name",
                        count_col,
                    ]
                ]
                .copy()
            )


            # ====================================================
            # SHARE
            # ====================================================

            if total_count > 0:

                table_df[
                    "share"
                ] = (
                    table_df[
                        count_col
                    ]
                    / total_count
                    * 100
                )

            else:

                table_df[
                    "share"
                ] = 0


            # ====================================================
            # SORT
            # ====================================================

            table_df = (
                table_df

                .sort_values(
                    count_col,
                    ascending=False
                )

                .reset_index(
                    drop=True
                )
            )


            # ====================================================
            # FORMAT
            # ====================================================

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
                "share"
            ] = (
                table_df[
                    "share"
                ]
                .round(1)
            )


            table_df.columns = [
                "지역",
                "자동차 등록대수",
                "전국 비중",
            ]


            display_df = (
                table_df
                .copy()
            )


            display_df[
                "자동차 등록대수"
            ] = (
                display_df[
                    "자동차 등록대수"
                ]
                .map(
                    lambda value:
                        f"{int(value):,}대"
                )
            )


            display_df[
                "전국 비중"
            ] = (
                display_df[
                    "전국 비중"
                ]
                .map(
                    lambda value:
                        f"{value:.1f}%"
                )
            )


            table_rows = ""


            for _, row in display_df.iterrows():

                table_rows += f"""
                    <tr>

                        <td>
                            {row["지역"]}
                        </td>

                        <td>
                            {row["자동차 등록대수"]}
                        </td>

                        <td>
                            {row["전국 비중"]}
                        </td>

                    </tr>
                """


            st.html(
                f"""
                <style>

                .region-dark-table-wrap {{

                    width: 100%;

                    overflow-x: auto;

                    background: #182035;

                    border: 1px solid #3A4662;

                    border-radius: 12px;
                }}


                .region-dark-table {{

                    width: 100%;

                    border-collapse: collapse;

                    background: #182035;

                    color: #E7EAF0;

                    font-size: 13px;
                }}


                .region-dark-table thead {{

                    background: #202A42;
                }}


                .region-dark-table th {{

                    background: #202A42;

                    color: #D6A348;

                    font-weight: 900;

                    text-align: center;

                    padding: 14px 16px;

                    border-bottom: 1px solid #4A5670;

                    white-space: nowrap;
                }}


                .region-dark-table td {{

                    background: #182035;

                    color: #E7EAF0;

                    font-weight: 600;

                    text-align: center;

                    padding: 13px 16px;

                    border-bottom: 1px solid #303B55;

                    white-space: nowrap;
                }}


                .region-dark-table tbody tr:nth-child(even) td {{

                    background: #1B243A;
                }}


                .region-dark-table tbody tr:hover td {{

                    background: #222D47;

                    color: #FFFFFF;
                }}


                .region-dark-table tbody tr:last-child td {{

                    border-bottom: none;
                }}

                </style>


                <div class="region-dark-table-wrap">

                    <table class="region-dark-table">

                        <thead>

                            <tr>

                                <th>
                                    지역
                                </th>

                                <th>
                                    자동차 등록대수
                                </th>

                                <th>
                                    전국 비중
                                </th>

                            </tr>

                        </thead>


                        <tbody>

                            {table_rows}

                        </tbody>

                    </table>

                </div>
                """
            )