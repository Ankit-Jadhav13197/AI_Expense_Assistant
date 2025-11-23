# api/routers/expenses.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from api.db.session import get_db
from api.models import schemas
from api.services import expense_service

router = APIRouter(prefix="/expenses", tags=["expenses"])

@router.post("/", response_model=schemas.ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(payload: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    return expense_service.create_expense(db, payload)

@router.get("/", response_model=List[schemas.ExpenseOut])
def list_expenses(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), db: Session = Depends(get_db)):
    return expense_service.get_expenses(db, skip=skip, limit=limit)

@router.get("/{expense_id}", response_model=schemas.ExpenseOut)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    db_exp = expense_service.get_expense(db, expense_id)
    if not db_exp:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_exp

@router.put("/{expense_id}", response_model=schemas.ExpenseOut)
def update_expense(expense_id: int, payload: schemas.ExpenseUpdate, db: Session = Depends(get_db)):
    db_exp = expense_service.update_expense(db, expense_id, payload)
    if not db_exp:
        raise HTTPException(status_code=404, detail="Expense not found")
    return db_exp

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    ok = expense_service.delete_expense(db, expense_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Expense not found")
    return
