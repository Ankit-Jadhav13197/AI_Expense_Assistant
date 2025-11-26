# # api/services/forecast_service.py
# from typing import Tuple, Dict, Any
# import pandas as pd
# from api.ml import forecast as ml_forecast


# def get_forecast(periods: int, freq: str, model_type: str, db):
    
#     rows = crud.get_expenses(db)   # FIXED
    
#     # convert rows → dataframe
#     df = [
#         {"date": row.date, "amount": row.amount}
#         for row in rows
#     ]
    


# # Example DB access - adapt to your ORM/session
# # Here we'll assume you have a function `get_all_expenses()` that returns list/dict rows.
# from api.db import crud  # you should implement a simple crud.get_expenses(start_date=None,end_date=None)

# def get_forecast(periods: int = 30, freq: str = "D", model_type: str = "prophet") -> Dict[str, Any]:
#     """
#     Fetch expense rows from DB, aggregate and call ML code.
#     Returns JSON-serializable dict with forecast rows and optional metrics.
#     """
#     rows = crud.get_expenses()  # expected list of dicts: [{'date':..., 'amount': ...}, ...]
#     if len(rows) == 0:
#         return {"error": "no expense data available"}

#     df = pd.DataFrame(rows)
#     forecast_df, train_df = ml_forecast.forecast_from_raw(df, periods=periods, freq=freq, model_type=model_type)

#     # If train_df exists we can compute MAE over the overlap (simple backtest: use last periods of train as "test")
#     metrics = {}
#     if train_df is not None:
#         # perform a simple backtest: last k days
#         k = min(14, len(train_df))
#         train_part = train_df.copy()
#         # naive one-step forecasting using model retraining could be expensive; as lightweight approximate: compare last k actuals to forecast last k before future
#         # For Prophet, forecast_df contains history + future - we can align by ds
#         # try find overlap
#         merged = pd.merge(train_part, forecast_df, on="ds", how="inner")
#         if not merged.empty:
#             metrics["mae"] = ml_forecast.compute_mae(merged["y"], merged["yhat"])
#     # Format forecast rows
#     rows_out = []
#     for _, r in forecast_df.iterrows():
#         rows_out.append({
#             "date": r["ds"].strftime("%Y-%m-%d"),
#             "predicted": float(r["yhat"]),
#             "lower": float(r.get("yhat_lower", r["yhat"] * 0.9)),
#             "upper": float(r.get("yhat_upper", r["yhat"] * 1.1)),
#         })
#     return {"forecast": rows_out, "metrics": metrics}


# api/services/forecast_service.py

from typing import Dict, Any
import pandas as pd
from api.ml import forecast as ml_forecast
from api.crud.expenses import get_expenses


def get_forecast(periods: int, freq: str, model_type: str, db) -> Dict[str, Any]:
    """
    Fetch expenses from DB and run forecasting ML model.
    """
    # 1. Fetch rows from DB
    rows = get_expenses(db)

    if not rows:
        return {"error": "no expense data available"}

    # 2. Convert to DataFrame
    df = pd.DataFrame([
        {"date": r.date, "amount": r.amount}
        for r in rows
    ])

    # 3. Call ML forecast function
    forecast_df, train_df = ml_forecast.forecast_from_raw(
        df,
        periods=periods,
        freq=freq,
        model_type=model_type
    )

    # 4. Optional backtest metrics
    metrics = {}
    if train_df is not None:
        merged = pd.merge(train_df, forecast_df, on="ds", how="inner")
        if not merged.empty:
            metrics["mae"] = ml_forecast.compute_mae(
                merged["y"],
                merged["yhat"]
            )

    # 5. Final output format
    rows_out = []
    for _, r in forecast_df.iterrows():
        rows_out.append({
            "date": r["ds"].strftime("%Y-%m-%d"),
            "predicted": float(r["yhat"]),
            "lower": float(r.get("yhat_lower", r["yhat"] * 0.9)),
            "upper": float(r.get("yhat_upper", r["yhat"] * 1.1)),
        })

    return {"forecast": rows_out, "metrics": metrics}
