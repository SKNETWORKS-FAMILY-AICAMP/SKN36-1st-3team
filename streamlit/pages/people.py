import streamlit as st


# ============================================================
# 페이지 이동 함수
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

    /* =========================================================
       전체 배경
    ========================================================= */

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


    /* =========================================================
       상단 NAV
    ========================================================= */

    .st-key-top_nav {

        background:
            rgba(255,255,255,.98);

        border-radius: 16px;

        padding:
            10px 20px;

        margin-bottom:
            20px;

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


    /* 현재 페이지 */
    .st-key-nav_people button {

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


    /* =========================================================
       메인 페이지
    ========================================================= */

    .st-key-people_page {

        background:
            #101625;

        border:
            1px solid
            #34405A;

        border-radius:
            20px;

        padding:
            34px 36px 50px 36px;

        box-shadow:
            0 12px 36px
            rgba(0,0,0,.18);

        min-height:
            760px;
    }


    /* =========================================================
       HEADER
    ========================================================= */

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
            43px;

        font-weight:
            900;

        letter-spacing:
            -2px;

        line-height:
            1.15;

        margin-bottom:
            16px;
    }


    .page-sub {

        color:
            #B7C0D3;

        font-size:
            15px;

        line-height:
            1.8;

        margin-bottom:
            26px;
    }


    /* =========================================================
       작은 카테고리 버튼
    ========================================================= */

    .category-wrap {

        display: flex;

        gap: 12px;

        margin-top: 4px;

        margin-bottom: 60px;
    }


    .category-pill {

        display: inline-flex;

        align-items: center;

        justify-content: center;

        min-width: 105px;

        height: 38px;

        padding:
            0 18px;

        border:
            1px solid #414D69;

        border-radius:
            22px;

        background:
            #182035;

        color:
            #CFD5E1;

        font-size:
            13px;

        font-weight:
            700;
    }


    /* =========================================================
       분석 항목
    ========================================================= */

    .section-title {

        color:
            #FFFFFF;

        font-size:
            24px;

        font-weight:
            900;

        margin-bottom:
            8px;
    }


    .section-sub {

        color:
            #8795B1;

        font-size:
            13px;

        margin-bottom:
            32px;
    }


    /* =========================================================
       CARD BUTTON
    ========================================================= */

    .st-key-local_population_card button,
    .st-key-resident_population_card button {

        width:
            100% !important;

        height:
            190px !important;

        min-height:
            190px !important;

        background:
            #1A2238 !important;

        border:
            1px solid
            #46516B !important;

        border-radius:
            22px !important;

        color:
            #FFFFFF !important;

        box-shadow:
            none !important;

        transition:
            all .18s ease !important;
    }


    .st-key-local_population_card button {

        border-top:
            5px solid
            #86B79E !important;
    }


    .st-key-resident_population_card button {

        border-top:
            5px solid
            #D6A348 !important;
    }


    .st-key-local_population_card button:hover,
    .st-key-resident_population_card button:hover {

        transform:
            translateY(-4px);

        background:
            #202A44 !important;

        border-color:
            #71809F !important;

        box-shadow:
            0 10px 25px
            rgba(0,0,0,.25) !important;
    }


    .st-key-local_population_card button p,
    .st-key-resident_population_card button p {

        color:
            #FFFFFF !important;

        font-size:
            17px !important;

        font-weight:
            800 !important;

        line-height:
            1.7 !important;

        white-space:
            pre-line !important;
    }


    /* =========================================================
       카드 설명
    ========================================================= */

    .card-description {

        color:
            #8393B4;

        font-size:
            13px;

        text-align:
            center;

        line-height:
            1.7;

        padding-top:
            13px;
    }


    /* =========================================================
       하단 설명
    ========================================================= */

    .people-info {

        margin-top:
            55px;

        padding:
            22px 24px;

        background:
            #141C2F;

        border-left:
            3px solid
            #D6A348;

        border-radius:
            4px;

        color:
            #9CA8BF;

        font-size:
            13px;

        line-height:
            1.9;
    }


    .people-info-title {

        color:
            #FFFFFF;

        font-size:
            14px;

        font-weight:
            800;

        margin-bottom:
            8px;
    }


    /* =========================================================
       Streamlit button text fix
    ========================================================= */

    button p {

        margin:
            0 !important;
    }

    </style>
    """
)


# ============================================================
# 상단 NAV
# ============================================================

with st.container(key="top_nav"):

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
    # 인구
    # --------------------------------------------------------

    with n1:

        if st.button(
            "인구",
            key="nav_people",
            use_container_width=True
        ):
            go_people()


    # --------------------------------------------------------
    # 자동차
    # --------------------------------------------------------

    with n2:

        if st.button(
            "자동차",
            key="nav_car",
            use_container_width=True
        ):
            go_car()


    # --------------------------------------------------------
    # 교통사고
    # --------------------------------------------------------

    with n3:

        if st.button(
            "교통사고",
            key="nav_accident",
            use_container_width=True
        ):
            go_accident()


    # --------------------------------------------------------
    # 제도
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
    # 미래 전망
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

with st.container(key="people_page"):


    # ========================================================
    # HEADER
    # ========================================================

    st.html(
        """
        <div class="page-path">
            SAFER DATA ANALYTICS
        </div>

        <div class="page-title">
            인구 분석
        </div>

        <div class="page-sub">
            지역별 인구와 주민등록 인구 데이터를 통해
            지역별 인구 규모와 최근 인구 변화 추이를 분석합니다.
        </div>


        <div class="category-wrap">

            <div class="category-pill">
                지역 인구
            </div>

            <div class="category-pill">
                주민등록 인구
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

        <div class="section-sub">
            분석할 인구 데이터셋을 선택하세요.
        </div>
        """
    )


    # ========================================================
    # CARDS
    # ========================================================

    left_space, card1, gap, card2, right_space = st.columns(
        [
            0.15,
            1,
            0.10,
            1,
            0.15,
        ],
        gap="large"
    )


    # ========================================================
    # CARD 1
    # 지역별 인구 현황
    # ========================================================

    with card1:

        if st.button(
            "🗺️\n\n지역별 인구 현황",
            key="local_population_card",
            use_container_width=True
        ):

            st.switch_page(
                "pages/people/local_population.py"
            )


        st.html(
            """
            <div class="card-description">
                연도별·지역별 인구 규모와<br>
                지역 간 인구 분포 비교 분석
            </div>
            """
        )


    # ========================================================
    # CARD 2
    # 주민등록 인구 및 세대 현황
    # ========================================================

    with card2:

        if st.button(
            "👥\n\n주민등록 인구 및 세대 현황 (월간)",
            key="resident_population_card",
            use_container_width=True
        ):

            st.switch_page(
                "pages/people/resident_population_monthly.py"
            )


        st.html(
            """
            <div class="card-description">
                월별 주민등록 인구 변화와<br>
                지역별 인구·세대 변화 추이 분석
            </div>
            """
        )


    # ========================================================
    # INFO
    # ========================================================

    st.html(
        """
        <div class="people-info">

            <div class="people-info-title">
                👥 인구 데이터 분석
            </div>

            <b>지역별 인구 현황</b>에서는
            연도별 시도 인구 규모와 지역 간 인구 분포를 비교합니다.
            <br>

            <b>주민등록 인구 및 세대 현황(월간)</b>에서는
            월별 주민등록 인구 변화를 통해 최근 인구 변화 흐름을
            확인할 수 있습니다.

        </div>
        """
    )