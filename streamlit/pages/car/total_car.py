import sys
import json
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sqlalchemy import text


# ============================================================
# PROJECT ROOT
# SAFE/streamlit/pages/car/total_car.py
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
def load_car_data():

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

        return json.load(f)


# ============================================================
# LOAD
# ============================================================

try:

    df = load_car_data()

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


region_col = find_column(
    [
        "region",
        "sido",
        "region_name",
        "area",
        "city",
    ]
)


year_col = find_column(
    [
        "year",
        "base_year",
        "registration_year",
    ]
)


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


car_type_col = find_column(
    [
        "car_type",
        "vehicle_type",
        "vehicle_category",
        "car_category",
        "type",
    ]
)


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
# REQUIRED CHECK
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
# LABEL
# ============================================================

TOTAL_LABELS = [
    "계",
    "합계",
    "총계",
    "전체",
]


INVALID_REGIONS = [
    "",
    "계",
    "합계",
    "총계",
    "전국",
    "미상",
    "불명",
]


df = df[
    ~df[region_col].isin(
        INVALID_REGIONS
    )
].copy()


# ============================================================
# REGION NORMALIZATION
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

    value = str(value).strip()

    return REGION_MAP.get(
        value,
        value
    )


df["short_region"] = (
    df[region_col]
    .apply(
        short_region
    )
)


# ============================================================
# MAP REGION
# ============================================================

MAP_REGION_MAP = {

    "서울": "서울특별시",
    "부산": "부산광역시",
    "대구": "대구광역시",
    "인천": "인천광역시",
    "광주": "광주광역시",
    "대전": "대전광역시",
    "울산": "울산광역시",
    "세종": "세종특별자치시",

    "경기": "경기도",

    "강원": "강원도",

    "충북": "충청북도",
    "충남": "충청남도",

    "전북": "전라북도",
    "전남": "전라남도",

    "경북": "경상북도",
    "경남": "경상남도",

    "제주": "제주특별자치도",
}


def map_region_name(value):

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

    font-weight:
        800 !important;

    border-radius:
        2px !important;
}


/* ==========================================================
   PAGE
========================================================== */

