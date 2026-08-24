# ============================================================
# streamlit/app.py
# SAFER - Main Navigation
# ============================================================

import streamlit as st


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="SAFER",
    page_icon="🚘",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# MAIN
# ============================================================

main_page = st.Page(
    "main.py",
    title="SAFER",
    url_path="main",
)


# ============================================================
# PEOPLE
# ============================================================

people_page = st.Page(
    "pages/people.py",
    title="인구 분석",
    url_path="people",
)


local_population_page = st.Page(
    "pages/people/local_population.py",
    title="지역별 인구 현황",
    url_path="local_population",
)


resident_population_monthly_page = st.Page(
    "pages/people/resident_population_monthly.py",
    title="주민등록 인구 현황",
    url_path="resident_population_monthly",
)


# ============================================================
# CAR MAIN
# ============================================================

car_page = st.Page(
    "pages/car.py",
    title="자동차 분석",
    url_path="car",
)


# ============================================================
# CAR - LICENSE
# ============================================================

license_gender_page = st.Page(
    "pages/car/license_gender.py",
    title="성별 운전면허 소지자 현황",
    url_path="license_gender",
)


license_age_page = st.Page(
    "pages/car/license_age.py",
    title="연령별 운전면허 소지자 현황",
    url_path="license_age",
)


license_region_page = st.Page(
    "pages/car/license_region.py",
    title="지역별 운전면허 소지자 현황",
    url_path="license_region",
)


# ============================================================
# CAR - RETURN LICENSE
# ============================================================

return_2023_page = st.Page(
    "pages/car/return_2023.py",
    title="2023 운전면허 자진반납",
    url_path="return_2023",
)


return_2025_page = st.Page(
    "pages/car/return_2025.py",
    title="2025 운전면허 자진반납",
    url_path="return_2025",
)


return_compare_page = st.Page(
    "pages/car/return_compare.py",
    title="2023·2025 자진반납 비교",
    url_path="return_compare",
)


# ============================================================
# CAR - REGISTRATION
# ============================================================

total_car_page = st.Page(
    "pages/car/total_car.py",
    title="전체 자동차 등록 현황",
    url_path="total_car",
)


registration_year_page = st.Page(
    "pages/car/registration_year.py",
    title="연도별 자동차 등록 현황",
    url_path="registration_year",
)


registration_region_page = st.Page(
    "pages/car/registration_region.py",
    title="지역별 자동차 등록 현황",
    url_path="registration_region",
)


# ============================================================
# ACCIDENT MAIN
# ============================================================

accident_page = st.Page(
    "pages/accident.py",
    title="교통사고 분석",
    url_path="accident",
)


# ============================================================
# ACCIDENT - AGE TOTAL
# ============================================================

age_total_page = st.Page(
    "pages/accident/age_total.py",
    title="연령별 교통사고 분석",
    url_path="age_total",
)


# ============================================================
# ACCIDENT - DRIVER AGE
# ============================================================

driver_age_page = st.Page(
    "pages/accident/driver_age.py",
    title="가해운전자 연령대별 사고",
    url_path="driver_age",
)


# ============================================================
# ACCIDENT - DRIVER AGE TIME
# ============================================================

driver_age_time_page = st.Page(
    "pages/accident/driver_age_time.py",
    title="가해운전자 연령대·시간대 사고",
    url_path="driver_age_time",
)


# ============================================================
# ACCIDENT - REGION TOTAL
# ============================================================

region_total_page = st.Page(
    "pages/accident/region_total.py",
    title="지역별 교통사고 분석",
    url_path="region_total",
)


# ============================================================
# ACCIDENT - SENIOR MONTH TIME
# ============================================================

senior_month_time_page = st.Page(
    "pages/accident/senior_month_time.py",
    title="고령운전자 월별·시간대 사고",
    url_path="senior_month_time",
)


# ============================================================
# ACCIDENT - SENIOR REGION MONTH
# ============================================================

senior_region_month_page = st.Page(
    "pages/accident/senior_region_month.py",
    title="고령운전자 지역별·월별 사고",
    url_path="senior_region_month",
)


# ============================================================
# ACCIDENT - SENIOR TYPE TIME
# ============================================================

senior_type_time_page = st.Page(
    "pages/accident/senior_type_time.py",
    title="고령운전자 사고유형·시간대 분석",
    url_path="senior_type_time",
)


# ============================================================
# ACCIDENT - WEATHER
# ============================================================

weather_page = st.Page(
    "pages/accident/weather.py",
    title="기상상태별 교통사고 분석",
    url_path="accident_weather",
)


# ============================================================
# POLICY
# ============================================================

policy_page = st.Page(
    "pages/policy.py",
    title="제도 분석",
    url_path="policy",
)


# ============================================================
# FAQ
# ============================================================

faq_page = st.Page(
    "pages/FAQ.py",
    title="FAQ",
    url_path="faq",
)


# ============================================================
# NAVIGATION
# ============================================================

pg = st.navigation(
    {

        # ====================================================
        # MAIN
        # ====================================================

        "SAFER": [
            main_page,
        ],


        # ====================================================
        # PEOPLE
        # ====================================================

        "인구": [

            people_page,

            local_population_page,

            resident_population_monthly_page,

        ],


        # ====================================================
        # CAR
        # ====================================================

        "자동차": [

            # 자동차 메인
            car_page,


            # 운전면허
            license_gender_page,
            license_age_page,
            license_region_page,


            # 자진반납
            return_2023_page,
            return_2025_page,
            return_compare_page,


            # 자동차 등록
            total_car_page,
            registration_year_page,
            registration_region_page,

        ],


        # ====================================================
        # ACCIDENT
        # ====================================================

        "교통사고": [

            # 메인
            accident_page,


            # 연령
            age_total_page,
            driver_age_page,
            driver_age_time_page,


            # 지역
            region_total_page,


            # 고령운전자
            senior_month_time_page,
            senior_region_month_page,
            senior_type_time_page,


            # 기상
            weather_page,

        ],


        # ====================================================
        # POLICY
        # ====================================================

        "제도": [
            policy_page,
        ],


        # ====================================================
        # FAQ
        # ====================================================

        "FAQ": [
            faq_page,
        ],

    },

    position="hidden",
)


# ============================================================
# RUN
# ============================================================

pg.run()