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


def go_license_return_guide():
    st.switch_page(
        "pages/poli/license_return_guide.py"
    )


def go_senior_education():
    st.switch_page(
        "pages/poli/senior_education.py"
    )


def go_senior_policy():
    st.switch_page(
        "pages/poli/senior_policy.py"
    )


def go_senior_safety_policy():
    st.switch_page(
        "pages/poli/senior_safety_policy.py"
    )


def go_license_return_policy():
    st.switch_page(
        "pages/poli/license_return_policy.py"
    )


def go_return_compare():
    st.switch_page(
        "pages/poli/return_compare.py"
    )


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
    padding-bottom: 55px;
}


/* ==========================================================
   TOP NAV
========================================================== */

.st-key-top_nav {

    background:
        rgba(255,255,255,.98);

    border-radius: 16px;

    padding:
        10px 20px;

    margin-bottom: 20px;

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


.st-key-nav_policy button {

    color:
        #D6A348 !important;

    font-weight:
        900 !important;
}


.st-key-nav_future button {

    background:
        #D9A64A !important;

    color:
        #172035 !important;

    border-radius:
        2px !important;

    font-size:
        15px !important;

    font-weight:
        800 !important;
}


/* ==========================================================
   PAGE
========================================================== */

.st-key-policy_page {

    background:
        #101625;

    border:
        1px solid #34405A;

    border-radius:
        20px;

    padding:
        34px 36px 48px 36px;

    box-shadow:
        0 12px 36px
        rgba(0,0,0,.18);
}


/* ==========================================================
   HEADER
========================================================== */

.page-path {

    color:
        #D6A348;

    font-size:
        13px;

    font-weight:
        900;

    letter-spacing:
        1.4px;

    margin-bottom:
        10px;
}


.page-title {

    color:
        #FFFFFF;

    font-size:
        42px;

    font-weight:
        900;

    letter-spacing:
        -1.5px;

    line-height:
        1.15;

    margin-bottom:
        12px;
}


.page-sub {

    color:
        #C3CBD8;

    font-size:
        15px;

    line-height:
        1.8;

    margin-bottom:
        24px;

    max-width:
        1050px;
}


/* ==========================================================
   SECTION
========================================================== */

.section-title {

    color:
        #FFFFFF;

    font-size:
        25px;

    font-weight:
        900;

    margin-top:
        34px;

    margin-bottom:
        8px;
}


.section-sub {

    color:
        #AEB8C9;

    font-size:
        13px;

    line-height:
        1.8;

    margin-bottom:
        20px;
}


/* ==========================================================
   GUIDE CARD
========================================================== */

.guide-card {

    background:
        linear-gradient(
            120deg,
            #172238 0%,
            #1C2941 65%,
            #302D28 100%
        );

    border:
        1px solid #A77E35;

    border-radius:
        24px;

    padding:
        28px 30px;

    position:
        relative;

    overflow:
        hidden;
}


.guide-card::after {

    content:
        "GUIDE";

    position:
        absolute;

    right:
        22px;

    top:
        5px;

    color:
        rgba(214,163,72,.05);

    font-size:
        72px;

    font-weight:
        900;
}


.guide-label {

    color:
        #E7B955;

    font-size:
        11px;

    font-weight:
        900;

    letter-spacing:
        1.4px;

    margin-bottom:
        10px;
}


.guide-title {

    color:
        #FFFFFF;

    font-size:
        26px;

    font-weight:
        900;

    margin-bottom:
        11px;
}


.guide-desc {

    color:
        #D0D7E1;

    font-size:
        14px;

    line-height:
        1.8;

    max-width:
        980px;
}


.guide-flow {

    display:
        flex;

    flex-wrap:
        wrap;

    align-items:
        center;

    gap:
        9px;

    margin-top:
        21px;
}


.flow-item {

    padding:
        7px 11px;

    border:
        1px solid #46536F;

    border-radius:
        8px;

    background:
        #1B263B;

    color:
        #DFE5ED;

    font-size:
        12px;

    font-weight:
        800;
}


.flow-arrow {

    color:
        #D6A348;

    font-size:
        15px;

    font-weight:
        900;
}


/* ==========================================================
   COMMON CARD
========================================================== */

.policy-card {

    background:
        #182035;

    border:
        1px solid #3A4662;

    border-radius:
        22px;

    padding:
        23px 24px;

    min-height:
        235px;

    height:
        100%;

    position:
        relative;

    overflow:
        hidden;
}


.policy-card-number {

    color:
        #D6A348;

    font-size:
        11px;

    font-weight:
        900;

    letter-spacing:
        1.2px;

    margin-bottom:
        12px;
}


.policy-card-title {

    color:
        #FFFFFF;

    font-size:
        20px;

    font-weight:
        900;

    margin-bottom:
        11px;
}


.policy-card-desc {

    color:
        #C7CFDB;

    font-size:
        13px;

    line-height:
        1.85;

    min-height:
        95px;
}


.policy-card-tag {

    display:
        inline-block;

    margin-top:
        15px;

    padding:
        6px 10px;

    background:
        rgba(214,163,72,.10);

    border:
        1px solid rgba(214,163,72,.30);

    border-radius:
        999px;

    color:
        #E7BC67;

    font-size:
        11px;

    font-weight:
        800;
}


/* ==========================================================
   CARD BUTTON
========================================================== */

.st-key-card_return_guide button,
.st-key-card_education button,
.st-key-card_policy button,
.st-key-card_safety button,
.st-key-card_return_policy button {

    background:
        #192136 !important;

    color:
        #E7EBF1 !important;

    border:
        1px solid #46536F !important;

    border-radius:
        10px !important;

    min-height:
        48px !important;

    font-size:
        13px !important;

    font-weight:
        800 !important;

    margin-top:
        10px !important;
}


.st-key-card_return_guide button:hover,
.st-key-card_education button:hover,
.st-key-card_policy button:hover,
.st-key-card_safety button:hover,
.st-key-card_return_policy button:hover {

    border-color:
        #D6A348 !important;

    color:
        #F0C66E !important;
}


/* ==========================================================
   2023 VS 2025 COMPARE CARD
========================================================== */

.compare-card {

    background:
        linear-gradient(
            120deg,
            #142036 0%,
            #1B2941 50%,
            #242D3F 100%
        );

    border:
        1px solid #596783;

    border-radius:
        26px;

    padding:
        31px 33px;

    position:
        relative;

    overflow:
        hidden;
}


.compare-card::after {

    content:
        "2023 VS 2025";

    position:
        absolute;

    right:
        24px;

    top:
        8px;

    color:
        rgba(255,255,255,.035);

    font-size:
        62px;

    font-weight:
        900;

    letter-spacing:
        2px;
}


.compare-label {

    color:
        #E0AC4C;

    font-size:
        12px;

    font-weight:
        900;

    letter-spacing:
        1.4px;

    margin-bottom:
        12px;
}


.compare-title {

    color:
        #FFFFFF;

    font-size:
        27px;

    font-weight:
        900;

    margin-bottom:
        12px;
}


.compare-desc {

    color:
        #C8D0DD;

    font-size:
        14px;

    line-height:
        1.9;

    max-width:
        1000px;
}


.compare-example {

    display:
        flex;

    gap:
        12px;

    flex-wrap:
        wrap;

    margin-top:
        20px;
}


.compare-pill {

    padding:
        7px 12px;

    border-radius:
        8px;

    background:
        #202B43;

    border:
        1px solid #45526D;

    color:
        #DCE2EC;

    font-size:
        12px;

    font-weight:
        700;
}


.compare-pill.yes {

    border-color:
        rgba(103,190,151,.55);

    color:
        #8FD5B4;

    background:
        rgba(66,137,106,.12);
}


.st-key-card_compare button {

    background:
        #D9A64A !important;

    color:
        #172035 !important;

    border:
        none !important;

    border-radius:
        10px !important;

    min-height:
        50px !important;

    font-size:
        14px !important;

    font-weight:
        900 !important;

    margin-top:
        11px !important;
}


.st-key-card_compare button:hover {

    background:
        #E9BB63 !important;
}


/* ==========================================================
   INFO
========================================================== */

.policy-info {

    margin-top:
        32px;

    padding:
        20px 22px;

    background:
        #121A2B;

    border:
        1px solid #35415C;

    border-left:
        4px solid #D6A348;

    border-radius:
        7px 15px 15px 7px;

    color:
        #D9DFE8;

    font-size:
        13px;

    line-height:
        1.9;
}


.policy-info b {

    color:
        #FFFFFF;
}


/* ==========================================================
   CAPTION
========================================================== */

[data-testid="stCaptionContainer"] {

    color:
        #9DA8B8 !important;

    font-size:
        12px !important;
}


/* ==========================================================
   MOBILE
========================================================== */

@media (max-width: 900px) {

    .guide-flow {
        gap: 6px;
    }

    .compare-card::after,
    .guide-card::after {
        display: none;
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
        gap="small"
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
                icon="📈"
            )


# ============================================================
# PAGE
# ============================================================

with st.container(
    key="policy_page"
):

    # ========================================================
    # HEADER
    # ========================================================

    st.html(
        """
        <div class="page-path">
            SAFER · POLICY
        </div>

        <div class="page-title">
            고령운전자 정책·제도
        </div>

        <div class="page-sub">
            운전면허 자진반납 방법부터 교통안전교육 통계,
            전국·지역별 고령운전자 정책과 자진반납 지원제도,
            연도별 자진반납 변화까지 한 곳에서 확인하고 비교합니다.
        </div>
        """
    )


    # ========================================================
    # 1. LICENSE RETURN GUIDE
    # ========================================================

    st.html(
        """
        <div class="section-title">
            운전면허 자진반납 이용 안내
        </div>

        <div class="section-sub">
            운전면허를 자진반납하려는 사용자가 실제 신청 절차를
            순서대로 확인할 수 있습니다.
        </div>
        """
    )


    st.html(
        """
        <div class="guide-card">

            <div class="guide-label">
                LICENSE RETURN GUIDE
            </div>

            <div class="guide-title">
                운전면허를 자진반납하려면 어떻게 해야 할까요?
            </div>

            <div class="guide-desc">
                신청 대상 확인부터 준비물, 신청 장소,
                면허 취소 처리와 지역별 지원혜택 확인까지
                운전면허 자진반납 과정을 단계별로 안내합니다.
            </div>

            <div class="guide-flow">

                <div class="flow-item">
                    01 대상 확인
                </div>

                <div class="flow-arrow">
                    →
                </div>

                <div class="flow-item">
                    02 준비물
                </div>

                <div class="flow-arrow">
                    →
                </div>

                <div class="flow-item">
                    03 방문
                </div>

                <div class="flow-arrow">
                    →
                </div>

                <div class="flow-item">
                    04 반납 신청
                </div>

                <div class="flow-arrow">
                    →
                </div>

                <div class="flow-item">
                    05 면허 취소
                </div>

                <div class="flow-arrow">
                    →
                </div>

                <div class="flow-item">
                    06 지원혜택 확인
                </div>

            </div>

        </div>
        """
    )


    guide_info, guide_button = st.columns(
        [3.5, 1],
        vertical_alignment="center"
    )


    with guide_info:

        st.caption(
            "※ 실제 신청 장소 및 지원 내용은 "
            "지역별 정책에 따라 다를 수 있습니다."
        )


    with guide_button:

        with st.container(
            key="card_return_guide"
        ):

            if st.button(
                "자진반납 방법 확인 →",
                use_container_width=True
            ):
                go_license_return_guide()


    # ========================================================
    # 2. 2023 VS 2025 RETURN COMPARISON
    # ========================================================

    st.html(
        """
        <div class="section-title">
            2023 vs 2025 운전면허 자진반납자 비교
        </div>

        <div class="section-sub">
            2023년과 2025년의 지역별·연령별 운전면허 자진반납 현황을
            비교하여 자진반납 건수와 증감 변화를 확인합니다.
        </div>
        """
    )


    st.html(
        """
        <div class="compare-card">

            <div class="compare-label">
                LICENSE RETURN COMPARISON
            </div>

            <div class="compare-title">
                2023년과 2025년 자진반납자는 어떻게 달라졌을까요?
            </div>

            <div class="compare-desc">
                2023년과 2025년 운전면허 자진반납 데이터를 이용하여
                지역별 자진반납 규모와 연령별 차이를 비교합니다.

                자진반납 건수의 증가·감소와 증감률을 확인하여
                지역별 변화가 어떻게 나타났는지 분석할 수 있습니다.
            </div>

            <div class="compare-example">

                <div class="compare-pill">
                    2023 자진반납
                </div>

                <div class="compare-pill">
                    2025 자진반납
                </div>

                <div class="compare-pill yes">
                    지역별 비교
                </div>

                <div class="compare-pill yes">
                    연령별 비교
                </div>

                <div class="compare-pill">
                    증감률 분석
                </div>

            </div>

        </div>
        """
    )


    compare_info, compare_button = st.columns(
        [3.5, 1],
        vertical_alignment="center"
    )


    with compare_info:

        st.caption(
            "※ 2023년과 2025년 운전면허 자진반납 건수 및 "
            "증감률을 기준으로 비교합니다."
        )


    with compare_button:

        with st.container(
            key="card_compare"
        ):

            if st.button(
                "2023 vs 2025 비교하기 →",
                use_container_width=True
            ):
                go_return_compare()




    # ========================================================
    # 3. POLICY ANALYSIS
    # ========================================================

    st.html(
        """
        <div class="section-title">
            정책 현황 및 분석
        </div>

        <div class="section-sub">
            교통안전교육 통계와 전국·지역별 고령운전자 정책,
            운전면허 자진반납 지원제도를 데이터 기반으로 확인합니다.
        </div>
        """
    )


    # ========================================================
    # ROW 1
    # ========================================================

    col1, col2 = st.columns(
        2,
        gap="large"
    )


    # --------------------------------------------------------
    # EDUCATION STATISTICS
    # --------------------------------------------------------

    with col1:

        st.html(
            """
            <div class="policy-card">

                <div class="policy-card-number">
                    01 · EDUCATION STATISTICS
                </div>

                <div class="policy-card-title">
                    고령운전자 교통안전교육 통계
                </div>

                <div class="policy-card-desc">
                    도로교통공단 고령운전자 교통안전교육 데이터를
                    기반으로 교육 현황을 분석합니다.
                    월별·지역별 교육 실적과 변화 추이를
                    확인할 수 있습니다.
                </div>

                <div class="policy-card-tag">
                    교육통계 · 지역분석 · 추이
                </div>

            </div>
            """
        )


        with st.container(
            key="card_education"
        ):

            if st.button(
                "고령운전자 교통안전교육 통계 보기 →",
                use_container_width=True
            ):
                go_senior_education()


    # --------------------------------------------------------
    # NATIONAL POLICY
    # --------------------------------------------------------

    with col2:

        st.html(
            """
            <div class="policy-card">

                <div class="policy-card-number">
                    02 · NATIONAL POLICY
                </div>

                <div class="policy-card-title">
                    전국 고령운전자 정책
                </div>

                <div class="policy-card-desc">
                    전국에서 시행 중인 고령운전자 관련 정책과
                    제도를 확인하고 정책 대상,
                    지원방식 및 주요 내용을 비교합니다.
                </div>

                <div class="policy-card-tag">
                    전국 · 정책비교 · 제도
                </div>

            </div>
            """
        )


        with st.container(
            key="card_policy"
        ):

            if st.button(
                "전국 고령운전자 정책 보기 →",
                use_container_width=True
            ):
                go_senior_policy()


    # ========================================================
    # ROW 2
    # ========================================================

    col3, col4 = st.columns(
        2,
        gap="large"
    )


    # --------------------------------------------------------
    # LOCAL SAFETY
    # --------------------------------------------------------

    with col3:

        st.html(
            """
            <div class="policy-card">

                <div class="policy-card-number">
                    03 · LOCAL SAFETY
                </div>

                <div class="policy-card-title">
                    지역 특화 고령운전자 안전정책
                </div>

                <div class="policy-card-desc">
                    각 지역의 교통환경과 고령인구 특성을 반영한
                    안전정책을 비교합니다.
                    지역별 특화사업과 지원 내용을 확인합니다.
                </div>

                <div class="policy-card-tag">
                    지역 · 안전 · 특화정책
                </div>

            </div>
            """
        )


        with st.container(
            key="card_safety"
        ):

            if st.button(
                "지역 특화 안전정책 보기 →",
                use_container_width=True
            ):
                go_senior_safety_policy()


    # --------------------------------------------------------
    # RETURN POLICY
    # --------------------------------------------------------

    with col4:

        st.html(
            """
            <div class="policy-card">

                <div class="policy-card-number">
                    04 · LICENSE RETURN
                </div>

                <div class="policy-card-title">
                    운전면허 자진반납 지원정책
                </div>

                <div class="policy-card-desc">
                    고령운전자의 운전면허 자진반납 시 제공되는
                    지역별 인센티브와 지원제도를 비교합니다.
                    지역에 따른 지원 차이를 확인할 수 있습니다.
                </div>

                <div class="policy-card-tag">
                    자진반납 · 혜택 · 지역비교
                </div>

            </div>
            """
        )


        with st.container(
            key="card_return_policy"
        ):

            if st.button(
                "운전면허 자진반납 정책 보기 →",
                use_container_width=True
            ):
                go_license_return_policy()


    # ========================================================
    # INFO
    # ========================================================

    st.html(
        """
        <div class="policy-info">

            <b>SAFER 정책·제도 분석 구성</b>

            <br><br>

            ① <b>운전면허 자진반납 방법</b>
            — 실제 제도 이용 절차 확인

            <br>

            ② <b>교통안전교육 통계</b>
            — 교육 실적 및 변화 추이 분석

            <br>

            ③ <b>전국·지역 특화 정책</b>
            — 고령운전자 관련 정책 내용 비교

            <br>

            ④ <b>운전면허 자진반납 지원정책</b>
            — 지역별 지원 및 혜택 비교

            <br>

            ⑤ <b>2023 vs 2025 자진반납 비교</b>
            — 지역·연령별 자진반납 건수와 증감 변화 비교

        </div>
        """
    )