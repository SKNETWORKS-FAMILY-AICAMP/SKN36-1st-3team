import sys
from pathlib import Path

# SAFE 프로젝트 루트를 Python 경로에 추가
ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


import sqlite3
import pandas as pd
import streamlit as st

from models.time_series import forecast_best


# ============================================================
# 페이지 설정
# ============================================================

st.set_page_config(
    page_title="SAFE 교통사고 분석",
    page_icon="🚨",
    layout="wide"
)


DB_PATH = "database/accident.db"


# ============================================================
# DB 함수
# ============================================================

@st.cache_data
def load_table(table_name):

    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql(
            f"SELECT * FROM {table_name}",
            conn
        )

    # 컬럼명 통일
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
    )

    return df


# ============================================================
# 데이터 로드
# ============================================================

region_df = load_table("accident_region_total")
driver_age_df = load_table("offending_driver_age")
driver_time_df = load_table("offending_driver_time")
weather_df = load_table("offending_driver_weather")
old_month_df = load_table("old_driver_month_time")
old_region_df = load_table("old_driver_region_time")


# ============================================================
# 제목
# ============================================================

st.title("🚨 SAFE 교통사고 분석")

st.caption(
    "지역·연령·시간대·기상상태를 기준으로 "
    "교통사고 현황과 고령운전자 사고 특성을 분석합니다."
)


# ============================================================
# TAB
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌎 지역별 사고",
    "👤 연령별 사고",
    "🕐 시간대 분석",
    "🌧 기상상태 분석",
    "👴 고령운전자 분석"
])


# ============================================================
# TAB 1
# 지역별 사고
# ============================================================

