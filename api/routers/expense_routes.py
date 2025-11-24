# api/routers/expense_routes.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from api.ml.classifier import ExpenseClassifier
from api.services import expense_service  # imaginary service layer for DB ops
import csv
from pathlib import Path
import datetime

router = APIRouter(prefix="/expenses", tags=["expenses"])
classifier = ExpenseClassifier()

# Pydantic schema
class ExpenseCreate(BaseModel):
    description: str
    amount: float
    date: Optional[str] = None
    category: Optional[str] = None
    user_id: Optional[int] = None

MISCLASS_LOG = Path(__file__).resolve().parent.parent.parent / "data" / "misclassified_log.csv"
MISCLASS_LOG.parent.mkdir(exist_ok=True, parents=True)

def log_misclassification(description, predicted, actual=None):
    row = {
        "ts": datetime.datetime.utcnow().isoformat(),
        "description": description,
        "predicted": predicted,
        "actual": actual or ""
    }
    write_header = not MISCLASS_LOG.exists()
    with open(MISCLASS_LOG, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if write_header:
            writer.writeheader()
        writer.writerow(row)

@router.post("/", status_code=201)
def create_expense(payload: ExpenseCreate):
    # If category missing, it will auto-predict the category
    category = payload.category
    if not category or not category.strip():
        predicted = classifier.predict(payload.description)
        category = predicted

    # Validate fields (simple)
    if payload.amount < 0:
        raise HTTPException(status_code=400, detail="Amount must be non-negative")

    # Create in DB (service returns created record)
    rec = expense_service.create({
        "description": payload.description,
        "amount": payload.amount,
        "date": payload.date,
        "category": category,
        "user_id": payload.user_id
    })

    # Optionally: if user supplied category that differs from prediction, log for QA
    # Suppose frontend will send an 'user_confirmed' flag when user edits; for now we log when payload.category exists and mismatches predicted
    if payload.category and payload.category.strip():
        predicted = classifier.predict(payload.description)
        if payload.category.strip().lower() != predicted.lower():
            log_misclassification(payload.description, predicted, payload.category.strip())

    return rec
