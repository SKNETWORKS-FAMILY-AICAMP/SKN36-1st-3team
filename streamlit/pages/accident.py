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