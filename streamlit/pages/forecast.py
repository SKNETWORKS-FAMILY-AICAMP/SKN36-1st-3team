import sys
import re
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from sqlalchemy import text


# ============================================================
# PROJECT ROOT
# SAFE/streamlit/pages/forecast.py
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

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
    return REGION_MAP.get(value, value)


REGION_ORDER = [
    "서울",
    "부산",
    "대구",
    "인천",
    "광주",
    "대전",
    "울산",
    "세종",
    "경기",
    "강원",
    "충북",
    "충남",
    "전북",
    "전남",
    "경북",
    "경남",
    "제주",
]


# ============================================================
# AGE HELPERS
# ============================================================

def age_start(value):
    value = str(value).strip()

    if not value:
        return 999

    if "이상" in value:
        match = re.search(r"(\d+)", value)
        return int(match.group(1)) if match else 999

    if "이하" in value:
        match = re.search(r"(\d+)", value)
        if match:
            upper = int(match.group(1))
            return max(0, upper - 4)
        return 999

    match = re.search(r"(\d+)", value)

    if match:
        return int(match.group(1))

    return 999


def is_65_plus(value):
    start = age_start(value)
    return 65 <= start < 999


# ============================================================
# DATABASE
# ============================================================

@st.cache_data(ttl=600)
def load_age_population():

    engine = get_engine()

    query = text(
        """
        SELECT
            region,
            year,
            gender,
            age_group,
            population
        FROM age_population
        """
    )

    with engine.connect() as conn:
        return pd.read_sql(query, conn)


@st.cache_data(ttl=600)
def load_license_age():

    engine = get_engine()

    query = text(
        """
        SELECT *
        FROM license_holder_age
        """
    )

    with engine.connect() as conn:
        return pd.read_sql(query, conn)


@st.cache_data(ttl=600)
def load_accident_age():

    engine = get_engine()

    query = text(
        """
        SELECT
            age_group,
            year,
            accidents,
            deaths,
            injuries
        FROM accident_age
        """
    )

    with engine.connect() as conn:
        return pd.read_sql(query, conn)


@st.cache_data(ttl=600)
def load_senior_region_accident():

    engine = get_engine()

    query = text(
        """
        SELECT
            sido,
            sigungu,
            year,
            month,
            accidents
        FROM senior_accident_region_month
        """
    )

    with engine.connect() as conn:
        return pd.read_sql(query, conn)



@st.cache_data(ttl=600)
def load_resident_population_monthly():

    engine = get_engine()

    query = text(
        """
        SELECT
            month,
            region,
            population
        FROM resident_population_monthly
        """
    )

    with engine.connect() as conn:
        return pd.read_sql(query, conn)


# ============================================================
# LOAD
# ============================================================

try:
    population_df = load_age_population()
    license_df = load_license_age()
    accident_age_df = load_accident_age()
    senior_region_df = load_senior_region_accident()
    resident_monthly_df = load_resident_population_monthly()

except Exception as e:
    st.error(
        f"미래 전망 데이터 조회 실패\n\n{e}"
    )
    st.stop()


# ============================================================
# COLUMN FINDER
# ============================================================

def find_column(frame, candidates):

    normalized = {
        str(col).strip().lower(): col
        for col in frame.columns
    }

    for candidate in candidates:

        if candidate in normalized:
            return normalized[candidate]

    return None


license_year_col = find_column(
    license_df,
    [
        "year",
        "base_year",
    ]
)

license_age_col = find_column(
    license_df,
    [
        "age",
        "age_group",
        "age_range",
    ]
)

license_count_col = find_column(
    license_df,
    [
        "count",
        "license_count",
        "holders",
        "holder_count",
    ]
)

license_region_col = find_column(
    license_df,
    [
        "region",
        "sido",
        "region_name",
    ]
)


if (
    license_year_col is None
    or license_age_col is None
    or license_count_col is None
):
    st.error(
        "license_holder_age 테이블에서 "
        "연도·연령·면허 소지자 수 컬럼을 찾을 수 없습니다."
    )
    st.stop()


# ============================================================
# BASIC CLEAN
# ============================================================

population_df["region"] = (
    population_df["region"]
    .fillna("")
    .astype(str)
    .str.strip()
    .apply(normalize_region)
)

population_df["year"] = pd.to_numeric(
    population_df["year"],
    errors="coerce"
)

population_df["population"] = pd.to_numeric(
    population_df["population"],
    errors="coerce"
).fillna(0)

population_df["gender"] = (
    population_df["gender"]
    .fillna("")
    .astype(str)
    .str.strip()
)

population_df["age_group"] = (
    population_df["age_group"]
    .fillna("")
    .astype(str)
    .str.strip()
)


license_df[license_year_col] = pd.to_numeric(
    license_df[license_year_col],
    errors="coerce"
)

license_df[license_count_col] = pd.to_numeric(
    license_df[license_count_col],
    errors="coerce"
).fillna(0)

license_df[license_age_col] = pd.to_numeric(
    license_df[license_age_col],
    errors="coerce"
)

if license_region_col is not None:
    license_df[license_region_col] = (
        license_df[license_region_col]
        .fillna("")
        .astype(str)
        .str.strip()
        .apply(normalize_region)
    )


accident_age_df["year"] = pd.to_numeric(
    accident_age_df["year"],
    errors="coerce"
)

for col in [
    "accidents",
    "deaths",
    "injuries",
]:
    accident_age_df[col] = pd.to_numeric(
        accident_age_df[col],
        errors="coerce"
    ).fillna(0)

accident_age_df["age_group"] = (
    accident_age_df["age_group"]
    .fillna("")
    .astype(str)
    .str.strip()
)


senior_region_df["sido"] = (
    senior_region_df["sido"]
    .fillna("")
    .astype(str)
    .str.strip()
    .apply(normalize_region)
)

senior_region_df["year"] = pd.to_numeric(
    senior_region_df["year"],
    errors="coerce"
)

senior_region_df["accidents"] = pd.to_numeric(
    senior_region_df["accidents"],
    errors="coerce"
).fillna(0)


resident_monthly_df["month"] = pd.to_datetime(
    resident_monthly_df["month"],
    errors="coerce"
)

resident_monthly_df["population"] = pd.to_numeric(
    resident_monthly_df["population"],
    errors="coerce"
).fillna(0)

