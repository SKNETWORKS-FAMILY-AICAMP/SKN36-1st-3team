import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from prophet import Prophet


# 연령대별 교통사고 수 비교

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 기본 데이터 차트 표시
def analyze_accident_age_basic(db_path: str = "database/accident.db"):
    """
    accident.db의 accident_age 테이블을 읽어 
    연령대별 실제 교통사고 데이터를 표로 요약하고, 개별 서브플롯 차트로 시각화합니다. (예측 제외)
    """
    # 1. 데이터베이스 연결 및 데이터 로드
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql("SELECT age_group, year, accidents FROM accident_age", conn)
        conn.close()
    except Exception as e:
        print(f"데이터베이스 연결 오류: {e}")
        return

    # 2. 콘솔에 연도별·연령대별 피벗 테이블 요약 출력
    pivot_df = df.pivot(index="age_group", columns="year", values="accidents")
    print("=" * 65)
    print(" [표] 연령대 및 연도별 교통사고 건수 현황 (실제 데이터)")
    print("=" * 65)
    print(pivot_df)
    print("=" * 65 + "\n")

    # 3. 연령대별 개별 서브플롯 차트 설정
    age_groups = df['age_group'].unique()
    n = len(age_groups)
    
    cols = 2
    rows = (n + 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(14, 5 * rows))
    axes = axes.flatten()

    for i, age in enumerate(age_groups):
        # 연령대별 데이터 추출 및 연도 순 정렬
        sub_df = df[df['age_group'] == age].sort_values('year')
        
        # 실제 데이터 라인 플롯 및 마커 그리기
        axes[i].plot(
            sub_df['year'], 
            sub_df['accidents'], 
            marker='o', 
            linestyle='-', 
            color='teal', 
            linewidth=2, 
            markersize=6, 
            label='실제 사고 건수'
        )
        
        # 그래프 디자인 설정
        axes[i].set_title(f"[{age}] 연도별 교통사고 발생 추이", fontsize=12, fontweight='bold')
        axes[i].set_xlabel("연도", fontsize=10)
        axes[i].set_ylabel("사고 건수", fontsize=10)
        axes[i].set_xticks(sub_df['year'])  # X축 연도를 명확하게 표시
        axes[i].legend(loc='best')
        axes[i].grid(True, linestyle='--', alpha=0.7)

    # 남는 서브플롯 빈 칸 제거
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.show()


# ARIMA 예측(2027~2035)
def forecast_accidents_age_arima(db_path: str = "database/accident.db"):
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql("SELECT age_group, year, accidents FROM accident_age", conn)
        conn.close()
    except Exception as e:
        print(f"데이터베이스 연결 오류: 예측 대상 엑셀/DB 경로를 확인해주세요. ({e})")
        return

    df = df[~df['age_group'].isin(['합계', '불명'])]
    
    target_years = list(range(2026, 2036))
    
    print("=" * 70)
    print(" [ARIMA 세밀 예측 - 2026~2035년 (2025년 실측 데이터 연계)]")
    print("=" * 70)
    
    age_groups = df['age_group'].unique()
    cols, rows = 2, (len(age_groups) + 1) // 2
    fig, axes = plt.subplots(rows, cols, figsize=(14, 4 * rows))
    axes = axes.flatten()
    
    for i, age in enumerate(age_groups):
        sub_df = df[df['age_group'] == age].sort_values('year')
        years = sub_df['year'].values
        values = sub_df['accidents'].values.astype(float)
        
        min_allowed = max(50.0, values.min() * 0.3)
        ts = pd.Series(values, index=pd.to_datetime(years.astype(str), format='%Y'))
        
        try:
            model = ARIMA(ts, order=(1, 1, 0))
            model_fit = model.fit()
            
            forecast_full = model_fit.forecast(steps=10)
            forecast_index = [2025 + j for j in range(1, 11)]
            forecast_series = pd.Series(forecast_full.values, index=forecast_index)
            
            target_preds = [max(min_allowed, forecast_series[yr]) for yr in target_years]
            
        except:
            avg_diff = np.mean(np.diff(values[-3:])) if len(values) > 1 else 0
            target_preds = [max(min_allowed, values[-1] + avg_diff * (yr - 2025)) for yr in target_years]

        print(f"\n- [{age}] 연령대 예측치:")
        for yr, val in zip(target_years, target_preds):
            print(f"  {yr}년: {int(val):,}건")

        # 1. 실제 데이터 그리기 (2021~2025년)
        axes[i].plot(years, values, marker='o', color='teal', linewidth=2, label='실제 데이터 (2021-2025)')
        
        # 2. 예측 데이터 그리기 (2026~2035년)
        # 자연스러운 연결을 위해 2025년 마지막 실제 데이터 값을 예측 배열의 맨 앞에 추가합니다.
        bridge_years = [years[-1]] + target_years
        bridge_preds = [values[-1]] + target_preds
        
        axes[i].plot(bridge_years, bridge_preds, linestyle='--', marker='x', color='crimson', linewidth=2, label='예측 (2026-2035)')
        
        axes[i].set_title(f"[{age}] 교통사고 정밀 예측", fontsize=11, fontweight='bold')
        axes[i].set_xlabel("연도")
        axes[i].set_ylabel("사고 건수")
        axes[i].legend(loc='best')
        axes[i].grid(True, linestyle='--', alpha=0.6)

    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.show()

