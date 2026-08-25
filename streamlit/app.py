import streamlit as st


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
# MAIN
# ============================================================

main_page = st.Page(
    "main.py",
    title="SAFER",
    icon="🏠",
    default=True,
)


# ============================================================
# MAIN CATEGORY PAGES
# ============================================================

people_page = st.Page(
    "pages/people.py",
    title="인구",
    icon="👥",
)

car_page = st.Page(
    "pages/car.py",
    title="자동차",
    icon="🚗",
)

accident_page = st.Page(
    "pages/accident.py",
    title="교통사고",
    icon="⚠️",
)

policy_page = st.Page(
    "pages/policy.py",
    title="제도",
    icon="📋",
)

faq_page = st.Page(
    "pages/FAQ.py",
    title="FAQ",
    icon="❓",
)


# ============================================================
# FUTURE FORECAST
# ============================================================

forecast_page = st.Page(
    "pages/forecast.py",
    title="미래 전망 예측",
    icon="📈",
    url_path="forecast",
)


# ============================================================
# PEOPLE DETAIL
# ============================================================

local_population_page = st.Page(
    "pages/people/local_population.py",
    title="지역별 인구 현황",
)

resident_population_monthly_page = st.Page(
    "pages/people/resident_population_monthly.py",
    title="주민등록 인구 현황",
)


# ============================================================
# CAR DETAIL
# ============================================================

total_car_page = st.Page(
    "pages/car/total_car.py",
    title="전국 자동차 등록 현황",
)

registration_year_page = st.Page(
    "pages/car/registration_year.py",
    title="연도별 자동차 등록 현황",
)

registration_region_page = st.Page(
    "pages/car/registration_region.py",
    title="지역별 자동차 등록 현황",
)

license_gender_page = st.Page(
    "pages/car/license_gender.py",
    title="성별 운전면허 소지자",
)

license_age_page = st.Page(
    "pages/car/license_age.py",
    title="연령별 운전면허 소지자",
)

license_region_page = st.Page(
    "pages/car/license_region.py",
    title="지역별 운전면허 소지자",
)

return_2023_page = st.Page(
    "pages/car/return_2023.py",
    title="2023 운전면허 자진반납 현황",
)

return_2025_page = st.Page(
    "pages/car/return_2025.py",
    title="2025 운전면허 자진반납 현황",
)


# ============================================================
# ACCIDENT DETAIL
# ============================================================

age_total_page = st.Page(
    "pages/accident/age_total.py",
    title="연령대별 교통사고",
)

driver_age_page = st.Page(
    "pages/accident/driver_age.py",
    title="가해운전자 연령대별 사고",
)

driver_age_time_page = st.Page(
    "pages/accident/driver_age_time.py",
    title="가해운전자 연령대·시간대 사고",
)

region_total_page = st.Page(
    "pages/accident/region_total.py",
    title="지역별 교통사고",
)

senior_month_time_page = st.Page(
    "pages/accident/senior_month_time.py",
    title="고령운전자 월별·시간대 사고",
)

senior_region_month_page = st.Page(
    "pages/accident/senior_region_month.py",
    title="고령운전자 지역별·월별 사고",
)

senior_type_time_page = st.Page(
    "pages/accident/senior_type_time.py",
    title="고령운전자 사고유형·시간대",
)

weather_page = st.Page(
    "pages/accident/weather.py",
    title="기상상태별 교통사고",
)


# ============================================================
# POLICY DETAIL
# ============================================================

license_return_guide_page = st.Page(
    "pages/poli/license_return_guide.py",
    title="운전면허 자진반납 안내",
)

license_return_policy_page = st.Page(
    "pages/poli/license_return_policy.py",
    title="운전면허 자진반납 정책",
)

policy_compare_page = st.Page(
    "pages/poli/policy_compare.py",
    title="정책 비교",
)

return_compare_page = st.Page(
    "pages/poli/return_compare.py",
    title="자진반납 정책 비교",
)

senior_education_page = st.Page(
    "pages/poli/senior_education.py",
    title="고령운전자 교육 현황",
)

senior_policy_page = st.Page(
    "pages/poli/senior_policy.py",
    title="전국 고령운전자 정책",
)

senior_safety_policy_page = st.Page(
    "pages/poli/senior_safety_policy.py",
    title="지역 특화 고령운전자 정책",
)


# ============================================================
# NAVIGATION
#
# position="hidden"
# Streamlit 기본 navigation/sidebar는 숨기고
# 각 페이지에서 만든 SAFER 상단 메뉴를 사용
#
# st.switch_page()로 이동하려는 파일은
# 반드시 여기에 등록되어 있어야 함
# ============================================================

pages = {

    # --------------------------------------------------------
    # MAIN
    # --------------------------------------------------------
    "메인": [
        main_page,
    ],


    # --------------------------------------------------------
    # PEOPLE
    # --------------------------------------------------------
    "인구": [
        people_page,
        local_population_page,
        resident_population_monthly_page,
    ],


    # --------------------------------------------------------
    # CAR
    # --------------------------------------------------------
    "자동차": [
        car_page,
        total_car_page,
        registration_year_page,
        registration_region_page,
        license_gender_page,
        license_age_page,
        license_region_page,
        return_2023_page,
        return_2025_page,
    ],


    # --------------------------------------------------------
    # ACCIDENT
    # --------------------------------------------------------
    "교통사고": [
        accident_page,
        age_total_page,
        driver_age_page,
        driver_age_time_page,
        region_total_page,
        senior_month_time_page,
        senior_region_month_page,
        senior_type_time_page,
        weather_page,
    ],


    # --------------------------------------------------------
    # POLICY
    # --------------------------------------------------------
    "제도": [
        policy_page,
        license_return_guide_page,
        license_return_policy_page,
        policy_compare_page,
        return_compare_page,
        senior_education_page,
        senior_policy_page,
        senior_safety_policy_page,
    ],


    # --------------------------------------------------------
    # FAQ
    # --------------------------------------------------------
    "FAQ": [
        faq_page,
    ],


    # --------------------------------------------------------
    # FUTURE FORECAST
    # --------------------------------------------------------
    "미래 전망": [
        forecast_page,
    ],
}


# ============================================================
# RUN NAVIGATION
# ============================================================

pg = st.navigation(
    pages,
    position="hidden",
)

pg.run()