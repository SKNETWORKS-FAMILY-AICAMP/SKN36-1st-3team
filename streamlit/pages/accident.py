import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import text


# ============================================================
# PROJECT ROOT
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

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
# ACCIDENT SUB PAGE
# ============================================================

def go_driver_age():
    st.switch_page(
        "pages/accident/age_total.py"
    )


def go_driver_age_time():
    st.switch_page(
        "pages/accident/driver_age_time.py"
    )


def go_weather():
    st.switch_page(
        "pages/accident/weather.py"
    )


def go_senior_type_time():
    st.switch_page(
        "pages/accident/senior_type_time.py"
    )


def go_senior_month_time():
    st.switch_page(
        "pages/accident/senior_month_time.py"
    )


def go_senior_region_month():
    st.switch_page(
        "pages/accident/senior_region_month.py"
    )


def go_age_total():
    st.switch_page(
        "pages/accident/age_total.py"
    )


def go_region_total():
    st.switch_page(
        "pages/accident/region_total.py"
    )


# ============================================================
# MYSQL
# ============================================================

@st.cache_data(ttl=600)
def load_table(table_name: str):

    allowed_tables = {
        "accident_region",
        "driver_age_accident",
        "driver_time_accident",
        "driver_weather_accident",
        "senior_accident_type_time",
        "senior_accident_month_time",
        "senior_accident_region_month",
        "accident_age",
    }


    if table_name not in allowed_tables:

        raise ValueError(
            f"허용되지 않은 테이블: {table_name}"
        )


    engine = get_engine()


    query = text(
        f"""
        SELECT *
        FROM `{table_name}`
        """
    )


    with engine.connect() as conn:

        df = pd.read_sql(
            query,
            conn,
        )


    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )


    return df



# ============================================================
# SENIOR POPULATION / LICENSE DATA
# ============================================================