.st-key-total_car_page {

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

    min-height:
        44px !important;
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

.st-key-type_bar_panel,
.st-key-type_pie_panel,
.st-key-region_map_panel,
.st-key-region_panel {

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
   MID SECTION TITLE
========================================================== */

.analysis-title {
    color: #FFFFFF;
    font-size: 23px;
    font-weight: 800;
    margin-top: 34px;
    margin-bottom: 6px;
}

.analysis-description {
    color: #AEB8C9;
    font-size: 15px;
    line-height: 1.7;
    margin-bottom: 12px;
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
    key="total_car_page"
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
                전체 자동차 등록 현황
            </div>

            <div class="page-sub">
                지역·차종·용도별 자동차 등록 데이터를 종합하여
                국내 자동차 등록 규모와 구성 특성을 확인합니다.
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
    # FILTER STATE / OPTIONS
    # 실제 필터 UI는 지도·지역 현황 아래에 렌더링합니다.
    # ========================================================

    if year_col is not None:
        year_options = sorted(
            df[year_col]
            .dropna()
            .astype(int)
            .unique()
            .tolist(),
            reverse=True
        )
    else:
        year_options = []

    region_options = (
        ["전체"]
        + sorted(
            df["short_region"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
    )

    if car_type_col is not None:
        type_values = sorted(
            [
                value
                for value in df[car_type_col]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
                if value not in TOTAL_LABELS
                and value != ""
            ]
        )
    else:
        type_values = []

    if usage_col is not None:
        usage_values = sorted(
            [
                value
                for value in df[usage_col]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
                if value not in TOTAL_LABELS
                and value != ""
            ]
        )
    else:
        usage_values = []

    # 첫 진입 시 기본값 지정
    if "total_car_year" not in st.session_state:
        st.session_state["total_car_year"] = (
            year_options[0] if year_options else None
        )

    if "total_car_region" not in st.session_state:
        st.session_state["total_car_region"] = "전체"

    if "total_car_type" not in st.session_state:
        st.session_state["total_car_type"] = "전체"

    if "total_car_usage" not in st.session_state:
        st.session_state["total_car_usage"] = "전체"

    # 옵션 변경/데이터 변경 시 잘못된 세션값 보정
    if (
        year_options
        and st.session_state.get("total_car_year") not in year_options
    ):
        st.session_state["total_car_year"] = year_options[0]

    if st.session_state.get("total_car_region") not in region_options:
        st.session_state["total_car_region"] = "전체"

    if st.session_state.get("total_car_type") not in (["전체"] + type_values):
        st.session_state["total_car_type"] = "전체"

    if st.session_state.get("total_car_usage") not in (["전체"] + usage_values):
        st.session_state["total_car_usage"] = "전체"

    selected_year = st.session_state.get("total_car_year")
    selected_region = st.session_state.get("total_car_region", "전체")
    selected_type = st.session_state.get("total_car_type", "전체")
    selected_usage = st.session_state.get("total_car_usage", "전체")


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


    if selected_region != "전체":

        filtered = filtered[
            filtered[
                "short_region"
            ] == selected_region
        ]


    if (
        car_type_col is not None
        and selected_type != "전체"
    ):

        filtered = filtered[
            filtered[
                car_type_col
            ] == selected_type
        ]


    if (
        usage_col is not None
        and selected_usage != "전체"
    ):

        filtered = filtered[
            filtered[
                usage_col
            ] == selected_usage
        ]


    # ========================================================
    # ANALYSIS DATA
    # 전체일 경우 합계행 사용
    # ========================================================

    analysis_df = filtered.copy()


    if (
        car_type_col is not None
        and selected_type == "전체"
    ):

        total_rows = analysis_df[
            analysis_df[
                car_type_col
            ].isin(
                TOTAL_LABELS
            )
        ]


        if not total_rows.empty:

            analysis_df = (
                total_rows.copy()
            )


    if (
        usage_col is not None
        and selected_usage == "전체"
    ):

        total_rows = analysis_df[
            analysis_df[
                usage_col
            ].isin(
                TOTAL_LABELS
            )
        ]


        if not total_rows.empty:

            analysis_df = (
                total_rows.copy()
            )


    # ========================================================
    # CURRENT SCOPE TOTAL
    # ========================================================

    region_current_df = (
        analysis_df

        .groupby(
            "short_region",
            as_index=False
        )[count_col]

        .sum()
    )


    total_count = int(
        region_current_df[
            count_col
        ].sum()
    )


    # ========================================================
    # NATIONAL DATA
    #
    # 전국 대비 비중 계산용
    # 지역 필터만 제외
    # ========================================================

    national_source = df.copy()


    if (
        year_col is not None
        and selected_year is not None
    ):

        national_source = national_source[
            national_source[
                year_col
            ] == selected_year
        ]


    if (
        car_type_col is not None
        and selected_type != "전체"
    ):

        national_source = national_source[
            national_source[
                car_type_col
            ] == selected_type
        ]


    if (
        usage_col is not None
        and selected_usage != "전체"
    ):

        national_source = national_source[
            national_source[
                usage_col
            ] == selected_usage
        ]


    if (
        car_type_col is not None
        and selected_type == "전체"
    ):

        national_total_type = national_source[
            national_source[
                car_type_col
            ].isin(
                TOTAL_LABELS
            )
        ]


        if not national_total_type.empty:

            national_source = (
                national_total_type.copy()
            )


    if (
        usage_col is not None
        and selected_usage == "전체"
    ):

        national_total_usage = national_source[
            national_source[
                usage_col
            ].isin(
                TOTAL_LABELS
            )
        ]


        if not national_total_usage.empty:

            national_source = (
                national_total_usage.copy()
            )


    national_region_df = (
        national_source

        .groupby(
            "short_region",
            as_index=False
        )[count_col]

        .sum()
    )


    national_total_count = int(
        national_region_df[
            count_col
        ].sum()
    )


    # ========================================================
    # TOP REGION
    # ========================================================

    if not national_region_df.empty:

        top_region_row = national_region_df.loc[
            national_region_df[
                count_col
            ].idxmax()
        ]


        top_region = str(
            top_region_row[
                "short_region"
            ]
        )


        top_region_count = int(
            top_region_row[
                count_col
            ]
        )

    else:

        top_region = "-"
        top_region_count = 0


    # ========================================================
    # TYPE DATA
    #
    # 지역 필터 반영
    # ========================================================

    type_source = df.copy()


    if (
        year_col is not None
        and selected_year is not None
    ):

        type_source = type_source[
            type_source[
                year_col
            ] == selected_year
        ]


    if selected_region != "전체":

        type_source = type_source[
            type_source[
                "short_region"
            ] == selected_region
        ]


    if (
        usage_col is not None
        and selected_usage != "전체"
    ):

        type_source = type_source[
            type_source[
                usage_col
            ] == selected_usage
        ]


    if car_type_col is not None:

        type_source = type_source[
            ~type_source[
                car_type_col
            ].isin(
                TOTAL_LABELS
            )
        ].copy()


        type_df = (
            type_source

            .groupby(
                car_type_col,
                as_index=False
            )[count_col]

            .sum()

            .sort_values(
                count_col,
                ascending=False
            )
        )

    else:

        type_df = pd.DataFrame()


    # ========================================================
    # TOP TYPE
    # ========================================================

    if not type_df.empty:

        top_type = str(
            type_df.iloc[0][
                car_type_col
            ]
        )


        top_type_count = int(
            type_df.iloc[0][
                count_col
            ]
        )

    else:

        top_type = "-"
        top_type_count = 0


    # ========================================================
    # USAGE DATA
    # ========================================================

    if usage_col is not None:

        usage_source = df.copy()


        if (
            year_col is not None
            and selected_year is not None
        ):

            usage_source = usage_source[
                usage_source[
                    year_col
                ] == selected_year
            ]


        if selected_region != "전체":

            usage_source = usage_source[
                usage_source[
                    "short_region"
                ] == selected_region
            ]


        if (
            car_type_col is not None
            and selected_type != "전체"
        ):

            usage_source = usage_source[
                usage_source[
                    car_type_col
                ] == selected_type
            ]


        usage_source = usage_source[
            ~usage_source[
                usage_col
            ].isin(
                TOTAL_LABELS
            )
        ].copy()


        usage_df = (
            usage_source

            .groupby(
                usage_col,
                as_index=False
            )[count_col]

            .sum()

            .sort_values(
                count_col,
                ascending=False
            )
        )

    else:

        usage_df = pd.DataFrame()


    # ========================================================
    # TOP USAGE
    # ========================================================

    if not usage_df.empty:

        top_usage = str(
            usage_df.iloc[0][
                usage_col
            ]
        )


        top_usage_count = int(
            usage_df.iloc[0][
                count_col
            ]
        )

    else:

        top_usage = "-"
        top_usage_count = 0


    # ========================================================
    # SCOPE
    # ========================================================

    analysis_scope = (
        "전국"
        if selected_region == "전체"
        else selected_region
    )


    # ========================================================
    # SELECTED REGION SHARE
    # ========================================================

    if (
        selected_region != "전체"
        and national_total_count > 0
    ):

        selected_region_share = (
            total_count
            / national_total_count
            * 100
        )

    else:

        selected_region_share = (
            top_region_count
            / national_total_count
            * 100
            if national_total_count > 0
            else 0
        )


    # ========================================================
    # MAP DATA
    #
    # 지도와 지역 순위는 전국 데이터 사용
    # ========================================================

    map_region_df = (
        national_region_df.copy()
    )


    map_region_df[
        "map_region"
    ] = (
        map_region_df[
            "short_region"
        ]
        .apply(
            map_region_name
        )
    )


    # ========================================================
    # MAP + REGION
    # ========================================================

    region_left, region_right = st.columns(
        [
            1.08,
            1,
        ],
        gap="medium"
    )


    # ========================================================
    # MAP
    # ========================================================

    with region_left:

        with st.container(
            key="region_map_panel"
        ):

            st.html(
                """
                <div class="panel-title">
                    대한민국 지역별 자동차 등록 분포
                </div>

                <div class="panel-sub">
                    전국 지역별 자동차 등록 규모를 지도에서 비교합니다.
                </div>
                """
            )


            try:

                korea_geojson = (
                    load_korea_geojson()
                )


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


                map_region_df[
                    "matched"
                ] = (
                    map_region_df[
                        "map_region"
                    ]
                    .isin(
                        geo_region_names
                    )
                )


                matched_df = (
                    map_region_df[
                        map_region_df[
                            "matched"
                        ]
                    ]
                    .copy()
                )


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


                    # 선택 지역 강조용
                    matched_df[
                        "selected"
                    ] = (
                        matched_df[
                            "short_region"
                        ]
                        == selected_region
                    )


                    border_colors = [

                        "#FFFFFF"
                        if selected_region != "전체"
                        and selected

                        else "#D1D6DF"

                        for selected
                        in matched_df[
                            "selected"
                        ]
                    ]


                    border_widths = [

                        3
                        if selected_region != "전체"
                        and selected

                        else 1

                        for selected
                        in matched_df[
                            "selected"
                        ]
                    ]


                    fig_map = go.Figure(
                        go.Choropleth(

                            geojson=korea_geojson,

                            locations=matched_df[
                                "map_region"
                            ],

                            z=matched_df[
                                "color_rank"
                            ],

                            featureidkey="properties.name",

                            customdata=matched_df[
                                count_col
                            ],

                            colorscale=[

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

                            zmin=0,
                            zmax=1,

                            marker=dict(

                                line=dict(
                                    color=border_colors,
                                    width=border_widths,
                                )
                            ),

                            hovertemplate=(
                                "<b>%{location}</b>"
                                "<br>"
                                "자동차 등록대수: "
                                "%{customdata:,}대"
                                "<extra></extra>"
                            ),

                            colorbar=dict(

                                title=dict(
                                    text=(
                                        "자동차 등록"
                                        "<br>"
                                        "상대 수준"
                                    )
                                ),

                                tickmode="array",

                                tickvals=[
                                    .1,
                                    .3,
                                    .5,
                                    .7,
                                    .9,
                                ],

                                ticktext=[
                                    "낮음",
                                    "↓",
                                    "중간",
                                    "↑",
                                    "높음",
                                ],

                                thickness=16,

                                len=.68,

                                outlinewidth=0,
                            ),
                        )
                    )


                    # 대한민국 전체 영역이 한 화면에 들어오도록
                    # 수동 확대값을 제거하고 GeoJSON 경계에 자동 맞춤합니다.
                    fig_map.update_geos(

                        projection_type="mercator",

                        fitbounds="locations",

                        visible=False,

                        showcoastlines=False,

                        showcountries=False,

                        showland=False,

                        bgcolor="#182035",
                    )


                    fig_map.update_layout(

                        height=610,

                        margin=dict(
                            l=0,
                            r=55,
                            t=10,
                            b=0,
                        ),

                        paper_bgcolor="#182035",

                        plot_bgcolor="#182035",

                        font=dict(
                            color="#E7EAF0"
                        ),

                        # 드래그 확대/이동 비활성화
                        dragmode=False,
                    )


                    st.plotly_chart(

                        fig_map,

                        use_container_width=True,

                        config={
                            "displayModeBar": False,
                            "scrollZoom": False,
                            "doubleClick": False
                        }
                    )


            except Exception as e:

                st.error(
                    "지도 표시 중 오류가 발생했습니다."
                )

                st.code(
                    str(e)
                )


    # ========================================================
    # REGION BAR
    # ========================================================

    with region_right:

        with st.container(
            key="region_panel"
        ):

            st.html(
                """
                <div class="panel-title">
                    지역별 자동차 등록 현황
                </div>

                <div class="panel-sub">
                    전국 지역별 자동차 등록 규모를 순위로 비교합니다.
                </div>
                """
            )


            region_chart_df = (
                national_region_df

                .sort_values(
                    count_col,
                    ascending=True
                )

                .copy()
            )


            if not region_chart_df.empty:

                max_region_value = float(
                    region_chart_df[
                        count_col
                    ].max()
                )


                if max_region_value <= 0:
                    max_region_value = 1


                region_colors = []


                for _, row in region_chart_df.iterrows():

                    if (
                        selected_region != "전체"
                        and row[
                            "short_region"
                        ] == selected_region
                    ):

                        color = "#E9783F"

                    elif (
                        row[
                            "short_region"
                        ] == top_region
                    ):

                        color = "#D9A64A"

                    else:

                        color = "#78927E"


                    region_colors.append(
                        color
                    )


                fig_region = go.Figure(
                    go.Bar(

                        x=region_chart_df[
                            count_col
                        ],

                        y=region_chart_df[
                            "short_region"
                        ],

                        orientation="h",

                        marker_color=region_colors,

                        text=[
                            f"{int(value):,}"
                            for value
                            in region_chart_df[
                                count_col
                            ]
                        ],

                        textposition="outside",

                        cliponaxis=False,

                        hovertemplate=(
                            "<b>%{y}</b>"
                            "<br>"
                            "%{x:,}대"
                            "<extra></extra>"
                        ),
                    )
                )


                fig_region.update_layout(

                    height=610,

                    margin=dict(
                        l=70,
                        r=115,
                        t=25,
                        b=65,
                    ),

                    paper_bgcolor="#182035",

                    plot_bgcolor="#182035",

                    showlegend=False,

                    font=dict(
                        color="#E7EAF0"
                    ),

                    xaxis=dict(

                        title="자동차 등록대수(대)",

                        gridcolor="#35405A",

                        tickformat=",",

                        range=[
                            0,
                            max_region_value * 1.22,
                        ],
                    ),

                    yaxis=dict(
                        title=None
                    ),
                )


                st.plotly_chart(

                    fig_region,

                    use_container_width=True,

                    config={
                        "displayModeBar": False
                    }
                )




    # ========================================================
    # REGION / TYPE / USAGE FILTER
    # 지도 및 지역별 등록 현황 다음에 배치
    # ========================================================

    st.html(
        """
        <div class="analysis-title" style="margin-top:34px;">
            지역별 자동차 등록 현황
        </div>

        <div class="analysis-description">
            지역·차종·용도를 선택하여 자동차 등록 현황을 상세하게 확인합니다.
        </div>
        """
    )

    # 지역 → 차종 → 용도 순서로 왼쪽 정렬
    # 연도 선택은 사용하지 않습니다.
    selected_year = None

    f1, f2, f3, spacer = st.columns([1, 1, 1, 1.8], gap="medium")

    with f1:
        selected_region = st.selectbox(
            "지역 선택",
            region_options,
            key="total_car_region"
        )

    with f2:
        selected_type = st.selectbox(
            "차종 선택",
            ["전체"] + type_values,
            key="total_car_type"
        )

    with f3:
        selected_usage = st.selectbox(
            "용도 선택",
            ["전체"] + usage_values,
            key="total_car_usage"
        )


    # ========================================================
    # KPI
    # ========================================================

    st.write("")

    k1, k2, k3, k4 = st.columns(4)

    # 첫 번째 KPI는 선택 지역 기준으로 표시
    if selected_region == "전체":
        first_kpi_label = "전국 자동차 등록대수"
        first_kpi_value = national_total_count
    else:
        first_kpi_label = f"{selected_region} 자동차 등록대수"
        first_kpi_value = total_count

    with k1:
        st.html(
            f"""
            <div class="kpi">
                <div class="kpi-label">
                    {first_kpi_label}
                </div>
                <div class="kpi-value">
                    {first_kpi_value:,}대
                </div>
            </div>
            """
        )

    with k2:
        st.html(
            f"""
            <div class="kpi">
                <div class="kpi-label">
                    등록대수 최다 지역
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
                    등록대수 최다 차종
                </div>
                <div class="kpi-value">
                    {top_type}
                </div>
            </div>
            """
        )

    if selected_region == "전체":
        share_region_label = top_region
        share_region_value = (
            top_region_count / national_total_count * 100
            if national_total_count > 0
            else 0
        )
    else:
        share_region_label = selected_region
        share_region_value = selected_region_share

    with k4:
        st.html(
            f"""
            <div class="kpi">
                <div class="kpi-label">
                    {share_region_label} 전국 비중
                </div>
                <div class="kpi-value">
                    {share_region_value:.1f}%
                </div>
            </div>
            """
        )


    # ========================================================
    # TYPE CHART
    # 지역 지도/지역별 등록 현황 다음으로 이동
    # ========================================================

    type_left, type_right = st.columns(
        [
            1.25,
            1,
        ],
        gap="medium"
    )


    # ========================================================
    # TYPE BAR
    # ========================================================

    with type_left:

        with st.container(
            key="type_bar_panel"
        ):

            st.html(
                f"""
                <div class="panel-title">
                    {analysis_scope} 차종별 자동차 등록대수
                </div>

                <div class="panel-sub">
                    선택한 지역과 조건에서 차종별 자동차 등록 규모를 비교합니다.
                </div>
                """
            )


            if type_df.empty:

                st.info(
                    "차종별 데이터가 없습니다."
                )

            else:

                chart_type_df = (
                    type_df

                    .sort_values(
                        count_col,
                        ascending=True
                    )

                    .copy()
                )


                max_type_value = float(
                    chart_type_df[
                        count_col
                    ].max()
                )


                if max_type_value <= 0:
                    max_type_value = 1


                type_colors = [

                    "#D9A64A"
                    if value == max_type_value

                    else "#79B69B"

                    for value
                    in chart_type_df[
                        count_col
                    ]
                ]


                fig_type = go.Figure(
                    go.Bar(

                        x=chart_type_df[
                            count_col
                        ],

                        y=chart_type_df[
                            car_type_col
                        ],

                        orientation="h",

                        marker_color=type_colors,

                        text=[
                            f"{int(value):,}대"
                            for value
                            in chart_type_df[
                                count_col
                            ]
                        ],

                        textposition="outside",

                        cliponaxis=False,

                        hovertemplate=(
                            "<b>%{y}</b>"
                            "<br>"
                            "%{x:,}대"
                            "<extra></extra>"
                        ),
                    )
                )


                fig_type.update_layout(

                    height=470,

                    margin=dict(
                        l=80,
                        r=130,
                        t=25,
                        b=65,
                    ),

                    paper_bgcolor="#182035",

                    plot_bgcolor="#182035",

                    showlegend=False,

                    font=dict(
                        color="#E7EAF0",
                        size=13,
                    ),

                    xaxis=dict(

                        title="자동차 등록대수(대)",

                        showgrid=True,

                        gridcolor="#35405A",

                        tickformat=",",

                        range=[
                            0,
                            max_type_value * 1.22,
                        ],
                    ),

                    yaxis=dict(
                        title=None
                    ),
                )


                st.plotly_chart(

                    fig_type,

                    use_container_width=True,

                    config={
                        "displayModeBar": False
                    }
                )


    # ========================================================
    # TYPE PIE
    # ========================================================

    with type_right:

        with st.container(
            key="type_pie_panel"
        ):

            st.html(
                f"""
                <div class="panel-title">
                    {analysis_scope} 차종별 등록 구성비
                </div>

                <div class="panel-sub">
                    선택 범위의 자동차 등록대수에서
                    각 차종이 차지하는 비중입니다.
                </div>
                """
            )


            if type_df.empty:

                st.info(
                    "차종별 구성비 데이터가 없습니다."
                )

            else:

                fig_pie = go.Figure(
                    go.Pie(

                        labels=type_df[
                            car_type_col
                        ],

                        values=type_df[
                            count_col
                        ],

                        hole=.58,

                        textinfo="label+percent",

                        hovertemplate=(
                            "<b>%{label}</b>"
                            "<br>"
                            "%{value:,}대"
                            "<br>"
                            "%{percent}"
                            "<extra></extra>"
                        ),
                    )
                )


                fig_pie.update_layout(

                    height=470,

                    margin=dict(
                        l=25,
                        r=25,
                        t=25,
                        b=25,
                    ),

                    paper_bgcolor="#182035",

                    plot_bgcolor="#182035",

                    legend=dict(

                        orientation="h",

                        y=-.08,

                        x=.5,

                        xanchor="center",
                    ),
                )


                st.plotly_chart(

                    fig_pie,

                    use_container_width=True,

                    config={
                        "displayModeBar": False
                    }
                )




    # ========================================================
    # SUMMARY
    # ========================================================

    if selected_region == "전체":

        summary_text = f"""
            선택한 조건에서 전국 자동차 등록대수는
            <b>{total_count:,}대</b>입니다.<br>

            자동차 등록대수가 가장 많은 지역은
            <b>{top_region}</b>이며,
            총 <b>{top_region_count:,}대</b>입니다.<br>

            가장 많은 자동차가 등록된 차종은
            <b>{top_type}</b>입니다.
        """

    else:

        summary_text = f"""
            선택한 지역은 <b>{selected_region}</b>이며,
            자동차 등록대수는 총
            <b>{total_count:,}대</b>입니다.<br>

            전국 자동차 등록대수 중
            약 <b>{selected_region_share:.1f}%</b>를 차지합니다.<br>

            {selected_region}에서 가장 많은 차종은
            <b>{top_type}</b>이며,
            가장 많은 차량 용도는
            <b>{top_usage}</b>입니다.
        """


    st.html(
        f"""
        <div class="info-box">

            <b>자동차 등록 현황 요약</b>
            <br><br>

            {summary_text}

        </div>
        """
    )