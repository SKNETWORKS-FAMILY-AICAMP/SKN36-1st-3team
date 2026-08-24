# ============================================================
# streamlit/pages/car.py
# SAFER - 자동차·운전면허 분석 메인 페이지
# ============================================================

import streamlit as st


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
# CSS
# ============================================================

st.html(
    """
<style>

/* ==========================================================
   전체 배경
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
   상단 NAV
========================================================== */

.st-key-top_nav {

    background:
        rgba(255,255,255,.98);

    border-radius: 16px;

    padding:
        10px 20px;

    margin-bottom: 28px;

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


/* 로고 */

.st-key-nav_logo button {

    color:
        #27314C !important;

    font-size:
        30px !important;

    font-weight:
        900 !important;

    justify-content:
        flex-start !important;

    padding-left:
        0 !important;
}


/* 현재 자동차 메뉴 */

.st-key-nav_car button {

    color:
        #D6A348 !important;

    font-weight:
        800 !important;
}


/* 미래 전망 */

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
   MAIN PAGE
========================================================== */

.st-key-car_page {

    background:
        #101625;

    border:
        1px solid
        #34405A;

    border-radius:
        20px;

    padding:
        34px 34px 48px 34px;

    box-shadow:
        0 12px 36px
        rgba(0,0,0,.18);
}


/* ==========================================================
   HEADER
========================================================== */

.page-eyebrow {

    color:
        #D6A348;

    font-size:
        13px;

    font-weight:
        900;

    letter-spacing:
        1.6px;

    margin-bottom:
        10px;
}


.page-title {

    color:
        #FFFFFF;

    font-size:
        42px;

    line-height:
        1.15;

    font-weight:
        900;

    letter-spacing:
        -2px;

    margin-bottom:
        13px;
}


.page-description {

    color:
        #AEB7C8;

    font-size:
        15px;

    line-height:
        1.8;

    margin-bottom:
        25px;
}


/* ==========================================================
   CATEGORY PILLS
========================================================== */

.category-pill {

    display:
        inline-block;

    padding:
        8px 15px;

    margin-right:
        8px;

    background:
        #171F33;

    color:
        #B7C0D0;

    border:
        1px solid
        #3B465F;

    border-radius:
        999px;

    font-size:
        12px;

    font-weight:
        600;
}


/* ==========================================================
   SECTION
========================================================== */

.analysis-title {

    color:
        #FFFFFF;

    font-size:
        23px;

    font-weight:
        800;

    margin-top:
        42px;

    margin-bottom:
        5px;
}


.analysis-description {

    color:
        #8995A9;

    font-size:
        13px;

    margin-bottom:
        26px;
}


/* ==========================================================
   CARD
========================================================== */

.st-key-card_license_gender button,
.st-key-card_license_age button,
.st-key-card_license_region button,
.st-key-card_return_2023 button,
.st-key-card_return_2025 button,
.st-key-card_return_compare button,
.st-key-card_total_car button,
.st-key-card_registration_year button,
.st-key-card_registration_region button {

    width:
        100% !important;

    min-height:
        165px !important;

    background:
        #192136 !important;

    border:
        1px solid
        #3A4661 !important;

    border-radius:
        22px !important;

    color:
        #FFFFFF !important;

    font-size:
        16px !important;

    font-weight:
        800 !important;

    line-height:
        1.55 !important;

    box-shadow:
        none !important;

    transition:
        transform .18s ease,
        background .18s ease,
        border-color .18s ease !important;
}


.st-key-card_license_gender button:hover,
.st-key-card_license_age button:hover,
.st-key-card_license_region button:hover,
.st-key-card_return_2023 button:hover,
.st-key-card_return_2025 button:hover,
.st-key-card_return_compare button:hover,
.st-key-card_total_car button:hover,
.st-key-card_registration_year button:hover,
.st-key-card_registration_region button:hover {

    transform:
        translateY(-4px);

    background:
        #202A43 !important;

    border-color:
        #D6A348 !important;
}


/* ==========================================================
   카드별 상단 컬러
========================================================== */

.st-key-card_license_gender button {
    border-top:
        5px solid #79B69B !important;
}


.st-key-card_license_age button {
    border-top:
        5px solid #88A8CF !important;
}


.st-key-card_license_region button {
    border-top:
        5px solid #A58AC8 !important;
}


.st-key-card_return_2023 button {
    border-top:
        5px solid #D2A653 !important;
}


.st-key-card_return_2025 button {
    border-top:
        5px solid #C57B5E !important;
}


.st-key-card_return_compare button {
    border-top:
        5px solid #E2BA58 !important;
}


/* 전체 자동차 */

.st-key-card_total_car button {
    border-top:
        5px solid #C78C72 !important;
}


/* 연도별 자동차 */

.st-key-card_registration_year button {
    border-top:
        5px solid #83B39E !important;
}


/* 지역별 자동차 */

.st-key-card_registration_region button {
    border-top:
        5px solid #85AEB8 !important;
}


/* ==========================================================
   CARD DESCRIPTION
========================================================== */

.card-description {

    text-align:
        center;

    color:
        #8290A6;

    font-size:
        12px;

    line-height:
        1.65;

    min-height:
        48px;

    margin-top:
        8px;

    margin-bottom:
        25px;
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


    # --------------------------------------------------------
    # LOGO
    # --------------------------------------------------------

    with logo:

        if st.button(
            "SAFER",
            key="nav_logo"
        ):
            go_main()


    # --------------------------------------------------------
    # PEOPLE
    # --------------------------------------------------------

    with n1:

        if st.button(
            "인구",
            key="nav_people",
            use_container_width=True
        ):
            go_people()


    # --------------------------------------------------------
    # CAR
    # --------------------------------------------------------

    with n2:

        if st.button(
            "자동차",
            key="nav_car",
            use_container_width=True
        ):
            go_car()


    # --------------------------------------------------------
    # ACCIDENT
    # --------------------------------------------------------

    with n3:

        if st.button(
            "교통사고",
            key="nav_accident",
            use_container_width=True
        ):
            go_accident()


    # --------------------------------------------------------
    # POLICY
    # --------------------------------------------------------

    with n4:

        if st.button(
            "제도",
            key="nav_policy",
            use_container_width=True
        ):
            go_policy()


    # --------------------------------------------------------
    # FAQ
    # --------------------------------------------------------

    with n5:

        if st.button(
            "FAQ",
            key="nav_faq",
            use_container_width=True
        ):
            go_faq()


    # --------------------------------------------------------
    # FUTURE
    # --------------------------------------------------------

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
# MAIN
# ============================================================

with st.container(
    key="car_page"
):

    # ========================================================
    # HEADER
    # ========================================================

    st.html(
        """
        <div class="page-eyebrow">
            SAFER DATA ANALYTICS
        </div>

        <div class="page-title">
            자동차·운전면허 분석
        </div>

        <div class="page-description">
            운전면허 보유 현황, 고령운전자 자진반납,
            자동차 등록 데이터를 통해 지역별 자동차·운전자 특성을 분석합니다.
        </div>

        <div>
            <span class="category-pill">
                운전면허
            </span>

            <span class="category-pill">
                자진반납
            </span>

            <span class="category-pill">
                자동차 등록
            </span>
        </div>
        """
    )


    # ========================================================
    # ANALYSIS TITLE
    # ========================================================

    st.html(
        """
        <div class="analysis-title">
            분석 항목
        </div>

        <div class="analysis-description">
            분석할 자동차·운전면허 데이터셋을 선택하세요.
        </div>
        """
    )


    # ========================================================
    # ROW 1
    # 운전면허
    # ========================================================

    col1, col2, col3 = st.columns(
        3,
        gap="large"
    )


    # --------------------------------------------------------
    # 성별 면허
    # --------------------------------------------------------

    with col1:

        if st.button(
            "👥\n\n운전면허소지자\n성별 분석",
            key="card_license_gender",
            use_container_width=True
        ):

            st.switch_page(
                "pages/car/license_gender.py"
            )


        st.html(
            """
            <div class="card-description">
                성별 면허 보유 규모와<br>
                인구 대비 면허 보유 특성 분석
            </div>
            """
        )


    # --------------------------------------------------------
    # 연령별 면허
    # --------------------------------------------------------

    with col2:

        if st.button(
            "🧓\n\n운전면허소지자\n연령대별 분석",
            key="card_license_age",
            use_container_width=True
        ):

            st.switch_page(
                "pages/car/license_age.py"
            )


        st.html(
            """
            <div class="card-description">
                연령대별 운전자 규모와<br>
                고령운전자 증가 추세 분석
            </div>
            """
        )


    # --------------------------------------------------------
    # 지역별 면허
    # --------------------------------------------------------

    with col3:

        if st.button(
            "📍\n\n운전면허소지자\n지역별 분석",
            key="card_license_region",
            use_container_width=True
        ):

            st.switch_page(
                "pages/car/license_region.py"
            )


        st.html(
            """
            <div class="card-description">
                지역별 면허 보유자와<br>
                고령운전자 분포 분석
            </div>
            """
        )


    # ========================================================
    # ROW 2
    # 자진반납
    # ========================================================

    col4, col5, col6 = st.columns(
        3,
        gap="large"
    )


    # --------------------------------------------------------
    # 2023
    # --------------------------------------------------------

    with col4:

        if st.button(
            "📄\n\n운전면허 자진반납\n2023",
            key="card_return_2023",
            use_container_width=True
        ):

            st.switch_page(
                "pages/car/return_2023.py"
            )


        st.html(
            """
            <div class="card-description">
                2023년 지역·연령별<br>
                운전면허 자진반납 분석
            </div>
            """
        )


    # --------------------------------------------------------
    # 2025
    # --------------------------------------------------------

    with col5:

        if st.button(
            "📄\n\n운전면허 자진반납\n2025",
            key="card_return_2025",
            use_container_width=True
        ):

            st.switch_page(
                "pages/car/return_2025.py"
            )


        st.html(
            """
            <div class="card-description">
                2025년 지역·연령별<br>
                운전면허 자진반납 분석
            </div>
            """
        )


    # --------------------------------------------------------
    # 비교
    # --------------------------------------------------------

    with col6:

        if st.button(
            "📊\n\n자진반납\n2023 ↔ 2025 비교",
            key="card_return_compare",
            use_container_width=True
        ):

            st.switch_page(
                "pages/car/return_compare.py"
            )


        st.html(
            """
            <div class="card-description">
                지역·연령별 증감과<br>
                자진반납 변화율 비교
            </div>
            """
        )


    # ========================================================
    # ROW 3
    # 자동차 등록
    # ========================================================

    col7, col8, col9 = st.columns(
        3,
        gap="large"
    )


    # --------------------------------------------------------
    # 전체 자동차 등록 현황
    # --------------------------------------------------------

    with col7:

        if st.button(
            "🚘\n\n전체 자동차\n등록 현황",
            key="card_total_car",
            use_container_width=True
        ):

            st.switch_page(
                "pages/car/total_car.py"
            )


        st.html(
            """
            <div class="card-description">
                지역·차종·용도별<br>
                자동차 등록 종합 분석
            </div>
            """
        )


    # --------------------------------------------------------
    # 연도별 자동차 등록
    # --------------------------------------------------------

    with col8:

        if st.button(
            "🚗\n\n자동차 등록\n연도별 현황",
            key="card_registration_year",
            use_container_width=True
        ):

            st.switch_page(
                "pages/car/registration_year.py"
            )


        st.html(
            """
            <div class="card-description">
                연도별 자동차 등록대수와<br>
                등록 변화 추이 분석
            </div>
            """
        )


    # --------------------------------------------------------
    # 지역별 자동차 등록
    # --------------------------------------------------------

    with col9:

        if st.button(
            "🌎\n\n자동차 등록\n지역별 현황",
            key="card_registration_region",
            use_container_width=True
        ):

            st.switch_page(
                "pages/car/registration_region.py"
            )


        st.html(
            """
            <div class="card-description">
                지역별 자동차 등록 규모와<br>
                공간적 분포 비교
            </div>
            """
        )