with tab1:

    st.header("지역별 교통사고 현황")

    region_df["year"] = pd.to_numeric(region_df["year"])
    region_df["accidents"] = pd.to_numeric(region_df["accidents"])

    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    latest_year = int(region_df["year"].max())

    latest = region_df[
        region_df["year"] == latest_year
    ]

    total_accident = int(
        latest["accidents"].sum()
    )

    top_sido = (
        latest
        .groupby("sido")["accidents"]
        .sum()
        .idxmax()
    )

    top_sigungu = (
        latest
        .assign(
            region=lambda x:
                x["sido"] + " " + x["sigungu"]
        )
        .groupby("region")["accidents"]
        .sum()
        .idxmax()
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        f"{latest_year}년 사고 건수",
        f"{total_accident:,}건"
    )

    c2.metric(
        "사고 최다 시도",
        top_sido
    )

    c3.metric(
        "사고 최다 시군구",
        top_sigungu
    )

    st.divider()


    # --------------------------------------------------------
    # 연도별 전국 사고 추세
    # --------------------------------------------------------

    st.subheader("연도별 전체 교통사고 추세")

    yearly = (
        region_df
        .groupby("year")["accidents"]
        .sum()
    )

    st.line_chart(
        yearly,
        x_label="연도",
        y_label="사고 건수"
    )


    # --------------------------------------------------------
    # 시도별
    # --------------------------------------------------------

    st.subheader(
        f"{latest_year}년 시도별 사고 현황"
    )

    sido_data = (
        latest
        .groupby("sido")["accidents"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(
        sido_data,
        x_label="시도",
        y_label="사고 건수"
    )


    # --------------------------------------------------------
    # 지역 선택
    # --------------------------------------------------------

    st.subheader("지역 상세 분석")

    col1, col2 = st.columns(2)

    with col1:

        sido = st.selectbox(
            "시도 선택",
            sorted(region_df["sido"].unique()),
            key="accident_sido"
        )

    sigungu_list = sorted(
        region_df[
            region_df["sido"] == sido
        ]["sigungu"].unique()
    )

    with col2:

        sigungu = st.selectbox(
            "시군구 선택",
            sigungu_list,
            key="accident_sigungu"
        )


    selected_region = region_df[
        (region_df["sido"] == sido)
        &
        (region_df["sigungu"] == sigungu)
    ]

    region_trend = (
        selected_region
        .groupby("year")["accidents"]
        .sum()
    )

    st.line_chart(
        region_trend,
        x_label="연도",
        y_label="사고 건수"
    )


# ============================================================
# TAB 2
# 연령별 사고
# ============================================================

with tab2:

    st.header("가해운전자 연령대별 교통사고")

    # wide → long
    age = driver_age_df.melt(
        id_vars="age_group",
        var_name="year",
        value_name="accidents"
    )

    age["year"] = (
        age["year"]
        .str.extract(r"(\d{4})")[0]
        .astype(int)
    )

    age["accidents"] = pd.to_numeric(
        age["accidents"]
    )

    age = age[
        age["age_group"] != "불명"
    ]


    # --------------------------------------------------------
    # 연령대 선택
    # --------------------------------------------------------

    selected_age = st.selectbox(
        "연령대 선택",
        age["age_group"].unique(),
        index=(
            list(age["age_group"].unique())
            .index("65세 이상")
            if "65세 이상"
            in age["age_group"].unique()
            else 0
        )
    )


    # --------------------------------------------------------
    # 연령대별 전체 사고
    # --------------------------------------------------------

    st.subheader("연령대별 사고 규모")

    age_total = (
        age
        .groupby("age_group")["accidents"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(
        age_total,
        x_label="연령대",
        y_label="사고 건수"
    )


    # --------------------------------------------------------
    # 선택 연령 연도별 추세
    # --------------------------------------------------------

    st.subheader(
        f"{selected_age} 사고 추세"
    )

    selected_age_df = (
        age[
            age["age_group"]
            == selected_age
        ]
        .groupby("year")["accidents"]
        .sum()
    )

    st.line_chart(
        selected_age_df,
        x_label="연도",
        y_label="사고 건수"
    )


    # --------------------------------------------------------
    # 전체 연령대 연도 비교
    # --------------------------------------------------------

    st.subheader(
        "연령대별 연도 변화"
    )

    age_trend = (
        age
        .pivot_table(
            index="year",
            columns="age_group",
            values="accidents",
            aggfunc="sum"
        )
    )

    st.line_chart(
        age_trend,
        x_label="연도",
        y_label="사고 건수"
    )


# ============================================================
# TAB 3
# 시간대
# ============================================================

with tab3:

    st.header(
        "가해운전자 연령대·시간대별 사고"
    )

    time = driver_time_df.melt(
        id_vars="age_group",
        var_name="time_slot",
        value_name="accidents"
    )

    time["time_slot"] = (
        time["time_slot"]
        .str.replace(
            "time_",
            "",
            regex=False
        )
        .str.replace(
            "_",
            "~",
            regex=False
        )
    )

    time["accidents"] = pd.to_numeric(
        time["accidents"]
    )

    time = time[
        time["age_group"] != "불명"
    ]


    # --------------------------------------------------------
    # 전체 시간대
    # --------------------------------------------------------

    st.subheader(
        "시간대별 전체 사고"
    )

    time_total = (
        time
        .groupby("time_slot")["accidents"]
        .sum()
    )

    st.bar_chart(
        time_total,
        x_label="시간대",
        y_label="사고 건수"
    )


    # --------------------------------------------------------
    # 연령대 선택
    # --------------------------------------------------------

    selected_time_age = st.selectbox(
        "분석할 연령대",
        time["age_group"].unique(),
        key="time_age"
    )

    selected = time[
        time["age_group"]
        == selected_time_age
    ]

    time_age = (
        selected
        .groupby("time_slot")["accidents"]
        .sum()
    )

    st.subheader(
        f"{selected_time_age} 시간대별 사고"
    )

    st.bar_chart(
        time_age,
        x_label="시간대",
        y_label="사고 건수"
    )


    # --------------------------------------------------------
    # 표
    # --------------------------------------------------------

    st.subheader(
        "연령 × 시간대 상세 비교"
    )

    time_matrix = time.pivot_table(
        index="age_group",
        columns="time_slot",
        values="accidents",
        aggfunc="sum",
        fill_value=0
    )

    st.dataframe(
        time_matrix,
        use_container_width=True
    )


# ============================================================
# TAB 4
# 기상상태
# ============================================================

with tab4:

    st.header(
        "기상상태별 교통사고"
    )

    weather_df["year"] = pd.to_numeric(
        weather_df["year"]
    )

    weather_df["accidents"] = pd.to_numeric(
        weather_df["accidents"]
    )

    weather_df = weather_df[
        weather_df["age_group"]
        != "불명"
    ]


    # --------------------------------------------------------
    # 연령대 선택
    # --------------------------------------------------------

    selected_weather_age = st.selectbox(
        "연령대 선택",
        weather_df["age_group"].unique(),
        key="weather_age"
    )

    selected = weather_df[
        weather_df["age_group"]
        == selected_weather_age
    ]


    # --------------------------------------------------------
    # 날씨별 사고
    # --------------------------------------------------------

    st.subheader(
        f"{selected_weather_age} 날씨별 사고 규모"
    )

    weather_total = (
        selected
        .groupby("weather")["accidents"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(
        weather_total,
        x_label="기상상태",
        y_label="사고 건수"
    )


    # --------------------------------------------------------
    # 연도 × 날씨
    # --------------------------------------------------------

    st.subheader(
        f"{selected_weather_age} 연도별·날씨별 사고 추세"
    )

    weather_trend = (
        selected
        .pivot_table(
            index="year",
            columns="weather",
            values="accidents",
            aggfunc="sum",
            fill_value=0
        )
    )

    st.line_chart(
        weather_trend,
        x_label="연도",
        y_label="사고 건수"
    )


# ============================================================
# TAB 5
# 고령운전자
# ============================================================

with tab5:

    st.header(
        "고령운전자 교통사고 분석"
    )


    # ========================================================
    # 월별 × 시간대
    # ========================================================

    old_month_df["year"] = pd.to_numeric(
        old_month_df["year"]
    )

    old_month_df["month"] = pd.to_numeric(
        old_month_df["month"]
    )

    old_month_df["accidents"] = pd.to_numeric(
        old_month_df["accidents"]
    )


    # 날짜 생성
    old_month_df["date"] = pd.to_datetime(
        dict(
            year=old_month_df["year"],
            month=old_month_df["month"],
            day=1
        )
    )


    # --------------------------------------------------------
    # 월별 사고 시계열
    # --------------------------------------------------------

    st.subheader(
        "월별 고령운전자 사고 추세"
    )

    monthly = (
        old_month_df
        .groupby("date")["accidents"]
        .sum()
    )

    st.line_chart(
        monthly,
        x_label="월",
        y_label="사고 건수"
    )


    # --------------------------------------------------------
    # 월별 사고
    # --------------------------------------------------------

    st.subheader(
        "월별 사고 규모"
    )

    month_total = (
        old_month_df
        .groupby("month")["accidents"]
        .sum()
    )

    st.bar_chart(
        month_total,
        x_label="월",
        y_label="사고 건수"
    )


    # --------------------------------------------------------
    # 시간대
    # --------------------------------------------------------

    st.subheader(
        "시간대별 고령운전자 사고"
    )

    old_time = (
        old_month_df
        .groupby("time_slot")["accidents"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(
        old_time,
        x_label="시간대",
        y_label="사고 건수"
    )


    st.divider()


    # ========================================================
    # 지역별 월간 사고
    # ========================================================

    st.subheader(
        "지역별 고령운전자 사고"
    )

    old_region_df["year"] = pd.to_numeric(
        old_region_df["year"]
    )

    old_region_df["month"] = pd.to_numeric(
        old_region_df["month"]
    )

    old_region_df["accidents"] = pd.to_numeric(
        old_region_df["accidents"]
    )


    # --------------------------------------------------------
    # 지역 선택
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        old_sido = st.selectbox(
            "시도",
            sorted(
                old_region_df[
                    "sido"
                ].unique()
            ),
            key="old_sido"
        )

    old_sigungu_list = sorted(
        old_region_df[
            old_region_df["sido"]
            == old_sido
        ]["sigungu"].unique()
    )

    with col2:

        old_sigungu = st.selectbox(
            "시군구",
            old_sigungu_list,
            key="old_sigungu"
        )


    selected_region = old_region_df[
        (old_region_df["sido"] == old_sido)
        &
        (
            old_region_df["sigungu"]
            == old_sigungu
        )
    ].copy()


    selected_region["date"] = pd.to_datetime(
        dict(
            year=selected_region["year"],
            month=selected_region["month"],
            day=1
        )
    )


    region_month = (
        selected_region
        .groupby("date")["accidents"]
        .sum()
    )


    st.subheader(
        f"{old_sido} {old_sigungu} 월별 사고 추세"
    )

    st.line_chart(
        region_month,
        x_label="월",
        y_label="사고 건수"
    )


    # --------------------------------------------------------
    # 지역 전체 비교
    # --------------------------------------------------------

    st.subheader(
        "시도별 고령운전자 사고 비교"
    )

    sido_old = (
        old_region_df
        .groupby("sido")["accidents"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(
        sido_old,
        x_label="시도",
        y_label="사고 건수"
    )


# ========================================================
# 미래 예측
# ========================================================

st.divider()

st.subheader("🔮 고령운전자 사고 미래 예측")

st.write(
    "ARIMA, SARIMA, Prophet 모델을 비교하고 "
    "예측 오차가 가장 작은 모델로 향후 12개월을 예측합니다."
)


# --------------------------------------------------------
# 월별 시계열 데이터 생성
# --------------------------------------------------------

forecast_data = (
    old_month_df
    .groupby(
        ["year", "month"],
        as_index=False
    )["accidents"]
    .sum()
)

forecast_data["date"] = pd.to_datetime(
    dict(
        year=forecast_data["year"],
        month=forecast_data["month"],
        day=1
    )
)


# --------------------------------------------------------
# 예측 실행 버튼
# --------------------------------------------------------

if st.button(
    "미래 12개월 예측",
    type="primary"
):

    with st.spinner(
        "ARIMA / SARIMA / Prophet 모델을 비교하고 있습니다..."
    ):

        forecast = forecast_best(
            forecast_data,
            "date",
            "accidents",
            frequency="monthly",
            steps=12
        )


    # ----------------------------------------------------
    # 미래 예측 결과
    # ----------------------------------------------------

    st.success(
        "모델 비교 및 미래 예측이 완료되었습니다."
    )

    st.subheader(
        "향후 12개월 사고 예측"
    )

    forecast_chart = (
        forecast
        .set_index("date")["prediction"]
    )

    st.line_chart(
        forecast_chart,
        x_label="월",
        y_label="예측 사고 건수"
    )


    # ----------------------------------------------------
    # 실제 + 예측 연결 차트
    # ----------------------------------------------------

    st.subheader(
        "실제 사고 추세 + 미래 예측"
    )

    actual = (
        forecast_data[
            ["date", "accidents"]
        ]
        .rename(
            columns={
                "accidents": "실제 사고"
            }
        )
        .set_index("date")
    )

    future = (
        forecast
        .rename(
            columns={
                "prediction": "예측 사고"
            }
        )
        .set_index("date")
    )

    combined = pd.concat(
        [
            actual,
            future
        ],
        axis=1
    )

    st.line_chart(
        combined,
        x_label="월",
        y_label="사고 건수"
    )


    # ----------------------------------------------------
    # 예측 데이터 표
    # ----------------------------------------------------

    with st.expander(
        "예측 결과 상세 보기"
    ):

        result_table = forecast.copy()

        result_table["date"] = (
            result_table["date"]
            .dt.strftime("%Y-%m")
        )

        result_table.columns = [
            "예측 월",
            "예측 사고 건수"
        ]

        st.dataframe(
            result_table,
            use_container_width=True,
            hide_index=True
        )