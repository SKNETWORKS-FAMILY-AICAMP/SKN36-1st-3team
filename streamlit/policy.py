import sqlite3
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="SAFE 정책 분석",
    page_icon="📋",
    layout="wide"
)


# ============================================================
# 데이터 불러오기
# ============================================================

@st.cache_data
def load_data():

    with sqlite3.connect("database/policy.db") as conn:

        education = pd.read_sql(
            "SELECT * FROM education_reservation",
            conn
        )

        return_policy = pd.read_sql(
            "SELECT * FROM return_license_policy",
            conn
        )

        region_policy = pd.read_sql(
            "SELECT * FROM region_old_driver_policy",
            conn
        )

        old_policy = pd.read_sql(
            "SELECT * FROM old_driver_policy",
            conn
        )

    return education, return_policy, region_policy, old_policy


education, return_policy, region_policy, old_policy = load_data()


# ============================================================
# 기본 전처리
# ============================================================

education["edu_date"] = pd.to_datetime(
    education["edu_date"]
)

education["capacity"] = pd.to_numeric(
    education["capacity"]
)

education["month"] = (
    education["edu_date"]
    .dt.to_period("M")
    .astype(str)
)


# ============================================================
# 페이지 제목
# ============================================================

st.title("📋 고령운전자 정책 분석")

st.caption(
    "교통안전교육 현황과 전국·지역별 고령운전자 정책을 비교합니다."
)


# ============================================================
# TAB
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 교육 통계",
    "🏛 전국 정책",
    "📍 지역 정책",
    "🚘 면허반납·안전지원"
])


# ============================================================
# TAB 1
# 교육 예약 통계
# ============================================================

