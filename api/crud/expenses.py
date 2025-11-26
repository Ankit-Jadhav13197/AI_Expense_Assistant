# api/crud/expenses.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from api.db import models
from api.models.schemas import ExpenseCreate

def get_expenses(db: Session):
    """Return all expenses (used by forecast_service)."""
    return db.query(models.Expense).all()

def get_expenses_grouped_by_date(db: Session):
    return (
        db.query(models.Expense.date, func.sum(models.Expense.amount).label("total"))
        .group_by(models.Expense.date)
        .all()
    )