resident_monthly_df["region"] = (
    resident_monthly_df["region"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.replace(
        r"\s*\([^)]*\)\s*$",
        "",
        regex=True
    )
    .apply(normalize_region)
)

resident_monthly_df = resident_monthly_df[
    resident_monthly_df["month"].notna()
].copy()


# ============================================================
# SERIES BUILDERS
# ============================================================

def build_total_population_proxy_series(region="전체"):

    data = resident_monthly_df.copy()

    invalid_regions = [
        "",
        "전국",
        "전국 총계",
        "계",
        "합계",
        "총계",
    ]

    if region == "전체":

        data = data[
            ~data["region"].isin(
                invalid_regions
            )
        ].copy()

        monthly = (
            data
            .groupby(
                "month",
                as_index=False
            )["population"]
            .sum()
        )

    else:

        monthly = data[
            data["region"] == region
        ][
            [
                "month",
                "population",
            ]
        ].copy()

    if monthly.empty:
        return pd.DataFrame(
            columns=[
                "year",
                "value",
            ]
        )

    # 연도별 마지막 관측 월을 대표값으로 사용
    monthly["year"] = monthly[
        "month"
    ].dt.year

    monthly = monthly.sort_values(
        "month"
    )

    annual = (
        monthly
        .groupby(
            "year",
            as_index=False
        )
        .tail(1)[
            [
                "year",
                "population",
            ]
        ]
        .rename(
            columns={
                "population": "value"
            }
        )
        .sort_values(
            "year"
        )
        .reset_index(
            drop=True
        )
    )

    return annual


def build_population_series(region="전체"):

    data = population_df.copy()

    if "계" in data["gender"].unique():
        data = data[
            data["gender"] == "계"
        ].copy()

    if region == "전체":
        regional = data[
            ~data["region"].isin(
                ["", "전국", "계", "합계", "총계"]
            )
        ].copy()

        if not regional.empty:
            data = regional

    else:
        data = data[
            data["region"] == region
        ].copy()

    data["age_group_clean"] = (
        data["age_group"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    data["senior_population"] = 0.0

    mask_60_69 = (
        data["age_group_clean"]
        .str.contains(
            r"60\s*[~\-]\s*69",
            regex=True,
            na=False
        )
    )

    mask_70_plus = (
        data["age_group_clean"]
        .apply(
            lambda value:
                70 <= age_start(value) < 999
        )
    )

    data.loc[
        mask_60_69,
        "senior_population"
    ] = (
        data.loc[
            mask_60_69,
            "population"
        ]
        * 0.5
    )

    data.loc[
        mask_70_plus,
        "senior_population"
    ] = data.loc[
        mask_70_plus,
        "population"
    ]

    result = (
        data
        .groupby(
            "year",
            as_index=False
        )["senior_population"]
        .sum()
        .rename(
            columns={
                "senior_population": "value"
            }
        )
        .dropna(
            subset=["year"]
        )
    )

    result["year"] = (
        result["year"]
        .astype(int)
    )

    return (
        result
        .sort_values("year")
        .reset_index(drop=True)
    )


def build_license_series(region="전체"):

    data = license_df.copy()

    data = data[
        data[
            license_year_col
        ].notna()
    ].copy()

    age_numeric = pd.to_numeric(
        data[
            license_age_col
        ],
        errors="coerce"
    )

    data = data[
        age_numeric >= 65
    ].copy()

    if (
        region != "전체"
        and license_region_col is not None
    ):
        data = data[
            data[
                license_region_col
            ] == region
        ].copy()

    result = (
        data
        .groupby(
            license_year_col,
            as_index=False
        )[license_count_col]
        .sum()
        .rename(
            columns={
                license_year_col: "year",
                license_count_col: "value",
            }
        )
    )

    result["year"] = pd.to_numeric(
        result["year"],
        errors="coerce"
    )

    result = result.dropna(
        subset=["year"]
    )

    result["year"] = (
        result["year"]
        .astype(int)
    )

    return (
        result
        .sort_values("year")
        .reset_index(drop=True)
    )


def build_accident_series(region="전체"):

    if region == "전체":

        data = accident_age_df[
            accident_age_df[
                "age_group"
            ].apply(is_65_plus)
        ].copy()

        result = (
            data
            .groupby(
                "year",
                as_index=False
            )["accidents"]
            .sum()
            .rename(
                columns={
                    "accidents": "value"
                }
            )
        )

    else:

        data = senior_region_df[
            senior_region_df[
                "sido"
            ] == region
        ].copy()

        result = (
            data
            .groupby(
                "year",
                as_index=False
            )["accidents"]
            .sum()
            .rename(
                columns={
                    "accidents": "value"
                }
            )
        )

    result["year"] = pd.to_numeric(
        result["year"],
        errors="coerce"
    )

    result = result.dropna(
        subset=["year"]
    )

    result["year"] = result[
        "year"
    ].astype(int)

    return result.sort_values(
        "year"
    ).reset_index(drop=True)


# ============================================================
# FORECAST
# ============================================================

def linear_forecast(
    series_df,
    horizon,
    proxy_series_df=None,
):

    source = (
        series_df[
            [
                "year",
                "value",
            ]
        ]
        .dropna()
        .copy()
        .sort_values(
            "year"
        )
        .drop_duplicates(
            "year",
            keep="last"
        )
    )

    if source.empty:

        return (
            source,
            pd.DataFrame(
                columns=[
                    "year",
                    "value",
                ]
            ),
            None
        )

    # --------------------------------------------------------
    # 실측 연도가 2개 이상이면 기존 선형 추세 사용
    # --------------------------------------------------------
    if len(source) >= 2:

        x = source[
            "year"
        ].to_numpy(
            dtype=float
        )

        y = source[
            "value"
        ].to_numpy(
            dtype=float
        )

        slope, intercept = np.polyfit(
            x,
            y,
            1
        )

        last_year = int(
            x.max()
        )

        future_years = np.arange(
            last_year + 1,
            last_year + horizon + 1
        )

        future_values = (
            slope
            * future_years
            + intercept
        )

        future_values = np.maximum(
            future_values,
            0
        )

        forecast_df = pd.DataFrame(
            {
                "year": future_years.astype(int),
                "value": future_values,
            }
        )

        fitted = (
            slope
            * x
            + intercept
        )

        ss_res = float(
            np.sum(
                (
                    y
                    - fitted
                ) ** 2
            )
        )

        ss_tot = float(
            np.sum(
                (
                    y
                    - y.mean()
                ) ** 2
            )
        )

        r2 = (
            1 - ss_res / ss_tot
            if ss_tot > 0
            else 1.0
        )

        model_info = {
            "method": "Linear Trend",
            "slope": float(slope),
            "intercept": float(intercept),
            "r2": float(r2),
            "n_years": len(source),
            "last_year": last_year,
        }

        return (
            source,
            forecast_df,
            model_info
        )

    # --------------------------------------------------------
    # 실측 연도가 1개뿐이면 주민등록 총인구의 장기 증가율을
    # 대리 추세(proxy)로 사용한 시나리오 전망
    # --------------------------------------------------------
    last_year = int(
        source.iloc[-1][
            "year"
        ]
    )

    base_value = float(
        source.iloc[-1][
            "value"
        ]
    )

    annual_growth = 0.0
    proxy_years = 0

    if (
        proxy_series_df is not None
        and not proxy_series_df.empty
    ):

        proxy = (
            proxy_series_df[
                [
                    "year",
                    "value",
                ]
            ]
            .dropna()
            .sort_values(
                "year"
            )
            .drop_duplicates(
                "year",
                keep="last"
            )
        )

        if len(proxy) >= 2:

            first_value = float(
                proxy.iloc[0][
                    "value"
                ]
            )

            last_proxy_value = float(
                proxy.iloc[-1][
                    "value"
                ]
            )

            year_gap = int(
                proxy.iloc[-1][
                    "year"
                ]
                - proxy.iloc[0][
                    "year"
                ]
            )

            if (
                first_value > 0
                and last_proxy_value > 0
                and year_gap > 0
            ):

                annual_growth = (
                    (
                        last_proxy_value
                        / first_value
                    ) ** (
                        1 / year_gap
                    )
                    - 1
                )

                proxy_years = len(
                    proxy
                )

    future_years = np.arange(
        last_year + 1,
        last_year + horizon + 1
    )

    future_values = np.array(
        [
            max(
                base_value
                * (
                    1 + annual_growth
                ) ** step,
                0
            )
            for step in range(
                1,
                horizon + 1
            )
        ]
    )

    forecast_df = pd.DataFrame(
        {
            "year": future_years.astype(int),
            "value": future_values,
        }
    )

    model_info = {
        "method": "Proxy Growth Scenario",
        "annual_growth": float(
            annual_growth
        ),
        "n_years": 1,
        "proxy_years": proxy_years,
        "last_year": last_year,
    }

    return (
        source,
        forecast_df,
        model_info
    )


def forecast_change_pct(
    actual_df,
    forecast_df
):

    if (
        actual_df.empty
        or forecast_df.empty
    ):
        return 0.0


    base = float(
        actual_df.iloc[-1][
            "value"
        ]
    )

    future = float(
        forecast_df.iloc[-1][
            "value"
        ]
    )


    if base <= 0:
        return 0.0


    return (
        future - base
    ) / base * 100


# ============================================================
# REGIONAL PRIORITY
# ============================================================

def build_region_priority(
    horizon
):

    rows = []

    for region in REGION_ORDER:

        pop_series = build_population_series(
            region
        )

        population_proxy = build_total_population_proxy_series(
            region
        )

        accident_series = build_accident_series(
            region
        )

        pop_actual, pop_future, _ = linear_forecast(
            pop_series,
            horizon,
            proxy_series_df=population_proxy
        )

        # 사고 실측 연도 2개 이상이면 자체 추세 사용
        if len(accident_series) >= 2:

            acc_actual, acc_future, _ = linear_forecast(
                accident_series,
                horizon
            )

        # 사고가 1개 연도뿐이면 고령인구 증가 시나리오에 연동
        elif len(accident_series) == 1:

            acc_actual = accident_series.copy()

            base_accidents = float(
                acc_actual.iloc[-1][
                    "value"
                ]
            )

            base_population = (
                float(
                    pop_actual.iloc[-1][
                        "value"
                    ]
                )
                if not pop_actual.empty
                else 0
            )

            future_years = (
                pop_future[
                    "year"
                ].tolist()
                if not pop_future.empty
                else []
            )

            if (
                base_population > 0
                and not pop_future.empty
            ):

                future_values = (
                    pop_future[
                        "value"
                    ]
                    / base_population
                    * base_accidents
                )

            else:

                future_values = pd.Series(
                    [
                        base_accidents
                        for _ in future_years
                    ]
                )

            acc_future = pd.DataFrame(
                {
                    "year": future_years,
                    "value": future_values,
                }
            )

        else:

            acc_actual = pd.DataFrame(
                columns=[
                    "year",
                    "value",
                ]
            )

            acc_future = pd.DataFrame(
                columns=[
                    "year",
                    "value",
                ]
            )

        if (
            pop_actual.empty
            and acc_actual.empty
        ):
            continue

        pop_change = forecast_change_pct(
            pop_actual,
            pop_future
        )

        accident_change = forecast_change_pct(
            acc_actual,
            acc_future
        )

        latest_population = (
            float(
                pop_actual.iloc[-1][
                    "value"
                ]
            )
            if not pop_actual.empty
            else 0
        )

        latest_accidents = (
            float(
                acc_actual.iloc[-1][
                    "value"
                ]
            )
            if not acc_actual.empty
            else 0
        )

        forecast_accidents = (
            float(
                acc_future.iloc[-1][
                    "value"
                ]
            )
            if not acc_future.empty
            else latest_accidents
        )

        accident_rate_10k = (
            latest_accidents
            / latest_population
            * 10000
            if latest_population > 0
            else 0
        )

        rows.append(
            {
                "region": region,
                "population_change": pop_change,
                "accident_change": accident_change,
                "latest_population": latest_population,
                "latest_accidents": latest_accidents,
                "forecast_accidents": forecast_accidents,
                "accident_rate_10k": accident_rate_10k,
            }
        )

    result = pd.DataFrame(
        rows
    )

    if result.empty:
        return result

    result[
        "population_score"
    ] = (
        result[
            "population_change"
        ]
        .rank(
            pct=True,
            method="average"
        )
        * 100
    )

    result[
        "accident_rate_score"
    ] = (
        result[
            "accident_rate_10k"
        ]
        .rank(
            pct=True,
            method="average"
        )
        * 100
    )

    result[
        "accident_scale_score"
    ] = (
        result[
            "forecast_accidents"
        ]
        .rank(
            pct=True,
            method="average"
        )
        * 100
    )

    # 지역별 값이 실제로 달라지도록
    # 고령인구 증가 30% + 현재 사고율 40% + 미래 사고규모 30%
    result[
        "priority_score"
    ] = (
        result[
            "population_score"
        ] * 0.30
        +
        result[
            "accident_rate_score"
        ] * 0.40
        +
        result[
            "accident_scale_score"
        ] * 0.30
    )

    result = result.sort_values(
        [
            "priority_score",
            "forecast_accidents",
            "accident_rate_10k",
        ],
        ascending=[
            False,
            False,
            False,
        ]
    ).reset_index(
        drop=True
    )

    result[
        "rank"
    ] = np.arange(
        1,
        len(result) + 1
    )

    return result


def priority_grade(score):

    if score >= 80:
        return "매우 높음"

    if score >= 65:
        return "높음"

    if score >= 45:
        return "주의"

    return "관심"


# ============================================================
# OPTIONS
# ============================================================

available_regions = [
    region
    for region in REGION_ORDER
    if (
        region in population_df[
            "region"
        ].unique()
        or region in senior_region_df[
            "sido"
        ].unique()
    )
]


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
    font-size: 19px !important;
    font-weight: 500 !important;
    min-height: 44px !important;
    white-space: nowrap !important;
}

.st-key-top_nav button:hover {
    color: #D6A348 !important;
}

.st-key-nav_logo button {
    color: #27314C !important;
    font-size: 34px !important;
    font-weight: 900 !important;
    justify-content: flex-start !important;
    padding-left: 0 !important;
}

.st-key-nav_future button {
    background: #D9A64A !important;
    color: #172035 !important;
    border-radius: 2px !important;
    font-weight: 900 !important;
}

.st-key-nav_future button * {
    color: #172035 !important;
    -webkit-text-fill-color: #172035 !important;
}


/* ==========================================================
   PAGE
========================================================== */

.st-key-forecast_page {
    background: #101625;
    border: 1px solid #34405A;
    border-radius: 20px;
    padding: 34px 36px 48px 36px;
    min-height: 900px;
}

.page-path {
    color: #D6A348;
    font-size: 16px;
    font-weight: 800;
    letter-spacing: 1.2px;
    margin-bottom: 10px;
}

.page-title {
    color: #FFFFFF;
    font-size: 45px;
    font-weight: 900;
    letter-spacing: -2px;
    line-height: 1.15;
    margin-bottom: 13px;
}

.page-sub {
    color: #B4BCCB;
    font-size: 18px;
    line-height: 1.7;
    margin-bottom: 24px;
}


/* ==========================================================
   INPUT
========================================================== */

label[data-testid="stWidgetLabel"] p {
    color: #E2E7EF !important;
    font-size: 16px !important;
    font-weight: 800 !important;
}

div[data-baseweb="select"] > div {
    background: #182035 !important;
    color: #FFFFFF !important;
    min-height: 46px !important;
    border: 1px solid #3A4662 !important;
    border-radius: 10px !important;
    box-shadow: none !important;
}

div[data-baseweb="select"] span,
div[data-baseweb="select"] svg {
    color: #E7ECF4 !important;
}

div[data-baseweb="select"] > div:focus-within {
    border-color: #D6A348 !important;
}


/* RADIO */

.st-key-horizon_radio [data-testid="stRadio"] {
    background: #182035;
    border: 1px solid #3A4662;
    border-radius: 11px;
    padding: 6px 12px;
}

.st-key-horizon_radio [data-testid="stRadio"] label p {
    color: #E7ECF4 !important;
}


/* ==========================================================
   KPI
========================================================== */

.forecast-kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 16px;
    width: 100%;
    align-items: stretch;
}

.forecast-kpi {
    width: 100%;
    min-width: 0;
    min-height: 180px;
    box-sizing: border-box;
    padding: 22px 20px;
    background: #182035;
    border: 1px solid #3A4661;
    border-radius: 16px;
    display: flex;
    flex-direction: column;
}

.forecast-kpi-label {
    color: #AAB5C7;
    font-size: 14px;
    line-height: 1.5;
    min-height: 46px;
    display: flex;
    align-items: flex-start;
}

.forecast-kpi-value {
    color: #FFFFFF;
    font-size: 25px;
    font-weight: 900;
    line-height: 1.2;
    min-height: 48px;
    display: flex;
    align-items: center;
    white-space: nowrap;
}

.forecast-kpi-value.gold {
    color: #F1C66A;
}

.forecast-kpi-value.orange {
    color: #E37B59;
}

.forecast-kpi-compare {
    color: #9EA9BA;
    font-size: 14px;
    line-height: 1.55;
    min-height: 34px;
    margin-top: auto;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 4px;
}

.forecast-kpi-compare b {
    color: #E7ECF4;
    font-size: 15px;
}

.forecast-kpi-change {
    display: inline-block;
    margin-left: 7px;
    padding: 3px 7px;
    border-radius: 999px;
    background: rgba(214,163,72,.10);
    border: 1px solid rgba(214,163,72,.30);
    color: #F1C66A;
    font-size: 13px;
    font-weight: 900;
}


/* ==========================================================
   PANELS
========================================================== */

.st-key-main_forecast_panel,
.st-key-priority_panel,
.st-key-detail_panel {
    background: #182035;
    border: 1px solid #3A4662;
    border-radius: 24px;
    padding: 24px 26px;
    margin-top: 18px;
}

.panel-title {
    color: #FFFFFF;
    font-size: 25px;
    font-weight: 900;
    margin-bottom: 7px;
}

.panel-sub {
    color: #B9C2D0;
    font-size: 16px;
    line-height: 1.75;
    margin-bottom: 12px;
}

.panel-sub b {
    color: #F1C66A;
}


/* ==========================================================
   SECTION
========================================================== */

.section-heading {
    display: flex;
    align-items: center;
    gap: 11px;
    margin: 34px 0 12px 3px;
    color: #FFFFFF;
    font-size: 27px;
    font-weight: 900;
}

.section-heading::before {
    content: "";
    width: 5px;
    height: 25px;
    border-radius: 4px;
    background: #D9A64A;
}

.section-sub {
    color: #AEB8C8;
    font-size: 16px;
    line-height: 1.75;
    margin: -3px 0 15px 3px;
}

.section-divider {
    height: 1px;
    margin: 34px 0 4px 0;
    background: linear-gradient(
        90deg,
        rgba(217,166,74,0),
        rgba(217,166,74,.85) 18%,
        rgba(92,107,137,.85) 82%,
        rgba(92,107,137,0)
    );
}


/* ==========================================================
   ANALYSIS
========================================================== */

.analysis-box {
    background: #121A2B;
    border: 1px solid #35415C;
    border-left: 4px solid #D6A348;
    border-radius: 7px 15px 15px 7px;
    padding: 18px 21px;
    margin-top: 18px;
    color: #DDE3EC;
    font-size: 16px;
    line-height: 1.85;
}

.analysis-box b {
    color: #FFFFFF;
}

.analysis-title {
    color: #F3C867;
    font-size: 19px;
    font-weight: 900;
    margin-bottom: 8px;
}


/* ==========================================================
   DATA SOURCE
========================================================== */

.source-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
}

