import sys
from pathlib import Path
from html import escape

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sqlalchemy import text


# ============================================================
# PROJECT ROOT
# SAFE/streamlit/pages/poli/license_return_policy.py
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
def load_return_policy():

    engine = get_engine()

    query = text(
        """
        SELECT
            id,
            region,
            policy_name,
            base_year,
            target_condition,
            general_support,
            active_driver_support,
            support_type,
            apply_method,
            residence_condition,
            status,
            saas_metric,
            source_url,
            verify_memo
        FROM return_license_policy
        ORDER BY region, policy_name
        """
    )

    with engine.connect() as conn:
        return pd.read_sql(query, conn)


# ============================================================
# LOAD DATA
# ============================================================

try:
    df = load_return_policy()

except Exception as e:
    st.error(
        f"운전면허 자진반납 지원정책 데이터 조회 실패\n\n{e}"
    )
    st.stop()


# ============================================================
# DATA CLEAN
# ============================================================

TEXT_COLUMNS = [
    "region",
    "policy_name",
    "target_condition",
    "general_support",
    "active_driver_support",
    "support_type",
    "apply_method",
    "residence_condition",
    "status",
    "saas_metric",
    "source_url",
    "verify_memo",
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
    "해당 없음",
]


def safe_text(value, default="-"):

    value = str(value).strip()

    if value in INVALID_VALUES:
        return default

    return value


def html_text(value, default="-"):
    """
    DB 문자열을 HTML 안에 출력할 때 안전하게 사용
    """
    return escape(
        safe_text(value, default),
        quote=True
    )


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
        x
        for x
        in df["region_name"]
        .dropna()
        .unique()
        .tolist()
        if x not in INVALID_VALUES
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


support_types = sorted(
    [
        x
        for x
        in df["support_type"]
        .dropna()
        .unique()
        .tolist()
        if x not in INVALID_VALUES
    ]
)


statuses = sorted(
    [
        x
        for x
        in df["status"]
        .dropna()
        .unique()
        .tolist()
        if x not in INVALID_VALUES
    ]
)


if df.empty:

    st.warning(
        "운전면허 자진반납 지원정책 데이터가 없습니다."
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

    background: rgba(255,255,255,.98);

    border-radius: 16px;

    padding: 10px 20px;

    margin-bottom: 20px;
}


.st-key-top_nav button {

    background: transparent !important;

    color: #30384D !important;

    border: none !important;

    box-shadow: none !important;

    font-size: 18px !important;

    font-weight: 500 !important;

    min-height: 44px !important;
}


.st-key-nav_logo button {

    color: #27314C !important;

    font-size: 33px !important;

    font-weight: 900 !important;

    justify-content: flex-start !important;

    padding-left: 0 !important;
}


.st-key-nav_policy button {

    color: #D6A348 !important;

    font-weight: 900 !important;
}


.st-key-nav_future button {

    background: #D9A64A !important;

    color: #172035 !important;

    font-weight: 800 !important;
}


/* ==========================================================
   PAGE
========================================================== */

.st-key-return_policy_page {

    background: #101625;

    border: 1px solid #34405A;

    border-radius: 20px;

    padding: 34px 36px 48px 36px;
}


/* ==========================================================
   HEADER
========================================================== */

.page-path {

    color: #D6A348;

    font-size: 15px;

    font-weight: 800;

    margin-bottom: 10px;
}


.page-title {

    color: #FFFFFF;

    font-size: 44px;

    font-weight: 900;

    margin-bottom: 12px;
}


.page-sub {

    color: #C3CBD8;

    font-size: 17px;

    line-height: 1.75;

    margin-bottom: 25px;
}


/* ==========================================================
   BACK
========================================================== */

.st-key-back_policy button {

    background: #192136 !important;

    color: #E3E7EE !important;

    border: 1px solid #39445D !important;

    border-radius: 11px !important;

    min-height: 44px !important;
}


/* ==========================================================
   INPUT
========================================================== */

