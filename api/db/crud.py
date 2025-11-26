# api/db/crud.py

from sqlalchemy.orm import Session
from datetime import date
from api.db import models
from api.models.schemas import ExpenseCreate


def get_expenses(db: Session, start_date: date = None, end_date: date = None):
    query = db.query(models.Expense)

    if start_date:
        query = query.filter(models.Expense.date >= start_date)

    if end_date:
        query = query.filter(models.Expense.date <= end_date)

    return query.all()


def create_expense(db: Session, expense: ExpenseCreate):
    db_expense = models.Expense(
        date=expense.date,
        description=expense.description,
        amount=expense.amount,
        category=expense.category,
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense
