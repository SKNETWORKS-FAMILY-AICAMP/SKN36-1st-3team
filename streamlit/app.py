import sys
from pathlib import Path

import streamlit as st


# ============================================================
# PROJECT ROOT
# ============================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="SAFER",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# PAGE 등록
# ============================================================

pages = {

    "SAFER": [

        st.Page(
            "main.py",
            title="메인",
            default=True,
        ),

        st.Page(
            "pages/people.py",
            title="인구",
        ),

        st.Page(
            "pages/car.py",
            title="자동차",
        ),

        st.Page(
            "pages/accident.py",
            title="교통사고",
        ),

        st.Page(
            "pages/policy.py",
            title="제도",
        ),

        st.Page(
            "pages/FAQ.py",
            title="FAQ",
        ),
    ],


    # ========================================================
    # 교통사고 상세 페이지
    # ========================================================

    "교통사고 분석": [

        st.Page(
            "pages/accident/driver_age.py",
            title="가해운전자 연령대별",
        ),

        st.Page(
            "pages/accident/driver_age_time.py",
            title="가해운전자 연령 × 시간",
        ),

        st.Page(
            "pages/accident/weather.py",
            title="기상상태별 사고",
        ),

        st.Page(
            "pages/accident/senior_type_time.py",
            title="고령운전자 사고유형 × 시간",
        ),

        st.Page(
            "pages/accident/senior_month_time.py",
            title="고령운전자 월 × 시간",
        ),

        st.Page(
            "pages/accident/senior_region_month.py",
            title="고령운전자 지역 × 월",
        ),

        st.Page(
            "pages/accident/age_total.py",
            title="연령대별 전체 사고",
        ),

        st.Page(
            "pages/accident/region_total.py",
            title="지역별 전체 사고",
        ),
    ],
}


# ============================================================
# NAVIGATION
# ============================================================

pg = st.navigation(
    pages,
    position="hidden",
)


pg.run()