# SARIMA 예측(2027~2035)
def forecast_accidents_age_sarima(db_path: str = "database/accident.db"):
    # 1. 데이터베이스 연결 및 데이터 로드
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql("SELECT age_group, year, accidents FROM accident_age", conn)
        conn.close()
    except Exception as e:
        print(f"데이터베이스 연결 오류: {e}")
        return

    # 합계 및 불명 제외
    df = df[~df['age_group'].isin(['합계', '불명'])]
    
    # 예측할 연도 (2026년 ~ 2035년)
    target_years = list(range(2026, 2036))
    
    print("=" * 70)
    print(" [SARIMAX 모델 연동 - 2026~2035년 연령대별 예측]")
    print(" (※ 연간 데이터 5개년 특성상 계절성 대신 안정된 상태 공간 추세 반영)")
    print("=" * 70)
    
    age_groups = df['age_group'].unique()
    cols, rows = 2, (len(age_groups) + 1) // 2
    fig, axes = plt.subplots(rows, cols, figsize=(14, 4 * rows))
    axes = axes.flatten()
    
    for i, age in enumerate(age_groups):
        sub_df = df[df['age_group'] == age].sort_values('year')
        years = sub_df['year'].values
        values = sub_df['accidents'].values.astype(float)
        
        # 하한선 설정 (최저치 기준 방어선)
        min_allowed = max(50.0, values.min() * 0.3)
        ts = pd.Series(values, index=pd.to_datetime(years.astype(str), format='%Y'))
        
        try:
            # SARIMAX 모델 학습 (연간 데이터이므로 비계절성 order만 부여)
            model = SARIMAX(ts, order=(1, 1, 0), enforce_stationarity=False, enforce_invertibility=False)
            model_fit = model.fit(disp=False)
            
            # 2026년부터 2035년까지 총 10년치 예측
            forecast_full = model_fit.forecast(steps=10)
            forecast_index = [2025 + j for j in range(1, 11)]
            forecast_series = pd.Series(forecast_full.values, index=forecast_index)
            
            # 하한선 보정 적용
            target_preds = [max(min_allowed, forecast_series[yr]) for yr in target_years]
            
        except Exception as e:
            # 예외 발생 시 최근 추세 평균 활용
            avg_diff = np.mean(np.diff(values[-3:])) if len(values) > 1 else 0
            target_preds = [max(min_allowed, values[-1] + avg_diff * (yr - 2025)) for yr in target_years]

        print(f"\n- [{age}] 연령대 예측치:")
        for yr, val in zip(target_years, target_preds):
            print(f"  {yr}년: {int(val):,}건")

        # 시각화 (2025년 실측치와 2026년 예측치 자연스럽게 연결)
        axes[i].plot(years, values, marker='o', color='teal', linewidth=2, label='실제 데이터 (2021-2025)')
        
        bridge_years = [years[-1]] + target_years
        bridge_preds = [values[-1]] + target_preds
        
        axes[i].plot(bridge_years, bridge_preds, linestyle='--', marker='x', color='crimson', linewidth=2, label='SARIMAX 예측 (2026-2035)')
        
        axes[i].set_title(f"[{age}] 교통사고 SARIMAX 예측", fontsize=11, fontweight='bold')
        axes[i].set_xlabel("연도")
        axes[i].set_ylabel("사고 건수")
        axes[i].legend(loc='best')
        axes[i].grid(True, linestyle='--', alpha=0.6)

    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.show()

