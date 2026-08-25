# ============================================================
# streamlit/pages/people.py
# SAFER - 인구 분석 메인 페이지
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


def go_local_population():
    st.switch_page(
        "pages/people/local_population.py"
    )


def go_age_population():
    # 파일명은 기존 그대로 유지
    st.switch_page(
        "pages/people/resident_population_monthly.py"
    )


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


/* ==========================================================
   Streamlit 기본 UI 제거
========================================================== */

header[data-testid="stHeader"],
section[data-testid="stSidebar"],
#MainMenu,
footer {

    display: none;
}


/* ==========================================================
   전체 폭
========================================================== */

.block-container {

    max-width: 1600px;

    padding-top: 14px;
    padding-left: 30px;
    padding-right: 30px;
    padding-bottom: 55px;
}


/* ==========================================================
   TOP NAV
========================================================== */

.st-key-top_nav {

    background: rgba(255,255,255,.98);

    border-radius: 16px;

    padding: 10px 20px;

    margin-bottom: 28px;

    box-shadow:
        0 5px 20px
        rgba(0,0,0,.10);
}


.st-key-top_nav button {

    background: transparent !important;

    color: #30384D !important;

    border: none !important;

    box-shadow: none !important;

    font-size: 16px !important;

    font-weight: 500 !important;

    min-height: 44px !important;

    white-space: nowrap !important;
}


.st-key-top_nav button:hover {

    background: transparent !important;

    color: #D6A348 !important;
}


/* 로고 */

.st-key-nav_logo button {

    color: #27314C !important;

    font-size: 30px !important;

    font-weight: 900 !important;

    justify-content: flex-start !important;

    padding-left: 0 !important;
}


/* 현재 메뉴 */

.st-key-nav_people button {

    color: #D6A348 !important;

    font-weight: 900 !important;
}


/* 미래 전망 */

.st-key-nav_future button {

    background: #D9A64A !important;

    color: #172035 !important;

    font-size: 15px !important;

    font-weight: 800 !important;

    border-radius: 2px !important;
}


.st-key-nav_future button:hover {

    background: #E5B557 !important;

    color: #101625 !important;
}


/* ==========================================================
   PEOPLE PAGE
========================================================== */

.st-key-people_page {

    background: #101625;

    border: 1px solid #34405A;

    border-radius: 20px;

    padding:
        42px
        30px
        55px
        30px;
}


/* ==========================================================
   HEADER
========================================================== */

.safer-label {

    color: #D9A64A;

    font-size: 12px;

    font-weight: 900;

    letter-spacing: 1.3px;

    margin-bottom: 12px;
}


.page-title {

    color: #FFFFFF;

    font-size: 43px;

    font-weight: 900;

    line-height: 1.15;

    margin-bottom: 24px;
}


.page-description {

    color: #C6D0DE;

    font-size: 15px;

    line-height: 1.8;

    margin-bottom: 28px;
}


/* ==========================================================
   TAG
========================================================== */

.tag-wrap {

    display: flex;

    gap: 12px;

    margin-top: 5px;

    margin-bottom: 75px;
}


.data-tag {

    display: inline-flex;

    align-items: center;

    justify-content: center;

    padding: 8px 26px;

    min-height: 38px;

    border: 1px solid #53607A;

    border-radius: 30px;

    background: #171E31;

    color: #E1E6EF;

    font-size: 14px;

    font-weight: 800;
}


/* ==========================================================
   SECTION
========================================================== */

.section-title {

    color: #FFFFFF;

    font-size: 25px;

    font-weight: 900;

    margin-bottom: 12px;
}


.section-description {

    color: #8290AB;

    font-size: 14px;

    margin-bottom: 52px;
}


/* ==========================================================
   큰 카드 버튼 공통
========================================================== */

.st-key-local_population_card button,
.st-key-age_population_card button {

    width: 100% !important;

    height: 185px !important;

    min-height: 185px !important;

    background: #1D2439 !important;

    border: 1px solid #4A5874 !important;

    border-radius: 22px !important;

    box-shadow: none !important;

    color: #FFFFFF !important;

    font-size: 18px !important;

    font-weight: 900 !important;

    transition:
        transform .15s ease,
        background .15s ease,
        border-color .15s ease !important;
}


/* 버튼 안 텍스트 */

