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
# CAR DETAIL PAGE MOVE
# ============================================================

def go_license_gender():
    st.switch_page("pages/car/license_gender.py")


def go_license_age():
    st.switch_page("pages/car/license_age.py")


def go_license_region():
    st.switch_page("pages/car/license_region.py")


def go_return_2023():
    st.switch_page("pages/car/return_2023.py")


def go_return_2025():
    st.switch_page("pages/car/return_2025.py")


def go_return_compare():
    st.switch_page("pages/car/return_compare.py")


def go_return_policy_region():
    st.switch_page("pages/car/return_policy_region.py")


def go_registration_year():
    st.switch_page("pages/car/registration_year.py")


def go_registration_region():
    st.switch_page("pages/car/registration_region.py")


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
   NAVBAR
========================================================== */

.st-key-top_nav {

    background: rgba(255,255,255,.98);

    border-radius: 16px;

    padding: 10px 20px;

    margin-bottom: 18px;

    box-shadow:
        0 5px 20px
        rgba(0,0,0,.10);
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

    transition: all .15s ease !important;
}


.st-key-top_nav button:hover {

    background: transparent !important;

    color: #D6A348 !important;
}


/* ==========================================================
   SAFER LOGO
========================================================== */

.st-key-nav_logo button {

    color: #27314C !important;

    font-size: 28px !important;

    font-weight: 900 !important;

    justify-content: flex-start !important;

    padding-left: 0 !important;

    letter-spacing: -1px !important;
}


/* ==========================================================
   ACTIVE NAV
========================================================== */

.st-key-nav_car button {

    color: #D6A348 !important;

    font-weight: 800 !important;
}


/* ==========================================================
   FUTURE BUTTON
========================================================== */

.st-key-nav_future button {

    background: #D9A64A !important;

    color: #172035 !important;

    font-weight: 800 !important;

    border-radius: 1px !important;

    padding-left: 18px !important;
    padding-right: 18px !important;
}


.st-key-nav_future button:hover {

    background: #C9973C !important;

    color: #172035 !important;
}


/* ==========================================================
   PAGE
========================================================== */

