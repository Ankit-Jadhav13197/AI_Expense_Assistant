# # api/routers/forecast.py
# from fastapi import APIRouter, Query
# from typing import Optional
# from api.services import forecast_service

# router = APIRouter(prefix="/forecast", tags=["forecast"])


# @router.get("/")
# def get_forecast(periods: int = Query(30, ge=1, le=365),
#                  freq: str = Query("D", regex="^[DWMQ]$"),  # D=day,W=week,M=month,Q=quarter
#                  model: str = Query("prophet")):
#     """
#     Returns predicted totals for the next `periods` intervals.
#     freq: D,W,M,Q
#     model: 'prophet' or 'lr'
#     """
#     # map freq param to pandas freq string
#     freq_map = {"D": "D", "W": "W", "M": "MS", "Q": "QS"}
#     used_freq = freq_map.get(freq, "D")
#     result = forecast_service.get_forecast(periods=periods, freq=used_freq, model_type=("prophet" if model == "prophet" else "lr"))
#     return result

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.db.database import get_db
# from api.services import forecast_service
import api.services.forecast_service as forecast_service


router = APIRouter()

@router.get("/forecast/")
def get_forecast(
    periods: int = 7,
    freq: str = "D",
    model: str = "lr",
    db: Session = Depends(get_db)
):
    used_freq = freq.upper()
    return forecast_service.get_forecast(
        periods=periods,
        freq=used_freq,
        model_type=("prophet" if model == "prophet" else "lr"),
        db=db
    )