# prophet예측(2027~2035)
def forecast_accidents_age_prophet(db_path: str = "database/accident.db"):
    # 1. 데이터베이스 연결 및 데이터 로드
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql("SELECT age_group, year, accidents FROM accident_age", conn)
        conn.close()
    except Exception as e:
        print(f"데이터베이스 연결 오류: {e}")
        return

    # 합계 및 불명 제외
    df = df[~df['age_group'].isin(['합계', '불명'])]
    
    # 예측할 연도 (2026년 ~ 2035년)
    target_years = list(range(2026, 2036))
    
    print("=" * 70)
    print(" [Prophet 모델 연동 - 2026~2035년 연령대별 장기 예측]")
    print("=" * 70)
    
    age_groups = df['age_group'].unique()
    cols, rows = 2, (len(age_groups) + 1) // 2
    fig, axes = plt.subplots(rows, cols, figsize=(14, 4 * rows))
    axes = axes.flatten()
    
    for i, age in enumerate(age_groups):
        sub_df = df[df['age_group'] == age].sort_values('year')
        
        # Prophet 형식에 맞게 데이터프레임 구성 (ds: 날짜, y: 값)
        prophet_df = pd.DataFrame({
            'ds': pd.to_datetime(sub_df['year'].astype(str) + '-01-01'),
            'y': sub_df['accidents'].astype(float)
        })
        
        min_allowed = max(50.0, prophet_df['y'].min() * 0.3)
        
        try:
            # Prophet 모델 생성 및 학습 (연간 데이터이므로 일별/주별 계절성 비활성화)
            model = Prophet(
                yearly_seasonality=False,
                weekly_seasonality=False,
                daily_seasonality=False,
                changepoint_prior_scale=0.05
            )
            model.fit(prophet_df)
            
            # 미래 예측을 위한 데이터프레임 생성 (2026~2035년)
            future_dates = pd.DataFrame({
                'ds': pd.to_datetime([f"{yr}-01-01" for yr in target_years])
            })
            
            forecast = model.predict(future_dates)
            raw_preds = forecast['yhat'].values
            
            # 하한선 보정 적용
            target_preds = [max(min_allowed, val) for val in raw_preds]
            
        except Exception as e:
            # 예외 발생 시 최근 추세 평균 활용
            values = prophet_df['y'].values
            avg_diff = np.mean(np.diff(values[-3:])) if len(values) > 1 else 0
            target_preds = [max(min_allowed, values[-1] + avg_diff * (yr - 2025)) for yr in target_years]

        print(f"\n- [{age}] 연령대 예측치:")
        for yr, val in zip(target_years, target_preds):
            print(f"  {yr}년: {int(val):,}건")

        # 시각화 (실제 데이터와 예측 데이터 연결)
        years = sub_df['year'].values
        values = sub_df['accidents'].values.astype(float)
        
        axes[i].plot(years, values, marker='o', color='teal', linewidth=2, label='실제 데이터 (2021-2025)')
        
        bridge_years = [years[-1]] + target_years
        bridge_preds = [values[-1]] + target_preds
        
        axes[i].plot(bridge_years, bridge_preds, linestyle='--', marker='x', color='crimson', linewidth=2, label='Prophet 예측 (2026-2035)')
        
        axes[i].set_title(f"[{age}] 교통사고 Prophet 예측", fontsize=11, fontweight='bold')
        axes[i].set_xlabel("연도")
        axes[i].set_ylabel("사고 건수")
        axes[i].legend(loc='best')
        axes[i].grid(True, linestyle='--', alpha=0.6)

    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    plt.show()


# 함수 실행 예시
if __name__ == "__main__":
    forecast_accidents_age_prophet("database/accident.db")