label[data-testid="stWidgetLabel"] p {

    color: #E2E7EF !important;

    font-size: 15px !important;

    font-weight: 700 !important;
}


/* SELECT / MULTISELECT */

div[data-baseweb="select"] > div {

    background: #182035 !important;

    color: #FFFFFF !important;

    min-height: 46px !important;

    border: 1px solid #3A4662 !important;

    border-radius: 10px !important;

    box-shadow: none !important;
}


div[data-baseweb="select"] span {

    color: #E7ECF4 !important;
}


div[data-baseweb="select"] input {

    color: #E7ECF4 !important;

    caret-color: #F0C66E !important;
}


div[data-baseweb="select"] input::placeholder {

    color: #8F9AAF !important;

    opacity: 1 !important;
}


div[data-baseweb="select"] svg {

    color: #AEB8C8 !important;

    fill: #AEB8C8 !important;
}


div[data-baseweb="select"] > div:focus-within {

    border-color: #D6A348 !important;

    box-shadow:
        0 0 0 1px
        rgba(214,163,72,.25) !important;
}


/* MULTISELECT TAG */

div[data-baseweb="tag"] {

    background: rgba(214,163,72,.14) !important;

    border: 1px solid rgba(214,163,72,.38) !important;

    border-radius: 999px !important;
}


div[data-baseweb="tag"] span {

    color: #F0C66E !important;

    font-weight: 800 !important;
}


/* DROPDOWN */

div[data-baseweb="popover"] ul {

    background: #182035 !important;

    border: 1px solid #3A4662 !important;

    border-radius: 10px !important;
}


div[data-baseweb="popover"] li {

    background: #182035 !important;

    color: #E2E7EF !important;
}


div[data-baseweb="popover"] li * {

    color: #E2E7EF !important;
}


div[data-baseweb="popover"] li:hover {

    background: #242F49 !important;
}


div[data-baseweb="popover"] li[aria-selected="true"] {

    background: rgba(214,163,72,.16) !important;
}


div[data-baseweb="popover"] li[aria-selected="true"] * {

    color: #F0C66E !important;
}


/* ==========================================================
   KPI
========================================================== */

.kpi {

    min-height: 112px;

    background: #192136;

    border: 1px solid #394560;

    border-radius: 17px;

    padding: 18px 20px;
}


.kpi-label {

    color: #C4CCD9;

    font-size: 14px;

    margin-bottom: 15px;
}


.kpi-value {

    color: #FFFFFF;

    font-size: 25px;

    font-weight: 900;

    word-break: keep-all;
}


/* ==========================================================
   PANELS
========================================================== */

.st-key-region_panel,
.st-key-support_panel,
.st-key-status_panel,
.st-key-compare_panel,
.st-key-detail_panel,
.st-key-safer_panel,
.st-key-verify_panel {

    background: #182035;

    border: 1px solid #3A4662;

    border-radius: 28px;

    padding: 24px 26px;

    margin-top: 24px;
}


.panel-title {

    color: #FFFFFF;

    font-size: 24px;

    font-weight: 900;

    margin-bottom: 8px;
}


.panel-sub {

    color: #C8D0DC;

    font-size: 15px;

    line-height: 1.75;

    margin-bottom: 12px;
}


.panel-sub b {

    color: #FFFFFF;
}


/* ==========================================================
   CUSTOM COMPARE TABLE
========================================================== */

.policy-compare-table-wrap {

    width: 100%;

    margin-top: 22px;

    overflow-x: auto;

    border-radius: 18px;

    border: 1px solid #3B4864;

    background: #121A2B;

    box-shadow:
        0 12px 30px rgba(0,0,0,.18);
}


.policy-compare-table {

    width: 100%;

    min-width: 1150px;

    border-collapse: collapse;

    font-size: 15px;
}


/* TABLE HEADER */

.policy-compare-table thead th {

    padding: 17px 17px;

    background:
        linear-gradient(
            180deg,
            #29344F 0%,
            #202940 100%
        );

    color: #F5F7FB;

    font-size: 14px;

    font-weight: 900;

    text-align: left;

    border-bottom: 1px solid #46536F;

    white-space: nowrap;

    letter-spacing: .2px;
}


