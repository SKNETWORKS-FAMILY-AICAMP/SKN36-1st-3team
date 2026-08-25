import sys
from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import text


# ============================================================
# PROJECT ROOT
# SAFE/streamlit/pages/poli/senior_safty_policy.py
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[3]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database.connection import get_engine


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
# DATABASE
# ============================================================

@st.cache_data(ttl=600)
def load_region_policy():

    engine = get_engine()

    query = text(
        """
        SELECT
            id,
            region,
            policy_project,
            base_year,
            target,
            scale,
            content,
            current_stage,
            saas_idea,
            source_url,
            note
        FROM region_old_driver_policy
        ORDER BY region, policy_project
        """
    )

    with engine.connect() as conn:
        return pd.read_sql(query, conn)


# ============================================================
# LOAD
# ============================================================

try:
    df = load_region_policy()

except Exception as e:

    st.error(
        f"MySQL 지역 특화 정책 데이터 조회 실패\n\n{e}"
    )

    st.stop()


# ============================================================
# CLEAN
# ============================================================

TEXT_COLUMNS = [
    "region",
    "policy_project",
    "target",
    "scale",
    "content",
    "current_stage",
    "saas_idea",
    "source_url",
    "note",
]


for col in TEXT_COLUMNS:

    df[col] = (
        df[col]
        .fillna("")
        .astype(str)
        .str.strip()
    )


df["base_year"] = pd.to_numeric(
    df["base_year"],
    errors="coerce"
)


INVALID_VALUES = [
    "",
    "-",
    "nan",
    "None",
    "없음",
]


def safe_text(value, default="-"):

    value = str(value).strip()

    if value in INVALID_VALUES:
        return default

    return value


# ============================================================
# REGION NORMALIZE
# ============================================================

REGION_MAP = {
    "서울특별시": "서울",
    "서울": "서울",

    "부산광역시": "부산",
    "부산": "부산",

    "대구광역시": "대구",
    "대구": "대구",

    "인천광역시": "인천",
    "인천": "인천",

    "광주광역시": "광주",
    "광주": "광주",

    "대전광역시": "대전",
    "대전": "대전",

    "울산광역시": "울산",
    "울산": "울산",

    "세종특별자치시": "세종",
    "세종": "세종",

    "경기도": "경기",
    "경기": "경기",

    "강원특별자치도": "강원",
    "강원도": "강원",
    "강원": "강원",

    "충청북도": "충북",
    "충북": "충북",

    "충청남도": "충남",
    "충남": "충남",

    "전북특별자치도": "전북",
    "전라북도": "전북",
    "전북": "전북",

    "전라남도": "전남",
    "전남": "전남",

    "경상북도": "경북",
    "경북": "경북",

    "경상남도": "경남",
    "경남": "경남",

    "제주특별자치도": "제주",
    "제주": "제주",
}


def normalize_region(value):

    value = str(value).strip()

    return REGION_MAP.get(
        value,
        value
    )


df["region_name"] = (
    df["region"]
    .apply(normalize_region)
)


# ============================================================
# OPTIONS
# ============================================================

regions = sorted(
    [
        value
        for value
        in df["region_name"]
        .dropna()
        .unique()
        .tolist()
        if value not in INVALID_VALUES
    ]
)


years = sorted(
    df["base_year"]
    .dropna()
    .astype(int)
    .unique()
    .tolist(),
    reverse=True
)


stages = sorted(
    [
        value
        for value
        in df["current_stage"]
        .dropna()
        .unique()
        .tolist()
        if value not in INVALID_VALUES
    ]
)


if df.empty:

    st.warning(
        "지역 특화 고령운전자 정책 데이터가 없습니다."
    )

    st.stop()


# ============================================================
# CSS
# ============================================================

st.html(
    """
<style>

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
   NAV
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

    font-size: 18px !important;

    font-weight:
        500 !important;

    min-height:
        44px !important;
}


.st-key-nav_logo button {

    color:
        #27314C !important;

    font-size: 33px !important;

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

.st-key-region_policy_page {

    background:
        #101625;

    border:
        1px solid #34405A;

    border-radius:
        20px;

    padding:
        34px 36px 48px 36px;
}


/* ==========================================================
   HEADER
========================================================== */

.page-path {

    color:
        #D6A348;

    font-size: 15px;

    font-weight:
        800;

    margin-bottom:
        10px;
}


.page-title {

    color:
        #FFFFFF;

    font-size: 44px;

    font-weight:
        900;

    margin-bottom:
        12px;
}


.page-sub {

    color:
        #C3CBD8;

    font-size: 17px;

    line-height:
        1.75;

    margin-bottom:
        25px;
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
   INPUT
========================================================== */

label[data-testid="stWidgetLabel"] p {

    color:
        #E2E7EF !important;

    font-size: 15px !important;

    font-weight:
        700 !important;
}


div[data-baseweb="select"] > div {

    background:
        #F4F5F8 !important;

    color:
        #1C2435 !important;

    min-height:
        46px !important;

    border-radius:
        8px !important;
}


div[data-baseweb="select"] span {

    color:
        #273149 !important;
}


/* ==========================================================
   KPI
========================================================== */

.kpi {

    min-height:
        112px;

    background:
        #192136;

    border:
        1px solid #394560;

    border-radius:
        17px;

    padding:
        18px 20px;
}


.kpi-label {

    color:
        #C4CCD9;

    font-size: 14px;

    margin-bottom:
        15px;
}


.kpi-value {

    color:
        #FFFFFF;

    font-size: 26px;

    font-weight:
        900;

    word-break:
        keep-all;
}


/* ==========================================================
   PANEL
========================================================== */

.st-key-region_rank_panel,
.st-key-stage_panel,
.st-key-year_panel,
.st-key-heatmap_panel,
.st-key-policy_list_panel,
.st-key-saas_panel,
.st-key-note_panel {

    background:
        #182035;

    border:
        1px solid #3A4662;

    border-radius:
        28px;

    padding:
        24px 26px 24px 26px;

    margin-top:
        24px;
}


.panel-title {

    color:
        #FFFFFF;

    font-size: 23px;

    font-weight:
        900;

    margin-bottom:
        8px;
}


.panel-sub {

    color:
        #C8D0DC;

    font-size: 15px;

    line-height:
        1.75;

    margin-bottom:
        12px;
}


.panel-sub b {

    color:
        #FFFFFF;
}


/* ==========================================================
   ANALYSIS
========================================================== */

.analysis-box {

    background:
        #121A2B;

    border:
        1px solid #35415C;

    border-left:
        4px solid #D6A348;

    border-radius:
        7px 15px 15px 7px;

    padding:
        20px 22px;

    margin-top:
        18px;

    color:
        #E5EAF2;

    font-size: 15px;

    line-height:
        1.95;
}


.analysis-title {

    color:
        #F3C867;

    font-size: 18px;

    font-weight:
        900;

    margin-bottom:
        10px;
}


.analysis-box b {

    color:
        #FFFFFF;
}


/* ==========================================================
   POLICY CARD
========================================================== */

.policy-card {

    background:
        #121A2B;

    border:
        1px solid #3A4662;

    border-radius:
        18px;

    padding:
        22px 23px;

    margin:
        14px 0;
}


.policy-region {

    display:
        inline-block;

    padding:
        5px 10px;

    border-radius:
        999px;

    background:
        rgba(214,163,72,.12);

    border:
        1px solid rgba(214,163,72,.32);

    color:
        #E7BC67;

    font-size: 13px;

    font-weight:
        900;

    margin-bottom:
        12px;
}


.policy-name {

    color:
        #FFFFFF;

    font-size: 22px;

    font-weight:
        900;

    margin-bottom:
        12px;
}


.policy-meta {

    color:
        #C9D0DB;

    font-size: 14px;

    line-height:
        1.9;

    margin-bottom:
        13px;
}


.policy-meta b {

    color:
        #FFFFFF;
}


.policy-content {

    color:
        #DDE3EC;

    font-size: 15px;

    line-height:
        1.9;

    padding-top:
        14px;

    border-top:
        1px solid #2E3951;
}


/* ==========================================================
   STAGE
========================================================== */

.stage-active {

    color:
        #88D5AE;

    font-weight:
        900;
}


.stage-etc {

    color:
        #E7BC67;

    font-weight:
        900;
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
        14px;

    border-top:
        1px solid #2E3951;
}


.source-label {

    color:
        #8F9AAF;

    font-size: 14px;

    font-weight:
        800;
}


.source-link {

    display:
        inline-block;

    padding:
        6px 11px;

    background:
        rgba(214,163,72,.10);

    border:
        1px solid rgba(214,163,72,.35);

    border-radius:
        7px;

    color:
        #F0C66E !important;

    font-size: 14px;

    font-weight:
        800;

    text-decoration:
        none !important;
}


.source-link:hover {

    background:
        rgba(214,163,72,.20);

    border-color:
        #D6A348;
}


.source-empty {

    color:
        #737E93;

    font-size: 14px;
}


/* ==========================================================
   SAFER IDEA
========================================================== */

.saas-card {

    background:
        linear-gradient(
            120deg,
            #172338 0%,
            #1B2941 62%,
            #302D28 100%
        );

    border:
        1px solid #A77E35;

    border-radius:
        20px;

    padding:
        23px 24px;

    margin:
        14px 0;

    position:
        relative;

    overflow:
        hidden;
}


.saas-card::after {

    content:
        "SAFER";

    position:
        absolute;

    right:
        18px;

    top:
        4px;

    font-size: 57px;

    font-weight:
        900;

    color:
        rgba(214,163,72,.05);
}


.saas-label {

    color:
        #E7B955;

    font-size: 13px;

    font-weight:
        900;

    letter-spacing:
        1.3px;

    margin-bottom:
        10px;
}


.saas-region {

    color:
        #AAB7CB;

    font-size: 13px;

    margin-bottom:
        5px;
}


.saas-policy {

    color:
        #FFFFFF;

    font-size: 19px;

    font-weight:
        900;

    margin-bottom:
        10px;
}


.saas-idea {

    color:
        #E1E6EE;

    font-size: 15px;

    line-height:
        1.9;
}


/* ==========================================================
   NOTE
========================================================== */

.note-card {

    background:
        #121A2B;

    border:
        1px solid #35415C;

    border-radius:
        16px;

    padding:
        18px 20px;

    margin:
        10px 0;
}


.note-title {

    color:
        #FFFFFF;

    font-size: 16px;

    font-weight:
        900;

    margin-bottom:
        7px;
}


.note-text {

    color:
        #BCC6D5;

    font-size: 14px;

    line-height:
        1.75;
}


/* ==========================================================
   SECTION
========================================================== */

.section-title {
    color: #FFFFFF;
    font-size: 25px;
    font-weight: 900;
    margin-top: 30px;
    margin-bottom: 8px;
}

.section-sub {
    color: #C8D0DC;
    font-size: 17px;
    line-height: 1.75;
    margin-bottom: 18px;
}

.section-divider {
    margin-top: 30px;
    padding-top: 2px;
    border-top: 1px solid #2F3A52;
}

.st-key-policy_compare_btn button {
    background: #D6A348 !important;
    color: #172035 !important;
    border: 1px solid #E7BC67 !important;
    border-radius: 9px !important;
    font-size: 17px !important;
    font-weight: 900 !important;
    min-height: 44px !important;
}



/* ==========================================================
   GOVERNMENT SECTION
========================================================== */

.section-heading {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 34px 0 14px 4px;
    color: #FFFFFF;
    font-size: 25px;
    font-weight: 900;
    letter-spacing: -1px;
}

.section-heading::before {
    content: "";
    width: 5px;
    height: 27px;
    border-radius: 4px;
    background: #D9A64A;
}

.section-sub-gov {
    color: #AEB8C8;
    font-size: 13px;
    line-height: 1.75;
    margin: -4px 0 16px 4px;
}

.section-divider-gov {
    height: 1px;
    margin: 38px 0 6px 0;
    background: linear-gradient(
        90deg,
        rgba(217,166,74,0),
        rgba(217,166,74,.9) 18%,
        rgba(92,107,137,.9) 82%,
        rgba(92,107,137,0)
    );
}


/* ==========================================================
   KPI
========================================================== */

.gov-kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-top: 10px;
    margin-bottom: 8px;
}

.gov-kpi {
    background: #192136;
    border: 1px solid #394560;
    border-radius: 17px;
    padding: 18px 20px;
    min-height: 112px;
}

.gov-kpi-label {
    color: #C4CCD9;
    font-size: 12px;
    margin-bottom: 15px;
}

.gov-kpi-value {
    color: #FFFFFF;
    font-size: 24px;
    font-weight: 900;
    word-break: keep-all;
}

.gov-kpi-value.gold {
    color: #F1C66A;
}


/* ==========================================================
   POLICY REVIEW 2-COLUMN
========================================================== */

.st-key-region_policy_detail_column,
.st-key-region_policy_recommend_column {
    background: #151D30;
    border: 1px solid #3A4662;
    border-radius: 22px;
    padding: 22px 22px 24px 22px;
    margin-top: 8px;
    min-height: 190px;
}

.review-box-title {
    color: #FFFFFF;
    font-size: 21px;
    font-weight: 900;
    margin-bottom: 8px;
}

.review-box-sub {
    color: #B8C2D2;
    font-size: 12px;
    line-height: 1.75;
    min-height: 64px;
    margin-bottom: 14px;
}

.review-box-sub b {
    color: #F3C867;
}


/* ==========================================================
   COLLAPSE BUTTONS
========================================================== */

.st-key-region_policy_detail_toggle button,
.st-key-region_policy_recommend_toggle button,
.st-key-region_compare_toggle button,
.st-key-region_note_toggle button,
.st-key-region_detail_toggle button,
.st-key-region_policy_cards_more button,
.st-key-region_policy_ideas_more button {

    width: 100% !important;
    min-height: 48px !important;

    background: #192238 !important;
    color: #E7EAF0 !important;

    border: 1px solid #414D69 !important;
    border-radius: 11px !important;

    box-shadow: none !important;

    font-size: 13px !important;
    font-weight: 800 !important;
}

.st-key-region_policy_detail_toggle button,
.st-key-region_policy_recommend_toggle button,
.st-key-region_compare_toggle button,
.st-key-region_note_toggle button,
.st-key-region_detail_toggle button {
    justify-content: flex-start !important;
    padding-left: 16px !important;
}

.st-key-region_policy_detail_toggle button *,
.st-key-region_policy_recommend_toggle button *,
.st-key-region_compare_toggle button *,
.st-key-region_note_toggle button *,
.st-key-region_detail_toggle button *,
.st-key-region_policy_cards_more button *,
.st-key-region_policy_ideas_more button * {

    color: #E7EAF0 !important;
    -webkit-text-fill-color: #E7EAF0 !important;
    opacity: 1 !important;
}

.st-key-region_policy_detail_toggle button:hover,
.st-key-region_policy_recommend_toggle button:hover,
.st-key-region_compare_toggle button:hover,
.st-key-region_note_toggle button:hover,
.st-key-region_detail_toggle button:hover,
.st-key-region_policy_cards_more button:hover,
.st-key-region_policy_ideas_more button:hover {

    background: #232D46 !important;
    border-color: #D6A348 !important;
}

.st-key-region_policy_detail_toggle button:hover *,
.st-key-region_policy_recommend_toggle button:hover *,
.st-key-region_compare_toggle button:hover *,
.st-key-region_note_toggle button:hover *,
.st-key-region_detail_toggle button:hover *,
.st-key-region_policy_cards_more button:hover *,
.st-key-region_policy_ideas_more button:hover * {

    color: #F1C66A !important;
    -webkit-text-fill-color: #F1C66A !important;
}


/* ==========================================================
   COLLAPSE BODY
========================================================== */

.st-key-region_policy_detail_body,
.st-key-region_policy_recommend_body,
.st-key-region_compare_body,
.st-key-region_note_body,
.st-key-region_detail_body {
    background: #182035;
    border: 1px solid #394560;
    border-radius: 14px;
    padding: 18px 20px 20px 20px;
    margin-top: 10px;
}


/* ==========================================================
   COMPACT CARDS
========================================================== */

.compact-region-policy-card {
    padding: 18px 18px;
    margin: 10px 0;
}

.compact-region-policy-card .policy-name {
    font-size: 17px;
}

.compact-region-policy-card .policy-meta,
.compact-region-policy-card .policy-content {
    font-size: 12px;
}

.compact-region-saas-card {
    padding: 18px 18px;
    margin: 10px 0;
}

.compact-region-saas-card .saas-policy {
    font-size: 15px;
}

.compact-region-saas-card .saas-idea {
    font-size: 12px;
}


/* ==========================================================
   DARK TABLE
========================================================== */

.region-dark-table-wrap {
    width: 100%;
    max-height: 560px;
    overflow-y: auto;
    overflow-x: auto;

    background: #182035;
    border: 1px solid #3A4662;
    border-radius: 12px;
}

.region-dark-table {
    width: 100%;
    min-width: 1500px;
    border-collapse: collapse;

    background: #182035;
    color: #E7EAF0;
    font-size: 12px;
}

.region-dark-table thead {
    position: sticky;
    top: 0;
    z-index: 3;
}

.region-dark-table th {
    background: #202A42;
    color: #D6A348;
    font-weight: 900;
    text-align: center;
    padding: 13px 14px;
    border-bottom: 1px solid #4A5670;
    white-space: nowrap;
}

.region-dark-table td {
    background: #182035;
    color: #E7EAF0;
    padding: 11px 13px;
    border-bottom: 1px solid #303B55;
    vertical-align: top;
    line-height: 1.65;
}

.region-dark-table tbody tr:nth-child(even) td {
    background: #1B243A;
}

.region-dark-table tbody tr:hover td {
    background: #222D47;
    color: #FFFFFF;
}

.region-dark-table a {
    color: #F1C66A !important;
    font-weight: 800;
    text-decoration: none;
}

@media(max-width:1000px) {
    .gov-kpi-grid {
        grid-template-columns: 1fr 1fr;
    }

    .review-box-sub {
        min-height: auto;
    }
}

</style>
"""
)


