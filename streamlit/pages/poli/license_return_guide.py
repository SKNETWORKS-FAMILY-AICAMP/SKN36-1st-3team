import sys
from pathlib import Path

import streamlit as st


# ============================================================
# PROJECT ROOT
# SAFE/streamlit/pages/poli/license_return_guide.py
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[3]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))



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

    border-radius:
        16px;

    padding:
        10px 20px;

    margin-bottom:
        20px;
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

    font-weight:
        800 !important;
}


/* ==========================================================
   PAGE
========================================================== */

.st-key-guide_page {

    background:
        #101625;

    border:
        1px solid #34405A;

    border-radius:
        20px;

    padding:
        34px 36px 50px 36px;
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
        1000px;
}


/* ==========================================================
   BACK
========================================================== */

.st-key-back_policy button {

    background:
        #192136 !important;

    color:
        #E3E7EE !important;

    border:
        1px solid #39445D !important;

    border-radius:
        11px !important;

    min-height:
        44px !important;
}


/* ==========================================================
   NOTICE
========================================================== */

.guide-notice {

    background:
        linear-gradient(
            110deg,
            #19243A 0%,
            #232A38 100%
        );

    border:
        1px solid #9B7736;

    border-left:
        5px solid #D6A348;

    border-radius:
        8px 18px 18px 8px;

    padding:
        21px 23px;

    margin:
        12px 0 28px 0;

    color:
        #DCE2EB;

    font-size:
        13px;

    line-height:
        1.9;
}


.guide-notice-title {

    color:
        #F0C66E;

    font-size:
        15px;

    font-weight:
        900;

    margin-bottom:
        7px;
}