.policy-compare-table thead th:first-child {

    border-top-left-radius: 17px;
}


.policy-compare-table thead th:last-child {

    border-top-right-radius: 17px;
}


/* TABLE BODY */

.policy-compare-table tbody tr {

    background: #151D30;

    transition:
        background .15s ease;
}


.policy-compare-table tbody tr:nth-child(even) {

    background: #182136;
}


.policy-compare-table tbody tr:hover {

    background: #202C47;
}


.policy-compare-table tbody td {

    padding: 17px 17px;

    color: #DCE3ED;

    vertical-align: middle;

    border-bottom: 1px solid #2B364D;

    line-height: 1.65;
}


.policy-compare-table tbody tr:last-child td {

    border-bottom: none;
}


/* REGION */

.region-pill {

    display: inline-block;

    padding: 6px 11px;

    border-radius: 999px;

    background: rgba(214,163,72,.12);

    border: 1px solid rgba(214,163,72,.38);

    color: #F0C66E;

    font-size: 13px;

    font-weight: 900;

    white-space: nowrap;
}


/* POLICY NAME */

.policy-title-cell {

    color: #FFFFFF !important;

    font-weight: 800;

    min-width: 220px;
}


/* GENERAL SUPPORT */

.support-main {

    color: #F3F5F9;

    font-weight: 700;

    min-width: 180px;
}


/* ACTIVE SUPPORT */

.active-badge {

    display: inline-block;

    padding: 4px 9px;

    margin-bottom: 7px;

    border-radius: 999px;

    font-size: 12px;

    font-weight: 900;

    white-space: nowrap;
}


.active-yes {

    background: rgba(105,190,148,.13);

    border: 1px solid rgba(105,190,148,.42);

    color: #8ED8B4;
}


.active-no {

    background: rgba(130,140,158,.10);

    border: 1px solid rgba(130,140,158,.28);

    color: #9AA5B7;
}


.support-active-text {

    color: #E1E7EF;

    font-size: 14px;

    line-height: 1.6;

    min-width: 210px;
}


/* SUPPORT TYPE */

.support-type-pill {

    display: inline-block;

    padding: 6px 10px;

    border-radius: 8px;

    background: rgba(141,169,196,.11);

    border: 1px solid rgba(141,169,196,.32);

    color: #B7CDE2;

    font-size: 13px;

    font-weight: 800;

    white-space: nowrap;
}


/* SCROLLBAR */

.policy-compare-table-wrap::-webkit-scrollbar {

    height: 8px;
}


.policy-compare-table-wrap::-webkit-scrollbar-track {

    background: #121A2B;
}


.policy-compare-table-wrap::-webkit-scrollbar-thumb {

    background: #46536F;

    border-radius: 999px;
}




/* ==========================================================
   SECTION DIVIDER
========================================================== */

.section-divider {

    margin-top: 30px;

    margin-bottom: 4px;

    padding-top: 2px;

    border-top: 1px solid #2F3A52;
}


/* ==========================================================
   REGION COMPARE TABLE
========================================================== */

.compare-result-wrap {

    width: 100%;

    margin-top: 18px;

    overflow-x: auto;

    border: 1px solid #3A4662;

    border-radius: 16px;

    background: #121A2B;

    box-shadow:
        0 10px 28px
        rgba(0,0,0,.16);
}


.compare-result-table {

    width: 100%;

    min-width: 1180px;

    border-collapse: collapse;
}


.compare-result-table thead th {

    background:
        linear-gradient(
            180deg,
            #27324B 0%,
            #202940 100%
        );

    color: #F6F8FB;

    font-size: 14px;

    font-weight: 900;

    text-align: left;

    padding: 14px 15px;

    border-bottom: 1px solid #46536F;

    white-space: nowrap;
}


.compare-result-table tbody tr {

    background: #151D30;
}


.compare-result-table tbody tr:nth-child(even) {

    background: #182136;
}


