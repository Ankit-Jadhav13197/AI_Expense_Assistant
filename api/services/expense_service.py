# api/services/expense_service.py
from sqlalchemy.orm import Session
from api.db.models import Expense
from api.models.schemas import ExpenseCreate, ExpenseUpdate
from typing import List, Optional

def create_expense(db: Session, payload: ExpenseCreate) -> Expense:
    db_exp = Expense(**payload.dict())
    db.add(db_exp)
    db.commit()
    db.refresh(db_exp)
    return db_exp

def get_expenses(db: Session, skip: int = 0, limit: int = 100) -> List[Expense]:
    return db.query(Expense).order_by(Expense.date.desc()).offset(skip).limit(limit).all()

def get_expense(db: Session, expense_id: int) -> Optional[Expense]:
    return db.query(Expense).filter(Expense.id == expense_id).first()

def update_expense(db: Session, expense_id: int, payload: ExpenseUpdate) -> Optional[Expense]:
    db_exp = get_expense(db, expense_id)
    if not db_exp:
        return None
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(db_exp, field, value)
    db.add(db_exp)
    db.commit()
    db.refresh(db_exp)
    return db_exp

def delete_expense(db: Session, expense_id: int) -> bool:
    db_exp = get_expense(db, expense_id)
    if not db_exp:
        return False
    db.delete(db_exp)
    db.commit()
    return True