.source-item {
    background: #121A2B;
    border: 1px solid #35415C;
    border-radius: 12px;
    padding: 13px 14px;
}

.source-label {
    color: #F1C66A;
    font-size: 14px;
    font-weight: 900;
    margin-bottom: 6px;
}

.source-text {
    color: #B8C2D2;
    font-size: 14px;
    line-height: 1.5;
}


/* ==========================================================
   TABLE
========================================================== */

.forecast-dark-table-wrap {
    width: 100%;
    overflow-x: auto;
    background: #182035;
    border: 1px solid #3A4662;
    border-radius: 12px;
}

.forecast-dark-table {
    width: 100%;
    border-collapse: collapse;
    background: #182035;
    color: #E7EAF0;
    font-size: 15px;
}

.forecast-dark-table th {
    background: #202A42;
    color: #D6A348;
    font-weight: 900;
    text-align: center;
    padding: 13px 14px;
    border-bottom: 1px solid #4A5670;
    white-space: nowrap;
}

.forecast-dark-table td {
    background: #182035;
    color: #E7EAF0;
    padding: 11px 13px;
    border-bottom: 1px solid #303B55;
    text-align: center;
}

.forecast-dark-table tbody tr:nth-child(even) td {
    background: #1B243A;
}


/* ==========================================================
   NOTICE
========================================================== */