with tab1:

    st.header("고령운전자 교통안전교육 통계")

    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    total_capacity = int(
        education["capacity"].sum()
    )

    branch_count = (
        education["branch_name"]
        .nunique()
    )

    course_count = (
        education["course_name"]
        .nunique()
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "전체 교육 정원",
        f"{total_capacity:,}명"
    )

    c2.metric(
        "교육장 수",
        f"{branch_count}개"
    )

    c3.metric(
        "교육 과정 수",
        f"{course_count}개"
    )


    st.divider()


    # --------------------------------------------------------
    # 월별 교육 정원
    # --------------------------------------------------------

    st.subheader("월별 교육 정원")

    monthly = (
        education
        .groupby("month")["capacity"]
        .sum()
    )

    st.line_chart(
        monthly,
        x_label="월",
        y_label="교육 정원"
    )


    # --------------------------------------------------------
    # 과정별 월별 추세
    # --------------------------------------------------------

    st.subheader("과정별 월별 교육 정원")

    course_month = (
        education
        .groupby(
            ["month", "course_name"]
        )["capacity"]
        .sum()
        .unstack(fill_value=0)
    )

    st.line_chart(
        course_month,
        x_label="월",
        y_label="교육 정원"
    )


    # --------------------------------------------------------
    # 교육장별 비교
    # --------------------------------------------------------

    st.subheader("교육장별 교육 정원")

    branch = (
        education
        .groupby("branch_name")["capacity"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(
        branch,
        x_label="교육장",
        y_label="교육 정원"
    )


    # --------------------------------------------------------
    # 교육 과정 비교
    # --------------------------------------------------------

    st.subheader("교육 과정별 정원")

    course = (
        education
        .groupby("course_name")["capacity"]
        .sum()
    )

    st.bar_chart(
        course,
        x_label="교육 과정",
        y_label="교육 정원"
    )


    # --------------------------------------------------------
    # 상세 데이터
    # --------------------------------------------------------

    with st.expander("교육 예약 상세 데이터"):

        st.dataframe(
            education,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# TAB 2
# 전국 고령운전자 정책
# ============================================================

with tab2:

    st.header("전국 고령운전자 정책 비교")

    # --------------------------------------------------------
    # 필터
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        categories = [
            "전체"
        ] + sorted(
            old_policy["category"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_category = st.selectbox(
            "정책 분야",
            categories,
            key="old_category"
        )

    with col2:

        status_list = [
            "전체"
        ] + sorted(
            old_policy["status"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_status = st.selectbox(
            "정책 상태",
            status_list
        )


    filtered = old_policy.copy()

    if selected_category != "전체":
        filtered = filtered[
            filtered["category"]
            == selected_category
        ]

    if selected_status != "전체":
        filtered = filtered[
            filtered["status"]
            == selected_status
        ]


    st.metric(
        "조회 정책",
        f"{len(filtered)}건"
    )


    # --------------------------------------------------------
    # 정책 카드
    # --------------------------------------------------------

    for _, row in filtered.iterrows():

        with st.expander(
            f"{row['category']} | {row['policy_name']}"
        ):

            c1, c2 = st.columns(2)

            with c1:
                st.write(
                    "**상태**",
                    row["status"]
                )

                st.write(
                    "**대상**",
                    row["target"]
                )

                st.write(
                    "**시행기관**",
                    row["agency"]
                )

                st.write(
                    "**시작 시점**",
                    row["start_date"]
                )

            with c2:
                st.write(
                    "**규모**",
                    row["scale"]
                )

                st.write(
                    "**필요 데이터**",
                    row["needed_data"]
                )

            st.write("**주요 내용**")
            st.write(row["content"])

            st.write("**SAFE 활용 아이디어**")
            st.info(row["saas_idea"])

            if pd.notna(row["source_url"]):
                st.link_button(
                    "출처 확인",
                    row["source_url"]
                )


# ============================================================
# TAB 3
# 지역별 고령운전자 정책
# ============================================================

with tab3:

    st.header("지역별 고령운전자 정책 비교")

    regions = sorted(
        region_policy["region"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_regions = st.multiselect(
        "비교할 지역 선택",
        regions,
        default=regions[:2]
    )


    if selected_regions:

        compare = region_policy[
            region_policy["region"]
            .isin(selected_regions)
        ].copy()


        # ----------------------------------------------------
        # 핵심 비교표
        # ----------------------------------------------------

        st.subheader("정책 비교표")

        columns = [
            "region",
            "정책명",
            "대상 연령/조건",
            "일반 반납자 지원",
            "실운전자 지원",
            "지원 형태",
            "신청 방법",
            "거주/특이 조건",
            "정책 상태"
        ]

        st.dataframe(
            compare[columns],
            use_container_width=True,
            hide_index=True
        )


        # ----------------------------------------------------
        # 지역별 정책 상세
        # ----------------------------------------------------

        st.subheader("지역별 정책 상세")

        for _, row in compare.iterrows():

            with st.expander(
                f"{row['region']} | {row['정책명']}"
            ):

                st.write(
                    "**대상:**",
                    row["대상 연령/조건"]
                )

                st.write(
                    "**일반 반납자 지원:**",
                    row["일반 반납자 지원"]
                )

                st.write(
                    "**실운전자 지원:**",
                    row["실운전자 지원"]
                )

                st.write(
                    "**지원 형태:**",
                    row["지원 형태"]
                )

                st.write(
                    "**신청 방법:**",
                    row["신청 방법"]
                )

                st.write(
                    "**특이 조건:**",
                    row["거주/특이 조건"]
                )

                st.info(
                    row["SaaS에서 볼 지표"]
                )

                if pd.notna(row["source_url"]):
                    st.link_button(
                        "정책 출처",
                        row["source_url"]
                    )

    else:

        st.info(
            "비교할 지역을 선택해주세요."
        )


# ============================================================
# TAB 4
# 면허반납 / 안전장치 정책
# ============================================================

with tab4:

    st.header(
        "면허반납 대안 및 안전지원 정책 비교"
    )

    regions = sorted(
        return_policy["region"]
        .dropna()
        .unique()
        .tolist()
    )

    selected = st.multiselect(
        "지역 선택",
        regions,
        default=regions[:3],
        key="return_region"
    )


    if selected:

        compare = return_policy[
            return_policy["region"]
            .isin(selected)
        ].copy()


        # ----------------------------------------------------
        # 정책 비교
        # ----------------------------------------------------

        st.dataframe(
            compare[
                [
                    "region",
                    "정책/사업",
                    "base_year",
                    "대상",
                    "지원·규모",
                    "핵심 내용",
                    "현재 단계"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )


        # ----------------------------------------------------
        # 정책 상세
        # ----------------------------------------------------

        for _, row in compare.iterrows():

            with st.expander(
                f"{row['region']} | {row['정책/사업']}"
            ):

                st.write(
                    "**기준 연도:**",
                    row["base_year"]
                )

                st.write(
                    "**대상:**",
                    row["대상"]
                )

                st.write(
                    "**지원 규모:**",
                    row["지원·규모"]
                )

                st.write(
                    "**핵심 내용:**"
                )

                st.write(
                    row["핵심 내용"]
                )

                st.write(
                    "**현재 단계:**",
                    row["현재 단계"]
                )

                st.write(
                    "**SAFE 활용 아이디어:**"
                )

                st.info(
                    row["SaaS 활용 아이디어"]
                )

                if pd.notna(row["source_url"]):
                    st.link_button(
                        "정책 출처",
                        row["source_url"]
                    )

    else:

        st.info(
            "비교할 지역을 선택해주세요."
        )