.st-key-local_population_card button p,
.st-key-age_population_card button p {

    color: #FFFFFF !important;

    font-size: 18px !important;

    font-weight: 900 !important;

    line-height: 2 !important;

    text-align: center !important;

    white-space: pre-line !important;
}


/* ==========================================================
   왼쪽 카드
========================================================== */

.st-key-local_population_card button {

    border-top:
        5px solid #93B79E !important;
}


.st-key-local_population_card button:hover {

    background: #232C43 !important;

    border-color: #93B79E !important;

    transform: translateY(-3px);
}


/* ==========================================================
   오른쪽 카드
========================================================== */

.st-key-age_population_card button {

    border-top:
        5px solid #D1A647 !important;
}


.st-key-age_population_card button:hover {

    background: #232C43 !important;

    border-color: #D1A647 !important;

    transform: translateY(-3px);
}


/* ==========================================================
   카드 설명
========================================================== */

.card-desc {

    color: #8FA0C0;

    text-align: center;

    font-size: 14px;

    line-height: 1.85;

    margin-top: 27px;

    min-height: 70px;
}


/* ==========================================================
   카드 클릭 안내
========================================================== */

.card-click {

    color: #65728D;

    text-align: center;

    font-size: 12px;

    margin-top: 3px;
}


/* ==========================================================
   INFO
========================================================== */

.info-box {

    margin-top: 48px;

    background: #161D30;

    border-left:
        3px solid #D9A64A;

    border-radius: 4px;

    padding: 23px 25px;

    color: #ADB8CA;

    font-size: 14px;

    line-height: 1.9;
}


.info-title {

    color: #FFFFFF;

    font-size: 16px;

    font-weight: 900;

    margin-bottom: 8px;
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
# PEOPLE PAGE
# ============================================================

with st.container(
    key="people_page"
):

    # ========================================================
    # HEADER
    # ========================================================

    st.html(
        """
        <div class="safer-label">
            SAFER DATA ANALYTICS
        </div>

        <div class="page-title">
            인구 분석
        </div>

        <div class="page-description">
            지역별 인구와 연령별 인구 데이터를 통해
            지역별 인구 규모와 고연령 인구 구조를 분석합니다.
        </div>
        """
    )


    # ========================================================
    # TAG
    # ========================================================

    st.html(
        """
        <div class="tag-wrap">

            <div class="data-tag">
                지역 인구
            </div>

            <div class="data-tag">
                연령별 인구
            </div>

        </div>
        """
    )


    # ========================================================
    # SECTION TITLE
    # ========================================================

    st.html(
        """
        <div class="section-title">
            분석 항목
        </div>

        <div class="section-description">
            분석할 인구 데이터셋을 선택하세요.
        </div>
        """
    )


    # ========================================================
    # CARDS
    # ========================================================

    left, right = st.columns(
        [
            1,
            1
        ],
        gap="large"
    )


    # ========================================================
    # LEFT CARD
    # ========================================================

    with left:

        with st.container(
            key="local_population_card"
        ):

            if st.button(
                "🗺️\n\n지역별 인구 현황",
                key="local_population_click",
                use_container_width=True
            ):

                go_local_population()


        st.html(
            """
            <div class="card-desc">

                연도별·지역별 인구 규모와

                <br>

                지역 간 인구 분포 비교 분석

            </div>
            """
        )


    # ========================================================
    # RIGHT CARD
    # ========================================================

    with right:

        with st.container(
            key="age_population_card"
        ):

            if st.button(
                "👥\n\n연령별 인구 현황",
                key="age_population_click",
                use_container_width=True
            ):

                go_age_population()


        st.html(
            """
            <div class="card-desc">

                지역·성별·연령대별 인구 구조와

                <br>

                60세 이상 인구 비율 분석

            </div>
            """
        )


    # ========================================================
    # INFO
    # ========================================================

    st.html(
        """
        <div class="info-box">

            <div class="info-title">
                SAFER 인구 분석
            </div>

            지역별 인구 현황에서는
            전국 시도의 인구 규모와 인구 분포를 비교합니다.

            <br>

            연령별 인구 현황에서는
            지역·성별·연령대별 인구 구조를 확인하고,
            지역별 60세 이상 인구 규모와 비율을 비교합니다.

        </div>
        """
    )