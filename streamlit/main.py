import streamlit as st
import plotly.graph_objects as go


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
            #3A5A8C 42%,
            #F2A93B 76%,
            #FBF6EC 100%
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
    padding-left: 18px;
    padding-right: 18px;
    padding-bottom: 35px;
}


/* ==========================================================
   NAV
========================================================== */

.st-key-top_nav {

    background: rgba(255,255,255,.98);

    border-radius: 16px;

    padding: 10px 20px;

    margin-bottom: 14px;

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

    transition: .15s ease;
}


.st-key-top_nav button:hover {

    background: transparent !important;

    color: #D6A348 !important;
}


/* ==========================================================
   SAFER
========================================================== */

.st-key-nav_logo button {

    color: #27314C !important;

    font-size: 28px !important;

    font-weight: 900 !important;

    letter-spacing: -1px !important;

    justify-content: flex-start !important;

    padding-left: 0 !important;
}


.st-key-nav_logo button:hover {

    color: #D6A348 !important;
}


/* ==========================================================
   FUTURE BUTTON
========================================================== */

.st-key-nav_future button {

    background: #D9A64A !important;

    color: #172035 !important;

    font-weight: 800 !important;

    border-radius: 1px !important;
}


.st-key-nav_future button:hover {

    background: #C9973C !important;

    color: #172035 !important;
}


/* ==========================================================
   MAIN PANEL
========================================================== */

.st-key-main_panel {

    background: rgba(15,21,36,.94);

    border:
        1px solid
        rgba(93,109,145,.55);

    border-radius:
        0 0 72px 72px;

    padding:
        35px 46px 55px 46px;

    min-height: 590px;

    backdrop-filter: blur(5px);
}


/* ==========================================================
   HERO
========================================================== */

.hero-area {

    padding-top: 38px;

    min-height: 310px;
}


.hero-title {

    color: #FFFFFF;

    font-size: 54px;

    font-weight: 900;

    letter-spacing: -3px;

    line-height: 1.08;

    margin-bottom: 32px;
}


.hero-desc {

    color: rgba(255,255,255,.82);

    font-size: 15px;

    line-height: 1.5;

    margin-bottom: 28px;
}


/* ==========================================================
   COLOR LINE
========================================================== */

.risk-line {

    width: 100%;

    height: 8px;

    border-radius: 30px;

    background:
        linear-gradient(
            90deg,

            #6DB99A 0%,
            #6DB99A 45%,

            #DAA748 45%,
            #DAA748 74%,

            #CF6C4E 74%,
            #CF6C4E 100%
        );

    margin-top: 25px;

    margin-bottom: 45px;
}


/* ==========================================================
   QUICK CARDS
========================================================== */

.st-key-quick_menu button {

    width: 100% !important;

    height: 132px !important;

    background: rgba(255,255,255,.98) !important;

    color: #26304A !important;

    border: none !important;

    border-radius: 18px !important;

    font-size: 15px !important;

    font-weight: 800 !important;

    line-height: 1.55 !important;

    white-space: pre-line !important;

    box-shadow:
        0 7px 20px
        rgba(0,0,0,.12) !important;

    transition:
        transform .15s ease,
        box-shadow .15s ease !important;
}


.st-key-quick_menu button:hover {

    transform: translateY(-5px);

    box-shadow:
        0 14px 28px
        rgba(0,0,0,.22) !important;
}


.st-key-card_population button {
    border-top: 7px solid #69B895 !important;
}


.st-key-card_car button {
    border-top: 7px solid #DDA847 !important;
}


.st-key-card_accident button {
    border-top: 7px solid #CE6B4D !important;
}


.st-key-card_policy button {
    border-top: 7px solid #7FC3A6 !important;
}


.st-key-card_faq button {
    border-top: 7px solid #E2A45E !important;
}


.quick-caption {

    color: rgba(255,255,255,.65);

    text-align: center;

    font-size: 10px;

    margin-top: -6px;
}