@st.cache_data(ttl=600)
def load_senior_compare_data():

    engine = get_engine()

    population_query = text(
        """
        SELECT
            region,
            year,
            gender,
            age_group,
            population
        FROM age_population
        """
    )

    license_query = text(
        """
        SELECT *
        FROM license_holder_age
        """
    )

    with engine.connect() as conn:

        population_df = pd.read_sql(
            population_query,
            conn,
        )

        license_df = pd.read_sql(
            license_query,
            conn,
        )

    population_df.columns = (
        population_df.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    license_df.columns = (
        license_df.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    return population_df, license_df


def find_column(
    df: pd.DataFrame,
    candidates: list[str],
):

    for column in candidates:

        if column in df.columns:
            return column

    return None


def parse_age_range(
    value,
):

    """
    연령 문자열을 (최소연령, 최대연령) 형태로 변환합니다.

    예)
    65        -> (65, 65)
    65세      -> (65, 65)
    60~69세   -> (60, 69)
    65세 이상 -> (65, None)
    """

    import re

    text_value = str(
        value
    ).strip()

    numbers = [
        int(number)
        for number
        in re.findall(
            r"\d+",
            text_value,
        )
    ]

    if not numbers:
        return None, None

    if (
        "이상"
        in text_value
    ):

        return (
            numbers[0],
            None,
        )

    if len(numbers) >= 2:

        return (
            numbers[0],
            numbers[1],
        )

    return (
        numbers[0],
        numbers[0],
    )


def population_65_weight(
    age_value,
):

    """
    65세 이상 인구 계산용 가중치입니다.

    age_population이 60~69세처럼 구간으로 제공되는 경우
    65~69세에 해당하는 비율만 추정하여 반영합니다.

    예)
    60~69세 -> 5 / 10 = 0.5
    70~79세 -> 1.0
    50~59세 -> 0.0
    """

    minimum_age, maximum_age = (
        parse_age_range(
            age_value
        )
    )

    if minimum_age is None:
        return 0.0

    if maximum_age is None:

        return (
            1.0
            if minimum_age >= 65
            else 0.0
        )

    if maximum_age < 65:
        return 0.0

    if minimum_age >= 65:
        return 1.0

    total_ages = (
        maximum_age
        - minimum_age
        + 1
    )

    senior_ages = (
        maximum_age
        - 65
        + 1
    )

    if total_ages <= 0:
        return 0.0

    return max(
        0.0,
        min(
            senior_ages
            / total_ages,
            1.0,
        ),
    )


def is_license_age_65_plus(
    age_value,
):

    minimum_age, maximum_age = (
        parse_age_range(
            age_value
        )
    )

    if minimum_age is None:
        return False

    return minimum_age >= 65



# ============================================================
# DB STATUS
# ============================================================

db_connected = True

try:
    _ = load_table("accident_region")
except Exception:
    db_connected = False


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
            #25395F 48%,
            #A08C68 79%,
            #DDA747 100%
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

    max-width: 1500px;

    padding-top: 12px;

    padding-left: 26px;

    padding-right: 26px;

    padding-bottom: 40px;
}


/* ==========================================================
   NAV
========================================================== */

.st-key-top_nav {

    background: rgba(255,255,255,.98);

    border-radius: 16px;

    padding:
        10px 20px;

    margin-bottom: 18px;

    box-shadow:
        0 5px 20px
        rgba(0,0,0,.1);
}


.st-key-top_nav button {

    background: transparent !important;

    color: #30384D !important;

    border: none !important;

    box-shadow: none !important;

    min-height: 42px !important;

    font-size: 14px !important;

    font-weight: 500 !important;

    white-space: nowrap !important;
}


.st-key-top_nav button:hover {

    background: transparent !important;

    color: #69B895 !important;
}


.st-key-nav_logo button {

    color: #27314C !important;

    font-size: 28px !important;

    font-weight: 900 !important;

    justify-content: flex-start !important;

    padding-left: 0 !important;
}


.st-key-nav_accident button {

    color: #49A982 !important;

    font-weight: 800 !important;
}


.st-key-nav_future button {

    background: #D9A64A !important;

    color: #172035 !important;

    font-weight: 800 !important;

    border-radius: 1px !important;
}


/* ==========================================================
   PAGE
========================================================== */

.st-key-accident_page {

    background: #101625;

    border:
        1px solid
        #34405A;

    border-radius: 20px;

    padding:
        30px 32px 40px 32px;

    box-shadow:
        0 12px 36px
        rgba(0,0,0,.18);
}


/* ==========================================================
   HEADER
========================================================== */

.accident-path {

    color: #69B895;

    font-size: 11px;

    font-weight: 800;

    letter-spacing: 1.5px;

    margin-bottom: 9px;
}


.accident-title {

    color: #FFFFFF;

    font-size: 38px;

    font-weight: 900;

    letter-spacing: -2px;

    line-height: 1.15;

    margin-bottom: 10px;
}


.accident-sub {

    color: #929AAC;

    font-size: 13px;

    line-height: 1.6;

    margin-bottom: 26px;
}


/* ==========================================================
   SECTION
========================================================== */

.section-title {

    color: white;

    font-size: 19px;

    font-weight: 800;

    margin-top: 28px;

    margin-bottom: 5px;
}


.section-sub {

    color: #7F899B;

    font-size: 11px;

    margin-bottom: 18px;
}


/* ==========================================================
   ANALYSIS CARD
========================================================== */

.st-key-analysis_cards button {

    width: 100% !important;

    height: 160px !important;

    background: #182035 !important;

    color: #FFFFFF !important;

    border:
        1px solid
        #3A4662 !important;

    border-radius: 22px !important;

    white-space: pre-line !important;

    line-height: 1.55 !important;

    font-size: 15px !important;

    font-weight: 800 !important;

    box-shadow:
        0 7px 16px
        rgba(0,0,0,.12) !important;

    transition:
        transform .15s ease,
        border-color .15s ease,
        box-shadow .15s ease !important;
}


.st-key-analysis_cards button:hover {

    transform: translateY(-4px);

    border-color: #69B895 !important;

    box-shadow:
        0 13px 25px
        rgba(0,0,0,.22) !important;
}


/* card accent */

.st-key-card_driver_age button {
    border-top: 5px solid #69B895 !important;
}


.st-key-card_driver_time button {
    border-top: 5px solid #D8A04D !important;
}


.st-key-card_weather button {
    border-top: 5px solid #5D91C8 !important;
}


.st-key-card_senior_type button {
    border-top: 5px solid #C96C50 !important;
}


.st-key-card_senior_month button {
    border-top: 5px solid #8DB79E !important;
}


.st-key-card_senior_region button {
    border-top: 5px solid #D9A45B !important;
}


.st-key-card_age_total button {
    border-top: 5px solid #9D7FC1 !important;
}


.st-key-card_region_total button {
    border-top: 5px solid #69A8B5 !important;
}


.card-desc {

    color: #7E8799;

    text-align: center;

    font-size: 10px;

    line-height: 1.45;

    margin-top: -7px;

    margin-bottom: 12px;
}


/* ==========================================================
   DB STATUS
========================================================== */

.db-ok {

    color: #69B895;

    font-size: 11px;

    margin-top: 23px;
}


.db-error {

    color: #C96A50;

    font-size: 11px;

    margin-top: 23px;
}



/* ==========================================================
   SENIOR POPULATION · LICENSE COMPARISON
========================================================== */

.st-key-senior_license_compare {

    background:
        #182035;

    border:
        1px solid
        #3A4662;

    border-radius:
        22px;

    padding:
        22px
        24px
        24px
        24px;

    margin-top:
        8px;

    margin-bottom:
        28px;
}


.senior-compare-title {

    color:
        #FFFFFF;

    font-size:
        20px;

    font-weight:
        900;

    margin-bottom:
        7px;
}


.senior-compare-sub {

    color:
        #98A3B7;

    font-size:
        12px;

    line-height:
        1.65;

    margin-bottom:
        20px;
}


.senior-compare-grid {

    display:
        grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap:
        14px;

    margin-bottom:
        20px;
}


.senior-compare-card {

    background:
        #131B2E;

    border:
        1px solid
        #394560;

    border-radius:
        15px;

    padding:
        17px
        19px;
}


.senior-compare-label {

    color:
        #A8B1C1;

    font-size:
        11px;

    margin-bottom:
        10px;
}


.senior-compare-value {

    color:
        #FFFFFF;

    font-size:
        24px;

    font-weight:
        900;
}


.senior-compare-value.gold {

    color:
        #F1C66A;
}


.senior-progress-head {

    display:
        flex;

    align-items:
        center;

    justify-content:
        space-between;

    color:
        #DCE3ED;

    font-size:
        12px;

    font-weight:
        700;

    margin-bottom:
        8px;
}


.senior-progress-track {

    width:
        100%;

    height:
        14px;

    background:
        #0F1726;

    border:
        1px solid
        #35415A;

    border-radius:
        999px;

    overflow:
        hidden;
}


.senior-progress-fill {

    height:
        100%;

    border-radius:
        999px;

    background:
        linear-gradient(
            90deg,
            #8E7656 0%,
            #D6A348 100%
        );
}


.senior-compare-note {

    margin-top:
        13px;

    color:
        #7F8A9F;

    font-size:
        10px;

    line-height:
        1.6;
}


@media(max-width:900px) {

    .senior-compare-grid {

        grid-template-columns:
            1fr;
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
        gap="small",
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
                icon="📈",
            )


# ============================================================
# ACCIDENT PAGE
# ============================================================

with st.container(
    key="accident_page"
):

    # ========================================================
    # HEADER
    # ========================================================

    st.html(
        """
        <div class="accident-path">
            SAFER DATA ANALYTICS
        </div>

        <div class="accident-title">
            교통사고 분석
        </div>

        <div class="accident-sub">
            가해운전자·고령운전자·지역·기상 데이터를 연결하여
            사고 발생 특성과 고위험 조건을 분석합니다.
        </div>
        """
    )


    # ========================================================
    # 65+ POPULATION · LICENSE COMPARISON
    # ========================================================

    try:

        senior_population_df, senior_license_df = (
            load_senior_compare_data()
        )


        # ----------------------------------------------------
        # POPULATION CLEAN
        # ----------------------------------------------------

        senior_population_df[
            "year"
        ] = pd.to_numeric(
            senior_population_df[
                "year"
            ],
            errors="coerce",
        )


        senior_population_df[
            "population"
        ] = pd.to_numeric(
            senior_population_df[
                "population"
            ],
            errors="coerce",
        ).fillna(0)


        senior_population_df[
            "region"
        ] = (
            senior_population_df[
                "region"
            ]
            .fillna("")
            .astype(str)
            .str.strip()
        )


        senior_population_df[
            "gender"
        ] = (
            senior_population_df[
                "gender"
            ]
            .fillna("")
            .astype(str)
            .str.strip()
        )


        senior_population_df[
            "age_group"
        ] = (
            senior_population_df[
                "age_group"
            ]
            .fillna("")
            .astype(str)
            .str.strip()
        )


        senior_population_df = (
            senior_population_df[
                senior_population_df[
                    "year"
                ].notna()
            ]
            .copy()
        )


        senior_population_df[
            "year"
        ] = (
            senior_population_df[
                "year"
            ]
            .astype(int)
        )


        # ----------------------------------------------------
        # LICENSE COLUMN FIND
        # ----------------------------------------------------

        license_year_col = find_column(
            senior_license_df,
            [
                "year",
                "base_year",
            ],
        )


        license_age_col = find_column(
            senior_license_df,
            [
                "age_group",
                "age",
                "age_range",
            ],
        )


        license_count_col = find_column(
            senior_license_df,
            [
                "count",
                "license_count",
                "holders",
                "holder_count",
            ],
        )


        if (
            license_year_col is None
            or license_age_col is None
            or license_count_col is None
        ):

            raise ValueError(
                "license_holder_age 테이블에서 "
                "연도·연령·면허 소지자 수 컬럼을 찾을 수 없습니다."
            )


        senior_license_df[
            license_year_col
        ] = pd.to_numeric(
            senior_license_df[
                license_year_col
            ],
            errors="coerce",
        )


        senior_license_df[
            license_count_col
        ] = pd.to_numeric(
            senior_license_df[
                license_count_col
            ],
            errors="coerce",
        ).fillna(0)


        senior_license_df[
            license_age_col
        ] = (
            senior_license_df[
                license_age_col
            ]
            .fillna("")
            .astype(str)
            .str.strip()
        )


        senior_license_df = (
            senior_license_df[
                senior_license_df[
                    license_year_col
                ].notna()
            ]
            .copy()
        )


        senior_license_df[
            license_year_col
        ] = (
            senior_license_df[
                license_year_col
            ]
            .astype(int)
        )


        # ----------------------------------------------------
        # YEAR MATCH
        #
        # 우선 동일 연도를 찾고,
        # 공통 연도가 없으면 각 데이터의 최신 연도를 사용
        # ----------------------------------------------------

        population_years = sorted(
            senior_population_df[
                "year"
            ]
            .unique()
            .tolist()
        )


        license_years = sorted(
            senior_license_df[
                license_year_col
            ]
            .unique()
            .tolist()
        )


        common_years = sorted(
            set(
                population_years
            )
            &
            set(
                license_years
            )
        )


        if common_years:

            population_compare_year = (
                common_years[-1]
            )

            license_compare_year = (
                common_years[-1]
            )

            same_year = True


        else:

            population_compare_year = (
                population_years[-1]
                if population_years
                else None
            )

            license_compare_year = (
                license_years[-1]
                if license_years
                else None
            )

            same_year = False


        # ----------------------------------------------------
        # POPULATION YEAR FILTER
        # ----------------------------------------------------

        population_compare_df = (
            senior_population_df[
                senior_population_df[
                    "year"
                ]
                == population_compare_year
            ]
            .copy()
        )


        # 성별 계가 있으면 계만 사용
        if (
            "계"
            in population_compare_df[
                "gender"
            ].unique()
        ):

            population_compare_df = (
                population_compare_df[
                    population_compare_df[
                        "gender"
                    ] == "계"
                ]
                .copy()
            )


        # 전국/합계 행과 지역별 행의 중복 합산 방지
        regional_population_df = (
            population_compare_df[
                ~population_compare_df[
                    "region"
                ].isin(
                    [
                        "",
                        "전국",
                        "계",
                        "합계",
                        "총계",
                    ]
                )
            ]
            .copy()
        )


        if not regional_population_df.empty:

            population_compare_df = (
                regional_population_df
            )


        # ----------------------------------------------------
        # 65+ POPULATION
        # ----------------------------------------------------

        population_compare_df[
            "senior_weight"
        ] = (
            population_compare_df[
                "age_group"
            ]
            .apply(
                population_65_weight
            )
        )


        senior_population_65 = int(
            round(
                (
                    population_compare_df[
                        "population"
                    ]
                    *
                    population_compare_df[
                        "senior_weight"
                    ]
                )
                .sum()
            )
        )


        # ----------------------------------------------------
        # 65+ LICENSE HOLDERS
        # ----------------------------------------------------

        license_compare_df = (
            senior_license_df[
                senior_license_df[
                    license_year_col
                ]
                == license_compare_year
            ]
            .copy()
        )


        license_compare_df[
            "is_65_plus"
        ] = (
            license_compare_df[
                license_age_col
            ]
            .apply(
                is_license_age_65_plus
            )
        )


        senior_license_65 = int(
            license_compare_df.loc[
                license_compare_df[
                    "is_65_plus"
                ],
                license_count_col,
            ]
            .sum()
        )


        # ----------------------------------------------------
        # RATIO
        # ----------------------------------------------------

        senior_license_ratio = (
            senior_license_65
            / senior_population_65
            * 100

            if senior_population_65 > 0

            else 0
        )


        progress_width = max(
            0,
            min(
                senior_license_ratio,
                100,
            ),
        )


        # ----------------------------------------------------
        # LABEL
        # ----------------------------------------------------

        if same_year:

            compare_year_text = (
                f"{population_compare_year}년 기준"
            )

        else:

            compare_year_text = (
                f"인구 {population_compare_year}년 · "
                f"면허 {license_compare_year}년 기준"
            )


        # ----------------------------------------------------
        # PANEL
        # ----------------------------------------------------

        with st.container(
            key="senior_license_compare"
        ):

            st.html(
                f"""
                <div class="senior-compare-title">
                    65세 이상 인구 · 운전면허 보유 비교
                </div>

                <div class="senior-compare-sub">
                    {compare_year_text} 전체 고령 인구와
                    65세 이상 운전면허 소지자 규모를 비교합니다.
                </div>


                <div class="senior-compare-grid">

                    <div class="senior-compare-card">

                        <div class="senior-compare-label">
                            65세 이상 전체 인구
                        </div>

                        <div class="senior-compare-value">
                            {senior_population_65:,}명
                        </div>

                    </div>


                    <div class="senior-compare-card">

                        <div class="senior-compare-label">
                            65세 이상 면허 소지자
                        </div>

                        <div class="senior-compare-value">
                            {senior_license_65:,}명
                        </div>

                    </div>


                    <div class="senior-compare-card">

                        <div class="senior-compare-label">
                            고령 인구 대비 면허 보유 비율
                        </div>

                        <div class="senior-compare-value gold">
                            {senior_license_ratio:.1f}%
                        </div>

                    </div>

                </div>


                <div class="senior-progress-head">

                    <span>
                        65세 이상 인구 대비 면허 보유 수준
                    </span>

                    <span>
                        {senior_license_ratio:.1f}%
                    </span>

                </div>


                <div class="senior-progress-track">

                    <div
                        class="senior-progress-fill"
                        style="width:{progress_width:.1f}%;">
                    </div>

                </div>


                <div class="senior-compare-note">
                    ※ 인구 원자료가 10세 단위 연령 구간으로 제공되는 경우
                    60~69세 구간 중 65~69세 인구는 구간 내 균등 분포를 가정한
                    추정값을 사용합니다.
                </div>
                """
            )


        if (
            not same_year
            and population_compare_year is not None
            and license_compare_year is not None
        ):

            st.info(
                "인구 데이터와 면허 데이터에 동일한 연도가 없어 "
                f"인구 {population_compare_year}년, "
                f"면허 {license_compare_year}년 최신 자료를 비교합니다."
            )


    except Exception as e:

        st.warning(
            f"65세 이상 인구·면허 비교 데이터를 불러오지 못했습니다: {e}"
        )



    # ========================================================
    # 1. DRIVER
    # ========================================================

    st.html(
        """
        <div class="section-title">
            가해운전자
        </div>

        <div class="section-sub">
            가해운전자의 연령대와 시간대별 사고 특성을 분석합니다.
        </div>
        """
    )

    with st.container(
        key="analysis_cards"
    ):

        c1, c2, empty1 = st.columns(
            3,
            gap="medium",
        )

        with c1:

            if st.button(
                "👤\n\n가해운전자\n연령대별 사고",
                key="card_driver_age",
                use_container_width=True,
            ):
                go_driver_age()

            st.html(
                """
                <div class="card-desc">
                    연령대별 사고 규모와<br>
                    연도별 변화 분석
                </div>
                """
            )

        with c2:

            if st.button(
                "🕐\n\n가해운전자\n연령 × 시간",
                key="card_driver_time",
                use_container_width=True,
            ):
                go_driver_age_time()

            st.html(
                """
                <div class="card-desc">
                    연령대와 시간대별<br>
                    사고 집중 패턴 분석
                </div>
                """
            )


        # ====================================================
        # 2. SENIOR DRIVER
        # ====================================================

        st.html(
            """
            <div class="section-title">
                고령운전자
            </div>

            <div class="section-sub">
                고령운전자의 사고유형·시간·월·지역별 사고 특성을 분석합니다.
            </div>
            """
        )

        c3, c4, c5 = st.columns(
            3,
            gap="medium",
        )

        with c3:

            if st.button(
                "⚠️\n\n고령운전자\n사고유형 × 시간",
                key="card_senior_type",
                use_container_width=True,
            ):
                go_senior_type_time()

            st.html(
                """
                <div class="card-desc">
                    사고유형과 시간대별<br>
                    고령운전자 사고 분석
                </div>
                """
            )

        with c4:

            if st.button(
                "📅\n\n고령운전자\n월 × 시간",
                key="card_senior_month",
                use_container_width=True,
            ):
                go_senior_month_time()

            st.html(
                """
                <div class="card-desc">
                    월별·시간대별 사고 추세와<br>
                    계절성 분석
                </div>
                """
            )

        with c5:

            if st.button(
                "📍\n\n고령운전자\n지역 × 월",
                key="card_senior_region",
                use_container_width=True,
            ):
                go_senior_region_month()

            st.html(
                """
                <div class="card-desc">
                    지역별 월간 사고 추세와<br>
                    고위험 지역 분석
                </div>
                """
            )


        # ====================================================
        # 3. INTEGRATED TRAFFIC ACCIDENT
        # ====================================================

        st.html(
            """
            <div class="section-title">
                통합 교통사고
            </div>

            <div class="section-sub">
                지역·연령대·기상상태를 기준으로 전체 교통사고를 비교 분석합니다.
            </div>
            """
        )

        c6, c7, c8 = st.columns(
            3,
            gap="medium",
        )

        with c6:

            if st.button(
                "🗺️\n\n지역별\n전체 교통사고",
                key="card_region_total",
                use_container_width=True,
            ):
                go_region_total()

            st.html(
                """
                <div class="card-desc">
                    지역별 사고 수준과<br>
                    연도별 변화 비교
                </div>
                """
            )

        with c7:

            if st.button(
                "👥\n\n연령대별\n전체 교통사고",
                key="card_age_total",
                use_container_width=True,
            ):
                go_age_total()

            st.html(
                """
                <div class="card-desc">
                    전체 연령대 사고 규모와<br>
                    변화 추세 비교
                </div>
                """
            )

        with c8:

            if st.button(
                "🌦️\n\n기상상태별\n교통사고",
                key="card_weather",
                use_container_width=True,
            ):
                go_weather()

            st.html(
                """
                <div class="card-desc">
                    날씨 조건별 사고 규모와<br>
                    연도별 변화 비교
                </div>
                """
            )


    # ========================================================
    # DB STATUS
    # ========================================================

    if db_connected:

        st.html(
            """
            <div class="db-ok">
                ● Aiven MySQL · safe 데이터베이스 연결됨
            </div>
            """
        )

    else:

        st.html(
            """
            <div class="db-error">
                ● MySQL 연결을 확인해주세요.
            </div>
            """
        )