.compare-result-table tbody tr:hover {

    background: #202C47;
}


.compare-result-table tbody td {

    color: #DCE3ED;

    font-size: 14px;

    line-height: 1.65;

    vertical-align: top;

    padding: 14px 15px;

    border-bottom: 1px solid #2B364D;
}


.compare-result-table tbody tr:last-child td {

    border-bottom: none;
}


.compare-region-pill {

    display: inline-block;

    padding: 5px 10px;

    border-radius: 999px;

    background: rgba(214,163,72,.12);

    border: 1px solid rgba(214,163,72,.38);

    color: #F0C66E;

    font-weight: 900;

    white-space: nowrap;
}


.compare-policy-name {

    color: #FFFFFF !important;

    font-weight: 800;

    min-width: 190px;
}


.compare-result-wrap::-webkit-scrollbar {

    height: 8px;
}


.compare-result-wrap::-webkit-scrollbar-track {

    background: #121A2B;
}


.compare-result-wrap::-webkit-scrollbar-thumb {

    background: #46536F;

    border-radius: 999px;
}


/* ==========================================================
   ANALYSIS
========================================================== */

.analysis-box {

    background: #121A2B;

    border: 1px solid #35415C;

    border-left: 4px solid #D6A348;

    border-radius: 7px 15px 15px 7px;

    padding: 20px 22px;

    margin-top: 22px;

    color: #E5EAF2;

    font-size: 15px;

    line-height: 1.95;
}


.analysis-title {

    color: #F3C867;

    font-size: 18px;

    font-weight: 900;

    margin-bottom: 10px;
}


.analysis-box b {

    color: #FFFFFF;
}


/* ==========================================================
   POLICY CARD
========================================================== */

.policy-card {

    background: #121A2B;

    border: 1px solid #3A4662;

    border-radius: 20px;

    padding: 24px 25px;

    margin: 15px 0;
}


.region-badge {

    display: inline-block;

    padding: 5px 11px;

    border-radius: 999px;

    background: rgba(214,163,72,.12);

    border: 1px solid rgba(214,163,72,.32);

    color: #E7BC67;

    font-size: 13px;

    font-weight: 900;

    margin-bottom: 12px;
}


.policy-name {

    color: #FFFFFF;

    font-size: 23px;

    font-weight: 900;

    margin-bottom: 15px;
}


.policy-meta {

    color: #C9D0DB;

    font-size: 14px;

    line-height: 2;
}


.policy-meta b {

    color: #FFFFFF;
}


/* ==========================================================
   SUPPORT
========================================================== */

.support-grid {

    display: grid;

    grid-template-columns:
        repeat(2, minmax(0, 1fr));

    gap: 12px;

    margin-top: 17px;
}


.support-box {

    background: #19233A;

    border: 1px solid #35425D;

    border-radius: 13px;

    padding: 15px 16px;
}


.support-label {

    color: #91A0B8;

    font-size: 13px;

    font-weight: 800;

    margin-bottom: 7px;
}


.support-value {

    color: #FFFFFF;

    font-size: 15px;

    font-weight: 700;

    line-height: 1.7;
}


.active-support {

    border-color: rgba(121,182,155,.50);

    background: rgba(121,182,155,.08);
}


.active-support .support-label {

    color: #8ED1B2;
}


/* ==========================================================
   STATUS
========================================================== */

.status-active {

    color: #82D3A8;

    font-weight: 900;
}


.status-other {

    color: #F0C66E;

    font-weight: 900;
}


/* ==========================================================
   SOURCE
========================================================== */

.policy-source {

    display: flex;

    align-items: center;

    gap: 12px;

    margin-top: 18px;

    padding-top: 15px;

    border-top: 1px solid #2E3951;
}


.source-label {

    color: #8F9AAF;

    font-size: 14px;

    font-weight: 800;
}


.source-link {

    display: inline-block;

    padding: 6px 11px;

    background: rgba(214,163,72,.10);

    border: 1px solid rgba(214,163,72,.35);

    border-radius: 7px;

    color: #F0C66E !important;

    font-size: 14px;

    font-weight: 800;

    text-decoration: none !important;
}