.forecast-notice {
    background: rgba(217,166,74,.07);
    border: 1px solid rgba(217,166,74,.35);
    color: #C9D1DE;
    border-radius: 12px;
    padding: 14px 16px;
    font-size: 14px;
    line-height: 1.7;
    margin-top: 18px;
}

.forecast-notice b {
    color: #F1C66A;
}


@media(max-width:1000px) {
    .forecast-kpi-grid,
    .source-grid {
        grid-template-columns: 1fr 1fr;
    }
}


@media (max-width: 1100px) {
    .forecast-kpi-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 700px) {
    .forecast-kpi-grid {
        grid-template-columns: 1fr;
    }
}



/* ==========================================================
   FORECAST METHOD COMPARE TOGGLE
========================================================== */

.st-key-forecast_method_compare_toggle {
    margin-top: 14px;
    margin-bottom: 14px;
}

.st-key-forecast_method_compare_toggle button {
    width: 100% !important;
    min-height: 48px !important;

    background: #192238 !important;
    color: #E7EAF0 !important;

    border: 1px solid #414D69 !important;
    border-radius: 11px !important;

    box-shadow: none !important;

    justify-content: flex-start !important;
    padding-left: 16px !important;

    font-size: 16px !important;
    font-weight: 800 !important;
}

.st-key-forecast_method_compare_toggle button * {
    color: #E7EAF0 !important;
    -webkit-text-fill-color: #E7EAF0 !important;
}

.st-key-forecast_method_compare_toggle button:hover {
    background: #232D46 !important;
    border-color: #D6A348 !important;
}

.st-key-forecast_method_compare_toggle button:hover * {
    color: #F1C66A !important;
    -webkit-text-fill-color: #F1C66A !important;
}

.st-key-forecast_method_compare_body {
    background: #151D30;
    border: 1px solid #3A4662;
    border-radius: 16px;
    padding: 18px 20px 20px 20px;
    margin-top: -4px;
    margin-bottom: 18px;
}


/* ==========================================================
   METHOD COMPARE TABLE
========================================================== */

.method-compare-card {
    width: 100%;
    overflow-x: auto;
}

.method-compare-title {
    color: #FFFFFF;
    font-size: 19px;
    font-weight: 900;
    margin-bottom: 7px;
}

.method-compare-sub {
    color: #AEB8C8;
    font-size: 14px;
    line-height: 1.65;
    margin-bottom: 14px;
}

.method-compare-table {
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
    color: #FFFFFF;
    font-size: 14px;
}

.method-compare-table th {
    padding: 14px 12px;
    background: #222C45;
    border: 1px solid #46526C;
    color: #F1C66A;
    font-size: 14px;
    font-weight: 900;
    text-align: center;
    vertical-align: middle;
}

.method-compare-table td {
    padding: 14px 12px;
    border: 1px solid #35415C;
    color: #E7ECF4;
    line-height: 1.55;
    vertical-align: middle;
    word-break: keep-all;
}

.method-compare-table tbody tr:hover {
    background: rgba(214,163,72,.07);
}

.method-name {
    color: #FFFFFF !important;
    font-weight: 900;
}

.method-use {
    color: #F1C66A !important;
    font-size: 18px;
    font-weight: 900;
    text-align: center;
}

.method-no {
    color: #8F9AAF !important;
    font-size: 18px;
    font-weight: 900;
    text-align: center;
}

.method-summary {
    margin-top: 16px;
    padding: 15px 17px;
    background: #121A2B;
    border-left: 4px solid #D6A348;
    border-radius: 8px;
    color: #D8DFEA;
    font-size: 14px;
    line-height: 1.7;
}

