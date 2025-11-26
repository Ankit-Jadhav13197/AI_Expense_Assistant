# tests/test_forecast.py
import pandas as pd
from api.ml import forecast as ml

def test_aggregate_and_train_lr(tmp_path):
    # create toy daily data
    dates = pd.date_range("2025-01-01", periods=60, freq="D")
    amounts = (pd.Series(range(60)) * 1.5 + 10).values
    df = pd.DataFrame({"date": dates, "amount": amounts})
    artifact, agg = ml.prepare_and_train(df, freq="D", model_type="lr", model_name=str(tmp_path / "lr_test"))
    assert "model" in artifact
    # basic prediction
    fc, _ = ml.forecast_from_raw(df, periods=10, freq="D", model_type="lr", model_name=str(tmp_path / "lr_test"))
    assert len(fc) >= 10
