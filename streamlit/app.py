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
    url_path="main",
    default=True,
)


# ============================================================
# PEOPLE MAIN
# ============================================================

people_page = st.Page(
    "pages/people.py",
    title="인구 분석",
    url_path="people",
)


# ============================================================
# PEOPLE SUB
# ============================================================

local_population_page = st.Page(
    "pages/people/local_population.py",
    title="지역별 인구 현황",
    url_path="local-population",
)


resident_population_monthly_page = st.Page(
    "pages/people/resident_population_monthly.py",
    title="주민등록 인구 및 세대 현황",
    url_path="resident-population-monthly",
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
    title="성별 운전면허 현황",
    url_path="license-gender",
)


license_age_page = st.Page(
    "pages/car/license_age.py",
    title="연령별 운전면허 현황",
    url_path="license-age",
)


license_region_page = st.Page(
    "pages/car/license_region.py",
    title="지역별 운전면허 현황",
    url_path="license-region",
)


# ============================================================
# CAR - REGISTRATION
# ============================================================

total_car_page = st.Page(
    "pages/car/total_car.py",
    title="자동차 등록 현황",
    url_path="total-car",
)


registration_year_page = st.Page(
    "pages/car/registration_year.py",
    title="연도별 자동차 등록",
    url_path="registration-year",
)


registration_region_page = st.Page(
    "pages/car/registration_region.py",
    title="지역별 자동차 등록",
    url_path="registration-region",
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
# ACCIDENT SUB
# ============================================================

age_total_page = st.Page(
    "pages/accident/age_total.py",
    title="연령별 교통사고",
    url_path="age-total",
)


driver_age_page = st.Page(
    "pages/accident/driver_age.py",
    title="가해운전자 연령대별 사고",
    url_path="driver-age",
)


driver_age_time_page = st.Page(
    "pages/accident/driver_age_time.py",
    title="가해운전자 연령대·시간대 사고",
    url_path="driver-age-time",
)


region_total_page = st.Page(
    "pages/accident/region_total.py",
    title="지역별 교통사고",
    url_path="region-total",
)


senior_month_time_page = st.Page(
    "pages/accident/senior_month_time.py",
    title="고령운전자 월별·시간대 사고",
    url_path="senior-month-time",
)


senior_region_month_page = st.Page(
    "pages/accident/senior_region_month.py",
    title="고령운전자 지역별·월별 사고",
    url_path="senior-region-month",
)


senior_type_time_page = st.Page(
    "pages/accident/senior_type_time.py",
    title="고령운전자 사고유형·시간대",
    url_path="senior-type-time",
)


weather_page = st.Page(
    "pages/accident/weather.py",
    title="기상상태별 교통사고",
    url_path="weather",
)


# ============================================================
# POLICY MAIN
# ============================================================

policy_page = st.Page(
    "pages/policy.py",
    title="정책·제도",
    url_path="policy",
)


# ============================================================
# POLICY SUB
# 실제 폴더명: streamlit/pages/poli/
# ============================================================

senior_education_page = st.Page(
    "pages/poli/senior_education.py",
    title="고령운전자 교통안전교육",
    url_path="senior-education",
)


senior_policy_page = st.Page(
    "pages/poli/senior_policy.py",
    title="전국 고령운전자 정책",
    url_path="senior-policy",
)


senior_safety_policy_page = st.Page(
    "pages/poli/senior_safety_policy.py",
    title="지역 특화 고령운전자 안전정책",
    url_path="senior-safety-policy",
)


license_return_policy_page = st.Page(
    "pages/poli/license_return_policy.py",
    title="운전면허 자진반납 지원정책",
    url_path="license-return-policy",
)


license_return_guide_page = st.Page(
    "pages/poli/license_return_guide.py",
    title="운전면허 자진반납 방법",
    url_path="license-return-guide",
)


# ============================================================
# POLICY - LICENSE RETURN COMPARE
# 자동차 → 제도 영역으로 이동
# ============================================================

return_compare_page = st.Page(
    "pages/poli/return_compare.py",
    title="운전면허 자진반납 비교",
    url_path="return-compare",
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
            car_page,

            # 운전면허
            license_gender_page,
            license_age_page,
            license_region_page,

            # 자동차 등록
            total_car_page,
            registration_year_page,
            registration_region_page,
        ],


        # ====================================================
        # ACCIDENT
        # ====================================================

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


        # ====================================================
        # POLICY
        # ====================================================

        "정책·제도": [
            policy_page,

            license_return_guide_page,

            senior_education_page,

            senior_policy_page,
            senior_safety_policy_page,

            license_return_policy_page,

            return_compare_page,
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