.guide-notice b {

    color:
        #FFFFFF;
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
   STEPS
========================================================== */

.step-card {

    background:
        #182035;

    border:
        1px solid #3A4662;

    border-radius:
        20px;

    padding:
        22px 22px;

    min-height:
        225px;

    height:
        100%;

    position:
        relative;

    overflow:
        hidden;
}


.step-number {

    display:
        inline-flex;

    width:
        35px;

    height:
        35px;

    justify-content:
        center;

    align-items:
        center;

    border-radius:
        50%;

    background:
        #D6A348;

    color:
        #172035;

    font-size:
        13px;

    font-weight:
        900;

    margin-bottom:
        15px;
}


.step-label {

    color:
        #D6A348;

    font-size:
        10px;

    font-weight:
        900;

    letter-spacing:
        1.3px;

    margin-bottom:
        7px;
}


.step-title {

    color:
        #FFFFFF;

    font-size:
        18px;

    font-weight:
        900;

    margin-bottom:
        10px;
}


.step-desc {

    color:
        #C5CEDC;

    font-size:
        12px;

    line-height:
        1.8;

    word-break:
        keep-all;
}


/* ==========================================================
   CHECK LIST
========================================================== */

.check-card {

    background:
        #182035;

    border:
        1px solid #3A4662;

    border-radius:
        20px;

    padding:
        23px 24px;

    min-height:
        165px;
}


.check-title {

    color:
        #FFFFFF;

    font-size:
        16px;

    font-weight:
        900;

    margin-bottom:
        15px;
}


.check-item {

    color:
        #D6DEE9;

    font-size:
        12px;

    line-height:
        2;
}


.check-icon {

    color:
        #85CFA7;

    font-weight:
        900;

    margin-right:
        7px;
}


/* ==========================================================
   SOURCE
========================================================== */

.policy-source {

    display:
        flex;

    align-items:
        center;

    gap:
        12px;

    margin-top:
        18px;

    padding-top:
        15px;

    border-top:
        1px solid #344057;
}


.source-label {

    color:
        #8F9AAF;

    font-size:
        11px;

    font-weight:
        800;
}


.source-link {

    display:
        inline-block;

    padding:
        6px 11px;

    border-radius:
        7px;

    background:
        rgba(214,163,72,.10);

    border:
        1px solid rgba(214,163,72,.35);

    color:
        #F0C66E !important;

    text-decoration:
        none !important;

    font-size:
        11px;

    font-weight:
        900;
}


.source-empty {

    color:
        #788399;

    font-size:
        11px;
}


/* ==========================================================
   WARNING
========================================================== */

.warning-card {

    background:
        rgba(202,111,82,.07);

    border:
        1px solid rgba(221,132,105,.34);

    border-left:
        4px solid #DD8469;

    border-radius:
        7px 15px 15px 7px;

    padding:
        20px 22px;

    margin-top:
        20px;

    color:
        #DCE2EB;

    font-size:
        12px;

    line-height:
        1.9;
}


.warning-title {

    color:
        #E99B83;

    font-size:
        15px;

    font-weight:
        900;

    margin-bottom:
        8px;
}


.warning-card b {

    color:
        #FFFFFF;
}


/* ==========================================================
   FOOT
========================================================== */

.guide-foot {

    background:
        #121A2B;

    border:
        1px solid #35415C;

    border-left:
        4px solid #D6A348;

    border-radius:
        7px 15px 15px 7px;

    padding:
        19px 21px;

    margin-top:
        30px;

    color:
        #BFC8D6;

    font-size:
        12px;

    line-height:
        1.9;
}


.guide-foot b {

    color:
        #FFFFFF;
}


/* ==========================================================
   MOBILE
========================================================== */

@media (max-width: 900px) {

    .region-info-grid,
    .support-area {

        grid-template-columns: 1fr;
    }

}

</style>
"""
)


# ============================================================
# NAV
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
        vertical_alignment="center"
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
    key="guide_page"
):

    # ========================================================
    # HEADER
    # ========================================================

    head_left, head_right = st.columns(
        [5, 1],
        vertical_alignment="center"
    )


    with head_left:

        st.html(
            """
            <div class="page-path">
                정책·제도 &gt; 운전면허 자진반납 안내
            </div>

            <div class="page-title">
                운전면허 자진반납 방법
            </div>

            <div class="page-sub">
                운전면허 자진반납을 고려하고 있다면
                신청 대상과 준비물, 방문 장소, 신청 절차,
                지역별 지원정책을 순서대로 확인해보세요.
            </div>
            """
        )


    with head_right:

        with st.container(
            key="back_policy"
        ):

            if st.button(
                "← 정책·제도",
                use_container_width=True
            ):

                go_policy()


    # ========================================================
    # IMPORTANT NOTICE
    # ========================================================

    st.html(
        """
        <div class="guide-notice">

            <div class="guide-notice-title">
                신청하기 전에 확인하세요
            </div>

            운전면허 자진반납 지원사업은
            <b>지역별로 대상 연령, 지원금액, 준비서류,
            신청 장소 및 지원방식이 다를 수 있습니다.</b>

            <br>

            따라서 아래 공통 절차를 확인한 후,
            반드시 본인의 주민등록 주소지에 해당하는
            지역 정책을 함께 확인하는 것이 좋습니다.

        </div>
        """
    )


    # ========================================================
    # STEP GUIDE
    # ========================================================

    st.html(
        """
        <div class="section-title">
            자진반납 절차
        </div>

        <div class="section-sub">
            일반적인 운전면허 자진반납 과정입니다.
            실제 처리 절차는 지역별 정책에 따라 일부 달라질 수 있습니다.
        </div>
        """
    )


    # ROW 1
    step1, step2, step3 = st.columns(
        3,
        gap="medium"
    )


    with step1:

        st.html(
            """
            <div class="step-card">

                <div class="step-number">
                    1
                </div>

                <div class="step-label">
                    ELIGIBILITY
                </div>

                <div class="step-title">
                    대상 확인
                </div>

                <div class="step-desc">
                    거주 지역의 운전면허 자진반납 지원사업
                    대상 연령과 거주 조건을 확인합니다.

                    <br><br>

                    동일한 자진반납 제도라도
                    지자체마다 지원 연령과 조건이
                    다를 수 있습니다.
                </div>

            </div>
            """
        )


    with step2:

        st.html(
            """
            <div class="step-card">

                <div class="step-number">
                    2
                </div>

                <div class="step-label">
                    DOCUMENT
                </div>

                <div class="step-title">
                    준비물 확인
                </div>

                <div class="step-desc">
                    일반적으로 본인의 운전면허증과
                    본인 확인을 위한 신분증 등을 준비합니다.

                    <br><br>

                    면허증 분실 여부나 지역별 정책에 따라
                    추가 서류가 필요할 수 있으므로
                    방문 전 확인하는 것이 좋습니다.
                </div>

            </div>
            """
        )


    with step3:

        st.html(
            """
            <div class="step-card">

                <div class="step-number">
                    3
                </div>

                <div class="step-label">
                    VISIT
                </div>

                <div class="step-title">
                    신청 장소 방문
                </div>

                <div class="step-desc">
                    지역별 신청방법에 따라
                    주민센터 또는 지정된 신청기관을 방문합니다.

                    <br><br>

                    일부 지역은 자진반납과
                    지원혜택 신청을 함께 처리하는
                    원스톱 방식을 운영합니다.
                </div>

            </div>
            """
        )


    st.write("")


    # ROW 2
    step4, step5, step6 = st.columns(
        3,
        gap="medium"
    )


    with step4:

        st.html(
            """
            <div class="step-card">

                <div class="step-number">
                    4
                </div>

                <div class="step-label">
                    APPLICATION
                </div>

                <div class="step-title">
                    자진반납 신청
                </div>

                <div class="step-desc">
                    운전면허 자진반납 의사를 확인하고
                    필요한 신청 절차를 진행합니다.

                    <br><br>

                    면허 반납은 운전 가능 여부에
                    직접 영향을 주는 절차이므로
                    충분히 확인한 뒤 신청하세요.
                </div>

            </div>
            """
        )


    with step5:

        st.html(
            """
            <div class="step-card">

                <div class="step-number">
                    5
                </div>

                <div class="step-label">
                    CANCELLATION
                </div>

                <div class="step-title">
                    면허 취소 처리
                </div>

                <div class="step-desc">
                    자진반납 절차가 완료되면
                    보유 운전면허에 대한 취소 처리가 진행됩니다.

                    <br><br>

                    이후에는 유효한 면허 없이
                    자동차 등을 운전해서는 안 됩니다.
                </div>

            </div>
            """
        )


    with step6:

        st.html(
            """
            <div class="step-card">

                <div class="step-number">
                    6
                </div>

                <div class="step-label">
                    BENEFIT
                </div>

                <div class="step-title">
                    지원혜택 확인
                </div>

                <div class="step-desc">
                    자진반납 지원사업 대상자라면
                    지역별 기준에 따라 교통카드,
                    지역화폐, 상품권, 현금 등
                    지원혜택을 확인합니다.

                    <br><br>

                    예산 소진 여부도 함께 확인하세요.
                </div>

            </div>
            """
        )


    # ========================================================
    # PREPARE
    # ========================================================

    st.html(
        """
        <div class="section-title">
            방문 전 체크리스트
        </div>

        <div class="section-sub">
            방문 전에 아래 항목을 미리 확인하면
            보다 원활하게 신청할 수 있습니다.
        </div>
        """
    )


    c1, c2, c3 = st.columns(
        3,
        gap="medium"
    )


    with c1:

        st.html(
            """
            <div class="check-card">

                <div class="check-title">
                    기본 준비
                </div>

                <div class="check-item">
                    <span class="check-icon">✓</span>
                    운전면허증
                </div>

                <div class="check-item">
                    <span class="check-icon">✓</span>
                    본인 확인용 신분증
                </div>

                <div class="check-item">
                    <span class="check-icon">✓</span>
                    주소지 및 거주조건 확인
                </div>

            </div>
            """
        )


    with c2:

        st.html(
            """
            <div class="check-card">

                <div class="check-title">
                    정책 확인
                </div>

                <div class="check-item">
                    <span class="check-icon">✓</span>
                    지원 대상 연령
                </div>

                <div class="check-item">
                    <span class="check-icon">✓</span>
                    일반 지원 금액·혜택
                </div>

                <div class="check-item">
                    <span class="check-icon">✓</span>
                    실제 운전자 추가지원 여부
                </div>

            </div>
            """
        )


    with c3:

        st.html(
            """
            <div class="check-card">

                <div class="check-title">
                    신청 전 확인
                </div>

                <div class="check-item">
                    <span class="check-icon">✓</span>
                    신청 장소
                </div>

                <div class="check-item">
                    <span class="check-icon">✓</span>
                    신청 가능 기간
                </div>

                <div class="check-item">
                    <span class="check-icon">✓</span>
                    예산 소진 여부
                </div>

            </div>
            """
        )


    # ========================================================
    # WARNING
    # ========================================================

    st.html(
        """
        <div class="section-title">
            자진반납 전 꼭 알아두세요
        </div>
        """
    )


    st.html(
        """
        <div class="warning-card">

            <div class="warning-title">
                면허반납은 신중하게 결정하세요
            </div>

            운전면허 자진반납은 단순히 면허증을 보관기관에
            맡기는 절차가 아니라 <b>운전면허 취소와 연결되는 절차</b>입니다.

            <br>

            따라서 향후 차량 운전 필요성, 가족의 이동지원 가능 여부,
            대중교통 접근성 등을 충분히 고려한 뒤 결정하는 것이 좋습니다.

            <br><br>

            특히 보유한 면허 종류와 자진반납 이후 운전 가능 여부 등
            법적 사항은 신청기관에서 최종 확인하세요.

        </div>
        """
    )


    # ========================================================
    # FOOT
    # ========================================================

    st.html(
        """
        <div class="guide-foot">

            <b>안내</b>

            <br>

            SAFER의 지역별 안내는
            <b>return_license_policy</b> 테이블에 수집된
            정책 데이터를 기반으로 제공합니다.

            <br>

            지자체별 사업은 예산, 사업기간 및 정책 변경에 따라
            지원 내용이 달라질 수 있으므로
            신청 전 카드 하단의 <b>공식 출처</b>에서
            최신 내용을 다시 확인하는 것을 권장합니다.

        </div>
        """
    )