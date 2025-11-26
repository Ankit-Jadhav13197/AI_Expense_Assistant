# api/ml/forecast.py
from __future__ import annotations
import os
from typing import Tuple, Optional, Dict, Any
import pandas as pd
import numpy as np
from datetime import timedelta
import joblib

# Try Prophet, fall back to sklearn LinearRegression if Prophet not available
try:
    from prophet import Prophet  # package name: "prophet"
    PROPHET_AVAILABLE = True
except Exception:
    PROPHET_AVAILABLE = False

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

MODEL_DIR = os.getenv("ML_MODEL_DIR", "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def _aggregate_expenses(expenses_df: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
    """
    expenses_df must have columns: 'date' (datetime-like), 'amount' (numeric).
    Returns dataframe indexed by date with column 'y' (total amount) and column 'ds' for Prophet.
    """
    df = expenses_df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    # Resample (fill missing with 0)
    agg = df["amount"].resample(freq).sum().rename("y").to_frame()
    agg = agg.reset_index().rename(columns={"date": "ds"})
    return agg


def _detect_and_handle_outliers(df: pd.DataFrame, z_thresh: float = 3.0) -> pd.DataFrame:
    """
    Simple outlier handling: winsorize values beyond z_thresh standard deviations.
    Keeps shape same.
    """
    out = df.copy()
    y = out["y"].astype(float)
    mean = y.mean()
    std = y.std() if y.std() > 0 else 1.0
    upper = mean + z_thresh * std
    lower = mean - z_thresh * std
    out["y"] = np.clip(y, lower, upper)
    return out


def train_prophet(df: pd.DataFrame, model_name: str = "prophet_expense", kwargs: Optional[Dict[str, Any]] = None):
    """
    Train a Prophet model on aggregated dataframe (ds, y). Returns a fitted model.
    Saves model to disk as joblib.
    """
    if not PROPHET_AVAILABLE:
        raise RuntimeError("Prophet not available in environment.")

    kwargs = kwargs or {}
    m = Prophet(**kwargs)
    m.fit(df)
    filepath = os.path.join(MODEL_DIR, f"{model_name}.joblib")
    joblib.dump(m, filepath)
    return m


def train_linear_regression(df: pd.DataFrame, model_name: str = "lr_expense"):
    """
    Fallback simple model: use day index as feature for linear regression.
    Saves model and scalers if needed.
    """
    X = (pd.to_datetime(df["ds"]) - pd.to_datetime(df["ds"].min())).dt.days.values.reshape(-1, 1)
    y = df["y"].values
    lr = LinearRegression()
    lr.fit(X, y)
    artifact = {"model": lr, "start_date": str(df["ds"].min())}
    filepath = os.path.join(MODEL_DIR, f"{model_name}.joblib")
    joblib.dump(artifact, filepath)
    return artifact


def load_model(model_name: str):
    filepath = os.path.join(MODEL_DIR, f"{model_name}.joblib")
    if not os.path.exists(filepath):
        return None
    return joblib.load(filepath)


def predict_with_prophet(model, periods: int = 30, freq: str = "D") -> pd.DataFrame:
    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)
    # Select relevant columns and rename to consistent output
    out = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
    return out


def predict_with_lr(artifact: Dict[str, Any], periods: int = 30, freq: str = "D") -> pd.DataFrame:
    start = pd.to_datetime(artifact["start_date"])
    # compute ordinal days for existing model and future
    last_date = start
    # find model's last trained day by loading a saved training frame? we stored start only; assume length from artifact if present
    # For robustness user should pass original df; here we will create future based on start + range
    # We'll reconstruct days from 0..n+periods-1, but need n; we cannot reconstruct n. So assume artifact contains 'n_days' optionally.
    n_days = artifact.get("n_days", 30)
    total = n_days + periods
    days = np.arange(total).reshape(-1, 1)
    preds = artifact["model"].predict(days)
    # Build ds: start + days
    ds = pd.date_range(start=start, periods=total, freq=freq)
    out = pd.DataFrame({"ds": ds, "yhat": preds})
    # For LR we do not have intervals — set approx +/-10% (naive)
    out["yhat_lower"] = out["yhat"] * 0.9
    out["yhat_upper"] = out["yhat"] * 1.1
    # Keep only the last n_days-> future? For simplicity return all
    return out


def prepare_and_train(expenses_df: pd.DataFrame, freq: str = "D", model_type: str = "prophet", model_name: str = None):
    """
    Prepare raw expense rows and train chosen model_type. Returns trained model/artifact and aggregated train_df.
    """
    agg = _aggregate_expenses(expenses_df, freq=freq)
    agg = _detect_and_handle_outliers(agg)
    model_name = model_name or f"{model_type}_expense"
    if model_type == "prophet" and PROPHET_AVAILABLE:
        m = train_prophet(agg, model_name=model_name)
        return m, agg
    else:
        artifact = train_linear_regression(agg, model_name=model_name)
        # store n_days to help predictions later
        artifact["n_days"] = len(agg)
        return artifact, agg


def forecast_from_raw(expenses_df: pd.DataFrame, periods: int = 30, freq: str = "D", model_type: str = "prophet", model_name: str = None):
    """
    Convenience function: prepare, train (or load existing), and produce forecast dataframe.
    """
    model_name = model_name or f"{model_type}_expense"
    loaded = load_model(model_name)
    if loaded is None:
        model_or_artifact, train_df = prepare_and_train(expenses_df, freq=freq, model_type=model_type, model_name=model_name)
    else:
        model_or_artifact = loaded
        # We still need a train_df to calculate MAE if desired; user can pass test set separately.
        train_df = None

    if model_type == "prophet" and PROPHET_AVAILABLE:
        forecast_df = predict_with_prophet(model_or_artifact, periods=periods, freq=freq)
    else:
        forecast_df = predict_with_lr(model_or_artifact, periods=periods, freq=freq)

    return forecast_df, train_df


def compute_mae(y_true: pd.Series, y_pred: pd.Series) -> float:
    return float(mean_absolute_error(y_true, y_pred))
