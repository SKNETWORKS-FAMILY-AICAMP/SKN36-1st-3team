import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from prophet import Prophet


plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


# ============================================================
# 평가
# ============================================================

def evaluate(actual, pred):
    actual = np.array(actual, dtype=float)
    pred = np.array(pred, dtype=float)

    mae = mean_absolute_error(actual, pred)
    rmse = np.sqrt(mean_squared_error(actual, pred))

    mask = actual != 0
    mape = np.mean(
        np.abs(
            (actual[mask] - pred[mask])
            / actual[mask]
        )
    ) * 100

    return {
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2),
        "MAPE": round(mape, 2)
    }


# ============================================================
# ARIMA
# ============================================================

def arima(train, steps):
    model = ARIMA(
        train,
        order=(1, 1, 1)
    ).fit()

    return np.clip(
        model.forecast(steps),
        0,
        None
    )


# ============================================================
# SARIMA
# ============================================================

def sarima(train, steps):
    model = SARIMAX(
        train,
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, 12)
    ).fit(disp=False)

    return np.clip(
        model.forecast(steps),
        0,
        None
    )


# ============================================================
# Prophet
# ============================================================

def prophet(train_df, steps, frequency="monthly"):
    data = train_df[["date", "value"]].copy()

    data.columns = ["ds", "y"]

    model = Prophet(
        yearly_seasonality=(frequency == "monthly"),
        weekly_seasonality=False,
        daily_seasonality=False
    )

    model.fit(data)

    freq = "MS" if frequency == "monthly" else "YS"

    future = model.make_future_dataframe(
        periods=steps,
        freq=freq
    )

    forecast = model.predict(future)

    return np.clip(
        forecast.tail(steps)["yhat"].values,
        0,
        None
    )


# ============================================================
# 모델 비교
# ============================================================

def compare_models(
    df,
    date_col,
    value_col,
    frequency="monthly",
    test_size=None
):
    data = df[[date_col, value_col]].copy()
    data.columns = ["date", "value"]

    data["date"] = pd.to_datetime(data["date"])
    data["value"] = pd.to_numeric(data["value"])

    data = (
        data.groupby("date", as_index=False)["value"]
        .sum()
        .sort_values("date")
    )

    if test_size is None:
        test_size = 12 if frequency == "monthly" else 1

    train = data.iloc[:-test_size]
    test = data.iloc[-test_size:]

    train_series = (
        train
        .set_index("date")["value"]
    )

    actual = test["value"].values

    results = {}
    predictions = {}

    # ARIMA
    arima_pred = arima(
        train_series,
        test_size
    )

    results["ARIMA"] = evaluate(
        actual,
        arima_pred
    )

    predictions["ARIMA"] = arima_pred

    # SARIMA는 월별 데이터만
    if frequency == "monthly":
        sarima_pred = sarima(
            train_series,
            test_size
        )

        results["SARIMA"] = evaluate(
            actual,
            sarima_pred
        )

        predictions["SARIMA"] = sarima_pred

    # Prophet
    prophet_pred = prophet(
        train,
        test_size,
        frequency
    )

    results["Prophet"] = evaluate(
        actual,
        prophet_pred
    )

    predictions["Prophet"] = prophet_pred

    result_df = (
        pd.DataFrame(results)
        .T
        .reset_index()
        .rename(columns={"index": "model"})
        .sort_values("MAPE")
        .reset_index(drop=True)
    )

    print("\n===== 모델 성능 비교 =====")
    print(result_df)

    print(
        "\n최적 모델:",
        result_df.iloc[0]["model"]
    )

    # 실제값 vs 예측값
    plt.figure(figsize=(10, 5))

    plt.plot(
        test["date"],
        actual,
        marker="o",
        label="실제값"
    )

    for name, pred in predictions.items():
        plt.plot(
            test["date"],
            pred,
            marker="o",
            linestyle="--",
            label=name
        )

    plt.title("모델별 예측 성능 비교")
    plt.xlabel("기간")
    plt.ylabel(value_col)
    plt.legend()
    plt.grid(alpha=0.3)

    if frequency == "yearly":
        years = test["date"].dt.year
        plt.xticks(
            test["date"],
            years.astype(int)
        )

    plt.tight_layout()
    plt.show()

    return result_df


# ============================================================
# 가장 좋은 모델로 미래 예측
# ============================================================

def forecast_best(
    df,
    date_col,
    value_col,
    frequency="monthly",
    steps=12
):
    # 1. 모델 성능 비교
    result = compare_models(
        df,
        date_col,
        value_col,
        frequency
    )

    best_model = result.iloc[0]["model"]

    # 2. 전체 데이터
    data = df[[date_col, value_col]].copy()

    data.columns = ["date", "value"]
    data["date"] = pd.to_datetime(data["date"])
    data["value"] = pd.to_numeric(data["value"])

    data = (
        data.groupby("date", as_index=False)["value"]
        .sum()
        .sort_values("date")
    )

    series = data.set_index("date")["value"]

    # 3. 최적 모델로 재학습
    if best_model == "ARIMA":
        pred = arima(
            series,
            steps
        )

    elif best_model == "SARIMA":
        pred = sarima(
            series,
            steps
        )

    else:
        pred = prophet(
            data,
            steps,
            frequency
        )

    # 4. 미래 날짜
    freq = "MS" if frequency == "monthly" else "YS"

    future_dates = pd.date_range(
        data["date"].max(),
        periods=steps + 1,
        freq=freq
    )[1:]

    forecast_df = pd.DataFrame({
        "date": future_dates,
        "prediction": np.round(pred).astype(int)
    })

    # 5. 최종 미래예측 그래프
    plt.figure(figsize=(10, 5))

    plt.plot(
        data["date"],
        data["value"],
        marker="o",
        label="실제값"
    )

    plt.plot(
        future_dates,
        pred,
        marker="o",
        linestyle="--",
        label=f"{best_model} 예측"
    )

    plt.title(
        f"최적 모델 미래 예측 - {best_model}"
    )

    plt.xlabel("연도")
    plt.ylabel(value_col)
    plt.legend()
    plt.grid(alpha=0.3)

    if frequency == "yearly":
        all_dates = list(data["date"]) + list(future_dates)
        all_years = [d.year for d in all_dates]

        plt.xticks(
            all_dates,
            all_years
        )

    plt.tight_layout()
    plt.show()

    print("\n===== 미래 예측 결과 =====")
    print(forecast_df)

    return forecast_df