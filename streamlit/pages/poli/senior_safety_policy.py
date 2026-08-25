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
   EXPANDER
========================================================== */

[data-testid="stExpander"] {

    background:
        #182035 !important;

    border:
        1px solid #46536F !important;

    border-radius:
        14px !important;

    overflow:
        hidden !important;

    margin-top:
        12px !important;
}


[data-testid="stExpander"] summary * {

    color:
        #FFFFFF !important;

    opacity:
        1 !important;
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

[data-testid="stDataFrame"] {
    border: 1px solid #3A4662 !important;
    border-radius: 14px !important;
    overflow: hidden !important;
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
    # REGION DETAIL
    # ========================================================

    st.html(
        """
        <div class="section-title">
            지역별 고령운전자 안전정책 상세
        </div>
        <div class="section-sub">
            선택한 지역의 정책 대상, 규모, 주요 내용과 현재 추진단계를 확인합니다.
        </div>
        """
    )

    if filtered_df.empty:
        st.info("현재 조건에 해당하는 정책이 없습니다.")

    else:
        for _, row in filtered_df.iterrows():

            region = safe_text(row["region_name"])
            policy = safe_text(row["policy_project"])
            target = safe_text(row["target"])
            scale = safe_text(row["scale"])
            content = safe_text(row["content"])
            current_stage = safe_text(row["current_stage"])
            source_url = safe_text(row["source_url"], default="")

            base_year = (
                f"{int(row['base_year'])}년"
                if pd.notna(row["base_year"])
                else "-"
            )

            stage_class = (
                "stage-active"
                if any(
                    word in current_stage
                    for word in ["시행", "운영", "진행", "추진", "확대"]
                )
                else "stage-etc"
            )

            if source_url:
                source_html = f"""
                <div class="policy-source">
                    <span class="source-label">출처</span>
                    <a href="{source_url}"
                       target="_blank"
                       rel="noopener noreferrer"
                       class="source-link">
                        원문 보기 ↗
                    </a>
                </div>
                """
            else:
                source_html = """
                <div class="policy-source">
                    <span class="source-label">출처</span>
                    <span class="source-empty">출처 정보 없음</span>
                </div>
                """

            st.html(
                f"""
                <div class="policy-card">

                    <div class="policy-region">
                        {region}
                    </div>

                    <div class="policy-name">
                        {policy}
                    </div>

                    <div class="policy-meta">
                        <b>기준연도</b> : {base_year}
                        &nbsp;&nbsp; | &nbsp;&nbsp;
                        <b>현재 단계</b> :
                        <span class="{stage_class}">
                            {current_stage}
                        </span>

                        <br>

                        <b>정책 대상</b> : {target}

                        <br>

                        <b>정책 규모</b> : {scale}
                    </div>

                    <div class="policy-content">
                        {content}
                    </div>

                    {source_html}

                </div>
                """
            )

    # ========================================================
    # REGION COMPARE
    # ========================================================

    st.html('<div class="section-divider"></div>')

    st.html(
        """
        <div class="section-title">
            지역별 고령운전자 안전정책 비교
        </div>
        <div class="section-sub">
            비교할 지역을 선택하면 지역별 정책 내용을 한 화면에서 비교할 수 있습니다.
        </div>
        """
    )

    compare_regions = st.multiselect(
        "비교 지역",
        regions,
        max_selections=4,
        placeholder="비교할 지역을 2~4개 선택하세요",
        key="region_policy_compare"
    )

    compare_btn_col, _ = st.columns([1, 3])

    with compare_btn_col:
        compare_clicked = st.button(
            "비교하기",
            key="policy_compare_btn",
            use_container_width=True
        )

    if compare_clicked:

        if len(compare_regions) < 2:
            st.warning("비교할 지역을 2개 이상 선택해주세요.")

        else:
            compare_df = df[
                df["region_name"].isin(compare_regions)
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
            ].copy()

            compare_df["base_year"] = (
                pd.to_numeric(compare_df["base_year"], errors="coerce")
                .astype("Int64")
            )

            compare_df.columns = [
                "지역",
                "정책사업",
                "기준연도",
                "정책대상",
                "정책규모",
                "현재단계",
                "정책내용",
            ]

            st.dataframe(
                compare_df,
                use_container_width=True,
                hide_index=True,
                height=min(520, 60 + len(compare_df) * 38),
                column_config={
                    "지역": st.column_config.TextColumn("지역", width="small"),
                    "정책사업": st.column_config.TextColumn("정책사업", width="large"),
                    "기준연도": st.column_config.NumberColumn("기준연도", format="%d년"),
                    "정책대상": st.column_config.TextColumn("정책대상", width="medium"),
                    "정책규모": st.column_config.TextColumn("정책규모", width="medium"),
                    "현재단계": st.column_config.TextColumn("현재단계", width="medium"),
                    "정책내용": st.column_config.TextColumn("정책내용", width="large"),
                }
            )

    # ========================================================
    # ANALYSIS
    # ========================================================

    st.html('<div class="section-divider"></div>')

    st.html(
        f"""
        <div class="analysis-box">

            <div class="analysis-title">
                지역 특화 고령운전자 정책 분석 요약
            </div>

            현재 DB에는
            <b>{total_regions:,}개 지역</b>에서
            총 <b>{total_policy:,}개의 정책</b>이 확인됩니다.

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

            ※ 정책 수는 실제 전국 정책 전체를 의미하는 통계가 아니라
            현재 <b>region_old_driver_policy</b> 테이블에 수집된 데이터를
            기준으로 한 비교 결과입니다.

        </div>
        """
    )

    # ========================================================
    # SAFER IDEA
    # ========================================================

    st.html('<div class="section-divider"></div>')

    with st.container(key="saas_panel"):

        st.html(
            """
            <div class="panel-title">
                SAFER 지역 정책 추천
            </div>

            <div class="panel-sub">
                기존 지역 정책을 기반으로 SAFER에서 활용할 수 있는
                서비스·정책 아이디어를 확인합니다.

                <br>

                <b style="color:#F3C867;">
                    아래 내용은 실제 시행 중인 정책이 아니라
                    기존 정책 데이터를 기반으로 작성된 SAFER 활용 아이디어입니다.
                </b>
            </div>
            """
        )

        idea_df = filtered_df[
            ~filtered_df["saas_idea"].isin(INVALID_VALUES)
        ].copy()

        if idea_df.empty:
            st.info("현재 조건에 해당하는 SAFER 추천 아이디어가 없습니다.")

        else:
            for _, row in idea_df.iterrows():

                st.html(
                    f"""
                    <div class="saas-card">

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

    # ========================================================
    # NOTE
    # ========================================================

    st.html('<div class="section-divider"></div>')

    with st.container(key="note_panel"):

        st.html(
            """
            <div class="panel-title">
                정책 참고사항
            </div>

            <div class="panel-sub">
                선택한 정책 데이터에 별도로 기록된 참고사항을 확인합니다.
            </div>
            """
        )

        note_df = filtered_df[
            ~filtered_df["note"].isin(INVALID_VALUES)
        ].copy()

        if note_df.empty:
            st.info("현재 조건에 별도로 기록된 참고사항이 없습니다.")

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
    # DETAIL TABLE
    # ========================================================

    st.write("")

    with st.expander(
        "지역 특화 고령운전자 정책 전체 데이터 보기"
    ):

        detail_df = filtered_df[
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
        ].copy()

        detail_df["base_year"] = (
            pd.to_numeric(detail_df["base_year"], errors="coerce")
            .astype("Int64")
        )

        detail_df.columns = [
            "지역",
            "정책사업",
            "기준연도",
            "정책대상",
            "정책규모",
            "정책내용",
            "현재단계",
            "SAFER 추천 아이디어",
            "참고사항",
            "출처",
        ]

        st.dataframe(
            detail_df,
            use_container_width=True,
            hide_index=True,
            height=500,
            column_config={
                "지역": st.column_config.TextColumn("지역"),
                "정책사업": st.column_config.TextColumn("정책사업", width="large"),
                "기준연도": st.column_config.NumberColumn("기준연도", format="%d년"),
                "정책대상": st.column_config.TextColumn("정책대상", width="medium"),
                "정책규모": st.column_config.TextColumn("정책규모", width="medium"),
                "정책내용": st.column_config.TextColumn("정책내용", width="large"),
                "현재단계": st.column_config.TextColumn("현재단계"),
                "SAFER 추천 아이디어": st.column_config.TextColumn(
                    "SAFER 추천 아이디어",
                    width="large"
                ),
                "참고사항": st.column_config.TextColumn(
                    "참고사항",
                    width="large"
                ),
                "출처": st.column_config.LinkColumn(
                    "출처",
                    display_text="원문 보기"
                ),
            }
        )