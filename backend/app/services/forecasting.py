import pandas as pd
import numpy as np
from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
from typing import List, Dict, Optional
from datetime import date, timedelta
import warnings
warnings.filterwarnings('ignore')


class DemandForecaster:
    """
    Ensemble demand forecaster combining Facebook Prophet and ARIMA.
    Prophet handles seasonality (monsoon spikes); ARIMA captures 
    short-term autocorrelation.
    """

    # Monsoon demand multipliers by medicine category (Jul=7, Aug=8, Sep=9)
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
        self.arima_model = None

    def prepare_dataframe(self, consumption_records: List[Dict]) -> pd.DataFrame:
        """
        Converts raw consumption records to Prophet-compatible format.
        Adds monsoon seasonality as external regressor.
        """
        df = pd.DataFrame(consumption_records)
        df['ds'] = pd.to_datetime(df['date'])
        df['y'] = df['units_consumed'].astype(float)
        df = df.sort_values('ds').reset_index(drop=True)
        
        # Add monsoon regressor
        df['is_monsoon'] = df['ds'].dt.month.isin([7, 8, 9]).astype(float)
        
        # Apply seasonal multiplier based on category
        seasonal = self.SEASONAL_FACTORS.get(self.category, {})
        df['seasonal_boost'] = df['ds'].dt.month.map(seasonal).fillna(1.0)
        
        return df[['ds', 'y', 'is_monsoon', 'seasonal_boost']]

    def fit_prophet(self, df: pd.DataFrame) -> Prophet:
        """
        Fits Prophet model with yearly + weekly seasonality and monsoon regressor.
        """
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            changepoint_prior_scale=0.05,  # Conservative — pharma demand is stable
            seasonality_prior_scale=10.0,
            interval_width=0.95
        )
        model.add_regressor('is_monsoon', standardize=False)
        model.fit(df[['ds', 'y', 'is_monsoon']])
        self.prophet_model = model
        return model

    def fit_arima(self, series: pd.Series) -> None:
        """
        ARIMA(2,1,2) — captures short-term autocorrelation in daily consumption.
        """
        model = ARIMA(series.values, order=(2, 1, 2))
        self.arima_model = model.fit()

    def forecast(self, df: pd.DataFrame, horizon_days: int = 90) -> pd.DataFrame:
        """
        Returns ensemble forecast (70% Prophet + 30% ARIMA) with confidence intervals.
        """
        self.fit_prophet(df)
        self.fit_arima(df['y'])

        # Prophet forecast
        future = self.prophet_model.make_future_dataframe(periods=horizon_days)
        future['is_monsoon'] = future['ds'].dt.month.isin([7, 8, 9]).astype(float)
        prophet_pred = self.prophet_model.predict(future).tail(horizon_days)

        # ARIMA forecast
        arima_pred = self.arima_model.forecast(steps=horizon_days)
        arima_ci = self.arima_model.get_forecast(steps=horizon_days).conf_int()

        # Ensemble blend
        ensemble_yhat = 0.70 * prophet_pred['yhat'].values + 0.30 * arima_pred
        
        result = pd.DataFrame({
            'forecast_date': prophet_pred['ds'].values,
            'predicted_units': np.maximum(0, ensemble_yhat).astype(int),
            'upper_ci': np.maximum(0, prophet_pred['yhat_upper'].values).astype(int),
            'lower_ci': np.maximum(0, prophet_pred['yhat_lower'].values).astype(int),
            'prophet_pred': prophet_pred['yhat'].values,
            'arima_pred': arima_pred,
        })
        return result

    def calculate_mape(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """Mean Absolute Percentage Error — model accuracy metric."""
        mask = actual != 0
        return float(np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100)