# ============================================================
# NAV
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

with st.container(key="region_policy_page"):

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
                정책·제도 &gt; 지역 특화 고령운전자 안전정책
            </div>

            <div class="page-title">
                지역 특화 고령운전자 안전정책
            </div>

            <div class="page-sub">
                각 지역에서 추진 중인 고령운전자 교통안전 정책을 비교하고,
                정책 대상·규모·현재 단계와 지역별 정책 분포를 분석합니다.
                정책 데이터를 기반으로 SAFER 서비스 활용 아이디어도 함께 제공합니다.
            </div>
            """
        )


    with head_right:

        with st.container(key="back_policy"):

            if st.button(
                "← 정책·제도",
                use_container_width=True
            ):
                go_policy()


    # ========================================================
    # REGION SELECT
    # ========================================================

    selected_region = st.selectbox(
        "지역 선택",
        ["전체"] + regions,
        key="region_policy_region"
    )


    # ========================================================
    # 지역 선택 변경 감지
    # 특정 지역을 조회하면 아래 정책 상세가 자동으로 펼쳐지도록 처리
    # ========================================================

    previous_region = st.session_state.get(
        "previous_region_policy_region"
    )


    if previous_region != selected_region:

        st.session_state[
            "previous_region_policy_region"
        ] = selected_region

        st.session_state[
            "show_region_policy_detail"
        ] = True

        # 지역을 변경해도 SAFER 정책 추천은 펼친 상태 유지
        st.session_state[
            "show_region_policy_recommend"
        ] = True

        # 전체보기 상태 초기화
        st.session_state[
            "show_all_region_policy_cards"
        ] = False

        st.session_state[
            "show_all_region_policy_ideas"
        ] = False


    filtered_df = df.copy()

    if selected_region != "전체":
        filtered_df = filtered_df[
            filtered_df["region_name"] == selected_region
        ]

    # ========================================================
    # REGION SUMMARY
    # ========================================================

    region_summary = (
        df[df["region_name"] != ""]
        .groupby("region_name", as_index=False)
        .size()
        .rename(columns={"size": "policy_count"})
        .sort_values("policy_count", ascending=False)
        .reset_index(drop=True)
    )

    total_policy = len(df)

    total_regions = (
        df["region_name"]
        .replace("", pd.NA)
        .nunique()
    )

    if not region_summary.empty:
        top_region = str(region_summary.iloc[0]["region_name"])
        top_region_count = int(region_summary.iloc[0]["policy_count"])
    else:
        top_region = "-"
        top_region_count = 0

    avg_policy = (
        total_policy / total_regions
        if total_regions > 0
        else 0
    )

    top3_regions = region_summary.head(3)

    top3_names = (
        ", ".join(top3_regions["region_name"].astype(str).tolist())
        if not top3_regions.empty
        else "-"
    )

    top3_count = int(top3_regions["policy_count"].sum())

    top3_share = (
        top3_count / total_policy * 100
        if total_policy > 0
        else 0
    )

    # ========================================================
    # KPI / POLICY STATUS OVERVIEW
    # ========================================================

    selected_policy_count = len(
        filtered_df
    )


    selected_idea_count = int(
        filtered_df[
            "saas_idea"
        ]
        .replace(
            "",
            pd.NA
        )
        .notna()
        .sum()
    )


    selected_stage_count = (
        filtered_df[
            "current_stage"
        ]
        .replace(
            "",
            pd.NA
        )
        .nunique()
    )


    selected_label = (
        selected_region
        if selected_region != "전체"
        else "전국"
    )


    st.html(
        f"""
        <div class="gov-kpi-grid">

            <div class="gov-kpi">
                <div class="gov-kpi-label">
                    현재 조회 지역
                </div>
                <div class="gov-kpi-value gold">
                    {selected_label}
                </div>
            </div>

            <div class="gov-kpi">
                <div class="gov-kpi-label">
                    조회 정책 수
                </div>
                <div class="gov-kpi-value">
                    {selected_policy_count:,}개
                </div>
            </div>

            <div class="gov-kpi">
                <div class="gov-kpi-label">
                    추진단계 유형
                </div>
                <div class="gov-kpi-value">
                    {selected_stage_count:,}개
                </div>
            </div>

            <div class="gov-kpi">
                <div class="gov-kpi-label">
                    SAFER 추천 아이디어
                </div>
                <div class="gov-kpi-value">
                    {selected_idea_count:,}건
                </div>
            </div>

        </div>
        """
    )


    # ========================================================
    # POLICY REVIEW
    # ========================================================

    st.html(
        """
        <div class="section-divider-gov"></div>
        <div class="section-heading">정책 검토</div>
        <div class="section-sub-gov">
            실제 지역 정책과 SAFER 활용 제안을 나란히 비교하여 검토합니다.
        </div>
        """
    )


    review_left, review_right = st.columns(
        [1, 1],
        gap="medium"
    )


    # ========================================================
    # LEFT : REGION POLICY DETAIL
    # ========================================================

    with review_left:

        with st.container(
            key="region_policy_detail_column"
        ):

            st.html(
                f"""
                <div class="review-box-title">
                    지역 정책 세부 현황
                </div>

                <div class="review-box-sub">
                    선택한 지역의 정책 대상·규모·현재 단계·주요 내용을 확인합니다.
                    현재 <b>{len(filtered_df):,}개</b> 정책이 조회됩니다.
                    {f"<br><span style='color:#F3C867;font-weight:800;'>{selected_region} 정책 조회 결과가 아래에 표시됩니다.</span>" if selected_region != "전체" else ""}
                </div>
                """
            )


            if "show_region_policy_detail" not in st.session_state:

                st.session_state[
                    "show_region_policy_detail"
                ] = True


            with st.container(
                key="region_policy_detail_toggle"
            ):

                policy_open = st.session_state[
                    "show_region_policy_detail"
                ]


                policy_label = (
                    "▲ 지역 정책 세부 현황 접기"
                    if policy_open
                    else "▼ 지역 정책 세부 현황 펼치기"
                )


                if st.button(
                    policy_label,
                    key="region_policy_detail_button",
                    use_container_width=True
                ):

                    st.session_state[
                        "show_region_policy_detail"
                    ] = not policy_open

                    st.rerun()


            if st.session_state[
                "show_region_policy_detail"
            ]:

                with st.container(
                    key="region_policy_detail_body"
                ):

                    if filtered_df.empty:

                        st.info(
                            "현재 조건에 해당하는 정책이 없습니다."
                        )

                    else:

                        if "show_all_region_policy_cards" not in st.session_state:

                            st.session_state[
                                "show_all_region_policy_cards"
                            ] = False


                        display_policy_df = (
                            filtered_df
                            if st.session_state[
                                "show_all_region_policy_cards"
                            ]
                            else filtered_df.head(5)
                        )


                        for _, row in display_policy_df.iterrows():

                            region = safe_text(
                                row["region_name"]
                            )

                            policy = safe_text(
                                row["policy_project"]
                            )

                            target = safe_text(
                                row["target"]
                            )

                            scale = safe_text(
                                row["scale"]
                            )

                            content = safe_text(
                                row["content"]
                            )

                            current_stage = safe_text(
                                row["current_stage"]
                            )

                            source_url = safe_text(
                                row["source_url"],
                                default=""
                            )

                            base_year = (
                                f"{int(row['base_year'])}년"
                                if pd.notna(
                                    row["base_year"]
                                )
                                else "-"
                            )


                            stage_class = (
                                "stage-active"
                                if any(
                                    word in current_stage
                                    for word in [
                                        "시행",
                                        "운영",
                                        "진행",
                                        "추진",
                                        "확대",
                                    ]
                                )
                                else "stage-etc"
                            )


                            if source_url:

                                source_html = f"""
                                <div class="policy-source">

                                    <span class="source-label">
                                        출처
                                    </span>

                                    <a
                                        href="{source_url}"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        class="source-link"
                                    >
                                        원문 보기 ↗
                                    </a>

                                </div>
                                """

                            else:

                                source_html = """
                                <div class="policy-source">

                                    <span class="source-label">
                                        출처
                                    </span>

                                    <span class="source-empty">
                                        출처 정보 없음
                                    </span>

                                </div>
                                """


                            st.html(
                                f"""
                                <div class="policy-card compact-region-policy-card">

                                    <div class="policy-region">
                                        {region}
                                    </div>

                                    <div class="policy-name">
                                        {policy}
                                    </div>

                                    <div class="policy-meta">

                                        <b>기준연도</b> :
                                        {base_year}

                                        <br>

                                        <b>현재 단계</b> :
                                        <span class="{stage_class}">
                                            {current_stage}
                                        </span>

                                        <br>

                                        <b>정책 대상</b> :
                                        {target}

                                        <br>

                                        <b>정책 규모</b> :
                                        {scale}

                                    </div>

                                    <div class="policy-content">
                                        {content}
                                    </div>

                                    {source_html}

                                </div>
                                """
                            )


                        if len(filtered_df) > 5:

                            more_label = (
                                "정책 목록 줄이기"
                                if st.session_state[
                                    "show_all_region_policy_cards"
                                ]
                                else f"전체 {len(filtered_df):,}개 정책 보기"
                            )


                            with st.container(
                                key="region_policy_cards_more"
                            ):

                                if st.button(
                                    more_label,
                                    key="region_policy_cards_more_button",
                                    use_container_width=True
                                ):

                                    st.session_state[
                                        "show_all_region_policy_cards"
                                    ] = not st.session_state[
                                        "show_all_region_policy_cards"
                                    ]

                                    st.rerun()


    # ========================================================
    # RIGHT : SAFER IDEA
    # ========================================================

    with review_right:

        with st.container(
            key="region_policy_recommend_column"
        ):

            idea_df = (
                filtered_df[
                    ~filtered_df[
                        "saas_idea"
                    ].isin(
                        INVALID_VALUES
                    )
                ]
                .copy()
            )


            st.html(
                f"""
                <div class="review-box-title">
                    SAFER 지역 정책 추천
                </div>

                <div class="review-box-sub">
                    기존 지역 정책을 바탕으로 SAFER에서 활용할 수 있는
                    서비스·정책 제안 <b>{len(idea_df):,}건</b>을 확인합니다.

                    <br>

                    <span style="color:#F3C867;font-weight:800;">
                        ※ 실제 시행정책이 아닌 SAFER 활용 제안입니다.
                    </span>
                </div>
                """
            )


            if "show_region_policy_recommend" not in st.session_state:

                st.session_state[
                    "show_region_policy_recommend"
                ] = True


            with st.container(
                key="region_policy_recommend_toggle"
            ):

                recommend_open = st.session_state[
                    "show_region_policy_recommend"
                ]


                recommend_label = (
                    "▲ SAFER 지역 정책 추천 접기"
                    if recommend_open
                    else "▼ SAFER 지역 정책 추천 펼치기"
                )


                if st.button(
                    recommend_label,
                    key="region_policy_recommend_button",
                    use_container_width=True
                ):

                    st.session_state[
                        "show_region_policy_recommend"
                    ] = not recommend_open

                    st.rerun()


            if st.session_state[
                "show_region_policy_recommend"
            ]:

                with st.container(
                    key="region_policy_recommend_body"
                ):

                    if idea_df.empty:

                        st.info(
                            "현재 조건에 해당하는 SAFER 추천 아이디어가 없습니다."
                        )

                    else:

                        if "show_all_region_policy_ideas" not in st.session_state:

                            st.session_state[
                                "show_all_region_policy_ideas"
                            ] = False


                        display_idea_df = (
                            idea_df
                            if st.session_state[
                                "show_all_region_policy_ideas"
                            ]
                            else idea_df.head(5)
                        )


                        for _, row in display_idea_df.iterrows():

                            st.html(
                                f"""
                                <div class="saas-card compact-region-saas-card">

                                    <div class="saas-label">
                                        SAFER RECOMMENDATION
                                    </div>

                                    <div class="saas-region">
                                        {safe_text(row["region_name"])}
                                    </div>

                                    <div class="saas-policy">
                                        {safe_text(row["policy_project"])}
                                    </div>

                                    <div class="saas-idea">
                                        {safe_text(row["saas_idea"])}
                                    </div>

                                </div>
                                """
                            )


                        if len(idea_df) > 5:

                            idea_more_label = (
                                "추천 목록 줄이기"
                                if st.session_state[
                                    "show_all_region_policy_ideas"
                                ]
                                else f"전체 {len(idea_df):,}개 추천 보기"
                            )


                            with st.container(
                                key="region_policy_ideas_more"
                            ):

                                if st.button(
                                    idea_more_label,
                                    key="region_policy_ideas_more_button",
                                    use_container_width=True
                                ):

                                    st.session_state[
                                        "show_all_region_policy_ideas"
                                    ] = not st.session_state[
                                        "show_all_region_policy_ideas"
                                    ]

                                    st.rerun()


    st.html(
        """
        <div class="section-divider-gov"></div>
        """
    )


    # ========================================================
    # ANALYSIS SUMMARY
    # ========================================================

    st.html(
        """
        <div class="section-heading">정책 현황 요약</div>
        <div class="section-sub-gov">
            지역별 정책 보유 수준과 현재 선택 지역의 정책 현황을 먼저 확인합니다.
        </div>
        """
    )


    st.html(
        f"""
        <div class="analysis-box">

            <div class="analysis-title">
                지역 특화 고령운전자 정책 분석 요약
            </div>

            현재 DB에는
            <b>{total_regions:,}개 지역</b>에서
            총 <b>{total_policy:,}개 정책</b>이 확인됩니다.

            <br>

            지역당 평균 정책 수는
            약 <b>{avg_policy:.1f}개</b>입니다.

            <br>

            가장 많은 정책이 등록된 지역은
            <b>{top_region}</b>으로
            총 <b>{top_region_count:,}개</b>가 확인됩니다.

            <br>

            정책 수 상위 지역은
            <b>{top3_names}</b>이며,
            전체 수집 정책의 약
            <b>{top3_share:.1f}%</b>를 차지합니다.

            <br><br>

            ※ 본 수치는 현재
            <b>region_old_driver_policy</b> 테이블에 수집된 데이터를
            기준으로 한 비교 결과입니다.

        </div>
        """
    )


    # ========================================================
    # REGION COMPARISON
    # ========================================================

    st.html(
        """
        <div class="section-divider-gov"></div>
        <div class="section-heading">지역 정책 비교</div>
        <div class="section-sub-gov">
            필요한 경우 2~4개 지역을 선택해 정책 내용을 비교합니다.
        </div>
        """
    )


    if "show_region_compare" not in st.session_state:

        st.session_state[
            "show_region_compare"
        ] = False


    with st.container(
        key="region_compare_toggle"
    ):

        compare_open = st.session_state[
            "show_region_compare"
        ]


        compare_label = (
            "▲ 지역별 정책 비교 닫기"
            if compare_open
            else "▼ 지역별 정책 비교 보기"
        )


        if st.button(
            compare_label,
            key="region_compare_toggle_button",
            use_container_width=True
        ):

            st.session_state[
                "show_region_compare"
            ] = not compare_open

            st.rerun()


    if st.session_state[
        "show_region_compare"
    ]:

        with st.container(
            key="region_compare_body"
        ):

            compare_regions = st.multiselect(
                "비교 지역",
                regions,
                max_selections=4,
                placeholder="비교할 지역을 2~4개 선택하세요",
                key="region_policy_compare"
            )


            compare_btn_col, _ = st.columns(
                [1, 3]
            )


            with compare_btn_col:

                compare_clicked = st.button(
                    "비교하기",
                    key="policy_compare_btn",
                    use_container_width=True
                )


            if compare_clicked:

                if len(compare_regions) < 2:

                    st.warning(
                        "비교할 지역을 2개 이상 선택해주세요."
                    )

                else:

                    compare_df = (
                        df[
                            df[
                                "region_name"
                            ].isin(
                                compare_regions
                            )
                        ][
                            [
                                "region_name",
                                "policy_project",
                                "base_year",
                                "target",
                                "scale",
                                "current_stage",
                                "content",
                            ]
                        ]
                        .copy()
                    )


                    compare_df[
                        "base_year"
                    ] = (
                        pd.to_numeric(
                            compare_df[
                                "base_year"
                            ],
                            errors="coerce"
                        )
                        .astype(
                            "Int64"
                        )
                    )


                    compare_rows = ""


                    for _, row in compare_df.iterrows():

                        year_text = (
                            f"{int(row['base_year'])}년"
                            if pd.notna(
                                row["base_year"]
                            )
                            else "-"
                        )


                        compare_rows += f"""
                            <tr>
                                <td>{safe_text(row["region_name"])}</td>
                                <td>{safe_text(row["policy_project"])}</td>
                                <td>{year_text}</td>
                                <td>{safe_text(row["target"])}</td>
                                <td>{safe_text(row["scale"])}</td>
                                <td>{safe_text(row["current_stage"])}</td>
                                <td>{safe_text(row["content"])}</td>
                            </tr>
                        """


                    st.html(
                        f"""
                        <div class="region-dark-table-wrap">

                            <table class="region-dark-table">

                                <thead>
                                    <tr>
                                        <th>지역</th>
                                        <th>정책사업</th>
                                        <th>기준연도</th>
                                        <th>정책대상</th>
                                        <th>정책규모</th>
                                        <th>현재단계</th>
                                        <th>정책내용</th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {compare_rows}
                                </tbody>

                            </table>

                        </div>
                        """
                    )


    # ========================================================
    # SUPPORTING INFORMATION
    # ========================================================

    st.html(
        """
        <div class="section-divider-gov"></div>
        <div class="section-heading">정책 활용·참고 정보</div>
        <div class="section-sub-gov">
            참고사항과 원본 데이터를 필요할 때만 펼쳐서 확인합니다.
        </div>
        """
    )


    # ========================================================
    # NOTE - COLLAPSIBLE
    # ========================================================

    if "show_region_note" not in st.session_state:

        st.session_state[
            "show_region_note"
        ] = False


    with st.container(
        key="region_note_toggle"
    ):

        note_open = st.session_state[
            "show_region_note"
        ]


        note_label = (
            "▲ 정책 참고사항 닫기"
            if note_open
            else "▼ 정책 참고사항 보기"
        )


        if st.button(
            note_label,
            key="region_note_button",
            use_container_width=True
        ):

            st.session_state[
                "show_region_note"
            ] = not note_open

            st.rerun()


    if st.session_state[
        "show_region_note"
    ]:

        with st.container(
            key="region_note_body"
        ):

            note_df = (
                filtered_df[
                    ~filtered_df[
                        "note"
                    ].isin(
                        INVALID_VALUES
                    )
                ]
                .copy()
            )


            if note_df.empty:

                st.info(
                    "현재 조건에 별도로 기록된 참고사항이 없습니다."
                )

            else:

                for _, row in note_df.iterrows():

                    st.html(
                        f"""
                        <div class="note-card">

                            <div class="note-title">
                                {safe_text(row["region_name"])}
                                ·
                                {safe_text(row["policy_project"])}
                            </div>

                            <div class="note-text">
                                {safe_text(row["note"])}
                            </div>

                        </div>
                        """
                    )


    # ========================================================
    # DETAIL TABLE - COLLAPSIBLE
    # ========================================================

    st.write("")


    if "show_region_detail" not in st.session_state:

        st.session_state[
            "show_region_detail"
        ] = False


    with st.container(
        key="region_detail_toggle"
    ):

        detail_open = st.session_state[
            "show_region_detail"
        ]


        detail_label = (
            "▲ 지역 특화 고령운전자 정책 데이터 닫기"
            if detail_open
            else "▼ 지역 특화 고령운전자 정책 데이터 상세 보기"
        )


        if st.button(
            detail_label,
            key="region_detail_button",
            use_container_width=True
        ):

            st.session_state[
                "show_region_detail"
            ] = not detail_open

            st.rerun()


    if st.session_state[
        "show_region_detail"
    ]:

        with st.container(
            key="region_detail_body"
        ):

            detail_df = (
                filtered_df[
                    [
                        "region_name",
                        "policy_project",
                        "base_year",
                        "target",
                        "scale",
                        "content",
                        "current_stage",
                        "saas_idea",
                        "note",
                        "source_url",
                    ]
                ]
                .copy()
                .reset_index(
                    drop=True
                )
            )


            detail_rows = ""


            for _, row in detail_df.iterrows():

                base_year_text = (
                    f"{int(row['base_year'])}년"
                    if pd.notna(
                        row["base_year"]
                    )
                    else "-"
                )


                source_value = safe_text(
                    row["source_url"],
                    default=""
                )


                source_html = (
                    f'<a href="{source_value}" target="_blank" '
                    f'rel="noopener noreferrer">원문 보기 ↗</a>'
                    if source_value
                    else "-"
                )


                detail_rows += f"""
                    <tr>
                        <td>{safe_text(row["region_name"])}</td>
                        <td>{safe_text(row["policy_project"])}</td>
                        <td>{base_year_text}</td>
                        <td>{safe_text(row["target"])}</td>
                        <td>{safe_text(row["scale"])}</td>
                        <td>{safe_text(row["content"])}</td>
                        <td>{safe_text(row["current_stage"])}</td>
                        <td>{safe_text(row["saas_idea"])}</td>
                        <td>{safe_text(row["note"])}</td>
                        <td>{source_html}</td>
                    </tr>
                """


            st.html(
                f"""
                <div class="region-dark-table-wrap">

                    <table class="region-dark-table">

                        <thead>
                            <tr>
                                <th>지역</th>
                                <th>정책사업</th>
                                <th>기준연도</th>
                                <th>정책대상</th>
                                <th>정책규모</th>
                                <th>정책내용</th>
                                <th>현재단계</th>
                                <th>SAFER 추천 아이디어</th>
                                <th>참고사항</th>
                                <th>출처</th>
                            </tr>
                        </thead>

                        <tbody>
                            {detail_rows}
                        </tbody>

                    </table>

                </div>
                """
            )