.st-key-car_page {

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

.car-path {

    color: #D6A348;

    font-size: 11px;

    font-weight: 800;

    letter-spacing: 1.5px;

    margin-bottom: 9px;
}


.car-title {

    color: #FFFFFF;

    font-size: 38px;

    font-weight: 900;

    letter-spacing: -2px;

    line-height: 1.15;

    margin-bottom: 10px;
}


.car-sub {

    color: #929AAC;

    font-size: 13px;

    line-height: 1.6;

    margin-bottom: 28px;
}


/* ==========================================================
   CATEGORY BADGES
========================================================== */

.category-row {

    display: flex;

    gap: 8px;

    margin-top: 5px;

    margin-bottom: 34px;
}


.category-badge {

    background: #192136;

    color: #A3ABBA;

    border:
        1px solid
        #39445D;

    border-radius: 50px;

    padding:
        7px 14px;

    font-size: 10px;
}


/* ==========================================================
   SECTION
========================================================== */

.section-title {

    color: white;

    font-size: 19px;

    font-weight: 800;

    margin-top: 8px;

    margin-bottom: 5px;
}


.section-sub {

    color: #7F899B;

    font-size: 11px;

    margin-bottom: 20px;
}


/* ==========================================================
   ANALYSIS CARDS
========================================================== */

.st-key-car_cards button {

    width: 100% !important;

    height: 165px !important;

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


.st-key-car_cards button:hover {

    transform: translateY(-4px);

    border-color: #D6A348 !important;

    box-shadow:
        0 13px 25px
        rgba(0,0,0,.22) !important;
}


/* ==========================================================
   CARD ACCENTS
========================================================== */

.st-key-card_license_gender button {
    border-top: 5px solid #69B895 !important;
}


.st-key-card_license_age button {
    border-top: 5px solid #85A7C7 !important;
}


.st-key-card_license_region button {
    border-top: 5px solid #9C82BF !important;
}


.st-key-card_return_2023 button {
    border-top: 5px solid #D3A24A !important;
}


.st-key-card_return_2025 button {
    border-top: 5px solid #C76A4F !important;
}


.st-key-card_return_compare button {

    border-top:
        5px solid
        #E9BD55 !important;

    background:
        linear-gradient(
            145deg,
            #1B243A,
            #242943
        ) !important;
}


.st-key-card_return_policy button {
    border-top: 5px solid #CB866B !important;
}


.st-key-card_registration_year button {
    border-top: 5px solid #70B29A !important;
}


.st-key-card_registration_region button {
    border-top: 5px solid #6AA8B4 !important;
}


/* ==========================================================
   DESCRIPTION
========================================================== */

.card-desc {

    color: #7E8799;

    text-align: center;

    font-size: 10px;

    line-height: 1.45;

    margin-top: -7px;

    margin-bottom: 18px;
}


/* ==========================================================
   DATA INFO
========================================================== */

.data-info {

    margin-top: 26px;

    padding-top: 18px;

    border-top:
        1px solid
        #252F46;

    color: #798296;

    font-size: 10px;

    line-height: 1.7;
}


/* ==========================================================
   RESPONSIVE
========================================================== */

@media(max-width: 1000px) {

    .car-title {
        font-size: 30px;
    }

    .st-key-car_page {
        padding: 20px;
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
        gap="small",
    )


    # --------------------------------------------------------
    # SAFER
    # --------------------------------------------------------

    with logo:

        if st.button(
            "SAFER",
            key="nav_logo",
        ):
            go_main()


    # --------------------------------------------------------
    # 인구
    # --------------------------------------------------------

    with n1:

        if st.button(
            "인구",
            key="nav_people",
            use_container_width=True,
        ):
            go_people()


    # --------------------------------------------------------
    # 자동차
    # --------------------------------------------------------

    with n2:

        if st.button(
            "자동차",
            key="nav_car",
            use_container_width=True,
        ):
            go_car()


    # --------------------------------------------------------
    # 교통사고
    # --------------------------------------------------------

    with n3:

        if st.button(
            "교통사고",
            key="nav_accident",
            use_container_width=True,
        ):
            go_accident()


    # --------------------------------------------------------
    # 제도
    # --------------------------------------------------------

    with n4:

        if st.button(
            "제도",
            key="nav_policy",
            use_container_width=True,
        ):
            go_policy()


    # --------------------------------------------------------
    # FAQ
    # --------------------------------------------------------

    with n5:

        if st.button(
            "FAQ",
            key="nav_faq",
            use_container_width=True,
        ):
            go_faq()


    # --------------------------------------------------------
    # 미래전망
    # --------------------------------------------------------

    with nf:

        if st.button(
            "미래 전망 예측하기 ▶",
            key="nav_future",
            use_container_width=True,
        ):

            st.toast(
                "미래 전망 페이지는 준비 중입니다.",
                icon="📈",
            )


# ============================================================
# CAR PAGE
# ============================================================

with st.container(
    key="car_page"
):

    # ========================================================
    # HEADER
    # ========================================================

    st.html(
        """
        <div class="car-path">
            SAFER DATA ANALYTICS
        </div>

        <div class="car-title">
            자동차 · 운전면허 분석
        </div>

        <div class="car-sub">
            운전면허 보유 현황, 고령운전자 자진반납,
            자동차 등록 데이터를 통해 지역별 자동차·운전자 특성을 분석합니다.
        </div>

        <div class="category-row">

            <div class="category-badge">
                운전면허
            </div>

            <div class="category-badge">
                자진반납
            </div>

            <div class="category-badge">
                자동차 등록
            </div>

        </div>
        """
    )


    # ========================================================
    # SECTION
    # ========================================================

    st.html(
        """
        <div class="section-title">
            분석 항목
        </div>

        <div class="section-sub">
            분석할 자동차·운전면허 데이터셋을 선택하세요.
        </div>
        """
    )


    # ========================================================
    # CARDS
    # ========================================================

    with st.container(
        key="car_cards"
    ):

        # ====================================================
        # ROW 1
        # ====================================================

        c1, c2, c3 = st.columns(
            3,
            gap="medium",
        )


        # ====================================================
        # 1. LICENSE GENDER
        # ====================================================

        with c1:

            if st.button(
                "👥\n\n운전면허소지자\n성별 분석",
                key="card_license_gender",
                use_container_width=True,
            ):

                go_license_gender()


            st.html(
                """
                <div class="card-desc">
                    성별 면허 보유 규모와<br>
                    연도별 변화 분석
                </div>
                """
            )


        # ====================================================
        # 2. LICENSE AGE
        # ====================================================

        with c2:

            if st.button(
                "🎂\n\n운전면허소지자\n연령대별 분석",
                key="card_license_age",
                use_container_width=True,
            ):

                go_license_age()


            st.html(
                """
                <div class="card-desc">
                    연령대별 운전자 규모와<br>
                    고령운전자 증가 추세 분석
                </div>
                """
            )


        # ====================================================
        # 3. LICENSE REGION
        # ====================================================

        with c3:

            if st.button(
                "📍\n\n운전면허소지자\n지역별 분석",
                key="card_license_region",
                use_container_width=True,
            ):

                go_license_region()


            st.html(
                """
                <div class="card-desc">
                    지역별 면허 보유자와<br>
                    고령운전자 분포 분석
                </div>
                """
            )


        # ====================================================
        # ROW 2
        # ====================================================

        c4, c5, c6 = st.columns(
            3,
            gap="medium",
        )


        # ====================================================
        # 4. RETURN 2023
        # ====================================================

        with c4:

            if st.button(
                "📄\n\n운전면허 자진반납\n2023",
                key="card_return_2023",
                use_container_width=True,
            ):

                go_return_2023()


            st.html(
                """
                <div class="card-desc">
                    2023년 지역·연령별<br>
                    운전면허 자진반납 분석
                </div>
                """
            )


        # ====================================================
        # 5. RETURN 2025
        # ====================================================

        with c5:

            if st.button(
                "📄\n\n운전면허 자진반납\n2025",
                key="card_return_2025",
                use_container_width=True,
            ):

                go_return_2025()


            st.html(
                """
                <div class="card-desc">
                    2025년 지역·연령별<br>
                    운전면허 자진반납 분석
                </div>
                """
            )


        # ====================================================
        # 6. COMPARE
        # ====================================================

        with c6:

            if st.button(
                "📊\n\n자진반납\n2023 ↔ 2025 비교",
                key="card_return_compare",
                use_container_width=True,
            ):

                go_return_compare()


            st.html(
                """
                <div class="card-desc">
                    지역·연령별 증감과<br>
                    자진반납 변화율 비교
                </div>
                """
            )


        # ====================================================
        # ROW 3
        # ====================================================

        c7, c8, c9 = st.columns(
            3,
            gap="medium",
        )


        # ====================================================
        # 7. RETURN REGION
        # ====================================================

        with c7:

            if st.button(
                "🗺️\n\n자진반납\n지역별 종합 현황",
                key="card_return_policy",
                use_container_width=True,
            ):

                go_return_policy_region()


            st.html(
                """
                <div class="card-desc">
                    지역별 면허 반납 규모와<br>
                    정책 활용 현황 비교
                </div>
                """
            )


        # ====================================================
        # 8. REGISTRATION YEAR
        # ====================================================

        with c8:

            if st.button(
                "🚗\n\n자동차 등록\n연도별 현황",
                key="card_registration_year",
                use_container_width=True,
            ):

                go_registration_year()


            st.html(
                """
                <div class="card-desc">
                    차종·용도별 등록대수와<br>
                    장기 변화 추세 분석
                </div>
                """
            )


        # ====================================================
        # 9. REGISTRATION REGION
        # ====================================================

        with c9:

            if st.button(
                "🌎\n\n자동차 등록\n지역별 현황",
                key="card_registration_region",
                use_container_width=True,
            ):

                go_registration_region()


            st.html(
                """
                <div class="card-desc">
                    지역·차종·용도별<br>
                    자동차 등록 현황 비교
                </div>
                """
            )


    # ========================================================
    # DATA INFO
    # ========================================================

    st.html(
        """
        <div class="data-info">

            연결 데이터<br><br>

            · KOSIS 운전면허소지자현황 성별<br>
            · KOSIS 운전면허소지자현황 연령대별<br>
            · KOSIS 운전면허소지자현황 지역별<br>
            · 경찰청 운전면허 자진반납 2023<br>
            · 경찰청 운전면허 자진반납 2025<br>
            · 경찰청 운전면허 자진반납 지역별 종합 현황<br>
            · 국토교통통계누리 자동차등록현황 연도별<br>
            · 국토교통통계누리 자동차등록현황 지역별

        </div>
        """
    )