.source-link:hover {

    background: rgba(214,163,72,.20);

    border-color: #D6A348;
}


.source-empty {

    color: #737E93;

    font-size: 14px;
}


/* ==========================================================
   SAFER
========================================================== */

.safer-card {

    background:
        linear-gradient(
            120deg,
            #172338 0%,
            #1B2941 62%,
            #302D28 100%
        );

    border: 1px solid #A77E35;

    border-radius: 20px;

    padding: 23px 24px;

    margin: 14px 0;

    position: relative;

    overflow: hidden;
}


.safer-card::after {

    content: "SAFER";

    position: absolute;

    right: 18px;

    top: 4px;

    font-size: 57px;

    font-weight: 900;

    color: rgba(214,163,72,.05);
}


.safer-label {

    color: #E7B955;

    font-size: 13px;

    font-weight: 900;

    letter-spacing: 1.2px;

    margin-bottom: 10px;
}


.safer-title {

    color: #FFFFFF;

    font-size: 20px;

    font-weight: 900;

    margin-bottom: 9px;
}


.safer-content {

    color: #E1E6EE;

    font-size: 15px;

    line-height: 1.9;
}


/* ==========================================================
   VERIFY
========================================================== */

.verify-card {

    background: #121A2B;

    border: 1px solid #35415C;

    border-radius: 15px;

    padding: 18px 20px;

    margin: 11px 0;
}


.verify-title {

    color: #FFFFFF;

    font-size: 16px;

    font-weight: 900;

    margin-bottom: 7px;
}


.verify-text {

    color: #BCC6D5;

    font-size: 14px;

    line-height: 1.8;
}


/* ==========================================================
   EXPANDER
========================================================== */

[data-testid="stExpander"] {

    background: #182035 !important;

    border: 1px solid #46536F !important;

    border-radius: 14px !important;

    overflow: hidden !important;

    margin-top: 14px !important;
}