.method-summary b {
    color: #F1C66A;
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
        vertical_alignment="center",
        gap="small",
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

        st.button(
            "미래 전망 예측하기 ▶",
            key="nav_future",
            use_container_width=True,
            disabled=True,
        )


# ============================================================
# PAGE
# ============================================================

with st.container(
    key="forecast_page"
):

    # ========================================================
    # HEADER
    # ========================================================

    st.html(
        """
        <div class="page-path">
            SAFER · FUTURE FORECAST
        </div>

        <div class="page-title">
            미래 전망 예측 결과
        </div>

        <div class="page-sub">
            고령인구, 고령운전자 면허 보유, 고령운전자 교통사고의
            과거 추세를 이용해 향후 변화를 전망하고
            지역별 정책 대응 우선순위를 비교합니다.
        </div>
        """
    )


    # ========================================================
    # FILTER
    # ========================================================

    f1, f2, f3 = st.columns(
        [
            1.25,
            1.0,
            2.0,
        ],
        gap="medium"
    )


    with f1:

        selected_region = st.selectbox(
            "지역",
            [
                "전체"
            ] + available_regions,
            index=0,
            key="forecast_region"
        )


    with f2:

        selected_horizon = st.selectbox(
            "예측 기간",
            [
                1,
                3,
                5,
                10,
            ],
            index=2,
            format_func=lambda value:
                f"{value}년",
            key="forecast_horizon"
        )


    with f3:

        st.html(
            """
            <div style="
                color:#AEB8C8;
                font-size: 15px;
                margin-top:3px;
                margin-bottom:7px;
                font-weight:800;
            ">
                예측 방식
            </div>

            <div style="
                min-height:46px;
                display:flex;
                align-items:center;
                padding:0 15px;
                background:#182035;
                border:1px solid #3A4662;
                border-radius:10px;
                color:#E7ECF4;
                font-size: 16px;
            ">
                데이터 충분 시 Linear Trend · 1개 연도만 있으면 인구증가 연동 시나리오
            </div>
            """
        )


    # ========================================================
    # SERIES
    # ========================================================

    pop_series = build_population_series(
        selected_region
    )

    license_series = build_license_series(
        selected_region
    )

    accident_series = build_accident_series(
        selected_region
    )


    population_proxy_series = build_total_population_proxy_series(
        selected_region
    )

    pop_actual, pop_forecast, pop_model = linear_forecast(
        pop_series,
        selected_horizon,
        proxy_series_df=population_proxy_series
    )

    # 면허는 지역 컬럼이 없으므로 전국 주민등록 총인구 추세를 proxy로 사용
    license_proxy_series = build_total_population_proxy_series(
        "전체"
    )

    license_actual, license_forecast, license_model = linear_forecast(
        license_series,
        selected_horizon,
        proxy_series_df=license_proxy_series
    )

    # 사고 실측이 1개 연도뿐이면 고령인구 전망과 연동
    if len(accident_series) >= 2:

        accident_actual, accident_forecast, accident_model = linear_forecast(
            accident_series,
            selected_horizon
        )

    elif len(accident_series) == 1:

        accident_actual = accident_series.copy()

        base_accidents = float(
            accident_actual.iloc[-1][
                "value"
            ]
        )

        base_population = (
            float(
                pop_actual.iloc[-1][
                    "value"
                ]
            )
            if not pop_actual.empty
            else 0
        )

        if (
            base_population > 0
            and not pop_forecast.empty
        ):

            accident_forecast = pd.DataFrame(
                {
                    "year": pop_forecast[
                        "year"
                    ].tolist(),
                    "value": (
                        pop_forecast[
                            "value"
                        ]
                        / base_population
                        * base_accidents
                    ).tolist(),
                }
            )

        else:

            accident_forecast = pd.DataFrame(
                {
                    "year": [
                        int(
                            accident_actual.iloc[-1][
                                "year"
                            ]
                        ) + step
                        for step in range(
                            1,
                            selected_horizon + 1
                        )
                    ],
                    "value": [
                        base_accidents
                        for _ in range(
                            selected_horizon
                        )
                    ],
                }
            )

        accident_model = {
            "method": "Senior Population Linked Scenario",
            "n_years": 1,
            "last_year": int(
                accident_actual.iloc[-1][
                    "year"
                ]
            ),
        }

    else:

        accident_actual = accident_series.copy()

        accident_forecast = pd.DataFrame(
            columns=[
                "year",
                "value",
            ]
        )

        accident_model = None


    available_last_years = [
        model["last_year"]
        for model in [
            pop_model,
            license_model,
            accident_model,
        ]
        if model is not None
    ]


    base_year = (
        max(
            available_last_years
        )
        if available_last_years
        else "-"
    )


    target_year = (
        base_year + selected_horizon
        if isinstance(
            base_year,
            int
        )
        else "-"
    )


    # ========================================================
    # FORECAST VALUES
    # ========================================================

    target_population = (
        int(
            round(
                pop_forecast.iloc[-1][
                    "value"
                ]
            )
        )
        if not pop_forecast.empty
        else 0
    )


    target_license = (
        int(
            round(
                license_forecast.iloc[-1][
                    "value"
                ]
            )
        )
        if not license_forecast.empty
        else 0
    )


    target_accident = (
        int(
            round(
                accident_forecast.iloc[-1][
                    "value"
                ]
            )
        )
        if not accident_forecast.empty
        else 0
    )


    pop_change = forecast_change_pct(
        pop_actual,
        pop_forecast
    )

    license_change = forecast_change_pct(
        license_actual,
        license_forecast
    )

    accident_change = forecast_change_pct(
        accident_actual,
        accident_forecast
    )


    priority_df = build_region_priority(
        selected_horizon
    )


    if (
        selected_region != "전체"
        and not priority_df.empty
        and selected_region
        in priority_df[
            "region"
        ].values
    ):

        selected_priority_row = (
            priority_df[
                priority_df[
                    "region"
                ] == selected_region
            ]
            .iloc[0]
        )

        selected_priority_score = float(
            selected_priority_row[
                "priority_score"
            ]
        )

        selected_priority_rank = int(
            selected_priority_row[
                "rank"
            ]
        )

        selected_priority_grade = priority_grade(
            selected_priority_score
        )

    elif not priority_df.empty:

        selected_priority_score = float(
            priority_df.iloc[0][
                "priority_score"
            ]
        )

        selected_priority_rank = 1

        selected_priority_grade = (
            "Top 5"
        )

    else:

        selected_priority_score = 0
        selected_priority_rank = 0
        selected_priority_grade = "-"


    # ========================================================
    # FORECAST METHOD COMPARISON - TOP COLLAPSIBLE
    # ========================================================

    if "show_forecast_method_compare" not in st.session_state:

        st.session_state[
            "show_forecast_method_compare"
        ] = False


    with st.container(
        key="forecast_method_compare_toggle"
    ):

        method_compare_open = st.session_state[
            "show_forecast_method_compare"
        ]


        method_compare_label = (
            "▲ 예측 방법 비교 및 선정 근거 닫기"
            if method_compare_open
            else "▼ 예측 방법 비교 및 선정 근거 보기"
        )


        if st.button(
            method_compare_label,
            key="forecast_method_compare_button",
            use_container_width=True,
        ):

            st.session_state[
                "show_forecast_method_compare"
            ] = not method_compare_open

            st.rerun()


    if st.session_state[
        "show_forecast_method_compare"
    ]:

        with st.container(
            key="forecast_method_compare_body"
        ):

            method_rows = [
                {
                    "방법": "Linear Trend",
                    "필요 데이터": "연도별 실측값 2개 이상",
                    "장점": "추세 방향과 변화량을 단순·명확하게 설명 가능",
                    "한계": "관측 연도가 적으면 장기 전망 신뢰도가 낮음",
                    "현재 적용": "○",
                    "선정 이유": "실측 연도가 2개 이상 확보된 지표의 기본 추세 전망",
                },
                {
                    "방법": "Proxy Growth Scenario",
                    "필요 데이터": "실측값 1개 + 장기 대리 시계열",
                    "장점": "실측 연도가 1개여도 0 또는 고정값 예측을 피할 수 있음",
                    "한계": "대리 지표의 변화가 대상 지표에도 이어진다는 가정 필요",
                    "현재 적용": "○",
                    "선정 이유": "고령인구·면허처럼 자체 연도 자료가 부족할 때 주민등록 인구 추세 활용",
                },
                {
                    "방법": "고령인구 연동 사고 시나리오",
                    "필요 데이터": "사고 실측값 1개 + 고령인구 전망",
                    "장점": "정책 대상 인구 변화와 사고 규모를 직접 연결해 해석하기 쉬움",
                    "한계": "도로환경·정책·운전행태 등 다른 사고 요인은 직접 반영하지 못함",
                    "현재 적용": "○",
                    "선정 이유": "지역별 사고 연도 자료가 부족한 경우 고령인구 변화에 연동해 사고 전망",
                },
                {
                    "방법": "ARIMA / 시계열 모델",
                    "필요 데이터": "충분히 긴 연속 시계열",
                    "장점": "자기상관과 시간 흐름을 통계적으로 반영 가능",
                    "한계": "현재처럼 연도별 관측치가 적은 데이터에는 부적합",
                    "현재 적용": "×",
                    "선정 이유": "현재 확보된 연도 수가 부족해 안정적인 모형 추정이 어려움",
                },
                {
                    "방법": "Prophet",
                    "필요 데이터": "충분한 월별·분기별 시계열",
                    "장점": "추세·계절성·변화점을 함께 다루기 편리함",
                    "한계": "짧은 연간 데이터에서는 장점이 거의 없음",
                    "현재 적용": "×",
                    "선정 이유": "고령인구·면허·지역 사고 데이터의 시간 해상도가 충분하지 않음",
                },
            ]


            method_df = pd.DataFrame(
                method_rows
            )


            method_table_rows = ""


            for _, row in method_df.iterrows():

                apply_class = (
                    "method-use"
                    if row["현재 적용"] == "○"
                    else "method-no"
                )


                method_table_rows += f"""
                <tr>
                    <td class="method-name">{row["방법"]}</td>
                    <td>{row["필요 데이터"]}</td>
                    <td>{row["장점"]}</td>
                    <td>{row["한계"]}</td>
                    <td class="{apply_class}">{row["현재 적용"]}</td>
                    <td>{row["선정 이유"]}</td>
                </tr>
                """


            st.html(
                f"""
                <div class="method-compare-card">

                    <div class="method-compare-title">
                        예측 방법 비교 및 선정 근거
                    </div>

                    <div class="method-compare-sub">
                        현재 SAFE 데이터의 연도 수와 구조를 기준으로
                        적용 가능한 예측 방법을 비교합니다.
                    </div>

                    <table class="method-compare-table">

                        <colgroup>
                            <col style="width:13%">
                            <col style="width:15%">
                            <col style="width:18%">
                            <col style="width:18%">
                            <col style="width:8%">
                            <col style="width:28%">
                        </colgroup>

                        <thead>
                            <tr>
                                <th>예측 방법</th>
                                <th>필요 데이터</th>
                                <th>장점</th>
                                <th>한계</th>
                                <th>적용</th>
                                <th>SAFE 선정 근거</th>
                            </tr>
                        </thead>

                        <tbody>
                            {method_table_rows}
                        </tbody>

                    </table>

                    <div class="method-summary">
                        <b>현재 SAFE의 선택</b><br>

                        하나의 모델을 모든 지표에 강제로 적용하지 않고,
                        <b>실측 연도가 충분하면 Linear Trend</b>,
                        실측값이 1개뿐이면 <b>Proxy Growth Scenario</b>,
                        지역 사고 전망은 <b>고령인구 변화 연동 시나리오</b>를 사용합니다.

                        현재 데이터 길이에서는 ARIMA·Prophet보다
                        계산 근거를 정책 담당자에게 설명하기 쉽고
                        과도한 모델링을 피할 수 있습니다.
                    </div>

                </div>
                """
            )


    # ========================================================
    # CURRENT VALUES
    # ========================================================

    current_population = int(round(pop_actual.iloc[-1]["value"])) if not pop_actual.empty else 0
    current_license = int(round(license_actual.iloc[-1]["value"])) if not license_actual.empty else 0
    current_accident = int(round(accident_actual.iloc[-1]["value"])) if not accident_actual.empty else 0

    current_population_year = int(pop_actual.iloc[-1]["year"]) if not pop_actual.empty else "-"
    current_license_year = int(license_actual.iloc[-1]["year"]) if not license_actual.empty else "-"
    current_accident_year = int(accident_actual.iloc[-1]["year"]) if not accident_actual.empty else "-"


    # ========================================================
    # KPI
    # ========================================================

    st.html(
        f"""
        <div class="forecast-kpi-grid">

            <div class="forecast-kpi">
                <div class="forecast-kpi-label">
                    65세 이상 인구 · 현재 대비 {target_year}년
                </div>
                <div class="forecast-kpi-value gold">
                    {target_population:,}명
                </div>
                <div class="forecast-kpi-compare">
                    현재 {current_population_year}년
                    <b>{current_population:,}명</b>
                    <span class="forecast-kpi-change">{pop_change:+.1f}%</span>
                </div>
            </div>

            <div class="forecast-kpi">
                <div class="forecast-kpi-label">
                    65세 이상 면허 소지자 · 현재 대비 {target_year}년
                </div>
                <div class="forecast-kpi-value">
                    {target_license:,}명
                </div>
                <div class="forecast-kpi-compare">
                    현재 {current_license_year}년
                    <b>{current_license:,}명</b>
                    <span class="forecast-kpi-change">{license_change:+.1f}%</span>
                </div>
            </div>

            <div class="forecast-kpi">
                <div class="forecast-kpi-label">
                    고령운전자 사고 · 현재 대비 {target_year}년
                </div>
                <div class="forecast-kpi-value orange">
                    {target_accident:,}건
                </div>
                <div class="forecast-kpi-compare">
                    현재 {current_accident_year}년
                    <b>{current_accident:,}건</b>
                    <span class="forecast-kpi-change">{accident_change:+.1f}%</span>
                </div>
            </div>

            <div class="forecast-kpi">
                <div class="forecast-kpi-label">
                    정책 대응 필요도
                </div>
                <div class="forecast-kpi-value">
                    {selected_priority_grade}
                </div>
                <div class="forecast-kpi-compare">
                    {(
                        f"지역 순위 <b>{selected_priority_rank}위</b>"
                        if selected_region != "전체" and selected_priority_rank > 0
                        else "전국 상위 우선지역 <b>Top 5</b>"
                    )}
                </div>
            </div>

        </div>
        """
    )


    # ========================================================
    # MAIN FORECAST
    # ========================================================

    st.html(
        """
        <div class="section-heading">
            전망 분석
        </div>

        <div class="section-sub">
            실선은 실제 데이터, 골드 점선은 미래 전망 구간입니다.
        </div>
        """
    )


    with st.container(
        key="main_forecast_panel"
    ):

        st.html(
            f"""
            <div class="panel-title">
                {selected_region if selected_region != "전체" else "전국"} 고령화 · 면허 · 사고 전망
            </div>

            <div class="panel-sub">
                서로 단위가 다른 세 지표를 각각 독립 패널로 확인합니다.
                예측기간은 <b>{selected_horizon}년</b>입니다.
            </div>
            """
        )


        c1, c2, c3 = st.columns(
            3,
            gap="medium"
        )


        def draw_forecast_chart(
            title,
            actual_df,
            forecast_df,
            unit,
            color,
        ):

            fig = go.Figure()


            if not actual_df.empty:

                fig.add_trace(
                    go.Scatter(
                        x=actual_df[
                            "year"
                        ],
                        y=actual_df[
                            "value"
                        ],
                        mode="lines+markers",
                        name="실제",
                        line=dict(
                            color=color,
                            width=3.5,
                        ),
                        marker=dict(
                            size=7,
                        ),
                        hovertemplate=(
                            "<b>%{x}년</b>"
                            "<br>"
                            f"{title}: %{{y:,.0f}}{unit}"
                            "<extra></extra>"
                        ),
                    )
                )


            if (
                not actual_df.empty
                and not forecast_df.empty
            ):

                connector = pd.DataFrame(
                    {
                        "year": [
                            int(
                                actual_df.iloc[-1][
                                    "year"
                                ]
                            )
                        ]
                        + forecast_df[
                            "year"
                        ].tolist(),

                        "value": [
                            float(
                                actual_df.iloc[-1][
                                    "value"
                                ]
                            )
                        ]
                        + forecast_df[
                            "value"
                        ].tolist(),
                    }
                )


                fig.add_trace(
                    go.Scatter(
                        x=connector[
                            "year"
                        ],
                        y=connector[
                            "value"
                        ],
                        mode="lines+markers",
                        name="예측",
                        line=dict(
                            color="#D98A68",
                            width=3,
                            dash="dash",
                        ),
                        marker=dict(
                            size=7,
                            color="#D98A68",
                        ),
                        hovertemplate=(
                            "<b>%{x}년</b>"
                            "<br>"
                            f"예측: %{{y:,.0f}}{unit}"
                            "<extra></extra>"
                        ),
                    )
                )


                fig.add_vline(
                    x=int(
                        actual_df.iloc[-1][
                            "year"
                        ]
                    ),
                    line_dash="dot",
                    line_color="#D6A348",
                    line_width=2,
                )


            fig.update_layout(
                title=dict(
                    text=title,
                    font=dict(
                        color="#FFFFFF",
                        size=21,
                    ),
                    x=0,
                ),
                height=350,
                margin=dict(
                    l=65,
                    r=25,
                    t=55,
                    b=55,
                ),
                paper_bgcolor="#182035",
                plot_bgcolor="#182035",
                showlegend=False,
                font=dict(
                    color="#E7ECF4",
                    size=17,
                ),
                xaxis=dict(
                    title="연도",
                    gridcolor="#303B55",
                    dtick=1,
                ),
                yaxis=(
                    lambda values: {
                        "title": unit,
                        "gridcolor": "#303B55",
                        "tickformat": ",",
                        "range": [
                            max(
                                0,
                                min(values)
                                - max(
                                    (max(values) - min(values)) * 0.35,
                                    abs(max(values)) * 0.025,
                                    1,
                                )
                            ),
                            max(values)
                            + max(
                                (max(values) - min(values)) * 0.35,
                                abs(max(values)) * 0.025,
                                1,
                            ),
                        ],
                    }
                )(
                    (
                        actual_df["value"].astype(float).tolist()
                        if not actual_df.empty
                        else []
                    )
                    +
                    (
                        forecast_df["value"].astype(float).tolist()
                        if not forecast_df.empty
                        else []
                    )
                    or [0, 1]
                ),
            )

            if (
                not actual_df.empty
                and not forecast_df.empty
            ):

                current_value = float(actual_df.iloc[-1]["value"])
                future_value = float(forecast_df.iloc[-1]["value"])

                change_pct = (
                    (future_value - current_value)
                    / current_value
                    * 100
                    if current_value > 0
                    else 0
                )

                fig.add_annotation(
                    x=int(forecast_df.iloc[-1]["year"]),
                    y=future_value,
                    text=(
                        f"<b>{future_value:,.0f}{unit}</b>"
                        f"<br>{change_pct:+.1f}%"
                    ),
                    showarrow=False,
                    xshift=-10,
                    yshift=30,
                    font=dict(
                        color="#F1C66A",
                        size=17,
                    ),
                    bgcolor="rgba(18,26,43,.90)",
                    bordercolor="#D6A348",
                    borderwidth=1,
                    borderpad=4,
                )


            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                }
            )


        with c1:
            draw_forecast_chart(
                "65세 이상 인구",
                pop_actual,
                pop_forecast,
                "명",
                "#79B69B",
            )


        with c2:
            draw_forecast_chart(
                "65세 이상 면허 소지자",
                license_actual,
                license_forecast,
                "명",
                "#91A8C8",
            )


        with c3:
            draw_forecast_chart(
                "고령운전자 사고",
                accident_actual,
                accident_forecast,
                "건",
                "#D9A64A",
            )


        license_scope_note = (
            "선택 지역별 면허 데이터가 없어 전국 면허 추세를 사용했습니다."
            if (
                selected_region != "전체"
                and license_region_col is None
            )
            else ""
        )


        st.html(
            f"""
            <div class="analysis-box">

                <div class="analysis-title">
                    전망 요약
                </div>

                {target_year}년까지 현재 추세가 이어진다고 가정할 경우
                65세 이상 인구는 최근 실측 대비
                <b>{pop_change:+.1f}%</b>,
                65세 이상 면허 소지자는
                <b>{license_change:+.1f}%</b>,
                고령운전자 사고는
                <b>{accident_change:+.1f}%</b> 변할 것으로 전망됩니다.

                <br>

                {license_scope_note}

            </div>
            """
        )


    # ========================================================
    # REGION PRIORITY
    # ========================================================

    st.html(
        """
        <div class="section-divider"></div>

        <div class="section-heading">
            정책 대응 우선지역
        </div>

        <div class="section-sub">
            고령인구 전망 변화, 고령인구 1만명당 현재 사고율,
            미래 예상 사고 규모를 종합해 지역별 상대 우선순위를 산출합니다.
        </div>
        """
    )


    with st.container(
        key="priority_panel"
    ):

        st.html(
            f"""
            <div class="panel-title">
                {target_year}년 기준 정책 대응 우선순위
            </div>

            <div class="panel-sub">
                지수는 절대적인 위험확률이 아니라
                <b>지역 간 상대 비교용 정책 우선순위</b>입니다.
                실측 연도가 부족한 지표는 주민등록 총인구 변화 또는
                고령인구 변화와 연동한 시나리오를 사용합니다.
            </div>
            """
        )


        if priority_df.empty:

            st.info(
                "지역별 우선순위를 계산할 데이터가 부족합니다."
            )

        else:

            top_priority = priority_df.head(
                7
            ).sort_values(
                "priority_score",
                ascending=True
            )


            colors = [
                "#D9A64A"
                if region == selected_region
                else "#D46A4F"
                if score >= 80
                else "#79B69B"

                for region, score
                in zip(
                    top_priority[
                        "region"
                    ],
                    top_priority[
                        "priority_score"
                    ]
                )
            ]


            fig_priority = go.Figure(
                go.Bar(
                    x=top_priority[
                        "priority_score"
                    ],
                    y=top_priority[
                        "region"
                    ],
                    orientation="h",
                    marker_color=colors,
                    text=[
                        f"{value:.1f}"
                        for value
                        in top_priority[
                            "priority_score"
                        ]
                    ],
                    textposition="outside",
                    textfont=dict(
                        color="#FFFFFF",
                        size=18,
                    ),
                    cliponaxis=False,
                    customdata=top_priority[
                        [
                            "population_change",
                            "accident_change",
                            "forecast_accidents",
                        ]
                    ],
                    hovertemplate=(
                        "<b>%{y}</b>"
                        "<br>"
                        "우선순위 지수: %{x:.1f}"
                        "<br>"
                        "고령인구 전망 변화: %{customdata[0]:+.1f}%"
                        "<br>"
                        "사고 전망 변화: %{customdata[1]:+.1f}%"
                        "<br>"
                        "예상 사고: %{customdata[2]:,.0f}건"
                        "<extra></extra>"
                    ),
                )
            )


            fig_priority.update_layout(
                height=500,
                margin=dict(
                    l=75,
                    r=70,
                    t=30,
                    b=55,
                ),
                paper_bgcolor="#182035",
                plot_bgcolor="#182035",
                showlegend=False,
                font=dict(
                    color="#E7ECF4",
                ),
                xaxis=dict(
                    title="정책 대응 우선순위 지수",
                    gridcolor="#303B55",
                    range=[
                        0,
                        max(
                            float(
                                top_priority[
                                    "priority_score"
                                ].max()
                            ) * 1.20,
                            100,
                        )
                    ],
                ),
                yaxis=dict(
                    title=None,
                ),
            )


            st.plotly_chart(
                fig_priority,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                }
            )


            top3 = priority_df.head(
                3
            )

            top3_text = " · ".join(
                [
                    (
                        f"{int(row['rank'])}위 "
                        f"{row['region']} "
                        f"({row['priority_score']:.1f})"
                    )
                    for _, row in top3.iterrows()
                ]
            )


            reason_lines = []

            for _, row in top3.iterrows():

                reason_lines.append(
                    f"""
                    <div style="
                        margin-top:8px;
                        padding:9px 11px;
                        background:#182035;
                        border:1px solid #35415C;
                        border-radius:9px;
                    ">
                        <b>{row['region']}</b>
                        · 우선순위 {row['priority_score']:.1f}점
                        <br>
                        고령인구 전망 변화
                        <b>{row['population_change']:+.1f}%</b>
                        · 고령인구 1만명당 사고
                        <b>{row['accident_rate_10k']:.1f}건</b>
                        · {target_year}년 예상 사고
                        <b>{row['forecast_accidents']:,.0f}건</b>
                    </div>
                    """
                )

            priority_reason_html = "".join(
                reason_lines
            )


            st.html(
                f"""
                <div class="analysis-box">

                    <div class="analysis-title">
                        우선지역 선정 기준
                    </div>

                    이 순위는 단순 사고건수 순위가 아니라
                    세 지표를 지역 간 상대점수로 환산해 계산합니다.

                    <br><br>

                    <b>① 고령인구 전망 변화 30%</b>
                    · 향후 고령 인구 증가 부담

                    <br>

                    <b>② 고령인구 1만명당 현재 사고율 40%</b>
                    · 인구 규모를 보정한 현재 사고 위험

                    <br>

                    <b>③ {target_year}년 예상 사고 규모 30%</b>
                    · 향후 실제 정책 수요 규모

                    <br><br>

                    현재 모델 기준 상위 지역은
                    <b>{top3_text}</b>입니다.

                    {priority_reason_html}

                    <br>

                    ※ 우선순위 지수는 절대 위험확률이 아니라
                    <b>지역 간 정책 검토 우선순위</b>를 비교하기 위한 상대 지표입니다.

                </div>
                """
            )


    # ========================================================
    # DETAIL TABLE
    # ========================================================

    st.html(
        """
        <div class="section-divider"></div>

        <div class="section-heading">
            전망 결과 상세
        </div>

        <div class="section-sub">
            지역별 전망 변화와 정책 대응 우선순위를 표로 확인합니다.
        </div>
        """
    )


    with st.container(
        key="detail_panel"
    ):

        if priority_df.empty:

            st.info(
                "표시할 지역별 전망 데이터가 없습니다."
            )

        else:

            table_rows = ""


            for _, row in priority_df.iterrows():

                grade = priority_grade(
                    float(
                        row[
                            "priority_score"
                        ]
                    )
                )


                table_rows += f"""
                    <tr>
                        <td>{int(row["rank"])}</td>
                        <td>{row["region"]}</td>
                        <td>{int(round(row["latest_population"])):,}명</td>
                        <td>{row["population_change"]:+.1f}%</td>
                        <td>{int(round(row["latest_accidents"])):,}건</td>
                        <td>{row["accident_change"]:+.1f}%</td>
                        <td>{row["accident_rate_10k"]:.1f}건</td>
                        <td>{int(round(row["forecast_accidents"])):,}건</td>
                        <td>{row["priority_score"]:.1f}</td>
                        <td>{grade}</td>
                    </tr>
                """


            st.html(
                f"""
                <div class="forecast-dark-table-wrap">

                    <table class="forecast-dark-table">

                        <thead>
                            <tr>
                                <th>순위</th>
                                <th>지역</th>
                                <th>현재 고령인구</th>
                                <th>{target_year}년 고령인구 변화</th>
                                <th>현재 사고</th>
                                <th>{target_year}년 사고 변화</th>
                                <th>고령인구 1만명당 사고</th>
                                <th>{target_year}년 예상 사고</th>
                                <th>우선순위 지수</th>
                                <th>정책 필요도</th>
                            </tr>
                        </thead>

                        <tbody>
                            {table_rows}
                        </tbody>

                    </table>

                </div>
                """
            )


    # ========================================================
    # DATA SOURCES
    # ========================================================

    st.html(
        """
        <div class="section-divider"></div>

        <div class="section-heading">
            연결 데이터
        </div>

        <div class="section-sub">
            미래 전망 계산에 사용되는 SAFE 데이터 테이블입니다.
        </div>

        <div class="source-grid">

            <div class="source-item">
                <div class="source-label">
                    주민등록 총인구 추세
                </div>
                <div class="source-text">
                    resident_population_monthly
                </div>
            </div>

            <div class="source-item">
                <div class="source-label">
                    고령 인구
                </div>
                <div class="source-text">
                    age_population
                </div>
            </div>

            <div class="source-item">
                <div class="source-label">
                    운전면허
                </div>
                <div class="source-text">
                    license_holder_age
                </div>
            </div>

            <div class="source-item">
                <div class="source-label">
                    전국 고령운전자 사고
                </div>
                <div class="source-text">
                    accident_age
                </div>
            </div>

            <div class="source-item">
                <div class="source-label">
                    지역 고령운전자 사고
                </div>
                <div class="source-text">
                    senior_accident_region_month
                </div>
            </div>

        </div>
        """
    )



    # ========================================================
    # MODEL NOTICE
    # ========================================================

    st.html(
        f"""
        <div class="forecast-notice">

            <b>예측 해석 주의</b>

            <br>

            현재 페이지는 DB에 적재된 연도별 실측값에
            단순 선형 추세(Linear Trend)를 적용한 참고용 전망입니다.

            <br>

            <b>65세 이상 인구</b>는 현재 age_population 테이블이
            10세 단위 구간으로 구성되어 있어
            60~69세 인구의 50%를 65~69세로 근사하고
            70세 이상 인구를 합산하여 계산합니다.

            <br>

            연도별 고령인구·면허·사고 실측값이 1개 연도뿐인 경우에는
            임의의 선형회귀를 만들지 않고,
            resident_population_monthly의 장기 인구 변화 또는
            고령인구 전망 변화에 연동한 <b>시나리오 전망</b>을 사용합니다.

            <br>

            특히 실측 연도가 짧은 상태에서 5년·10년을 예측하면
            실제 정책 변화, 인구 이동, 면허 반납, 제도 변화 등을
            충분히 반영하지 못할 수 있습니다.

            <br>

            따라서 이 결과는 확정적인 미래값이 아니라
            <b>지역 간 추세 비교와 정책 검토 우선순위 지원</b>을 위한
            보조 지표로 사용하는 것을 권장합니다.

        </div>
        """
    )