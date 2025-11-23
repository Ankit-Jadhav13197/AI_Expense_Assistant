# api/db/models.py
from sqlalchemy import Column, Integer, String, Date, Float
from .session import Base
import datetime

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, default=datetime.date.today)
    description = Column(String(512), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String(128), nullable=True)