[data-testid="stExpander"] summary * {

    color: #FFFFFF !important;

    opacity: 1 !important;
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

with st.container(key="return_policy_page"):

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
                정책·제도 &gt; 운전면허 자진반납 지원정책
            </div>

            <div class="page-title">
                운전면허 자진반납 지원정책
            </div>

            <div class="page-sub">
                지역별 고령운전자 운전면허 자진반납 지원정책을 비교합니다.
                지원 대상, 일반 지원, 실제 운전자 추가 지원, 지원 방식,
                신청 방법과 거주 조건 등을 한눈에 확인할 수 있습니다.
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
    # FILTER
    # ========================================================

    selected_region = st.selectbox(
        "지역 선택",
        ["전체"] + regions
    )


    # ========================================================
    # FILTER DATA
    # ========================================================

    filtered_df = df.copy()

    if selected_region != "전체":
        filtered_df = filtered_df[
            filtered_df["region_name"] == selected_region
        ]


    # ========================================================
    # REGION DETAIL
    # ========================================================

    with st.container(key="detail_panel"):

        st.html(
            f"""
            <div class="panel-title">
                지역별 자진반납 지원정책 상세
            </div>

            <div class="panel-sub">
                현재 선택 지역 기준
                <b>{len(filtered_df):,}개</b> 정책을 확인합니다.
            </div>
            """
        )

        if filtered_df.empty:

            st.info(
                "현재 선택한 지역에 해당하는 정책이 없습니다."
            )

        else:

            for _, row in filtered_df.iterrows():

                region = html_text(
                    row["region_name"]
                )

                policy_name = html_text(
                    row["policy_name"]
                )

                target = html_text(
                    row["target_condition"]
                )

                general_support = html_text(
                    row["general_support"]
                )

                active_support = html_text(
                    row["active_driver_support"]
                )

                support_type = html_text(
                    row["support_type"]
                )

                apply_method = html_text(
                    row["apply_method"]
                )

                residence = html_text(
                    row["residence_condition"]
                )

                status_raw = safe_text(
                    row["status"]
                )

                status = escape(
                    status_raw,
                    quote=True
                )

                source_url_raw = safe_text(
                    row["source_url"],
                    default=""
                )

                source_url = escape(
                    source_url_raw,
                    quote=True
                )

                base_year = (
                    f"{int(row['base_year'])}년"
                    if pd.notna(
                        row["base_year"]
                    )
                    else "-"
                )

                status_class = (
                    "status-active"
                    if any(
                        x in status_raw
                        for x in [
                            "시행",
                            "운영",
                            "진행",
                            "추진",
                        ]
                    )
                    else "status-other"
                )

                if source_url_raw.startswith(
                    (
                        "http://",
                        "https://"
                    )
                ):

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
                            정책 원문 확인 ↗
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
                    <div class="policy-card">

                        <div class="region-badge">
                            {region}
                        </div>

                        <div class="policy-name">
                            {policy_name}
                        </div>

                        <div class="policy-meta">

                            <b>기준연도</b> :
                            {base_year}

                            &nbsp;&nbsp; | &nbsp;&nbsp;

                            <b>상태</b> :
                            <span class="{status_class}">
                                {status}
                            </span>

                            <br>

                            <b>지원 대상</b> :
                            {target}

                            <br>

                            <b>지원 유형</b> :
                            {support_type}

                            <br>

                            <b>신청 방법</b> :
                            {apply_method}

                            <br>

                            <b>거주 조건</b> :
                            {residence}

                        </div>

                        <div class="support-grid">

                            <div class="support-box">

                                <div class="support-label">
                                    일반 자진반납 지원
                                </div>

                                <div class="support-value">
                                    {general_support}
                                </div>

                            </div>

                            <div class="support-box active-support">

                                <div class="support-label">
                                    실제 운전자 추가지원
                                </div>

                                <div class="support-value">
                                    {active_support}
                                </div>

                            </div>

                        </div>

                        {source_html}

                    </div>
                    """
                )


    st.html('<div class="section-divider"></div>')

    # ========================================================
    # REGION COMPARISON
    # ========================================================

    with st.container(key="compare_panel"):

        st.html(
            """
            <div class="panel-title">
                지역별 자진반납 지원정책 비교
            </div>

            <div class="panel-sub">
                비교할 지역을 선택한 뒤 <b>비교하기</b>를 누르면
                지역별 정책 내용을 한 화면에서 비교할 수 있습니다.
            </div>
            """
        )

        compare_regions = st.multiselect(
            "비교 지역",
            regions,
            default=[],
            placeholder="비교할 지역을 2개 이상 선택하세요"
        )

        compare_btn_col, compare_btn_empty = st.columns(
            [1, 3]
        )

        with compare_btn_col:

            compare_clicked = st.button(
                "비교하기",
                key="compare_regions_btn",
                use_container_width=True
            )

        if compare_clicked:

            if len(compare_regions) < 2:
                st.warning("비교할 지역을 2개 이상 선택해주세요.")

            else:
                region_compare_df = df[
                    df["region_name"].isin(compare_regions)
                ][
                    [
                        "region_name",
                        "policy_name",
                        "general_support",
                        "active_driver_support",
                        "support_type",
                        "target_condition",
                        "apply_method",
                        "residence_condition",
                    ]
                ].copy()

                if region_compare_df.empty:
                    st.info("선택한 지역의 자진반납 지원정책 데이터가 없습니다.")

                else:
                    region_compare_df.columns = [
                        "지역",
                        "정책명",
                        "일반 지원",
                        "실운전자 추가지원",
                        "지원 유형",
                        "지원 대상",
                        "신청 방법",
                        "거주 조건",
                    ]

                    compare_rows = ""

                    for _, row in region_compare_df.iterrows():

                        compare_rows += f"""
                        <tr>

                            <td>
                                <span class="compare-region-pill">
                                    {html_text(row["지역"])}
                                </span>
                            </td>

                            <td class="compare-policy-name">
                                {html_text(row["정책명"])}
                            </td>

                            <td>
                                {html_text(row["일반 지원"])}
                            </td>

                            <td>
                                {html_text(row["실운전자 추가지원"])}
                            </td>

                            <td>
                                {html_text(row["지원 유형"])}
                            </td>

                            <td>
                                {html_text(row["지원 대상"])}
                            </td>

                            <td>
                                {html_text(row["신청 방법"])}
                            </td>

                            <td>
                                {html_text(row["거주 조건"])}
                            </td>

                        </tr>
                        """

                    st.html(
                        f"""
                        <div class="compare-result-wrap">

                            <table class="compare-result-table">

                                <thead>

                                    <tr>
                                        <th>지역</th>
                                        <th>정책명</th>
                                        <th>일반 지원</th>
                                        <th>실운전자 추가지원</th>
                                        <th>지원 유형</th>
                                        <th>지원 대상</th>
                                        <th>신청 방법</th>
                                        <th>거주 조건</th>
                                    </tr>

                                </thead>

                                <tbody>
                                    {compare_rows}
                                </tbody>

                            </table>

                        </div>
                        """
                    )




    st.html('<div class="section-divider"></div>')

    # ========================================================
    # ANALYSIS
    # ========================================================

    total_policy = len(df)

    total_region = (
        df["region_name"]
        .replace("", pd.NA)
        .nunique()
    )

    active_support_total = (
        ~df[
            "active_driver_support"
        ].isin(INVALID_VALUES)
    ).sum()

    active_rate = (
        active_support_total
        / total_policy
        * 100
        if total_policy > 0
        else 0
    )

    type_df = (
        df[
            ~df["support_type"].isin(INVALID_VALUES)
        ]
        .groupby("support_type", as_index=False)
        .size()
        .rename(columns={"size": "count"})
        .sort_values("count", ascending=False)
    )

    if not type_df.empty:

        top_type = (
            type_df.iloc[0][
                "support_type"
            ]
        )

        top_type_count = int(
            type_df.iloc[0][
                "count"
            ]
        )

    else:

        top_type = "-"
        top_type_count = 0

    st.html(
        f"""
        <div class="analysis-box">

            <div class="analysis-title">
                운전면허 자진반납 지원정책 분석 요약
            </div>

            현재 DB에는
            <b>{total_region:,}개 지역</b>에서
            총 <b>{total_policy:,}개의 자진반납 정책</b>이
            수집되어 있습니다.

            <br>

            이 중 실제 운전자에 대한 별도 추가지원 내용이
            기록된 정책은
            <b>{active_support_total:,}개</b>로,
            전체의 약 <b>{active_rate:.1f}%</b>입니다.

            <br>

            현재 가장 많이 확인되는 지원 유형은
            <b>{escape(str(top_type))}</b>이며,
            총 <b>{top_type_count:,}개 정책</b>에서
            확인됩니다.

            <br><br>

            단, 이 결과는 전국 모든 지자체의 정책 존재 여부를
            확정하는 통계가 아니라 현재
            <b>return_license_policy</b> 테이블에
            수집된 데이터를 기준으로 한 비교 결과입니다.

        </div>
        """
    )


    st.html('<div class="section-divider"></div>')

    # ========================================================
    # SAFER METRIC
    # ========================================================

    with st.container(key="safer_panel"):

        st.html(
            """
            <div class="panel-title">
                SAFER 정책 분석 지표
            </div>

            <div class="panel-sub">
                자진반납 정책을 비교·분석할 때 활용할 수 있도록
                데이터에 정의된 SAFER 분석 지표를 제공합니다.

                <br>

                <b style="color:#F3C867;">
                    아래 내용은 정책의 실제 지원내용과 구분되는
                    SAFER 서비스 분석용 지표입니다.
                </b>
            </div>
            """
        )

        safer_df = (
            filtered_df[
                ~filtered_df[
                    "saas_metric"
                ].isin(INVALID_VALUES)
            ]
        )

        if safer_df.empty:

            st.info(
                "현재 조건에 해당하는 SAFER 분석 지표가 없습니다."
            )

        else:

            for _, row in safer_df.iterrows():

                st.html(
                    f"""
                    <div class="safer-card">

                        <div class="safer-label">
                            SAFER POLICY METRIC
                        </div>

                        <div class="safer-title">
                            {html_text(row["region_name"])}
                            ·
                            {html_text(row["policy_name"])}
                        </div>

                        <div class="safer-content">
                            {html_text(row["saas_metric"])}
                        </div>

                    </div>
                    """
                )


    st.html('<div class="section-divider"></div>')

    # ========================================================
    # VERIFY MEMO
    # ========================================================

    with st.container(key="verify_panel"):

        st.html(
            """
            <div class="panel-title">
                데이터 검증 메모
            </div>

            <div class="panel-sub">
                정책 데이터 수집 과정에서 확인한
                검증·주의사항을 표시합니다.
            </div>
            """
        )

        verify_df = (
            filtered_df[
                ~filtered_df[
                    "verify_memo"
                ].isin(INVALID_VALUES)
            ]
        )

        if verify_df.empty:

            st.info(
                "현재 조건에 별도의 검증 메모가 없습니다."
            )

        else:

            for _, row in verify_df.iterrows():

                st.html(
                    f"""
                    <div class="verify-card">

                        <div class="verify-title">
                            {html_text(row["region_name"])}
                            ·
                            {html_text(row["policy_name"])}
                        </div>

                        <div class="verify-text">
                            {html_text(row["verify_memo"])}
                        </div>

                    </div>
                    """
                )


    # ========================================================
    # FULL DATA
    # ========================================================

    st.write("")

    with st.expander(
        "운전면허 자진반납 지원정책 전체 데이터 보기"
    ):

        detail_df = filtered_df[
            [
                "region_name",
                "policy_name",
                "base_year",
                "target_condition",
                "general_support",
                "active_driver_support",
                "support_type",
                "apply_method",
                "residence_condition",
                "status",
                "saas_metric",
                "verify_memo",
                "source_url",
            ]
        ].copy()

        detail_df.columns = [
            "지역",
            "정책명",
            "기준연도",
            "지원대상",
            "일반지원",
            "실운전자 추가지원",
            "지원유형",
            "신청방법",
            "거주조건",
            "상태",
            "SAFER 분석지표",
            "검증메모",
            "출처",
        ]

        st.dataframe(
            detail_df,
            use_container_width=True,
            hide_index=True,
            height=520,

            column_config={

                "지역":
                    st.column_config.TextColumn(
                        "지역"
                    ),

                "정책명":
                    st.column_config.TextColumn(
                        "정책명",
                        width="large"
                    ),

                "기준연도":
                    st.column_config.NumberColumn(
                        "기준연도",
                        format="%d년"
                    ),

                "지원대상":
                    st.column_config.TextColumn(
                        "지원대상",
                        width="large"
                    ),

                "일반지원":
                    st.column_config.TextColumn(
                        "일반지원",
                        width="large"
                    ),

                "실운전자 추가지원":
                    st.column_config.TextColumn(
                        "실운전자 추가지원",
                        width="large"
                    ),

                "지원유형":
                    st.column_config.TextColumn(
                        "지원유형",
                        width="medium"
                    ),

                "신청방법":
                    st.column_config.TextColumn(
                        "신청방법",
                        width="large"
                    ),

                "거주조건":
                    st.column_config.TextColumn(
                        "거주조건",
                        width="large"
                    ),

                "상태":
                    st.column_config.TextColumn(
                        "상태"
                    ),

                "SAFER 분석지표":
                    st.column_config.TextColumn(
                        "SAFER 분석지표",
                        width="large"
                    ),

                "검증메모":
                    st.column_config.TextColumn(
                        "검증메모",
                        width="large"
                    ),

                "출처":
                    st.column_config.LinkColumn(
                        "출처",
                        display_text="원문 보기"
                    ),
            }
        )