/* ==========================================================
   FUTURE PANEL
========================================================== */

.st-key-future_panel {

    background: #F7F3E9;

    border-radius: 72px;

    padding:
        35px 42px 38px 42px;

    min-height: 460px;
}


.future-title {

    color: #29334F;

    font-size: 27px;

    font-weight: 900;

    letter-spacing: -1px;

    margin-bottom: 7px;
}


.future-sub {

    color: #A0A5AF;

    font-size: 11px;

    margin-bottom: 22px;
}


/* ==========================================================
   CHART BOX
========================================================== */

.st-key-chart_left,
.st-key-chart_right {

    background: #192138;

    border:
        1px solid
        #35405B;

    border-radius: 30px;

    overflow: hidden;
}


.chart-head {

    padding:
        16px 17px 0 17px;
}


.chart-title {

    color: white;

    font-size: 15px;

    font-weight: 800;

    margin-bottom: 4px;
}


.chart-sub {

    color: #9299AA;

    font-size: 9px;
}


/* ==========================================================
   POLICY BOX
========================================================== */

.policy-box {

    margin-top: 20px;

    background: #27324F;

    color: white;

    padding:
        14px 18px;

    font-size: 11px;

    line-height: 1.6;
}

</style>
"""
)


# ============================================================
# TOP NAVIGATION
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
        gap="small",
    )


    with logo:

        if st.button(
            "SAFER",
            key="nav_logo",
        ):
            go_main()


    with n1:

        if st.button(
            "인구",
            key="nav_population",
            use_container_width=True,
        ):
            go_people()


    with n2:

        if st.button(
            "자동차",
            key="nav_car",
            use_container_width=True,
        ):
            go_car()


    with n3:

        if st.button(
            "교통사고",
            key="nav_accident",
            use_container_width=True,
        ):
            go_accident()


    with n4:

        if st.button(
            "제도",
            key="nav_policy",
            use_container_width=True,
        ):
            go_policy()


    with n5:

        if st.button(
            "FAQ",
            key="nav_faq",
            use_container_width=True,
        ):
            go_faq()


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
# MAIN
# ============================================================

with st.container(key="main_panel"):

    left, right = st.columns(
        [1.08, 1],
        gap="large",
    )


    # ========================================================
    # LEFT
    # ========================================================

    with left:

        st.html(
            """
            <div class="hero-area">

                <div class="hero-title">
                    위험을<br>
                    데이터로 읽다
                </div>

                <div class="hero-desc">
                    SAFER는 인구·자동차·교통사고·제도 데이터를 연결해<br>
                    지역별 고령운전자 위험과 정책 필요도를 시각화합니다.
                </div>

                <div class="risk-line"></div>

            </div>
            """
        )


        with st.container(key="quick_menu"):

            c1, c2, c3, c4, c5 = st.columns(
                5,
                gap="small",
            )


            # =================================================
            # 인구
            # =================================================

            with c1:

                if st.button(
                    "👥\n\n인구",
                    key="card_population",
                    use_container_width=True,
                ):
                    go_people()

                st.html(
                    """
                    <div class="quick-caption">
                        지역별 / 세대
                    </div>
                    """
                )


            # =================================================
            # 자동차
            # =================================================

            with c2:

                if st.button(
                    "🚗\n\n자동차",
                    key="card_car",
                    use_container_width=True,
                ):
                    go_car()

                st.html(
                    """
                    <div class="quick-caption">
                        면허 / 등록 / 반납
                    </div>
                    """
                )


            # =================================================
            # 교통사고
            # =================================================

            with c3:

                if st.button(
                    "⚠️\n\n교통사고",
                    key="card_accident",
                    use_container_width=True,
                ):
                    go_accident()

                st.html(
                    """
                    <div class="quick-caption">
                        사고유형 / 시간 / 지역
                    </div>
                    """
                )


            # =================================================
            # 제도
            # =================================================

            with c4:

                if st.button(
                    "📋\n\n제도",
                    key="card_policy",
                    use_container_width=True,
                ):
                    go_policy()

                st.html(
                    """
                    <div class="quick-caption">
                        교육 / 정책 / 지원
                    </div>
                    """
                )


            # =================================================
            # FAQ
            # =================================================

            with c5:

                if st.button(
                    "❓\n\nFAQ",
                    key="card_faq",
                    use_container_width=True,
                ):
                    go_faq()

                st.html(
                    """
                    <div class="quick-caption">
                        검색 / 카테고리
                    </div>
                    """
                )


    # ========================================================
    # RIGHT
    # ========================================================

    with right:

        with st.container(key="future_panel"):

            st.html(
                """
                <div class="future-title">
                    미래 정책 관심지역
                </div>

                <div class="future-sub">
                    지역별 인구·자동차·교통사고 데이터를 기반으로
                    향후 정책 우선지역을 분석합니다.
                </div>
                """
            )


            chart1, chart2 = st.columns(
                2,
                gap="medium",
            )


            # =================================================
            # BAR
            # =================================================

            with chart1:

                with st.container(
                    key="chart_left"
                ):

                    st.html(
                        """
                        <div class="chart-head">

                            <div class="chart-title">
                                관심지역 Top
                            </div>

                            <div class="chart-sub">
                                X축: 지역 / Y축: 위험 점수
                            </div>

                        </div>
                        """
                    )


                    regions = [
                        "전남",
                        "경북",
                        "강원",
                        "전북",
                    ]

                    scores = [
                        89,
                        82,
                        76,
                        70,
                    ]


                    fig = go.Figure(
                        go.Bar(
                            x=regions,
                            y=scores,
                            marker_color=[
                                "#73B99C",
                                "#D6A45B",
                                "#C86C50",
                                "#6DAF98",
                            ],
                        )
                    )


                    fig.update_layout(

                        height=215,

                        margin=dict(
                            l=10,
                            r=10,
                            t=10,
                            b=25,
                        ),

                        paper_bgcolor="#192138",

                        plot_bgcolor="#192138",

                        showlegend=False,

                        font=dict(
                            color="#B9BFCC",
                            size=9,
                        ),
                    )


                    fig.update_yaxes(
                        visible=False
                    )

                    fig.update_xaxes(
                        showgrid=False
                    )


                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                        config={
                            "displayModeBar": False
                        },
                    )


            # =================================================
            # LINE
            # =================================================

            with chart2:

                with st.container(
                    key="chart_right"
                ):

                    st.html(
                        """
                        <div class="chart-head">

                            <div class="chart-title">
                                2035 전망
                            </div>

                            <div class="chart-sub">
                                X축: 연도 / Y축: 위험지수
                            </div>

                        </div>
                        """
                    )


                    fig = go.Figure(
                        go.Scatter(
                            x=[
                                2025,
                                2030,
                                2035,
                            ],

                            y=[
                                38,
                                61,
                                87,
                            ],

                            mode="lines+markers",

                            line=dict(
                                color="#6CC19B",
                                width=4,
                            ),
                        )
                    )


                    fig.update_layout(

                        height=215,

                        margin=dict(
                            l=15,
                            r=15,
                            t=10,
                            b=25,
                        ),

                        paper_bgcolor="#192138",

                        plot_bgcolor="#192138",

                        showlegend=False,

                        font=dict(
                            color="#B9BFCC",
                            size=9,
                        ),
                    )


                    fig.update_yaxes(
                        visible=False
                    )

                    fig.update_xaxes(
                        showgrid=False
                    )


                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                        config={
                            "displayModeBar": False
                        },
                    )


            st.html(
                """
                <div class="policy-box">

                    <b>미래 대응 정책 추천</b><br><br>

                    • 고령운전자 교통안전교육 확대<br>
                    • 면허 자진반납 지원 강화<br>
                    • 고위험 지역 정책 우선 배치<br>
                    • 차량 안전장치 지원 확대

                </div>
                """
            )