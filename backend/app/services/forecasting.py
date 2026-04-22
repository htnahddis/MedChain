import pandas as pd
import numpy as np
from prophet import Prophet
import lightgbm as lgb
from typing import List, Dict, Optional
import warnings

warnings.filterwarnings('ignore')

class DemandForecaster:
    """
    Ensemble demand forecaster combining Facebook Prophet and LightGBM.
    The ultimate balance of API latency and forecast accuracy.
    """

    SEASONAL_FACTORS = {
        'Rehydration':   {7: 3.40, 8: 3.10, 9: 2.90},
        'Antibiotic':    {7: 1.80, 8: 1.75, 9: 1.60},
        'Antifungal':    {7: 2.20, 8: 2.00, 9: 1.80},
        'GI':            {7: 1.60, 8: 1.55, 9: 1.45},
        'Respiratory':   {7: 1.30, 8: 1.25, 9: 1.20},
    }

    def __init__(self, medicine_category: str):
        self.category = medicine_category
        self.prophet_model: Optional[Prophet] = None
        self.lgb_model: Optional[lgb.LGBMRegressor] = None
        self.last_time_idx = 0

    def prepare_dataframe(self, consumption_records: List[Dict]) -> pd.DataFrame:
        df = pd.DataFrame(consumption_records)
        df['ds'] = pd.to_datetime(df['date'])
        df['y'] = df['units_consumed'].astype(float)
        df = df.sort_values('ds').reset_index(drop=True)
        
        df['is_monsoon'] = df['ds'].dt.month.isin([7, 8, 9]).astype(float)
        
        return df[['ds', 'y', 'is_monsoon']]

    def fit_prophet(self, df: pd.DataFrame) -> Prophet:
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            changepoint_prior_scale=0.05,
            seasonality_prior_scale=10.0,
            interval_width=0.95
        )
        model.add_regressor('is_monsoon', standardize=False)
        model.fit(df[['ds', 'y', 'is_monsoon']])
        self.prophet_model = model
        return model

    def fit_lightgbm(self, df: pd.DataFrame) -> None:
        """Engineers temporal features so the tree model understands the calendar."""
        df_lgb = df.copy()
        df_lgb['time_idx'] = np.arange(len(df_lgb))
        df_lgb['dayofweek'] = df_lgb['ds'].dt.dayofweek
        df_lgb['month'] = df_lgb['ds'].dt.month
        df_lgb['dayofyear'] = df_lgb['ds'].dt.dayofyear
        
        X = df_lgb[['time_idx', 'dayofweek', 'month', 'dayofyear', 'is_monsoon']]
        y = df_lgb['y']
        
        # LightGBM is inherently faster than XGBoost
        self.lgb_model = lgb.LGBMRegressor(
            n_estimators=100, 
            max_depth=5, 
            learning_rate=0.05,
            subsample=0.8,
            verbosity=-1  # Mutes LightGBM console spam
        )
        self.lgb_model.fit(X, y)
        self.last_time_idx = len(df_lgb) - 1

    def forecast(self, df: pd.DataFrame, horizon_days: int = 90) -> pd.DataFrame:
        self.fit_prophet(df)
        self.fit_lightgbm(df)

        # --- Prophet Forecast ---
        future = self.prophet_model.make_future_dataframe(periods=horizon_days)
        future['is_monsoon'] = future['ds'].dt.month.isin([7, 8, 9]).astype(float)
        prophet_pred = self.prophet_model.predict(future).tail(horizon_days)

        # --- LightGBM Forecast ---
        lgb_future = pd.DataFrame({'ds': future['ds'].tail(horizon_days)})
        lgb_future['time_idx'] = np.arange(self.last_time_idx + 1, self.last_time_idx + 1 + horizon_days)
        lgb_future['dayofweek'] = lgb_future['ds'].dt.dayofweek
        lgb_future['month'] = lgb_future['ds'].dt.month
        lgb_future['dayofyear'] = lgb_future['ds'].dt.dayofyear
        lgb_future['is_monsoon'] = lgb_future['ds'].dt.month.isin([7, 8, 9]).astype(float)
        
        lgb_yhat = self.lgb_model.predict(lgb_future[['time_idx', 'dayofweek', 'month', 'dayofyear', 'is_monsoon']])

        # --- Dynamic Blend ---
        # 85% Prophet during monsoon to preserve the outbreak spike, 60% otherwise.
        blend_weights = np.where(lgb_future['is_monsoon'] == 1.0, 0.85, 0.60)
        ensemble_yhat = (blend_weights * prophet_pred['yhat'].values) + ((1 - blend_weights) * lgb_yhat)
        
        result = pd.DataFrame({
            'forecast_date': prophet_pred['ds'].values,
            'predicted_units': np.maximum(0, ensemble_yhat).astype(int),
            'upper_ci': np.maximum(0, prophet_pred['yhat_upper'].values).astype(int),
            'lower_ci': np.maximum(0, prophet_pred['yhat_lower'].values).astype(int),
            'model_pred': ensemble_yhat,  # Keeps your Pydantic schema happy
        })
        return result

    def calculate_mape(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        mask = actual != 0
        return float(np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100)