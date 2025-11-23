# api/models/schemas.py
from pydantic import BaseModel, Field, validator
from datetime import date as DateType
from typing import Optional

class ExpenseBase(BaseModel):
    date: DateType = Field(default_factory=DateType.today)
    description: str = Field(..., min_length=1, max_length=512)
    amount: float = Field(..., gt=0, description="Positive amount")
    category: Optional[str] = Field(None, max_length=128)

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    date: Optional[DateType] = None
    description: Optional[str] = Field(None, min_length=1, max_length=512)
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=128)

class ExpenseOut(ExpenseBase):
    id: int

model_config = {"from_attributes": True}

    # class Config:
    #     orm_mode = True     ogg
